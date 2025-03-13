"""Base command for CLI commands."""

import os
import click
from pathlib import Path
from typing import Optional, Dict, Any

from rich.console import Console

from docstra.core import IDocstraService, create_service


class BaseCommand:
    """Base command for CLI commands."""

    def __init__(self, working_dir: Optional[str] = None, verbose: bool = False):
        """Initialize the base command.

        Args:
            working_dir: The working directory to use.
            verbose: Whether to enable verbose output.
        """
        self.working_dir = working_dir or os.getcwd()
        self.verbose = verbose
        self.console = Console()
        self._service = None
        self._config = None

    @property
    def config(self) -> Dict[str, Any]:
        """Get the configuration.

        Returns:
            The configuration.
        """
        if self._config is None:
            config_path = Path(self.working_dir) / ".docstra" / "config.json"
            if config_path.exists():
                import json

                with open(config_path, "r") as f:
                    self._config = json.load(f)
            else:
                self._config = {}
        return self._config

    def save_config(self):
        """Save the configuration."""
        config_path = Path(self.working_dir) / ".docstra" / "config.json"
        config_path.parent.mkdir(parents=True, exist_ok=True)
        import json

        with open(config_path, "w") as f:
            json.dump(self.config, f, indent=2)

    def initialize_service(
        self, log_level: Optional[str] = None, log_file: Optional[str] = None
    ) -> IDocstraService:
        """Initialize the service.

        Args:
            log_level: The log level to use.
            log_file: The log file to use.

        Returns:
            The initialized service.
        """
        if self._service is None:
            # Update config with logging settings
            if log_level:
                self.config["log_level"] = log_level
            if log_file:
                self.config["log_file"] = log_file

            # Create service with dependency injection
            self._service = create_service(
                working_dir=self.working_dir,
                config=self.config,
                log_level=log_level,
            )
        return self._service


def working_dir_option(f):
    """Add a working directory option to a command."""
    return click.option(
        "--working-dir",
        "-w",
        help="The working directory to use.",
        type=click.Path(exists=True, file_okay=False, dir_okay=True),
    )(f)


def verbose_option(f):
    """Add a verbose option to a command."""
    return click.option(
        "--verbose", "-v", help="Enable verbose output.", is_flag=True, default=False
    )(f)


def log_level_option(f):
    """Add a log level option to a command."""
    return click.option(
        "--log-level",
        "-l",
        help="The log level to use.",
        type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]),
        default=None,
    )(f)


def log_file_option(f):
    """Add a log file option to a command."""
    return click.option(
        "--log-file",
        "-f",
        help="The log file to use.",
        type=click.Path(file_okay=True, dir_okay=False),
        default=None,
    )(f)
