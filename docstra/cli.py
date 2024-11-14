import json
import os
from pathlib import Path

import click
from docstra.main import Docstra
from docstra.logger import logger
import logging

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
        click.secho(header_art, fg=202)
        click.secho("Welcome to the Docstra CLI!", fg=202, bold=True)
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

    click.secho(header_art, fg=202)

    if not docstra_dir.exists():
        docstra_dir.mkdir(parents=True)
        click.secho(f"Created .docstra directory in repository at {repo}", fg="green")
    else:
        click.echo(f".docstra directory already exists in repository at {repo}")

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

        click.secho(f"Repository-specific configuration created at {repo_config_path}", fg="green")
    else:
        click.echo(f"Repository-specific configuration already exists at {repo_config_path}")

    click.secho("Docstra repository initialization complete.", fg=202)
    click.secho("Docstra needs an OpenAI API key to function. It will be stored in `.docstra/.env`.", fg=202)

    if not api_key and os.environ.get("OPENAI_API_KEY") is None:
        api_key = click.prompt(click.style("Enter your OpenAI API key: ", bold=True), type=str)

    env_path = docstra_dir / ".env"
    with open(env_path, "a") as f:
        f.write(f"OPENAI_API_KEY={api_key}\n")

    click.secho("OpenAI API key saved successfully.", fg="green")

    click.secho("Docstra initialization complete.", fg=202)
    click.secho("You can now start ingesting the repository using `docstra ingest`.", fg=202)



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
        question = click.prompt(click.style('Enter your query', bold=True, fg=202), type=str)

    result = docstra.query_repository(question)

    if raw_output:
        click.echo(result)
        return

    if with_sources:
        if "answer" in result:
            click.secho(result["answer"], fg=154, bold=True)

        if len(result["context"]) == 0:
            click.secho("No sources were found.", fg="red")
            return

        click.secho(f"{'-'*20} Sources {'-'*20}", fg=255)

        for source in result["context"]:
            click.secho(f"Source: {source}", fg=255)
        return

    if "answer" in result:
        click.echo(result["answer"])
        return


@cli.command()
@click.option("--repo", "-rp", default=".", help="Path to the repository to initialize Docstra in.")
@click.option('--with-sources', is_flag=True, default=False, help="Include sources in the response.")
def chat(repo, with_sources):
    """Interactive loop for ingesting repositories and querying."""

    repo = Path(repo).resolve()
    docstra = Docstra(repo)

    while True:
        question = click.prompt(click.style("Enter your query (or type 'exit' to quit)", bold=True, fg=202))
        if question.lower() == 'exit':
            break
        result = docstra.query_repository(question)
        formatted_output = result if with_sources else result["answer"]
        click.secho(formatted_output, fg=154, bold=True)

if __name__ == "__main__":
    cli()
