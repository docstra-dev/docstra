"""File ingestion command for Docstra CLI."""

import os
import click
from pathlib import Path

from docstra.service import DocstraService
from docstra.config import DocstraConfig
from docstra.cli.base import DocstraCommand
from docstra.cli.utils import create_spinner, resolve_relative_path


class IngestCommand(DocstraCommand):
    """Command to ingest specific files into the index."""
    
    def execute(
        self,
        file_paths: list = None,
        pattern: str = None,
        log_level: str = None,
        log_file: str = None,
        force: bool = False,
    ):
        """Execute the ingest command.
        
        Args:
            file_paths: List of file paths to ingest
            pattern: Glob pattern to match files
            log_level: Log level to use
            log_file: Log file path
            force: Force reingestion even if file is already indexed
        """
        self.console.print(f"Ingesting files in [bold]{self.working_dir}[/bold]")

        if not file_paths and not pattern:
            self.display_error("No files or pattern specified.")
            return

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
            
            # Resolve file paths to ingest
            files_to_ingest = []
            
            # Add specific files
            if file_paths:
                for file_path in file_paths:
                    abs_path = resolve_relative_path(str(self.working_dir), file_path)
                    if os.path.exists(abs_path):
                        files_to_ingest.append(Path(abs_path))
                    else:
                        self.console.print(f"[yellow]Warning: File not found: {file_path}[/yellow]")
            
            # Add files matching pattern
            if pattern:
                glob_files = list(Path(self.working_dir).glob(pattern))
                if not glob_files:
                    self.console.print(f"[yellow]Warning: No files match pattern: {pattern}[/yellow]")
                else:
                    files_to_ingest.extend(glob_files)
            
            if not files_to_ingest:
                self.display_error("No valid files to ingest.")
                return
                
            # Show activity during indexing
            with create_spinner("Ingesting files...") as progress:
                task = progress.add_task("Ingesting", total=len(files_to_ingest))
                
                # Process the files
                service._process_files_for_indexing(files_to_ingest)
                progress.update(task, advance=len(files_to_ingest))

            self.display_success(
                f"✅ Successfully ingested {len(files_to_ingest)} files!",
                title="Success",
            )
        except Exception as e:
            self.display_error(
                f"Error ingesting files: {str(e)}",
                title="Error",
            )


@click.command("ingest")
@click.argument("dir_path", type=click.Path(exists=True))
@click.option("--file", "-f", "file_paths", multiple=True, help="File path to ingest (can be used multiple times)")
@click.option("--pattern", "-p", help="Glob pattern to match files (e.g. '**/*.py')")
@click.option("--log-level", help="Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)")
@click.option("--log-file", help="Path to log file")
@click.option("--force", is_flag=True, help="Force reingestion even if already indexed")
def ingest(dir_path, file_paths, pattern, log_level, log_file, force):
    """Ingest specific files into the index.
    
    Either specify files directly with --file/-f (can be used multiple times)
    or use --pattern/-p with a glob pattern.
    """
    command = IngestCommand(working_dir=dir_path)
    command.execute(
        file_paths=file_paths, 
        pattern=pattern, 
        log_level=log_level, 
        log_file=log_file,
        force=force,
    )