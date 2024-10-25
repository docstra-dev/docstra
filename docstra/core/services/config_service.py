# File: ./docstra/core/services/config_service.py
"""
Service responsible for configuration management.
"""

from pathlib import Path
from typing import Dict, Optional, Any

from rich.console import Console

from docstra.core.config.settings import UserConfig, ConfigManager


class ConfigService:
    """
    Service for configuration management.
    """

    def __init__(self, console: Optional[Console] = None):
        """Initialize the config service.

        Args:
            console: Optional console for output
        """
        self.console = console or Console()

    def load_config(self, config_path: Optional[str] = None) -> UserConfig:
        """Load configuration from a file.

        Args:
            config_path: Path to the configuration file

        Returns:
            Loaded configuration
        """
        config_manager = ConfigManager(config_path)
        return config_manager.config

    def save_config(
        self, config: UserConfig, config_path: Optional[str] = None
    ) -> None:
        """Save configuration to a file.

        Args:
            config: Configuration to save
            config_path: Path to save the configuration file
        """
        if config_path:
            config.save_to_file(config_path)
        else:
            # Use ConfigManager to determine the correct path
            config_manager = ConfigManager()
            config_manager.config = config
            config_manager.save()

    def update_config(
        self, updates: Dict[str, Any], config_path: Optional[str] = None
    ) -> UserConfig:
        """Update configuration with new values.

        Args:
            updates: Updates to apply to the configuration
            config_path: Path to the configuration file

        Returns:
            Updated configuration
        """
        config_manager = ConfigManager(config_path)
        config_manager.update(**updates)
        return config_manager.config

    def reset_config(self, config_path: Optional[str] = None) -> UserConfig:
        """Reset configuration to defaults.

        Args:
            config_path: Path to the configuration file

        Returns:
            Default configuration
        """
        config_manager = ConfigManager(config_path)
        config_manager.reset_to_default()
        return config_manager.config

    def get_config_path(self) -> Path:
        """Get the path to the current configuration file.

        Returns:
            Path to the configuration file
        """
        config_manager = ConfigManager()
        return Path(config_manager.config_path)
