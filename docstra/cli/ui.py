"""UI utilities for Docstra CLI."""

import os
from typing import Dict, Optional
from pathlib import Path

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
        Align.center(
            f"[bright_yellow]{DOCSTRA_HEADER}[/bright_yellow]\n"
            + (f"[dim]{subtitle}[/dim]" if subtitle else ""),
            vertical="middle",
        ),
        border_style="bright_yellow",
        box=box.HEAVY,
        padding=(1, 2),
        title="[bright_yellow]✨ LLM-powered code documentation assistant[/bright_yellow]",
        subtitle=f"[bright_yellow]{subtitle}[/bright_yellow]" if subtitle else None,
    )
    console.print()
    console.print(header_panel)
    console.print()


def display_help_message():
    """Display help message for CLI commands."""
    help_sections = [
        (
            "Session Commands",
            [
                ("sessions", "List all available sessions"),
                ("session info <id>", "Show information about a specific session"),
                ("session switch <id>", "Switch to a different session"),
                ("session rename <id> <name>", "Rename a session"),
                ("session delete <id>", "Delete a session"),
            ],
        ),
        (
            "File Commands",
            [
                ("file add <path>", "Add a specific file to the current context"),
                ("file list", "List all files in the current context"),
                ("file remove <path>", "Remove a file from the current context"),
            ],
        ),
        (
            "System Commands",
            [
                ("clear", "Clear the terminal"),
                ("help", "Show this help message"),
                ("exit/quit/bye", "Exit the session"),
            ],
        ),
    ]

    console.print()
    console.print("[bright_yellow]Docstra CLI Help[/bright_yellow]", justify="center")
    console.print()

    for section_title, commands in help_sections:
        table = Table(
            show_header=True,
            header_style="bright_yellow",
            border_style="bright_yellow",
            box=box.ROUNDED,
            title=section_title,
            title_style="bright_yellow",
            padding=(0, 1),
        )
        table.add_column("Command", style="cyan")
        table.add_column("Description", style="green")

        for cmd, desc in commands:
            table.add_row(f"`{cmd}`", desc)

        console.print(table)
        console.print()

    # Add context behavior section
    context_panel = Panel(
        "[cyan]When you add specific files with [bright_yellow]`file add`[/bright_yellow], "
        "the assistant will focus on those files for context.\n"
        "When no files are added, all indexed documents in the vectorstore will be available.\n"
        "Use [bright_yellow]`file list`[/bright_yellow] to see which files are currently in context.[/cyan]",
        title="[bright_yellow]Context Behavior[/bright_yellow]",
        border_style="bright_yellow",
        box=box.ROUNDED,
        padding=(1, 2),
    )
    console.print(context_panel)
    console.print()


def display_command_result(result: str, success: bool = True):
    """Display the result of a command.

    Args:
        result: Result message to display
        success: Whether the command was successful
    """
    icon = "✓" if success else "✗"
    style = "bright_green" if success else "bright_red"
    panel = Panel(
        f"[{style}]{result}[/{style}]",
        border_style=style,
        box=box.ROUNDED,
        padding=(0, 1),
        title=f"[{style}]{icon} Result[/{style}]",
    )
    console.print(panel)


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


def display_session_info(session_id: str, session_data: dict):
    """Display detailed information about a session.

    Args:
        session_id: ID of the session
        session_data: Dictionary containing session information
    """
    console.print()

    # Create main info panel
    info_table = Table(show_header=False, box=box.ROUNDED, border_style="bright_yellow")
    info_table.add_column("Property", style="cyan")
    info_table.add_column("Value", style="green")

    # Add basic info
    info_table.add_row("ID", session_id)
    info_table.add_row("Created", session_data.get("created_at", "N/A"))
    info_table.add_row("Name", session_data.get("name", "N/A"))
    info_table.add_row("Model", session_data.get("model", "N/A"))
    info_table.add_row("Temperature", str(session_data.get("temperature", "N/A")))
    info_table.add_row("Messages", str(session_data.get("message_count", 0)))

    main_panel = Panel(
        info_table,
        title=f"[bright_yellow]Session Information - {session_id[:8]}...[/bright_yellow]",
        border_style="bright_yellow",
        box=box.HEAVY,
    )
    console.print(main_panel)

    # Display recent messages if available
    if messages := session_data.get("recent_messages", []):
        console.print()
        console.print("[bright_yellow]Recent Messages:[/bright_yellow]")
        for msg in messages[-5:]:  # Last 5 messages
            role_style = "bright_yellow" if msg["role"] == "assistant" else "cyan"
            msg_panel = Panel(
                (
                    f"{msg['content'][:100]}..."
                    if len(msg["content"]) > 100
                    else msg["content"]
                ),
                border_style=role_style,
                box=box.ROUNDED,
                padding=(0, 1),
                title=f"[{role_style}]{msg['role']}[/{role_style}]",
            )
            console.print(msg_panel)

    console.print()


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


def display_file_list(files: list, title: str = "Files in Context"):
    """Display a list of files in a nicely formatted table.

    Args:
        files: List of file paths
        title: Title for the file list table
    """
    if not files:
        console.print(
            Panel(
                "[yellow]No files in context[/yellow]",
                title=title,
                border_style="bright_yellow",
                box=box.ROUNDED,
            )
        )
        return

    table = Table(
        show_header=True,
        header_style="bright_yellow",
        border_style="bright_yellow",
        box=box.ROUNDED,
        title=title,
        title_style="bright_yellow",
    )

    table.add_column("File Path", style="cyan")
    table.add_column("Status", style="green", justify="right")

    for file_path in files:
        table.add_row(
            str(file_path),
            "[green]✓[/green]" if Path(file_path).exists() else "[red]✗[/red]",
        )

    console.print()
    console.print(table)
    console.print()
