"""File ingestion command for Docstra CLI."""

import click
from pathlib import Path

from docstra.config import DocstraConfig
from docstra.cli.base import DocstraCommand
from docstra.cli.utils import create_spinner
from docstra.loader import DocstraLoader


class IngestCommand(DocstraCommand):
    """Command to ingest the entire codebase into the index."""

    def execute(
        self,
        log_level: str = None,
        log_file: str = None,
        force: bool = False,
    ):
        """Execute the ingest command.

        Args:
            log_level: Log level to use
            log_file: Log file path
            force: Force reingestion even if file is already indexed
        """
        self.console.print(f"Ingesting codebase in [bold]{self.working_dir}[/bold]")

        try:
            # Load config
            config = DocstraConfig.load(self.working_dir)

            # Override log settings if provided
            if log_level:
                config.log_level = log_level
            if log_file:
                config.log_file = log_file

            # Initialize service
            service = self.initialize_service()

            # Create a loader with the config settings
            loader = DocstraLoader(
                working_dir=Path(self.working_dir),
                included_extensions=config.included_extensions,
                excluded_patterns=config.excluded_patterns,
                chunk_size=config.chunk_size,
                chunk_overlap=config.chunk_overlap,
                logger=service.logger,
            )

            # Collect files based on config patterns
            self.console.print("Collecting files based on configuration...")
            files_to_ingest = loader.collect_code_files()

            if not files_to_ingest:
                self.display_error("No files found matching the configured patterns.")
                return

            self.console.print(
                f"Found [bold]{len(files_to_ingest)}[/bold] files to ingest."
            )

            # Show activity during indexing
            with create_spinner("Ingesting files...") as progress:
                task = progress.add_task("Ingesting", total=len(files_to_ingest))

                # Process the files
                service.indexer._process_files_for_indexing(
                    files_to_ingest, force=force
                )
                progress.update(task, advance=len(files_to_ingest))

            self.display_success(
                f"✅ Successfully ingested {len(files_to_ingest)} files!",
                title="Success",
            )
        except Exception as e:
            import traceback

            error_details = traceback.format_exc()
            self.display_error(
                f"Error ingesting files: {str(e)}\n\nDetails:\n{error_details}",
                title="Error",
            )


@click.command("ingest")
@click.argument("dir_path", type=click.Path(exists=True), default=".")
@click.option("--log-level", help="Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)")
@click.option("--log-file", help="Path to log file")
@click.option("--force", is_flag=True, help="Force reingestion even if already indexed")
def ingest(dir_path, log_level, log_file, force):
    """Ingest all files in the codebase based on configuration.

    Uses the include patterns and exclude patterns from the configuration.
    """
    command = IngestCommand(working_dir=dir_path)
    command.execute(
        log_level=log_level,
        log_file=log_file,
        force=force,
    )
