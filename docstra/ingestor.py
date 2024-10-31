import ast
import hashlib
import json
import os
from os import PathLike
import time
import tiktoken
from docstra.logger import logger
from langchain_core.documents import Document
from tqdm import tqdm

DEFAULT_DIRS_TO_EXCLUDE = {".git", ".venv", "node_modules", "__pycache__", "dist", "build"}
DEFAULT_FILES_TO_EXCLUDE = {".env", "Pipfile.lock", "poetry.lock"}
DEFAULT_FILE_EXTENSIONS_TO_INCLUDE = {".py", ".md", ".txt", ".json", ".yaml", ".sh"}

def load_file_hashes(hash_file: str | PathLike[str]) -> dict:
    """Load file hashes from a JSON file."""
    if os.path.exists(hash_file):
        with open(hash_file, "r") as f:
            return json.load(f)
    return {}

def save_file_hashes(hash_file: str | PathLike[str], file_hashes: dict):
    """Save file hashes to a JSON file."""
    with open(hash_file, "w") as f:
        json.dump(file_hashes, f)

def file_hash(file_path: str) -> str:
    """Generate a hash of the file's content to detect changes."""
    with open(file_path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

def extract_python_metadata(file_content: str) -> dict:
    """Extracts metadata such as classes, functions, and imports from Python files."""
    try:
        parsed_code = ast.parse(file_content)
        classes = [node.name for node in ast.walk(parsed_code) if isinstance(node, ast.ClassDef)]
        functions = [node.name for node in ast.walk(parsed_code) if isinstance(node, ast.FunctionDef)]
        imports = [node.module for node in ast.walk(parsed_code) if isinstance(node, ast.ImportFrom) and node.module]

        return {
            "classes": ", ".join(classes) if classes else "No classes found",
            "functions": ", ".join(functions) if functions else "No functions found",
            "imports": ", ".join(imports) if imports else "No imports found",
        }
    except Exception as e:
        logger.error(f"Error extracting Python metadata: {e}")
        return {}

def format_as_markdown(file_path: str, file_content: str) -> str:
    """Format the file content as Markdown with proper code blocks."""
    file_extension = os.path.splitext(file_path)[1]
    lines = file_content.split("\n")
    numbered_lines = [f"{i + 1}: {line}" for i, line in enumerate(lines)]
    numbered_content = "\n".join(numbered_lines)

    code_block_map = {
        ".py": "python",
        ".md": "",
        ".txt": "",
        ".json": "json",
        ".yaml": "yaml",
        ".sh": "bash",
    }
    lang = code_block_map.get(file_extension, "")
    return f"```{lang}\n{numbered_content}\n```" if lang else numbered_content

def calculate_token_count(content: str, token_encoding_name: str = "cl100k_base") -> int:
    """Calculate the number of tokens in the document content."""
    encoding = tiktoken.get_encoding(token_encoding_name)
    return len(encoding.encode(content))

def process_file(file_path: str, file_hashes: dict, token_encoding_name: str) -> Document | None:
    try:
        current_hash = file_hash(file_path)

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

        if file_path.endswith(".py"):
            python_metadata = extract_python_metadata(file_content)
            file_metadata.update(python_metadata)

        sanitized_metadata = {k: (v if v is not None else "") for k, v in file_metadata.items()}
        markdown_content = format_as_markdown(file_path, file_content)

        document = Document(
            id=file_path, page_content=markdown_content, metadata=sanitized_metadata
        )

        file_hashes[file_path] = current_hash
        return document
    except Exception as e:
        logger.error(f"Error processing file {file_path}: {e}")
        return None

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
                if file in DEFAULT_FILES_TO_EXCLUDE:
                    continue
                if not any(file.endswith(ext) for ext in DEFAULT_FILE_EXTENSIONS_TO_INCLUDE):
                    continue
                file_path = os.path.join(root, file)
                result = process_file(file_path, file_hashes, token_encoding_name)

                if result:
                    token_count = calculate_token_count(result.page_content, token_encoding_name)
                    total_tokens += token_count

                    if total_tokens > max_tokens_per_minute:
                        logger.warning(f"Throttling to avoid exceeding token limit. Sleeping...")
                        time.sleep(60)
                        total_tokens = token_count

                    documents.append(result)
                    pbar.update(1)

    save_file_hashes(hash_file, file_hashes)
    logger.info(f"{len(documents)} documents were created...")
    return documents
