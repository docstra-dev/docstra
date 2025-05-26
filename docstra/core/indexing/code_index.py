# File: ./docstra/core/indexing/code_index.py
"""
Codebase indexing for efficient search and retrieval of code elements.
"""

from __future__ import annotations

import json
import os
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from docstra.core.document_processing.document import Document, DocumentType


class CodebaseIndex:
    """Index for efficient search and retrieval of code elements."""

    def __init__(self, index_directory: str = ".docstra/index"):
        """Initialize the codebase index.

        Args:
            index_directory: Directory to store the index
        """
        self.index_directory = index_directory

        # Ensure the directory exists
        os.makedirs(index_directory, exist_ok=True)

        # Initialize index structures
        self.symbol_index: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.file_index: Dict[str, Dict[str, Any]] = {}
        self.import_index: Dict[str, List[str]] = defaultdict(list)
        self.function_index: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.class_index: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

        # Load existing indexes if they exist
        self._load_indexes()

    def _load_indexes(self) -> None:
        """Load existing indexes from disk."""
        symbol_index_path = Path(self.index_directory) / "symbol_index.json"
        file_index_path = Path(self.index_directory) / "file_index.json"
        import_index_path = Path(self.index_directory) / "import_index.json"
        function_index_path = Path(self.index_directory) / "function_index.json"
        class_index_path = Path(self.index_directory) / "class_index.json"

        if symbol_index_path.exists():
            with open(symbol_index_path, "r") as f:
                self.symbol_index = defaultdict(list, json.load(f))

        if file_index_path.exists():
            with open(file_index_path, "r") as f:
                self.file_index = json.load(f)

        if import_index_path.exists():
            with open(import_index_path, "r") as f:
                self.import_index = defaultdict(list, json.load(f))

        if function_index_path.exists():
            with open(function_index_path, "r") as f:
                self.function_index = defaultdict(list, json.load(f))

        if class_index_path.exists():
            with open(class_index_path, "r") as f:
                self.class_index = defaultdict(list, json.load(f))

    def _save_indexes(self) -> None:
        """Save indexes to disk."""
        symbol_index_path = Path(self.index_directory) / "symbol_index.json"
        file_index_path = Path(self.index_directory) / "file_index.json"
        import_index_path = Path(self.index_directory) / "import_index.json"
        function_index_path = Path(self.index_directory) / "function_index.json"
        class_index_path = Path(self.index_directory) / "class_index.json"

        with open(symbol_index_path, "w") as f:
            json.dump(dict(self.symbol_index), f)

        with open(file_index_path, "w") as f:
            json.dump(self.file_index, f)

        with open(import_index_path, "w") as f:
            json.dump(dict(self.import_index), f)

        with open(function_index_path, "w") as f:
            json.dump(dict(self.function_index), f)

        with open(class_index_path, "w") as f:
            json.dump(dict(self.class_index), f)

    def index_document(self, document: Document) -> None:
        """Index a document.

        Args:
            document: Document to index
        """
        # Extract document path and normalize it
        filepath = document.metadata.filepath
        filepath = os.path.normpath(filepath)

        # Index file metadata
        self.file_index[filepath] = {
            "filepath": filepath,
            "language": str(document.metadata.language),
            "size_bytes": document.metadata.size_bytes,
            "line_count": document.metadata.line_count,
            "last_modified": document.metadata.last_modified,
            "classes": document.metadata.classes,
            "functions": document.metadata.functions,
            "imports": document.metadata.imports,
        }

        # Index symbols
        for symbol, lines in document.metadata.symbols.items():
            for line in lines:
                self.symbol_index[symbol].append(
                    {
                        "filepath": filepath,
                        "line": line,
                        "language": str(document.metadata.language),
                    }
                )

        # Index imports
        for import_stmt in document.metadata.imports:
            self.import_index[import_stmt].append(filepath)

        # Index functions
        for function_name in document.metadata.functions:
            self.function_index[function_name].append(
                {
                    "filepath": filepath,
                    "language": str(document.metadata.language),
                }
            )

        # Index classes
        for class_name in document.metadata.classes:
            self.class_index[class_name].append(
                {
                    "filepath": filepath,
                    "language": str(document.metadata.language),
                }
            )

        # Save the updated indexes
        self._save_indexes()

    def index_documents(self, documents: List[Document]) -> None:
        """Index multiple documents.

        Args:
            documents: Documents to index
        """
        for document in documents:
            self.index_document(document)

    def search_symbol(self, symbol: str) -> List[Dict[str, Any]]:
        """Search for a symbol in the codebase.

        Args:
            symbol: Symbol to search for

        Returns:
            List of locations where the symbol is defined
        """
        return self.symbol_index.get(symbol, [])

    def search_function(self, function_name: str) -> List[Dict[str, Any]]:
        """Search for a function in the codebase.

        Args:
            function_name: Function name to search for

        Returns:
            List of locations where the function is defined
        """
        return self.function_index.get(function_name, [])

    def search_class(self, class_name: str) -> List[Dict[str, Any]]:
        """Search for a class in the codebase.

        Args:
            class_name: Class name to search for

        Returns:
            List of locations where the class is defined
        """
        return self.class_index.get(class_name, [])

    def get_files_by_language(self, language: Union[DocumentType, str]) -> List[str]:
        """Get all files of a specific language.

        Args:
            language: Language to filter by

        Returns:
            List of file paths
        """
        language_str = str(language)
        return [
            filepath
            for filepath, metadata in self.file_index.items()
            if metadata["language"] == language_str
        ]

    def get_file_metadata(self, filepath: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a specific file.

        Args:
            filepath: Path to the file

        Returns:
            File metadata if found, None otherwise
        """
        filepath = os.path.normpath(filepath)
        return self.file_index.get(filepath)

    def search_files_by_import(self, import_stmt: str) -> List[str]:
        """Find files that use a specific import.

        Args:
            import_stmt: Import statement to search for

        Returns:
            List of file paths that use the import
        """
        # Try exact match first
        if import_stmt in self.import_index:
            return self.import_index[import_stmt]

        # Try partial matching if exact match not found
        results = []
        for idx, files in self.import_index.items():
            if import_stmt in idx:
                results.extend(files)

        return list(set(results))  # Remove duplicates

    def full_text_search(self, query: str) -> List[Dict[str, Any]]:
        """Perform a simple full-text search across the codebase.

        This is a basic implementation. For more sophisticated full-text search,
        a dedicated search engine like Elasticsearch would be better.

        Args:
            query: Text to search for

        Returns:
            List of matches with file and context information
        """
        results = []

        for filepath, metadata in self.file_index.items():
            try:
                # Read the file content
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                # Check if query exists in content
                if query.lower() in content.lower():
                    # Find line numbers with matches
                    lines = content.splitlines()
                    matches = []

                    for i, line in enumerate(lines):
                        if query.lower() in line.lower():
                            matches.append(
                                {
                                    "line_number": i + 1,
                                    "line_content": line.strip(),
                                }
                            )

                    if matches:
                        results.append(
                            {
                                "filepath": filepath,
                                "language": metadata["language"],
                                "matches": matches,
                            }
                        )
            except Exception:
                # Skip files that can't be read
                continue

        return results

    def get_related_files(self, filepath: str) -> List[str]:
        """Find files that are related to a given file.

        Files are considered related if they:
        - Share imports
        - Import each other
        - Define or use the same symbols

        Args:
            filepath: Path to the file

        Returns:
            List of related file paths
        """
        filepath = os.path.normpath(filepath)
        related_files = set()

        # Get file metadata
        metadata = self.get_file_metadata(filepath)
        if not metadata:
            return []

        # Find files with shared imports
        for import_stmt in metadata["imports"]:
            related_files.update(self.search_files_by_import(import_stmt))

        # Find files defining symbols used in this file
        for symbol in self.symbol_index:
            # Check if this symbol is used in our file
            for location in self.symbol_index[symbol]:
                if location["filepath"] == filepath:
                    # Find other files defining this symbol
                    for other_location in self.symbol_index[symbol]:
                        if other_location["filepath"] != filepath:
                            related_files.add(other_location["filepath"])

        # Find files using functions defined in this file
        for function_name in metadata["functions"]:
            for location in self.function_index.get(function_name, []):
                if location["filepath"] != filepath:
                    related_files.add(location["filepath"])

        # Find files using classes defined in this file
        for class_name in metadata["classes"]:
            for location in self.class_index.get(class_name, []):
                if location["filepath"] != filepath:
                    related_files.add(location["filepath"])

        # Remove the original file from the results
        if filepath in related_files:
            related_files.remove(filepath)

        return list(related_files)

    def clear(self) -> None:
        """Clear all indexes."""
        self.symbol_index.clear()
        self.file_index.clear()
        self.import_index.clear()
        self.function_index.clear()
        self.class_index.clear()
        self._save_indexes()


class CodebaseIndexer:
    """Index a codebase for efficient search and retrieval."""

    def __init__(
        self,
        index_directory: str = ".docstra/index",
        exclude_patterns: Optional[List[str]] = None,
    ):
        """Initialize the codebase indexer.

        Args:
            index_directory: Directory to store the index
            exclude_patterns: Patterns to exclude from indexing
        """
        self.index = CodebaseIndex(index_directory=index_directory)
        self.exclude_patterns = exclude_patterns or [
            ".git",
            "__pycache__",
            ".mypy_cache",
            ".ruff_cache",
            ".pytest_cache",
            ".coverage",
            ".tox",
            ".nox",
            "node_modules",
            "venv",
            ".venv",
            "env",
            ".env",
            ".vscode",
            ".idea",
            "build",
            "dist",
        ]

    def should_exclude(self, path: str) -> bool:
        """Check if a path should be excluded from indexing.

        Args:
            path: Path to check

        Returns:
            True if the path should be excluded, False otherwise
        """
        path_norm = os.path.normpath(path)

        for pattern in self.exclude_patterns:
            if pattern in path_norm:
                return True

        return False

    def index_document(self, document: Document) -> None:
        """Index a document.

        Args:
            document: Document to index
        """
        if not self.should_exclude(document.metadata.filepath):
            self.index.index_document(document)

    def index_documents(self, documents: List[Document]) -> None:
        """Index multiple documents.

        Args:
            documents: Documents to index
        """
        filtered_documents = [
            doc for doc in documents if not self.should_exclude(doc.metadata.filepath)
        ]

        self.index.index_documents(filtered_documents)

    def get_index(self) -> CodebaseIndex:
        """Get the underlying codebase index.

        Returns:
            The codebase index
        """
        return self.index
