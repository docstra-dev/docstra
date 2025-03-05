"""UI utilities for Docstra CLI."""

import os
from typing import Dict, Optional

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box
from rich.align import Align

# ASCII art header for Docstra
DOCSTRA_HEADER = """
██████╗  ██████╗  ██████╗███████╗████████╗██████╗  █████╗ 
██╔══██╗██╔═══██╗██╔════╝██╔════╝╚══██╔══╝██╔══██╗██╔══██╗
██║  ██║██║   ██║██║     ███████╗   ██║   ██████╔╝███████║
██║  ██║██║   ██║██║     ╚════██║   ██║   ██╔══██╗██╔══██║
██████╔╝╚██████╔╝╚██████╗███████║   ██║   ██║  ██║██║  ██║
╚═════╝  ╚═════╝  ╚═════╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝
"""

console = Console()


def display_header(subtitle: str = None):
    """Display the Docstra ASCII art header.

    Args:
        subtitle: Optional subtitle to display under the header
    """
    header_panel = Panel(
        Align.center(DOCSTRA_HEADER, vertical="middle", style="bright_yellow"),
        border_style="bright_yellow",
        box=box.ROUNDED,
        padding=(0, 2),
        title="LLM-powered code documentation assistant",
        subtitle=subtitle,
    )
    console.print(header_panel)


def display_help_message():
    """Display help message for CLI commands."""
    help_text = """
## Available Commands

### Session Commands
- `sessions` or `session list` - List all available sessions
- `session info <id>` - Show information about a specific session
- `session switch <id>` or `use <id>` - Switch to a different session
- `session rename <id> <name>` - Rename a session
- `session delete <id>` - Delete a session

### File Commands
- `file add <path>` - Add a specific file to the current context
- `file list` - List all files in the current context
- `file remove <path>` - Remove a file from the current context

### Context Behavior
- When you add specific files with `file add`, the assistant will focus on those files for context
- When no files are added, all indexed documents in the vectorstore will be available as context
- Use `file list` to see which files are currently in context

### System Commands
- `clear` - Clear the terminal
- `help` - Show this help message
- `exit`, `quit`, or `bye` - Exit the session

You can ask questions about your code by typing your question directly.
    """

    console.print(Markdown(help_text))


def display_command_result(result: str, success: bool = True):
    """Display the result of a command.

    Args:
        result: Result message to display
        success: Whether the command was successful
    """
    style = "green" if success else "red"
    console.print(f"[{style}]{result}[/{style}]")


def list_sessions(service, aliases: Optional[Dict[str, str]] = None):
    """List all available sessions in a nice table.

    Args:
        service: DocstraService instance
        aliases: Optional dict of session aliases
    """
    session_ids = service.get_all_session_ids()

    if not session_ids:
        console.print("[yellow]No sessions found[/yellow]")
        return

    # Create a table
    table = Table(title="Available Sessions")

    table.add_column("ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Created", style="magenta")
    table.add_column("Messages", style="blue")

    # Get session details and add to table
    for session_id in session_ids:
        session = service.get_session(session_id)
        if session:
            name = session.config.name if hasattr(session.config, "name") else ""

            # Check if there's an alias
            alias = ""
            if aliases:
                for alias_name, aliased_id in aliases.items():
                    if aliased_id == session_id:
                        alias = f"({alias_name})"
                        break

            created = session.created_at.strftime("%Y-%m-%d %H:%M")
            messages = str(len(session.messages))

            table.add_row(session_id[:8] + "...", f"{name} {alias}", created, messages)

    console.print(table)


def show_session_info(service, session_id: str):
    """Show detailed information about a session.

    Args:
        service: DocstraService instance
        session_id: ID of the session to show
    """
    session = service.get_session(session_id)
    if not session:
        console.print(f"[red]Session {session_id} not found[/red]")
        return

    # Create a table for session info
    table = Table(title=f"Session {session_id}")

    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")

    # Basic info
    table.add_row("ID", session_id)
    table.add_row("Created", session.created_at.strftime("%Y-%m-%d %H:%M:%S"))

    # Config info
    if hasattr(session.config, "name") and session.config.name:
        table.add_row("Name", session.config.name)

    table.add_row("Model", session.config.model_name)
    table.add_row("Temperature", str(session.config.temperature))

    # Messages
    table.add_row("Messages", str(len(session.messages)))

    # Context files
    if hasattr(session, "context_files") and session.context_files:
        table.add_row("Context Files", str(len(session.context_files)))

    console.print(table)

    # Show recent messages
    if session.messages:
        console.print("\n[bold]Recent Messages:[/bold]")

        for msg in session.messages[-5:]:  # Last 5 messages
            role_style = "bright_yellow" if msg["role"] == "assistant" else "blue"
            console.print(
                f"[{role_style}]{msg['role']}[/{role_style}]: {msg['content'][:50]}..."
            )


def create_spinner(message: str = "Processing..."):
    """Create a spinner with the given message.

    Args:
        message: Message to display with the spinner

    Returns:
        Progress object that can be used in a context manager
    """
    return Progress(
        SpinnerColumn(),
        TextColumn(f"[bold bright_yellow]{message}[/bold bright_yellow]"),
        console=console,
    )


def clear_screen():
    """Clear the terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")
