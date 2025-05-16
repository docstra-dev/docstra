# File: ./docstra/core/services/documentation_service.py
"""
Service responsible for generating documentation for the codebase.
"""

import json
import os
from pathlib import Path
from typing import Any, List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
)

from docstra.core.config.settings import DocumentationConfig, ModelProvider, UserConfig
from docstra.core.document_processing.document import Document
from docstra.core.document_processing.extractor import DocumentProcessor
from docstra.core.documentation.generator import DocumentationGenerator
from docstra.core.indexing.code_index import (
    CodebaseIndexer,
)  # For loading index for repo_map
from docstra.core.indexing.repo_map import RepositoryMap
from docstra.core.ingestion.embeddings import EmbeddingFactory
from docstra.core.ingestion.storage import ChromaDBStorage
from docstra.core.llm.base import LLMClient
from docstra.core.retrieval.chroma import ChromaRetriever

# Using the same LLM client factory as ChatService for consistency
# This assumes _get_llm_client_for_chat_service is suitable or will be generalized
from docstra.core.services.chat_service import (
    _get_llm_client_for_chat_service as _get_llm_client_for_doc_service,
)
from docstra.core.utils.file_collector import (
    FileCollector,
    collect_files,
    filter_files_with_patterns,
)


class DocumentationService:
    """
    Handles the generation of codebase documentation.
    """

    def __init__(
        self,
        user_config: UserConfig,
        console: Optional[Console] = None,
        callbacks: Optional[List[Any]] = None,
    ) -> None:
        self.user_config = user_config
        self.doc_config: DocumentationConfig
        # Handle the case where documentation might be None
        if user_config.documentation is None:
            # Create a default documentation config
            self.doc_config = DocumentationConfig()
        else:
            self.doc_config = user_config.documentation
        self.console = console or Console()
        self.callbacks = callbacks

        self.llm_client: LLMClient = _get_llm_client_for_doc_service(
            self.user_config, self.callbacks
        )
        self.document_processor = DocumentProcessor()

    def generate_documentation(
        self,
        input_path_str: str,
        output_dir_str: Optional[str] = None,
        doc_format_str: Optional[str] = None,
        project_name_str: Optional[str] = None,
        project_description_str: Optional[str] = None,
        theme_str: Optional[str] = None,
        structure_str: Optional[str] = None,
        module_depth_str: Optional[str] = None,
        llm_style_prompt_str: Optional[str] = None,
        cli_include_patterns: Optional[List[str]] = None,
        cli_exclude_patterns: Optional[List[str]] = None,
        max_workers_override: Optional[int] = None,
        incremental: bool = False,
    ) -> bool:
        self.console.print(
            Panel("Starting Documentation Generation", style="bold blue")
        )

        effective_output_dir = Path(output_dir_str or self.doc_config.output_dir)
        effective_format = doc_format_str or self.doc_config.format
        input_path_abs = Path(input_path_str).resolve()
        effective_project_name = (
            project_name_str or self.doc_config.project_name or input_path_abs.name
        )
        effective_project_description = (
            project_description_str or self.doc_config.project_description or ""
        )
        effective_theme = theme_str or self.doc_config.theme
        effective_structure = structure_str or self.doc_config.documentation_structure
        effective_module_depth = module_depth_str or self.doc_config.module_doc_depth
        effective_llm_style_prompt = (
            llm_style_prompt_str or self.doc_config.llm_style_prompt
        )

        effective_include_dirs = (
            cli_include_patterns
            if cli_include_patterns is not None
            else (self.doc_config.include_dirs or [])
        )
        effective_exclude_patterns = (
            cli_exclude_patterns
            if cli_exclude_patterns is not None
            else (self.doc_config.exclude_patterns or [])
        )

        if max_workers_override is not None:
            effective_max_workers = max(1, max_workers_override)
        else:
            provider_specific_workers = None
            if (
                self.user_config.model.provider == ModelProvider.OLLAMA
                and self.doc_config.max_workers_ollama is not None
            ):
                provider_specific_workers = self.doc_config.max_workers_ollama
            elif (
                self.user_config.model.provider
                in [ModelProvider.OPENAI, ModelProvider.ANTHROPIC]
                and self.doc_config.max_workers_api is not None
            ):
                provider_specific_workers = self.doc_config.max_workers_api

            if provider_specific_workers is not None:
                effective_max_workers = provider_specific_workers
            elif self.doc_config.max_workers_default is not None:
                effective_max_workers = self.doc_config.max_workers_default
            else:
                effective_max_workers = os.cpu_count() or 2
            effective_max_workers = max(1, effective_max_workers)

        self.console.print(f"  Input path: [cyan]{input_path_abs}[/cyan]")
        self.console.print(f"  Output directory: [cyan]{effective_output_dir}[/cyan]")
        self.console.print(f"  Format: [cyan]{effective_format}[/cyan]")
        self.console.print(f"  Project Name: [cyan]{effective_project_name}[/cyan]")
        self.console.print(f"  Max Workers: [cyan]{effective_max_workers}[/cyan]")
        self.console.print(f"  Incremental: [cyan]{incremental}[/cyan]")

        effective_output_dir.mkdir(parents=True, exist_ok=True)

        persist_dir_name = self.user_config.storage.persist_directory
        base_persist_path = Path(persist_dir_name)
        if not base_persist_path.is_absolute():
            base_persist_path = input_path_abs / persist_dir_name
        abs_persist_directory = base_persist_path.resolve()

        self.console.print(
            f"[dim]Collecting files from {input_path_abs}, persist_dir for ignores: {abs_persist_directory}[/dim]"
        )
        all_files_for_gen = collect_files(
            base_path=str(input_path_abs),
            file_extensions=FileCollector.default_code_file_extensions(),
        )
        self.console.print(
            f"Collected {len(all_files_for_gen)} files (before filtering)."
        )

        docs_target_file_paths = filter_files_with_patterns(
            file_paths=all_files_for_gen,
            base_path=str(input_path_abs),
            include_dirs=effective_include_dirs,
            exclude_patterns=effective_exclude_patterns,
        )
        self.console.print(
            f"Filtered down to {len(docs_target_file_paths)} files for documentation."
        )

        if not docs_target_file_paths:
            self.console.print(
                "[yellow]No files to document after filtering. Exiting.[/yellow]"
            )
            return True

        documents_for_generation: List[Document] = []
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=self.console,
            transient=True,
        ) as progress:
            task_load = progress.add_task(
                "[cyan]Loading files...", total=len(docs_target_file_paths)
            )
            for file_path in docs_target_file_paths:
                try:
                    document = self.document_processor.process(str(file_path))
                    if document:
                        document.metadata.filepath = str(
                            file_path.relative_to(input_path_abs)
                        )
                        documents_for_generation.append(document)
                except Exception as e:
                    self.console.print(
                        f"[yellow]Failed to process {file_path}: {e}[/yellow]"
                    )
                progress.update(task_load, advance=1)

        if not documents_for_generation:
            self.console.print(
                "[bold red]No documents could be successfully loaded for generation. Exiting.[/bold red]"
            )
            return False

        repo_map: Optional[RepositoryMap] = None
        chroma_retriever: Optional[ChromaRetriever] = None
        map_path = abs_persist_directory / "repo_map.json"
        code_indexer_path = abs_persist_directory / "index"
        chroma_storage_path = abs_persist_directory / "chroma"

        if map_path.exists() and code_indexer_path.exists():
            try:
                temp_code_index = CodebaseIndexer(
                    index_directory=str(code_indexer_path)
                ).get_index()
                if temp_code_index:
                    with open(map_path, "r") as f_map:
                        repo_map_data = json.load(f_map)
                    repo_map = RepositoryMap.from_dict(repo_map_data, temp_code_index)
                    self.console.print(
                        f"[dim]Repo map data found at {map_path}. Generator may use it.[/dim]"
                    )
            except Exception as e_map:
                self.console.print(
                    f"[yellow]Warning: Could not load repository map: {e_map}[/yellow]"
                )

        if chroma_storage_path.exists():
            try:
                embedding_gen = EmbeddingFactory.create_embedding_generator(
                    embedding_type=self.user_config.embedding.provider,
                    model_name=self.user_config.embedding.model_name,
                )
                chroma_db = ChromaDBStorage(str(chroma_storage_path))
                chroma_retriever = ChromaRetriever(
                    chroma_db,
                    embedding_gen,
                )
                self.console.print(
                    f"[dim]ChromaRetriever initialized from {chroma_storage_path}.[/dim]"
                )
            except Exception as e_chroma:
                self.console.print(
                    f"[yellow]Warning: Could not initialize ChromaRetriever: {e_chroma}[/yellow]"
                )

        doc_generator = DocumentationGenerator(
            llm_client=self.llm_client,
            output_dir=effective_output_dir,
            format=effective_format,
            repo_map=repo_map,
            chroma_retriever=chroma_retriever,
            documentation_structure=effective_structure,
            module_doc_depth=effective_module_depth,
            llm_style_prompt=effective_llm_style_prompt,
            exclude_patterns=effective_exclude_patterns,
            theme=effective_theme,
            project_name=effective_project_name,
            project_description=effective_project_description,
            incremental=incremental,
            console=self.console,
        )

        self.console.print(
            f"Generating documentation with {effective_max_workers} worker(s)..."
        )
        try:
            doc_generator.generate_for_repository(
                documents=documents_for_generation,
                repo_name=effective_project_name,
                repo_description=effective_project_description,
                max_workers=effective_max_workers,
            )
            self.console.print(
                "[bold green]Documentation generation process finished.[/bold green]"
            )
            self.console.print(
                f"Output at: [link=file://{effective_output_dir.resolve()}]{effective_output_dir.resolve()}[/link]"
            )
            return True
        except Exception as e_gen:
            self.console.print(
                f"[bold red]Error during documentation generation: {e_gen}[/bold red]"
            )
            return False
