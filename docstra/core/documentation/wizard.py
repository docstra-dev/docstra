import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

import typer
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich import print as rprint
from rich.panel import Panel
from rich.markdown import Markdown


class DocumentationWizard:
    """Interactive wizard for documentation generation setup."""

    def __init__(self, console: Console, base_path: str):
        """Initialize the documentation wizard.

        Args:
            console: Rich console for UI
            base_path: Base path for the codebase
        """
        self.console = console
        self.base_path = os.path.abspath(base_path)
        self.config: Dict[str, Any] = {
            "name": os.path.basename(self.base_path),
            "description": "",
            "version": "0.1.0",
            "include_dirs": [],
            "exclude_dirs": [".git", "__pycache__", "node_modules", "venv", ".env"],
            "exclude_files": [],
            "theme": "default",
            "output_dir": "./docs",
            "format": "html",
        }

    def run(self) -> Dict[str, Any]:
        """Run the interactive wizard.

        Returns:
            Configuration dictionary
        """
        self.console.print(Panel("Documentation Generation Wizard", expand=False))
        self.console.print("Let's configure your documentation settings.\n")

        # Project information
        self.config["name"] = Prompt.ask("Project name", default=self.config["name"])

        self.config["description"] = Prompt.ask(
            "Project description", default=self.config["description"]
        )

        self.config["version"] = Prompt.ask(
            "Project version", default=self.config["version"]
        )

        # Output configuration
        self.config["output_dir"] = Prompt.ask(
            "Output directory", default=self.config["output_dir"]
        )

        formats = ["html", "markdown", "rst"]
        format_idx = 0
        for i, fmt in enumerate(formats):
            if fmt == self.config["format"]:
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
        if Confirm.ask("Save this configuration for future use?", default=True):
            self._save_config()

        return self.config

    def _configure_directories(self) -> None:
        """Configure included and excluded directories."""
        # First, discover directories
        dirs = self._discover_directories()

        # Show available directories
        self.console.print("\nAvailable directories:")
        for i, directory in enumerate(dirs):
            is_excluded = directory in self.config["exclude_dirs"]
            color = "red" if is_excluded else "green"
            marker = "✗" if is_excluded else "✓"
            self.console.print(f"  [{color}]{marker}[/{color}] {directory}")

        # Select directories to exclude
        self.console.print(
            "\nSelect directories to exclude (comma-separated list, empty to keep current):"
        )
        exclude_input = Prompt.ask(
            "Exclude", default=",".join(self.config["exclude_dirs"])
        )

        if exclude_input.strip():
            self.config["exclude_dirs"] = [d.strip() for d in exclude_input.split(",")]

        # Ask if user wants to specify specific directories to include
        if Confirm.ask(
            "Do you want to specify specific directories to include?", default=False
        ):
            include_input = Prompt.ask("Include (comma-separated list)")
            if include_input.strip():
                self.config["include_dirs"] = [
                    d.strip() for d in include_input.split(",")
                ]

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
        theme_idx = 0
        for i, theme in enumerate(themes):
            if theme == self.config["theme"]:
                theme_idx = i
                break

        theme_choice = Prompt.ask(
            "Documentation theme", choices=themes, default=themes[theme_idx]
        )
        self.config["theme"] = theme_choice

        # File exclusion patterns
        exclude_files = Prompt.ask(
            "Exclude file patterns (comma-separated, e.g. *.test.py,*.spec.js)",
            default=(
                ",".join(self.config["exclude_files"])
                if self.config["exclude_files"]
                else ""
            ),
        )

        if exclude_files.strip():
            self.config["exclude_files"] = [f.strip() for f in exclude_files.split(",")]

    def _save_config(self) -> None:
        """Save configuration to a file."""
        config_dir = os.path.join(self.base_path, ".docstra")
        os.makedirs(config_dir, exist_ok=True)

        config_path = os.path.join(config_dir, "docs_config.json")
        with open(config_path, "w") as f:
            json.dump(self.config, f, indent=2)

        self.console.print(f"[green]Configuration saved to:[/] {config_path}")


def load_wizard_config(path: str) -> Optional[Dict[str, Any]]:
    """Load wizard configuration from a file.

    Args:
        path: Path to the codebase

    Returns:
        Configuration dictionary if found, None otherwise
    """
    config_path = os.path.join(path, ".docstra", "docs_config.json")
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except Exception:
            return None
    return None


def run_documentation_wizard(console: Console, path: str) -> Dict[str, Any]:
    """Run the documentation wizard.

    Args:
        console: Rich console
        path: Path to the codebase

    Returns:
        Documentation configuration
    """
    wizard = DocumentationWizard(console, path)
    return wizard.run()
