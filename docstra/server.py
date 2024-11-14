from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path
import uvicorn

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
