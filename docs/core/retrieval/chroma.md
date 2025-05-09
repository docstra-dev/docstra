---
language: documenttype.markdown
source_file: /Users/jorgenosberg/development/docstra/docs/core/retrieval/chroma.md
summary: 'Chroma Retrieval Module

  =========================='
title: chroma

---

Chroma Retrieval Module
==========================

The Chroma retrieval module is a part of the Docstra framework, providing a way to retrieve documents and chunks from a database using ChromaDB. This module allows users to search for documents and chunks based on various criteria such as query strings, file paths, languages, and context values.

Overview
--------

The Chroma retrieval module uses ChromaDB as its underlying storage system. It provides a flexible and efficient way to retrieve data from the database, allowing users to search for documents and chunks based on different criteria.

Classes
-------

### `ChromaRetriever`

The `ChromaRetriever` class is the main class in this module, responsible for retrieving documents and chunks from ChromaDB. It takes two parameters in its constructor:

*   `storage`: An instance of `ChromaDBStorage`, which is used to interact with the ChromaDB database.
*   `embedding_generator`: An instance of `EmbeddingGenerator`, which is used to generate embeddings for query strings.

#### Attributes

*   `storage`: The ChromaDB storage instance.
*   `embedding_generator`: The embedding generator instance.

#### Methods

### `__init__(self, storage: ChromaDBStorage, embedding_generator: EmbeddingGenerator)`

Initializes the `ChromaRetriever` instance with the provided storage and embedding generator.

```python
def __init__(
    self, storage: ChromaDBStorage, embedding_generator: EmbeddingGenerator
):
    """Initialize the ChromaDB retriever.

    Args:
        storage: ChromaDB storage
        embedding_generator: Generator for creating embeddings
    """
```

### `retrieve_documents(self, query: str, n_results: int = 10, **filters) -> List[Dict[str, Any]]`

Retrieves documents from ChromaDB based on the provided query string and filters.

```python
def retrieve_documents(
    self, query: str, n_results: int = 10, **filters
) -> List[Dict[str, Any]]:
    """Retrieve documents by similarity to a query.

    Args:
        query: Query string
        n_results: Number of results to return
        **filters: Additional filters to apply

    Returns:
        List of matching documents
    """
```

### `retrieve_chunks(self, query: str, n_results: int = 20, **filters) -> List[Dict[str, Any]]`

Retrieves chunks from ChromaDB based on the provided query string and filters.

```python
def retrieve_chunks(
    self, query: str, n_results: int = 20, **filters
) -> List[Dict[str, Any]]:
    """Retrieve document chunks by similarity to a query.

    Args:
        query: Query string
        n_results: Number of results to return
        **filters: Additional filters to apply

    Returns:
        List of matching chunks
    """
```

### `retrieve_by_context(self, query: str, context_type: str, context_value: str, n_results: int = 20) -> List[Dict[str, Any]]`

Retrieves chunks from ChromaDB based on the provided query string and context filters.

```python
def retrieve_by_context(
    self, query: str, context_type: str, context_value: str, n_results: int = 20
) -> List[Dict[str, Any]]:
    """Retrieve chunks filtered by a specific context.

    Args:
        query: Query string
        context_type: Type of context to filter by (e.g., "language", "document_id")
        context_value: Value to filter on
        n_results: Number of results to return

    Returns:
        List of matching chunks
    """
```

### `retrieve_by_filepath(self, query: str, filepath: str, n_results: int = 20) -> List[Dict[str, Any]]`

Retrieves chunks from ChromaDB based on the provided query string and file path filters.

```python
def retrieve_by_filepath(
    self, query: str, filepath: str, n_results: int = 20
) -> List[Dict[str, Any]]:
    """Retrieve chunks filtered by a specific file path.

    Args:
        query: Query string
        filepath: Path to the file
        n_results: Number of results to return

    Returns:
        List of matching chunks
    """
```

### `retrieve_by_language(self, query: str, language: str, n_results: int = 20) -> List[Dict[str, Any]]`

Retrieves chunks from ChromaDB based on the provided query string and language filters.

```python
def retrieve_by_language(
    self, query: str, language: str, n_results: int = 20
) -> List[Dict[str, Any]]:
    """Retrieve chunks filtered by a specific language.

    Args:
        query: Query string
        language: Programming language
        n_results: Number of results to return

    Returns:
        List of matching chunks
    """
```

Functions
---------

### `get_embedding(self, query: str) -> Dict[str, Any]`

Generates an embedding for the provided query string.

```python
def get_embedding(self, query: str) -> Dict[str, Any]:
    """Generate an embedding for the provided query string.

    Args:
        query: Query string

    Returns:
        Dictionary containing the generated embedding
    """
```

Usage Examples
-------------

### Retrieving Documents

```python
# Create a ChromaRetriever instance
retriever = ChromaRetriever(storage, embedding_generator)

# Retrieve documents based on a query string
documents = retriever.retrieve_documents(query="example query")

# Print the retrieved documents
for document in documents:
    print(document)
```

### Retrieving Chunks

```python
# Create a ChromaRetriever instance
retriever = ChromaRetriever(storage, embedding_generator)

# Retrieve chunks based on a query string and filters
chunks = retriever.retrieve_chunks(query="example query", n_results=10)

# Print the retrieved chunks
for chunk in chunks:
    print(chunk)
```

Important Dependencies
--------------------

The `ChromaRetriever` class depends on the following modules:

*   `ChromaDBStorage`: Provides a way to interact with the ChromaDB database.
*   `EmbeddingGenerator`: Generates embeddings for query strings.

These dependencies are required for the `ChromaRetriever` class to function correctly.

Source Code
-----------

```python
# File: ./docstra/core/retrieval/chroma.py

"""
Document retrieval using ChromaDB.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from docstra.core.ingestion.embeddings import EmbeddingGenerator
from docstra.core.ingestion.storage import ChromaDBStorage


class ChromaRetriever:
    def __init__(self, storage: ChromaDBStorage, embedding_generator: EmbeddingGenerator):
        self.storage = storage
        self.embedding_generator = embedding_generator

    # ... (rest of the class definition)
```

```


## Source Code

```documenttype.markdown
---
language: documenttype.python
source_file: /Users/jorgenosberg/development/docstra/docstra/core/retrieval/chroma.py
summary: 'Chroma Retrieval Module

  =========================='
title: chroma

---

# Chroma Retrieval Module
==========================

## Overview

The Chroma retrieval module is a part of the Docstra framework, providing a way to retrieve documents and chunks from a database using ChromaDB. This module allows users to search for documents and chunks based on various criteria such as query strings, file paths, languages, and context values.

## Classes

### `ChromaRetriever`

The `ChromaRetriever` class is the main class in this module, responsible for retrieving documents and chunks from ChromaDB. It takes two parameters in its constructor:

*   `storage`: An instance of `ChromaDBStorage`, which is used to interact with the ChromaDB database.
*   `embedding_generator`: An instance of `EmbeddingGenerator`, which is used to generate embeddings for query strings.

#### Attributes

*   `storage`: The ChromaDB storage instance.
*   `embedding_generator`: The embedding generator instance.

#### Methods

### `__init__(self, storage: ChromaDBStorage, embedding_generator: EmbeddingGenerator)`

Initializes the `ChromaRetriever` instance with the provided storage and embedding generator.

```python
def __init__(
    self, storage: ChromaDBStorage, embedding_generator: EmbeddingGenerator
):
    """Initialize the ChromaDB retriever.

    Args:
        storage: ChromaDB storage
        embedding_generator: Generator for creating embeddings
    """
```

### `retrieve_documents(self, query: str, n_results: int = 10, **filters) -> List[Dict[str, Any]]`

Retrieves documents from ChromaDB based on the provided query string and filters.

```python
def retrieve_documents(
    self, query: str, n_results: int = 10, **filters
) -> List[Dict[str, Any]]:
    """Retrieve documents by similarity to a query.

    Args:
        query: Query string
        n_results: Number of results to return
        **filters: Additional filters to apply

    Returns:
        List of matching documents
    """
```

### `retrieve_chunks(self, query: str, n_results: int = 20, **filters) -> List[Dict[str, Any]]`

Retrieves chunks from ChromaDB based on the provided query string and filters.

```python
def retrieve_chunks(
    self, query: str, n_results: int = 20, **filters
) -> List[Dict[str, Any]]:
    """Retrieve document chunks by similarity to a query.

    Args:
        query: Query string
        n_results: Number of results to return
        **filters: Additional filters to apply

    Returns:
        List of matching chunks
    """
```

### `retrieve_by_context(self, query: str, context_type: str, context_value: str, n_results: int = 20) -> List[Dict[str, Any]]`

Retrieves chunks from ChromaDB based on the provided query string and context filters.

```python
def retrieve_by_context(
    self, query: str, context_type: str, context_value: str, n_results: int = 20
) -> List[Dict[str, Any]]:
    """Retrieve chunks filtered by a specific context.

    Args:
        query: Query string
        context_type: Type of context to filter by (e.g., "language", "document_id")
        context_value: Value to filter on
        n_results: Number of results to return

    Returns:
        List of matching chunks
    """
```

### `retrieve_by_filepath(self, query: str, filepath: str, n_results: int = 20) -> List[Dict[str, Any]]`

Retrieves chunks from ChromaDB based on the provided query string and file path filters.

```python
def retrieve_by_filepath(
    self, query: str, filepath: str, n_results: int = 20
) -> List[Dict[str, Any]]:
    """Retrieve chunks filtered by a specific file path.

    Args:
        query: Query string
        filepath: File path to filter by
        n_results: Number of results to return

    Returns:
        List of matching chunks
    """
```

### `retrieve_by_language(self, query: str, language: str, n_results: int = 20) -> List[Dict[str, Any]]`

Retrieves chunks from ChromaDB based on the provided query string and language filters.

```python
def retrieve_by_language(
    self, query: str, language: str, n_results: int = 20
) -> List[Dict[str, Any]]:
    """Retrieve chunks filtered by a specific language.

    Args:
        query: Query string
        language: Language to filter by
        n_results: Number of results to return

    Returns:
        List of matching chunks
    """
```

## Functions

### `get_embedding(self, query: str) -> Dict[str, Any]`

Generates an embedding for the provided query string.

```python
def get_embedding(self, query: str) -> Dict[str, Any]:
    """Generate an embedding for the provided query string.

    Args:
        query: Query string

    Returns:
        Dictionary containing the generated embedding
    """
```

## Usage Examples

### Retrieving Documents

```python
# Create a ChromaRetriever instance
retriever = ChromaRetriever(storage, embedding_generator)

# Retrieve documents based on a query string
documents = retriever.retrieve_documents(query="example query")

# Print the retrieved documents
for document in documents:
    print(document)
```

### Retrieving Chunks

```python
# Create a ChromaRetriever instance
retriever = ChromaRetriever(storage, embedding_generator)

# Retrieve chunks based on a query string and filters
chunks = retriever.retrieve_chunks(query="example query", n_results=10)

# Print the retrieved chunks
for chunk in chunks:
    print(chunk)
```

## Important Dependencies

The `ChromaRetriever` class depends on the following modules:

*   `ChromaDBStorage`: Provides a way to interact with the ChromaDB database.
*   `EmbeddingGenerator`: Generates embeddings for query strings.

These dependencies are required for the `ChromaRetriever` class to function correctly.


## Source Code

```documenttype.python
# File: ./docstra/core/retrieval/chroma.py

"""
Document retrieval using ChromaDB.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from docstra.core.ingestion.embeddings import EmbeddingGenerator
from docstra.core.ingestion.storage import ChromaDBStorage


class ChromaRetriever:
    """Retriever for documents and chunks using ChromaDB."""

    def __init__(
        self, storage: ChromaDBStorage, embedding_generator: EmbeddingGenerator
    ):
        """Initialize the ChromaDB retriever.

        Args:
            storage: ChromaDB storage
            embedding_generator: Generator for creating embeddings
        """
        self.storage = storage
        self.embedding_generator = embedding_generator

    def retrieve_documents(
        self, query: str, n_results: int = 10, **filters
    ) -> List[Dict[str, Any]]:
        """Retrieve documents by similarity to a query.

        Args:
            query: Query string
            n_results: Number of results to return
            **filters: Additional filters to apply

        Returns:
            List of matching documents
        """
        # Generate embedding for the query
        query_embedding = self.embedding_generator.generate_embedding(query)

        # Search for similar documents
        results = self.storage.search_documents(
            query_embedding=query_embedding, n_results=n_results, **filters
        )

        return results

    def retrieve_chunks(
        self, query: str, n_results: int = 20, **filters
    ) -> List[Dict[str, Any]]:
        """Retrieve document chunks by similarity to a query.

        Args:
            query: Query string
            n_results: Number of results to return
            **filters: Additional filters to apply

        Returns:
            List of matching chunks
        """
        # Generate embedding for the query
        query_embedding = self.embedding_generator.generate_embedding(query)

        # Search for similar chunks
        results = self.storage.search_chunks(
            query_embedding=query_embedding, n_results=n_results, **filters
        )

        return results

    def retrieve_by_context(
        self, query: str, context_type: str, context_value: str, n_results: int = 20
    ) -> List[Dict[str, Any]]:
        """Retrieve chunks filtered by a specific context.

        Args:
            query: Query string
            context_type: Type of context to filter by (e.g., "language", "document_id")
            context_value: Value to filter on
            n_results: Number of results to return

        Returns:
            List of matching chunks
        """
        # Apply context as a filter
        filters = {context_type: context_value}

        return self.retrieve_chunks(query=query, n_results=n_results, **filters)

    def retrieve_by_filepath(
        self, query: str, filepath: str, n_results: int = 20
    ) -> List[Dict[str, Any]]:
        """Retrieve chunks from a specific file.

        Args:
            query: Query string
            filepath: Path to the file
            n_results: Number of results to return

        Returns:
            List of matching chunks
        """
        return self.retrieve_by_context(
            query=query,
            context_type="document_id",
            context_value=filepath,
            n_results=n_results,
        )

    def retrieve_by_language(
        self, query: str, language: str, n_results: int = 20
    ) -> List[Dict[str, Any]]:
        """Retrieve chunks in a specific programming language.

        Args:
            query: Query string
            language: Programming language
            n_results: Number of results to return

        Returns:
            List of matching chunks
        """
        return self.retrieve_by_context(
            query=query,
            context_type="language",
            context_value=language,
            n_results=n_results,
        )

    def get_context_for_document(self, document_id: str) -> Dict[str, Any]:
        """Get the full context for a document.

        Args:
            document_id: Document ID

        Returns:
            Document and its chunks
        """
        document = self.storage.get_document(document_id)
        chunks = self.storage.get_chunks_for_document(document_id)

        return {"document": document, "chunks": chunks}

    def get_document_by_id(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get a document by ID.

        Args:
            document_id: Document ID

        Returns:
            The document if found, None otherwise
        """
        return self.storage.get_document(document_id)

    def get_chunks_for_document(self, document_id: str) -> List[Dict[str, Any]]:
        """Get all chunks for a document.

        Args:
            document_id: Document ID

        Returns:
            List of chunks for the document
        """
        return self.storage.get_chunks_for_document(document_id)

```

```
