import os
import click
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.panel import Panel
from rich import print as rprint
from typing import Optional

from docstra.core import DocstraService, DocstraConfig

console = Console()

header_art = """
  ██████╗  ██████╗  ██████╗███████╗████████╗██████╗  █████╗ 
  ██╔══██╗██╔═══██╗██╔════╝██╔════╝╚══██╔══╝██╔══██╗██╔══██╗
  ██║  ██║██║   ██║██║     ███████╗   ██║   ██████╔╝███████║
  ██║  ██║██║   ██║██║       ╔══██╝   ██║   ██╔══██╗██╔══██║
  ██████╔╝╚██████╔╝╚██████╗███████╗   ██║   ██║  ██║██║  ██║
  ╚═════╝  ╚═════╝  ╚═════╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝
"""


@click.group()
def cli():
    """Docstra - An LLM-powered code assistant."""

    rprint(header_art)
    rprint("Welcome to Docstra! 🚀")

    # Load environment variables
    print(os.getenv("OPENAI_API_KEY"))
    pass


@cli.command()
@click.option("--dir", "-d", help="Working directory", default=".")
@click.option("--model", "-m", help="LLM model to use", default=None)
@click.option("--temp", "-t", type=float, help="Model temperature", default=None)
def init(dir: str, model: Optional[str], temp: Optional[float]):
    """Initialize Docstra in the specified directory."""
    dir = os.path.abspath(dir)
    console.print(f"Initializing Docstra in [bold]{dir}[/bold]")

    # Create config with custom values if provided
    config = DocstraConfig()
    if model:
        config.model_name = model
    if temp is not None:
        config.temperature = temp

    # Create the service, which will index the codebase
    try:
        service = DocstraService(working_dir=dir, config_path=None)
        # Force reindexing
        service._index_codebase()

        console.print(
            Panel.fit(
                "✅ Docstra initialized successfully!",
                title="Success",
                border_style="green",
            )
        )
        console.print(
            f"Configuration saved to [bold]{os.path.join(dir, '.docstra', 'config.json')}[/bold]"
        )
    except Exception as e:
        console.print(
            Panel.fit(
                f"❌ Error initializing Docstra: {str(e)}",
                title="Error",
                border_style="red",
            )
        )


@cli.command()
@click.option("--dir", "-d", help="Working directory", default=".")
def chat(dir: str):
    """Start an interactive chat session with Docstra."""
    dir = os.path.abspath(dir)
    console.print(f"Starting Docstra chat in [bold]{dir}[/bold]")

    try:
        # Initialize service
        service = DocstraService(working_dir=dir)

        # Create a session
        session_id = service.create_session()
        console.print(
            Panel.fit(
                "Docstra is ready to chat! Type 'exit' or press Ctrl+C to quit.",
                title="Chat Session",
                border_style="blue",
            )
        )

        # Chat loop
        while True:
            try:
                # Get user input
                user_input = Prompt.ask("\n[bold blue]You[/bold blue]")

                # Check for exit command
                if user_input.lower() in ("exit", "quit", "bye"):
                    break

                # Show typing indicator
                with console.status("[bold green]Docstra is thinking...[/bold green]"):
                    # Process the message
                    response = service.process_message(session_id, user_input)

                # Display the response
                console.print("\n[bold green]Docstra[/bold green]")
                console.print(Markdown(response))

            except KeyboardInterrupt:
                break
            except Exception as e:
                console.print(f"[bold red]Error:[/bold red] {str(e)}")

        console.print("Chat session ended.")

    except Exception as e:
        console.print(
            Panel.fit(
                f"❌ Error starting chat: {str(e)}", title="Error", border_style="red"
            )
        )


@cli.command()
@click.option("--dir", "-d", help="Working directory", default=".")
@click.option("--host", help="Host to bind the server to", default="127.0.0.1")
@click.option("--port", "-p", type=int, help="Port to bind the server to", default=8000)
def serve(dir: str, host: str, port: int):
    """Start the Docstra API server."""
    dir = os.path.abspath(dir)
    console.print(
        f"Starting Docstra API server for [bold]{dir}[/bold] at http://{host}:{port}"
    )

    try:
        # Import here to avoid circular imports
        from .api import start_server

        # Start the server
        start_server(host=host, port=port, working_dir=dir)
    except ImportError:
        console.print(
            "[bold red]Error:[/bold red] Could not import docstra_api. Make sure it's installed."
        )
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")


@cli.command()
@click.option("--dir", "-d", help="Working directory", default=".")
@click.option("--file", "-f", required=True, help="File to ask about")
@click.argument("question")
def ask(dir: str, file: str, question: str):
    """Ask a one-off question about a specific file."""
    dir = os.path.abspath(dir)
    file_path = os.path.join(dir, file)

    console.print(f"Asking about [bold]{file}[/bold]")

    if not os.path.exists(file_path):
        console.print(f"[bold red]Error:[/bold red] File {file} not found.")
        return

    try:
        # Initialize service
        service = DocstraService(working_dir=dir)

        # Create a session
        session_id = service.create_session()

        # Add file context
        service.add_context(session_id, file)

        # Show typing indicator
        with console.status("[bold green]Docstra is thinking...[/bold green]"):
            # Process the question
            response = service.process_message(session_id, question)

        # Display the response
        console.print("\n[bold green]Docstra[/bold green]")
        console.print(Markdown(response))

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")


@cli.command()
@click.option("--dir", "-d", help="Working directory", default=".")
def reindex(dir: str):
    """Re-index the codebase in the specified directory."""
    dir = os.path.abspath(dir)
    console.print(f"Re-indexing codebase in [bold]{dir}[/bold]")

    try:
        # Initialize service
        service = DocstraService(working_dir=dir)

        # Force reindexing
        service._index_codebase()

        console.print(
            Panel.fit(
                "✅ Codebase re-indexed successfully!",
                title="Success",
                border_style="green",
            )
        )
    except Exception as e:
        console.print(
            Panel.fit(
                f"❌ Error re-indexing codebase: {str(e)}",
                title="Error",
                border_style="red",
            )
        )


if __name__ == "__main__":
    cli()
