import getpass
import os
from pathlib import Path

from docstra.ingestor import DocstraIngestor
from docstra.llm_engine import DocstraLLMEngine
from docstra.vectorstore import DocstraVectorstore
from dotenv import load_dotenv

load_dotenv(Path(".docstra/.env"))  # This loads variables from .env into environment
openai_api_key = os.environ.get("OPENAI_API_KEY")

if not openai_api_key:
    openai_api_key = getpass.getpass("Please enter your OpenAI API key: ")
    os.environ["OPENAI_API_KEY"] = openai_api_key
    with open(env_path, "a") as f:
        f.write(f"\nOPENAI_API_KEY={openai_api_key}")


class Docstra:
    def __init__(
        self,
        repo_path: str | PathLike[str],
        db_dir: str | PathLike[str] = Path(
            ".app_data/projects/",
        ),
    ):
        self.ingestor = DocstraIngestor(repo_path)
        self.vectorstore = DocstraVectorstore(db_dir)
        self.retriever = self.vectorstore.as_retriever()
        self.llm_engine = DocstraLLMEngine(retriever=self.retriever)

    def ingest_repository(self):
        documents = self.ingestor.ingest_repo()
        self.vectorstore.add_documents(documents)

    def query_repository(self, query):
        return self.llm_engine.run_query(query)


def get_docstra_path(repo_path: str | PathLike[str]) -> Path:
    # Define the .docstra directory in the repository
    docstra_dir = os.path.join(repo_path, ".docstra")

    # Check if it exists; if not, create it
    pathlib.Path(docstra_dir).mkdir(parents=True, exist_ok=True)

    return docstra_dir


def generateProjectPath(repoPath: str | PathLike[str]) -> Path:
    return Path(".docstra/projects/", repoPath)
