"""Query command for Docstra CLI."""

import asyncio
from typing import Optional

import click
from rich.live import Live
from rich.markdown import Markdown
from rich.console import Console

from docstra.cli.base import BaseCommand

# Create a console instance for UI display
console = Console()


class QueryCommand(BaseCommand):
    """Query your codebase with Docstra."""

    async def execute_async(
        self,
        query: str,
        session_id: Optional[str] = None,
        debug: bool = False,
        log_level: Optional[str] = None,
        log_file: Optional[str] = None,
    ) -> None:
        """Execute the query command asynchronously.

        Args:
            query: The query to send.
            session_id: Optional session ID to use.
            debug: Whether to show debug information.
            log_level: Optional log level override.
            log_file: Optional log file path.
        """
        # Ensure workspace is initialized
        self.ensure_initialized()

        # Get or create session
        if not session_id:
            session_id = "default"

        # Process the query with streaming
        response = ""
        with Live(Markdown(response), refresh_per_second=10, transient=True) as live:
            try:
                async for chunk in self.service.process_message_stream(
                    session_id, query, debug=debug
                ):
                    response += chunk
                    live.update(Markdown(response))
                    await asyncio.sleep(0.01)
            except Exception as e:
                self.display_error(str(e))
                return

        # Final print with the complete response
        console.print(Markdown(response))

    def execute(
        self,
        query: str,
        session_id: Optional[str] = None,
        debug: bool = False,
        log_level: Optional[str] = None,
        log_file: Optional[str] = None,
    ) -> None:
        """Execute the query command.

        Args:
            query: The query to send.
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
                query=query,
                session_id=session_id,
                debug=debug,
                log_level=log_level,
                log_file=log_file,
            )
        )


@click.command("query")
@click.argument("query", required=True)
@click.option("--session-id", help="Session ID to use")
@click.option("--debug", is_flag=True, help="Show debug information")
@click.option("--log-level", help="Set log level")
@click.option("--log-file", help="Set log file path")
@click.option(
    "--working-dir", type=click.Path(exists=True), default=".", help="Working directory"
)
def query(
    query: str,
    session_id: Optional[str] = None,
    debug: bool = False,
    log_level: Optional[str] = None,
    log_file: Optional[str] = None,
    working_dir: str = ".",
) -> None:
    """Query your codebase with Docstra."""
    cmd = QueryCommand(working_dir=working_dir)
    cmd.execute(
        query=query,
        session_id=session_id,
        debug=debug,
        log_level=log_level,
        log_file=log_file,
    )
