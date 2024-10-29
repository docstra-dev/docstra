from pathlib import Path

import click
from docstra.main import Docstra
from docstra.logger import logger
import logging

@click.group(invoke_without_command=True)
@click.option('--verbose', is_flag=True, help="Enable all logging.")
@click.option('--with-sources', is_flag=True, help="Include sources in the response.")
@click.pass_context
def cli(ctx, verbose, with_sources=False):
    if ctx.invoked_subcommand is None:

        if verbose:
            logger.setLevel(logging.INFO)
        else:
            logger.setLevel(logging.WARNING)

        click.echo("Welcome to the Docstra CLI. You can start ingesting a repository or ask queries.")
        interactive_mode(with_sources)

@click.command()
@click.argument('repo_path')
@click.option('--db-dir', default="./db", help="Directory to store the vector database.")
def ingest(repo_path, db_dir):
    """Ingest a repository to extract metadata and store embeddings."""
    docstra = Docstra(Path(repo_path), db_dir=db_dir)
    click.echo(f"Starting ingestion for repository: {repo_path}")
    docstra.ingest_repository()
    click.echo("Ingestion completed.")

@click.command()
@click.argument('question', required=False)
@click.option('--with-sources', is_flag=True, help="Include sources in the response.")
@click.option('--repo-path', required=True, help="The path to the repository for querying.")
@click.option('--db-dir', default="./db", help="Directory where the vector database is stored.")
def query(question, with_sources, repo_path, db_dir):
    """Query the repository for answers."""
    docstra = Docstra(repo_path, db_dir=db_dir)
    if not question:
        question = click.prompt('Enter your query')
    click.echo(f"Querying repository: {question}")
    result = docstra.query_repository(question)
    if with_sources:
        click.echo("Query result with sources:")
    click.echo(result)

def interactive_mode(with_sources=False):
    """Interactive loop for ingesting repositories and querying."""
    repo_path = click.prompt('Enter the repository path for ingestion', default=Path.cwd())
    db_dir = click.prompt('Enter the vectorstore directory (or press Enter for default ./db)', default='./db')
    docstra = Docstra(repo_path, db_dir=db_dir)

    click.echo(f"Starting ingestion for repository: {repo_path}")
    docstra.ingest_repository()
    click.echo("Ingestion completed.")

    while True:
        question = click.prompt("Enter your query (or type 'exit' to quit)")
        if question.lower() == 'exit':
            break
        result = docstra.query_repository(question)
        formatted_output = result if with_sources else result["answer"]
        click.echo(formatted_output)

cli.add_command(ingest)
cli.add_command(query)

if __name__ == "__main__":
    cli()
