"""Vector store management for Docstra."""

from pathlib import Path
from typing import Optional, List, Dict, Any

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

from docstra.core.config import DocstraConfig
from docstra.core.interfaces import IVectorStore


class ChromaVectorStore(IVectorStore):
    """Chroma vector store implementation."""

    def __init__(
        self,
        persist_dir: Path,
        config: DocstraConfig,
        logger: Optional[object] = None,
    ):
        """Initialize the vector store.

        Args:
            persist_dir: Directory to persist the vector store
            config: Docstra configuration
            logger: Optional logger instance
        """
        self.persist_dir = persist_dir
        self.config = config
        self.logger = logger
        self.store = self._create_store()

    def _create_store(self) -> Chroma:
        """Create or load the Chroma vector store.

        Returns:
            Chroma vector store instance
        """
        # Create embeddings model
        embeddings = OpenAIEmbeddings(
            openai_api_key=self.config.openai_api_key,
            model=self.config.embedding_model or "text-embedding-3-small",
        )

        # Create or load vector store
        return Chroma(
            persist_directory=str(self.persist_dir),
            embedding_function=embeddings,
        )

    def add_documents(self, documents: List[Document]) -> None:
        """Add documents to the vector store.

        Args:
            documents: List of Document objects to add
        """
        texts = [doc.page_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        self.store.add_texts(texts=texts, metadatas=metadatas)

    def add_texts(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
    ) -> List[str]:
        """Add texts to the vector store.

        Args:
            texts: List of texts to add
            metadatas: Optional list of metadata for each text
            ids: Optional list of IDs for each text

        Returns:
            List of IDs for the added texts
        """
        return self.store.add_texts(texts=texts, metadatas=metadatas, ids=ids)

    def similarity_search(
        self,
        query: str,
        k: int = 4,
        filter: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Search for similar texts.

        Args:
            query: Query text
            k: Number of results to return
            filter: Optional filter for the search

        Returns:
            List of similar documents with scores
        """
        docs = self.store.similarity_search(query, k=k, filter=filter)
        return [{"text": doc.page_content, "metadata": doc.metadata} for doc in docs]

    def delete(self, ids: Optional[List[str]] = None) -> None:
        """Delete texts from the vector store.

        Args:
            ids: Optional list of IDs to delete. If None, deletes everything.
        """
        if ids:
            self.store.delete(ids=ids)
        else:
            self.store._collection.delete()

    def persist(self) -> None:
        """Persist the vector store to disk."""
        self.store.persist()

    def get(self) -> Dict[str, Any]:
        """Get all documents from the vector store.

        Returns:
            Dictionary containing all documents and their metadata
        """
        result = self.store.get()
        # Ensure documents is a list to avoid "Documents is not a list" warning
        if isinstance(result, dict) and "documents" in result:
            return result
        elif isinstance(result, list):
            return {"documents": result}
        else:
            # Default to empty list if structure is unexpected
            return {"documents": []}

    def get_last_modified(self, file_path: str) -> float:
        """Get the last modified time of a file in the index.

        Args:
            file_path: Path to the file

        Returns:
            Last modified timestamp or 0 if not found
        """
        # For now, just return 0 to force reindexing
        return 0

    def clear(self) -> None:
        """Clear all documents from the vector store."""
        self.store._collection.delete()

    def search(
        self, query: str, k: int = 4, filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar texts.

        Args:
            query: Query text
            k: Number of results to return
            filter: Optional filter for the search

        Returns:
            List of similar documents with scores
        """
        docs = self.store.similarity_search(query, k=k, filter=filter)
        return [{"text": doc.page_content, "metadata": doc.metadata} for doc in docs]


def create_vectorstore(
    persist_dir: Path,
    config: DocstraConfig,
    logger: Optional[object] = None,
) -> ChromaVectorStore:
    """Create or load a vector store for document storage.

    Args:
        persist_dir: Directory to persist the vector store
        config: Docstra configuration
        logger: Optional logger instance

    Returns:
        ChromaVectorStore instance
    """
    return ChromaVectorStore(persist_dir=persist_dir, config=config, logger=logger)
