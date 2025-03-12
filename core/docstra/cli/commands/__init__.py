"""Command implementations for the Docstra CLI."""

from docstra.cli.commands.init import init
from docstra.cli.commands.chat import chat
from docstra.cli.commands.query import query
from docstra.cli.commands.serve import serve
from docstra.cli.commands.ingest import ingest
from docstra.cli.commands.docs import docs_generate

# Export all commands
__all__ = ["init", "chat", "query", "serve", "ingest", "docs_generate"]


def get_all_commands():
    """Get all available CLI commands.

    Returns:
        List of command functions
    """
    return [init, chat, query, serve, ingest, docs_generate]
