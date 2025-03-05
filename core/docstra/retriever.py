from pathlib import Path
from langchain_core.retrievers import BaseRetriever
from langchain.retrievers.contextual_compression import ContextualCompressionRetriever
from langchain.retrievers.document_compressors.chain_extract import LLMChainExtractor
from typing import List
from langchain_core.documents import Document
from langchain_core.callbacks import CallbackManagerForRetrieverRun


# Define a wrapper class that properly extends BaseRetriever
class DocstraRetriever(BaseRetriever):
    """Enhanced retrieval system for code that combines multiple strategies."""

    # Use only the Pydantic v1 style config to avoid conflicts
    class Config:
        arbitrary_types_allowed = True

    def __init__(
        self, vectorstore, llm, config, logger, db=None, service=None, **kwargs
    ):
        """Initialize the enhanced retriever."""
        # Initialize the parent BaseRetriever class first to ensure proper Pydantic setup
        super().__init__(**kwargs)

        # Store all dependencies
        self._vectorstore = vectorstore
        self._llm = llm
        self._config = config
        self._logger = logger
        self._db = db
        self._service = service
        self._working_dir = getattr(service, "working_dir", None)
        self._lazy_indexing = getattr(config, "lazy_indexing", False)

        # Track files specifically added to context
        self._specific_context_files = set()

        # Create base retriever from vectorstore
        self._base_retriever = vectorstore.as_retriever(
            search_kwargs={"k": config.max_context_chunks}
        )

        # Create LLM-based compressor for extracting relevant parts
        self._compressor = LLMChainExtractor.from_llm(llm)

        # Create compression retriever
        self._compression_retriever = ContextualCompressionRetriever(
            base_compressor=self._compressor, base_retriever=self._base_retriever
        )

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        """Get documents relevant to a query."""
        return self.retrieve(query)

    def set_specific_context_files(self, file_paths: List[str]) -> None:
        """Set specific files to use for context retrieval.

        Args:
            file_paths: List of file paths to use for context
        """
        self._specific_context_files = set(file_paths)
        self._logger.debug(
            f"Set specific context files: {self._specific_context_files}"
        )

    def clear_specific_context_files(self) -> None:
        """Clear the list of specific files to use for context."""
        self._specific_context_files.clear()
        self._logger.debug("Cleared specific context files")

    def retrieve(self, query: str) -> List[Document]:
        """Retrieve relevant code documents using a multi-stage approach.

        If specific context files have been set, retrieves only from those files.
        Otherwise, performs a full vectorstore search across all indexed documents.
        """
        # Ensure files mentioned in the query are indexed if lazy_indexing is enabled
        if self._lazy_indexing and self._service:
            self._ensure_query_referenced_files_indexed(query)

        # Check if we should limit to specific files
        docs = []
        if self._specific_context_files:
            self._logger.debug(
                f"Retrieving from specific context files: {self._specific_context_files}"
            )

            # Retrieve documents from each specific file
            for file_path in self._specific_context_files:
                try:
                    # Use on-demand indexing if needed
                    if self._lazy_indexing and self._service:
                        self._service.get_or_index_file(file_path)

                    # Get documents for this file from vectorstore
                    max_k = min(5, self._config.max_context_chunks)
                    file_docs = self._vectorstore.similarity_search(
                        query,
                        filter={"file_path": file_path},
                        k=max_k,
                    )

                    docs.extend(file_docs)
                except Exception as e:
                    self._logger.warning(
                        f"Error retrieving from file {file_path}: {str(e)}"
                    )

            # If we didn't get any documents from specific files, fall back to regular search
            if not docs:
                self._logger.debug(
                    "No documents found in specific files, falling back to vectorstore search"
                )
                docs = self._base_retriever.invoke(query)
        else:
            # Normal case: search across all documents in vectorstore
            self._logger.debug("Retrieving from all indexed documents")
            docs = self._base_retriever.invoke(query)

        # If we have enough docs, we can skip hybrid search
        if len(docs) >= self._config.max_context_chunks:
            return docs

        # If we need more docs and we're not using specific context files,
        # add keyword search results and related files
        if not self._specific_context_files:
            # This simulates hybrid search by combining semantic and keyword search
            keyword_results = self._keyword_search(query)
            combined_results = self._combine_results(docs, keyword_results)

            # Optional: add documents from related files
            related_docs = self._get_related_file_documents(docs)
            combined_results = self._combine_results(combined_results, related_docs)

            # Limit to max chunks
            return combined_results[: self._config.max_context_chunks]

        # For specific context files, just return what we found
        return docs[: self._config.max_context_chunks]

    def retrieve_compressed(self, query: str) -> List[Document]:
        """Retrieve and compress documents to extract most relevant parts."""
        return self._compression_retriever.get_relevant_documents(query)

    def _keyword_search(self, query: str) -> List[Document]:
        """Simple keyword search implementation."""
        results = []

        # Extract keywords (naive approach for simplicity)
        keywords = set(query.lower().split())
        keywords = {k for k in keywords if len(k) > 3}  # Filter short words

        # Get all documents from vectorstore
        all_docs = self._vectorstore.get()

        for i, doc_text in enumerate(all_docs["documents"]):
            # Check if document contains keywords
            if any(keyword in doc_text.lower() for keyword in keywords):
                # Create a Document object
                metadata = (
                    all_docs["metadatas"][i] if i < len(all_docs["metadatas"]) else {}
                )
                results.append(Document(page_content=doc_text, metadata=metadata))

        return results[: self._config.max_context_chunks]

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

    def _ensure_query_referenced_files_indexed(self, query: str) -> None:
        """Index any files that might be referenced in the query.

        This is a heuristic approach to identify possible file references in the query
        and ensure they're indexed before retrieval.

        Args:
            query: The user query which might reference file paths
        """
        if not self._service or not self._working_dir:
            return

        # Use the utility function to extract potential file references
        from docstra.loader import extract_file_references

        potential_references = extract_file_references(query)

        for reference in potential_references:
            try:
                # Try direct indexing first
                self._service.get_or_index_file(reference)
            except Exception:
                # If that fails and this looks like a file name without a path,
                # try to find matching files in the working directory
                if "/" not in reference:
                    try:
                        matching_files = list(
                            Path(self._working_dir).glob(f"**/{reference}")
                        )
                        for file_path in matching_files:
                            rel_path = file_path.relative_to(
                                self._working_dir
                            ).as_posix()
                            try:
                                self._service.get_or_index_file(rel_path)
                            except Exception as e:
                                self._logger.debug(
                                    f"Could not index found file '{rel_path}': {str(e)}"
                                )
                    except Exception as e:
                        self._logger.debug(
                            f"Error searching for file '{reference}': {e}"
                        )
                else:
                    self._logger.debug(f"Could not index referenced file '{reference}'")

    def _get_related_file_documents(self, docs: List[Document]) -> List[Document]:
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
                try:
                    # Index the file on-demand if using lazy indexing
                    if self._lazy_indexing and self._service:
                        self._service.get_or_index_file(file_path)

                    # Get documents from this file
                    file_docs = self._vectorstore.similarity_search(
                        "", filter={"file_path": file_path}, k=2
                    )
                    related_docs.extend(file_docs)
                except Exception as e:
                    self._logger.debug(
                        f"Error retrieving related documents for {file_path}: {str(e)}"
                    )

        return related_docs

    def _find_imported_files(self, file_paths: set) -> set:
        """Find files imported by the given files using dependency tracking."""
        if not self._db:
            self._logger.warning("Database not available for dependency tracking")
            return set()

        imported_files = set()

        # First, ensure all related files are properly indexed if using lazy mode
        if self._lazy_indexing and self._service:
            for file_path in file_paths:
                # Convert to string if needed
                path_str = (
                    str(file_path) if not isinstance(file_path, str) else file_path
                )

                # Index on-demand if needed
                try:
                    self._service.get_or_index_file(path_str)
                    self._logger.debug(f"Ensured file is indexed: {path_str}")
                except Exception as e:
                    self._logger.warning(
                        f"Failed to ensure indexing for {path_str}: {str(e)}"
                    )

        # Process each file path
        for file_path in file_paths:
            # Normalize path
            rel_path = file_path
            if not isinstance(file_path, str):
                if self._working_dir:
                    rel_path = file_path.relative_to(self._working_dir).as_posix()
                else:
                    rel_path = str(file_path)

            # Get direct dependencies (imports)
            try:
                # Query the file_dependencies table for imports
                deps = self._db.get_file_dependencies(
                    rel_path, relationship_type="import", as_source=True
                )

                for dep in deps:
                    target_file = dep["target_file"]
                    if (
                        target_file not in file_paths
                        and target_file not in imported_files
                    ):
                        imported_files.add(target_file)
                        self._logger.debug(
                            f"Found dependency: {rel_path} imports {target_file}"
                        )

                # Also get reverse dependencies (files that import this file)
                reverse_deps = self._db.get_file_dependencies(
                    rel_path, relationship_type="import", as_source=False
                )

                for dep in reverse_deps:
                    source_file = dep["source_file"]
                    if (
                        source_file not in file_paths
                        and source_file not in imported_files
                    ):
                        imported_files.add(source_file)
                        self._logger.debug(
                            f"Found reverse dependency: {source_file} imports {rel_path}"
                        )

            except Exception as e:
                self._logger.error(
                    f"Error getting dependencies for {rel_path}: {str(e)}"
                )

        return imported_files
