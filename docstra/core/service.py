"""Main service class for Docstra that coordinates all components."""

from pathlib import Path
from typing import Dict, List, Optional, Union, Any

from docstra.core.base import BaseService
from docstra.core.interfaces import (
    IContextManager,
    IDatabase,
    IDocstraService,
    IIndexer,
    ILLMChain,
    ILogger,
    ISessionManager,
    IVectorStore,
)
from docstra.core.config import DocstraConfig
from docstra.core.errors import ConfigError


class DocstraService(BaseService, IDocstraService):
    """Main service for Docstra, coordinating all components."""

    def __init__(
        self,
        working_dir: Optional[Union[str, Path]] = None,
        config_path: Optional[Union[str, Path]] = None,
        log_level: Optional[str] = None,
        log_file: Optional[str] = None,
        config: Optional[DocstraConfig] = None,
        logger: Optional[ILogger] = None,
        container: Optional[Any] = None,
        db: Optional[IDatabase] = None,
        vectorstore: Optional[IVectorStore] = None,
        context_manager: Optional[IContextManager] = None,
        llm_chain: Optional[ILLMChain] = None,
        indexer: Optional[IIndexer] = None,
        session_manager: Optional[ISessionManager] = None,
    ):
        """Initialize the Docstra service.

        Args:
            working_dir: Working directory containing the codebase
            config_path: Optional path to configuration file
            log_level: Optional logging level override
            log_file: Optional log file path
            config: Optional configuration instance
            logger: Optional logger instance
            container: Optional dependency injection container
            db: Optional database instance
            vectorstore: Optional vectorstore instance
            context_manager: Optional context manager instance
            llm_chain: Optional LLM chain instance
            indexer: Optional indexer instance
            session_manager: Optional session manager instance
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

        # Create persistence directory per config
        self.persist_dir = self.working_dir / self.config.persist_directory
        self.persist_dir.mkdir(exist_ok=True, parents=True)

        # Save config to persistence directory
        saved_config_path = self.persist_dir / "config.json"
        self.config.to_file(str(saved_config_path))

        # Initialize components using dependency injection
        if container:
            # Use container to resolve dependencies
            from docstra.core.container import Container

            self.container = container
            self.db = db or container.resolve(IDatabase)
            self.context_manager = context_manager or container.resolve(IContextManager)
            self.vectorstore = vectorstore or container.resolve(IVectorStore)
            self.llm_chain = llm_chain or container.resolve(ILLMChain)
            self.indexer = indexer or container.resolve(IIndexer)
            self.session_manager = session_manager or container.resolve(ISessionManager)
        else:
            # Initialize components manually
            from docstra.core.database import create_database
            from docstra.core.context import DocstraContextManager
            from docstra.core.indexer import DocstraIndexer
            from docstra.core.llm import DocstraLLMChain
            from docstra.core.session import DocstraSessionManager
            from docstra.core.vectorstore import create_vectorstore

            # Initialize the database
            db_path = self.persist_dir / "sessions.db"
            self.db = db or create_database(str(db_path))

            # Initialize context manager
            self.context_manager = context_manager or DocstraContextManager(
                working_dir=working_dir,
                config_path=config_path,
                log_level=log_level,
                log_file=log_file,
                config=config,
                logger=logger,
            )

            # Create vectorstore
            try:
                self.vectorstore = vectorstore or create_vectorstore(
                    persist_dir=self.persist_dir,
                    config=self.config,
                    logger=self.logger,
                )
            except Exception as e:
                self.logger.warning(f"Failed to create vectorstore: {str(e)}")
                self.vectorstore = None

            # Initialize LLM chain
            self.llm_chain = llm_chain or DocstraLLMChain(
                working_dir=working_dir,
                config_path=config_path,
                log_level=log_level,
                log_file=log_file,
                config=config,
                logger=logger,
                vectorstore=self.vectorstore,
                db=self.db,
                context_manager=self.context_manager,
            )

            # Initialize indexer
            self.indexer = indexer or DocstraIndexer(
                working_dir=working_dir,
                config_path=config_path,
                log_level=log_level,
                log_file=log_file,
                config=config,
                logger=logger,
                vectorstore=self.vectorstore,
            )

            # Initialize session manager
            self.session_manager = session_manager or DocstraSessionManager(
                working_dir=working_dir,
                config_path=config_path,
                log_level=log_level,
                log_file=log_file,
                config=config,
                logger=logger,
                db=self.db,
                vectorstore=self.vectorstore,
            )

    def _validate_config(self) -> None:
        """Validate service configuration.

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

    def create_session(self, name: Optional[str] = None) -> str:
        """Create a new session.

        Args:
            name: Optional name for the session

        Returns:
            Session ID
        """
        return self.session_manager.create_session(name)

    def rename_session(self, session_id: str, name: str) -> None:
        """Rename a session.

        Args:
            session_id: Session ID
            name: New name for the session
        """
        self.session_manager.rename_session(session_id, name)

    # Add other service methods here
