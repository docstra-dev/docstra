# File: ./docstra/core/services/ingestion_service.py
"""
Service responsible for ingesting and indexing codebases.
"""

from pathlib import Path
from typing import List, Optional, Any
import shutil

from rich.console import Console
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
)

from docstra.core.config.settings import UserConfig
from docstra.core.document_processing.document import Document
from docstra.core.document_processing.extractor import DocumentProcessor
from docstra.core.document_processing.parser import CodeParser
from docstra.core.document_processing.chunking import (
    ChunkingPipeline,
    SemanticChunking,
    SyntaxAwareChunking,
)
from docstra.core.ingestion.embeddings import EmbeddingFactory
from docstra.core.ingestion.storage import ChromaDBStorage, DocumentIndexer
from docstra.core.indexing.code_index import CodebaseIndexer
from docstra.core.indexing.repo_map import RepositoryMap
from docstra.core.utils.file_collector import collect_files, FileCollector


class IngestionService:
    """
    Service for ingesting and indexing codebases.
    """

    def __init__(
        self,
        console: Optional[Console] = None,
        callbacks: Optional[List[Any]] = None,
    ):
        """Initialize the ingestion service.

        Args:
            console: Optional console for output
            callbacks: Optional callbacks for tracking
        """
        self.console = console or Console()
        self.callbacks = callbacks
        self.document_processor = DocumentProcessor()
        self.code_parser = CodeParser()

    def ingest_codebase(
        self,
        codebase_path: str,
        user_config: UserConfig,
        force: bool = False,
    ) -> bool:
        """Ingest and index a codebase.

        Args:
            codebase_path: Path to the codebase
            user_config: User configuration
            force: Whether to force reindexing

        Returns:
            True if ingestion was successful, False otherwise
        """
        # Get paths
        codebase_path_abs = Path(codebase_path).resolve()
        persist_directory_name = user_config.storage.persist_directory
        persist_directory = self._resolve_persist_directory(
            codebase_path_abs, persist_directory_name
        )

        # If forcing, remove existing ChromaDB and index directories
        if force:
            chroma_dir = persist_directory / "chroma"
            if chroma_dir.exists() and chroma_dir.is_dir():
                shutil.rmtree(chroma_dir)
            index_dir = persist_directory / "index"
            if index_dir.exists() and index_dir.is_dir():
                shutil.rmtree(index_dir)

        # Check if already indexed and not forcing
        index_path = persist_directory / "index"
        if index_path.exists() and not force:
            self.console.print(
                "[yellow]Codebase already indexed. Use --force to reindex.[/]"
            )
            return True

        # Ensure persistence directory exists
        persist_directory.mkdir(parents=True, exist_ok=True)

        # Get ingestion configuration
        include_dirs = None
        exclude_patterns = None
        if user_config.ingestion:
            include_dirs = user_config.ingestion.include_dirs
            exclude_patterns = (
                user_config.ingestion.exclude_patterns
                or user_config.processing.exclude_patterns
            )
        else:
            exclude_patterns = user_config.processing.exclude_patterns

        # Initialize components
        chunking_pipeline = ChunkingPipeline(
            [
                SyntaxAwareChunking(),
                SemanticChunking(max_chunk_size=user_config.processing.chunk_size),
            ]
        )

        embedding_generator = EmbeddingFactory.create_embedding_generator(
            embedding_type=user_config.embedding.provider,
            model_name=user_config.embedding.model_name,
        )

        storage = ChromaDBStorage(persist_directory=str(persist_directory / "chroma"))

        doc_indexer = DocumentIndexer(storage, embedding_generator)

        code_indexer = CodebaseIndexer(
            index_directory=str(persist_directory / "index"),
            exclude_patterns=exclude_patterns or [],
        )

        # Collect files
        self.console.print(f"Collecting files from: [bold]{codebase_path_abs}[/]")
        file_paths = collect_files(
            base_path=str(codebase_path_abs),
            include_dirs=include_dirs,
            exclude_dirs=exclude_patterns,
            file_extensions=FileCollector.default_code_file_extensions(),
        )

        if not file_paths:
            self.console.print("[yellow]No files found to ingest.[/]")
            return False

        self.console.print(f"Found [bold]{len(file_paths)}[/] files to process.")

        # Process, parse, chunk, and index files
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=self.console,
        ) as progress:
            # Process files
            task_process = progress.add_task(
                "[cyan]Processing files...", total=len(file_paths)
            )

            documents: List[Document] = []
            for file_path in file_paths:
                try:
                    document = self.document_processor.process(str(file_path))
                    documents.append(document)
                except Exception as e:
                    self.console.print(
                        f"[yellow]Warning:[/] Failed to process {file_path}: {str(e)}"
                    )
                progress.update(task_process, advance=1)

            # Parse documents
            task_parse = progress.add_task(
                "[cyan]Parsing code structure...", total=len(documents)
            )

            for document in documents:
                try:
                    self.code_parser.parse_document(document)
                except Exception as e:
                    self.console.print(
                        f"[yellow]Warning:[/] Failed to parse {document.metadata.filepath}: {str(e)}"
                    )
                progress.update(task_parse, advance=1)

            # Chunk documents
            task_chunk = progress.add_task(
                "[cyan]Chunking documents...", total=len(documents)
            )

            for document in documents:
                try:
                    chunking_pipeline.process(document)
                except Exception as e:
                    self.console.print(
                        f"[yellow]Warning:[/] Failed to chunk {document.metadata.filepath}: {str(e)}"
                    )
                progress.update(task_chunk, advance=1)

            # Index documents
            task_index = progress.add_task("[cyan]Indexing documents...", total=None)

            doc_indexer.index_documents(documents)
            code_indexer.index_documents(documents)

            progress.update(
                task_index, completed=True, description="[green]Indexed all documents"
            )

            # Create repository map
            task_map = progress.add_task("[cyan]Creating repository map...", total=None)

            repo_map = RepositoryMap.from_documents(
                documents, str(codebase_path_abs), code_indexer.index
            )

            # Save repository map
            map_path = persist_directory / "repo_map.json"
            with open(map_path, "w") as f:
                import json

                json.dump(repo_map.to_dict(), f)

            progress.update(
                task_map, completed=True, description="[green]Created repository map"
            )

        self.console.print("[bold green]Ingestion complete![/]")
        self.console.print(f"Processed and indexed {len(documents)} files")
        return True

    def _resolve_persist_directory(
        self, codebase_path: Path, persist_directory_name: str
    ) -> Path:
        """Resolve the persistence directory path.

        Args:
            codebase_path: Path to the codebase
            persist_directory_name: Name of the persistence directory

        Returns:
            Resolved persistence directory path
        """
        persist_directory = Path(persist_directory_name)

        # If the path is relative, resolve it relative to the codebase path
        if not persist_directory.is_absolute():
            persist_directory = codebase_path / persist_directory

        return persist_directory.resolve()
