# File: ./docstra/core/services/query_service.py
"""
Service responsible for handling user queries against the indexed codebase.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

from rich.console import Console

# Assuming UserConfig and ModelProvider will be accessible
from docstra.core.config.settings import UserConfig, ModelProvider
from docstra.core.llm.anthropic import AnthropicClient
from docstra.core.llm.local import LocalModelClient
from docstra.core.llm.ollama import OllamaClient
from docstra.core.llm.openai import OpenAIClient
from docstra.core.ingestion.embeddings import EmbeddingFactory
from docstra.core.ingestion.storage import ChromaDBStorage
from docstra.core.retrieval.chroma import ChromaRetriever
from docstra.core.indexing.code_index import CodebaseIndexer
from docstra.core.retrieval.hybrid import HybridRetriever


def _get_llm_client_for_service(
    config: UserConfig, callbacks: Optional[List[Any]] = None
):
    """
    Helper to get LLM client based on config.
    """
    provider = config.model.provider

    # Currently only AnthropicClient and OpenAIClient support callbacks
    # So we need to handle each case separately
    if provider == ModelProvider.ANTHROPIC:
        return AnthropicClient(
            model_name=config.model.model_name,
            api_key=config.model.api_key,
            max_tokens=config.model.max_tokens,
            temperature=config.model.temperature,
        )
    elif provider == ModelProvider.OPENAI:
        return OpenAIClient(
            model_name=config.model.model_name,
            api_key=config.model.api_key,
            max_tokens=config.model.max_tokens,
            temperature=config.model.temperature,
        )
    elif provider == ModelProvider.OLLAMA:
        # Ollama client doesn't support callbacks, so we just create without them
        return OllamaClient(
            model_name=config.model.model_name,
            api_base=config.model.api_base or "http://localhost:11434",
            max_tokens=config.model.max_tokens,
            temperature=config.model.temperature,
            validate_connection=False,  # Don't validate during service creation
        )
    elif provider == ModelProvider.LOCAL:
        # Local client may not support callbacks either
        return LocalModelClient(
            model_name=config.model.model_name,
            model_path=config.model.model_path,
            max_tokens=config.model.max_tokens,
            temperature=config.model.temperature,
            device=config.model.device,
            # callbacks parameter removed
        )
    else:
        raise ValueError(f"Unsupported model provider: {provider}")


class QueryService:
    """
    Handles querying the codebase and generating answers.
    """

    def __init__(
        self,
        user_config: UserConfig,
        console: Optional[Console] = None,
        callbacks: Optional[List[Any]] = None,
    ):
        self.user_config = user_config
        self.console = console if console else Console()
        self.callbacks = callbacks  # Callbacks list, potentially including DocstraStatsCallbackHandler

        self.llm_client = _get_llm_client_for_service(self.user_config, self.callbacks)
        self.embedding_generator = EmbeddingFactory.create_embedding_generator(
            embedding_type=self.user_config.embedding.provider,
            model_name=self.user_config.embedding.model_name,
        )

        self.storage: Optional[ChromaDBStorage] = None
        self.retriever: Optional[ChromaRetriever] = None
        self.code_indexer: Optional[CodebaseIndexer] = None
        self.hybrid_retriever: Optional[HybridRetriever] = None
        self._retrieval_initialized_for_path: Optional[Path] = None

    def _ensure_retrieval_components_initialized(self, abs_codebase_path: Path):
        """Initializes or re-initializes retrieval components if the codebase path has changed."""
        if (
            self._retrieval_initialized_for_path == abs_codebase_path
            and self.hybrid_retriever
        ):
            self.console.print(
                f"[debug]QueryService: Retrieval components already initialized for {abs_codebase_path}[/debug]",
                style="dim",
            )
            return

        self.console.print(
            f"[debug]QueryService: Initializing retrieval components for {abs_codebase_path}[/debug]",
            style="dim",
        )

        persist_directory_name = self.user_config.storage.persist_directory
        if not Path(persist_directory_name).is_absolute():
            effective_persist_dir = abs_codebase_path / persist_directory_name
        else:
            effective_persist_dir = Path(persist_directory_name)
        effective_persist_dir = effective_persist_dir.resolve()

        chroma_path = effective_persist_dir / "chroma"
        index_path = effective_persist_dir / "index"
        chroma_check_file = chroma_path / "chroma.sqlite3"

        if not index_path.exists() or not chroma_check_file.exists():
            error_msg = (
                f"Codebase at {abs_codebase_path} not fully initialized for querying. "
                f"ChromaDB path: {chroma_path} (check file: {chroma_check_file}, exists: {chroma_check_file.exists()}), "
                f"Index path: {index_path} (exists: {index_path.exists()}). "
                "Run 'docstra init' and 'docstra ingest' first."
            )
            self.console.print(f"[bold red]Error:[/] {error_msg}")
            raise FileNotFoundError(error_msg)

        try:
            self.storage = ChromaDBStorage(persist_directory=str(chroma_path))
            self.retriever = ChromaRetriever(
                self.storage, self.embedding_generator
            )
            self.code_indexer = CodebaseIndexer(
                index_directory=str(index_path)
            )  # Callbacks not typically passed here
            code_index_instance = self.code_indexer.get_index()
            if code_index_instance is None:
                raise ValueError(f"Failed to load code index from {index_path}")
            self.hybrid_retriever = HybridRetriever(
                self.retriever, code_index_instance
            )
            self._retrieval_initialized_for_path = abs_codebase_path
            self.console.print(
                f"[debug]QueryService: Retrieval components initialized successfully for {abs_codebase_path}[/debug]",
                style="dim",
            )
        except Exception as e:
            self.console.print(
                f"[bold red]Error initializing retrieval components: {e}[/]"
            )
            # import traceback; traceback.print_exc() # For more detailed debugging
            raise

    def answer_question(
        self, question: str, codebase_path_str: str, n_results: int = 5
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Answers a question about the codebase using retrieval and LLM.
        """
        abs_codebase_path = Path(codebase_path_str).resolve()

        try:
            self._ensure_retrieval_components_initialized(abs_codebase_path)
        except (FileNotFoundError, ValueError) as e:
            return f"Error: Could not initialize components for querying. {e}", []

        if not self.hybrid_retriever:
            return "Error: Hybrid retriever not initialized.", []

        self.console.print(f"Querying codebase at: [cyan]{abs_codebase_path}[/cyan]")
        self.console.print(f"Question: [bold yellow]{question}[/bold yellow]")

        retrieved_chunks: List[Dict[str, Any]] = []
        with self.console.status("[cyan]Searching codebase context...", spinner="dots"):
            try:
                retrieved_chunks = self.hybrid_retriever.retrieve(
                    query=question, n_results=n_results, use_code_context=True
                )
                self.console.print(
                    f"[debug]Retrieved {len(retrieved_chunks)} chunks.[/debug]",
                    style="dim",
                )
            except Exception as e:
                self.console.print(f"[bold red]Error during retrieval: {e}[/]")
                return f"Error during retrieval: {e}", []

        answer_text = "Could not generate an answer."
        if not retrieved_chunks:
            self.console.print(
                "[yellow]No relevant context found in the codebase for your query. Attempting to answer without specific context...[/yellow]"
            )
            # Fallback: try to answer with the LLM without specific context from retrieval
            # The llm_client.answer_question might need to handle context=None or context=[]
            # For now, we'll pass an empty list for context.
            pass  # Continue to LLM call with empty context

        with self.console.status("[cyan]Generating answer with LLM...", spinner="dots"):
            try:
                # The llm_client.answer_question method is expected to handle the list of dicts (chunks)
                # or an empty list if no context was found.
                answer_text = self.llm_client.answer_question(
                    question=question, context=retrieved_chunks
                )
            except Exception as e:
                self.console.print(
                    f"[bold red]Error during LLM answer generation: {e}[/]"
                )
                return f"Error during LLM answer generation: {e}", retrieved_chunks

        return answer_text, retrieved_chunks
