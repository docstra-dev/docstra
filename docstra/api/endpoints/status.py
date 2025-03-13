"""Status endpoints for Docstra API."""

import os
from typing import Dict, List, Optional
import importlib.metadata
import requests
from packaging import version

from fastapi import APIRouter, Depends

from docstra.core import IIndexer, ILoader
from docstra.api.dependencies import get_indexer, get_container, handle_exceptions
from docstra.api.models import StatusResponse, VersionCheckResponse
from docstra.api.endpoints.ingest import ingest_tasks, IngestTaskStatus

router = APIRouter(prefix="/status", tags=["status"])


class TaskStatus(IngestTaskStatus):
    """Model for task status."""

    pass


class IndexedFilesResponse(StatusResponse):
    """Response model for indexed files endpoint."""

    files: List[str]


@router.get("", response_model=StatusResponse)
@handle_exceptions(status_code=500, error_message="Error getting status")
async def status_endpoint(
    indexer: IIndexer = Depends(get_indexer),
) -> StatusResponse:
    """Get the status of the Docstra API.

    Args:
        indexer: The indexer service.

    Returns:
        The status response.
    """
    try:
        # Get version from package if available
        try:
            version = importlib.metadata.version("docstra")
        except (ImportError, importlib.metadata.PackageNotFoundError):
            version = "unknown"

        # Get indexed files count
        indexed_files = len(indexer.get_indexed_files())

        return StatusResponse(
            status="ok",
            version=version,
            working_directory=os.getcwd(),
            indexed_files=indexed_files,
        )
    except Exception as e:
        return StatusResponse(
            status="error",
            version="unknown",
            working_directory=os.getcwd(),
            indexed_files=0,
        )


@router.get("/indexed-files", response_model=IndexedFilesResponse)
@handle_exceptions(status_code=500, error_message="Error getting indexed files")
async def get_indexed_files(
    indexer: IIndexer = Depends(get_indexer),
) -> IndexedFilesResponse:
    """Get the list of indexed files.

    Args:
        indexer: The indexer service.

    Returns:
        Response containing the list of indexed files
    """
    indexed_files = indexer.get_indexed_files()

    try:
        version = importlib.metadata.version("docstra")
    except (ImportError, importlib.metadata.PackageNotFoundError):
        version = "unknown"

    return IndexedFilesResponse(
        status="ok",
        version=version,
        working_directory=os.getcwd(),
        indexed_files=len(indexed_files),
        files=indexed_files,
    )


@router.get("/tasks", response_model=Dict[str, TaskStatus])
@handle_exceptions(status_code=500, error_message="Error getting tasks")
async def get_tasks() -> Dict[str, TaskStatus]:
    """Get the status of all tasks.

    Returns:
        Dictionary of task statuses
    """
    return ingest_tasks


@router.get("/version-check", response_model=VersionCheckResponse)
@handle_exceptions(status_code=500, error_message="Error checking version")
async def check_version() -> VersionCheckResponse:
    """Check if the current version is up to date.

    Returns:
        Version check response containing current and latest version information
    """
    try:
        # Get current version
        current_version = importlib.metadata.version("docstra")

        # Get latest version from PyPI
        response = requests.get("https://pypi.org/pypi/docstra/json")
        if response.status_code == 200:
            latest_version = response.json()["info"]["version"]
            needs_update = version.parse(current_version) < version.parse(
                latest_version
            )
        else:
            latest_version = current_version
            needs_update = False

        return VersionCheckResponse(
            current_version=current_version,
            latest_version=latest_version,
            needs_update=needs_update,
        )
    except Exception as e:
        # If we can't get version info, assume we're up to date
        try:
            current_version = importlib.metadata.version("docstra")
        except (ImportError, importlib.metadata.PackageNotFoundError):
            current_version = "unknown"

        return VersionCheckResponse(
            current_version=current_version,
            latest_version=current_version,
            needs_update=False,
        )
