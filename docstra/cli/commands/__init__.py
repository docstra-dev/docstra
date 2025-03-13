"""Command implementations for the Docstra CLI."""

from docstra.cli.commands.init import init
from docstra.cli.commands.chat import chat
from docstra.cli.commands.query import query
from docstra.cli.commands.serve import serve
from docstra.cli.commands.ingest import ingest
from docstra.cli.commands.docs import docs
from docstra.cli.commands.sessions import sessions


def get_all_commands():
    """Get all available CLI commands.

    Returns:
        list: List of command functions.
    """
    return [init, chat, query, serve, ingest, docs, sessions]
