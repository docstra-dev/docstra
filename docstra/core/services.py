"""Core services for Docstra."""

import os
from pathlib import Path
from typing import Optional, Dict, Any, Tuple

from dotenv import load_dotenv

from docstra.core.errors import ConfigError, AuthenticationError


class ConfigurationService:
    """Service for managing Docstra configuration."""

    # Map of providers to their required API keys and environment variables
    PROVIDER_KEYS = {
        "openai": {
            "env_var": "OPENAI_API_KEY",
            "prompt": "Enter your OpenAI API key",
            "required": True,
        },
        "anthropic": {
            "env_var": "ANTHROPIC_API_KEY",
            "prompt": "Enter your Anthropic API key",
            "required": True,
        },
        "huggingface": {
            "env_var": "HUGGINGFACE_API_KEY",
            "prompt": "Enter your Hugging Face API key (optional for some models)",
            "required": False,
        },
        "llama": {
            "env_var": "LLAMA_API_KEY",
            "prompt": "Enter your Llama API key (optional for local models)",
            "required": False,
        },
    }

    @classmethod
    def get_provider_config(cls, provider: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a model provider.

        Args:
            provider: The model provider name

        Returns:
            Provider configuration if available, None otherwise
        """
        return cls.PROVIDER_KEYS.get(provider)

    @classmethod
    def check_api_key(cls, provider: str) -> Tuple[bool, Optional[str]]:
        """Check if an API key is set for a provider.

        Args:
            provider: The model provider name

        Returns:
            Tuple of (is_valid, error_message)
        """
        config = cls.get_provider_config(provider)
        if not config:
            return False, f"Unknown provider: {provider}"

        env_var = config["env_var"]
        api_key = os.getenv(env_var)

        if config["required"] and not api_key:
            return False, f"Missing required API key for {provider}"

        return True, None

    @classmethod
    def validate_api_key(cls, provider: str) -> None:
        """Validate that an API key is set for a provider.

        Args:
            provider: The model provider name

        Raises:
            AuthenticationError: If the API key is missing or invalid
        """
        is_valid, error = cls.check_api_key(provider)
        if not is_valid:
            raise AuthenticationError(error)

    @classmethod
    def setup_environment(cls, working_dir: Path) -> None:
        """Set up the environment for Docstra.

        Args:
            working_dir: The working directory
        """
        # First try loading from .docstra/.env (preferred location)
        docstra_env_path = working_dir / ".docstra" / ".env"
        if docstra_env_path.exists():
            load_dotenv(docstra_env_path)
        
        # Also check for .env file in working directory as fallback
        env_path = working_dir / ".env"
        if env_path.exists():
            load_dotenv(env_path)

    @classmethod
    def save_api_key(cls, working_dir: Path, provider: str, api_key: str) -> None:
        """Save an API key to the environment.

        Args:
            working_dir: The working directory
            provider: The model provider name
            api_key: The API key to save

        Raises:
            ConfigError: If the provider is unknown or the API key is invalid
        """
        config = cls.get_provider_config(provider)
        if not config:
            raise ConfigError(f"Unknown provider: {provider}")

        env_var = config["env_var"]
        env_path = working_dir / ".env"

        # Create or update .env file
        if env_path.exists():
            with open(env_path, "r") as f:
                lines = f.readlines()
        else:
            lines = []

        # Update or add the API key
        key_line = f"{env_var}={api_key}\n"
        key_found = False
        for i, line in enumerate(lines):
            if line.startswith(f"{env_var}="):
                lines[i] = key_line
                key_found = True
                break
        if not key_found:
            lines.append(key_line)

        # Write back to file
        with open(env_path, "w") as f:
            f.writelines(lines)

        # Update environment
        os.environ[env_var] = api_key
