"""Main entry point for the Docstra CLI."""

import os
import sys
from pathlib import Path

import click
from rich.console import Console

from docstra.cli.commands import get_all_commands
from docstra.cli.ui import display_header, display_command_result

console = Console()


@click.group()
def cli():
    """Docstra CLI - Your AI-powered documentation assistant."""
    # Display the header when CLI starts
    display_header()


def main():
    """Main entry point for the CLI."""
    try:
        # Register all commands
        for cmd in get_all_commands():
            cli.add_command(cmd)

        # Run the CLI
        cli()
    except click.ClickException as e:
        display_command_result(str(e), success=False)
        sys.exit(1)
    except Exception as e:
        display_command_result(f"An unexpected error occurred: {str(e)}", success=False)
        if "--debug" in sys.argv:
            console.print_exception()
        sys.exit(1)


if __name__ == "__main__":
    main()
