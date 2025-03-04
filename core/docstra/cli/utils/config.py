"""Configuration utilities for the Docstra CLI."""

import os
import json
from typing import Dict, Any, Optional

from rich.prompt import Prompt, Confirm
from rich.console import Console

from docstra.config import DocstraConfig
from docstra.cli.utils.paths import get_docstra_dir, ensure_docstra_dir

console = Console()


def configure_from_env(config: DocstraConfig) -> DocstraConfig:
    """Update configuration from environment variables.
    
    Args:
        config: Base configuration to update
        
    Returns:
        Updated configuration
    """
    # OpenAI configuration
    if "OPENAI_API_KEY" in os.environ:
        # Only set this as an indicator that we have the API key
        config.model_provider = "openai"
        
    if "OPENAI_MODEL" in os.environ:
        config.model_name = os.environ["OPENAI_MODEL"]
        
    # Advanced configuration
    if "DOCSTRA_CHUNK_SIZE" in os.environ:
        try:
            config.chunk_size = int(os.environ["DOCSTRA_CHUNK_SIZE"])
        except ValueError:
            pass
            
    if "DOCSTRA_CHUNK_OVERLAP" in os.environ:
        try:
            config.chunk_overlap = int(os.environ["DOCSTRA_CHUNK_OVERLAP"])
        except ValueError:
            pass
    
    if "DOCSTRA_TEMPERATURE" in os.environ:
        try:
            config.temperature = float(os.environ["DOCSTRA_TEMPERATURE"])
        except ValueError:
            pass
            
    # Logging configuration        
    if "DOCSTRA_LOG_LEVEL" in os.environ:
        config.log_level = os.environ["DOCSTRA_LOG_LEVEL"]
        
    if "DOCSTRA_LOG_FILE" in os.environ:
        config.log_file = os.environ["DOCSTRA_LOG_FILE"]
        
    return config


def run_configuration_wizard(config: DocstraConfig) -> DocstraConfig:
    """Run an interactive configuration wizard.
    
    Args:
        config: Base configuration to update
        
    Returns:
        Updated configuration
    """
    console.print("[bold]Docstra Configuration Wizard[/bold]")
    console.print("Press Ctrl+C at any time to cancel")
    console.print()
    
    # Model configuration
    console.print("[bold]Model Configuration[/bold]")
    
    # Check if OpenAI API key is set
    if "OPENAI_API_KEY" not in os.environ:
        console.print(
            "[yellow]Warning: OPENAI_API_KEY environment variable is not set.[/yellow]"
        )
        console.print(
            "You'll need to set this before using Docstra."
        )
    
    # Model name
    config.model_name = Prompt.ask(
        "Model name",
        default=config.model_name
    )
    
    # Temperature
    temp_str = Prompt.ask(
        "Temperature (0.0-1.0)",
        default=str(config.temperature)
    )
    try:
        config.temperature = float(temp_str)
    except ValueError:
        console.print("[yellow]Invalid temperature value, using default.[/yellow]")
    
    # Advanced settings
    if Confirm.ask("Configure advanced settings?", default=False):
        # Chunk size
        chunk_size_str = Prompt.ask(
            "Chunk size for indexing",
            default=str(config.chunk_size)
        )
        try:
            config.chunk_size = int(chunk_size_str)
        except ValueError:
            console.print("[yellow]Invalid chunk size, using default.[/yellow]")
        
        # Chunk overlap
        chunk_overlap_str = Prompt.ask(
            "Chunk overlap for indexing",
            default=str(config.chunk_overlap)
        )
        try:
            config.chunk_overlap = int(chunk_overlap_str)
        except ValueError:
            console.print("[yellow]Invalid chunk overlap, using default.[/yellow]")
        
        # System prompt
        if Confirm.ask("Customize system prompt?", default=False):
            config.system_prompt = Prompt.ask(
                "System prompt",
                default=config.system_prompt
            )
        
        # Lazy indexing
        config.lazy_indexing = Confirm.ask(
            "Enable lazy indexing? (index files on-demand)",
            default=getattr(config, "lazy_indexing", False)
        )
        
        # File patterns
        if Confirm.ask("Configure file pattern settings?", default=False):
            # Included extensions
            extensions_str = Prompt.ask(
                "Included file extensions (comma-separated)",
                default=",".join(getattr(config, "included_extensions", 
                                        [".py", ".js", ".ts", ".java", ".cpp", ".c"]))
            )
            config.included_extensions = [ext.strip() for ext in extensions_str.split(",")]
            
            # Excluded patterns
            patterns_str = Prompt.ask(
                "Excluded patterns (comma-separated)",
                default=",".join(getattr(config, "excluded_patterns", 
                                       [".git", "node_modules", "venv", "__pycache__"]))
            )
            config.excluded_patterns = [pat.strip() for pat in patterns_str.split(",")]
    
    # Logging settings
    if Confirm.ask("Configure logging settings?", default=False):
        config.log_level = Prompt.ask(
            "Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
            default=config.log_level
        )
        
        if Confirm.ask("Enable log file?", default=bool(config.log_file)):
            config.log_file = Prompt.ask(
                "Log file path",
                default=config.log_file or "docstra.log"
            )
        else:
            config.log_file = None
            
        config.console_logging = Confirm.ask(
            "Enable console logging?",
            default=config.console_logging
        )
    
    console.print("[green]Configuration complete![/green]")
    return config


def save_session_alias(working_dir: str, session_id: str, alias: str) -> bool:
    """Save a session alias to the aliases file.
    
    Args:
        working_dir: Working directory
        session_id: Session ID to alias
        alias: Alias name
        
    Returns:
        True if successful, False otherwise
    """
    try:
        docstra_dir = ensure_docstra_dir(working_dir)
        aliases_file = docstra_dir / "aliases.json"
        
        # Load existing aliases
        aliases = {}
        if aliases_file.exists():
            with open(aliases_file, "r") as f:
                aliases = json.load(f)
        
        # Update with new alias
        aliases[alias] = session_id
        
        # Save back to file
        with open(aliases_file, "w") as f:
            json.dump(aliases, f, indent=2)
            
        return True
    except Exception as e:
        console.print(f"[red]Error saving alias: {str(e)}[/red]")
        return False


def get_session_aliases(working_dir: str) -> Dict[str, str]:
    """Get all session aliases.
    
    Args:
        working_dir: Working directory
        
    Returns:
        Dictionary of aliases to session IDs
    """
    try:
        docstra_dir = get_docstra_dir(working_dir)
        aliases_file = docstra_dir / "aliases.json"
        
        if not aliases_file.exists():
            return {}
            
        with open(aliases_file, "r") as f:
            return json.load(f)
    except Exception as e:
        console.print(f"[red]Error loading aliases: {str(e)}[/red]")
        return {}


def get_session_by_alias(service, working_dir: str, identifier: str) -> Optional[str]:
    """Get a session ID by its alias or partial ID.
    
    Args:
        service: DocstraService instance
        working_dir: Working directory
        identifier: Alias or partial session ID
        
    Returns:
        Complete session ID or None if not found
    """
    # First check if it's a direct session ID
    session = service.get_session(identifier)
    if session:
        return session.session_id
        
    # Next check aliases
    aliases = get_session_aliases(working_dir)
    if identifier in aliases:
        # Verify the session still exists
        session = service.get_session(aliases[identifier])
        if session:
            return session.session_id
    
    # Finally check for partial ID match in all sessions
    if len(identifier) >= 4:
        all_sessions = service.get_all_session_ids()
        matching_sessions = [sid for sid in all_sessions if sid.startswith(identifier)]
        if len(matching_sessions) == 1:
            return matching_sessions[0]
    
    return None


def setup_history(history_file):
    """Set up input history for the CLI.
    
    Args:
        history_file: Path to history file
    """
    try:
        import readline
        
        # Create history file if it doesn't exist
        if not os.path.exists(history_file):
            with open(history_file, "w") as f:
                pass
                
        readline.read_history_file(history_file)
        
        # Set up history file for writing
        readline.set_history_length(1000)
        import atexit
        atexit.register(readline.write_history_file, history_file)
    except (ImportError, IOError):
        # Readline may not be available on all platforms
        pass