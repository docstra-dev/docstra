"""API server command for Docstra CLI."""

import click
from pathlib import Path

from docstra.service import DocstraService
from docstra.config import DocstraConfig
from docstra.cli.base import DocstraCommand
from docstra.api import start_server


class ServeCommand(DocstraCommand):
    """Command to start the Docstra API server."""

    def execute(
        self,
        host: str = "127.0.0.1",
        port: int = 8000,
        log_level: str = None,
        log_file: str = None,
    ):
        """Execute the serve command.

        Args:
            host: Host to bind to
            port: Port to bind to
            log_level: Log level to use
            log_file: Log file path
        """
        self.console.print(
            f"Starting Docstra API server on [bold]{host}:{port}[/bold]\n"
            f"Working directory: [bold]{self.working_dir}[/bold]"
        )

        try:
            # Start server
            start_server(
                host=host,
                port=port,
                working_dir=str(self.working_dir),
                log_level=log_level or "INFO",
                log_file=log_file,
            )
        except Exception as e:
            self.display_error(
                f"Error starting API server: {str(e)}",
                title="Error",
            )


@click.command("serve")
@click.option(
    "--dir", default=".", type=click.Path(exists=True), help="Directory to serve"
)
@click.option("--host", default="127.0.0.1", help="Host to bind to")
@click.option("--port", default=8000, type=int, help="Port to bind to")
@click.option("--log-level", help="Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)")
@click.option("--log-file", help="Path to log file")
def serve(dir, host, port, log_level, log_file):
    """Start the Docstra API server in the specified directory."""
    command = ServeCommand(working_dir=dir)
    command.execute(host=host, port=port, log_level=log_level, log_file=log_file)
