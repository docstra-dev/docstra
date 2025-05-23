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
