"""Serve command for Docstra CLI."""

from typing import Optional

import click
import uvicorn

from docstra.cli.base import BaseCommand


class ServeCommand(BaseCommand):
    """Serve the Docstra API."""

    def execute(
        self,
        host: str = "127.0.0.1",
        port: int = 8000,
        reload: bool = False,
        log_level: Optional[str] = None,
        log_file: Optional[str] = None,
    ) -> None:
        """Execute the serve command.

        Args:
            host: The host to bind to.
            port: The port to bind to.
            reload: Whether to enable auto-reload.
            log_level: Optional log level override.
            log_file: Optional log file path.
        """
        # Ensure workspace is initialized
        self.ensure_initialized()

        # Display startup message
        self.display_success(f"Starting Docstra API server on http://{host}:{port}")

        # Run the server
        uvicorn.run(
            "docstra.api.app:app",
            host=host,
            port=port,
            reload=reload,
            log_level=log_level.lower() if log_level else "info",
        )


@click.command("serve")
@click.option("--host", default="127.0.0.1", help="Host to bind to")
@click.option("--port", default=8000, help="Port to bind to")
@click.option("--reload", is_flag=True, help="Enable auto-reload")
@click.option("--log-level", help="Set log level")
@click.option("--log-file", help="Set log file path")
@click.option(
    "--working-dir", type=click.Path(exists=True), default=".", help="Working directory"
)
def serve(
    host: str = "127.0.0.1",
    port: int = 8000,
    reload: bool = False,
    log_level: Optional[str] = None,
    log_file: Optional[str] = None,
    working_dir: str = ".",
) -> None:
    """Serve the Docstra API."""
    cmd = ServeCommand(working_dir=working_dir)
    cmd.execute(
        host=host,
        port=port,
        reload=reload,
        log_level=log_level,
        log_file=log_file,
    )
