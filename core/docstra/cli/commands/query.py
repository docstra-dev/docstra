"""Query command for the Docstra CLI."""

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


class QueryCommand(DocstraCommand):
    """Command to query the codebase with a one-off question."""

    def execute(
        self,
        question: str,
        file_paths: list[str] = None,
        log_level: str = None,
        log_file: str = None,
        debug: bool = False,
    ):
        """Execute the query command.

        Args:
            question: Question to ask
            file_paths: Optional list of file paths to include as context
            log_level: Log level to use
            log_file: Log file path
            debug: Whether to show debug information
        """
        from docstra.cli.utils import display_header

        # Display header
        display_header(f"Querying codebase")

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

            # Add file context if provided
            if file_paths and len(file_paths) > 0:
                for file_path in file_paths:
                    # Normalize file path
                    path = Path(file_path)
                    
                    # Handle absolute or relative paths
                    if path.is_absolute():
                        abs_file_path = path
                        rel_file_path = path.relative_to(self.working_dir)
                    else:
                        abs_file_path = self.working_dir / path
                        rel_file_path = path
                    
                    if not os.path.exists(abs_file_path):
                        self.display_error(f"File {rel_file_path} not found.")
                        continue
                        
                    service.add_context(session_id, str(rel_file_path))

            # Process the message with streaming
            response = self.run_async(
                self.stream_response(service, session_id, question, debug=debug)
            )

            # Ask if user wants to continue in chat mode with this session
            if Confirm.ask("Would you like to continue chatting?"):
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


@click.command("query")
@click.argument("question", type=str)
@click.option(
    "--files", "-f", 
    multiple=True, 
    help="Optional file paths to include as context"
)
@click.option("--log-level", help="Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)")
@click.option("--log-file", help="Path to log file")
@click.option(
    "--debug",
    is_flag=True,
    help="Show debug information including prompts and full responses",
)
def query(question, files, log_level, log_file, debug):
    """Query the codebase with a question.

    QUESTION is the question to ask about the codebase.
    
    Examples:
      docstra query "Where is the config defined?"
      docstra query "How does the file loading work?" --files src/loader.py src/utils.py
    """
    command = QueryCommand(working_dir=".")
    command.execute(question, files, log_level, log_file, debug)