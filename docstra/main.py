import getpass
from os import PathLike
from pathlib import Path

import chromadb
from langchain_core.documents import Document

from docstra.config import load_core_config, load_project_config, get_openai_api_key, set_openai_api_key
from docstra.ingestor import ingest_repo
from docstra.llm_engine import (
    initialize_llm,
    create_question_answer_chain,
    create_rag_chain,
    run_query,
)
from docstra.vectorstore import (
    initialize_vectorstore,
    add_documents_to_vectorstore,
    get_retriever,
)

class Docstra:
    def __init__(
        self,
        repo_path: str | PathLike[str],
        db_dir: str | PathLike[str] = None,
        collection_name: str = "codebase",
    ):
        # Load configurations
        self.repo_path = repo_path
        self.core_config = load_core_config()
        self.project_config = load_project_config(repo_path)

        # Set up DB directory from the core config if not provided
        self.db_dir = db_dir or self.core_config["default_db_dir"]

        # Ensure the OpenAI API key is available
        openai_api_key = get_openai_api_key(repo_path)

        if not openai_api_key:
            openai_api_key = getpass.getpass("Please enter your OpenAI API key: ")
            set_openai_api_key(repo_path, openai_api_key)

        self.client = chromadb.PersistentClient(path=self.db_dir)
        self.collection_name = collection_name

        # Initialize vectorstore
        self.vectorstore = initialize_vectorstore(
            client=self.client,
            collection_name=self.collection_name,
            embeddings_model=self.core_config.get("openai_model", "text-embedding-3-small")
        )

        self.retriever = get_retriever(self.vectorstore)

        # Initialize LLM engine components
        self.llm, self.prompt, self.document_prompt = initialize_llm()
        self.question_answer_chain = create_question_answer_chain(self.llm, self.prompt, self.document_prompt)
        self.rag_chain = create_rag_chain(self.retriever, self.question_answer_chain)

    def ingest_repository(self):
        # Use project-level config options like exclusion rules
        documents = ingest_repo(
            repo_path=self.repo_path,
            hash_file=Path(self.repo_path) / ".docstra/hashes.json",
            max_tokens_per_minute=self.project_config["throttling"]["max_tokens_per_minute"],
        )
        add_documents_to_vectorstore(self.vectorstore, documents)

    def query_repository(self, query):
        return run_query(self.retriever, query)

    def get_retriever(self):
        return self.retriever

    def get_all_docs(self):
        docs = self.vectorstore.get(include=["documents", "metadatas", "embeddings"])

        ids = docs["ids"]
        embeddings = docs["embeddings"]
        documents = docs["documents"]
        metadatas = docs["metadatas"]

        # Iterate over all elements concurrently with `zip`
        for doc_id, embedding, content, metadata in zip(ids, embeddings, documents, metadatas):
            doc = Document(
                page_content=content,
                metadata=metadata
            )
            yield doc
