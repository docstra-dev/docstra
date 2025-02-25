import signal
import threading
from typing import Dict, List, Optional, Any
from fastapi import (
    FastAPI,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
    BackgroundTasks,
    Depends,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi import status
from pydantic import BaseModel
import asyncio
import os
import uvicorn

# Import the core service
from .core import DocstraService, DocstraConfig


# Define API models
class SessionCreate(BaseModel):
    working_dir: Optional[str] = None


class MessageCreate(BaseModel):
    content: str


class ContextAdd(BaseModel):
    file_path: str
    content: Optional[str] = None
    selection_range: Optional[Dict[str, int]] = None


class ConfigUpdate(BaseModel):
    model_name: Optional[str] = None
    temperature: Optional[float] = None
    system_prompt: Optional[str] = None


class Message(BaseModel):
    role: str
    content: str
    timestamp: str


class Session(BaseModel):
    session_id: str
    created_at: str
    messages: List[Message]


# Initialize the app
app = FastAPI(title="Docstra API", description="API for Docstra code assistant")

# Add CORS middleware to allow requests from IDE extensions
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Ideally, restrict this to your extension's origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active connections
active_connections: Dict[str, WebSocket] = {}


# Initialize the service as a singleton
service = None


# Change the dependency to return the singleton instance
def get_service():
    """Dependency to return the singleton service instance."""
    global service
    if service is None:
        # Initialize with default if not already initialized
        service = DocstraService()
    return service


@app.post("/sessions/create", response_model=dict)
async def create_session(
    session_create: SessionCreate, service: DocstraService = Depends(get_service)
):
    """Create a new chat session."""
    # If working directory specified, initialize a new service
    if session_create.working_dir:
        service = DocstraService(working_dir=session_create.working_dir)

    session_id = service.create_session()
    return {"session_id": session_id}


@app.get("/sessions/{session_id}", response_model=Session)
async def get_session(session_id: str, service: DocstraService = Depends(get_service)):
    """Get session details."""
    session = service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "session_id": session.session_id,
        "created_at": session.created_at.isoformat(),
        "messages": session.messages,
    }


@app.post("/sessions/{session_id}/message", response_model=dict)
async def send_message(
    session_id: str,
    message: MessageCreate,
    background_tasks: BackgroundTasks,
    service: DocstraService = Depends(get_service),
):
    """Send a message to the session."""
    session = service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Process message in background if websocket is connected
    # Otherwise process synchronously
    if session_id in active_connections:
        background_tasks.add_task(
            stream_response, session_id=session_id, message=message.content
        )
        return {"status": "processing"}
    else:
        response = service.process_message(session_id, message.content)
        return {"response": response}


@app.post("/sessions/{session_id}/context", response_model=dict)
async def add_context(
    session_id: str, context: ContextAdd, service: DocstraService = Depends(get_service)
):
    """Add code context to session."""
    session = service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        service.add_context(
            session_id, context.file_path, context.content, context.selection_range
        )
        return {"status": "context added"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/sessions/{session_id}/config", response_model=dict)
async def update_config(
    session_id: str,
    config: ConfigUpdate,
    service: DocstraService = Depends(get_service),
):
    """Update session configuration."""
    session = service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Update config values
    if config.model_name is not None:
        session.config.model_name = config.model_name

    if config.temperature is not None:
        session.config.temperature = config.temperature

    if config.system_prompt is not None:
        session.config.system_prompt = config.system_prompt

    return {"status": "config updated"}


@app.delete("/sessions/{session_id}", response_model=dict)
async def delete_session(
    session_id: str, service: DocstraService = Depends(get_service)
):
    """End and cleanup session."""
    session = service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Remove session
    service.sessions.pop(session_id, None)

    return {"status": "session deleted"}


@app.get("/sessions/{session_id}/messages", response_model=List[Message])
async def get_messages(session_id: str, service: DocstraService = Depends(get_service)):
    """Get message history for a session."""
    session = service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return session.messages


@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check(service: DocstraService = Depends(get_service)):
    """Endpoint to verify the API is running and identify its working directory."""
    return {
        "status": "ok",
        "working_directory": service.working_dir,
    }


# Add shutdown endpoint
@app.post("/shutdown", status_code=status.HTTP_202_ACCEPTED)
async def shutdown():
    """Gracefully shut down the server."""

    def shutdown_server():
        # Give time for the response to be sent
        threading.Timer(1.0, lambda: os.kill(os.getpid(), signal.SIGTERM)).start()

    shutdown_server()
    return {"status": "shutting_down"}


@app.websocket("/sessions/{session_id}/stream")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: str,
):
    """WebSocket endpoint for streaming responses."""
    global service  # Use the global service directly

    await websocket.accept()

    # Check if session exists
    session = service.get_session(session_id)
    if not session:
        await websocket.close(code=1008, reason="Session not found")
        return

    # Store websocket connection
    active_connections[session_id] = websocket

    try:
        while True:
            # Wait for message from client
            data = await websocket.receive_text()

            # Process message in a non-blocking way
            asyncio.create_task(stream_response(session_id, data))
    except WebSocketDisconnect:
        # Remove connection when disconnected
        active_connections.pop(session_id, None)


@app.on_event("shutdown")
async def shutdown_event():
    global service
    if service:
        service.cleanup()


async def stream_response(session_id: str, message: str):
    """Stream response to websocket client."""
    websocket = active_connections.get(session_id)
    if not websocket:
        return

    try:
        # Send acknowledgment
        await websocket.send_json(
            {"type": "ack", "message": "Processing your message..."}
        )

        # Process the message (this would ideally be streaming, but for now we're simulating)
        response = service.process_message(session_id, message)

        # Send the full response
        await websocket.send_json({"type": "response", "content": response})
    except Exception as e:
        # Send error if something goes wrong
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
        except:
            pass


# CLI entry point
def start_server(host: str = "127.0.0.1", port: int = 8000, working_dir: str = None):
    """Start the API server."""
    # Initialize service with working directory if provided
    global service

    # Cleanup any existing service
    if service is not None:
        service.cleanup()

    if working_dir:
        service = DocstraService(working_dir=working_dir)
    else:
        service = DocstraService()  # Create with default directory

    # Run the server
    uvicorn.run(app, host=host, port=port, workers=1)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Start Docstra API server")
    parser.add_argument(
        "--host", default="127.0.0.1", help="Host to bind the server to"
    )
    parser.add_argument(
        "--port", type=int, default=8000, help="Port to bind the server to"
    )
    parser.add_argument(
        "--working-dir", help="Working directory to initialize the service with"
    )

    args = parser.parse_args()
    start_server(args.host, args.port, args.working_dir)
