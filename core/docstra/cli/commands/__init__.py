"""Command implementations for the Docstra CLI."""

from docstra.cli.commands.init import init
from docstra.cli.commands.chat import chat
from docstra.cli.commands.query import query
from docstra.cli.commands.reindex import reindex
from docstra.cli.commands.serve import serve
from docstra.cli.commands.ingest import ingest

# Export all commands
__all__ = ["init", "chat", "query", "reindex", "serve", "ingest"]

def get_all_commands():
    """Get all available CLI commands.
    
    Returns:
        List of command functions
    """
    return [init, chat, query, reindex, serve, ingest]