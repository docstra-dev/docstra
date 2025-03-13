"""Base command class for Docstra CLI."""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any, List

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from rich import box
from rich.align import Align
from rich.progress import Progress, SpinnerColumn, TextColumn

from docstra.core import IDocstraService, create_service
from docstra.core.config import DocstraConfig
from docstra.cli.ui import (
    display_header,
    display_command_result,
    display_help_message,
    display_session_info,
    display_file_list,
    create_spinner,
)

# Shared console instance
console = Console()


# Click decorator functions for common options
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


class BaseCommand:
    """Base class for Docstra CLI commands."""

    def __init__(self, working_dir: Optional[str] = None, verbose: bool = False, **kwargs):
        """Initialize the command.

        Args:
            working_dir: Working directory path.
            verbose: Whether to enable verbose output.
            **kwargs: Additional keyword arguments.
        """
        self.working_dir = working_dir or os.getcwd()
        self.verbose = verbose
        self.kwargs = kwargs
        self._service: Optional[IDocstraService] = None
        self._config = None
        self.console = console  # Use the shared console instance

    @property
    def service(self) -> IDocstraService:
        """Get the Docstra service instance.

        Returns:
            IDocstraService: The service instance.
        """
        if not self._service:
            self._service = self.initialize_service()
        return self._service

    @property
    def config(self) -> Dict[str, Any]:
        """Get the configuration.

        Returns:
            The configuration dictionary.
        """
        if self._config is None:
            config_path = self.get_config_path()
            if config_path.exists():
                with open(config_path, "r") as f:
                    self._config = json.load(f)
            else:
                self._config = {}
        return self._config

    def save_config(self) -> None:
        """Save the configuration to disk."""
        config_path = self.get_config_path()
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, "w") as f:
            json.dump(self.config, f, indent=2)

    def initialize_service(
        self, log_level: Optional[str] = None, log_file: Optional[str] = None
    ) -> IDocstraService:
        """Initialize the Docstra service.

        Args:
            log_level: The log level to use.
            log_file: The log file to use.

        Returns:
            IDocstraService: The initialized service.
        """
        if self._service is None:
            # Create service with dependency injection
            self._service = create_service(
                working_dir=self.working_dir,
                config=self.config,
                log_level=log_level,
                log_file=log_file,
            )
        return self._service

    def get_config_path(self) -> Path:
        """Get the path to the config file.

        Returns:
            Path: The config file path.
        """
        return Path(self.working_dir) / ".docstra" / "config.json"

    def ensure_initialized(self) -> None:
        """Ensure the workspace is initialized.

        Raises:
            click.ClickException: If the workspace is not initialized.
        """
        config_path = self.get_config_path()
        if not config_path.exists():
            self.display_error("Workspace not initialized. Run 'docstra init' first.")
            raise click.ClickException(
                "Workspace not initialized. Run 'docstra init' first."
            )

    def display_success(self, message: str) -> None:
        """Display a success message.

        Args:
            message: The message to display.
        """
        display_command_result(message, success=True)

    def display_error(self, message: str) -> None:
        """Display an error message.

        Args:
            message: The message to display.
        """
        display_command_result(message, success=False)

    def display_table(self, title: str, data: Dict[str, Any]) -> None:
        """Display data in a table format.

        Args:
            title: The table title.
            data: The data to display.
        """
        table = Table(
            title=title,
            show_header=True,
            header_style="bright_yellow",
            border_style="bright_yellow",
            box=box.ROUNDED,
            title_style="bright_yellow",
            padding=(0, 1),
        )
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")

        for key, value in data.items():
            table.add_row(str(key), str(value))

        console.print()
        console.print(table)
        console.print()

    def display_files(self, files: List[str], title: str = "Files") -> None:
        """Display a list of files.

        Args:
            files: List of file paths
            title: Title for the file list
        """
        display_file_list(files, title)

    def create_progress(self, message: str = "Processing...") -> Progress:
        """Create a progress indicator.

        Args:
            message: Message to display with the progress indicator

        Returns:
            Progress object that can be used in a context manager
        """
        return create_spinner(message)

    def display_session_info(self, session_id: str, session_data: dict) -> None:
        """Display session information.

        Args:
            session_id: ID of the session
            session_data: Dictionary containing session information
        """
        display_session_info(session_id, session_data)

    def show_help(self) -> None:
        """Display help information."""
        display_help_message()
