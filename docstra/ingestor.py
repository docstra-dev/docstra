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


class DocstraIngestor:
    def __init__(
        self,
        repo_path: str | PathLike[str],
        max_tokens_per_minute: int = 60000,
        token_encoding_name: str = "cl100k_base",
        hash_file: str | PathLike[str] = "./hashes.json",
    ):
        self.repo_path = repo_path
        self.max_tokens_per_minute = max_tokens_per_minute
        self.token_encoding_name = token_encoding_name
        self.hash_file = hash_file
        self.file_hashes = self.load_file_hashes()

    @staticmethod
    def extract_python_metadata(file_content):
        """Extracts metadata such as classes, functions, and imports from Python files."""
        try:
            parsed_code = ast.parse(file_content)
            classes = [
                node.name
                for node in ast.walk(parsed_code)
                if isinstance(node, ast.ClassDef) and node.name is not None
            ]
            functions = [
                node.name
                for node in ast.walk(parsed_code)
                if isinstance(node, ast.FunctionDef) and node.name is not None
            ]
            imports = [
                node.module
                for node in ast.walk(parsed_code)
                if isinstance(node, ast.ImportFrom) and node.module is not None
            ]

            return {
                "classes": ", ".join(classes) if classes else "No classes found",
                "functions": (
                    ", ".join(functions) if functions else "No functions found"
                ),
                "imports": ", ".join(imports) if imports else "No imports found",
            }
        except Exception as e:
            logger.error(f"Error extracting Python metadata: {e}")
            return {}

    @staticmethod
    def format_as_markdown(file_path, file_content):
        """Format the file content as Markdown with proper code blocks."""
        file_extension = os.path.splitext(file_path)[1]

        # Split content into lines and prepend line numbers
        lines = file_content.split("\n")
        numbered_lines = [f"{i + 1}: {line}" for i, line in enumerate(lines)]
        numbered_content = "\n".join(numbered_lines)

        if file_extension == ".py":
            # Format Python code as Markdown with python-specific code blocks
            return f"```python\n{numbered_content}\n```"
        elif file_extension == ".md":
            # If it's already Markdown, return as is
            return numbered_content
        elif file_extension == ".txt":
            # For plain text, wrap it in a generic code block
            return f"```\n{numbered_content}\n```"
        elif file_extension == ".json":
            # For JSON, format it with a JSON code block
            return f"```json\n{numbered_content}\n```"
        elif file_extension == ".yaml":
            # For YAML, format it with a YAML code block
            return f"```yaml\n{numbered_content}\n```"
        elif file_extension == ".sh":
            # For shell scripts, format it with a shell script code block
            return f"```bash\n{numbered_content}\n```"
        else:
            # Handle other file types (e.g., unknown) with a generic code block
            return f"```\n{numbered_content}\n```"

    def load_file_hashes(self):
        """Load file hashes from a JSON file."""
        if os.path.exists(self.hash_file):
            with open(self.hash_file, "r") as f:
                return json.load(f)
        return {}

    def save_file_hashes(self):
        """Save file hashes to a JSON file."""
        with open(self.hash_file, "w") as f:  # type: ignore
            json.dump(self.file_hashes, f)

    @staticmethod
    def file_hash(file_path):
        """Generate a hash of the file's content to detect changes."""
        with open(file_path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()

    def calculate_token_count(self, content: str) -> int:
        """Calculate the number of tokens in the document content."""
        encoding = tiktoken.get_encoding(self.token_encoding_name)
        return len(encoding.encode(content))

    def process_file(self, file_path):
        try:
            current_hash = self.file_hash(file_path)

            # Check if the file hash matches the previously stored hash
            if self.file_hashes.get(file_path) == current_hash:
                logger.info(f"Skipping {file_path}, no changes detected.")
                return None

            with open(file_path, "r", encoding="utf-8") as f:
                file_content = f.read()

            file_id = file_path
            file_metadata = {
                "file_path": file_path,
                "file_hash": self.file_hash(file_path),
                "file_size": os.path.getsize(file_path),
                "file_extension": os.path.splitext(file_path)[1],
                "file_name": os.path.basename(file_path),
                "line_count": file_content.count("\n") + 1,
                "last_modified": os.path.getmtime(file_path),
            }

            # Extract additional metadata using AST for Python files
            if file_path.endswith(".py"):
                python_metadata = self.extract_python_metadata(file_content)
                file_metadata.update(python_metadata)

            # Sanitize metadata to avoid None values
            sanitized_metadata = {
                k: (v if v is not None else "") for k, v in file_metadata.items()
            }

            markdown_content = self.format_as_markdown(file_path, file_content)

            document = Document(
                id=file_id, page_content=markdown_content, metadata=sanitized_metadata
            )

            # Update the file hash in memory
            self.file_hashes[file_path] = current_hash

            return document
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")

    def ingest_repo(self):
        dirs_to_exclude = {
            ".git",
            ".venv",
            "node_modules",
            "__pycache__",
            "dist",
            "build",
        }
        files_to_exclude = {".env", "Pipfile.lock", "poetry.lock"}
        file_extensions_to_include = {".py", ".md", ".txt", ".json", ".yaml", ".sh"}

        documents = []
        total_tokens = 0
        total_files = sum([len(files) for _, _, files in os.walk(self.repo_path)])

        # Walk through the repository directory
        with tqdm(
            total=total_files, desc="Processing files", position=0, leave=True
        ) as pbar:
            for root, dirs, files in tqdm(
                os.walk(self.repo_path), desc="Creating documents per directory"
            ):
                # Modify the dirs list in place to exclude unwanted directories
                dirs[:] = [d for d in dirs if d not in dirs_to_exclude]

                for file in files:
                    if file in files_to_exclude:
                        continue
                    if not any(
                        file.endswith(ext) for ext in file_extensions_to_include
                    ):
                        continue
                    file_path = os.path.join(root, file)
                    result = self.process_file(file_path)

                    if result:
                        # Calculate the token count for this document
                        token_count = self.calculate_token_count(result.page_content)
                        total_tokens += token_count

                        # Check if total tokens exceed the rate limit
                        if total_tokens > self.max_tokens_per_minute:
                            logger.warning(
                                f"Throttling to avoid exceeding token limit. Sleeping..."
                            )
                            time.sleep(60)  # Wait for a minute to reset the token limit
                            total_tokens = (
                                token_count  # Reset token counter after sleep
                            )

                        documents.append(result)
                        pbar.update(1)

        # Save file hashes to disk
        self.save_file_hashes()

        logger.info(f"{len(documents)} documents were created...")
        return documents
