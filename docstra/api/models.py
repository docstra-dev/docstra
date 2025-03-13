"""API request and response models."""

from typing import List, Optional
from pydantic import BaseModel


# Ingest Endpoint Models
class IngestRequest(BaseModel):
    """Request model for ingest endpoint."""

    force: bool = False
    lazy: bool = False


class IngestResponse(BaseModel):
    """Response model for ingest endpoint."""

    success: bool


# Query Endpoint Models
class QueryRequest(BaseModel):
    """Request model for query endpoint."""

    query: str
    session_id: Optional[str] = None
    temperature: float = 0.0
    context_files: Optional[List[str]] = None


class QueryResponse(BaseModel):
    """Response model for query endpoint."""

    response: str
    session_id: str


# Session Endpoint Models
class SessionResponse(BaseModel):
    """Response model for session endpoint."""

    id: str
    created_at: str
    updated_at: str


class SessionsListResponse(BaseModel):
    """Response model for sessions list endpoint."""

    sessions: List[SessionResponse]


class SessionDeleteResponse(BaseModel):
    """Response model for session delete endpoint."""

    success: bool


# Status Endpoint Models
class StatusResponse(BaseModel):
    """Response model for status endpoint."""

    status: str
    version: str
    working_directory: str
    indexed_files: int


class VersionCheckResponse(BaseModel):
    """Response model for version check endpoint."""

    current_version: str
    latest_version: str
    needs_update: bool
    update_url: str = "https://pypi.org/project/docstra/"
