---
language: documenttype.markdown
source_file: /Users/jorgenosberg/development/docstra/docs/core/indexing/repo_map.md
summary: 'Repository Map

  ================'
title: repo_map

---

Repository Map
================

Overview
--------

The `RepositoryMap` class is a data structure that represents a repository's directory structure and file metadata. It provides methods for building, querying, and manipulating the repository map.

Implementation Details
--------------------

The `RepositoryMap` class uses a tree-like data structure to store the repository's directory structure and file metadata. Each node in the tree represents a directory or file, and contains attributes such as its path, size, symbols (e.g., classes, functions), and imports.

**Classes**
-----------

### RepositoryMap

*   **Attributes:**

    *   `root`: The root directory of the repository map.
    *   `index`: An optional codebase index for enhanced metadata.
*   **Methods:**

    *   `__init__(root_path, index=None)`: Initializes a new instance of the `RepositoryMap` class.
    *   `get_or_create_directory(path)`: Creates or returns an existing directory node at the specified path.
    *   `add_file(file_path, metadata)`: Adds a new file node to the repository map with the given metadata.
    *   `find_file(file_path)`: Finds a file node by its path.
    *   `find_directory(dir_path)`: Finds a directory node by its path.
    *   `get_file_dependencies(file_path)`: Gets the dependencies of a file based on imports.
    *   `get_related_files(file_path)`: Gets related files to a given file.
    *   `to_dict()`: Converts the repository map to a dictionary.

### DirectoryNode

*   **Attributes:**

    *   `path`: The path of the directory node.
*   **Methods:**

    *   `__init__(parent, path)`: Initializes a new instance of the `DirectoryNode` class.
    *   `add_file(file_path, metadata)`: Adds a new file node to the directory.

### FileNode

*   **Attributes:**

    *   `path`: The path of the file node.
    *   `size`: The size of the file.
    *   `symbols`: A list of symbols (e.g., classes, functions) associated with the file.
    *   `imports`: A list of imports used by the file.
*   **Methods:**

    *   `__init__(parent, path, metadata)`: Initializes a new instance of the `FileNode` class.

**Functions**
-------------

### from_documents(documents, root_path, index=None)

Creates a repository map from a list of documents. The `root_path` parameter specifies the root directory of the repository map, and the `index` parameter is an optional codebase index for enhanced metadata.

**Usage Examples**
-----------------

```python
repo_map = RepositoryMap("/path/to/repo")
file_node = repo_map.find_file("/path/to/file.py")
print(file_node.size)  # prints the size of the file

dependencies = repo_map.get_file_dependencies("/path/to/file.py")
print(dependencies)  # prints a list of dependencies for the file
```

**Important Dependencies**
-------------------------

The `RepositoryMap` class depends on the following modules:

*   `Document`: Represents a document in the repository.
*   `CodebaseIndex`: Provides metadata about files and directories in the repository.

**Notes**
-------

*   The `RepositoryMap` class uses a tree-like data structure to store directory and file nodes. This allows for efficient querying and manipulation of the repository map.
*   The `find_file` method returns `None` if the file is not found in the repository map.
*   The `get_related_files` method returns an empty list if no related files are found.

```python
import os

class Document:
    def __init__(self, filepath, metadata):
        self.filepath = filepath
        self.metadata = metadata

class CodebaseIndex:
    def get_file_metadata(self, file_path):
        # implementation omitted for brevity
        pass

class RepositoryMap:
    def __init__(self, root_path, index=None):
        self.root = DirectoryNode(None, root_path)
        self.index = index

    def find_file(self, file_path):
        # implementation omitted for brevity
        pass

    def get_file_dependencies(self, file_path):
        # implementation omitted for brevity
        pass

    def get_related_files(self, file_path):
        # implementation omitted for brevity
        pass

class DirectoryNode:
    def __init__(self, parent, path):
        self.parent = parent
        self.path = path

class FileNode:
    def __init__(self, parent, path, metadata):
        self.parent = parent
        self.path = path
        self.size = metadata.get("size", 0)
        self.symbols = metadata.get("symbols", [])
        self.imports = metadata.get("imports", [])

def from_documents(documents, root_path, index=None):
    repo_map = RepositoryMap(root_path, index)
    # implementation omitted for brevity
    return repo_map
```


## Source Code

```documenttype.markdown
---
language: documenttype.python
source_file: /Users/jorgenosberg/development/docstra/docstra/core/indexing/repo_map.py
summary: 'Repository Map

  ================'
title: repo_map

---

**Repository Map**
================

Overview
--------

The `RepositoryMap` class is a data structure that represents a repository's directory structure and file metadata. It provides methods for building, querying, and manipulating the repository map.

Implementation Details
--------------------

The `RepositoryMap` class uses a tree-like data structure to store the repository's directory structure and file metadata. Each node in the tree represents a directory or file, and contains attributes such as its path, size, symbols (e.g., classes, functions), and imports.

**Classes**
-----------

### RepositoryMap

*   **Attributes:**

    *   `root`: The root directory of the repository map.
    *   `index`: An optional codebase index for enhanced metadata.
*   **Methods:**

    *   `__init__(root_path, index=None)`: Initializes a new instance of the `RepositoryMap` class.
    *   `get_or_create_directory(path)`: Creates or returns an existing directory node at the specified path.
    *   `add_file(file_path, metadata)`: Adds a new file node to the repository map with the specified metadata.
    *   `to_dict()`: Converts the repository map to a dictionary representation.

### DirectoryNode

*   **Attributes:**

    *   `path`: The path of the directory node.
    *   `children`: A list of child directory nodes.
    *   `files`: A list of file nodes in the directory.
*   **Methods:**

    *   `__init__(path)`: Initializes a new instance of the `DirectoryNode` class.

### FileNode

*   **Attributes:**

    *   `path`: The path of the file node.
    *   `size`: The size of the file in bytes.
    *   `symbols`: A list of symbols (e.g., classes, functions) associated with the file.
    *   `imports`: A list of imported files.
*   **Methods:**

    *   `__init__(path, metadata)`: Initializes a new instance of the `FileNode` class.

**Functions**
-------------

### from_documents(documents, root_path, index=None)

*   **Parameters:**

    *   `documents`: A list of documents to create the repository map from.
    *   `root_path`: The root path of the repository.
    *   `index`: An optional codebase index for enhanced metadata.
*   **Returns:** A new instance of the `RepositoryMap` class.

**Usage Examples**
-----------------

```python
# Create a new repository map from documents
documents = [...]  # list of documents
root_path = "/path/to/repository"
repo_map = RepositoryMap.from_documents(documents, root_path)

# Add files to the repository map
file_paths = ["file1.py", "file2.py"]
for file_path in file_paths:
    metadata = {"size_bytes": 1024, "classes": ["Class1"], "functions": ["Function1"]}
    repo_map.add_file(file_path, metadata)

# Get a list of files with imports
imported_files = repo_map.get_file_dependencies("/path/to/file.py")
print(imported_files)
```

**Important Dependencies**
-------------------------

The `RepositoryMap` class depends on the following modules:

*   `docstra.core.indexing.codebase_index`: Provides an optional codebase index for enhanced metadata.
*   `docstra.core.indexing.document`: Represents a document with metadata.

**Notes**
-------

*   The `RepositoryMap` class uses a tree-like data structure to store the repository's directory structure and file metadata. This allows for efficient querying and manipulation of the repository map.
*   The `from_documents` function creates a new instance of the `RepositoryMap` class from a list of documents. It assumes that each document has a `metadata` attribute with relevant information (e.g., file path, size, symbols).
*   The `get_file_dependencies` method returns a list of files that are imported by a given file. This can be used to analyze dependencies between files in the repository.


## Source Code

```documenttype.python
# File: ./docstra/core/indexing/repo_map.py
"""
Repository mapping for understanding codebase structure.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional, Union

from docstra.core.document_processing.document import Document
from docstra.core.indexing.code_index import CodebaseIndex


class FileNode:
    """Node representing a file in the repository structure."""

    def __init__(self, name: str, path: str, language: Optional[str] = None):
        """Initialize a file node.

        Args:
            name: File name
            path: Full path to the file
            language: Programming language of the file
        """
        self.name = name
        self.path = path
        self.language = language
        self.size: Optional[int] = None
        self.symbols: List[str] = []
        self.imports: List[str] = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation.

        Returns:
            Dictionary representation of the node
        """
        return {
            "type": "file",
            "name": self.name,
            "path": self.path,
            "language": self.language,
            "size": self.size,
            "symbols": self.symbols,
            "imports": self.imports,
        }


class DirectoryNode:
    """Node representing a directory in the repository structure."""

    def __init__(self, name: str, path: str):
        """Initialize a directory node.

        Args:
            name: Directory name
            path: Full path to the directory
        """
        self.name = name
        self.path = path
        self.children: Dict[str, Union[FileNode, DirectoryNode]] = {}

    def add_file(self, file_path: str, language: Optional[str] = None) -> FileNode:
        """Add a file to this directory.

        Args:
            file_path: Path to the file
            language: Programming language of the file

        Returns:
            The created file node
        """
        file_name = os.path.basename(file_path)
        node = FileNode(file_name, file_path, language)
        self.children[file_name] = node
        return node

    def add_directory(self, dir_path: str) -> DirectoryNode:
        """Add a subdirectory to this directory.

        Args:
            dir_path: Path to the directory

        Returns:
            The created directory node
        """
        dir_name = os.path.basename(dir_path)
        node = DirectoryNode(dir_name, dir_path)
        self.children[dir_name] = node
        return node

    def get_or_create_directory(self, dir_path: str) -> DirectoryNode:
        """Get a directory node, creating it if it doesn't exist.

        Args:
            dir_path: Path to the directory

        Returns:
            The directory node
        """
        dir_name = os.path.basename(dir_path)

        if dir_name in self.children and isinstance(
            self.children[dir_name], DirectoryNode
        ):
            return self.children[dir_name]

        return self.add_directory(dir_path)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation.

        Returns:
            Dictionary representation of the node
        """
        return {
            "type": "directory",
            "name": self.name,
            "path": self.path,
            "children": {
                name: child.to_dict() for name, child in sorted(self.children.items())
            },
        }


class RepositoryMap:
    """Map representing the structure of a code repository."""

    def __init__(self, root_path: str, index: Optional[CodebaseIndex] = None):
        """Initialize the repository map.

        Args:
            root_path: Root path of the repository
            index: Optional codebase index for enhanced metadata
        """
        self.root_path = os.path.normpath(root_path)
        self.root = DirectoryNode(os.path.basename(root_path), self.root_path)
        self.index = index
        self.exclude_patterns: List[str] = [
            ".git",
            "__pycache__",
            "node_modules",
            "venv",
            ".env",
            ".vscode",
            ".idea",
            ".pytest_cache",
        ]

    def should_exclude(self, path: str) -> bool:
        """Check if a path should be excluded from the map.

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

    def build(self) -> None:
        """Build the repository map by traversing the filesystem."""
        self._traverse_directory(self.root_path, self.root)

        # Enhance with metadata from the index if available
        if self.index:
            self._enhance_with_index()

    def _traverse_directory(self, dir_path: str, node: DirectoryNode) -> None:
        """Recursively traverse a directory and build the map.

        Args:
            dir_path: Path to the directory
            node: Directory node representing the directory
        """
        try:
            for entry in os.scandir(dir_path):
                if self.should_exclude(entry.path):
                    continue

                if entry.is_file():
                    # Add file to the current directory node
                    file_node = node.add_file(entry.path)

                    # Determine language from file extension
                    _, ext = os.path.splitext(entry.name)
                    language = self._get_language_from_extension(ext)
                    if language:
                        file_node.language = language

                    # Set file size
                    file_node.size = entry.stat().st_size

                elif entry.is_dir():
                    # Add directory and recursively traverse it
                    dir_node = node.add_directory(entry.path)
                    self._traverse_directory(entry.path, dir_node)

        except Exception as e:
            # Handle permission errors and other issues
            print(f"Error traversing {dir_path}: {str(e)}")

    def _get_language_from_extension(self, ext: str) -> Optional[str]:
        """Determine programming language from file extension.

        Args:
            ext: File extension

        Returns:
            Language name if recognized, None otherwise
        """
        ext = ext.lower()

        language_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".java": "java",
            ".go": "go",
            ".rs": "rust",
            ".cpp": "cpp",
            ".cc": "cpp",
            ".cxx": "cpp",
            ".c": "c",
            ".h": "c",
            ".hpp": "cpp",
            ".cs": "csharp",
            ".php": "php",
            ".rb": "ruby",
            ".swift": "swift",
            ".kt": "kotlin",
            ".md": "markdown",
            ".txt": "text",
            ".html": "html",
            ".css": "css",
            ".sql": "sql",
            ".json": "json",
            ".xml": "xml",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".toml": "toml",
        }

        return language_map.get(ext)

    def _enhance_with_index(self) -> None:
        """Enhance the map with metadata from the codebase index."""
        if not self.index:
            return

        def _enhance_node(node: Union[FileNode, DirectoryNode]) -> None:
            """Recursively enhance nodes with index metadata."""
            if isinstance(node, FileNode):
                # Enhance file nodes
                metadata = self.index.get_file_metadata(node.path)
                if metadata:
                    node.language = metadata.get("language", node.language)
                    node.symbols = metadata.get("classes", []) + metadata.get(
                        "functions", []
                    )
                    node.imports = metadata.get("imports", [])

            elif isinstance(node, DirectoryNode):
                # Recursively enhance child nodes
                for child in node.children.values():
                    _enhance_node(child)

        # Start enhancement from the root
        _enhance_node(self.root)

    def find_file(self, file_path: str) -> Optional[FileNode]:
        """Find a file node by path.

        Args:
            file_path: Path to the file

        Returns:
            File node if found, None otherwise
        """
        file_path = os.path.normpath(file_path)

        # Find relative path from root
        rel_path = os.path.relpath(file_path, self.root_path)
        if rel_path.startswith(".."):
            # File is outside the repository
            return None

        parts = rel_path.split(os.sep)
        current = self.root

        # Navigate to parent directory
        for i, part in enumerate(parts[:-1]):
            if part in current.children and isinstance(
                current.children[part], DirectoryNode
            ):
                current = current.children[part]
            else:
                return None

        # Check if file exists in the directory
        file_name = parts[-1]
        if file_name in current.children and isinstance(
            current.children[file_name], FileNode
        ):
            return current.children[file_name]

        return None

    def find_directory(self, dir_path: str) -> Optional[DirectoryNode]:
        """Find a directory node by path.

        Args:
            dir_path: Path to the directory

        Returns:
            Directory node if found, None otherwise
        """
        dir_path = os.path.normpath(dir_path)

        # Find relative path from root
        rel_path = os.path.relpath(dir_path, self.root_path)
        if rel_path.startswith(".."):
            # Directory is outside the repository
            return None

        parts = rel_path.split(os.sep)
        if parts == ["."]:
            # Root directory
            return self.root

        current = self.root

        # Navigate to the directory
        for part in parts:
            if part in current.children and isinstance(
                current.children[part], DirectoryNode
            ):
                current = current.children[part]
            else:
                return None

        return current

    def get_file_dependencies(self, file_path: str) -> List[str]:
        """Get dependencies of a file based on imports.

        Args:
            file_path: Path to the file

        Returns:
            List of file paths that are imported by the file
        """
        if not self.index:
            return []

        file_node = self.find_file(file_path)
        if not file_node:
            return []

        # Use index to find imported files
        imported_files = []
        for import_stmt in file_node.imports:
            # This is a simplified approach. A more sophisticated implementation
            # would resolve import statements to actual files.
            files = self.index.search_files_by_import(import_stmt)
            imported_files.extend(files)

        return imported_files

    def get_related_files(self, file_path: str) -> List[str]:
        """Get files related to a given file.

        Args:
            file_path: Path to the file

        Returns:
            List of related file paths
        """
        if not self.index:
            return []

        return self.index.get_related_files(file_path)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the repository map to a dictionary.

        Returns:
            Dictionary representation of the map
        """
        return self.root.to_dict()

    @staticmethod
    def from_documents(
        documents: List[Document], root_path: str, index: Optional[CodebaseIndex] = None
    ) -> RepositoryMap:
        """Create a repository map from a list of documents.

        Args:
            documents: List of documents
            root_path: Root path of the repository
            index: Optional codebase index for enhanced metadata

        Returns:
            Repository map
        """
        repo_map = RepositoryMap(root_path, index)

        # Build directory structure
        for document in documents:
            file_path = document.metadata.filepath

            # Skip if outside root path
            if not os.path.commonpath([root_path, file_path]).startswith(root_path):
                continue

            # Get relative path from root
            rel_path = os.path.relpath(file_path, root_path)
            parts = rel_path.split(os.sep)

            current = repo_map.root

            # Create directories
            for i, part in enumerate(parts[:-1]):
                dir_path = os.path.join(root_path, *parts[: i + 1])
                current = current.get_or_create_directory(dir_path)

            # Add file
            file_name = parts[-1]
            file_node = current.add_file(file_path, str(document.metadata.language))

            # Add metadata
            file_node.size = document.metadata.size_bytes
            file_node.symbols = document.metadata.classes + document.metadata.functions
            file_node.imports = document.metadata.imports

        return repo_map

```

```
