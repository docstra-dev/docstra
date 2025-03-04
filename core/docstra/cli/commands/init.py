"""Initialization command for Docstra CLI."""

import os
import click
from pathlib import Path

from rich.prompt import Confirm

from docstra.config import DocstraConfig
from docstra.service import DocstraService
from docstra.cli.base import DocstraCommand
from docstra.cli.utils import (
    configure_from_env,
    run_configuration_wizard,
    create_spinner,
    get_config_path,
)


class InitCommand(DocstraCommand):
    """Command to initialize Docstra in a directory."""
    
    def execute(
        self,
        force: bool = False,
        log_level: str = None,
        log_file: str = None,
        no_console_log: bool = False,
        wizard: bool = False,
        **kwargs,
    ):
        """Execute the init command.
        
        Args:
            force: Force reinitialization even if already initialized
            log_level: Log level to use
            log_file: Log file path
            no_console_log: Disable console logging
            wizard: Run configuration wizard
            **kwargs: Additional configuration options
        """
        from docstra.cli.utils import display_header
        
        # Display the header
        display_header("Initialization")

        # Check if already initialized
        config_path = get_config_path(str(self.working_dir))
        if config_path.exists() and not force:
            if not Confirm.ask("Docstra is already initialized. Reinitialize?"):
                return

        # Start with base config
        config = DocstraConfig()

        # Update from environment variables
        config = configure_from_env(config)

        # Interactive configuration wizard if requested
        if wizard:
            try:
                config = run_configuration_wizard(config)
            except click.Abort:
                self.console.print("[yellow]Configuration cancelled[/yellow]")
                return

        # Override with any explicit parameters
        for key, value in kwargs.items():
            if value is not None:
                setattr(config, key, value)

        # Configure logging options
        if log_level:
            config.log_level = log_level
        config.log_file = log_file
        config.console_logging = not no_console_log

        try:
            # Create progress spinner
            with create_spinner("Initializing Docstra...") as progress:
                progress_task = progress.add_task("", total=None)

                # Initialize service
                service = DocstraService(working_dir=str(self.working_dir))

                # Save the config
                config_dir = Path(self.working_dir) / ".docstra"
                config_dir.mkdir(exist_ok=True, parents=True)
                config_path = config_dir / "config.json"
                config.to_file(str(config_path))

                # Create a default session
                session_id = service.create_session()

                # Try to rename with a friendly name
                service.rename_session(session_id, "default")

                # Force index update
                service.update_index()

            self.display_success(
                f"✅ Docstra initialized successfully!\n\n"
                f"Configuration saved to [bold]{config_path}[/bold]\n"
                f"Created default session: [bold]{session_id}[/bold]",
                title="Success",
            )

            # Show current configuration
            self.show_config()

        except Exception as e:
            self.display_error(
                f"Error initializing Docstra: {str(e)}",
                title="Error",
            )
            raise

    def show_config(self):
        """Show the current configuration."""
        config_path = get_config_path(str(self.working_dir))
        if not config_path.exists():
            return

        try:
            config = DocstraConfig.from_file(str(config_path))
            
            # Display config in a nice format
            self.console.print("\n[bold]Current Configuration:[/bold]")
            
            for key, value in vars(config).items():
                if key.startswith('_') or callable(value):
                    continue
                    
                # Truncate long values like system prompt
                display_value = str(value)
                if len(display_value) > 50 and key == "system_prompt":
                    display_value = display_value[:50] + "..."
                    
                self.console.print(f"  [cyan]{key}[/cyan]: [green]{display_value}[/green]")
                
        except Exception as e:
            self.console.print(f"[red]Error reading configuration: {str(e)}[/red]")


@click.command("init")
@click.argument("dir_path", default=".", type=click.Path(exists=True))
@click.option("--force", is_flag=True, help="Force reinitialization")
@click.option("--log-level", help="Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)")
@click.option("--log-file", help="Path to log file")
@click.option("--no-console-log", is_flag=True, help="Disable console logging")
@click.option("--wizard", is_flag=True, help="Run interactive configuration wizard")
@click.option("--model-name", help="Model name to use")
@click.option("--temperature", type=float, help="Model temperature (0.0-1.0)")
@click.option("--lazy-indexing", is_flag=True, help="Enable lazy indexing mode")
def init(dir_path, **kwargs):
    """Initialize Docstra in the specified directory."""
    command = InitCommand(working_dir=dir_path)
    command.execute(**kwargs)