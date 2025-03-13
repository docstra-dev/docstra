import os
import re
import json
import hashlib
import traceback
from pathlib import Path
from typing import List, Optional, Dict, Any, Set
import fnmatch
from datetime import datetime
import io

# Import Document class from langchain
from langchain_core.documents import Document

# Import text splitters
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_text_splitters import Language


# Import utilities
# Manual implementation of metadata filtering to avoid dependency issues
def filter_complex_metadata(metadata):
    """Filter out complex metadata types that ChromaDB doesn't support.

    Args:
        metadata: A dictionary of metadata

    Returns:
        A dictionary with only primitive types
    """
    filtered = {}
    for key, value in metadata.items():
        if isinstance(value, (str, int, float, bool)) and value is not None:
            filtered[key] = value
        elif value is None:
            filtered[key] = ""
        elif isinstance(value, (list, dict, set, tuple)):
            # Convert complex types to JSON strings
            try:
                filtered[key] = json.dumps(value)
            except:
                filtered[key] = str(value)
        else:
            # Convert anything else to string
            filtered[key] = str(value)
    return filtered


def extract_file_references(text: str) -> List[str]:
    """Extract potential file references from text.

    Args:
        text: Text to extract file references from

    Returns:
        List of potential file paths
    """
    # Improved implementation with regex
    references = []

    # Pattern for file paths (like "/path/to/file.ext" or "path/to/file.ext")
    path_pattern = r"(?:\/|\\)?(?:[a-zA-Z0-9_-]+(?:\/|\\))+[a-zA-Z0-9_.-]+"

    # Pattern for import-like references (like "import foo.bar" or "from foo.bar import baz")
    import_pattern = r"(?:from|import)\s+([a-zA-Z0-9_.]+)"

    # Find all matches for file paths
    for match in re.finditer(path_pattern, text):
        path = match.group(0).strip(",.;:\"'()[]{}")
        if path not in references:
            references.append(path)

    # Find all import-like references
    for match in re.finditer(import_pattern, text):
        module = match.group(1).strip()
        if module and module not in references:
            references.append(module)

    return references


def extract_imports(content: str, language: str) -> List[str]:
    """Extract import statements from code.

    Args:
        content: The code content
        language: The programming language

    Returns:
        A list of imported modules/packages
    """
    imports = []

    if language == Language.PYTHON or language == "python":
        # Python imports: import X, from X import Y
        import_pattern = r"^\s*import\s+([a-zA-Z0-9_., ]+)(?:\s+as\s+[a-zA-Z0-9_]+)?"
        from_pattern = r"^\s*from\s+([a-zA-Z0-9_.]+)\s+import\s+"

        for line in content.split("\n"):
            # Check for import statement
            match = re.match(import_pattern, line)
            if match:
                # Split multiple imports (import os, sys, re)
                modules = [m.strip() for m in match.group(1).split(",")]
                imports.extend(modules)
                continue

            # Check for from ... import statement
            match = re.match(from_pattern, line)
            if match:
                imports.append(match.group(1))

    elif language in [Language.JS, Language.TS, "javascript", "typescript"]:
        # JavaScript/TypeScript imports
        import_pattern = r"(?:import|require)\s*\(?[\'\"]([^\'\"]+)[\'\"]"
        for match in re.finditer(import_pattern, content):
            imports.append(match.group(1))

    elif language in ["r", "R"]:
        # R imports: library(pkg), require(pkg), or pkg::func
        pkg_pattern = r'(?:library|require)\s*\(\s*["\']?([a-zA-Z0-9.]+)["\']?\s*\)'
        namespace_pattern = r"([a-zA-Z0-9.]+)::"

        for match in re.finditer(pkg_pattern, content):
            imports.append(match.group(1))

        for match in re.finditer(namespace_pattern, content):
            imports.append(match.group(1))

    # More languages can be added here as needed

    return list(set(imports))  # Return unique imports


def extract_code_elements(content: str, language: str) -> Dict[str, List[str]]:
    """Extract code elements like functions, classes, etc.

    Args:
        content: The code content
        language: The programming language

    Returns:
        Dictionary of code elements by type
    """
    elements = {
        "functions": [],
        "classes": [],
        "variables": [],
    }

    if language == Language.PYTHON or language == "python":
        # Python function definitions
        function_pattern = r"^\s*def\s+([a-zA-Z0-9_]+)\s*\("
        # Python class definitions
        class_pattern = r"^\s*class\s+([a-zA-Z0-9_]+)"
        # Python top-level variables/constants
        variable_pattern = r"^\s*([A-Z0-9_]+)\s*="

        for line in content.split("\n"):
            # Check for function definition
            match = re.match(function_pattern, line)
            if match:
                elements["functions"].append(match.group(1))
                continue

            # Check for class definition
            match = re.match(class_pattern, line)
            if match:
                elements["classes"].append(match.group(1))
                continue

            # Check for constant-like variables (uppercase)
            match = re.match(variable_pattern, line)
            if match:
                elements["variables"].append(match.group(1))

    elif language in ["r", "R"]:
        # R function definitions
        function_pattern = r"([a-zA-Z0-9_.]+)\s*<-\s*function\s*\("

        for match in re.finditer(function_pattern, content):
            elements["functions"].append(match.group(1))

    # More languages can be added here

    return elements


def locate_in_file(content: str, file_path: Path) -> Optional[List[int]]:
    """Locate content in a file and return line numbers.

    Args:
        content: The content to find
        file_path: Path to the file to search in

    Returns:
        Tuple of (start_line, end_line) or None if not found
    """
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            file_content = f.read()

        # Extract the first line for simpler matching
        first_content_line = content.split("\n")[0].strip()
        if not first_content_line:
            return None

        file_lines = file_content.split("\n")

        # Look for the first line of content in the file
        for i, line in enumerate(file_lines):
            if first_content_line in line:
                # Check if the rest of the content matches
                content_lines = content.strip().split("\n")
                if len(content_lines) == 1:
                    return [i, i]

                # Try to match multiple lines
                potential_match = "\n".join(file_lines[i : i + len(content_lines)])
                if content.strip() in potential_match:
                    return [i, i + len(content_lines) - 1]

        return None
    except Exception:
        return None


class DocstraLoader:
    """Handles file discovery, filtering, loading, chunking, and metadata creation.

    This class is responsible for loading code files into LangChain Document objects,
    with appropriate chunking and metadata. It uses LangChain's best practices for
    code handling.
    """

    # Mapping of file extensions to LangChain Language enum values
    language_map = {
        # Programming languages
        ".py": Language.PYTHON,
        ".js": Language.JS,
        ".jsx": Language.JS,
        ".ts": Language.TS,
        ".tsx": Language.TS,
        ".java": Language.JAVA,
        ".go": Language.GO,
        ".rb": Language.RUBY,
        ".rs": Language.RUST,
        ".php": Language.PHP,
        ".cs": Language.CSHARP,
        ".cpp": Language.CPP,
        ".cc": Language.CPP,
        ".c": Language.CPP,
        ".h": Language.CPP,
        ".hpp": Language.CPP,
        ".scala": Language.SCALA,
        ".swift": Language.SWIFT,
        ".kt": Language.KOTLIN,
        ".r": "r",  # R language
        ".R": "r",  # R language (uppercase extension)
        ".rmd": "r-markdown",  # R Markdown
        ".Rmd": "r-markdown",  # R Markdown (mixed case)
        # Markup and data formats
        ".md": "markdown",
        ".txt": "text",
        ".json": "json",
        ".yml": "yaml",
        ".yaml": "yaml",
        ".html": "html",
        ".css": "css",
        ".scss": "css",
        ".sql": "sql",
        # Config files
        ".toml": "toml",
        ".xml": "xml",
        ".ini": "ini",
        ".conf": "conf",
    }

    def __init__(
        self,
        working_dir: Path,
        included_extensions: List[str] = None,
        excluded_patterns: List[str] = None,
        chunk_size: int = 1200,
        chunk_overlap: int = 200,
        logger=None,
    ):
        """Initialize the code loader.

        Args:
            working_dir: Root directory for file operations
            included_extensions: List of file extensions to include (with dot, e.g., [".py", ".js"])
            excluded_patterns: List of glob patterns to exclude
            chunk_size: Size of chunks in characters/tokens
            chunk_overlap: Overlap between chunks in characters/tokens
            logger: Optional logger for logging messages
        """
        self.working_dir = Path(working_dir)
        self.included_extensions = included_extensions
        self.excluded_patterns = excluded_patterns
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.logger = logger

    def get_all_files(self) -> List[str]:
        """Get all files in the codebase.

        Returns:
            List of file paths
        """
        # First collect all matching files
        files = self.collect_code_files()
        if not files:
            if self.logger:
                self.logger.warning("No files found matching the criteria")
            return []

        # Convert Path objects to strings
        return [str(file_path) for file_path in files]

    def load_all(self) -> List[Document]:
        """Load all files matching the include/exclude patterns.

        Returns:
            List of Document objects with metadata
        """
        # First collect all matching files
        files = self.collect_code_files()
        if not files:
            if self.logger:
                self.logger.warning("No files found matching the criteria")
            return []

        return self.load_files(files)

    def load_files(self, file_paths: List[Path]) -> List[Document]:
        """Load and process specific files into Documents.

        Args:
            file_paths: List of file paths to load

        Returns:
            List of Document objects with metadata
        """
        if not file_paths:
            return []

        docs = []
        for file_path in file_paths:
            file_docs = self.load_file(file_path)
            docs.extend(file_docs)

        return docs

    def load_file(self, file_path: Path) -> List[Document]:
        """Load a single file into Documents.

        Args:
            file_path: Path to the file to load

        Returns:
            List of Document objects with metadata
        """
        if isinstance(file_path, str):
            file_path = Path(file_path)

        # Skip if file doesn't exist
        if not file_path.exists() or not file_path.is_file():
            if self.logger:
                self.logger.warning(
                    f"File does not exist or is not a file: {file_path}"
                )
            return []

        try:
            # Determine language based on file extension
            file_language = self.language_map.get(file_path.suffix, "text")

            # Read file content directly
            try:
                with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
            except Exception as e:
                try:
                    # Try with binary mode if text mode fails
                    with open(file_path, "rb") as f:
                        content = f.read().decode("utf-8", errors="replace")
                except Exception as e2:
                    if self.logger:
                        self.logger.error(f"Failed to read file {file_path}: {e}, {e2}")
                    return []

            if not content:
                if self.logger:
                    self.logger.warning(f"No content found in {file_path}")
                return []

            # Extract useful information from the content
            try:
                rel_path = file_path.relative_to(self.working_dir).as_posix()
            except ValueError:
                # If the file is outside the working directory, use its absolute path
                rel_path = str(file_path)

            now = datetime.now().isoformat()
            file_stat = file_path.stat()

            # Get code structure
            code_elements = extract_code_elements(content, file_language)
            imports = extract_imports(content, file_language)
            references = extract_file_references(content)

            # Calculate measurements
            word_count = len(content.split())
            approx_token_count = len(content) // 4  # Rough estimate
            content_hash = hashlib.md5(content.encode("utf-8")).hexdigest()
            file_size_kb = round(file_stat.st_size / 1024, 2)

            # Setup common metadata for all chunks
            metadata = {
                # File info
                "source": str(file_path),
                "file_path": rel_path,
                "file_name": file_path.name,
                "file_type": file_path.suffix,
                "file_size_kb": str(file_size_kb),
                # Language info
                "language": str(file_language),
                # Content metadata
                "word_count": str(word_count),
                "approx_tokens": str(approx_token_count),
                "content_hash": content_hash,
                # Time information
                "last_modified": str(datetime.fromtimestamp(file_stat.st_mtime)),
                "created": str(datetime.fromtimestamp(file_stat.st_ctime)),
                "indexed_at": now,
                # Code structure (all stringified)
                "imports": json.dumps(imports) if imports else "",
                "references": json.dumps(references) if references else "",
                "functions": (
                    json.dumps(code_elements.get("functions", []))
                    if code_elements.get("functions")
                    else ""
                ),
                "classes": (
                    json.dumps(code_elements.get("classes", []))
                    if code_elements.get("classes")
                    else ""
                ),
                "variables": (
                    json.dumps(code_elements.get("variables", []))
                    if code_elements.get("variables")
                    else ""
                ),
                # Repository context
                "repo_root": str(self.working_dir),
                "repo_relative_path": rel_path,
            }

            # Apply text splitting
            chunks = []
            chunk_size = self.chunk_size
            chunk_overlap = self.chunk_overlap

            # Use simple line-based chunking
            lines = content.split("\n")
            total_lines = len(lines)

            # For very small files, just create a single chunk
            if total_lines < 50 or len(content) < chunk_size:
                doc = Document(page_content=content, metadata=metadata.copy())
                doc.metadata["chunk_number"] = "1"
                doc.metadata["total_chunks"] = "1"
                # Final safety check
                doc.metadata = filter_complex_metadata(doc.metadata)
                return [doc]

            # For larger files, create overlapping chunks
            current_chunk = []
            current_length = 0
            chunk_num = 1

            for i, line in enumerate(lines):
                current_chunk.append(line)
                current_length += len(line) + 1  # +1 for the newline

                # Check if we've reached chunk size
                if current_length >= chunk_size and i < total_lines - 1:
                    # Create document with this chunk
                    chunk_text = "\n".join(current_chunk)
                    chunk_metadata = metadata.copy()
                    chunk_metadata["chunk_number"] = str(chunk_num)

                    # Add line numbers if possible
                    line_start = i - len(current_chunk) + 1
                    line_end = i
                    chunk_metadata["line_range"] = json.dumps([line_start, line_end])

                    # Create the document
                    doc = Document(page_content=chunk_text, metadata=chunk_metadata)

                    chunks.append(doc)
                    chunk_num += 1

                    # Keep overlap lines for next chunk
                    overlap_lines = int(
                        len(current_chunk) * (chunk_overlap / chunk_size)
                    )
                    current_chunk = (
                        current_chunk[-overlap_lines:] if overlap_lines > 0 else []
                    )
                    current_length = sum(len(line) + 1 for line in current_chunk)

            # Add the final chunk if there's anything left
            if current_chunk:
                chunk_text = "\n".join(current_chunk)
                chunk_metadata = metadata.copy()
                chunk_metadata["chunk_number"] = str(chunk_num)

                # Add line numbers
                line_start = total_lines - len(current_chunk)
                line_end = total_lines - 1
                chunk_metadata["line_range"] = json.dumps([line_start, line_end])

                doc = Document(page_content=chunk_text, metadata=chunk_metadata)
                chunks.append(doc)

            # Update total_chunks in all documents
            total_chunks = len(chunks)
            for doc in chunks:
                doc.metadata["total_chunks"] = str(total_chunks)

                # Final safety check - ensure all values are primitive types
                doc.metadata = filter_complex_metadata(doc.metadata)

            return chunks

        except Exception as e:
            if self.logger:
                error_details = traceback.format_exc()
                self.logger.error(f"Failed to load {file_path}: {e}\n{error_details}")
            return []

    def collect_code_files(self) -> List[Path]:
        """Collect files that match the include/exclude patterns.

        Returns:
            List of file paths that match the criteria
        """
        import pathspec

        # Convert excluded patterns to pathspec
        # pathspec uses .gitignore style patterns which are compatible with our patterns
        spec = pathspec.PathSpec.from_lines(
            pathspec.patterns.GitWildMatchPattern, self.excluded_patterns or []
        )

        collected_files = []

        # Get the absolute path of the working directory
        abs_working_dir = Path(self.working_dir).resolve()

        for root, dirs, files in os.walk(abs_working_dir):
            root_path = Path(root)
            rel_root = root_path.relative_to(abs_working_dir).as_posix()

            # Skip this directory if it matches an excluded pattern
            # For root directory, use empty string instead of '.'
            dir_to_check = "" if rel_root == "." else rel_root
            if dir_to_check and spec.match_file(dir_to_check):
                # Remove this directory from dirs to prevent os.walk from descending into it
                if self.logger:
                    self.logger.debug(f"Skipping excluded directory: {rel_root}")
                dirs.clear()  # This prevents os.walk from descending into subdirs
                continue

            # Filter directories to skip any that match excluded patterns
            # This is more efficient than clearing dirs after matching
            i = 0
            while i < len(dirs):
                dir_path = f"{rel_root}/{dirs[i]}" if rel_root else dirs[i]
                if spec.match_file(dir_path):
                    if self.logger:
                        self.logger.debug(f"Skipping excluded directory: {dir_path}")
                    dirs.pop(i)  # Remove and don't increment i
                else:
                    i += 1  # Only increment if we didn't remove

            # Check each file
            for file in files:
                file_path = root_path / file
                rel_path = file_path.relative_to(abs_working_dir).as_posix()

                # First check if the file has an included extension
                if (
                    not self.included_extensions
                    or file_path.suffix in self.included_extensions
                ):
                    # Then check if it matches any excluded pattern
                    if not spec.match_file(rel_path):
                        collected_files.append(file_path)
                        if self.logger:
                            self.logger.debug(f"Found file: {rel_path}")
                    elif self.logger:
                        self.logger.debug(f"Skipping excluded file: {rel_path}")

        if self.logger:
            self.logger.debug(f"Found {len(collected_files)} files to process")
        return collected_files

    def _enhance_metadata(self, doc: Document, file_path: Path) -> None:
        """Attach useful metadata to a document.

        Note: This method is deprecated and no longer used.
        The functionality has been integrated directly into load_file.

        Args:
            doc: Document to enhance
            file_path: Path to the source file
        """
        # This method is no longer used
        pass
