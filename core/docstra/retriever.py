from langchain.retrievers.contextual_compression import ContextualCompressionRetriever
from langchain.retrievers.document_compressors.chain_extract import LLMChainExtractor
from typing import List, Dict, Any


class EnhancedCodeRetriever:
    """Enhanced retrieval system for code that combines multiple strategies."""

    def __init__(self, vectorstore, llm, config):
        """Initialize the enhanced retriever.

        Args:
            vectorstore: The vector database for retrieving documents
            llm: LLM instance for re-ranking and extraction
            config: Docstra configuration
        """
        self.vectorstore = vectorstore
        self.llm = llm
        self.config = config

        # Create base retriever from vectorstore
        self.base_retriever = vectorstore.as_retriever(
            search_kwargs={"k": config.max_context_chunks}
        )

        # Create LLM-based compressor for extracting relevant parts
        self.compressor = LLMChainExtractor.from_llm(llm)

        # Create compression retriever that extracts relevant parts
        self.compression_retriever = ContextualCompressionRetriever(
            base_compressor=self.compressor, base_retriever=self.base_retriever
        )

    def retrieve(self, query: str) -> List[Dict[str, Any]]:
        """Retrieve relevant code documents using a multi-stage approach.

        Args:
            query: User's query or question

        Returns:
            List of relevant document dictionaries with content and metadata
        """
        # Semantic search with vectorstore
        docs = self.base_retriever.get_relevant_documents(query)

        # If we have enough docs, we can skip hybrid search
        if len(docs) >= self.config.max_context_chunks:
            return docs

        # If we need more docs, add keyword search results
        # This simulates hybrid search by combining semantic and keyword search
        keyword_results = self._keyword_search(query)
        combined_results = self._combine_results(docs, keyword_results)

        # Optional: add documents from related files
        related_docs = self._get_related_file_documents(docs)
        combined_results = self._combine_results(combined_results, related_docs)

        # Limit to max chunks
        return combined_results[: self.config.max_context_chunks]

    def retrieve_compressed(self, query: str) -> List[Dict[str, Any]]:
        """Retrieve and compress documents to extract most relevant parts.

        This is useful for fitting more context in the LLM context window.
        """
        return self.compression_retriever.get_relevant_documents(query)

    def _keyword_search(self, query: str) -> List[Dict[str, Any]]:
        """Simple keyword search implementation."""
        # Simplified keyword search logic - in production you'd use a proper text search
        results = []

        # Extract keywords (naive approach for simplicity)
        keywords = set(query.lower().split())
        keywords = {k for k in keywords if len(k) > 3}  # Filter short words

        # Get all documents from vectorstore
        all_docs = self.vectorstore.get()

        for doc in all_docs["documents"]:
            # Check if document contains keywords
            if any(keyword in doc.lower() for keyword in keywords):
                results.append(doc)

        return results[: self.config.max_context_chunks]

    def _combine_results(self, list1, list2):
        """Combine results while removing duplicates."""
        seen = set()
        combined = []

        for doc in list1 + list2:
            # Use document content as uniqueness key
            key = doc.page_content if hasattr(doc, "page_content") else doc
            if key not in seen:
                seen.add(key)
                combined.append(doc)

        return combined

    def _get_related_file_documents(self, docs):
        """Find documents from files that are related to the retrieved docs."""
        related_docs = []

        # Get unique file paths from retrieved docs
        retrieved_file_paths = set()
        for doc in docs:
            if hasattr(doc, "metadata") and "file_path" in doc.metadata:
                retrieved_file_paths.add(doc.metadata["file_path"])

        # If we have file paths, find import relationships
        if retrieved_file_paths:
            # Get imports from retrieved files
            imported_files = self._find_imported_files(retrieved_file_paths)

            # Get documents from imported files
            for file_path in imported_files:
                file_docs = self.vectorstore.similarity_search(
                    "", filter={"file_path": file_path}, k=2
                )
                related_docs.extend(file_docs)

        return related_docs

    def _find_imported_files(self, file_paths):
        """Find files imported by the given files."""
        # This would require code analysis to find imports
        # Simplified version just returns empty set
        return set()
