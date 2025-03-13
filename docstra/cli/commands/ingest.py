"""Ingest command for Docstra CLI."""

from pathlib import Path
from typing import Optional, List, Set, Union
import fnmatch
import os

import click
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from docstra.cli.base import BaseCommand
from docstra.core.loader import DocstraLoader


class IngestCommand(BaseCommand):
    """Ingest files into the Docstra index."""

    def __init__(self, working_dir: Optional[str] = None, **kwargs):
        """Initialize the command.

        Args:
            working_dir: Working directory path.
            **kwargs: Additional keyword arguments.
        """
        super().__init__(working_dir, **kwargs)
        self.console = Console()
        self.debug = False

    def _should_index_file(
        self, file_path: Union[str, Path], debug_mode: bool = False
    ) -> bool:
        """Check if a file should be indexed based on config settings.

        Args:
            file_path: Path to the file
            debug_mode: Whether to show debug output

        Returns:
            bool: True if the file should be indexed
        """
        # Convert string path to Path object
        if isinstance(file_path, str):
            file_path = Path(file_path)

        # Always try to get relative path from working directory
        try:
            rel_path = file_path.relative_to(self.working_dir)
        except ValueError:
            # If file is outside working directory, try to get relative path from parent
            try:
                # Get the common parent directory
                common_parent = Path(
                    os.path.commonpath([str(self.working_dir), str(file_path)])
                )
                rel_path = file_path.relative_to(common_parent)
            except ValueError:
                # If still can't get relative path, use the path as is
                rel_path = file_path

        rel_str = str(rel_path)

        # Check if file matches any excluded patterns
        for pattern in self.service.config.excluded_patterns:
            if fnmatch.fnmatch(rel_str, pattern):
                if debug_mode:
                    self.console.print(
                        f"[dim]Skipping excluded file: {rel_str} (matches pattern {pattern})[/dim]"
                    )
                return False

        # Check if file extension is supported
        if file_path.suffix not in self.service.config.included_extensions:
            if debug_mode:
                self.console.print(
                    f"[dim]Skipping unsupported extension: {rel_str} (extension {file_path.suffix})[/dim]"
                )
            return False

        return True

    def _get_files_to_index(
        self, paths: Optional[List[str]] = None, force: bool = False
    ) -> Set[str]:
        """Get set of files that need to be indexed."""
        files_to_index = set()
        indexed_files = set()

        if self.debug:
            print(f"Already indexed files: {len(indexed_files)}")
            print(f"Searching in paths: {paths}")
            print(f"Working directory: {self.service.working_dir}")
            print(f"Included extensions: {self.service.config.included_extensions}")
            print(f"Excluded patterns: {self.service.config.excluded_patterns}")

        # Create a new loader instance
        loader = DocstraLoader(
            working_dir=self.service.working_dir,
            included_extensions=self.service.config.included_extensions,
            excluded_patterns=self.service.config.excluded_patterns,
            logger=self.service.logger,
        )

        # If no paths provided, use current directory
        if not paths:
            paths = ["."]

        for path in paths:
            if self.debug:
                print(f"Checking path: {path}")

            if not os.path.exists(path):
                if self.debug:
                    print(f"Path does not exist: {path}")
                continue

            if os.path.isfile(path):
                if self._should_index_file(path):
                    files_to_index.add(path)
                    if self.debug:
                        print(f"Found file to index: {path}")
            else:
                if self.debug:
                    print(f"Scanning directory: {path}")
                try:
                    # Temporarily change loader's working directory
                    original_working_dir = loader.working_dir
                    loader.working_dir = os.path.abspath(path)

                    # Collect files from directory
                    found_files = loader.collect_code_files()
                    for file_path in found_files:
                        if self._should_index_file(file_path):
                            files_to_index.add(file_path)
                            if self.debug:
                                print(f"Found file to index: {file_path}")
                finally:
                    # Restore original working directory
                    loader.working_dir = original_working_dir

        if self.debug:
            print(f"Found {len(files_to_index)} files to index")

        return files_to_index

    def execute(
        self,
        paths: Optional[List[str]] = None,
        force: bool = False,
        log_level: Optional[str] = None,
        log_file: Optional[str] = None,
    ) -> None:
        """Execute the ingest command.

        Args:
            paths: List of file or directory paths to ingest. If None, uses current working directory.
            force: Whether to force reindexing.
            log_level: Optional log level override.
            log_file: Optional log file path.
        """
        # Set debug mode based on log level
        self.debug = log_level == "DEBUG"

        # Ensure workspace is initialized
        self.ensure_initialized()

        # Convert working directory to absolute path
        self.working_dir = os.path.abspath(self.working_dir)

        # Convert paths to absolute paths
        if paths is None:
            paths = [self.working_dir]
        else:
            paths = [os.path.abspath(p) for p in paths]

        # Collect all files info for better diagnostics
        all_files = []
        for path in paths:
            abs_path = Path(path)
            if abs_path.is_file():
                all_files.append(abs_path)
            elif abs_path.exists():
                # To prevent excessive scanning on large directories, use a more targeted approach
                # Only look for common file types to keep scan time reasonable
                extensions_to_find = [
                    ".py",
                    ".js",
                    ".ts",
                    ".md",
                    ".txt",
                    ".json",
                    ".yaml",
                    ".yml",
                    ".html",
                    ".css",
                    ".java",
                    ".c",
                    ".cpp",
                    ".h",
                    ".hpp",
                    ".rs",
                    ".go",
                ]

                for ext in extensions_to_find:
                    all_files.extend(list(abs_path.glob(f"**/*{ext}")))

        # Now count the statistics
        total_checked = len(all_files)
        skipped_extensions = 0
        skipped_excluded = 0

        # Filter files for statistics
        for file_path in all_files:
            # Check extension
            if file_path.suffix not in self.service.config.included_extensions:
                skipped_extensions += 1
                continue

            # Check exclusion patterns
            rel_str = str(file_path.relative_to(self.working_dir))
            for pattern in self.service.config.excluded_patterns:
                if fnmatch.fnmatch(rel_str, pattern):
                    skipped_excluded += 1
                    break

        # Get files that need indexing
        # Now that we have statistics, get files that need indexing
        self.console.print(f"Statistics on available files:")
        self.console.print(f"• Total files checked: {total_checked}")
        self.console.print(f"• Files skipped due to extension: {skipped_extensions}")
        self.console.print(
            f"• Files skipped due to exclusion patterns: {skipped_excluded}"
        )
        self.console.print("")

        files_to_index = self._get_files_to_index(paths, force=force)
        total_files = len(files_to_index)

        if total_files == 0:
            # Get total indexed files for the message
            indexed_files = self.service.indexer.get_indexed_files()
            total_indexed = len(indexed_files)

            if total_indexed > 0:
                # Show success message with suggestions
                self.console.print(
                    Panel(
                        f"[green]All files are already indexed![/green]\n\n"
                        f"Total indexed files: {total_indexed}\n\n"
                        f"Statistics:\n"
                        f"• Files checked: {total_checked}\n"
                        f"• Files skipped due to extension: {skipped_extensions}\n"
                        f"• Files skipped due to exclusion patterns: {skipped_excluded}\n\n"
                        "Suggestions:\n"
                        "• Use [yellow]--force[/yellow] to reindex all files\n"
                        "• Add new files to your codebase\n"
                        "• Check [yellow]--working-dir[/yellow] if you're in the wrong directory\n"
                        "• Use [yellow]docstra query[/yellow] to start exploring your codebase",
                        title="No New Files to Index",
                        border_style="green",
                    )
                )
            else:
                # Show error message with suggestions
                self.console.print(
                    Panel(
                        "[red]No files found to index![/red]\n\n"
                        f"Statistics:\n"
                        f"• Files checked: {total_checked}\n"
                        f"• Files skipped due to extension: {skipped_extensions}\n"
                        f"• Files skipped due to exclusion patterns: {skipped_excluded}\n\n"
                        "This could be because:\n"
                        "• No files with supported extensions found\n"
                        "• All files are excluded by patterns\n"
                        "• You're in the wrong directory\n\n"
                        "Supported extensions: "
                        + ", ".join(self.service.config.included_extensions)
                        + "\n\n"
                        "Try adding additional file extensions to include:\n"
                        "```python\n"
                        "# Edit .docstra/config.json to add more extensions\n"
                        "{\n"
                        '  "included_extensions": [".py", ".md", ".txt", ".jsx", /* add your extensions */]\n'
                        "}\n"
                        "```\n\n"
                        "Or run with debug output to see more details:\n"
                        "```\n"
                        "poetry run docstra ingest --log-level=DEBUG\n"
                        "```",
                        title="No Files Found",
                        border_style="red",
                    )
                )
            return

        # Create progress display
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TextColumn("({task.completed}/{task.total})"),
            console=self.console,
        )

        with progress:
            # Add overall progress task
            overall_task = progress.add_task(
                "[bright_yellow]Indexing files...[/bright_yellow]", total=total_files
            )

            # Process each file
            processed_files = 0
            failed_files = []

            for file_path in files_to_index:
                try:
                    # Create task for current file
                    path_desc = f"[cyan]{file_path}[/cyan]"
                    current_task = progress.add_task(
                        f"Processing {path_desc}", total=None
                    )

                    # Index the file
                    try:
                        if self.service.indexer.get_or_index_file(str(file_path)):
                            processed_files += 1
                            progress.update(overall_task, advance=1)
                        else:
                            failed_files.append(
                                (str(file_path), "Failed to index file")
                            )
                    except Exception as e:
                        failed_files.append((str(file_path), str(e)))

                    # Complete current file task
                    progress.update(current_task, completed=True)

                except Exception as e:
                    self.display_error(f"Error processing {file_path}: {str(e)}")
                    failed_files.append((str(file_path), str(e)))

            # Display summary
            if processed_files > 0:
                self.display_success(f"Successfully indexed {processed_files} files")

            if failed_files:
                self.display_error(f"Failed to index {len(failed_files)} files:")
                for file_path, error in failed_files:
                    self.display_error(f"  • {file_path}: {error}")


@click.command("ingest")
@click.argument("paths", nargs=-1, required=False, type=click.Path(exists=True))
@click.option("--force", is_flag=True, help="Force reindexing")
@click.option("--log-level", help="Set log level")
@click.option("--log-file", help="Set log file path")
@click.option(
    "--working-dir", type=click.Path(exists=True), default=".", help="Working directory"
)
def ingest(
    paths: Optional[List[str]] = None,
    force: bool = False,
    log_level: Optional[str] = None,
    log_file: Optional[str] = None,
    working_dir: str = ".",
) -> None:
    """Ingest files into the Docstra index. If no paths are provided, ingests the current working directory."""
    cmd = IngestCommand(working_dir=working_dir)
    # Convert empty tuple to None so execute() will use current directory
    paths_list = list(paths) if paths else None
    cmd.execute(
        paths=paths_list,
        force=force,
        log_level=log_level,
        log_file=log_file,
    )
