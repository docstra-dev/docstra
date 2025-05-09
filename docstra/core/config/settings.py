# File: ./docstra/core/config/settings.py
"""
User configuration settings for the code documentation assistant.
"""

from __future__ import annotations

import os
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml
from pydantic import BaseModel, Field


class ModelProvider(str, Enum):
    """Types of model providers."""

    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    OLLAMA = "ollama"
    LOCAL = "local"


class ModelConfig(BaseModel):
    """Configuration for a specific model."""

    provider: ModelProvider = Field(..., description="Model provider")
    model_name: str = Field(..., description="Name of the model")
    api_key: Optional[str] = Field(None, description="API key (if needed)")
    api_base: Optional[str] = Field(None, description="API base URL (if needed)")
    max_tokens: int = Field(4000, description="Maximum tokens to generate")
    temperature: float = Field(0.0, description="Generation temperature")
    model_path: Optional[str] = Field(
        None, description="Path to local model (if LOCAL provider)"
    )
    device: str = Field("auto", description="Device to run on (for LOCAL provider)")


class EmbeddingConfig(BaseModel):
    """Configuration for embeddings."""

    provider: str = Field("huggingface", description="Embedding provider")
    model_name: str = Field(
        "sentence-transformers/all-mpnet-base-v2",
        description="Embedding model name",
    )
    api_key: Optional[str] = Field(None, description="API key (if needed)")


class ProcessingConfig(BaseModel):
    """Configuration for document processing."""

    chunk_size: int = Field(800, description="Size of chunks in tokens")
    chunk_overlap: int = Field(100, description="Overlap between chunks in tokens")
    exclude_patterns: List[str] = Field(
        default_factory=lambda: [
            # Version control
            ".git",
            ".svn",
            ".hg",
            ".bzr",
            # Python
            "__pycache__",
            "*.pyc",
            "*.pyo",
            "*.pyd",
            ".Python",
            "venv",
            ".venv",
            "env",
            "ENV",
            "virtualenv",
            ".tox",
            ".coverage",
            ".pytest_cache",
            # JavaScript/Node.js
            "node_modules",
            "bower_components",
            "jspm_packages",
            "package-lock.json",
            "yarn.lock",
            # Build outputs and distribution
            "dist",
            "build",
            "*.egg-info",
            "*.egg",
            "*.whl",
            "*.so",
            "*.dylib",
            "*.dll",
            # IDE and editor files
            ".vscode",
            ".idea",
            ".vs",
            "*.swp",
            "*.swo",
            ".DS_Store",
            # Environment and secrets
            ".env",
            ".envrc",
            ".direnv",
            "*.env",
            "secrets.*",
            # Logs and temporary files
            "logs",
            "*.log",
            "tmp",
            "temp",
            # Documentation builds
            "docs/_build",
            "site",
            ".docusaurus",
            # Dependency directories for other languages
            "vendor",  # Go, PHP, Ruby
            "target",  # Java, Rust
            "out",  # Java, Kotlin
            "bin",
            "obj",  # .NET
        ],
        description="Patterns to exclude from processing",
    )


class StorageConfig(BaseModel):
    """Configuration for data storage."""

    persist_directory: str = Field(".docstra", description="Directory to persist data")
    vector_store: str = Field("chroma", description="Vector store type")


class UserConfig(BaseModel):
    """User configuration for the code documentation assistant."""

    model: ModelConfig = Field(..., description="Model configuration")
    embedding: EmbeddingConfig = Field(..., description="Embedding configuration")
    processing: ProcessingConfig = Field(
        default_factory=ProcessingConfig,
        description="Document processing configuration",
    )
    storage: StorageConfig = Field(
        default_factory=StorageConfig, description="Storage configuration"
    )
    custom_templates: Dict[str, str] = Field(
        default_factory=dict, description="Custom prompt templates"
    )

    @classmethod
    def from_file(cls, filepath: Union[str, Path]) -> UserConfig:
        """Load configuration from a file.

        Args:
            filepath: Path to the configuration file

        Returns:
            Loaded configuration

        Raises:
            FileNotFoundError: If the file doesn't exist
        """
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"Configuration file {filepath} not found")

        with open(path, "r") as f:
            config_data = yaml.safe_load(f)

        # Preprocess to convert string provider to enum before parsing
        if (
            isinstance(config_data, dict)
            and "model" in config_data
            and isinstance(config_data["model"], dict)
            and "provider" in config_data["model"]
            and isinstance(config_data["model"]["provider"], str)
        ):
            try:
                # Convert string to enum
                provider_str = config_data["model"]["provider"]
                config_data["model"]["provider"] = ModelProvider(provider_str)
            except ValueError:
                # If invalid provider, use default
                print(
                    f"Warning: Invalid model provider '{provider_str}', defaulting to 'ollama'"
                )
                config_data["model"]["provider"] = ModelProvider.OLLAMA

        # Parse the configuration
        return cls.model_validate(config_data)

    def save_to_file(self, filepath: Union[str, Path]) -> None:
        """Save configuration to a file.

        Args:
            filepath: Path to save the configuration file
        """
        path = Path(filepath)

        # Ensure parent directory exists
        path.parent.mkdir(parents=True, exist_ok=True)

        # Convert to dictionary
        config_dict = self.model_dump()

        # Handle the ModelProvider enum - convert to string for serialization
        if (
            "model" in config_dict
            and isinstance(config_dict["model"], dict)
            and "provider" in config_dict["model"]
            and isinstance(config_dict["model"]["provider"], ModelProvider)
        ):
            config_dict["model"]["provider"] = config_dict["model"]["provider"].value

        # Save to file
        with open(path, "w") as f:
            yaml.safe_dump(config_dict, f, default_flow_style=False)

    @classmethod
    def create_default(cls) -> UserConfig:
        """Create a default configuration.

        Returns:
            Default configuration
        """
        # Default to OpenAI if API key is available, otherwise use Ollama
        openai_api_key = os.environ.get("OPENAI_API_KEY")
        anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")

        if anthropic_api_key:
            model_config = ModelConfig(
                provider=ModelProvider.ANTHROPIC,
                model_name="claude-3-opus-20240229",
                api_key=anthropic_api_key,
            )
        elif openai_api_key:
            model_config = ModelConfig(
                provider=ModelProvider.OPENAI,
                model_name="gpt-4o-mini",
                api_key=openai_api_key,
            )
        else:
            model_config = ModelConfig(
                provider=ModelProvider.OLLAMA,
                model_name="llama3.2",
                api_base="http://localhost:11434",
            )

        # Default embedding configuration
        embedding_config = EmbeddingConfig()

        return cls(model=model_config, embedding=embedding_config)


class ConfigManager:
    """Manager for loading and saving user configuration."""

    DEFAULT_CONFIG_PATH = Path.home() / ".docstra" / "config.yaml"

    def __init__(self, config_path: Optional[Union[str, Path]] = None):
        """Initialize the configuration manager.

        Args:
            config_path: Path to the configuration file
        """
        # Path priority:
        # 1. Explicitly provided config_path
        # 2. Local .docstra/config.yaml in current directory
        # 3. Global ~/.docstra/config.yaml

        if config_path:
            self.config_path = Path(config_path)
        else:
            # Check for local config
            local_config = Path.cwd() / ".docstra" / "config.yaml"
            if local_config.exists():
                self.config_path = local_config
            else:
                self.config_path = self.DEFAULT_CONFIG_PATH

        # Load or create configuration
        try:
            self.config = UserConfig.from_file(self.config_path)

            # If using local config, merge with global defaults for missing values
            if (
                str(self.config_path) != str(self.DEFAULT_CONFIG_PATH)
                and self.DEFAULT_CONFIG_PATH.exists()
            ):
                try:
                    global_config = UserConfig.from_file(self.DEFAULT_CONFIG_PATH)
                    self.config = self._merge_configs(global_config, self.config)
                except Exception:
                    # If global config can't be loaded, just use local config
                    pass

        except FileNotFoundError:
            # Create default configuration
            self.config = UserConfig.create_default()
            # Save default configuration
            self.save()

    def _merge_configs(
        self, base_config: UserConfig, override_config: UserConfig
    ) -> UserConfig:
        """Merge two configurations, with override_config taking precedence.

        Args:
            base_config: The base configuration to start with
            override_config: The configuration with values that should override the base

        Returns:
            A new merged UserConfig instance
        """
        # Convert both configs to dictionaries
        base_dict = base_config.model_dump()
        override_dict = override_config.model_dump()

        # Merge dictionaries recursively
        merged_dict = self._merge_dicts(base_dict, override_dict)

        # Create a new UserConfig from the merged dictionary
        return UserConfig.model_validate(merged_dict)

    def _merge_dicts(self, base: Dict, override: Dict) -> Dict:
        """Recursively merge two dictionaries.

        Args:
            base: Base dictionary
            override: Dictionary with override values

        Returns:
            Merged dictionary
        """
        result = base.copy()

        for key, value in override.items():
            # If the key exists and both values are dicts, merge them recursively
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = self._merge_dicts(result[key], value)
            # If the override value is not None or an empty container, use it
            elif value is not None and (
                not hasattr(value, "__len__")
                or len(value) > 0
                or not isinstance(value, (list, dict, str))
            ):
                result[key] = value
            # Otherwise, keep the base value

        return result

    def save(self) -> None:
        """Save the current configuration."""
        self.config.save_to_file(self.config_path)

    def update(self, **kwargs) -> None:
        """Update configuration parameters.

        Args:
            **kwargs: Parameters to update
        """
        # Update nested parameters
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                if isinstance(value, dict) and isinstance(
                    getattr(self.config, key), BaseModel
                ):
                    # Update nested model
                    current = getattr(self.config, key)
                    for subkey, subvalue in value.items():
                        if hasattr(current, subkey):
                            setattr(current, subkey, subvalue)
                else:
                    # Update regular attribute
                    setattr(self.config, key, value)

        # Save updated configuration
        self.save()

    def reset_to_default(self) -> None:
        """Reset configuration to default."""
        self.config = UserConfig.create_default()
        self.save()

    def get_value(self, key: str, default: Any = None) -> Any:
        """Get a configuration value.

        Args:
            key: Configuration key (dot-separated for nested keys)
            default: Default value if key doesn't exist

        Returns:
            Configuration value
        """
        parts = key.split(".")

        # Navigate to the requested value
        value = self.config
        for part in parts:
            if hasattr(value, part):
                value = getattr(value, part)
            elif isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return default

        return value
