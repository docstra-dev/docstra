from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path
import uvicorn
from chat_db import save_chat_session, get_chat_sessions, get_chat_history  # Import from chat_db.py

from docstra.config import load_core_config, load_project_config, set_openai_api_key, get_openai_api_key
from docstra.ingestor import ingest_repo
from docstra.main import Docstra
from docstra.vectorstore import initialize_vectorstore, add_documents_to_vectorstore, get_retriever
from docstra.llm_engine import initialize_llm, create_question_answer_chain, create_rag_chain, run_query

# Initialize FastAPI app
app = FastAPI()


### Request Models for the API ###
class IngestRequest(BaseModel):
    repo_path: str  # Required repo path for ingestion


class QueryRequest(BaseModel):
    repo_path: str  # Required repo path to target specific repo
    query: str

### API Endpoints ###

@app.post("/chat/save")
async def save_chat(request: QueryRequest):
    """Save a chat session to the database."""
    try:
        session_name = f"Session - {request.repo_path}"  # Generate session name
        messages = [{"question": request.query, "answer": "Mock Answer"}]  # Replace with real chat response

        save_chat_session(session_name, messages)
        return {"message": "Chat session saved successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving chat session: {str(e)}")

@app.get("/chat/sessions")
async def list_chat_sessions():
    """List all stored chat sessions."""
    try:
        sessions = get_chat_sessions()
        return {"sessions": sessions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving chat sessions: {str(e)}")

@app.get("/chat/history/{session_id}")
async def get_chat_history_api(session_id: int):
    """Retrieve chat history for a specific session."""
    try:
        history = get_chat_history(session_id)
        if history is None:
            raise HTTPException(status_code=404, detail="Session not found")
        return {"history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving chat history: {str(e)}")


@app.post("/ingest")
async def ingest_repository(request: IngestRequest):
    try:
        repo = Path(request.repo_path).resolve()
        docstra = Docstra(repo)

        await docstra.ingest_repository()

        return {"message": f"Repository '{repo}' ingested successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during ingestion: {str(e)}")


@app.post("/query")
async def query_repository(request: QueryRequest):
    try:
        repo = Path(request.repo_path).resolve()
        docstra = Docstra(repo)

        result = docstra.query_repository(request.query)

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during query: {str(e)}")

def run_server(host: str = "127.0.0.1", port: int = 8000):
    uvicorn.run(app, host=host, port=port)

def main():
    run_server()

### Running the App ###
if __name__ == "__main__":
    main()
