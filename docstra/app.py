from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from pathlib import Path
import uvicorn
from docstra.main import Docstra
from docstra.ingestor import DocstraIngestor

# Initialize FastAPI app
app = FastAPI()

# Global Docstra instance
# Specify the repository path and database directory as needed
# get working directory where the script is running
DEFAULT_REPO_PATH = Path.cwd()
docstra_instance = Docstra(repo_path=DEFAULT_REPO_PATH)

### Request Models for the API
class IngestRequest(BaseModel):
    repo_path: Optional[str] = None  # Optional if you want to dynamically set repo paths

class QueryRequest(BaseModel):
    query: str

### API Endpoints ###

@app.post("/ingest")
async def ingest_repository(request: IngestRequest):
    try:
        if request.repo_path:
            # Update the repo path if provided in the request
            docstra_instance.ingestor = DocstraIngestor(Path(request.repo_path))
        docstra_instance.ingest_repository()
        return {"message": "Repository ingested successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query")
async def query_repository(request: QueryRequest):
    try:
        result = docstra_instance.query_repository(request.query)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
