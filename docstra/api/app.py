"""FastAPI application for Docstra."""

import os
import logging
from typing import Optional

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from docstra.api.endpoints import ingest, query, sessions, status


def create_app(
    working_dir: Optional[str] = None,
    config_path: Optional[str] = None,
    log_level: str = "INFO",
) -> FastAPI:
    """Create and configure the FastAPI application.

    Args:
        working_dir: Working directory for Docstra
        config_path: Path to configuration file
        log_level: Logging level to use

    Returns:
        Configured FastAPI application
    """
    # Configure logging
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Create FastAPI app
    app = FastAPI(title="Docstra API", description="API for Docstra codebase assistant")

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # TODO: Make configurable
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Store configuration in app state
    app.state.working_dir = working_dir
    app.state.config_path = config_path

    # Add error handler
    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        """Handle exceptions and return appropriate HTTP responses."""
        if isinstance(exc, HTTPException):
            return {"error": exc.detail}
        return {"error": str(exc)}

    # Include routers from endpoint modules
    app.include_router(ingest.router)
    app.include_router(query.router)
    app.include_router(sessions.router)
    app.include_router(status.router)

    return app


# Create the default app instance for uvicorn
app = create_app()


def start_server(
    host: str = "127.0.0.1",
    port: int = 8000,
    working_dir: Optional[str] = None,
    config_path: Optional[str] = None,
    log_level: str = "INFO",
    log_file: Optional[str] = None,
) -> None:
    """Start the Docstra API server.

    Args:
        host: Host to bind to
        port: Port to bind to
        working_dir: Working directory for Docstra
        config_path: Path to configuration file
        log_level: Logging level to use
        log_file: Path to log file
    """
    # Create the FastAPI app
    app = create_app(
        working_dir=working_dir,
        config_path=config_path,
        log_level=log_level,
    )

    # Configure uvicorn logging
    log_config = uvicorn.config.LOGGING_CONFIG
    if log_file:
        for handler in log_config["handlers"].values():
            handler["filename"] = log_file

    # Start the server
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level=log_level.lower(),
        log_config=log_config if log_file else None,
    )
