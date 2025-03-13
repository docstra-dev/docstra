"""Documentation management commands for Docstra CLI."""

from pathlib import Path
from typing import Optional, List

import click
from rich.table import Table

from docstra.cli.base import BaseCommand


class DocsCommand(BaseCommand):
    """Manage documentation for your codebase."""

    def execute(
        self,
        action: str,
        paths: Optional[List[str]] = None,
        output_dir: str = "docs",
        format: str = "markdown",
        force: bool = False,
        log_level: Optional[str] = None,
        log_file: Optional[str] = None,
    ) -> None:
        """Execute the docs command.

        Args:
            action: The action to perform (generate, list, update).
            paths: Optional list of file or directory paths to operate on.
            output_dir: Directory to output generated docs to.
            format: Output format (markdown or html).
            force: Whether to force regeneration.
            log_level: Optional log level override.
            log_file: Optional log file path.
        """
        # Ensure workspace is initialized
        self.ensure_initialized()

        # Handle different actions
        if action == "generate":
            if not paths:
                self.display_error("At least one path is required for generate action")
                return
            self._generate_docs(paths, output_dir, format, force)
        elif action == "list":
            self._list_docs(output_dir)
        elif action == "update":
            self._update_docs(output_dir, format, force)
        else:
            self.display_error(f"Unknown action: {action}")

    def _generate_docs(
        self,
        paths: List[str],
        output_dir: str,
        format: str,
        force: bool,
    ) -> None:
        """Generate documentation for specified paths.

        Args:
            paths: List of file or directory paths to generate docs for.
            output_dir: Directory to output generated docs to.
            format: Output format (markdown or html).
            force: Whether to force regeneration.
        """
        # Create output directory if it doesn't exist
        output_path = Path(self.working_dir) / output_dir
        output_path.mkdir(parents=True, exist_ok=True)

        # Process each path
        for path in paths:
            try:
                # Convert to absolute path
                abs_path = Path(self.working_dir) / path
                if not abs_path.exists():
                    self.display_error(f"Path does not exist: {path}")
                    continue

                # Display progress
                self.display_success(f"Generating documentation for {path}...")

                # Generate documentation
                if abs_path.is_file():
                    self.service.generate_file_docs(
                        str(abs_path), str(output_path), format=format, force=force
                    )
                else:
                    self.service.generate_directory_docs(
                        str(abs_path), str(output_path), format=format, force=force
                    )

            except Exception as e:
                self.display_error(f"Error generating docs for {path}: {str(e)}")

    def _list_docs(self, output_dir: str) -> None:
        """List all generated documentation files.

        Args:
            output_dir: Directory containing generated docs.
        """
        output_path = Path(self.working_dir) / output_dir
        if not output_path.exists():
            self.display_error(f"Documentation directory does not exist: {output_dir}")
            return

        table = Table(title="Generated Documentation")
        table.add_column("File", style="cyan")
        table.add_column("Type", style="magenta")
        table.add_column("Last Modified", style="green")
        table.add_column("Size", style="yellow")

        for file in output_path.rglob("*"):
            if file.is_file():
                table.add_row(
                    str(file.relative_to(output_path)),
                    file.suffix[1:] if file.suffix else "-",
                    file.stat().st_mtime,
                    f"{file.stat().st_size / 1024:.1f}KB",
                )

        self.console.print(table)

    def _update_docs(self, output_dir: str, format: str, force: bool) -> None:
        """Update all generated documentation.

        Args:
            output_dir: Directory containing generated docs.
            format: Output format (markdown or html).
            force: Whether to force regeneration.
        """
        try:
            self.display_success("Updating documentation...")
            self.service.update_all_docs(
                output_dir=output_dir, format=format, force=force
            )
            self.display_success("Documentation updated successfully")
        except Exception as e:
            self.display_error(f"Error updating documentation: {str(e)}")


@click.group("docs")
@click.option("--log-level", help="Set log level")
@click.option("--log-file", help="Set log file path")
@click.option(
    "--working-dir", type=click.Path(exists=True), default=".", help="Working directory"
)
def docs(
    log_level: Optional[str] = None,
    log_file: Optional[str] = None,
    working_dir: str = ".",
) -> None:
    """Manage documentation for your codebase."""
    pass


@docs.command("generate")
@click.argument("paths", nargs=-1, required=True, type=click.Path(exists=True))
@click.option(
    "--output-dir", default="docs", help="Output directory for generated docs"
)
@click.option(
    "--format",
    type=click.Choice(["markdown", "html"]),
    default="markdown",
    help="Output format",
)
@click.option("--force", is_flag=True, help="Force regeneration")
@click.pass_context
def generate_docs(ctx, paths: List[str], output_dir: str, format: str, force: bool):
    """Generate documentation for specified paths."""
    cmd = DocsCommand(working_dir=ctx.parent.params["working_dir"])
    cmd.execute(
        action="generate",
        paths=paths,
        output_dir=output_dir,
        format=format,
        force=force,
        log_level=ctx.parent.params.get("log_level"),
        log_file=ctx.parent.params.get("log_file"),
    )


@docs.command("list")
@click.option(
    "--output-dir", default="docs", help="Directory containing generated docs"
)
@click.pass_context
def list_docs(ctx, output_dir: str):
    """List all generated documentation files."""
    cmd = DocsCommand(working_dir=ctx.parent.params["working_dir"])
    cmd.execute(
        action="list",
        output_dir=output_dir,
        log_level=ctx.parent.params.get("log_level"),
        log_file=ctx.parent.params.get("log_file"),
    )


@docs.command("update")
@click.option(
    "--output-dir", default="docs", help="Directory containing generated docs"
)
@click.option(
    "--format",
    type=click.Choice(["markdown", "html"]),
    default="markdown",
    help="Output format",
)
@click.option("--force", is_flag=True, help="Force regeneration")
@click.pass_context
def update_docs(ctx, output_dir: str, format: str, force: bool):
    """Update all generated documentation."""
    cmd = DocsCommand(working_dir=ctx.parent.params["working_dir"])
    cmd.execute(
        action="update",
        output_dir=output_dir,
        format=format,
        force=force,
        log_level=ctx.parent.params.get("log_level"),
        log_file=ctx.parent.params.get("log_file"),
    )
