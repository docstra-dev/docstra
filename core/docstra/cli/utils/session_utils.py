"""Session management utilities for the Docstra CLI."""

import readline
from typing import Optional, List, Dict, Any

from rich.console import Console
from rich.prompt import Prompt

from docstra.service import DocstraService
from docstra.cli.utils.config import get_session_by_alias

console = Console()


def get_user_input(prompt: str = "You > ") -> str:
    """Get user input with tab completion for commands.

    Args:
        prompt: Input prompt to display

    Returns:
        User input
    """
    try:
        # Set up basic tab completion for commands
        def completer(text, state):
            commands = [
                "help",
                "exit",
                "quit",
                "bye",
                "clear",
                "sessions",
                "session list",
                "session info",
                "session switch",
                "session rename",
                "session delete",
                "file add",
                "file list",
                "file remove",
                "use",
            ]

            options = [cmd for cmd in commands if cmd.startswith(text)]
            if state < len(options):
                return options[state]
            else:
                return None

        readline.set_completer(completer)
        readline.parse_and_bind("tab: complete")

        # Print colored prompt using rich
        console.print(f"[bold blue]{prompt}[/bold blue] ", end="")
        return input()
    except (EOFError, KeyboardInterrupt):
        # Handle Ctrl+D and Ctrl+C
        print("\nExiting...")
        return "exit"


def select_session(service: DocstraService, working_dir: str) -> Optional[str]:
    """Select a session interactively.

    Args:
        service: DocstraService instance
        working_dir: Working directory

    Returns:
        Selected session ID or None if cancelled
    """
    session_ids = service.get_all_session_ids()

    if not session_ids:
        console.print("[yellow]No sessions found[/yellow]")
        return None

    # Display available sessions
    console.print("[bold]Available Sessions:[/bold]")

    for i, session_id in enumerate(session_ids):
        session = service.get_session(session_id)
        if session:
            name = session.config.name if hasattr(session.config, "name") else ""
            created = session.created_at.strftime("%Y-%m-%d %H:%M")
            console.print(f"{i+1}. {name or session_id[:8]} - Created: {created}")

    # Get user selection
    try:
        selection = Prompt.ask("Select session number (or enter ID/name)", default="1")

        # Check if it's a number
        try:
            idx = int(selection) - 1
            if 0 <= idx < len(session_ids):
                return session_ids[idx]
        except ValueError:
            # Not a number, try as ID or alias
            resolved_id = get_session_by_alias(service, working_dir, selection)
            if resolved_id:
                return resolved_id

            # Try direct match with session IDs
            for sid in session_ids:
                if sid.startswith(selection):
                    return sid
    except KeyboardInterrupt:
        return None

    console.print("[yellow]Invalid selection[/yellow]")
    return None
