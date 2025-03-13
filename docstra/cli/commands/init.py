"""Initialize a new Docstra workspace."""

import os
from pathlib import Path
from typing import Optional

import click
from rich.prompt import Confirm, Prompt

from docstra.cli.base import BaseCommand
from docstra.core.config import DocstraConfig


class InitCommand(BaseCommand):
    """Initialize a new Docstra workspace."""

    def execute(
        self,
        force: bool = False,
        log_level: Optional[str] = None,
        log_file: Optional[str] = None,
    ) -> None:
        """Execute the init command.

        Args:
            force: Whether to force initialization even if already initialized.
            log_level: Optional log level override.
            log_file: Optional log file path.
        """
        config_path = self.get_config_path()
        if config_path.exists() and not force:
            self.display_error("Workspace already initialized")
            if not Confirm.ask("Do you want to reinitialize?", default=False):
                return

        # Initialize configuration with user input first
        config = self._initialize_config()

        # Then show progress for file operations
        with self.create_progress("Initializing workspace...") as progress:
            task = progress.add_task("Setting up...", total=None)

            # Create .docstra directory if it doesn't exist
            config_dir = Path(self.working_dir) / ".docstra"
            config_dir.mkdir(exist_ok=True)

            # Create .env file if it doesn't exist
            env_path = config_dir / ".env"
            if not env_path.exists():
                env_path.touch()

            # Save API key to .env file if provided
            if hasattr(config, "openai_api_key") and config.openai_api_key:
                with open(env_path, "a") as f:
                    f.write(f"\nOPENAI_API_KEY={config.openai_api_key}")

            # Save configuration
            config.to_file(str(config_path))
            progress.update(task, completed=True)

        self.display_success("Workspace initialized successfully!")
        self.display_table(
            "Configuration",
            {
                "Model": config.model_name,
                "Temperature": config.temperature,
                "Working Directory": self.working_dir,
            },
        )

    def _initialize_config(self) -> DocstraConfig:
        """Initialize configuration with user input.

        Returns:
            DocstraConfig: The initialized configuration
        """
        # Select model provider
        provider = Prompt.ask(
            "Select model provider",
            choices=["openai", "anthropic"],
            default="openai",
        )

        # Define model options based on provider
        model_choices = {
            "openai": [
                "gpt-4o-mini",
                "gpt-4o",
                "gpt-4-turbo",
                "gpt-4",
                "gpt-3.5-turbo",
                "gpt-3.5-turbo-16k",
                "gpt-4.5-preview",
                "o3-mini",
                "o1",
            ],
            "anthropic": [
                "claude-3-7-sonnet-20250219",
                "claude-3-5-haiku-20241022",
                "claude-3-5-sonnet-20241022",
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229",
                "claude-3-haiku-20240307",
            ],
        }

        # Get model configuration
        model_name = Prompt.ask(
            "Select model",
            choices=model_choices[provider],
            default=model_choices[provider][0],
        )

        temperature = float(
            Prompt.ask(
                "Model temperature (0.0-1.0)",
                default="0.0",
            )
        )

        # Get API configuration based on provider
        env_var = "OPENAI_API_KEY" if provider == "openai" else "ANTHROPIC_API_KEY"
        api_key = os.getenv(env_var)
        if not api_key:
            api_key = Prompt.ask(
                f"{provider.capitalize()} API Key",
                password=True,
            )

        # Create and return config with the appropriate provider and key
        config_kwargs = {
            "model_provider": provider,
            "model_name": model_name,
            "temperature": temperature,
        }

        # Add the provider-specific API key
        if provider == "openai":
            config_kwargs["openai_api_key"] = api_key
        else:  # For Anthropic, we'll set it as an environment variable
            os.environ["ANTHROPIC_API_KEY"] = api_key

        return DocstraConfig(**config_kwargs)


@click.command("init")
@click.option("--force", is_flag=True, help="Force reinitialization")
@click.option("--log-level", help="Set log level")
@click.option("--log-file", help="Set log file path")
@click.option(
    "--working-dir", type=click.Path(exists=True), default=".", help="Working directory"
)
def init(
    working_dir: str,
    force: bool = False,
    log_level: Optional[str] = None,
    log_file: Optional[str] = None,
):
    """Initialize a new Docstra workspace."""
    cmd = InitCommand(working_dir=working_dir)
    cmd.execute(force=force, log_level=log_level, log_file=log_file)
