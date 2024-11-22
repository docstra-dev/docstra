import os
import time
import json
from pathlib import Path
from typing import List, Optional

import tiktoken
from tqdm import tqdm

from dotenv import load_dotenv
from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers import LanguageParser
from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
import hashlib

from docstra.logger import logger

# Load environment variables
docstra_path = Path("./.docstra")
env_path = docstra_path / Path(".env")
load_dotenv(env_path)

# Supported file extensions
SUPPORTED_CODE_FILE_EXTENSIONS = [
    ".c", ".cpp", ".cs", ".cbl", ".ex", ".go", ".java", ".js",
    ".kt", ".lua", ".pl", ".py", ".rb", ".rs", ".scala", ".ts"
]
SUPPORTED_MARKUP_FILE_EXTENSIONS = [".md", ".html", ".yaml", ".yml"]

# Directories and files to exclude
DEFAULT_DIRS_TO_EXCLUDE = {".git", ".venv", "node_modules", "__pycache__", "dist", "build"}
DEFAULT_FILES_TO_EXCLUDE = {".env", "Pipfile.lock", "poetry.lock"}

# File hash utilities
def load_file_hashes(hash_file: str) -> dict:
    if os.path.exists(hash_file):
        with open(hash_file, "r") as f:
            return json.load(f)
    return {}


def save_file_hashes(hash_file: str, file_hashes: dict):
    with open(hash_file, "w") as f:
        json.dump(file_hashes, f)


def generate_file_hash(file_path: str) -> str:
    with open(file_path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

# Token Count Calculation
def calculate_token_count(content: str, token_encoding_name: str = "cl100k_base") -> int:
    encoding = tiktoken.get_encoding(token_encoding_name)
    return len(encoding.encode(content))


# Document loaders
def load_code_files(path: str) -> List[Document]:
    loader = GenericLoader.from_filesystem(
        path,
        glob="*",
        suffixes=SUPPORTED_CODE_FILE_EXTENSIONS,
        parser=LanguageParser(),
    )
    return loader.load()


def load_markup_files(file_path: str) -> List[Document]:
    file_extension = os.path.splitext(file_path)[1]
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    if file_extension == ".md":
        splitter = MarkdownHeaderTextSplitter()
        return splitter.create_documents([content])

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    return splitter.create_documents([content])


def process_file(file_path: str, file_hashes: dict) -> Optional[List[Document]]:
    current_hash = generate_file_hash(file_path)

    # Skip unchanged files
    if file_hashes.get(file_path) == current_hash:
        return None

    documents = []

    # Load source file content
    try:
        # Attempt to read the file as UTF-8
        with open(file_path, "r", encoding="utf-8") as f:
            source_content = f.read()
    except UnicodeDecodeError:
        logger.warning(f"Skipping non-text or non-UTF-8 file: {file_path}")
        return None

    file_extension = os.path.splitext(file_path)[1]
    if file_extension in SUPPORTED_CODE_FILE_EXTENSIONS:
        # Use GenericLoader to get documents (chunks)
        loader = GenericLoader.from_filesystem(
            os.path.dirname(file_path),
            glob=os.path.basename(file_path),
            suffixes=[file_extension],
            parser=LanguageParser(),
        )
        raw_documents = loader.load()

        # Match each chunk with the source file to determine line numbers
        source_lines = source_content.splitlines()
        for doc in raw_documents:
            chunk_lines = doc.page_content.splitlines()
            start_line, end_line = find_chunk_line_numbers(source_lines, chunk_lines)

            metadata_template = {
                "source": file_path,
                "file_path": file_path,
                "file_hash": current_hash,
                "start_line": start_line,
                "end_line": end_line,
                "line_count": len(chunk_lines),
                "ingestion_timestamp": time.time(),
            }
            doc.metadata.update(metadata_template)
            documents.append(doc)

    elif file_extension in SUPPORTED_MARKUP_FILE_EXTENSIONS:
        # Use appropriate parser for markup files
        documents = load_markup_files(file_path)

    return documents if documents else None


def find_chunk_line_numbers(source_lines: List[str], chunk_lines: List[str]) -> (int, int):
    """
    Finds the start and end line numbers of a chunk in the source file.
    Args:
        source_lines: List of lines in the source file.
        chunk_lines: List of lines in the chunk.
    Returns:
        A tuple of (start_line, end_line).
    """
    start_line, end_line = -1, -1
    for i in range(len(source_lines)):
        if source_lines[i:i + len(chunk_lines)] == chunk_lines:
            start_line = i + 1
            end_line = i + len(chunk_lines)
            break
    return start_line, end_line


# Main repository ingestion
def ingest_repo(
        repo_path: str,
        hash_file: str = "./.docstra/hashes.json",
        max_tokens_per_minute: int = 60000,
        token_encoding_name: str = "cl100k_base"
) -> List[Document]:
    file_hashes = load_file_hashes(hash_file)
    documents = []
    total_tokens = 0
    total_files = sum(len(files) for _, _, files in os.walk(repo_path))
    start_time = time.time()

    with tqdm(total=total_files, desc="Processing files", position=0, leave=True) as pbar:
        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if d not in DEFAULT_DIRS_TO_EXCLUDE]
            for file in files:
                if file in DEFAULT_FILES_TO_EXCLUDE:
                    continue

                file_path = os.path.join(root, file)
                file_docs = process_file(file_path, file_hashes)

                if file_docs:
                    for doc in file_docs:
                        doc.metadata["file_path"] = file_path

                        # Calculate token count and throttle if necessary
                        token_count = calculate_token_count(doc.page_content, token_encoding_name)
                        total_tokens += token_count

                        # Check if the token limit has been exceeded
                        elapsed_time = time.time() - start_time
                        if total_tokens > max_tokens_per_minute:
                            sleep_time = max(0, 60 - elapsed_time)
                            logger.warning(
                                f"Throttling to avoid exceeding token limit. Sleeping for {sleep_time:.2f} seconds...")
                            time.sleep(sleep_time)
                            total_tokens = token_count  # Reset token count after sleeping
                            start_time = time.time()  # Reset start time
                    documents.extend(file_docs)
                    file_hashes[file_path] = generate_file_hash(file_path)
                pbar.update(1)

    save_file_hashes(hash_file, file_hashes)
    return documents


if __name__ == "__main__":
    # Ingest repository and print results
    repo_path = "./"
    documents = ingest_repo(repo_path)
    print(f"Ingested {len(documents)} documents.")