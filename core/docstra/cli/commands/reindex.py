"""Reindex command for the Docstra CLI."""

import click
from pathlib import Path

from docstra.service import DocstraService
from docstra.config import DocstraConfig
from docstra.cli.base import DocstraCommand
from docstra.cli.utils import create_spinner


class ReindexCommand(DocstraCommand):
    """Command to reindex the codebase."""
    
    def execute(
        self,
        log_level: str = None,
        log_file: str = None,
        force: bool = False,
    ):
        """Execute the reindex command.
        
        Args:
            log_level: Log level to use
            log_file: Log file path
            force: Force reindexing of all files
        """
        self.console.print(f"Re-indexing codebase in [bold]{self.working_dir}[/bold]")

        try:
            # Load config
            config_path = Path(self.working_dir) / ".docstra" / "config.json"
            config = DocstraConfig.from_file(str(config_path))

            # Override log settings if provided
            if log_level:
                config.log_level = log_level
            if log_file:
                config.log_file = log_file

            # Initialize service
            service = self.initialize_service(str(config_path))

            # Show activity during indexing
            with create_spinner("Indexing codebase...") as progress:
                task = progress.add_task("Indexing", total=None)

                # Force reindexing
                service.update_index(force=force)

            self.display_success(
                "✅ Codebase re-indexed successfully!",
                title="Success",
            )
        except Exception as e:
            self.display_error(
                f"Error re-indexing codebase: {str(e)}",
                title="Error",
            )


@click.command("reindex")
@click.argument("dir_path", default=".", type=click.Path(exists=True))
@click.option("--log-level", help="Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)")
@click.option("--log-file", help="Path to log file")
@click.option("--force", is_flag=True, help="Force reindexing of all files")
def reindex(dir_path, log_level, log_file, force):
    """Reindex the codebase in the specified directory."""
    command = ReindexCommand(working_dir=dir_path)
    command.execute(log_level=log_level, log_file=log_file, force=force)