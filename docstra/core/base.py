"""Base service class for Docstra."""

import logging
from pathlib import Path
from typing import Optional, Union

from docstra.core.config import DocstraConfig
from docstra.core.interfaces import ILogger
from docstra.core.services import ConfigurationService
from docstra.core.errors import ConfigError


class BaseService:
    """Base service class with common functionality."""

    def __init__(
        self,
        working_dir: Optional[Union[str, Path]] = None,
        config_path: Optional[Union[str, Path]] = None,
        log_level: Optional[str] = None,
        log_file: Optional[str] = None,
        config: Optional[DocstraConfig] = None,
        logger: Optional[ILogger] = None,
    ):
        """Initialize the base service.

        Args:
            working_dir: Working directory for the service
            config_path: Path to configuration file
            log_level: Logging level to use
            log_file: Path to log file
            config: Optional configuration instance (overrides config_path)
            logger: Optional logger instance
        """
        # Set working directory
        self.working_dir = Path(working_dir) if working_dir else Path.cwd()

        # Set configuration
        if config:
            self.config = config
        elif config_path:
            self.config = DocstraConfig.from_file(config_path)
        else:
            self.config = DocstraConfig.load(self.working_dir)

        # Set up logging
        if logger:
            self.logger = logger
        else:
            # Determine log level - use parameter, then config, then default
            config_log_level = getattr(self.config, 'log_level', 'INFO') if self.config else 'INFO'
            effective_log_level = log_level or config_log_level
            
            # Determine log file - use parameter, then config, then None
            config_log_file = getattr(self.config, 'log_file', None) if self.config else None
            effective_log_file = log_file or config_log_file
            
            self.logger = self._setup_logging(effective_log_level, effective_log_file)

        # Set up environment
        ConfigurationService.setup_environment(self.working_dir)

        # Validate configuration
        self._validate_config()

    def _setup_logging(self, log_level: str, log_file: Optional[str] = None) -> ILogger:
        """Set up logging for the service.

        Args:
            log_level: Logging level to use
            log_file: Optional path to log file

        Returns:
            Configured logger instance
        """
        from docstra.core.logger import DocstraLogger
        return DocstraLogger(log_level=log_level, log_file=log_file)

    def _validate_config(self) -> None:
        """Validate service configuration.

        This method should be overridden by subclasses to add specific validation.

        Raises:
            ConfigError: If configuration is invalid
        """
        # Base validation - ensure working directory exists
        if not self.working_dir.exists():
            raise ConfigError(f"Working directory does not exist: {self.working_dir}")

    def validate_api_key(self) -> None:
        """Validate that required API key is available.

        Raises:
            AuthenticationError: If required API key is missing
        """
        ConfigurationService.validate_api_key(self.config.model_provider)
