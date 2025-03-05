"""Main service class for Docstra that coordinates all components."""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Union

from docstra.config import DocstraConfig
from docstra.database import create_database
from docstra.errors import ConfigError
from docstra.service.context import DocstraContextManager
from docstra.service.indexer import DocstraIndexer
from docstra.service.llm import DocstraLLMChain
from docstra.service.session import DocstraSessionManager


def setup_logging(
    log_level: str = "INFO", log_file: Optional[str] = None, console_output: bool = True
):
    """Configure logging for Docstra.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path to write logs to
        console_output: Whether to output logs to console

    Returns:
        Logger instance configured for docstra

    Raises:
        ConfigError: If the log level is invalid or if there's an issue setting up logging
    """
    try:
        numeric_level = getattr(logging, log_level.upper(), None)
        if not isinstance(numeric_level, int):
            raise ConfigError(f"Invalid log level: {log_level}")

        # Create logger
        logger = logging.getLogger("docstra")
        logger.setLevel(numeric_level)

        # Remove any existing handlers to avoid duplicates
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        # Define formatter
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        formatter = logging.Formatter(log_format)

        # Add file handler if specified
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(numeric_level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        # Add console handler if requested
        if console_output:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(numeric_level)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

        return logger
    except Exception as e:
        if isinstance(e, ConfigError):
            raise e
        raise ConfigError(f"Failed to setup logging: {str(e)}", cause=e)


class DocstraService:
    """Main service for Docstra, coordinating all components."""

    def __init__(
        self,
        working_dir: str | Path = None,
        config_path: str | Path = None,
        log_level: str = None,
    ):
        """Initialize the Docstra service.

        Args:
            working_dir: The directory to index and operate in
            config_path: Path to explicit configuration file (optional)
            log_level: Override the logging level
        """
        # Set working directory first
        self.working_dir = Path(working_dir) if working_dir else Path.cwd()
        
        # Ensure we load the .env file explicitly to address environment variable issues
        env_file = self.working_dir / ".docstra" / ".env"
        if env_file.exists():
            from dotenv import load_dotenv
            load_dotenv(env_file)

        # Load configuration with proper precedence:
        # 1. Explicit config_path parameter (if provided)
        # 2. Environment variables
        # 3. .docstra/config.json
        # 4. docstra.json in repo root (legacy support)
        # 5. Default values
        if config_path:
            # If explicit config path provided, use it directly
            self.config = DocstraConfig.from_file(config_path)
        else:
            # Otherwise use the smart loading mechanism with proper precedence
            self.config = DocstraConfig.load(self.working_dir)

        # Create persistence directory per config
        self.persist_dir = self.working_dir / self.config.persist_directory
        self.persist_dir.mkdir(exist_ok=True, parents=True)

        # Set up logging from config (with potential override)
        log_level = log_level or self.config.log_level
        self.logger = setup_logging(
            log_level=log_level,
            log_file=self.config.log_file,
            console_output=self.config.console_logging,
        )
        self.logger.info(f"Initializing DocstraService in {self.working_dir}")

        # Initialize the database
        db_path = self.persist_dir / "sessions.db"
        self.db = create_database(str(db_path))

        # Save config to persistence directory (to ensure it exists for future runs)
        saved_config_path = self.persist_dir / "config.json"
        if not saved_config_path.exists():
            self.logger.debug(f"Saving configuration to {saved_config_path}")
            self.config.to_file(str(saved_config_path))

        # Initialize components
        self.logger.debug("Initializing components...")

        # Initialize context manager
        self.context_manager = DocstraContextManager(
            working_dir=self.working_dir, logger=self.logger
        )

        # Initialize indexer
        self.indexer = DocstraIndexer(
            working_dir=self.working_dir,
            persist_dir=self.persist_dir,
            config=self.config,
            db=self.db,
            logger=self.logger,
        )

        # Initialize LLM chain
        self.llm_chain = DocstraLLMChain(
            working_dir=self.working_dir,
            config=self.config,
            vectorstore=self.indexer.get_vectorstore(),
            db=self.db,
            context_manager=self.context_manager,
            logger=self.logger,
        )

        # Make retriever available at the service level for direct access
        self.retriever = self.llm_chain.retriever

        # Set service reference in retriever
        self.llm_chain.set_retriever_service(self)

        # Initialize session manager
        self.session_manager = DocstraSessionManager(
            working_dir=self.working_dir,
            config=self.config,
            db=self.db,
            retriever=self.llm_chain.retriever,
            context_manager=self.context_manager,
            logger=self.logger,
        )

    def update_index(self, force: bool = False) -> None:
        """Update the codebase index, only reindexing changed files.

        Args:
            force: If True, force reindexing of all files regardless of modification time
        """
        self.indexer.update_index(force=force)

    def get_or_index_file(self, file_path: str) -> Union[List, bool]:
        """Check if file is indexed, index on-demand if not.

        Args:
            file_path: Relative path to the file

        Returns:
            Either a list of document chunks or a boolean indicating success
        """
        return self.indexer.get_or_index_file(file_path)

    def create_session(self) -> str:
        """Create a new session and return its ID."""
        return self.session_manager.create_session()

    def get_session(self, session_id: str):
        """Get a session by ID."""
        return self.session_manager.get_session(session_id)

    def add_message(self, session_id: str, role: str, content: str) -> None:
        """Add a message to a session and save to database."""
        self.session_manager.add_message(session_id, role, content)

    async def process_message_stream(
        self, session_id: str, message: str, debug: bool = False
    ):
        """Process a user message and stream the assistant's response.

        Args:
            session_id: ID of the session to use
            message: User message to process
            debug: Whether to show debug information

        Yields:
            Chunks of the response as they are generated
        """
        session = self.session_manager.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        # Add user message
        self.session_manager.add_message(session_id, "user", message)

        # Process message with LLM chain
        try:
            # Extract file references from the message (for logging only)
            self._pre_process_file_references(message)

            # Make sure the retriever has the correct context files from this session
            self._ensure_retriever_has_session_context(session)

            # Get the chat history from the session
            chat_history = session.chat_history.messages

            # Stream the response chunks
            full_response = ""
            async for chunk in self.llm_chain.process_message_stream(
                message, chat_history
            ):
                if chunk:  # Skip empty chunks
                    full_response += chunk
                    yield chunk

            # If debug mode is enabled, yield model usage information
            if debug:
                usage_info = "\n\n---\n[DEBUG] Token usage info: Not available in this implementation"
                yield usage_info
                full_response += usage_info

            # Add the complete assistant response to the session
            if full_response:
                self.session_manager.add_message(session_id, "assistant", full_response)

        except Exception as e:
            self.logger.error(f"Chain streaming error: {str(e)}")
            # Fallback to direct LLM call if chain fails
            self.logger.info("Using fallback direct LLM call")

            error_response = f"Error processing message: {str(e)}"
            yield error_response

            # Add error message to session
            self.session_manager.add_message(session_id, "assistant", error_response)

    def process_message(self, session_id: str, message: str) -> str:
        """Process a user message and return the assistant's response."""
        session = self.session_manager.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        # Add user message
        self.session_manager.add_message(session_id, "user", message)

        # Process message with LLM chain
        try:
            # Extract file references from the message (for logging only)
            self._pre_process_file_references(message)

            # Make sure the retriever has the correct context files from this session
            self._ensure_retriever_has_session_context(session)

            # Get the chat history from the session
            chat_history = session.chat_history.messages

            # Process the message through the LLM chain
            answer = self.llm_chain.process_message(message, chat_history)

            # Add assistant response
            self.session_manager.add_message(session_id, "assistant", answer)

            return answer
        except Exception as e:
            self.logger.error(f"Error processing message: {str(e)}")
            error_response = f"Error processing message: {str(e)}"
            self.session_manager.add_message(session_id, "assistant", error_response)
            return error_response

    def _pre_process_file_references(self, message: str) -> None:
        """Extract file references from the message (simplified version).

        In the simplified workflow, all files are already indexed upfront,
        so this method now just logs found references but doesn't 
        trigger on-demand indexing.

        Args:
            message: The user message to process
        """
        from docstra.loader import extract_file_references

        potential_files = extract_file_references(message)
        if potential_files:
            self.logger.debug(
                f"Found potential file references in query: {potential_files}"
            )

    def _ensure_retriever_has_session_context(self, session) -> None:
        """Make sure the retriever has the correct context files set.

        Args:
            session: The current session
        """
        # Update retriever with context files if needed
        if hasattr(session, "context_files") and hasattr(
            self.retriever, "set_specific_context_files"
        ):
            if session.context_files:
                self.retriever.set_specific_context_files(session.context_files)
                self.logger.debug(
                    f"Updated retriever with {len(session.context_files)} context files"
                )
            else:
                self.retriever.clear_specific_context_files()
                self.logger.debug("Cleared specific context files from retriever")

    def add_context(
        self,
        session_id: str,
        file_path: str,
        content: str = None,
        selection_range: Dict = None,
    ) -> None:
        """Add additional context to a session."""
        self.session_manager.add_context(
            session_id=session_id,
            file_path=file_path,
            content=content,
            selection_range=selection_range,
        )

    def get_context_files(self, session_id: str) -> List[str]:
        """Get the list of files that have been added to a session's context."""
        return self.session_manager.get_context_files(session_id)

    def preview_context(self, session_id: str, message: str) -> str:
        """Get a preview of the context that would be retrieved for a message."""
        return self.llm_chain.preview_context(message)

    def remove_context_file(self, session_id: str, file_path: str) -> bool:
        """Remove a file from a session's context list."""
        return self.session_manager.remove_context_file(session_id, file_path)

    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        return self.session_manager.delete_session(session_id)

    def get_all_session_ids(self) -> List[str]:
        """Get all session IDs from the database."""
        return self.session_manager.get_all_session_ids()

    def get_all_sessions(self) -> List:
        """Get all sessions as DocstraSession objects."""
        return self.session_manager.get_all_sessions()

    def rename_session(self, session_id: str, new_name: str) -> bool:
        """Rename a session by storing a name in its config."""
        return self.session_manager.rename_session(session_id, new_name)

    def cleanup(self):
        """Clean up resources when shutting down."""
        try:
            # Close database connections
            if hasattr(self, "db"):
                self.db.close()

            # Clear memory caches
            if hasattr(self, "session_manager") and hasattr(
                self.session_manager, "sessions"
            ):
                self.session_manager.sessions.clear()

            self.logger.info("Resources cleaned up")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {str(e)}")
