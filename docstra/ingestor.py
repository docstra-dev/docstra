import hashlib
import json
import os
import time
from os import PathLike
from tqdm import tqdm
from tree_sitter import Parser, Node, Language
import tiktoken
from langchain_core.documents import Document
from docstra.logger import logger
from langchain_text_splitters import RecursiveCharacterTextSplitter, Language as TextSplitterLanguage

from docstra.vectorstore import initialize_vectorstore

# Constants for directory and file exclusions
DEFAULT_DIRS_TO_EXCLUDE = {".git", ".venv", "node_modules", "__pycache__", "dist", "build"}
DEFAULT_FILES_TO_EXCLUDE = {".env", "Pipfile.lock", "poetry.lock"}
DEFAULT_FILE_EXTENSIONS_TO_INCLUDE = {".py", ".json", ".yaml", ".sh"}

# Initialize Language Parsers
import tree_sitter_python as tspython
import tree_sitter_json as tsjson
import tree_sitter_html as tshtml
import tree_sitter_typescript as tstypescript
import tree_sitter_javascript as tsjavascript
import tree_sitter_markdown as tsmarkdown

LANGUAGES = {
    "python": Language(tspython.language()),
    "json": Language(tsjson.language()),
    "html": Language(tshtml.language()),
    "typescript": Language(tstypescript.language_typescript()),
    "javascript": Language(tsjavascript.language()),
    "markdown": Language(tsmarkdown.language()),
}

PARSERS = {
    ext: Parser(LANGUAGES[ext]) for ext in LANGUAGES.keys()
}

FILE_EXTENSIONS_TO_LANGUAGES = {
    ".py": "python",
    ".json": "json",
    ".html": "html",
    ".ts": "typescript",
    ".js": "javascript",
    ".md": "markdown",
}

# Mapping Tree-sitter languages to LangChain's Language enum
TREE_SITTER_TO_LANGCHAIN_LANGUAGE = {
    "python": TextSplitterLanguage.PYTHON,
    "json": TextSplitterLanguage.JS,
    "html": TextSplitterLanguage.HTML,
    "typescript": TextSplitterLanguage.TS,
    "javascript": TextSplitterLanguage.JS,
    "markdown": TextSplitterLanguage.MARKDOWN,
}

# Utility Functions for File Hashing and Loading
def load_file_hashes(hash_file: str | PathLike[str]) -> dict:
    if os.path.exists(hash_file):
        with open(hash_file, "r") as f:
            return json.load(f)
    return {}


def save_file_hashes(hash_file: str | PathLike[str], file_hashes: dict):
    with open(hash_file, "w") as f:
        json.dump(file_hashes, f)


def generate_file_hash(file_path: str) -> str:
    with open(file_path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


# Token Count Calculation
def calculate_token_count(content: str, token_encoding_name: str = "cl100k_base") -> int:
    encoding = tiktoken.get_encoding(token_encoding_name)
    return len(encoding.encode(content))


# Tree-sitter-based Chunking
def chunk_node(node: Node, text: str, file_path: str, file_hash: str, MAX_CHARS: int = 1500) -> list[Document]:
    documents = []
    current_chunk = ""
    metadata_template = {
        "file_path": file_path,
        "file_hash": file_hash,
        "node_type": node.type,
        "start_byte": node.start_byte,
        "end_byte": node.end_byte,
        "start_line": node.start_point[0] + 1,
        "end_line": node.end_point[0] + 1,
    }

    for child in node.children:
        chunk_size = child.end_byte - child.start_byte
        child_text = text[child.start_byte:child.end_byte]

        if chunk_size > MAX_CHARS:
            documents.extend(chunk_node(child, text, file_path, file_hash, MAX_CHARS))
        elif len(current_chunk) + chunk_size > MAX_CHARS:
            documents.append(Document(page_content=current_chunk, metadata=metadata_template))
            current_chunk = child_text
        else:
            current_chunk += child_text

    if current_chunk:
        documents.append(Document(page_content=current_chunk, metadata=metadata_template))

    return documents


def chunk(text: str, language: str, file_path: str, file_hash: str, MAX_CHARS: int = 1500) -> list[Document]:
    parser = PARSERS.get(language)
    tree = parser.parse(bytes(text, "utf-8"))

    if not tree.root_node.children or tree.root_node.children[0].type == "ERROR":
        logger.warning(f"Could not parse chunk with parser {language}")

        # Get the corresponding LangChain Language enum for the given language
        langchain_language = TREE_SITTER_TO_LANGCHAIN_LANGUAGE.get(language)
        if langchain_language is None:
            logger.error(f"No LangChain language mapping found for Tree-sitter language '{language}'")
            return []

        # Fallback: Naive splitting in case of parsing failure
        splitter = RecursiveCharacterTextSplitter.from_language(
            language=langchain_language,
            chunk_size=MAX_CHARS,
            chunk_overlap=0
        )
        return splitter.create_documents([text])

    return chunk_node(tree.root_node, text, file_path, file_hash, MAX_CHARS)


# Process Files with Tree-sitter Chunking
def process_file(file_path: str, file_hashes: dict) -> list[Document] | None:
    current_hash = generate_file_hash(file_path)

    if file_hashes.get(file_path) == current_hash:
        logger.info(f"Skipping {file_path}, no changes detected.")
        return None

    with open(file_path, "r", encoding="utf-8") as f:
        file_content = f.read()

    file_metadata = {
        "file_path": file_path,
        "file_hash": current_hash,
        "file_size": os.path.getsize(file_path),
        "file_extension": os.path.splitext(file_path)[1],
        "file_name": os.path.basename(file_path),
        "line_count": file_content.count("\n") + 1,
        "last_modified": os.path.getmtime(file_path),
    }

    language = FILE_EXTENSIONS_TO_LANGUAGES[file_metadata["file_extension"]]
    documents = chunk(file_content, language, file_path, current_hash)

    for doc in documents:
        doc.metadata.update(file_metadata)

    file_hashes[file_path] = current_hash
    return documents


# Ingest Repository with Token Count Management
def ingest_repo(
        repo_path: str | PathLike[str],
        hash_file: str | PathLike[str] = "./hashes.json",
        max_tokens_per_minute: int = 60000,
        token_encoding_name: str = "cl100k_base"
) -> list[Document]:
    file_hashes = load_file_hashes(hash_file)
    documents = []
    total_tokens = 0
    total_files = sum([len(files) for _, _, files in os.walk(repo_path)])

    with tqdm(total=total_files, desc="Processing files", position=0, leave=True) as pbar:
        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if d not in DEFAULT_DIRS_TO_EXCLUDE]
            for file in files:
                if file in DEFAULT_FILES_TO_EXCLUDE or not any(
                        file.endswith(ext) for ext in DEFAULT_FILE_EXTENSIONS_TO_INCLUDE):
                    continue
                file_path = os.path.join(root, file)
                file_docs = process_file(file_path, file_hashes)

                if file_docs:
                    for doc in file_docs:
                        token_count = calculate_token_count(doc.page_content, token_encoding_name)
                        total_tokens += token_count

                        if total_tokens > max_tokens_per_minute:
                            logger.warning(f"Throttling to avoid exceeding token limit. Sleeping...")
                            time.sleep(60)
                            total_tokens = token_count

                        documents.append(doc)
                    pbar.update(1)

    save_file_hashes(hash_file, file_hashes)
    logger.info(f"{len(documents)} documents were created...")
    return documents

if __name__ == "__main__":
    # Ingest repository and add documents to vectorstore
    documents = ingest_repo(repo_path=".")
    print(documents)