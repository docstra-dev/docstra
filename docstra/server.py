from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path
import uvicorn

from docstra.config import load_core_config, load_project_config, set_openai_api_key, get_openai_api_key
from docstra.ingestor import ingest_repo
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


### Helper Functions to Create Docstra Instances Dynamically ###
def create_docstra_instance(repo_path: str):
    """Dynamically create and return a Docstra instance configured for the given repo path."""
    repo_path = Path(repo_path)
    core_config = load_core_config()
    db_dir = core_config.get("default_db_dir", ".app_data/db")

    # Ensure OpenAI API key is set for the repository
    openai_api_key = get_openai_api_key(repo_path)
    if not openai_api_key:
        raise HTTPException(status_code=400, detail="OpenAI API key is not set for this repository.")

    # Initialize vectorstore and retriever
    vectorstore = initialize_vectorstore(db_dir=db_dir, collection_name=repo_path.name)
    retriever = get_retriever(vectorstore)

    # Initialize LLM components
    llm, prompt = initialize_llm()
    question_answer_chain = create_question_answer_chain(llm, prompt)
    rag_chain = create_rag_chain(retriever, question_answer_chain)

    return {
        "vectorstore": vectorstore,
        "retriever": retriever,
        "rag_chain": rag_chain
    }


### API Endpoints ###

@app.post("/ingest")
async def ingest_repository(request: IngestRequest):
    try:
        # Load project configuration and ensure the .docstra path exists
        repo_path = Path(request.repo_path)
        documents = ingest_repo(repo_path=repo_path)

        # Create a new vectorstore instance and add the documents
        vectorstore = initialize_vectorstore(db_dir=repo_path / ".docstra/db", collection_name=repo_path.name)
        add_documents_to_vectorstore(vectorstore, documents)

        return {"message": f"Repository '{repo_path}' ingested successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during ingestion: {str(e)}")


@app.post("/query")
async def query_repository(request: QueryRequest):
    try:
        # Dynamically create a Docstra instance for the given repo path
        docstra_instance = create_docstra_instance(request.repo_path)

        # Run the query using the dynamically created RAG chain
        result = run_query(docstra_instance["retriever"], request.query)

        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during query: {str(e)}")

def run_server(host: str = "127.0.0.1", port: int = 8000):
    uvicorn.run(app, host=host, port=port)

def main():
    run_server()

### Running the App ###
if __name__ == "__main__":
    main()
