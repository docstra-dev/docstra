from os import PathLike

import chromadb
from chromadb.utils.embedding_functions import create_langchain_embedding
from docstra.logger import logger
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings


class DocstraVectorstore:
    def __init__(self, db_dir:str|PathLike[str]="./db", collection_name:str="codebase", embeddings_model:str="text-embedding-3-small"):
        self.client = chromadb.PersistentClient(path=db_dir)
        self.embeddings = OpenAIEmbeddings(model=embeddings_model)
        self.ef = create_langchain_embedding(self.embeddings)
        self.collection = self.client.get_or_create_collection(collection_name)
        self.vectorstore = Chroma(
            client=self.client,
            collection_name=collection_name,
            embedding_function=self.ef,
        )

    def add_documents(self, documents, batch_size=100):
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            try:
                self.vectorstore.add_documents(batch)
                logger.info(f"Added batch {i // batch_size + 1}")
            except Exception as e:
                logger.error(f"Error adding batch {i // batch_size + 1}: {e}")

    def as_retriever(self):
        return self.vectorstore.as_retriever()