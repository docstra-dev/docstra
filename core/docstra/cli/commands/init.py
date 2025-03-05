"""Initialization command for Docstra CLI."""

import os
import click
from pathlib import Path

from rich.prompt import Confirm, Prompt

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
        no_wizard: bool = False,
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

        # Interactive configuration wizard by default, unless skipped
        if not no_wizard:
            try:
                self.console.print("[bold blue]Starting interactive configuration wizard...[/bold blue]")
                self.console.print("(Use Ctrl+C to skip and use defaults)\n")
                config = run_configuration_wizard(config)
                self.console.print()
            except click.Abort:
                self.console.print("[yellow]Configuration wizard skipped, using defaults[/yellow]")

        # Override with any explicit parameters
        for key, value in kwargs.items():
            if value is not None:
                # Handle special cases for negated flags
                if key == "no_lazy_indexing" and value:
                    setattr(config, "lazy_indexing", False)
                elif key == "no_file_watching" and value:
                    setattr(config, "auto_index", False)
                # Skip negated flags when setting attributes
                elif not key.startswith("no_"):
                    setattr(config, key, value)

        # Configure logging options
        if log_level:
            config.log_level = log_level
        if log_file is not None:
            config.log_file = log_file
        if no_console_log:
            config.console_logging = False

        try:
            # Create progress spinner
            with create_spinner("Initializing Docstra...") as progress:
                progress_task = progress.add_task("", total=None)

                # Initialize service
                service = DocstraService(working_dir=str(self.working_dir))

                # Save the config to .docstra/config.json
                docstra_dir = Path(self.working_dir) / ".docstra"
                docstra_dir.mkdir(exist_ok=True, parents=True)
                config_path = docstra_dir / "config.json"
                config.to_file(str(config_path))
                
                # Setup .env file in .docstra directory
                env_file = docstra_dir / ".env"
                
                # Create or update .env file
                if not env_file.exists():
                    self.console.print("\n[bold]Setting up environment variables[/bold]")
                    
                    # Check for API keys and prompt if not set
                    if "OPENAI_API_KEY" not in os.environ and config.model_provider == "openai":
                        openai_key = Prompt.ask(
                            "Enter your OpenAI API key",
                            password=True,
                            default=""
                        )
                        if openai_key:
                            with open(env_file, "a") as f:
                                f.write(f"OPENAI_API_KEY={openai_key}\n")
                    
                    if "ANTHROPIC_API_KEY" not in os.environ and config.model_provider == "anthropic":
                        anthropic_key = Prompt.ask(
                            "Enter your Anthropic API key",
                            password=True,
                            default=""
                        )
                        if anthropic_key:
                            with open(env_file, "a") as f:
                                f.write(f"ANTHROPIC_API_KEY={anthropic_key}\n")
                    
                    self.console.print(f"[green]Environment file created at [bold]{env_file}[/bold][/green]")
                
                # Create a default session
                session_id = service.create_session()

                # Try to rename with a friendly name
                service.rename_session(session_id, "default")

                # No automatic indexing during initialization
                # Files will be indexed when referenced or added explicitly

            env_file = Path(self.working_dir) / ".docstra" / ".env"
            env_file_msg = f"- [bold]{env_file}[/bold] (environment variables)" if env_file.exists() else ""
            
            # Check if legacy config exists
            legacy_config_path = Path(self.working_dir) / "docstra.json"
            legacy_msg = f"- [bold]{legacy_config_path}[/bold] (legacy, will be ignored)" if legacy_config_path.exists() else ""
            
            self.display_success(
                f"✅ Docstra initialized successfully!\n\n"
                f"Configuration saved to:\n"
                f"- [bold]{config_path}[/bold] (primary location)\n"
                f"{legacy_msg}\n"
                f"{env_file_msg}\n\n"
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
                if key.startswith("_") or callable(value):
                    continue

                # Truncate long values like system prompt
                display_value = str(value)
                if len(display_value) > 50 and key == "system_prompt":
                    display_value = display_value[:50] + "..."

                self.console.print(
                    f"  [cyan]{key}[/cyan]: [green]{display_value}[/green]"
                )

        except Exception as e:
            self.console.print(f"[red]Error reading configuration: {str(e)}[/red]")


@click.command("init")
@click.argument("dir_path", default=".", type=click.Path(exists=True))
@click.option("--force", is_flag=True, help="Force reinitialization")
@click.option("--log-level", help="Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)")
@click.option("--log-file", help="Path to log file")
@click.option("--no-console-log", is_flag=True, help="Disable console logging")
@click.option("--no-wizard", is_flag=True, help="Skip interactive configuration wizard (use defaults)")
@click.option("--model-name", help="Model name to use")
@click.option("--temperature", type=float, help="Model temperature (0.0-1.0)")
@click.option("--no-lazy-indexing", is_flag=True, help="Disable lazy indexing mode (indexes all files upfront)")
@click.option("--no-file-watching", is_flag=True, help="Disable automatic file watching")
def init(dir_path, **kwargs):
    """Initialize Docstra in the specified directory."""
    command = InitCommand(working_dir=dir_path)
    command.execute(**kwargs)
