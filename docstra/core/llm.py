"""LLM chain service for Docstra."""

from pathlib import Path
from typing import AsyncGenerator, Dict, List, Optional, Union, Any

from docstra.core.config import DocstraConfig
from docstra.core.base import BaseService
from docstra.core.interfaces import (
    IContextManager,
    IDatabase,
    ILLMChain,
    ILogger,
    IRetriever,
    IVectorStore,
)
from docstra.core.errors import ConfigError
from docstra.core.context import DocstraContextManager
from docstra.core.retriever import DocstraRetriever


class DocstraLLMChain(BaseService, ILLMChain):
    """Service for managing LLM interactions and retrieval chain."""

    def __init__(
        self,
        working_dir: Optional[Union[str, Path]] = None,
        config_path: Optional[Union[str, Path]] = None,
        log_level: Optional[str] = None,
        log_file: Optional[str] = None,
        config: Optional[DocstraConfig] = None,
        logger: Optional[ILogger] = None,
        vectorstore: Optional[IVectorStore] = None,
        db: Optional[IDatabase] = None,
        context_manager: Optional[IContextManager] = None,
        retriever: Optional[IRetriever] = None,
    ):
        """Initialize the LLM chain.

        Args:
            working_dir: Working directory containing the codebase
            config_path: Optional path to configuration file
            log_level: Optional logging level override
            log_file: Optional log file path
            config: Optional configuration instance
            logger: Optional logger instance
            vectorstore: Optional vectorstore for embeddings
            db: Optional database instance
            context_manager: Optional context manager instance
            retriever: Optional retriever instance
        """
        # Initialize base service
        super().__init__(
            working_dir=working_dir,
            config_path=config_path,
            log_level=log_level,
            log_file=log_file,
            config=config,
            logger=logger,
        )

        # Store components
        self.vectorstore = vectorstore
        self.db = db
        self.context_manager = context_manager

        # Initialize retriever if provided or if vectorstore is available
        if retriever:
            self.retriever = retriever
        elif vectorstore:
            self.retriever = DocstraRetriever(
                vectorstore=vectorstore,
                config=self.config,
                logger=self.logger,
            )
        else:
            self.retriever = None

        # Initialize components if vectorstore is provided
        if vectorstore:
            self._init_components()

    def _validate_config(self) -> None:
        """Validate LLM chain configuration.

        Raises:
            ConfigError: If configuration is invalid
        """
        # Call base validation
        super()._validate_config()

        # Validate API key
        self.validate_api_key()

        # Add any additional validation here
        if not self.config.model_name:
            raise ConfigError("Model name not configured")

    def _init_components(self) -> None:
        """Initialize LLM chain components."""
        from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
        from langchain_openai import ChatOpenAI

        # Initialize LLM
        self.llm = ChatOpenAI(
            model=self.config.model_name,
            temperature=self.config.temperature,
            streaming=True,
        )

        # Initialize prompt
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.config.system_prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{question}"),
                MessagesPlaceholder(variable_name="context"),
            ]
        )

    async def process_message_stream(
        self, message: str, chat_history: List[Dict]
    ) -> AsyncGenerator[str, None]:
        """Process a message and stream the response.

        Args:
            message: The user's message
            chat_history: List of previous chat messages

        Yields:
            Chunks of the response as they are generated
        """
        # Get relevant documents
        docs = await self.retriever.get_relevant_documents(message)

        # Format context from documents
        context = []
        for doc in docs:
            # Handle both Document objects and dictionary results
            if hasattr(doc, "metadata"):
                file_path = doc.metadata.get("file_path", "unknown")
                content = doc.page_content
            else:
                file_path = doc.get("metadata", {}).get("file_path", "unknown")
                content = doc.get("text", "")

            context.append(
                {
                    "role": "system",
                    "content": f"Relevant code from {file_path}:\n{content}",
                }
            )

        # Create chain
        chain = self.prompt | self.llm

        # Stream response
        async for chunk in chain.astream(
            {
                "question": message,
                "chat_history": chat_history,
                "context": context,
            }
        ):
            if chunk.content:
                yield chunk.content

    async def process_message(self, message: str, chat_history: List[Dict]) -> str:
        """Process a message and return the complete response.

        Args:
            message: The user's message
            chat_history: List of previous chat messages

        Returns:
            Complete response
        """
        # Get relevant documents
        docs = await self.retriever.get_relevant_documents(message)

        # Format context from documents
        context = []
        for doc in docs:
            # Handle both Document objects and dictionary results
            if hasattr(doc, "metadata"):
                file_path = doc.metadata.get("file_path", "unknown")
                content = doc.page_content
            else:
                file_path = doc.get("metadata", {}).get("file_path", "unknown")
                content = doc.get("text", "")

            context.append(
                {
                    "role": "system",
                    "content": f"Relevant code from {file_path}:\n{content}",
                }
            )

        # Create chain
        chain = self.prompt | self.llm

        # Get response
        response = await chain.ainvoke(
            {
                "question": message,
                "chat_history": chat_history,
                "context": context,
            }
        )

        return response.content

    async def preview_context(self, message: str) -> str:
        """Preview the context that would be used for a message.

        Args:
            message: The message to get context for

        Returns:
            A string containing the preview of relevant context
        """
        docs = await self.retriever.get_relevant_documents(message)
        preview = []
        for doc in docs:
            preview.append(
                f"From {doc.metadata.get('file_path', 'unknown')}:\n{doc.page_content}\n"
            )
        return "\n".join(preview)
