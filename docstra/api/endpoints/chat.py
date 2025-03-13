"""Chat endpoints for Docstra API."""

from typing import Dict, List, Optional
import json

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from docstra.service import DocstraService
from docstra.api.dependencies import get_service, handle_exceptions


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""

    message: str
    session_id: Optional[str] = None
    stream: bool = False


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""

    message: str
    session_id: str


router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
@handle_exceptions(status_code=500, error_message="Error processing chat message")
async def chat(request: ChatRequest, service: DocstraService = Depends(get_service)):
    """Chat with Docstra.

    Args:
        request: Chat request containing message and optional session ID
        service: DocstraService instance

    Returns:
        Response containing the assistant's message and session ID
    """
    # Create or get session
    session_id = request.session_id or service.create_session()
    session = service.session_manager.get_session(session_id)

    # Process message
    response = await service.llm_chain.process_message(
        message=request.message,
        chat_history=session.get_messages(),
    )

    # Add message to session
    session.add_user_message(request.message)
    session.add_assistant_message(response)

    return ChatResponse(
        message=response,
        session_id=session_id,
    )


@router.post("/chat/stream")
@handle_exceptions(status_code=500, error_message="Error processing streaming chat")
async def chat_stream(
    request: ChatRequest, service: DocstraService = Depends(get_service)
):
    """Chat with Docstra with streaming response.

    Args:
        request: Chat request containing message and optional session ID
        service: DocstraService instance

    Returns:
        Streaming response containing the assistant's message chunks
    """
    # Create or get session
    session_id = request.session_id or service.create_session()
    session = service.session_manager.get_session(session_id)

    # Add user message to session
    session.add_user_message(request.message)

    # Create streaming response
    async def stream_response():
        full_response = ""

        # Stream message chunks
        async for chunk in service.llm_chain.process_message_stream(
            message=request.message,
            chat_history=session.get_messages(),
        ):
            full_response += chunk
            yield f"data: {json.dumps({'chunk': chunk, 'session_id': session_id})}\n\n"

        # Add complete response to session
        session.add_assistant_message(full_response)

        # Send end of stream marker
        yield f"data: {json.dumps({'done': True})}\n\n"

    return StreamingResponse(
        stream_response(),
        media_type="text/event-stream",
    )
