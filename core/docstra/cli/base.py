"""Base command class for Docstra CLI."""

import asyncio
import os
from pathlib import Path
from typing import Optional, Any, AsyncGenerator

from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel

from docstra.service import DocstraService
from docstra.config import DocstraConfig


class DocstraCommand:
    """Base class for Docstra CLI commands."""

    def __init__(
        self, working_dir: Optional[str] = None, config: Optional[DocstraConfig] = None
    ):
        """Initialize the command with working directory and config.

        Args:
            working_dir: Working directory for the command
            config: Optional configuration to use
        """
        self.working_dir = Path(working_dir).absolute() if working_dir else Path.cwd()
        self.config = config
        self.console = Console()
        self.service = None

    def initialize_service(
        self,
        config_path: Optional[str] = None,
        log_level: Optional[str] = None,
        log_file: Optional[str] = None,
    ) -> DocstraService:
        """Initialize the Docstra service.

        Args:
            config_path: Path to the configuration file (optional, will auto-detect if not provided)
            log_level: Optional log level override
            log_file: Optional log file path

        Returns:
            Initialized DocstraService
        """
        # Use cached service if already initialized
        if self.service:
            return self.service
            
        # Ensure environment variables are loaded from .env file
        env_file = Path(self.working_dir) / ".docstra" / ".env"
        if env_file.exists():
            try:
                from dotenv import load_dotenv
                load_dotenv(env_file)
                self.console.print(f"[green]Loaded environment variables from {env_file}[/green]")
            except Exception as e:
                self.console.print(f"[yellow]Warning: Could not load .env file: {str(e)}[/yellow]")

        service_args = {"working_dir": str(self.working_dir)}

        # If config_path not explicitly provided, we'll let DocstraService.load method
        # handle the config loading with proper precedence
        if config_path:
            service_args["config_path"] = config_path

        if log_level:
            service_args["log_level"] = log_level

        self.service = DocstraService(**service_args)
        return self.service

    def get_config_path(self) -> Path:
        """Get the path to the config file.

        This checks for configuration in two locations:
        1. .docstra/config.json (preferred)
        2. docstra.json in the root directory (fallback for legacy support)

        Returns:
            Path to the configuration file
        """
        # First check for .docstra/config.json
        dotconfig_path = self.working_dir / ".docstra" / "config.json"
        if dotconfig_path.exists():
            return dotconfig_path

        # Fall back to root config
        return self.working_dir / "docstra.json"

    def ensure_initialized(self) -> bool:
        """Check if Docstra is initialized in the current directory.

        Docstra is considered initialized if either:
        1. A .docstra/config.json file exists (preferred approach)
        2. A docstra.json file exists in the working directory (legacy support)

        Returns:
            True if initialized, False otherwise
        """
        # Check for .docstra/config.json
        dotconfig_path = self.working_dir / ".docstra" / "config.json"
        if dotconfig_path.exists():
            return True

        # Check for root config (legacy support)
        root_config_path = self.working_dir / "docstra.json"
        return root_config_path.exists()

    def display_success(self, message: str, title: str = "Success") -> None:
        """Display a success message.

        Args:
            message: The success message
            title: Optional title for the panel
        """
        self.console.print(
            Panel.fit(
                message,
                title=title,
                border_style="green",
            )
        )

    def display_error(self, message: str, title: str = "Error") -> None:
        """Display an error message.

        Args:
            message: The error message
            title: Optional title for the panel
        """
        self.console.print(
            Panel.fit(
                f"❌ {message}",
                title=title,
                border_style="red",
            )
        )

    async def stream_response(
        self,
        service: DocstraService,
        session_id: str,
        message: str,
        debug: bool = False,
    ) -> str:
        """Stream response from the service and display it.

        Args:
            service: DocstraService instance
            session_id: Session ID to use
            message: Message to process
            debug: Whether to show debug information including prompts and context

        Returns:
            The complete response
        """
        # First, show a spinner while the model is starting to process
        with self.console.status(
            "[bold bright_yellow]Docstra is thinking...[/bold bright_yellow]",
            spinner="dots",
            spinner_style="bright_yellow",
        ):
            # Call the service once to start processing
            # We just want to get the first chunk to know the model has started generating
            first_chunk_future = asyncio.ensure_future(
                anext(
                    service.process_message_stream(
                        session_id, message, debug
                    ).__aiter__()
                )
            )

            # Wait for the first chunk or timeout after 3 seconds
            try:
                # Use asyncio.sleep as a timeout since asyncio.wait_for isn't available in all contexts
                for _ in range(30):  # 3 seconds total (30 * 0.1s)
                    if first_chunk_future.done():
                        break
                    await asyncio.sleep(0.1)

                # Get the first chunk result if available
                first_chunk = ""
                if first_chunk_future.done():
                    first_chunk = first_chunk_future.result()
            except Exception:
                # If anything goes wrong, we'll just start the stream from scratch
                first_chunk = ""

        # Get session and debug information if needed
        if debug:
            session = service.get_session(session_id)
            context_files = service.get_context_files(session_id)
            chat_history = session.chat_history.messages

            # Show debug information
            self.console.print("\n[bold yellow]DEBUG INFORMATION[/bold yellow]")
            self.console.print("[bold]Context Files:[/bold]")
            for file in context_files:
                self.console.print(f"  - {file}")

            self.console.print("\n[bold]Chain Input:[/bold]")
            # Format chat history for display - handling both dict and LangChain message objects
            formatted_history = []
            for msg in chat_history:
                if hasattr(msg, "type") and hasattr(msg, "content"):
                    # LangChain message object
                    formatted_history.append(f"{msg.type}: {msg.content}")
                elif isinstance(msg, dict) and "role" in msg and "content" in msg:
                    # Dictionary format
                    formatted_history.append(f"{msg['role']}: {msg['content']}")

            chain_input = {
                "question": message,
                "chat_history": formatted_history,
                "cwd": str(service.working_dir),
            }
            self.console.print_json(data=chain_input)

            # Display retrieved context
            self.console.print("\n[bold]Retrieved Context (preview):[/bold]")
            context = service.preview_context(session_id, message)
            self.console.print(
                Markdown(context[:500] + "..." if len(context) > 500 else context)
            )

            self.console.print("\n[bold]System Prompt:[/bold]")
            self.console.print(Markdown(session.config.system_prompt))

            self.console.print("\n-------------------")

        # Display the streaming response header
        self.console.print("\n[bold bright_yellow]Docstra[/bold bright_yellow]:")

        # Process the message with streaming
        response = first_chunk  # Start with the first chunk if we got one

        with Live(Markdown(response), refresh_per_second=10, transient=True) as live:
            try:
                # Create a new stream generator
                stream = service.process_message_stream(
                    session_id, message, debug=debug
                ).__aiter__()

                # Skip the first chunk if we already have it
                if first_chunk:
                    next_chunk = await anext(stream, "")

                # Process the rest of the chunks
                async for chunk in stream:
                    response += chunk
                    # Update the live display with new content
                    live.update(Markdown(response))
                    # Small delay to reduce CPU usage
                    await asyncio.sleep(0.01)
            except Exception as e:
                self.console.print(
                    f"[bold red]Error during streaming:[/bold red] {str(e)}"
                )
                error_msg = f"\n\nError: {str(e)}"
                response += error_msg
                live.update(Markdown(response))
                await asyncio.sleep(1)  # Give time to see the error

        # Final print with the complete response after streaming ends
        self.console.print(Markdown(response))

        return response

    def run_async(self, coro):
        """Run an async coroutine in a sync context.

        Args:
            coro: Coroutine to run

        Returns:
            The result of the coroutine
        """
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            # If no event loop exists, create a new one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(coro)
