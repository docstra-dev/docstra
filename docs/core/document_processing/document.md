---
language: documenttype.markdown
source_file: /Users/jorgenosberg/development/docstra/docs/core/document_processing/document.md
summary: 'Document Type: Python

  File Path: /Users/jorgenosberg/development/docstra/docs/core/documentprocessing/document.md'
title: document

---

Document Type: Python
File Path: /Users/jorgenosberg/development/docstra/docs/core/document_processing/document.md

Overview
--------

This module provides classes and functions for representing code documents and their metadata. It allows for the creation of metadata from file paths, parsing of code content, and organization of code chunks.

Classes
-------

### DocumentMetadata

Represents metadata for a document.

#### Attributes

*   `filepath`: The path to the document.
*   `language`: The programming language of the document (e.g., Python, JavaScript).
*   `size_bytes`: The size of the document in bytes.
*   `last_modified`: The last modified timestamp.
*   `line_count`: The number of lines in the document.
*   `imports`: A list of imports used in the document.
*   `classes`: A list of classes defined in the document.
*   `functions`: A list of functions defined in the document.
*   `symbols`: A dictionary mapping symbols to line numbers.
*   `module_docstring`: An optional module-level docstring if present.

#### Methods

*   `from_file(filepath)`: Creates metadata from a file path.

    ```python
# Create metadata from a file path
metadata = DocumentMetadata.from_file("/path/to/file.py")
```

### CodeChunk

Represents a chunk of code with its context.

#### Attributes

*   `content`: The content of the chunk.
*   `start_line`: The start line of the chunk.
*   `end_line`: The end line of the chunk.
*   `symbols`: A list of symbols in this chunk.
*   `chunk_type`: The type of the chunk (e.g., function, class).
*   `parent_symbols`: A list of parent symbols (containing classes/functions).

#### Methods

None.

### Document

Represents a code document with its content and metadata.

#### Attributes

*   `content`: The content of the document.
*   `metadata`: The metadata of the document.
*   `chunks`: A list of chunks in the document.
*   `embedding_id`: An optional ID in the embedding database.

#### Methods

*   `from_file(filepath)`: Creates a document from a file path.

    ```python
# Create a document from a file path
document = Document.from_file("/path/to/file.py")
```

Functions
---------

### DocumentMetadata.from_file

Creates metadata from a file path.

#### Parameters

*   `filepath`: The path to the file (str or Path).

#### Returns

A `DocumentMetadata` object.

    ```python
# Create metadata from a file path
metadata = DocumentMetadata.from_file("/path/to/file.py")
```

### Document.from_file

Creates a document from a file path.

#### Parameters

*   `filepath`: The path to the file (str or Path).

#### Returns

A `Document` object.

    ```python
# Create a document from a file path
document = Document.from_file("/path/to/file.py")
```

Important Dependencies and Relationships
--------------------------------------

This module depends on the following modules:

*   `docstra.core`: Provides core functionality for Docstra.
*   `docstra.embedding`: Provides embedding database functionality.

Usage Examples
--------------

### Creating Metadata from a File Path

```python
# Create metadata from a file path
metadata = DocumentMetadata.from_file("/path/to/file.py")
```

### Creating a Document from a File Path

```python
# Create a document from a file path
document = Document.from_file("/path/to/file.py")
```

Notes and Limitations
--------------------

*   This module assumes that the input files are in UTF-8 encoding.
*   The `DocumentMetadata` class does not handle edge cases where the file is empty or contains only whitespace.
*   The `Document` class does not handle edge cases where the file content is malformed.

Edge Cases and Limitations
-------------------------

*   If the input file is empty, an empty `DocumentMetadata` object will be created.
*   If the input file contains only whitespace, an empty `Document` object will be created.
*   If the input file is not a valid Python file, an error will occur.

API Documentation
-----------------

### DocumentMetadata

#### Attributes

| Attribute | Type | Description |
| --- | --- | --- |
| filepath | str or Path | The path to the document. |
| language | str | The programming language of the document (e.g., Python, JavaScript). |
| size_bytes | int | The size of the document in bytes. |
| last_modified | datetime | The last modified timestamp. |
| line_count | int | The number of lines in the document. |
| imports | list | A list of imports used in the document. |
| classes | list | A list of classes defined in the document. |
| functions | list | A list of functions defined in the document. |
| symbols | dict | A dictionary mapping symbols to line numbers. |
| module_docstring | str | An optional module-level docstring if present. |

#### Methods

| Method | Parameters | Returns |
| --- | --- | --- |
| from_file(filepath) | filepath (str or Path) | A `DocumentMetadata` object. |

### CodeChunk

#### Attributes

| Attribute | Type | Description |
| --- | --- | --- |
| content | str | The content of the chunk. |
| start_line | int | The start line of the chunk. |
| end_line | int | The end line of the chunk. |
| symbols | list | A list of symbols in this chunk. |
| chunk_type | str | The type of the chunk (function, class, etc.). |
| parent_symbols | list | Parent symbols (containing class/function). |

#### Methods

None.

### Document

#### Attributes

| Attribute | Type | Description |
| --- | --- | --- |
| content | str | The content of the document. |
| metadata | DocumentMetadata | Metadata of the document. |
| chunks | list | A list of chunks in the document. |
| embedding_id | str | An optional ID in the embedding database. |

#### Methods

| Method | Parameters | Returns |
| --- | --- | --- |
| from_file(filepath) | filepath (str or Path) | A `Document` object.

```python
# Create a new file with proper documentation formatting.
# File: /Users/jorgenosberg/development/docstra/docs/core/document_processing/document.md

# Document Type: Python
# File Path: /Users/jorgenosberg/development/docstra/docs/core/document_processing/document.md

# Overview
#--------

# This module provides classes and functions for representing code documents and their metadata.
# It allows for the creation of metadata from file paths, parsing of code content, and organization of code chunks.

# Classes
#-------

### DocumentMetadata

Represents metadata for a document.

#### Attributes

*   `filepath`: The path to the document.
*   `language`: The programming language of the document (e.g., Python, JavaScript).
*   `size_bytes`: The size of the document in bytes.
*   `last_modified`: The last modified timestamp.
*   `line_count`: The number of lines in the document.
*   `imports`: A list of imports used in the document.
*   `classes`: A list of classes defined in the document.
*   `functions`: A list of functions defined in the document.
*   `symbols`: A dictionary mapping symbols to line numbers.
*   `module_docstring`: An optional module-level docstring if present.

#### Methods

*   `from_file(filepath)`: Creates metadata from a file path.

    ```python
# Create metadata from a file path
metadata = DocumentMetadata.from_file("/path/to/file.py")
```

### CodeChunk

Represents a chunk of code with its context.

#### Attributes

*   `content`: The content of the chunk.
*   `start_line`: The start line of the chunk.
*   `end_line`: The end line of the chunk.
*   `symbols`: A list of symbols in this chunk.
*   `chunk_type`: The type of the chunk (function, class, etc.).
*   `parent_symbols`: Parent symbols (containing class/function).

#### Methods

None.

### Document

Represents a code document with its content and metadata.

#### Attributes

*   `content`: The content of the document.
*   `metadata`: The metadata of the document.
*   `chunks`: A list of chunks in the document.
*   `embedding_id`: An optional ID in the embedding database.

#### Methods

*   `from_file(filepath)`: Creates a document from a file path.

    ```python
# Create a document from a file path
document = Document.from_file("/path/to/file.py")
```

Functions
---------

### DocumentMetadata.from_file

Creates metadata from a file path.

#### Parameters

*   `filepath`: The path to the file (str or Path).

#### Returns

A `DocumentMetadata` object.

    ```python
# Create metadata from a file path
metadata = DocumentMetadata.from_file("/path/to/file.py")
```

### Document.from_file

Creates a document from a file path.

#### Parameters

*   `filepath`: The path to the file (str or Path).

#### Returns

A `Document` object.

    ```python
# Create a document from a file path
document = Document.from_file("/path/to/file.py")
```

Important Dependencies and Relationships
--------------------------------------

This module depends on the following modules:

*   `docstra.core`: Provides core functionality for Docstra.
*   `docstra.embedding`: Provides embedding database functionality.

Usage Examples
--------------

### Creating Metadata from a File Path

```python
# Create metadata from a file path
metadata = DocumentMetadata.from_file("/path/to/file.py")
```

### Creating a Document from a File Path

```python
# Create a document from a file path
document = Document.from_file("/path/to/file.py")
```

Notes and Limitations
--------------------

*   This module assumes that the input files are in UTF-8 encoding.
*   The `DocumentMetadata` class does not handle edge cases where the file is empty or contains only whitespace.
*   The `Document` class does not handle edge cases where the file content is malformed.

Edge Cases and Limitations
-------------------------

*   If the input file is empty, an empty `DocumentMetadata` object will be created.
*   If the input file contains only whitespace, an empty `Document` object will be created.
*   If the input file is not a valid Python file, an error will occur.

API Documentation
-----------------

### DocumentMetadata

#### Attributes

| Attribute | Type | Description |
| --- | --- | --- |
| filepath | str or Path | The path to the document. |
| language | str | The programming language of the document (e.g., Python, JavaScript). |
| size_bytes | int | The size of the document in bytes. |
| last_modified | datetime | The last modified timestamp. |
| line_count | int | The number of lines in the document. |
| imports | list | A list of imports used in the document. |
| classes | list | A list of classes defined in the document. |
| functions | list | A list of functions defined in the document. |
| symbols | dict | A dictionary mapping symbols to line numbers. |
| module_docstring | str | An optional module-level docstring if present. |

#### Methods

| Method | Parameters | Returns |
| --- | --- | --- |
| from_file(filepath) | filepath (str or Path) | A `DocumentMetadata` object.

### CodeChunk

#### Attributes

| Attribute | Type | Description |
| --- | --- | --- |
| content | str | The content of the chunk. |
| start_line | int | The start line of the chunk. |
| end_line | int | The end line of the chunk. |
| symbols | list | A list of symbols in this chunk. |
| chunk_type | str | The type of the chunk (function, class, etc.). |
| parent_symbols | list | Parent symbols (containing class/function). |

#### Methods

None.

### Document

#### Attributes

| Attribute | Type | Description |
| --- | --- | --- |
| content | str | The content of the document. |
| metadata | DocumentMetadata | Metadata of the document. |
| chunks | list | A list of chunks in the document. |
| embedding_id | str | An optional ID in the embedding database. |

#### Methods

| Method | Parameters | Returns |
| --- | --- | --- |
| from_file(filepath) | filepath (str or Path) | A `Document` object.

```


## Source Code

```documenttype.markdown
---
language: documenttype.python
source_file: /Users/jorgenosberg/development/docstra/docstra/core/document_processing/document.py
summary: 'Document Type: Python

  File Path: /Users/jorgenosberg/development/docstra/docstra/core/documentprocessing/document.py'
title: document

---

Document Type: Python
File Path: /Users/jorgenosberg/development/docstra/docstra/core/document_processing/document.py

Overview
--------

This module provides classes and functions for representing code documents and their metadata. It allows for the creation of metadata from file paths, parsing of code content, and organization of code chunks.

Classes
-------

### DocumentMetadata

Represents metadata for a document.

#### Attributes

*   `filepath`: The path to the document.
*   `language`: The programming language of the document (e.g., Python, JavaScript).
*   `size_bytes`: The size of the document in bytes.
*   `last_modified`: The last modified timestamp.
*   `line_count`: The number of lines in the document.
*   `imports`: A list of imports used in the document.
*   `classes`: A list of classes defined in the document.
*   `functions`: A list of functions defined in the document.
*   `symbols`: A dictionary mapping symbols to line numbers.
*   `module_docstring`: An optional module-level docstring if present.

#### Methods

*   `from_file(filepath)`: Creates metadata from a file path.

    ```python
# Create metadata from a file path
metadata = DocumentMetadata.from_file("/path/to/file.py")
```

### CodeChunk

Represents a chunk of code with its context.

#### Attributes

*   `content`: The content of the chunk.
*   `start_line`: The start line of the chunk.
*   `end_line`: The end line of the chunk.
*   `symbols`: A list of symbols in this chunk.
*   `chunk_type`: The type of the chunk (e.g., function, class).
*   `parent_symbols`: A list of parent symbols (containing classes/functions).

#### Methods

None.

### Document

Represents a code document with its content and metadata.

#### Attributes

*   `content`: The content of the document.
*   `metadata`: The metadata of the document.
*   `chunks`: A list of chunks in the document.
*   `embedding_id`: An optional ID in the embedding database.

#### Methods

*   `from_file(filepath)`: Creates a document from a file path.

    ```python
# Create a document from a file path
document = Document.from_file("/path/to/file.py")
```

Functions
---------

### DocumentMetadata.from_file

Creates metadata from a file path.

#### Parameters

*   `filepath`: The path to the file (str or Path).

#### Returns

A `DocumentMetadata` object.

    ```python
# Create metadata from a file path
metadata = DocumentMetadata.from_file("/path/to/file.py")
```

### Document.from_file

Creates a document from a file path.

#### Parameters

*   `filepath`: The path to the file (str or Path).

#### Returns

A `Document` object.

    ```python
# Create a document from a file path
document = Document.from_file("/path/to/file.py")
```

Important Dependencies and Relationships
--------------------------------------

This module depends on the following modules:

*   `docstra.core`: Provides core functionality for Docstra.
*   `docstra.embedding`: Provides embedding database functionality.

Usage Examples
--------------

### Creating Metadata from a File Path

```python
# Create metadata from a file path
metadata = DocumentMetadata.from_file("/path/to/file.py")
```

### Creating a Document from a File Path

```python
# Create a document from a file path
document = Document.from_file("/path/to/file.py")
```

Notes and Limitations
--------------------

*   This module assumes that the input files are in UTF-8 encoding.
*   The `DocumentMetadata` class does not handle edge cases where the file is empty or contains only whitespace.
*   The `Document` class does not handle edge cases where the file content is malformed.

Edge Cases and Limitations
-------------------------

*   If the input file is empty, an empty `DocumentMetadata` object will be created.
*   If the input file contains only whitespace, an empty `Document` object will be created.
*   If the input file is not a valid Python file, an error will occur.

API Documentation
-----------------

### DocumentMetadata

#### Attributes

| Attribute | Type | Description |
| --- | --- | --- |
| filepath | str or Path | The path to the document. |
| language | str | The programming language of the document (e.g., Python, JavaScript). |
| size_bytes | int | The size of the document in bytes. |
| last_modified | datetime | The last modified timestamp. |
| line_count | int | The number of lines in the document. |
| imports | list | A list of imports used in the document. |
| classes | list | A list of classes defined in the document. |
| functions | list | A list of functions defined in the document. |
| symbols | dict | A dictionary mapping symbols to line numbers. |
| module_docstring | str | An optional module-level docstring if present. |

#### Methods

| Method | Parameters | Returns |
| --- | --- | --- |
| from_file(filepath) | filepath (str or Path) | A `DocumentMetadata` object. |

### CodeChunk

#### Attributes

| Attribute | Type | Description |
| --- | --- | --- |
| content | str | The content of the chunk. |
| start_line | int | The start line of the chunk. |
| end_line | int | The end line of the chunk. |
| symbols | list | A list of symbols in this chunk. |
| chunk_type | str | The type of the chunk (e.g., function, class). |
| parent_symbols | list | A list of parent symbols (containing classes/functions). |

#### Methods

None.

### Document

#### Attributes

| Attribute | Type | Description |
| --- | --- | --- |
| content | str | The content of the document. |
| metadata | DocumentMetadata | The metadata of the document. |
| chunks | list | A list of chunks in the document. |
| embedding_id | str | An optional ID in the embedding database. |

#### Methods

| Method | Parameters | Returns |
| --- | --- | --- |
| from_file(filepath) | filepath (str or Path) | A `Document` object. |

### DocumentMetadata.from_file

#### Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| filepath | str or Path | The path to the file. |

#### Returns

A `DocumentMetadata` object.

### Document.from_file

#### Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| filepath | str or Path | The path to the file. |

#### Returns

A `Document` object.


## Source Code

```documenttype.python
# File: ./docstra/core/document_processing/document.py
"""
Document models for representing code documents and their metadata.
"""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field


class DocumentType(str, Enum):
    """Types of code documents that can be processed."""

    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    GO = "go"
    RUST = "rust"
    CPP = "cpp"
    C = "c"
    CSHARP = "csharp"
    PHP = "php"
    RUBY = "ruby"
    SWIFT = "swift"
    KOTLIN = "kotlin"
    MARKDOWN = "markdown"
    TEXT = "text"
    OTHER = "other"


class DocumentMetadata(BaseModel):
    """Metadata for a document."""

    filepath: str = Field(..., description="Path to the document")
    language: DocumentType = Field(
        ..., description="Programming language of the document"
    )
    size_bytes: int = Field(..., description="Size of the document in bytes")
    last_modified: float = Field(..., description="Last modified timestamp")
    line_count: int = Field(0, description="Number of lines in the document")
    imports: List[str] = Field(
        default_factory=list, description="Imports used in the document"
    )
    classes: List[str] = Field(
        default_factory=list, description="Classes defined in the document"
    )
    functions: List[str] = Field(
        default_factory=list, description="Functions defined in the document"
    )
    symbols: Dict[str, List[int]] = Field(
        default_factory=dict, description="Symbol to line numbers mapping"
    )
    module_docstring: Optional[str] = Field(
        None, description="Module level docstring if present"
    )

    @classmethod
    def from_file(cls, filepath: Union[str, Path]) -> DocumentMetadata:
        """Create metadata from a file path."""
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"File {filepath} not found")

        size = path.stat().st_size
        mtime = path.stat().st_mtime

        # Determine language from file extension
        extension = path.suffix.lower()
        language = DocumentType.OTHER
        if extension == ".py":
            language = DocumentType.PYTHON
        elif extension in [".js", ".mjs", ".cjs", ".jsx"]:
            language = DocumentType.JAVASCRIPT
        elif extension in [".ts", ".tsx"]:
            language = DocumentType.TYPESCRIPT
        elif extension == ".java":
            language = DocumentType.JAVA
        elif extension == ".go":
            language = DocumentType.GO
        elif extension == ".rs":
            language = DocumentType.RUST
        elif extension in [".cpp", ".cc", ".cxx"]:
            language = DocumentType.CPP
        elif extension == ".c":
            language = DocumentType.C
        elif extension == ".cs":
            language = DocumentType.CSHARP
        elif extension == ".php":
            language = DocumentType.PHP
        elif extension == ".rb":
            language = DocumentType.RUBY
        elif extension == ".swift":
            language = DocumentType.SWIFT
        elif extension == ".kt":
            language = DocumentType.KOTLIN
        elif extension == ".md":
            language = DocumentType.MARKDOWN
        elif extension == ".txt":
            language = DocumentType.TEXT

        # Basic line count (will be enhanced by parser)
        line_count = sum(1 for _ in path.open("r", encoding="utf-8", errors="ignore"))

        return cls(
            filepath=str(path.absolute()),
            language=language,
            size_bytes=size,
            last_modified=mtime,
            line_count=line_count,
        )


class CodeChunk(BaseModel):
    """A chunk of code with its context."""

    content: str = Field(..., description="The content of the chunk")
    start_line: int = Field(..., description="Start line of the chunk")
    end_line: int = Field(..., description="End line of the chunk")
    symbols: List[str] = Field(
        default_factory=list, description="Symbols in this chunk"
    )
    chunk_type: str = Field(
        "code", description="Type of the chunk (function, class, etc.)"
    )
    parent_symbols: List[str] = Field(
        default_factory=list, description="Parent symbols (containing class/function)"
    )


class Document(BaseModel):
    """A code document with its content and metadata."""

    content: str = Field(..., description="The content of the document")
    metadata: DocumentMetadata = Field(..., description="Metadata of the document")
    chunks: List[CodeChunk] = Field(
        default_factory=list, description="Chunks of the document"
    )
    embedding_id: Optional[str] = Field(
        None, description="ID in the embedding database"
    )

    @classmethod
    def from_file(cls, filepath: Union[str, Path]) -> Document:
        """Create a document from a file path."""
        path = Path(filepath)
        metadata = DocumentMetadata.from_file(path)

        # Read file content with error handling
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            content = f"Error reading file: {str(e)}"

        return cls(content=content, metadata=metadata)

```

```
