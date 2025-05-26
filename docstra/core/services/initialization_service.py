# File: ./docstra/core/services/initialization_service.py
"""
Service responsible for initializing the Docstra environment in a codebase.
"""

from pathlib import Path
from typing import List, Optional, Dict, Any

from rich.console import Console
from rich.panel import Panel

from docstra.core.config.settings import ConfigManager, UserConfig
from docstra.core.utils.language_detector import LanguageDetector

# It's good practice to alias imports if they might clash or for clarity
from docstra.core.config.wizard import run_init_wizard as run_config_wizard


class InitializationService:
    """
    Handles the setup of the Docstra environment, including configuration
    and necessary directory structures.
    """

    def __init__(self, console: Optional[Console] = None):
        self.console = console if console else Console()

    def initialize_project(
        self,
        codebase_path: str,
        config_file_path: Optional[str] = None,  # Renamed for clarity from config_path
        run_wizard: bool = True,
        initial_include_patterns: Optional[List[str]] = None,
        initial_exclude_patterns: Optional[List[str]] = None,
    ) -> bool:
        """
        Initializes Docstra in the given codebase path.

        Args:
            codebase_path: The root path of the codebase.
            config_file_path: Optional path to a specific config file.
            run_wizard: Whether to run the interactive configuration wizard.
            initial_include_patterns: Initial include patterns for the wizard.
            initial_exclude_patterns: Initial exclude patterns for the wizard.

        Returns:
            True if initialization was successful, False otherwise.
        """
        self.console.print(Panel("Initializing Docstra Environment", expand=False))

        # ConfigManager will use default path if config_file_path is None
        config_manager = ConfigManager(config_file_path)
        abs_codebase_path = Path(codebase_path).resolve()

        if not abs_codebase_path.is_dir():  # Check if it's a directory
            self.console.print(
                f"[bold red]Error:[/] Codebase path {abs_codebase_path} is not a valid directory."
            )
            return False

        if run_wizard:
            try:
                # Updated to match run_config_wizard signature
                run_config_wizard(
                    self.console,
                    str(abs_codebase_path),
                    config_file_path,  # Pass the string path to wizard
                )
                # Wizard saves the config, so we reload it to get the latest
                # No need to call load_config as ConfigManager's constructor handles loading
                self.console.print(
                    f"[green]Configuration processed. Current settings loaded from {config_manager.config_path}[/]"
                )
            except KeyboardInterrupt:
                self.console.print(
                    "\n[yellow]Wizard cancelled. Attempting to use or create default configuration.[/]"
                )
                # ConfigManager already handles loading config
            except Exception as e:
                self.console.print(f"[bold red]Error during wizard: {e}[/]")
                self.console.print(
                    "[yellow]Proceeding with potentially default configuration.[/]"
                )
                # ConfigManager already handles loading config
        else:
            # If not running wizard, ensure config is loaded or default is created and saved
            if not Path(config_manager.config_path).exists():
                config_manager.save()  # Using the renamed method
                self.console.print(
                    f"[green]Default configuration created at {config_manager.config_path}[/]"
                )
            else:
                self.console.print(
                    f"Using existing configuration at {config_manager.config_path}"
                )

        # Determine persist_directory from loaded config
        # ConfigManager.config should now be populated
        persist_directory_name = config_manager.config.storage.persist_directory

        # Resolve persist_directory: if relative, it's relative to codebase_path
        if not Path(persist_directory_name).is_absolute():
            persist_directory = abs_codebase_path / persist_directory_name
        else:
            persist_directory = Path(persist_directory_name)

        persist_directory = persist_directory.resolve()

        try:
            persist_directory.mkdir(parents=True, exist_ok=True)
            self.console.print(
                f"Ensured Docstra storage directory exists: [bold]{persist_directory}[/]"
            )
        except OSError as e:
            self.console.print(
                f"[bold red]Error creating storage directory {persist_directory}: {e}[/]"
            )
            return False

        # Define and write .docstraignore file within the persist_directory
        docstraignore_path = persist_directory / ".docstraignore"
        
        # Use intelligent language detection to generate appropriate ignore patterns
        self.console.print("[cyan]Analyzing codebase structure...[/]")
        detector = LanguageDetector(str(abs_codebase_path))
        detection_summary = detector.get_detection_summary()
        
        # Show detection results to user
        self.console.print(f"[green]Detected primary language:[/] {detection_summary['primary_language']}")
        if detection_summary['languages']:
            languages_str = ", ".join([f"{lang} ({count} files)" for lang, count in detection_summary['languages'].items()])
            self.console.print(f"[green]Languages found:[/] {languages_str}")
        if detection_summary['frameworks']:
            frameworks_str = ", ".join(detection_summary['frameworks'])
            self.console.print(f"[green]Frameworks detected:[/] {frameworks_str}")
        self.console.print(f"[green]Codebase type:[/] {detection_summary['codebase_type']}")
        
        # Get intelligent ignore patterns
        intelligent_patterns = detector.generate_ignore_patterns()
        
        # Merge with user-supplied patterns (if any)
        user_patterns = initial_exclude_patterns if initial_exclude_patterns else []
        # Deduplicate, preserve order: user patterns first, then intelligent patterns not already present
        seen = set()
        merged_patterns = []
        for pat in user_patterns + intelligent_patterns:
            if pat and pat not in seen:
                merged_patterns.append(pat)
                seen.add(pat)
        ignore_content = (
            "# Patterns to exclude from ALL docstra operations\n"
            "# These patterns are applied universally before any command-specific rules.\n"
            "# Use .gitignore syntax.\n"
            "# Add directories or files to ignore, one per line.\n"
            "#\n"
            f"# Auto-generated for {detection_summary['codebase_type']} project\n"
            f"# Primary language: {detection_summary['primary_language']}\n"
            f"# Detected frameworks: {', '.join(detection_summary['frameworks']) if detection_summary['frameworks'] else 'none'}\n"
            f"# Total patterns: {len(merged_patterns)}\n"
            "#\n\n"
            + "\n".join(merged_patterns)
            + "\n"
        )
        try:
            with open(docstraignore_path, "w") as f:
                f.write(ignore_content)
            self.console.print(
                f"Universal exclusion patterns written to: [bold]{docstraignore_path}[/]"
            )
            self.console.print(
                "[yellow]Edit this file to customize universal ignores.[/]"
            )
            self.console.print(
                f"[yellow]Use {Path(config_manager.config_path).name} for command-specific include/exclude rules.[/]"
            )
        except IOError as e:
            self.console.print(f"[bold red]Error writing {docstraignore_path}: {e}[/]")
            self.console.print(
                "[yellow]Warning: Proceeding without .docstraignore file. This is not recommended.[/]"
            )

        self.console.print("\n[bold green]Docstra initialized successfully![/]")
        self.console.print(f"Configuration: [cyan]{config_manager.config_path}[/]")
        self.console.print(f"Storage Directory: [cyan]{persist_directory}[/]")
        self.console.print(
            "Run [bold]'docstra ingest'[/] to process and index your codebase."
        )
        return True

    def ensure_config_exists(
        self,
        config_path: Optional[str] = None,
        project_path: Optional[str] = None,
    ) -> UserConfig:
        """Ensure configuration exists, creating a default one if needed."""
        try:
            # Instantiate ConfigManager - it handles loading or creating defaults
            config_manager = ConfigManager(config_path=config_path)
            return config_manager.config
        except FileNotFoundError:
            # This case should ideally be handled within ConfigManager's init,
            # but we catch it here as a fallback if needed.
            self.console.print(
                "[yellow]Warning:[/] Config file not found at specified path or default locations. Attempting to create default."
            )
            # ConfigManager already tried to create default, re-raising might be better
            # or simply returning the default created by ConfigManager.
            # Assuming ConfigManager handles creation, we just return its result.
            config_manager = ConfigManager(config_path=config_path)
            return config_manager.config  # Return the newly created config
        except Exception as e:
            self.console.print(
                f"[bold red]Error:[/] Failed to load or create configuration: {e}"
            )
            raise

    def update_config(
        self, updates: Dict[str, Any], config_path: Optional[str] = None
    ) -> UserConfig:
        """Update configuration with new values."""
        config_manager = ConfigManager(config_path=config_path)
        config_manager.update(**updates)
        # config_manager.save() # Update already saves
        return config_manager.config

    def reset_config(self, config_path: Optional[str] = None) -> UserConfig:
        """Reset configuration to defaults."""
        config_manager = ConfigManager(config_path=config_path)
        config_manager.reset_to_default()
        # config_manager.save() # reset_to_default already saves
        return config_manager.config

    def get_config(self, config_path: Optional[str] = None) -> UserConfig:
        """Get the current configuration."""
        config_manager = ConfigManager(config_path=config_path)
        return config_manager.config
