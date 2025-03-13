"""Retriever service for Docstra."""

from typing import Any, Dict, List, Optional

from docstra.core.config import DocstraConfig
from docstra.core.interfaces import ILogger, IRetriever, IVectorStore


class DocstraRetriever(IRetriever):
    """Service for retrieving relevant documents from the vectorstore."""

    def __init__(
        self,
        vectorstore: IVectorStore,
        config: Optional[DocstraConfig] = None,
        logger: Optional[ILogger] = None,
    ):
        """Initialize the retriever.

        Args:
            vectorstore: Vectorstore instance
            config: Optional configuration instance
            logger: Optional logger instance
        """
        self.vectorstore = vectorstore
        self.config = config or DocstraConfig()
        self.logger = logger

        # Set default parameters
        self.max_results = self.config.max_context_chunks

    async def get_relevant_documents(self, query: str, k: int = None) -> List[Any]:
        """Get documents relevant to a query.

        Args:
            query: Query string
            k: Number of documents to retrieve (defaults to config value)

        Returns:
            List of relevant documents
        """
        if not self.vectorstore:
            if self.logger:
                self.logger.warning("No vectorstore available for retrieval")
            return []

        # Use provided k or default from config
        k = k or self.max_results

        try:
            # Search the vectorstore
            results = self.vectorstore.search(query, k=k)

            if self.logger:
                self.logger.debug(
                    f"Retrieved {len(results)} documents for query: {query}"
                )

            return results
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error retrieving documents: {str(e)}")
            return []
