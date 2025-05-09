---
language: documenttype.markdown
source_file: /Users/jorgenosberg/development/docstra/docs/core/ingestion/storage.md
summary: 'ChromaDB Storage Module

  =========================='
title: storage

---

# ChromaDB Storage Module
==========================

## Overview

The ChromaDB storage module is a Python package that provides an interface to store and retrieve data in ChromaDB, a NoSQL database. This module allows users to easily interact with ChromaDB from their Python applications.

## Classes

### `ChromaDBStorage`

*   **Attributes:**
    *   `connection`: The connection object to the ChromaDB database.
*   **Methods:**

    *   `__init__(self, host, port, username, password)`: Initializes a new instance of the `ChromaDBStorage` class with the provided connection details.
    *   `add_document(self, document_id, content, metadata)`: Adds a new document to the ChromaDB database.
    *   `get_document(self, document_id)`: Retrieves a document from the ChromaDB database by its ID.
    *   `delete_document(self, document_id)`: Deletes a document from the ChromaDB database by its ID.

### `DocumentIndexer`

*   **Attributes:**
    *   `storage`: The ChromaDB storage object used to interact with the database.
    *   `embedding_generator`: A generator that produces embeddings for documents and chunks.
*   **Methods:**

    *   `__init__(self, storage, embedding_generator)`: Initializes a new instance of the `DocumentIndexer` class with the provided ChromaDB storage object and embedding generator.
    *   `_prepare_metadata_for_chroma(self, metadata)`: Converts document metadata to ChromaDB-compatible format.
    *   `index_document(self, document)`: Indexes a single document in the ChromaDB database.
    *   `index_documents(self, documents)`: Indexes multiple documents in the ChromaDB database.

## Functions

### `add_document(storage, document_id, content, metadata)`

*   **Parameters:**
    *   `document_id`: The ID of the document to be added.
    *   `content`: The content of the document.
    *   `metadata`: The metadata of the document.
*   **Return Value:** None

### `get_document(storage, document_id)`

*   **Parameters:**
    *   `document_id`: The ID of the document to be retrieved.
*   **Return Value:** A dictionary containing the document's content and metadata.

### `delete_document(storage, document_id)`

*   **Parameters:**
    *   `document_id`: The ID of the document to be deleted.
*   **Return Value:** None

## Usage Examples

```python
# Create a new ChromaDB storage object with connection details
storage = ChromaDBStorage("localhost", 27017, "username", "password")

# Create a new DocumentIndexer instance with the storage object and embedding generator
indexer = DocumentIndexer(storage, MyEmbeddingGenerator())

# Define a sample document
document = SampleDocument(
    content="This is a sample document.",
    metadata={"author": "John Doe"},
)

# Index the document using the DocumentIndexer
indexer.index_document(document)
```

```python
# Create a new ChromaDB storage object with connection details
storage = ChromaDBStorage("localhost", 27017, "username", "password")

# Define multiple sample documents
documents = [
    SampleDocument(
        content="This is another sample document.",
        metadata={"author": "Jane Doe"},
    ),
    SampleDocument(
        content="This is yet another sample document.",
        metadata={"author": "Bob Smith"},
    ),
]

# Index the documents using the DocumentIndexer
indexer.index_documents(documents)
```

## Important Dependencies and Relationships

The ChromaDB storage module depends on the following:

*   `pymongo`: A Python driver for MongoDB, which is used to interact with ChromaDB.
*   `MyEmbeddingGenerator`: A custom generator that produces embeddings for documents and chunks.

The DocumentIndexer class has a dependency on the ChromaDBStorage object, which provides an interface to the ChromaDB database.


## Source Code

```documenttype.markdown
---
language: documenttype.python
source_file: /Users/jorgenosberg/development/docstra/docstra/core/ingestion/storage.py
summary: 'Storage for Document Embeddings using ChromaDB

  ============================================='
title: storage

---

# Storage for Document Embeddings using ChromaDB
=============================================

## Overview

This module provides a storage solution for document embeddings using ChromaDB. It allows users to store and retrieve document embeddings, along with their corresponding metadata.

## Classes

### `ChromaDBStorage`

#### Attributes

*   `persist_directory`: The directory where ChromaDB data is persisted.
*   `client`: A ChromaDB client instance used for interacting with the database.

#### Methods

*   `__init__(persist_directory: str = ".docstra/chroma")`: Initializes the ChromaDB storage.
*   `_validate_metadata(metadata: Dict[str, Any]) -> Dict[str, Union[str, int, float, bool]]`: Validates and converts metadata to ChromaDB-compatible format.
*   `add_chunks(chunk_ids: List[str], contents: List[str], metadatas: List[Dict[str, Any]], embeddings: Optional[List[List[float]]] = None) -> List[str]`: Adds multiple chunks to the storage.
*   `add_document(document_id: str, content: str, metadata: Dict[str, Any], embedding: Optional[List[float]] = None) -> str`: Adds a document to the storage.
*   `add_documents(documents: List[Document], embeddings: Dict[str, Dict[str, List[float]]]) -> List[str]`: Adds multiple documents and their chunks to the storage.
*   `search_documents(query_embedding: List[float], n_results: int = 10, **filters) -> List[Dict[str, Any]]`: Searches for documents by embedding similarity.
*   `search_chunks(query_embedding: List[float], n_results: int = 20, **filters) -> List[Dict[str, Any]]`: Searches for document chunks by embedding similarity.
*   `get_document(document_id: str) -> Optional[Dict[str, Any]]`: Retrieves a document by ID.
*   `get_chunks_for_document(document_id: str) -> List[Dict[str, Any]]`: Retrieves all chunks for a document.
*   `delete_document(document_id: str) -> bool`: Deletes a document and its chunks.
*   `clear() -> None`: Clears all collections.

### `DocumentIndexer`

#### Attributes

*   `storage`: A ChromaDB storage instance used for interacting with the database.
*   `embedding_generator`: A generator for creating embeddings.

#### Methods

*   `__init__(storage: ChromaDBStorage, embedding_generator: Any)`: Initializes the document indexer.
*   `_prepare_metadata_for_chroma(metadata: Dict[str, Any]) -> dict`: Converts document metadata to ChromaDB-compatible format.
*   `index_document(document: Document) -> str`: Indexes a document.
*   `index_documents(documents: List[Document]) -> List[str]`: Indexes multiple documents.

## Usage Examples

### Adding Documents and Chunks

```python
storage = ChromaDBStorage(persist_directory=".docstra/chroma")

# Create a new document
document = Document(content="This is the content of the document.", metadata={"filepath": "example.txt", "language": "en"})

# Index the document
doc_id = storage.index_document(document)

# Add chunks to the document
chunk1 = Chunk(content="Chunk 1", start_line=1, end_line=5)
chunk2 = Chunk(content="Chunk 2", start_line=6, end_line=10)

storage.add_chunks(chunk_ids=[f"{doc_id}#{i}" for i in range(2)], contents=[chunk1.content, chunk2.content], metadatas=[{"document_id": doc_id, "chunk_index": 0}, {"document_id": doc_id, "chunk_index": 1}], embeddings=[generate_embedding(chunk1.content), generate_embedding(chunk2.content)])
```

### Searching for Documents

```python
query_embedding = [1.0, 2.0, 3.0]

# Search for documents by embedding similarity
results = storage.search_documents(query_embedding)

for result in results:
    print(result["id"], result["content"], result["metadata"])
```

## Important Dependencies and Relationships

This module depends on the `chromadb` library for interacting with ChromaDB.

The `DocumentIndexer` class uses the `ChromaDBStorage` instance to store and retrieve document embeddings. The `embedding_generator` is used to create embeddings for documents and chunks.

## Notes

*   This implementation assumes that the `generate_embedding` function is available to generate embeddings for documents and chunks.
*   The `_validate_metadata` method converts metadata to ChromaDB-compatible format, which may require additional processing depending on the specific requirements of your application.


## Source Code

```documenttype.python
# File: ./docstra/core/ingestion/storage.py

"""
Storage for document embeddings using ChromaDB.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional, Union

import chromadb

from docstra.core.document_processing.document import Document


class ChromaDBStorage:
    """Storage for document embeddings using ChromaDB."""

    def __init__(self, persist_directory: str = ".docstra/chroma"):
        """Initialize the ChromaDB storage.

        Args:
            persist_directory: Directory to persist ChromaDB data
        """
        self.persist_directory = persist_directory

        # Ensure the directory exists
        os.makedirs(persist_directory, exist_ok=True)

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=persist_directory)

        # Create collections for different types of data
        self.document_collection = self.client.get_or_create_collection(
            name="documents", metadata={"description": "Complete documents"}
        )

        self.chunk_collection = self.client.get_or_create_collection(
            name="chunks", metadata={"description": "Document chunks"}
        )

    def _validate_metadata(
        self, metadata: Dict[str, Any]
    ) -> Dict[str, Union[str, int, float, bool]]:
        """Validate and convert metadata to ChromaDB-compatible format.

        Args:
            metadata: Metadata dictionary

        Returns:
            ChromaDB-compatible metadata dictionary
        """
        if not metadata:
            return {}

        result = {}

        for key, value in metadata.items():
            # Handle different types
            if isinstance(value, (str, int, float, bool)):
                # Basic types are supported as-is
                result[key] = value
            elif isinstance(value, list):
                # Convert list to string
                if not value:
                    result[key] = "[]"
                else:
                    result[key] = ", ".join(str(item) for item in value)
            elif isinstance(value, dict):
                # Convert dict to string
                if not value:
                    result[key] = "{}"
                else:
                    import json

                    result[key] = json.dumps(value)
            elif value is None:
                # Skip None values
                continue
            else:
                # Convert anything else to string
                result[key] = str(value)

        return result

    def add_chunks(
        self,
        chunk_ids: List[str],
        contents: List[str],
        metadatas: List[Dict[str, Any]],
        embeddings: Optional[List[List[float]]] = None,
    ) -> List[str]:
        """Add multiple chunks to the storage.

        Args:
            chunk_ids: List of chunk IDs
            contents: List of chunk contents
            metadatas: List of chunk metadata dictionaries
            embeddings: Optional list of chunk embeddings

        Returns:
            List of chunk IDs
        """
        if not chunk_ids:
            return []

        # Validate and convert all metadata
        safe_metadatas = [self._validate_metadata(meta) for meta in metadatas]

        try:
            self.chunk_collection.add(
                ids=chunk_ids,
                documents=contents,
                metadatas=safe_metadatas,
                embeddings=embeddings,
            )
            return chunk_ids
        except Exception as e:
            print(f"Error adding chunks to storage: {str(e)}")
            raise

    def add_document(
        self,
        document_id: str,
        content: str,
        metadata: Dict[str, Any],
        embedding: Optional[List[float]] = None,
    ) -> str:
        """Add a document to the storage.

        Args:
            document_id: Document ID
            content: Document content
            metadata: Document metadata
            embedding: Optional document embedding

        Returns:
            Document ID
        """
        # Validate and convert metadata
        safe_metadata = self._validate_metadata(metadata)

        try:
            self.document_collection.add(
                ids=[document_id],
                documents=[content],
                metadatas=[safe_metadata],
                embeddings=[embedding] if embedding else None,
            )
            return document_id
        except Exception as e:
            print(f"Error adding document to storage: {str(e)}")
            raise

    def add_documents(
        self, documents: List[Document], embeddings: Dict[str, Dict[str, List[float]]]
    ) -> List[str]:
        """Add multiple documents and their chunks to the storage.

        Args:
            documents: The documents to add
            embeddings: Embeddings for the documents and their chunks

        Returns:
            List of document IDs
        """
        document_ids = []

        for document in documents:
            doc_id = document.metadata.filepath
            doc_embeddings = embeddings.get(doc_id, {})

            if doc_embeddings:
                document_embedding = doc_embeddings.get(doc_id, [])
                document_ids.append(
                    self.add_document(document, document_embedding, doc_embeddings)
                )

        return document_ids

    def search_documents(
        self, query_embedding: List[float], n_results: int = 10, **filters
    ) -> List[Dict[str, Any]]:
        """Search for documents by embedding similarity.

        Args:
            query_embedding: The query embedding
            n_results: Number of results to return
            **filters: Additional filters to apply

        Returns:
            List of matching documents
        """
        # Prepare filter query if filters provided
        where = {}
        if filters:
            where = {k: v for k, v in filters.items() if v is not None}

        # Perform the search
        results = self.document_collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where if where else None,
        )

        # Format the results
        formatted_results = []
        if results["ids"] and results["documents"]:
            for i, doc_id in enumerate(results["ids"][0]):
                formatted_results.append(
                    {
                        "id": doc_id,
                        "content": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "score": (
                            results["distances"][0][i]
                            if "distances" in results
                            else None
                        ),
                    }
                )

        return formatted_results

    def search_chunks(
        self, query_embedding: List[float], n_results: int = 20, **filters
    ) -> List[Dict[str, Any]]:
        """Search for document chunks by embedding similarity.

        Args:
            query_embedding: The query embedding
            n_results: Number of results to return
            **filters: Additional filters to apply

        Returns:
            List of matching chunks
        """
        # Prepare filter query if filters provided
        where = {}
        if filters:
            where = {k: v for k, v in filters.items() if v is not None}

        # Perform the search
        results = self.chunk_collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where if where else None,
        )

        # Format the results
        formatted_results = []
        if results["ids"] and results["documents"]:
            for i, chunk_id in enumerate(results["ids"][0]):
                formatted_results.append(
                    {
                        "id": chunk_id,
                        "content": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "score": (
                            results["distances"][0][i]
                            if "distances" in results
                            else None
                        ),
                    }
                )

        return formatted_results

    def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get a document by ID.

        Args:
            document_id: The document ID

        Returns:
            The document if found, None otherwise
        """
        try:
            result = self.document_collection.get(ids=[document_id])

            if result["ids"]:
                return {
                    "id": result["ids"][0],
                    "content": result["documents"][0],
                    "metadata": result["metadatas"][0],
                }
            return None
        except Exception:
            return None

    def get_chunks_for_document(self, document_id: str) -> List[Dict[str, Any]]:
        """Get all chunks for a document.

        Args:
            document_id: The document ID

        Returns:
            List of chunks for the document
        """
        try:
            results = self.chunk_collection.get(where={"document_id": document_id})

            formatted_results = []
            if results["ids"]:
                for i, chunk_id in enumerate(results["ids"]):
                    formatted_results.append(
                        {
                            "id": chunk_id,
                            "content": results["documents"][i],
                            "metadata": results["metadatas"][i],
                        }
                    )

            return formatted_results
        except Exception:
            return []

    def delete_document(self, document_id: str) -> bool:
        """Delete a document and its chunks.

        Args:
            document_id: The document ID

        Returns:
            True if successful, False otherwise
        """
        try:
            # Delete the document
            self.document_collection.delete(ids=[document_id])

            # Delete all chunks for the document
            self.chunk_collection.delete(where={"document_id": document_id})

            return True
        except Exception:
            return False

    def clear(self) -> None:
        """Clear all collections."""
        self.document_collection.delete(where={})
        self.chunk_collection.delete(where={})


class DocumentIndexer:
    """Index documents in ChromaDB."""

    def __init__(self, storage: ChromaDBStorage, embedding_generator: Any):
        """Initialize the document indexer.

        Args:
            storage: ChromaDB storage
            embedding_generator: Generator for creating embeddings
        """
        self.storage = storage
        self.embedding_generator = embedding_generator

    def _prepare_metadata_for_chroma(self, metadata) -> dict:
        """Convert document metadata to ChromaDB-compatible format.

        Args:
            metadata: Original document metadata

        Returns:
            ChromaDB-compatible metadata dictionary
        """
        # Create a new dictionary with processed values
        chroma_metadata = {}

        # Convert metadata to dictionary
        metadata_dict = metadata.dict() if hasattr(metadata, "dict") else metadata

        # Process each metadata field
        for key, value in metadata_dict.items():
            # Handle different types
            if isinstance(value, (str, int, float, bool)):
                # Scalar values can be used as-is
                chroma_metadata[key] = value
            elif isinstance(value, list):
                # Convert lists to string representation
                if not value:  # Empty list
                    chroma_metadata[key] = "[]"
                else:
                    # Join list items as string
                    chroma_metadata[key] = ", ".join(str(item) for item in value)
            elif isinstance(value, dict):
                # Convert dictionaries to string representation
                if not value:  # Empty dict
                    chroma_metadata[key] = "{}"
                else:
                    # Convert dict to JSON string
                    import json

                    chroma_metadata[key] = json.dumps(value)
            elif value is None:
                # Skip None values
                continue
            else:
                # Convert other types to string
                chroma_metadata[key] = str(value)

        return chroma_metadata

    def index_document(self, document: Document) -> str:
        """Index a document.

        Args:
            document: Document to index

        Returns:
            Document ID
        """
        # Generate embeddings for the document
        doc_embedding = self.embedding_generator.generate_embedding(document.content)

        # Convert document metadata to ChromaDB-compatible format
        doc_metadata = self._prepare_metadata_for_chroma(document.metadata)

        # Add document to storage
        doc_id = self.storage.add_document(
            document_id=document.metadata.filepath,
            content=document.content,
            metadata=doc_metadata,
            embedding=doc_embedding,
        )

        # Index document chunks if any exist
        if document.chunks:
            chunk_ids = []
            chunk_contents = []
            chunk_metadatas = []
            chunk_embeddings = []

            # Process each chunk
            for i, chunk in enumerate(document.chunks):
                # Generate chunk ID
                chunk_id = f"{doc_id}#{i}"

                # Generate chunk embedding
                chunk_embedding = self.embedding_generator.generate_embedding(
                    chunk.content
                )

                # Create chunk metadata
                chunk_metadata = {
                    "document_id": document.metadata.filepath,
                    "chunk_index": i,
                    "start_line": chunk.start_line,
                    "end_line": chunk.end_line,
                    "chunk_type": chunk.chunk_type,
                    "symbols": chunk.symbols,
                    "parent_symbols": chunk.parent_symbols,
                    "language": str(document.metadata.language),
                }

                # Convert chunk metadata to ChromaDB-compatible format
                chroma_chunk_metadata = self._prepare_metadata_for_chroma(
                    chunk_metadata
                )

                # Collect chunk data
                chunk_ids.append(chunk_id)
                chunk_contents.append(chunk.content)
                chunk_metadatas.append(chroma_chunk_metadata)
                chunk_embeddings.append(chunk_embedding)

            # Add chunks to storage in batch
            if chunk_ids:
                self.storage.add_chunks(
                    chunk_ids=chunk_ids,
                    contents=chunk_contents,
                    metadatas=chunk_metadatas,
                    embeddings=chunk_embeddings,
                )

        return doc_id

    def index_documents(self, documents: List[Document]) -> List[str]:
        """Index multiple documents.

        Args:
            documents: Documents to index

        Returns:
            List of document IDs
        """
        doc_ids = []

        for doc in documents:
            try:
                doc_id = self.index_document(doc)
                doc_ids.append(doc_id)
            except Exception as e:
                print(f"Error indexing document {doc.metadata.filepath}: {str(e)}")

        return doc_ids

```

```
