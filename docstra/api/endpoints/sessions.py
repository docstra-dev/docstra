"""Session endpoints for Docstra API."""

from fastapi import APIRouter, Depends, HTTPException

from docstra.core import ISessionManager
from docstra.api.dependencies import get_session_manager, handle_exceptions
from docstra.api.models import SessionResponse, SessionsListResponse, SessionDeleteResponse

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.get("", response_model=SessionsListResponse)
@handle_exceptions(status_code=500, error_message="Error listing sessions")
async def list_sessions_endpoint(
    session_manager: ISessionManager = Depends(get_session_manager),
) -> SessionsListResponse:
    """List all sessions.

    Args:
        session_manager: The session manager service.

    Returns:
        The sessions list response.
    """
    sessions = session_manager.list_sessions()
    return SessionsListResponse(
        sessions=[
            SessionResponse(
                id=session.id,
                created_at=str(session.created_at),
                updated_at=str(session.updated_at),
            )
            for session in sessions
        ]
    )


@router.post("", response_model=SessionResponse)
@handle_exceptions(status_code=500, error_message="Error creating session")
async def create_session_endpoint(
    session_manager: ISessionManager = Depends(get_session_manager),
) -> SessionResponse:
    """Create a new session.

    Args:
        session_manager: The session manager service.

    Returns:
        The session response.
    """
    session = session_manager.create_session()
    return SessionResponse(
        id=session.id,
        created_at=str(session.created_at),
        updated_at=str(session.updated_at),
    )


@router.get("/{session_id}", response_model=SessionResponse)
@handle_exceptions(status_code=404, error_message="Session not found")
async def get_session_endpoint(
    session_id: str,
    session_manager: ISessionManager = Depends(get_session_manager),
) -> SessionResponse:
    """Get a session by ID.

    Args:
        session_id: The ID of the session to get.
        session_manager: The session manager service.

    Returns:
        The session response.
    """
    session = session_manager.get_session(session_id)
    return SessionResponse(
        id=session.id,
        created_at=str(session.created_at),
        updated_at=str(session.updated_at),
    )


@router.delete("/{session_id}", response_model=SessionDeleteResponse)
@handle_exceptions(status_code=404, error_message="Error deleting session")
async def delete_session_endpoint(
    session_id: str,
    session_manager: ISessionManager = Depends(get_session_manager),
) -> SessionDeleteResponse:
    """Delete a session by ID.

    Args:
        session_id: The ID of the session to delete.
        session_manager: The session manager service.

    Returns:
        The session delete response.
    """
    success = session_manager.delete_session(session_id)
    return SessionDeleteResponse(success=success)