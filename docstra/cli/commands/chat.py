"""Chat command for Docstra CLI."""

import asyncio
from typing import Optional

import click
from rich.live import Live
from rich.markdown import Markdown
from rich.console import Console
from rich.prompt import Prompt

from docstra.cli.base import BaseCommand

# Create a console instance for UI display
console = Console()


class ChatCommand(BaseCommand):
    """Chat with Docstra about your codebase."""

    async def execute_async(
        self,
        session_id: Optional[str] = None,
        debug: bool = False,
        log_level: Optional[str] = None,
        log_file: Optional[str] = None,
    ) -> None:
        """Execute the chat command asynchronously.

        Args:
            session_id: Optional session ID to use.
            debug: Whether to show debug information.
            log_level: Optional log level override.
            log_file: Optional log file path.
        """
        # Ensure workspace is initialized
        self.ensure_initialized()

        # Get or create session
        if not session_id:
            session_id = self.service.create_session()

        # Get or create session from session manager
        try:
            session = self.service.session_manager.get_session(session_id)
        except Exception:
            # If session doesn't exist, create a new one
            session_id = self.service.create_session()
            session = self.service.session_manager.get_session(session_id)

        console.print("[bold green]Welcome to Docstra Chat![/bold green]")
        console.print(f"Session ID: {session_id}")
        console.print("Type 'exit' or press Ctrl+C to end the session.\n")

        while True:
            try:
                # Get user input
                message = Prompt.ask("[bold blue]You[/bold blue]")

                # Check for exit command
                if message.lower() in ["exit", "quit"]:
                    console.print("\n[bold green]Goodbye![/bold green]")
                    break

                # Add user message to session
                session.add_user_message(message)

                # Process the message with streaming
                response = ""
                with Live(
                    Markdown(response), refresh_per_second=10, transient=True
                ) as live:
                    try:
                        async for (
                            chunk
                        ) in self.service.llm_chain.process_message_stream(
                            message=message,
                            chat_history=session.get_messages(),
                        ):
                            response += chunk
                            live.update(Markdown(response))
                            await asyncio.sleep(0.01)
                    except Exception as e:
                        self.display_error(str(e))
                        continue

                # Add assistant message to session
                session.add_assistant_message(response)

                # Final print with the complete response
                console.print(Markdown(response))
                console.print()  # Add a blank line for readability

            except KeyboardInterrupt:
                console.print("\n[bold green]Goodbye![/bold green]")
                break
            except Exception as e:
                self.display_error(str(e))
                continue

    def execute(
        self,
        session_id: Optional[str] = None,
        debug: bool = False,
        log_level: Optional[str] = None,
        log_file: Optional[str] = None,
    ) -> None:
        """Execute the chat command.

        Args:
            session_id: Optional session ID to use.
            debug: Whether to show debug information.
            log_level: Optional log level override.
            log_file: Optional log file path.
        """
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        loop.run_until_complete(
            self.execute_async(
                session_id=session_id,
                debug=debug,
                log_level=log_level,
                log_file=log_file,
            )
        )


@click.command("chat")
@click.option("--session-id", help="Session ID to use")
@click.option("--debug", is_flag=True, help="Show debug information")
@click.option("--log-level", help="Set log level")
@click.option("--log-file", help="Set log file path")
@click.option(
    "--working-dir", type=click.Path(exists=True), default=".", help="Working directory"
)
def chat(
    session_id: Optional[str] = None,
    debug: bool = False,
    log_level: Optional[str] = None,
    log_file: Optional[str] = None,
    working_dir: str = ".",
) -> None:
    """Start an interactive chat session with Docstra about your codebase."""
    cmd = ChatCommand(working_dir=working_dir)
    cmd.execute(
        session_id=session_id,
        debug=debug,
        log_level=log_level,
        log_file=log_file,
    )
