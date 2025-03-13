"""Docstra indexing service for managing code embeddings and vector storage."""

from pathlib import Path
from typing import Dict, List, Optional, Set, Union, Any
import fnmatch

from docstra.core.config import DocstraConfig
from docstra.core.base import BaseService
from docstra.core.interfaces import IIndexer, ILoader, ILogger, IVectorStore
from docstra.core.errors import ConfigError
from docstra.core.loader import DocstraLoader
from docstra.core.vectorstore import create_vectorstore


class DocstraIndexer(BaseService, IIndexer):
    """Service for managing code embeddings and vector storage."""

    def __init__(
        self,
        working_dir: Optional[Union[str, Path]] = None,
        config_path: Optional[Union[str, Path]] = None,
        log_level: Optional[str] = None,
        log_file: Optional[str] = None,
        config: Optional[DocstraConfig] = None,
        logger: Optional[ILogger] = None,
        vectorstore: Optional[IVectorStore] = None,
        loader: Optional[ILoader] = None,
    ):
        """Initialize the indexer service.

        Args:
            working_dir: Working directory containing the codebase
            config_path: Optional path to configuration file
            log_level: Optional logging level override
            log_file: Optional log file path
            config: Optional configuration instance
            logger: Optional logger instance
            vectorstore: Optional vectorstore instance
            loader: Optional loader instance
        """
        # Initialize base service
        super().__init__(
            working_dir=working_dir,
            config_path=config_path,
            log_level=log_level,
            log_file=log_file,
            config=config,
            logger=logger,
        )

        # Create persistence directory
        self.persist_dir = (
            Path(self.working_dir) / self.config.persist_directory / "vectorstore"
        )
        self.persist_dir.mkdir(exist_ok=True, parents=True)

        # Initialize loader
        self.loader = loader or DocstraLoader(
            working_dir=Path(self.working_dir),
            included_extensions=self.config.included_extensions,
            excluded_patterns=self.config.excluded_patterns,
            chunk_size=self.config.chunk_size,
            chunk_overlap=self.config.chunk_overlap,
            logger=self.logger,
        )

        # Initialize vectorstore
        self.vectorstore = vectorstore or create_vectorstore(
            persist_dir=self.persist_dir,
            config=self.config,
            logger=self.logger,
        )

        # Track indexed files
        self._indexed_files: Set[str] = set()
        self._load_indexed_files()

    def _validate_config(self) -> None:
        """Validate indexer configuration.

        Raises:
            ConfigError: If configuration is invalid
        """
        # Call base validation
        super()._validate_config()

        # Validate API key for embeddings
        self.validate_api_key()

        # Add any additional validation here
        if not self.config.model_name:
            raise ConfigError("Model name not configured")

    def _load_indexed_files(self) -> None:
        """Load the set of already indexed files from disk."""
        index_file = self.persist_dir / "indexed_files.txt"
        if index_file.exists():
            with open(index_file, "r") as f:
                self._indexed_files = set(line.strip() for line in f)
            self.logger.debug(f"Loaded {len(self._indexed_files)} indexed files")

    def _save_indexed_files(self) -> None:
        """Save the current set of indexed files to disk."""
        index_file = self.persist_dir / "indexed_files.txt"
        with open(index_file, "w") as f:
            for file in sorted(self._indexed_files):
                f.write(f"{file}\n")
        self.logger.debug(f"Saved {len(self._indexed_files)} indexed files")

    def update_index(self, force: bool = False) -> None:
        """Update the codebase index, only reindexing changed files.

        Args:
            force: If True, force reindexing of all files regardless of modification time
        """
        self.logger.info("Updating codebase index...")

        # Get all files in codebase
        all_files = self.loader.get_all_files()
        self.logger.debug(f"Found {len(all_files)} files in codebase")

        # Track files to index
        files_to_index = []

        # Check which files need indexing
        for file_path in all_files:
            # Convert to Path object if it's a string
            file_path = Path(file_path) if isinstance(file_path, str) else file_path
            try:
                # Get relative path from working directory
                rel_path = str(file_path.relative_to(self.working_dir))
                abs_path = Path(self.working_dir) / rel_path

                # Skip if already indexed and not forced
                if not force and rel_path in self._indexed_files:
                    if not abs_path.exists():
                        # File was deleted
                        self._indexed_files.remove(rel_path)
                        continue

                    # Check if file was modified
                    last_modified = abs_path.stat().st_mtime
                    if last_modified <= self.vectorstore.get_last_modified(rel_path):
                        continue

                files_to_index.append(rel_path)
            except ValueError as e:
                # If the file is outside the working directory, use its absolute path
                if file_path.exists() and file_path.is_file():
                    files_to_index.append(str(file_path))
                else:
                    self.logger.warning(
                        f"File does not exist or is not a file: {file_path}"
                    )
                continue

        if not files_to_index:
            self.logger.info("No files need indexing")
            return

        self.logger.info(f"Indexing {len(files_to_index)} files...")

        # Index files in batches
        batch_size = 10
        for i in range(0, len(files_to_index), batch_size):
            batch = files_to_index[i : i + batch_size]
            self.logger.debug(f"Processing batch of {len(batch)} files")

            # Load and chunk files
            documents = []
            for file_path in batch:
                try:
                    docs = self.loader.load_file(file_path)
                    if docs:
                        documents.extend(docs)
                except Exception as e:
                    self.logger.error(f"Error loading {file_path}: {str(e)}")
                    continue

            if documents:
                # Add to vectorstore
                try:
                    self.vectorstore.add_documents(documents)
                    # Mark as indexed
                    for file_path in batch:
                        self._indexed_files.add(file_path)
                except Exception as e:
                    self.logger.error(f"Error indexing batch: {str(e)}")

        # Save indexed files
        self._save_indexed_files()
        self.logger.info("Index update complete")

    def get_indexed_files(self) -> List[str]:
        """Get list of indexed files.

        Returns:
            List of file paths that have been indexed
        """
        # Get all documents in the vectorstore
        if not self.vectorstore:
            return []

        # Get all documents and extract unique file paths
        try:
            # Get all documents
            docs = self.vectorstore.get()

            # Handle case where docs is a string or not a dict
            if isinstance(docs, str):
                self.logger.warning("Vectorstore returned string instead of documents")
                return []

            if not isinstance(docs, dict):
                self.logger.warning(
                    f"Vectorstore returned unexpected type: {type(docs)}"
                )
                return []

            # Extract unique file paths
            file_paths = set()

            # Handle both ChromaDB response formats
            if "documents" in docs:
                documents = docs["documents"]
            elif "ids" in docs and "metadatas" in docs:
                # ChromaDB sometimes returns a dict with ids and metadatas
                documents = [
                    {"metadata": metadata}
                    for metadata in docs.get("metadatas", [])
                    if isinstance(metadata, dict)
                ]
            else:
                self.logger.warning("Unexpected vectorstore response format")
                return []

            if not isinstance(documents, list):
                self.logger.warning("Documents is not a list")
                return []

            for doc in documents:
                if not isinstance(doc, dict):
                    continue
                metadata = doc.get("metadata", {})
                if isinstance(metadata, dict) and "file_path" in metadata:
                    file_paths.add(metadata["file_path"])

            return list(file_paths)
        except Exception as e:
            self.logger.error(f"Error getting indexed files: {e}")
            return []

    def get_or_index_file(self, file_path: str) -> bool:
        """Get a file from the index or index it if not present.

        This method supports lazy indexing by only indexing files
        when they are requested.

        Args:
            file_path: Path to the file to get or index

        Returns:
            True if file was indexed or already in index, False otherwise
        """
        # Check if file is already indexed
        indexed_files = self.get_indexed_files()
        if file_path in indexed_files:
            self.logger.debug(f"File already indexed: {file_path}")
            return True

        # Check if file exists
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            self.logger.warning(f"File does not exist: {file_path}")
            return False

        # Check if file should be excluded
        try:
            rel_path = file_path_obj.relative_to(self.working_dir)
            rel_str = str(rel_path)
            for pattern in self.config.excluded_patterns:
                if fnmatch.fnmatch(rel_str, pattern):
                    self.logger.debug(f"File excluded by pattern: {file_path}")
                    return False
        except ValueError:
            # If file is outside working directory, use absolute path
            rel_str = str(file_path_obj)
            for pattern in self.config.excluded_patterns:
                if fnmatch.fnmatch(rel_str, pattern):
                    self.logger.debug(f"File excluded by pattern: {file_path}")
                    return False

        try:
            # Load and process the file
            self.logger.info(f"Indexing file: {file_path}")
            docs = self.loader.load_file(file_path)

            if not docs:
                self.logger.warning(f"No documents extracted from file: {file_path}")
                return False

            # Add documents to vectorstore
            self.vectorstore.add_documents(docs)
            self.logger.info(f"Indexed file: {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error indexing file: {file_path} - {e}")
            return False

    def clear_index(self) -> None:
        """Clear the entire index."""
        self.vectorstore.clear()
        self._indexed_files.clear()
        self._save_indexed_files()
        self.logger.info("Index cleared")

    def index_directory(
        self, directory_path: Union[str, Path], force: bool = False
    ) -> None:
        """Index all files in a directory.

        Args:
            directory_path: Path to the directory to index
            force: Whether to force reindexing of all files
        """
        # Convert to Path object if it's a string
        directory_path = (
            Path(directory_path) if isinstance(directory_path, str) else directory_path
        )

        # Ensure directory exists
        if not directory_path.exists() or not directory_path.is_dir():
            raise ValueError(f"Directory does not exist: {directory_path}")

        # Store original working directory
        original_working_dir = self.working_dir

        try:
            # Update the working directory to the target directory
            self.working_dir = directory_path.resolve()

            # Update the loader's working directory
            self.loader.working_dir = self.working_dir

            # Update the index
            self.update_index(force=force)
        finally:
            # Restore the original working directory
            self.working_dir = original_working_dir
            self.loader.working_dir = original_working_dir
