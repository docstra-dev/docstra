"""Ingest endpoints for Docstra API."""

from typing import Dict, List, Optional
import asyncio
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel

from docstra.core import IIndexer
from docstra.api.dependencies import get_indexer, handle_exceptions
from docstra.api.models import IngestRequest, IngestResponse

# Dictionary to store background tasks
ingest_tasks = {}

router = APIRouter(prefix="/ingest", tags=["ingest"])


class IngestTaskStatus(BaseModel):
    """Status model for ingest tasks."""

    status: str
    progress: int
    error: Optional[str] = None


class IngestTaskResponse(BaseModel):
    """Response model for ingest task status endpoint."""

    task_id: str
    status: str
    progress: int
    error: Optional[str] = None


async def ingest_codebase(
    task_id: str,
    indexer: IIndexer,
    force: bool = False,
    lazy: bool = False,
    specific_files: Optional[List[str]] = None,
):
    """Background task to ingest the codebase.

    Args:
        task_id: Task ID for tracking
        indexer: Indexer service
        force: Whether to force reingestion
        lazy: Whether to use lazy indexing
        specific_files: List of specific files to ingest
    """
    try:
        # Update task status
        ingest_tasks[task_id] = IngestTaskStatus(status="running", progress=0)

        # Configure indexer
        indexer.config.lazy_indexing = lazy

        if specific_files:
            # Ingest specific files
            total_files = len(specific_files)
            for i, file_path in enumerate(specific_files):
                indexer.get_or_index_file(file_path)
                ingest_tasks[task_id].progress = int((i + 1) / total_files * 100)
        else:
            # Ingest entire codebase
            indexer.update_index(force=force)
            ingest_tasks[task_id].progress = 100

        # Update task status
        ingest_tasks[task_id].status = "completed"
    except Exception as e:
        # Update task status on error
        ingest_tasks[task_id] = IngestTaskStatus(
            status="failed", progress=0, error=str(e)
        )


@router.post("", response_model=IngestResponse)
@handle_exceptions(status_code=500, error_message="Error during ingestion")
async def ingest_endpoint(
    request: IngestRequest,
    background_tasks: BackgroundTasks,
    indexer: IIndexer = Depends(get_indexer),
) -> IngestResponse:
    """Ingest files into the codebase index.

    Args:
        request: The ingest request.
        background_tasks: FastAPI background tasks
        indexer: The indexer service.

    Returns:
        The ingest response.
    """
    # Generate task ID
    task_id = f"ingest_{uuid4()}"

    # Initialize task status
    ingest_tasks[task_id] = IngestTaskStatus(status="pending", progress=0)

    # Start background task
    background_tasks.add_task(
        ingest_codebase,
        task_id=task_id,
        indexer=indexer,
        force=request.force,
        lazy=request.lazy,
    )

    return IngestResponse(success=True)


@router.get("/tasks/{task_id}", response_model=IngestTaskResponse)
@handle_exceptions(status_code=404, error_message="Task not found")
async def get_task_status(task_id: str) -> IngestTaskResponse:
    """Get the status of an ingest task.

    Args:
        task_id: The ID of the task to check.

    Returns:
        The task status.
    """
    if task_id not in ingest_tasks:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    task_status = ingest_tasks[task_id]
    return IngestTaskResponse(
        task_id=task_id,
        status=task_status.status,
        progress=task_status.progress,
        error=task_status.error,
    )