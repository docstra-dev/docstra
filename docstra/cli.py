import json
import os
from pathlib import Path
import requests  # Added to interact with FastAPI
import click
from dotenv import load_dotenv

from docstra.main import Docstra
from docstra.logger import logger
import logging
from docstra.chat_db import ChatDB


# Initialize the chat session database
chat_db = ChatDB()

# API URL for chat interactions (FastAPI)
CHAT_API_URL = "http://127.0.0.1:8000/chat"

# Constants for repository configuration
REPO_CONFIG_FILENAME = "config.json"
DEFAULT_REPO_CONFIG = {
    "exclusion_rules": {
        "dirs_to_exclude": [".git", ".venv", "node_modules", "__pycache__", "dist", "build"],
        "files_to_exclude": [".env", "Pipfile.lock", "poetry.lock"],
        "file_extensions_to_include": [".py", ".md", ".txt", ".json", ".yaml", ".sh"]
    },
    "throttling": {
        "max_tokens_per_minute": 60000
    }
}

header_art = """
  ██████╗  ██████╗  ██████╗███████╗████████╗██████╗  █████╗ 
  ██╔══██╗██╔═══██╗██╔════╝██╔════╝╚══██╔══╝██╔══██╗██╔══██╗
  ██║  ██║██║   ██║██║     ███████╗   ██║   ██████╔╝███████║
  ██║  ██║██║   ██║██║       ╔══██╝   ██║   ██╔══██╗██╔══██║
  ██████╔╝╚██████╔╝╚██████╗███████╗   ██║   ██║  ██║██║  ██║
  ╚═════╝  ╚═════╝  ╚═════╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝
"""


@click.group(invoke_without_command=True)
@click.pass_context
@click.option('--verbose', '-v', is_flag=True, help="Enable all logging.")
@click.option("--quiet", "-q", is_flag=True, help="Disable all logging.")
def cli(ctx, verbose, quiet):
    """Docstra CLI tool for managing repositories and querying codebases."""

    if verbose:
        logger.setLevel(logging.DEBUG)
    elif quiet:
        logger.setLevel(logging.ERROR)
    else:
        logger.setLevel(logging.WARNING)

    if ctx.invoked_subcommand is None:
        click.secho(header_art, fg="bright_yellow")
        click.secho("Welcome to the Docstra CLI!", fg="bright_yellow", bold=True)
        click.echo(ctx.get_help())


@cli.command()
@click.option("--repo", "-rp", default=".", help="Path to the repository to initialize Docstra in.")
@click.option("--api-key", "-k", help="OpenAI API key to use for the repository.")
@click.option("--embeddings-model", "-em", default="text-embedding-3-small", help="OpenAI model to use for embeddings.")
@click.option("--chat-model", "-cm", default="gpt-4o-mini", help="OpenAI model to use for chat.")
@click.option("--max-tokens", "-t", default=60000, help="Maximum tokens per minute for OpenAI API throttling.")
def init(repo, api_key, embeddings_model, chat_model, max_tokens):
    """Initialize repository-specific configuration for Docstra."""
    repo = Path(repo).resolve()
    docstra_dir = repo / ".docstra"
    env_path = docstra_dir / ".env"

    click.secho(header_art, fg="bright_yellow")

    if not docstra_dir.exists():
        docstra_dir.mkdir(parents=True, exist_ok=True)

    if not env_path.exists():
        env_path.touch()
        if api_key:
            with open(env_path, "a") as f:
                f.write(f"OPENAI_API_KEY={api_key}\n")
        else:
            click.secho("Docstra needs an OpenAI API key to function. It will be stored in `.docstra/.env`.",
                        fg="bright_yellow")
            api_key = click.prompt(click.style("Enter your OpenAI API key", bold=True), type=str)

            with open(env_path, "a") as f:
                f.write(f"OPENAI_API_KEY={api_key}\n")
        click.secho("OpenAI API key saved successfully.", fg="bright_green")

    load_dotenv(env_path)

    # Create repository-specific config file if it doesn’t exist
    repo_config_path = docstra_dir / REPO_CONFIG_FILENAME

    if not repo_config_path.exists():
        new_repo_config = DEFAULT_REPO_CONFIG.copy()
        if embeddings_model:
            new_repo_config["embeddings_model"] = embeddings_model
        if chat_model:
            new_repo_config["chat_model"] = chat_model
        if max_tokens:
            new_repo_config["throttling"]["max_tokens_per_minute"] = max_tokens

        with open(repo_config_path, "w") as f:
            json.dump(new_repo_config, f, indent=4)


    click.secho("Docstra initialization complete. To update your settings, run `docstra config` later.")
    click.secho("You can now start ingesting the repository using `docstra ingest`.", fg="bright_yellow")


@cli.command()
@click.option("--repo", "-rp", default=".", help="Path to the repository to initialize Docstra in.")
def ingest(repo):
    """Ingest a repository to extract metadata and store embeddings."""

    repo = Path(repo).resolve()
    docstra = Docstra(repo)

    click.echo(f"Starting ingestion for repository: {repo}")

    docstra.ingest_repository()

    click.echo("Ingestion completed.")


@cli.command()
@click.argument('question', required=False)
@click.option("--repo", "-rp", default=".", help="Path to the repository to initialize Docstra in.")
@click.option('--with-sources', "-ws", is_flag=True, help="Include sources in the response.")
@click.option("--raw-output", "-ro", is_flag=True, help="Output raw JSON response.")
def query(question, repo, with_sources, raw_output):
    """Query the repository for answers."""

    repo = Path(repo).resolve()
    docstra = Docstra(repo)

    if not question:
        question = click.prompt(click.style('Enter your query', bold=True, fg="bright_yellow"), type=str)

    result = docstra.query_repository(question)

    if raw_output:
        click.echo(result)
        return

    if with_sources:
        if "answer" in result:
            click.secho(result["answer"])

        if len(result["context"]) == 0:
            click.secho("No sources were found.", fg="bright_red")
            return

        click.secho(f"{'-' * 20} Sources {'-' * 20}", fg="bright_white")

        for source in result["context"]:
            source_file = source.metadata["file_path"]
            source_start_line = source.metadata["start_line"]
            source_end_line = source.metadata["end_line"]
            click.secho(f"{source_file}, L{click.style(f"#{source_start_line}", fg="bright_red")}-L{click.style(f"#{source_end_line}", fg="cyan")}", fg="bright_white")
        return

    if "answer" in result:
        click.echo(result["answer"])
        return

@cli.command()
def list_sessions():
    """List all past chat sessions."""
    sessions = chat_db.get_all_sessions()
    if not sessions:
        click.secho("No chat sessions found.", fg="yellow")
        return
    click.secho("Past Chat Sessions:", fg="bright_blue", bold=True)
    for session in sessions:
        click.secho(f"[{session['id']}] {session['session_name']} (Created: {session['created_at']})", fg="white")

@cli.command()
@click.argument("session_id", type=int)
def show_session(session_id):
    """Retrieve and display chat history."""
    history = chat_db.get_session_history(session_id)
    if not history:
        click.secho(f"No history found for session {session_id}.", fg="red")
        return
    click.secho(f"Chat History for Session {session_id}:", fg="bright_blue", bold=True)
    for entry in history:
        click.secho(click.style("User:", fg="yellow") + f" {entry['question']}")
        click.secho(click.style("Docstra:", fg="cyan") + f" {entry['answer']}")
        click.secho("-" * 40)


@cli.command()
@click.option("--repo", "-rp", default=".", help="Path to the repository to initialize Docstra in.")
@click.option('--with-sources', is_flag=True, default=False, help="Include sources in the response.")
def chat(repo, with_sources):
    """Interactive loop for querying with session management."""

    repo = Path(repo).resolve()
    docstra = Docstra(repo)
    chat_db = ChatDB()

    # List available sessions
    sessions = chat_db.list_sessions()

    if sessions:
        click.secho("\nAvailable Chat Sessions:", fg="cyan")
        for session in sessions:
            click.secho(f"ID: {session['id']} | Name: {session['name']} | Created: {session['created_at']}",
                        fg="yellow")

        # Ask user if they want to use an existing session
        use_existing = click.confirm("Do you want to continue an existing session?")
        if use_existing:
            session_name = click.prompt("Enter the session name")
            session_id = chat_db.get_session_id_by_name(session_name)
            if session_id is None:
                click.secho("Session not found. Starting a new session.", fg="red")
                session_name = click.prompt("Enter a new session name")
                session_id, session_name = chat_db.create_session(session_name)
        else:
            session_name = click.prompt("Enter a new session name")
            session_id, session_name = chat_db.create_session(session_name)
    else:
        # No previous sessions found, create a new one
        click.secho("No saved sessions found. Creating a new session.", fg="yellow")
        session_name = click.prompt("Enter a new session name")
        session_id, session_name = chat_db.create_session(session_name)

    click.secho(f"\nChat session started: {session_name} (ID: {session_id})", fg="green")

    # Start the interactive chat loop
    while True:
        question = click.prompt(click.style("Enter your query (or type 'exit' to quit)", bold=True, fg="bright_yellow"))

        if question.lower() == 'exit':
            break

        result = docstra.query_repository(question)
        if "answer" in result:
            click.secho(result["answer"])

            # Save message to session
            chat_db.save_message(session_id, question, result["answer"])

@cli.command()
@click.option("--port", "-p", default=8000, help="Port to run the FastAPI server on.")
@click.option("--host", "-h", default="127.0.0.1", help="Host to run the FastAPI server on.")
def server(port, host):
    """Start a FastAPI server for querying repositories."""
    from docstra.server import run_server
    run_server(port=port, host=host)


def main():
    cli()


if __name__ == "__main__":
    main()
