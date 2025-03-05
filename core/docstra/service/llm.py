"""LLM chain module for Docstra."""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any

from langchain_openai.chat_models import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document

from docstra.config import DocstraConfig
from docstra.database import Database
from docstra.service.context import DocstraContextManager


class DocstraLLMChain:
    """Manages LLM chain creation and execution for Docstra."""

    def __init__(
        self,
        working_dir: Path,
        config: DocstraConfig,
        vectorstore: Any,
        db: Database,
        context_manager: DocstraContextManager,
        logger: Optional[logging.Logger] = None,
    ):
        """Initialize the LLM chain manager.

        Args:
            working_dir: The project working directory
            config: Docstra configuration
            vectorstore: Initialized vector store
            db: Database instance
            context_manager: Context manager for formatting documents
            logger: Optional logger instance
        """
        self.working_dir = working_dir
        self.config = config
        self.vectorstore = vectorstore
        self.db = db
        self.context_manager = context_manager
        self.logger = logger or logging.getLogger("docstra.llm")

        # Initialize components
        self._init_llm()

    def _init_llm(self) -> None:
        """Initialize the LLM and related components."""
        # Verify that we have API keys loaded from environment variables
        import os
        
        # Check for OpenAI API key if using OpenAI
        if self.config.model_provider.lower() == 'openai' and not os.environ.get('OPENAI_API_KEY'):
            # Try to load from .env file directly as a fallback
            env_file = self.working_dir / ".docstra" / ".env"
            if env_file.exists():
                from dotenv import load_dotenv
                load_dotenv(env_file)
                self.logger.debug(f"Loaded environment variables from {env_file}")
            
            # Verify API key is now available
            if not os.environ.get('OPENAI_API_KEY'):
                self.logger.error("OPENAI_API_KEY not found in environment variables")
                raise ValueError(
                    "OpenAI API key not found. Please set OPENAI_API_KEY environment variable "
                    "or add it to .docstra/.env file."
                )
        
        self.llm = ChatOpenAI(
            model_name=self.config.model_name,
            temperature=self.config.temperature,
        )

        # Create enhanced retriever with access to database
        self.retriever = self.vectorstore.as_retriever(
            search_kwargs={"k": self.config.max_context_chunks}
        )

        # Contextualize question system prompt
        contextualize_q_system_prompt = (
            "Given a chat history and the latest user question "
            "which might reference context in the chat history, "
            "formulate a standalone question which can be understood "
            "without the chat history. Do NOT answer the question, just "
            "reformulate it if needed and otherwise return it as is."
        )

        # Create contextualize question prompt
        self.contextualize_q_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", contextualize_q_system_prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
            ]
        )

        # QA prompt
        self.qa_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.config.system_prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "Current working directory: {cwd}"),
                ("human", "{question}"),
                ("human", "Relevant documents:\n{context}"),
            ]
        )

        # Define the chain
        # First define how we process the user input with chat history
        self.contextualize_question_chain = (
            self.contextualize_q_prompt | self.llm | StrOutputParser()
        )

        # Then define the complete retrieval and answer chain
        self.chain = (
            RunnablePassthrough.assign(
                context=lambda x: self._get_context_for_query(
                    question=x["question"], chat_history=x.get("chat_history", [])
                ),
            )
            | self.qa_prompt
            | self.llm
            | StrOutputParser()
        )

    def process_message(self, question: str, chat_history: List = None) -> str:
        """Process a user message through the LLM chain.

        Args:
            question: The user question to process
            chat_history: Optional chat history for context

        Returns:
            The assistant's response
        """
        try:
            # Invoke the chain
            self.logger.debug(f"Processing message: {question[:50]}...")

            if not chat_history:
                chat_history = []

            response = self.chain.invoke(
                {
                    "question": question,
                    "chat_history": chat_history,
                    "cwd": self.working_dir,
                }
            )

            return response
        except Exception as e:
            self.logger.error(f"Chain execution error: {str(e)}")
            # Fallback to direct LLM call if chain fails
            self.logger.info("Using fallback direct LLM call")
            response = self.llm.invoke(
                f"Question about codebase: {question}\nWorking directory: {self.working_dir}"
            )
            return response.content

    async def process_message_stream(self, question: str, chat_history: List = None):
        """Process a user message and stream the assistant's response.

        Args:
            question: The user question to process
            chat_history: Optional chat history for context

        Yields:
            Chunks of the response as they are generated
        """
        try:
            if not chat_history:
                chat_history = []

            # Prepare the input for the chain
            chain_input = {
                "question": question,
                "chat_history": chat_history,
                "cwd": self.working_dir,
            }

            # Stream the response chunks
            full_response = ""
            async for chunk in self.chain.astream(chain_input):
                if chunk:  # Skip empty chunks
                    full_response += chunk
                    yield chunk

            return
        except Exception as e:
            self.logger.error(f"Error during streaming: {str(e)}")
            error_msg = f"Error generating response: {str(e)}"
            yield error_msg
            return

    def _get_context_for_query(self, question: str, chat_history: List = None) -> str:
        """Get formatted context for a query, applying context reformulation if needed.

        Args:
            question: The user question
            chat_history: Optional chat history for context

        Returns:
            Formatted context string ready for the LLM
        """
        # First, reformulate the question if we have chat history
        if chat_history:
            # Create a standalone question that incorporates context from chat history
            standalone_question = self.contextualize_question_chain.invoke(
                {
                    "input": question,
                    "chat_history": chat_history,
                }
            )
            self.logger.debug(f"Reformulated question: {standalone_question}")
        else:
            standalone_question = question

        # Get documents from retriever
        try:
            docs = self.retriever.invoke(standalone_question)
            self.logger.debug(f"Retrieved {len(docs)} documents for context")

            # Format the documents with clickable links
            formatted_context = self.context_manager.format_context_with_links(docs)
            return formatted_context
        except Exception as e:
            self.logger.error(f"Error retrieving context: {e}")
            # Ensure we return a proper string to avoid concatenation issues
            return f"Error retrieving context: {str(e)}"

    def preview_context(self, question: str) -> str:
        """Get a preview of the context that would be retrieved for a question.

        Args:
            question: User question

        Returns:
            Formatted context string
        """
        try:
            # We don't need to use the contextualize chain for preview
            # Just retrieve context documents directly
            docs = self.retriever.invoke(question)

            # Format context with links
            formatted_context = self.context_manager.format_context_with_links(docs)

            return formatted_context
        except Exception as e:
            self.logger.error(f"Error previewing context: {e}")
            # Ensure we return a proper string to avoid concatenation issues
            return f"Error generating context preview: {str(e)}"

    def set_retriever_service(self, service: Any) -> None:
        """Set the service reference in the retriever.

        Args:
            service: DocstraService instance
        """
        if hasattr(self.retriever, "service"):
            self.retriever.service = service
