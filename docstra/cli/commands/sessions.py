"""Session management commands for Docstra CLI."""

from typing import Optional, Dict, Any

import click
from rich.table import Table
from rich.console import Console
from rich.layout import Layout
from rich.spinner import Spinner
from rich.text import Text
from rich.box import Box

from docstra.cli.base import BaseCommand

console = Console()


class SessionsCommand(BaseCommand):
    """Manage Docstra sessions."""

    def execute(
        self,
        action: str,
        session_id: Optional[str] = None,
        name: Optional[str] = None,
        log_level: Optional[str] = None,
        log_file: Optional[str] = None,
    ) -> None:
        """Execute the sessions command.

        Args:
            action: The action to perform (list, info, rename, delete).
            session_id: Optional session ID to operate on.
            name: Optional new name for rename action.
            log_level: Optional log level override.
            log_file: Optional log file path.
        """
        # Ensure workspace is initialized
        self.ensure_initialized()

        # Handle different actions
        if action == "list":
            self._list_sessions()
        elif action == "info":
            if not session_id:
                self.display_error("Session ID is required for info action")
                return
            self._show_session_info(session_id)
        elif action == "rename":
            if not session_id or not name:
                self.display_error(
                    "Session ID and new name are required for rename action"
                )
                return
            self._rename_session(session_id, name)
        elif action == "delete":
            if not session_id:
                self.display_error("Session ID is required for delete action")
                return
            self._delete_session(session_id)
        else:
            self.display_error(f"Unknown action: {action}")

    def _list_sessions(self) -> None:
        """List all available sessions."""
        with self.create_progress("Loading sessions...") as progress:
            task = progress.add_task("Fetching...", total=None)
            session_ids = self.service.get_all_session_ids()
            progress.update(task, completed=True)

        if not session_ids:
            self.display_error("No sessions found")
            return

        table = Table(
            title="Available Sessions",
            show_header=True,
            header_style="bright_yellow",
            border_style="bright_yellow",
            box=Box.ROUNDED,
            title_style="bright_yellow",
            padding=(0, 1),
        )

        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Created", style="magenta")
        table.add_column("Messages", style="blue")

        for session_id in session_ids:
            session = self.service.get_session(session_id)
            if session:
                name = (
                    session.config.name
                    if hasattr(session.config, "name")
                    else "Unnamed"
                )
                created = session.created_at.strftime("%Y-%m-%d %H:%M")
                messages = str(len(session.messages))
                table.add_row(
                    f"[cyan]{session_id[:8]}...[/cyan]",
                    f"[green]{name}[/green]",
                    created,
                    messages,
                )

        console.print()
        console.print(table)
        console.print()

    def _show_session_info(self, session_id: str) -> None:
        """Show information about a specific session.

        Args:
            session_id: ID of the session to show
        """
        with self.create_progress(f"Loading session {session_id}...") as progress:
            task = progress.add_task("Fetching...", total=None)
            session = self.service.get_session(session_id)
            progress.update(task, completed=True)

        if not session:
            self.display_error(f"Session {session_id} not found")
            return

        # Prepare session data
        session_data = {
            "id": session_id,
            "created_at": session.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "name": (
                session.config.name if hasattr(session.config, "name") else "Unnamed"
            ),
            "model": session.config.model_name,
            "temperature": session.config.temperature,
            "message_count": len(session.messages),
            "recent_messages": session.messages[-5:] if session.messages else [],
        }

        self.display_session_info(session_id, session_data)

    def _rename_session(self, session_id: str, name: str) -> None:
        """Rename a session.

        Args:
            session_id: ID of the session to rename
            name: New name for the session
        """
        with self.create_progress(f"Renaming session {session_id}...") as progress:
            task = progress.add_task("Updating...", total=None)
            session = self.service.get_session(session_id)
            if not session:
                self.display_error(f"Session {session_id} not found")
                return

            session.config.name = name
            self.service.save_session(session)
            progress.update(task, completed=True)

        self.display_success(f"Session {session_id} renamed to '{name}'")

    def _delete_session(self, session_id: str) -> None:
        """Delete a session.

        Args:
            session_id: ID of the session to delete
        """
        with self.create_progress(f"Deleting session {session_id}...") as progress:
            task = progress.add_task("Deleting...", total=None)
            if not self.service.delete_session(session_id):
                self.display_error(f"Session {session_id} not found")
                return
            progress.update(task, completed=True)

        self.display_success(f"Session {session_id} deleted")


@click.group("sessions")
@click.option("--log-level", help="Set log level")
@click.option("--log-file", help="Set log file path")
@click.option(
    "--working-dir", type=click.Path(exists=True), default=".", help="Working directory"
)
def sessions(
    log_level: Optional[str] = None,
    log_file: Optional[str] = None,
    working_dir: str = ".",
) -> None:
    """Manage Docstra sessions."""
    pass


@sessions.command("list")
@click.pass_context
def list_sessions(ctx):
    """List all available sessions."""
    cmd = SessionsCommand(working_dir=ctx.parent.params["working_dir"])
    cmd.execute(
        action="list",
        log_level=ctx.parent.params.get("log_level"),
        log_file=ctx.parent.params.get("log_file"),
    )


@sessions.command("info")
@click.argument("session_id", required=True)
@click.pass_context
def session_info(ctx, session_id: str):
    """Show information about a specific session."""
    cmd = SessionsCommand(working_dir=ctx.parent.params["working_dir"])
    cmd.execute(
        action="info",
        session_id=session_id,
        log_level=ctx.parent.params.get("log_level"),
        log_file=ctx.parent.params.get("log_file"),
    )


@sessions.command("rename")
@click.argument("session_id", required=True)
@click.argument("name", required=True)
@click.pass_context
def rename_session(ctx, session_id: str, name: str):
    """Rename a session."""
    cmd = SessionsCommand(working_dir=ctx.parent.params["working_dir"])
    cmd.execute(
        action="rename",
        session_id=session_id,
        name=name,
        log_level=ctx.parent.params.get("log_level"),
        log_file=ctx.parent.params.get("log_file"),
    )


@sessions.command("delete")
@click.argument("session_id", required=True)
@click.pass_context
def delete_session(ctx, session_id: str):
    """Delete a session."""
    cmd = SessionsCommand(working_dir=ctx.parent.params["working_dir"])
    cmd.execute(
        action="delete",
        session_id=session_id,
        log_level=ctx.parent.params.get("log_level"),
        log_file=ctx.parent.params.get("log_file"),
    )
