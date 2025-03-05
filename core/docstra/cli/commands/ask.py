"""Ask command for the Docstra CLI."""

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
from docstra.cli.utils import resolve_relative_path


class AskCommand(DocstraCommand):
    """Command to ask a one-off question about a file."""

    def execute(
        self,
        file_path: Path | str,
        question: str,
        log_level: str = None,
        log_file: str = None,
        debug: bool = False,
    ):
        """Execute the ask command.

        Args:
            file_path: Path to the file to ask about
            question: Question to ask
            log_level: Log level to use
            log_file: Log file path
            debug: Whether to show debug information
        """
        from docstra.cli.utils import display_header

        # Normalize file path
        file_path = Path(file_path).resolve()

        # Handle absolute or relative paths
        if Path(file_path).is_absolute():
            abs_file_path = file_path
            rel_file_path = Path(file_path).relative_to(self.working_dir)
        else:
            abs_file_path = self.working_dir / file_path
            rel_file_path = file_path

        # Display header with file information
        display_header(f"Asking about {rel_file_path}")

        if not os.path.exists(abs_file_path):
            self.display_error(f"File {rel_file_path} not found.")
            return

        try:
            # Load config
            config_path = Path(self.working_dir) / ".docstra" / "config.json"
            config = DocstraConfig.from_file(str(config_path))

            # Override log settings if provided
            if log_level:
                config.log_level = log_level
            if log_file:
                config.log_file = log_file

            # Initialize service
            service = self.initialize_service(str(config_path))

            # Create a session
            session_id = service.create_session()

            # Add file context
            service.add_context(session_id, rel_file_path)

            # Process the message with streaming
            response = self.run_async(
                self.stream_response(service, session_id, question, debug=debug)
            )

            # Ask if user wants to continue in chat mode with this session
            if Confirm.ask("Would you like to continue chatting about this file?"):
                # Import here to avoid circular imports
                from docstra.cli.commands.chat import ChatCommand

                chat_cmd = ChatCommand(working_dir=str(self.working_dir))
                chat_cmd.execute(
                    session_id=session_id,
                    log_level=log_level,
                    log_file=log_file,
                    debug=debug,
                )

        except Exception as e:
            self.display_error(str(e))


@click.command("ask")
@click.argument("dir_path", type=click.Path(exists=True))
@click.argument("file_path", type=str)
@click.argument("question", type=str)
@click.option("--log-level", help="Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)")
@click.option("--log-file", help="Path to log file")
@click.option(
    "--debug",
    is_flag=True,
    help="Show debug information including prompts and full responses",
)
def ask(dir_path, file_path, question, log_level, log_file, debug):
    """Ask a question about a specific file.

    DIR_PATH is the directory containing the codebase.
    FILE_PATH is the path to the file to ask about.
    QUESTION is the question to ask about the file.
    """
    command = AskCommand(working_dir=dir_path)
    command.execute(file_path, question, log_level, log_file, debug)
