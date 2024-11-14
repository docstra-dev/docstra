from os import PathLike
import chromadb
from chromadb.utils.embedding_functions import create_langchain_embedding
from docstra.logger import logger
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

def initialize_vectorstore(
    db_dir: str | PathLike[str] = "./.docstra/db",
    collection_name: str = "codebase",
    embeddings_model: str = "text-embedding-3-small"
):
    """Initializes the Chroma vectorstore with a persistent client and embeddings."""
    client = chromadb.PersistentClient(path=db_dir)
    embeddings = OpenAIEmbeddings(model=embeddings_model)
    ef = create_langchain_embedding(embeddings)
    vectorstore = Chroma(
        client=client,
        collection_name=collection_name,
        embedding_function=ef,
    )
    return vectorstore

def add_documents_to_vectorstore(vectorstore, documents, batch_size=100):
    """Adds documents to the given vectorstore in batches."""
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i + batch_size]
        try:
            vectorstore.add_documents(batch)
            logger.info(f"Added batch {i // batch_size + 1}")
        except Exception as e:
            logger.error(f"Error adding batch {i // batch_size + 1}: {e}")

def get_retriever(vectorstore):
    """Returns a retriever from the given vectorstore."""
    return vectorstore.as_retriever()
