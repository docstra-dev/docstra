import json
import logging
import os
from pathlib import Path
from typing import Optional, Union, List

from dotenv import load_dotenv

from docstra.core.errors import ConfigError


class DocstraConfig:
    """Configuration for Docstra service."""

    def __init__(
        self,
        model_provider: str = "openai",
        model_name: str = "gpt-4o",
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
        openai_api_key: Optional[str] = None,  # OpenAI API key
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
            openai_api_key: OpenAI API key
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
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")

        # Default excluded patterns
        self.excluded_patterns = excluded_patterns or [
            # Version control
            ".git/**",
            # Package managers & dependencies
            "node_modules/**",
            "venv/**",
            ".venv/**",
            "**/env/**",
            "**/virtualenv/**",
            "yarn.lock",
            "package-lock.json",
            "poetry.lock",
            "Pipfile.lock",
            # Build and distribution
            "build/**",
            "dist/**",
            "**/bin/**",
            "**/out/**",
            "**/target/**",
            # Cache files
            "__pycache__/**",
            "**/*.pyc",
            ".cache/**",
            ".pytest_cache/**",
            ".ruff_cache/**",
            ".mypy_cache/**",
            "**/.ipynb_checkpoints/**",
            "coverage/**",
            ".coverage",
            # System files
            "**/.DS_Store",
            "**/Thumbs.db",
            # IDE and editor files
            "**/.idea/**",
            "**/.vscode/**",
            "**/.vs/**",
            # Testing
            "**/test/**",
            "**/tests/**",
            "**/*.test.*",
            "**/*.spec.*",
            # Environment and config files
            ".env*",
            "**/*.config.*",
            "**/*.min.*",  # Minified files
            # R-specific
            ".Rproj.user/**",
            ".Rhistory",
            ".RData",
            "**/*.Rproj",
            # Logs
            "**/logs/**",
            "**/*.log",
            # Documentation is now included
            # No longer excluding documentation files
            # Temp files
            "**/tmp/**",
            "**/temp/**",
            # Special directories
            "**/fixtures/**",
            "**/vendor/**",
            "**/third_party/**",
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
            ".md",  # Include Markdown files for documentation
            ".txt", # Include text files
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
    def load(cls, working_dir: Union[str, Path] = None, **kwargs) -> "DocstraConfig":
        """Load configuration from all available sources with proper precedence.

        Configuration is loaded in the following order of precedence (highest to lowest):
        1. Direct kwargs/arguments passed to this method
        2. Environment variables (from system and .docstra/.env file)
        3. .docstra/config.json in the current working directory
        4. Default values

        Args:
            working_dir: Working directory to load config from (default: current directory)
            **kwargs: Direct configuration overrides (highest precedence)

        Returns:
            A DocstraConfig instance with merged configuration
        """
        working_dir = Path(working_dir) if working_dir else Path.cwd()

        # Start with default config
        config = cls()

        # Load from .docstra/config.json (if exists)
        dotconfig_path = working_dir / ".docstra" / "config.json"
        if dotconfig_path.exists():
            try:
                dot_config = cls.from_file(dotconfig_path)
                # Update only non-None values from file config
                for key, value in vars(dot_config).items():
                    if value is not None:
                        setattr(config, key, value)
            except ConfigError as e:
                logging.warning(f"Error loading .docstra/config.json: {str(e)}")

        # Load environment variables from .env file
        cls._load_env_file(working_dir)

        # Apply environment variables
        config = cls._update_from_env(config)

        # Apply direct kwargs (highest precedence)
        for key, value in kwargs.items():
            if hasattr(config, key) and value is not None:
                setattr(config, key, value)
            elif value is not None:
                logging.warning(f"Unknown configuration parameter: {key}")

        return config

    @classmethod
    def _update_from_env(cls, config: "DocstraConfig") -> "DocstraConfig":
        """Update configuration from environment variables.

        Environment variables should be prefixed with DOCSTRA_ and use uppercase.
        For example: DOCSTRA_MODEL_PROVIDER, DOCSTRA_MODEL_NAME, etc.

        Args:
            config: Base configuration to update

        Returns:
            Updated configuration instance
        """
        # Map of environment variable names to config attributes
        env_mapping = {
            "DOCSTRA_MODEL_PROVIDER": "model_provider",
            "DOCSTRA_MODEL_NAME": "model_name",
            "DOCSTRA_TEMPERATURE": ("temperature", float),
            "DOCSTRA_EMBEDDING_PROVIDER": "embedding_provider",
            "DOCSTRA_EMBEDDING_MODEL": "embedding_model",
            "DOCSTRA_CHUNK_SIZE": ("chunk_size", int),
            "DOCSTRA_CHUNK_OVERLAP": ("chunk_overlap", int),
            "DOCSTRA_MAX_CONTEXT_CHUNKS": ("max_context_chunks", int),
            "DOCSTRA_PERSIST_DIRECTORY": "persist_directory",
            "DOCSTRA_SYSTEM_PROMPT": "system_prompt",
            "DOCSTRA_LOG_LEVEL": "log_level",
            "DOCSTRA_LOG_FILE": "log_file",
            "DOCSTRA_CONSOLE_LOGGING": (
                "console_logging",
                lambda x: x.lower() == "true",
            ),
            "DOCSTRA_MAX_INDEXING_WORKERS": ("max_indexing_workers", int),
            "DOCSTRA_DEPENDENCY_TRACKING": (
                "dependency_tracking",
                lambda x: x.lower() == "true",
            ),
            "DOCSTRA_LAZY_INDEXING": ("lazy_indexing", lambda x: x.lower() == "true"),
            "DOCSTRA_OPENAI_API_KEY": (
                "openai_api_key",
                lambda x: x or os.getenv("OPENAI_API_KEY"),
            ),
        }

        for env_var, config_attr in env_mapping.items():
            value = os.getenv(env_var)
            if value is not None:
                if isinstance(config_attr, tuple):
                    attr_name, converter = config_attr
                    try:
                        value = converter(value)
                    except (ValueError, TypeError) as e:
                        logging.warning(f"Error converting {env_var} value: {str(e)}")
                        continue
                else:
                    attr_name = config_attr
                setattr(config, attr_name, value)

        # Handle list-type environment variables
        if excluded_patterns := os.getenv("DOCSTRA_EXCLUDED_PATTERNS"):
            try:
                config.excluded_patterns = json.loads(excluded_patterns)
            except json.JSONDecodeError:
                config.excluded_patterns = [
                    p.strip() for p in excluded_patterns.split(",")
                ]

        if included_extensions := os.getenv("DOCSTRA_INCLUDED_EXTENSIONS"):
            try:
                config.included_extensions = json.loads(included_extensions)
            except json.JSONDecodeError:
                config.included_extensions = [
                    e.strip() for e in included_extensions.split(",")
                ]

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
