"""Main entry point for the Docstra CLI."""

import os
import sys
import click

from docstra.cli.commands import get_all_commands


@click.group()
@click.version_option(package_name="docstra")
@click.pass_context
def cli(ctx):
    """Docstra CLI - AI-powered code assistant.
    
    Analyze, understand, and work with codebases more efficiently.
    """
    ctx.ensure_object(dict)


# Register all commands
for command in get_all_commands():
    cli.add_command(command)


def main():
    """Main entry point for the Docstra CLI."""
    try:
        cli()
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()