import os
from typing import List

from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel

from docstra.core.config.settings import ConfigManager, DocumentationConfig


class DocumentationWizard:
    """Interactive wizard for documentation generation setup."""

    def __init__(self, console: Console, base_path: str, config_manager: ConfigManager):
        """Initialize the documentation wizard.

        Args:
            console: Rich console for UI
            base_path: Base path for the codebase
            config_manager: The configuration manager instance
        """
        self.console = console
        self.base_path = os.path.abspath(base_path)
        self.config_manager = config_manager

        # Load existing config from ConfigManager or use defaults
        existing_doc_config = self.config_manager.config.documentation
        if existing_doc_config:
            # Convert Pydantic model to dict for self.config, ensuring all keys exist
            self.config = existing_doc_config.model_dump()
        else:
            # Use defaults from DocumentationConfig Pydantic model
            default_doc_config = DocumentationConfig()
            self.config = default_doc_config.model_dump()

        # Ensure project name has a fallback if not in config
        if not self.config.get("project_name"):
            self.config["project_name"] = os.path.basename(self.base_path)

    def run(self) -> None:
        """Run the interactive wizard."""
        self.console.print(Panel("Documentation Generation Wizard", expand=False))
        self.console.print("Let's configure your documentation settings.\n")

        # Project information
        self.config["project_name"] = Prompt.ask(
            "Project name", default=self.config.get("project_name")
        )

        self.config["project_description"] = Prompt.ask(
            "Project description", default=self.config.get("project_description", "")
        )

        self.config["project_version"] = Prompt.ask(
            "Project version", default=self.config.get("project_version", "0.1.0")
        )

        # Output configuration
        self.config["output_dir"] = Prompt.ask(
            "Output directory", default=self.config.get("output_dir", "./docs")
        )

        formats = ["html", "markdown", "rst"]
        current_format = self.config.get("format", "markdown")
        format_idx = 0
        for i, fmt in enumerate(formats):
            if fmt == current_format:
                format_idx = i
                break

        format_choice = Prompt.ask(
            "Output format", choices=formats, default=formats[format_idx]
        )
        self.config["format"] = format_choice

        # Directory selection
        self.console.print("\n[bold]Directory Selection[/bold]")
        self._configure_directories()

        # Advanced options
        if Confirm.ask("Configure advanced options?", default=False):
            self._configure_advanced_options()

        # Summary
        self.console.print("\n[bold]Configuration Summary:[/bold]")
        for key, value in self.config.items():
            self.console.print(f"[cyan]{key}:[/cyan] {value}")

        # Save configuration
        if Confirm.ask("Save this configuration?", default=True):
            self._save_config()
        else:
            self.console.print("[yellow]Configuration not saved.[/]")

    def _configure_directories(self) -> None:
        """Configure included and excluded directories/patterns."""
        # First, discover directories
        self._discover_directories()

        # Show available directories
        self.console.print("\nAvailable directories:")
        self.console.print(
            "\nUniversal file/directory exclusion patterns are in .docstra/.docstraignore."
        )
        self.console.print(
            "Enter additional comma-separated gitignore-style patterns to exclude specifically for documentation (e.g., 'tests/*', '*.tmp'):"
        )
        exclude_input = Prompt.ask(
            "Documentation Exclude Patterns",
            default=",".join(self.config.get("exclude_patterns") or []),
        )
        if exclude_input.strip():
            self.config["exclude_patterns"] = [
                p.strip() for p in exclude_input.split(",")
            ]
        else:
            self.config["exclude_patterns"] = []

        # Ask if user wants to specify specific directories to include
        if Confirm.ask(
            "Do you want to specify specific directories to include for documentation?",
            default=False,
        ):
            include_input = Prompt.ask(
                "Include Directories (comma-separated list)",
                default=",".join(self.config.get("include_dirs") or []),
            )
            if include_input.strip():
                self.config["include_dirs"] = [
                    d.strip() for d in include_input.split(",")
                ]
            else:
                self.config["include_dirs"] = []
        else:
            if "include_dirs" not in self.config or self.config["include_dirs"] is None:
                self.config["include_dirs"] = []

    def _discover_directories(self) -> List[str]:
        """Discover directories in the base path.

        Returns:
            List of directory names
        """
        try:
            return [
                d
                for d in os.listdir(self.base_path)
                if os.path.isdir(os.path.join(self.base_path, d))
            ]
        except Exception as e:
            self.console.print(f"[bold red]Error discovering directories:[/] {str(e)}")
            return []

    def _configure_advanced_options(self) -> None:
        """Configure advanced documentation options."""
        # Theme selection
        themes = ["default", "readthedocs", "material", "sphinx_rtd_theme"]
        current_theme = self.config.get("theme", "default")
        theme_idx = 0
        for i, theme in enumerate(themes):
            if theme == current_theme:
                theme_idx = i
                break

        theme_choice = Prompt.ask(
            "Documentation theme", choices=themes, default=themes[theme_idx]
        )
        self.config["theme"] = theme_choice

    def _save_config(self) -> None:
        """Save configuration to the ConfigManager."""
        try:
            # Update the documentation section of the main config
            if self.config_manager.config.documentation is None:
                self.config_manager.config.documentation = DocumentationConfig(
                    include_dirs=self.config.get("include_dirs"),
                    exclude_patterns=self.config.get("exclude_patterns"),
                    output_dir=self.config.get("output_dir", "./docs"),
                    format=self.config.get("format", "markdown"),
                    theme=self.config.get("theme", "default"),
                    project_name=self.config.get("project_name"),
                    project_description=self.config.get("project_description"),
                    project_version=self.config.get("project_version", "0.1.0"),
                    documentation_structure=self.config.get(
                        "documentation_structure", "file_based"
                    ),
                    module_doc_depth=self.config.get("module_doc_depth", "full"),
                    llm_style_prompt=self.config.get("llm_style_prompt"),
                    max_workers_ollama=self.config.get("max_workers_ollama", 1),
                    max_workers_api=self.config.get("max_workers_api", 4),
                    max_workers_default=self.config.get("max_workers_default"),
                )
            else:
                for key, value in self.config.items():
                    if hasattr(self.config_manager.config.documentation, key):
                        setattr(self.config_manager.config.documentation, key, value)
                    else:
                        # This case should ideally not happen if self.config is derived from DocumentationConfig model_dump
                        self.console.print(
                            f"[yellow]Warning: Unknown key '{key}' found in wizard config. Skipping.[/]"
                        )

            self.config_manager.save()
            self.console.print(
                f"[green]Configuration saved to:[/] {self.config_manager.config_path}"
            )
        except Exception as e:
            self.console.print(f"[bold red]Error saving configuration:[/] {str(e)}")
            self.console.print(
                f"Please check your main configuration file: {self.config_manager.config_path}"
            )


def run_documentation_wizard(
    console: Console, path: str, config_manager: ConfigManager
) -> None:
    """Run the documentation wizard."""
    wizard = DocumentationWizard(console, path, config_manager)
    wizard.run()
