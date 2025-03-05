import json
import logging
import os
from pathlib import Path
from typing import Optional, Union, List

from dotenv import load_dotenv

from docstra.errors import ConfigError


class DocstraConfig:
    """Configuration for Docstra service."""

    def __init__(
        self,
        model_provider: str = "openai",
        model_name: str = "gpt-4o-mini",
        temperature: float = 0.0,
        embedding_provider: str = "openai",
        embedding_model: str = "text-embedding-3-small",
        chunk_size: int = 1000,
        chunk_overlap: int = 100,
        max_context_chunks: int = 5,
        persist_directory: str = ".docstra",
        system_prompt: str = """You are a documentation expert for code. When answering questions:
- Always reference specific files and line numbers in your responses
- Focus on explaining code clearly and concisely
- Provide accurate information with code structure insights
- When explaining code, mention relationships between components
- Keep explanations brief but thorough
- Use markdown formatting for clarity
- Include clickable links to relevant code files
""",
        log_level: str = "WARNING",
        log_file: Optional[str] = None,
        console_logging: bool = True,
        excluded_patterns: Optional[List[str]] = None,
        included_extensions: Optional[List[str]] = None,
        name: Optional[str] = None,
        # Indexing options
        max_indexing_workers: int = None,  # Parallelism for indexing, None = auto
        dependency_tracking: bool = True,  # Track file relationships
        lazy_indexing: bool = False,  # Whether to use lazy (on-demand) indexing
    ):
        """Initialize configuration.

        Args:
            model_provider: LLM provider (openai, anthropic, llama, huggingface)
            model_name: Model name or path
            temperature: Model temperature
            embedding_provider: Embedding provider
            embedding_model: Embedding model
            chunk_size: Size of text chunks for indexing
            chunk_overlap: Overlap between chunks
            max_context_chunks: Maximum number of chunks to include in context
            persist_directory: Directory to persist data
            system_prompt: Custom system prompt
            log_level: Logging level
            log_file: Path to log file
            console_logging: Whether to log to console
            excluded_patterns: List of glob patterns to exclude from indexing
            included_extensions: List of file extensions to include in indexing
            name: Optional name for this configuration
            max_indexing_workers: Number of workers for parallel indexing (None = auto)
            dependency_tracking: Whether to track file relationships
            lazy_indexing: Whether to use lazy (on-demand) indexing
        """
        self.model_provider = model_provider
        self.model_name = model_name
        self.temperature = temperature
        self.embedding_provider = embedding_provider
        self.embedding_model = embedding_model
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.max_context_chunks = max_context_chunks
        self.persist_directory = persist_directory
        self.system_prompt = system_prompt
        self.log_level = log_level
        self.log_file = log_file
        self.console_logging = console_logging

        # Default excluded patterns
        self.excluded_patterns = excluded_patterns or [
            ".git/**",
            "node_modules/**",
            "venv/**",
            ".venv/**",
            "build/**",
            "dist/**",
            "__pycache__/**",
            "**/*.pyc",
            "**/.DS_Store",
        ]

        # Default supported file extensions
        self.included_extensions = included_extensions or [
            ".py",
            ".js",
            ".ts",
            ".java",
            ".kt",
            ".cs",
            ".go",
            ".rs",
            ".cpp",
            ".c",
            ".h",
            ".hpp",
            ".jsx",
            ".tsx",
            ".vue",
            ".rb",
            ".php",
        ]

        self.name = name

        # Indexing properties
        self.max_indexing_workers = max_indexing_workers
        self.dependency_tracking = dependency_tracking
        self.lazy_indexing = lazy_indexing

    @classmethod
    def _load_env_file(cls, working_dir: Union[str, Path]) -> None:
        """Load environment variables from .docstra/.env file.
        
        Args:
            working_dir: Working directory containing the .docstra folder
        """
        working_dir = Path(working_dir) if working_dir else Path.cwd()
        env_file = working_dir / ".docstra" / ".env"
        
        if env_file.exists():
            load_dotenv(env_file)
            logging.debug(f"Loaded environment variables from {env_file}")
        else:
            logging.debug(f"No .env file found at {env_file}")

    @classmethod
    def load(cls, working_dir: Union[str, Path] = None) -> "DocstraConfig":
        """Load configuration from all available sources with proper precedence.

        Configuration is loaded in the following order of precedence (highest to lowest):
        1. Environment variables (from system and .docstra/.env file)
        2. .docstra/config.json in the current working directory
        3. docstra.json in the current working directory (legacy support)
        4. Default values

        Args:
            working_dir: Working directory to load config from (default: current directory)

        Returns:
            A DocstraConfig instance with merged configuration
        """
        working_dir = Path(working_dir) if working_dir else Path.cwd()
        
        # First load environment variables from .env file
        cls._load_env_file(working_dir)

        # Start with default config
        config = cls()

        # Try loading from legacy docstra.json in root (lowest precedence)
        root_config_path = working_dir / "docstra.json"
        if root_config_path.exists():
            try:
                root_config = cls.from_file(root_config_path)
                config = root_config
                logging.warning(
                    "Using legacy docstra.json file. This location is deprecated, "
                    "please use .docstra/config.json instead."
                )
            except ConfigError as e:
                logging.warning(f"Error loading docstra.json: {str(e)}")

        # Try loading from .docstra/config.json (takes precedence over legacy)
        dotconfig_path = working_dir / ".docstra" / "config.json"
        if dotconfig_path.exists():
            try:
                dot_config = cls.from_file(dotconfig_path)
                config = dot_config
            except ConfigError as e:
                logging.warning(f"Error loading .docstra/config.json: {str(e)}")

        # Apply environment variables (highest precedence)
        config = cls._update_from_env(config)

        return config

    @classmethod
    def _update_from_env(cls, config: "DocstraConfig") -> "DocstraConfig":
        """Update configuration from environment variables.

        Args:
            config: Base configuration to update

        Returns:
            Updated configuration
        """
        # OpenAI configuration
        if "OPENAI_API_KEY" in os.environ:
            # Only set this as an indicator that we have the API key
            config.model_provider = "openai"

        if "OPENAI_MODEL" in os.environ:
            config.model_name = os.environ["OPENAI_MODEL"]

        # Anthropic configuration
        if "ANTHROPIC_API_KEY" in os.environ:
            config.model_provider = "anthropic"

        if "ANTHROPIC_MODEL" in os.environ:
            config.model_name = os.environ["ANTHROPIC_MODEL"]

        # Basic Docstra configuration
        if "DOCSTRA_MODEL_PROVIDER" in os.environ:
            config.model_provider = os.environ["DOCSTRA_MODEL_PROVIDER"]

        if "DOCSTRA_MODEL_NAME" in os.environ:
            config.model_name = os.environ["DOCSTRA_MODEL_NAME"]

        # Advanced configuration
        if "DOCSTRA_CHUNK_SIZE" in os.environ:
            try:
                config.chunk_size = int(os.environ["DOCSTRA_CHUNK_SIZE"])
            except ValueError:
                pass

        if "DOCSTRA_CHUNK_OVERLAP" in os.environ:
            try:
                config.chunk_overlap = int(os.environ["DOCSTRA_CHUNK_OVERLAP"])
            except ValueError:
                pass

        if "DOCSTRA_TEMPERATURE" in os.environ:
            try:
                config.temperature = float(os.environ["DOCSTRA_TEMPERATURE"])
            except ValueError:
                pass

        # Embeddings configuration
        if "DOCSTRA_EMBEDDING_PROVIDER" in os.environ:
            config.embedding_provider = os.environ["DOCSTRA_EMBEDDING_PROVIDER"]

        if "DOCSTRA_EMBEDDING_MODEL" in os.environ:
            config.embedding_model = os.environ["DOCSTRA_EMBEDDING_MODEL"]

        # Logging configuration
        if "DOCSTRA_LOG_LEVEL" in os.environ:
            config.log_level = os.environ["DOCSTRA_LOG_LEVEL"]

        if "DOCSTRA_LOG_FILE" in os.environ:
            config.log_file = os.environ["DOCSTRA_LOG_FILE"]

        # Persistence configuration
        if "DOCSTRA_PERSIST_DIR" in os.environ:
            config.persist_directory = os.environ["DOCSTRA_PERSIST_DIR"]

        # No feature flags needed in simplified version

        return config

    @classmethod
    def from_file(cls, config_path: Union[str, Path]) -> "DocstraConfig":
        """Load configuration from a JSON file.

        Args:
            config_path: Path to the configuration file

        Returns:
            A DocstraConfig instance

        Raises:
            ConfigError: If the configuration file cannot be read or parsed correctly
        """
        try:
            config_path = Path(config_path)
            if not config_path.exists():
                return cls()

            config_dict = json.loads(config_path.read_text())
            return cls(**config_dict)

        except json.JSONDecodeError as e:
            raise ConfigError(
                f"Invalid JSON in configuration file {config_path}: {str(e)}", cause=e
            )
        except Exception as e:
            # Fall back to default config if file doesn't exist or has issues
            if isinstance(e, FileNotFoundError):
                return cls()
            raise ConfigError(
                f"Error loading configuration from {config_path}: {str(e)}", cause=e
            )

    def to_file(self, config_path: Union[str, Path]) -> None:
        """Save configuration to a JSON file.

        Args:
            config_path: Path where the configuration should be saved

        Raises:
            ConfigError: If the configuration cannot be saved
        """
        try:
            config_path = Path(config_path)
            config_path.parent.mkdir(exist_ok=True, parents=True)
            config_path.write_text(json.dumps(self.__dict__, indent=2))
        except Exception as e:
            raise ConfigError(
                f"Failed to save configuration to {config_path}: {str(e)}", cause=e
            )
