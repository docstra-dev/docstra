import json
import logging
from pathlib import Path
from typing import Optional, Union, Dict, Any, List

from docstra.errors import ConfigError


class DocstraConfig:
    """Configuration for Docstra service."""

    def __init__(
        self,
        model_provider: str = "openai",
        model_name: str = "gpt-4",
        temperature: float = 0.0,
        embedding_provider: str = "openai",
        embedding_model: str = "text-embedding-ada-002",
        chunk_size: int = 1000,
        chunk_overlap: int = 100,
        max_context_chunks: int = 5,
        persist_directory: str = ".docstra",
        system_prompt: str = "You are a helpful code assistant that provides concise and accurate information about code.",
        log_level: str = "INFO",
        log_file: Optional[str] = None,
        console_logging: bool = True,
        lazy_indexing: bool = False,
        excluded_patterns: Optional[List[str]] = None,
        included_extensions: Optional[List[str]] = None,
        name: Optional[str] = None,
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
            lazy_indexing: Whether to use lazy (on-demand) indexing
            excluded_patterns: List of glob patterns to exclude from indexing
            included_extensions: List of file extensions to include in indexing
            name: Optional name for this configuration
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
        self.lazy_indexing = lazy_indexing
        
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
            "**/.DS_Store"
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
            ".php"
        ]
        
        self.name = name

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
            raise ConfigError(f"Invalid JSON in configuration file {config_path}: {str(e)}", cause=e)
        except Exception as e:
            # Fall back to default config if file doesn't exist or has issues
            if isinstance(e, FileNotFoundError):
                return cls()
            raise ConfigError(f"Error loading configuration from {config_path}: {str(e)}", cause=e)

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
            raise ConfigError(f"Failed to save configuration to {config_path}: {str(e)}", cause=e)
