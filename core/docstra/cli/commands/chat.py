"""Chat command for the Docstra CLI."""

import os
import click
import asyncio
from pathlib import Path

from rich.prompt import Confirm
from rich.markdown import Markdown
from rich.live import Live

from docstra.service import DocstraService
from docstra.config import DocstraConfig
from docstra.cli.base import DocstraCommand
from docstra.cli.utils import (
    display_help_message,
    list_sessions,
    show_session_info,
    get_user_input,
    get_session_by_alias,
    save_session_alias,
    get_session_aliases,
    setup_history,
    clear_screen,
    get_docstra_dir,
)


class ChatCommand(DocstraCommand):
    """Command to start a chat session with Docstra."""

    def execute(
        self,
        session_id: str = None,
        log_level: str = None,
        log_file: str = None,
        debug: bool = False,
    ):
        """Execute the chat command.

        Args:
            session_id: Session ID or alias to use
            log_level: Log level to use
            log_file: Log file path
            debug: Whether to show debug information
        """
        from docstra.cli.utils import display_header

        # Display the header with version
        display_header(f"Chat Session - {self.working_dir}")

        try:
            # Load config first
            config_path = Path(self.working_dir) / ".docstra" / "config.json"
            config = DocstraConfig.from_file(str(config_path))

            # Override log settings if provided
            if log_level:
                config.log_level = log_level
            if log_file:
                config.log_file = log_file

            # Initialize service with modified config
            service = self.initialize_service(str(config_path))

            # Setup session
            current_session_id = self._setup_session(service, session_id)
            if not current_session_id:
                return

            # Set up readline history
            history_file = get_docstra_dir(str(self.working_dir)) / "chat_history.txt"
            setup_history(history_file)

            # Get session info
            session = service.get_session(current_session_id)
            session_display = session.config.name or current_session_id[:8] + "..."

            self.console.print(
                f"\n[bold blue]Docstra Chat[/bold blue]\n"
                f"Current session: [bold blue]{session_display}[/bold blue]\n"
                f"Model: [bold green]{session.config.model_name}[/bold green]\n"
                f"Type 'help' for available commands or 'exit' to quit.\n"
            )

            # Chat loop
            self._run_chat_loop(service, current_session_id, debug)

            self.console.print("Chat session ended.")

        except Exception as e:
            self.display_error(f"Error in chat: {str(e)}")

    def _setup_session(self, service: DocstraService, session_id: str = None) -> str:
        """Set up the chat session.

        Args:
            service: Service instance
            session_id: Optional session ID or alias

        Returns:
            Resolved session ID to use
        """
        if session_id:
            # Try to resolve by alias or partial ID
            resolved_id = get_session_by_alias(
                service, str(self.working_dir), session_id
            )
            if not resolved_id:
                self.console.print(
                    f"[bold red]Error:[/bold red] Session {session_id} not found."
                )
                if Confirm.ask("Create a new session instead?"):
                    current_session_id = service.create_session()
                    if Confirm.ask(
                        f"Would you like to name this session '{session_id}'?"
                    ):
                        service.rename_session(current_session_id, session_id)
                        save_session_alias(
                            str(self.working_dir), current_session_id, session_id
                        )
                else:
                    return None
            else:
                current_session_id = resolved_id
        else:
            # Get existing sessions
            session_ids = service.get_all_session_ids()

            if not session_ids:
                # No sessions found, create one
                self.console.print(
                    "No existing sessions found. Creating a new session."
                )
                current_session_id = service.create_session()
            else:
                # Use the most recent session if any exist
                current_session_id = session_ids[0]

        return current_session_id

    def _run_chat_loop(self, service: DocstraService, session_id: str, debug: bool = False):
        """Run the main chat loop.

        Args:
            service: Service instance
            session_id: Session ID to use
            debug: Whether to show debug information
        """
        while True:
            try:
                # Get user input
                user_input = get_user_input("\nYou > ")

                # Check for special commands
                user_input = user_input.strip()

                # Empty input
                if not user_input:
                    continue

                # Exit commands
                if user_input.lower() in ("exit", "quit", "bye"):
                    break

                # Help command
                elif user_input.lower() == "help":
                    display_help_message()
                    continue

                # Clear command
                elif user_input.lower() == "clear":
                    clear_screen()
                    continue

                # Session commands
                elif (
                    user_input.lower() == "sessions"
                    or user_input.lower() == "session list"
                ):
                    list_sessions(service, get_session_aliases(str(self.working_dir)))
                    continue

                elif user_input.lower().startswith("session info"):
                    parts = user_input.split(maxsplit=2)
                    session_to_show = parts[2] if len(parts) > 2 else session_id
                    resolved_id = get_session_by_alias(
                        service, str(self.working_dir), session_to_show
                    )
                    if resolved_id:
                        show_session_info(service, resolved_id)
                    else:
                        self.console.print(
                            f"[red]Session {session_to_show} not found[/red]"
                        )
                    continue

                elif user_input.lower().startswith(
                    "session switch"
                ) or user_input.lower().startswith("use"):
                    parts = user_input.split(maxsplit=2)

                    # Handle both "session switch ID" and "use ID" formats
                    if user_input.lower().startswith("use"):
                        session_to_switch = parts[1] if len(parts) > 1 else None
                    else:
                        session_to_switch = parts[2] if len(parts) > 2 else None

                    if not session_to_switch:
                        self.console.print("[red]No session specified[/red]")
                        continue

                    resolved_id = get_session_by_alias(
                        service, str(self.working_dir), session_to_switch
                    )
                    if resolved_id:
                        session_id = resolved_id
                        session = service.get_session(session_id)
                        
                        # Update retriever's context with the session's context files
                        if hasattr(session, "context_files") and service.retriever:
                            try:
                                if hasattr(service.retriever, "set_specific_context_files"):
                                    if session.context_files:
                                        service.retriever.set_specific_context_files(session.context_files)
                                    else:
                                        service.retriever.clear_specific_context_files()
                                    self.console.print(
                                        f"[blue]Using context files: {len(session.context_files)} file(s)[/blue]"
                                    )
                            except Exception as e:
                                self.console.print(f"[yellow]Warning: Could not set context files: {str(e)}[/yellow]")
                        
                        session_display = session.config.name or session_id[:8] + "..."
                        self.console.print(
                            f"[green]Switched to session: {session_display}[/green]"
                        )
                    else:
                        self.console.print(
                            f"[red]Session {session_to_switch} not found[/red]"
                        )
                    continue

                elif user_input.lower().startswith("session rename"):
                    parts = user_input.split(maxsplit=3)
                    if len(parts) < 4:
                        self.console.print(
                            "[red]Usage: session rename <session_id> <new_name>[/red]"
                        )
                        continue

                    session_to_rename = parts[2]
                    new_name = parts[3]

                    resolved_id = get_session_by_alias(
                        service, str(self.working_dir), session_to_rename
                    )
                    if resolved_id:
                        if service.rename_session(resolved_id, new_name):
                            save_session_alias(
                                str(self.working_dir), resolved_id, new_name
                            )
                            self.console.print(
                                f"[green]Renamed session to: {new_name}[/green]"
                            )

                            # Update current session display if it's the active one
                            if resolved_id == session_id:
                                session = service.get_session(session_id)
                                session_display = (
                                    session.config.name or session_id[:8] + "..."
                                )
                        else:
                            self.console.print(f"[red]Failed to rename session[/red]")
                    else:
                        self.console.print(
                            f"[red]Session {session_to_rename} not found[/red]"
                        )
                    continue

                elif user_input.lower().startswith("session delete"):
                    parts = user_input.split(maxsplit=2)
                    if len(parts) < 3:
                        self.console.print(
                            "[red]Usage: session delete <session_id>[/red]"
                        )
                        continue

                    session_to_delete = parts[2]

                    # Don't delete the current session
                    if session_to_delete == session_id:
                        self.console.print(
                            "[red]Cannot delete the current session[/red]"
                        )
                        continue

                    resolved_id = get_session_by_alias(
                        service, str(self.working_dir), session_to_delete
                    )
                    if resolved_id:
                        if Confirm.ask(
                            f"Are you sure you want to delete session {session_to_delete}?"
                        ):
                            if service.delete_session(resolved_id):
                                self.console.print(
                                    f"[green]Deleted session: {session_to_delete}[/green]"
                                )
                            else:
                                self.console.print(
                                    f"[red]Failed to delete session[/red]"
                                )
                    else:
                        self.console.print(
                            f"[red]Session {session_to_delete} not found[/red]"
                        )
                    continue

                # File management commands
                elif user_input.lower().startswith("file add"):
                    parts = user_input.split(maxsplit=2)
                    if len(parts) < 3:
                        self.console.print("[red]Usage: file add <file_path>[/red]")
                        continue

                    file_path = parts[2]

                    # Handle relative paths
                    full_path = os.path.join(str(self.working_dir), file_path)
                    if os.path.exists(full_path):
                        try:
                            service.add_context(session_id, file_path)
                            self.console.print(
                                f"[green]Added file to context: {file_path}[/green]"
                            )
                        except Exception as e:
                            self.console.print(
                                f"[red]Error adding file: {str(e)}[/red]"
                            )
                    else:
                        self.console.print(f"[red]File not found: {file_path}[/red]")
                    continue

                elif user_input.lower() == "file list":
                    try:
                        context_files = service.get_context_files(session_id)
                        if not context_files:
                            self.console.print("[yellow]No files in specific context[/yellow]")
                            self.console.print("[blue]Using all indexed documents for context retrieval[/blue]")
                        else:
                            self.console.print("[bold]Files in specific context:[/bold]")
                            for file in context_files:
                                self.console.print(f"  {file}")
                            self.console.print("\n[blue]Note: Retrieval will prioritize these files. When no files are specified, all indexed documents are used.[/blue]")
                    except Exception as e:
                        self.console.print(f"[red]Error listing files: {str(e)}[/red]")
                    continue

                elif user_input.lower().startswith("file remove"):
                    parts = user_input.split(maxsplit=2)
                    if len(parts) < 3:
                        self.console.print("[red]Usage: file remove <file_path>[/red]")
                        continue

                    file_path = parts[2]

                    try:
                        if service.remove_context_file(session_id, file_path):
                            self.console.print(
                                f"[green]Removed file from context: {file_path}[/green]"
                            )
                        else:
                            self.console.print(
                                f"[yellow]File not in context: {file_path}[/yellow]"
                            )
                    except Exception as e:
                        self.console.print(f"[red]Error removing file: {str(e)}[/red]")
                    continue

                # Process regular message with streaming
                self.run_async(self.stream_response(service, session_id, user_input, debug=debug))

            except KeyboardInterrupt:
                if Confirm.ask("\nDo you want to exit?"):
                    break
                continue
            except Exception as e:
                self.console.print(f"[bold red]Error:[/bold red] {str(e)}")


@click.command("chat")
@click.argument("dir_path", default=".", type=click.Path(exists=True))
@click.option("--session", "-s", help="Session ID or alias to use")
@click.option("--log-level", help="Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)")
@click.option("--log-file", help="Path to log file")
@click.option("--debug", is_flag=True, help="Show debug information including prompts and full responses")
def chat(dir_path, session, log_level, log_file, debug):
    """Start a chat session with Docstra in the specified directory."""
    command = ChatCommand(working_dir=dir_path)
    command.execute(session_id=session, log_level=log_level, log_file=log_file, debug=debug)
