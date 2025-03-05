"""Indexer module for handling code file indexing in Docstra."""

import json
import logging
import os
import concurrent.futures
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from langchain_core.documents import Document
import chromadb
from chromadb.config import Settings
from langchain_chroma.vectorstores import Chroma
from langchain_openai.embeddings import OpenAIEmbeddings


class DocstraIndexer:
    """Handles code file indexing and management for Docstra."""

    def __init__(
        self,
        working_dir: Path,
        persist_dir: Path,
        config: "DocstraConfig",
        db: "Database",
        logger: Optional[logging.Logger] = None,
    ):
        """Initialize the indexer.

        Args:
            working_dir: The project working directory
            persist_dir: Directory for persistence
            config: Docstra configuration
            db: Docstra database instance
            logger: Optional logger instance
        """
        self.working_dir = working_dir
        self.persist_dir = persist_dir
        self.config = config
        self.db = db
        self.logger = logger or logging.getLogger("docstra.indexer")

        # Initialize vector store
        self._init_vectorstore()

    def _init_vectorstore(self) -> None:
        """Initialize the vector store for code storage and retrieval."""
        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(model=self.config.embedding_model)

        # Initialize ChromaDB client
        self.chroma_client = chromadb.PersistentClient(
            path=str(self.persist_dir / "chromadb"),
            settings=Settings(anonymized_telemetry=False),
        )

        # Check if collection exists, create if not
        collection_name = "docstra_code"
        collections = self.chroma_client.list_collections()
        collection_exists = any(c.name == collection_name for c in collections)

        if not collection_exists:
            self.chroma_client.create_collection(collection_name)
            # No automatic indexing when creating collection
            self.logger.info(
                "Vector store initialized. Files will be indexed on-demand."
            )

        # Initialize Chroma vector store
        self.vectorstore = Chroma(
            client=self.chroma_client,
            collection_name=collection_name,
            embedding_function=self.embeddings,
        )

    def update_index(self, force: bool = False) -> None:
        """Update the codebase index, only reindexing changed files.

        Args:
            force: If True, force reindexing of all files regardless of modification time
        """
        self.logger.info(f"Checking for code changes in {self.working_dir}...")

        # Get all code files
        code_files = self._collect_code_files()
        if not code_files:
            self.logger.warning("No code files found to index.")
            return

        # Get indexed files metadata from database
        indexed_files = self._get_indexed_files_metadata()

        # Track new, modified, and deleted files
        new_files = []
        modified_files = []
        deleted_file_paths = set(indexed_files.keys())

        # Check each file
        for file_path in code_files:
            relative_path = file_path.relative_to(self.working_dir).as_posix()
            mtime = file_path.stat().st_mtime

            if relative_path in deleted_file_paths:
                # File exists, remove from deleted set
                deleted_file_paths.remove(relative_path)

                # Check if modified or if forced reindex
                if force or str(mtime) != indexed_files[relative_path]["last_modified"]:
                    modified_files.append(file_path)
            else:
                # New file
                new_files.append(file_path)

        # Process new and modified files, prioritizing frequently accessed files
        if new_files or modified_files:
            self.logger.info(
                f"Processing {len(new_files)} new and {len(modified_files)} modified files"
            )

            # Get priority threshold from config
            priority_threshold = getattr(self.config, "index_priority_threshold", None)
            if priority_threshold is None:
                priority_threshold = 5

            # Assign priorities to modified files based on access count
            prioritized_files = []
            normal_files = []

            # New files always get normal priority
            normal_files.extend(new_files)

            # Prioritize modified files based on access count
            for file_path in modified_files:
                rel_path = file_path.relative_to(self.working_dir).as_posix()
                metadata = indexed_files.get(rel_path, {})
                # Ensure access_count is an integer with a default of 0
                access_count = int(metadata.get("access_count", 0) or 0)

                # Assign higher priority to frequently accessed files
                if access_count > priority_threshold:
                    prioritized_files.append(file_path)
                else:
                    normal_files.append(file_path)

            # Process prioritized files first with high priority
            if prioritized_files:
                self.logger.info(
                    f"Processing {len(prioritized_files)} high-priority files first"
                )
                self._process_files_for_indexing(prioritized_files, parallel=True)

            # Then process normal priority files
            if normal_files:
                self._process_files_for_indexing(normal_files, parallel=True)

        # Remove deleted files from index
        if deleted_file_paths:
            self.logger.info(
                f"Removing {len(deleted_file_paths)} deleted files from index"
            )
            self._remove_files_from_index(deleted_file_paths)

        self.logger.info(
            f"Index updated: {len(new_files)} new files, {len(modified_files)} modified files, {len(deleted_file_paths)} deleted files"
        )

    def _get_indexed_files_metadata(self) -> Dict[str, Dict]:
        """Get metadata for all indexed files from the database."""
        # First try to get from database
        indexed_files = self.db.get_file_metadata()

        # If database has no records, try to get from vectorstore
        if not indexed_files:
            self.logger.debug(
                "No file metadata in database, trying to extract from vectorstore"
            )
            try:
                # Query all documents to get metadata
                indexed_docs = self.vectorstore.get()
                for i, metadata in enumerate(indexed_docs["metadatas"]):
                    if "file_path" in metadata and "last_modified" in metadata:
                        file_path = metadata["file_path"]
                        if file_path not in indexed_files:
                            indexed_files[file_path] = {
                                "last_modified": metadata["last_modified"],
                                "last_indexed": metadata.get(
                                    "indexed_at", datetime.now().isoformat()
                                ),
                                "chunk_count": 0,  # We don't know the count yet
                            }

                        # Update count for this file
                        indexed_files[file_path]["chunk_count"] += 1

                # Save to database for future use
                for file_path, metadata in indexed_files.items():
                    self.db.save_file_metadata(
                        file_path,
                        metadata["last_modified"],
                        metadata["last_indexed"],
                        metadata["chunk_count"],
                    )

                self.logger.debug(
                    f"Extracted and saved metadata for {len(indexed_files)} files from vectorstore"
                )
            except Exception as e:
                self.logger.error(
                    f"Error retrieving indexed files from vectorstore: {str(e)}"
                )

        return indexed_files

    def _collect_code_files(self) -> List[Path]:
        """Collect all code files in the working directory based on configuration."""
        from docstra.loader import DocstraLoader

        # Create loader with configuration settings
        loader = DocstraLoader(
            working_dir=self.working_dir,
            included_extensions=self.config.included_extensions,
            excluded_patterns=self.config.excluded_patterns,
            chunk_size=self.config.chunk_size,
            chunk_overlap=self.config.chunk_overlap,
            logger=self.logger,
        )

        # Use the loader to collect files
        return loader.collect_code_files()

    def get_or_index_file(self, file_path: str) -> Union[List[Document], bool]:
        """Get documents for a file from the index.

        Args:
            file_path: Relative path to the file

        Returns:
            A list of document chunks or an empty list if not found
        """
        try:
            # Normalize the path
            rel_path = file_path
            if isinstance(file_path, Path):
                rel_path = file_path.relative_to(self.working_dir).as_posix()
            elif Path(file_path).is_absolute():
                rel_path = Path(file_path).relative_to(self.working_dir).as_posix()

            # Get documents from vectorstore
            docs = self.vectorstore.get(where={"file_path": rel_path})

            # Convert to Document objects
            from langchain_core.documents import Document

            result = []
            for i, doc_text in enumerate(docs["documents"]):
                metadata = docs["metadatas"][i] if i < len(docs["metadatas"]) else {}
                result.append(Document(page_content=doc_text, metadata=metadata))

            # Update access count in database
            try:
                self.db.increment_file_access_count(rel_path)
            except Exception as e:
                self.logger.debug(f"Could not update access count: {str(e)}")

            return result
        except Exception as e:
            self.logger.error(f"Error retrieving file {file_path}: {str(e)}")
            return []

    def _process_files_for_indexing(
        self,
        file_paths: List[Path],
        parallel: bool = True,
        batch_size: int = 20,
        force: bool = False,
    ) -> None:
        """Process a list of files for indexing with support for parallel processing.

        Args:
            file_paths: List of file paths to process
            parallel: Whether to use parallel processing for multiple files
            batch_size: Size of batches for vector storage to improve performance
            force: Force reindexing even if the file is already indexed
        """
        from docstra.loader import DocstraLoader
        import concurrent.futures
        import json

        # Get max workers from config or default to CPU count
        default_workers = min(10, os.cpu_count() or 4)
        max_workers = getattr(self.config, "max_indexing_workers", None)
        if max_workers is None:
            max_workers = default_workers

        # Create loader with specified settings
        loader = DocstraLoader(
            working_dir=self.working_dir,
            included_extensions=self.config.included_extensions,
            excluded_patterns=self.config.excluded_patterns,
            chunk_size=self.config.chunk_size,
            chunk_overlap=self.config.chunk_overlap,
            logger=self.logger,
        )

        # Process files in parallel if enabled and multiple files
        if parallel and len(file_paths) > 1 and max_workers > 1:
            self.logger.info(
                f"Processing {len(file_paths)} files in parallel with {max_workers} workers"
            )

            # Mark files as pending in database
            for file_path in file_paths:
                if file_path.is_file():
                    relative_path = file_path.relative_to(self.working_dir).as_posix()
                    self.db.update_file_status(relative_path, "PENDING")

            # Use a ThreadPoolExecutor for parallel processing
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=max_workers
            ) as executor:
                # Submit all files for processing
                futures = {
                    executor.submit(
                        self._process_single_file_with_loader, file_path, loader
                    ): file_path
                    for file_path in file_paths
                    if file_path.is_file()
                }

                # Collect all documents for batch processing
                all_docs = []
                processed_files = []

                # Process results as they complete
                for future in concurrent.futures.as_completed(futures):
                    file_path = futures[future]
                    try:
                        result = future.result()
                        if result:
                            rel_path, docs, metadata = result
                            processed_files.append((rel_path, metadata))
                            all_docs.extend(docs)

                            # Process in batches to avoid memory issues
                            if len(all_docs) >= batch_size:
                                # Add batch to vectorstore
                                self.vectorstore.add_documents(all_docs)
                                all_docs = []
                    except Exception as e:
                        # Mark file as failed in database
                        relative_path = file_path.relative_to(
                            self.working_dir
                        ).as_posix()
                        self.db.update_file_status(
                            relative_path, "FAILED", error_message=str(e)
                        )
                        self.logger.error(
                            f"Error indexing {file_path}: {str(e)}", exc_info=True
                        )

                # Add any remaining documents
                if all_docs:
                    self.vectorstore.add_documents(all_docs)

                # Update database with all processed files
                for rel_path, metadata in processed_files:
                    self.db.save_file_metadata(**metadata)
                    self.logger.info(
                        f"Indexed: {rel_path} ({metadata['chunk_count']} chunks)"
                    )
        else:
            # Process sequentially for single file or when parallel is disabled
            for file_path in file_paths:
                try:
                    if not file_path.is_file():
                        continue

                    relative_path = file_path.relative_to(self.working_dir).as_posix()
                    self.db.update_file_status(relative_path, "PENDING")

                    result = self._process_single_file_with_loader(file_path, loader)
                    if result:
                        rel_path, docs, metadata = result

                        # Add to vectorstore
                        self.vectorstore.add_documents(docs)

                        # Update database
                        self.db.save_file_metadata(**metadata)
                        self.logger.info(
                            f"Indexed: {rel_path} ({metadata['chunk_count']} chunks)"
                        )
                except Exception as e:
                    relative_path = file_path.relative_to(self.working_dir).as_posix()
                    self.db.update_file_status(
                        relative_path, "FAILED", error_message=str(e)
                    )
                    self.logger.error(
                        f"Error indexing {file_path}: {str(e)}", exc_info=True
                    )

    def _process_single_file_with_loader(
        self, file_path: Path, loader
    ) -> Optional[Tuple[str, List, Dict]]:
        """Process a single file for indexing using the DocstraLoader.

        Args:
            file_path: Path to the file to process
            loader: Initialized DocstraLoader instance to use

        Returns:
            Tuple containing (relative_path, documents, metadata_dict) if successful,
            None if processing should be skipped
        """
        self.logger.debug(f"Processing file: {file_path}")

        # Skip if file doesn't exist or is empty
        if not file_path.exists() or not file_path.is_file():
            self.logger.warning(f"File does not exist or is not a file: {file_path}")
            return None

        # Prepare metadata
        relative_path = file_path.relative_to(self.working_dir).as_posix()
        mtime = file_path.stat().st_mtime
        indexed_at = datetime.now().isoformat()

        # First remove any existing chunks for this file
        self._remove_files_from_index([relative_path])

        # Use the loader to load the file into documents
        docs = loader.load_file(file_path)
        if not docs:
            self.logger.warning(f"No documents generated for file: {file_path}")
            return None

        # Extract and store semantic information
        additional_metadata = {}

        # Store semantic unit info if available in the document metadata
        if any("units" in doc.metadata for doc in docs):
            units = []
            for doc in docs:
                if "units" in doc.metadata:
                    units.extend(doc.metadata["units"])
            additional_metadata["units"] = list(set(units))

        # Store import info and record dependencies if available
        if any("imports" in doc.metadata for doc in docs):
            imports = []
            for doc in docs:
                if "imports" in doc.metadata:
                    imports.extend(doc.metadata["imports"])

            # Store in metadata
            additional_metadata["imports"] = list(set(imports))

            # Record each import as a dependency
            for imported_item in set(imports):
                # Try to find the target file that provides this import
                try:
                    # For demonstration - just using simple matching
                    # In a real system, this would use language-specific import resolution
                    matches = self.db.get_file_metadata(status="INDEXED")
                    for target_path, target_data in matches.items():
                        units = target_data.get("units", [])
                        if any(unit == imported_item for unit in units):
                            # Record the dependency
                            self.db.save_file_dependency(
                                relative_path, target_path, "import"
                            )
                except Exception as e:
                    self.logger.debug(
                        f"Error recording dependency for {imported_item}: {str(e)}"
                    )

        # Prepare metadata for database
        metadata_json = json.dumps(additional_metadata) if additional_metadata else None
        metadata_dict = {
            "file_path": relative_path,
            "last_modified": str(mtime),
            "indexed_at": indexed_at,
            "chunk_count": len(docs),
            "metadata_json": metadata_json,
            "status": "INDEXED",
            "priority": 0,  # Default priority
        }

        return relative_path, docs, metadata_dict

    def _remove_files_from_index(self, file_paths: List[str]) -> None:
        """Remove files from the index."""
        try:
            for path in file_paths:
                # Use the Chroma API to filter and delete by metadata
                self.vectorstore.delete(where={"file_path": path})

                # Remove from database
                self.db.delete_file_metadata(path)

                self.logger.info(f"Removed from index: {path}")
        except Exception as e:
            self.logger.error(f"Error removing files from index: {str(e)}")

    def get_vectorstore(self) -> Chroma:
        """Get the vector store instance.

        Returns:
            The ChromaDB vector store
        """
        return self.vectorstore
