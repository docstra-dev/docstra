"""Session management service for Docstra."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union, Any

from docstra.core.config import DocstraConfig
from docstra.core.base import BaseService
from docstra.core.interfaces import IDatabase, ILogger, ISessionManager, IVectorStore
from docstra.core.database import Database


class DocstraSession:
    """Represents a Docstra session with configuration and context."""

    def __init__(
        self,
        session_id: Optional[str] = None,
        config: Optional[DocstraConfig] = None,
        created_at: Optional[str] = None,
    ):
        """Initialize a new session.

        Args:
            session_id: Optional session ID (generated if not provided)
            config: Optional configuration (default used if not provided)
            created_at: Optional creation timestamp
        """
        from uuid import uuid4

        self.session_id = session_id or str(uuid4())
        self.config = config or DocstraConfig()
        self.created_at = created_at or datetime.now().isoformat()
        self.context_files = []
        self.messages = []
        self.name = None

    @classmethod
    def from_database(
        cls,
        session_id: str,
        created_at: str,
        config_json: str,
        name: Optional[str] = None,
    ) -> "DocstraSession":
        """Create a session from database records.

        Args:
            session_id: The session ID
            created_at: Creation timestamp
            config_json: JSON string of configuration
            name: Optional session name

        Returns:
            DocstraSession instance
        """
        config = DocstraConfig(**json.loads(config_json))
        session = cls(session_id=session_id, config=config, created_at=created_at)
        session.name = name
        return session

    def to_dict(self) -> Dict:
        """Convert session to dictionary.

        Returns:
            Dictionary representation of session
        """
        return {
            "session_id": self.session_id,
            "created_at": self.created_at,
            "config": self.config.__dict__,
            "name": self.name,
        }

    def add_user_message(self, message: str) -> None:
        """Add a user message to the session.

        Args:
            message: User message
        """
        self.messages.append({"role": "user", "content": message})

    def add_assistant_message(self, message: str) -> None:
        """Add an assistant message to the session.

        Args:
            message: Assistant message
        """
        self.messages.append({"role": "assistant", "content": message})

    def get_messages(self) -> List[Dict[str, str]]:
        """Get all messages in the session.

        Returns:
            List of message dictionaries
        """
        return self.messages


class DocstraSessionManager(BaseService, ISessionManager):
    """Service for managing Docstra sessions."""

    def __init__(
        self,
        working_dir: Optional[Union[str, Path]] = None,
        config_path: Optional[Union[str, Path]] = None,
        log_level: Optional[str] = None,
        log_file: Optional[str] = None,
        config: Optional[DocstraConfig] = None,
        logger: Optional[ILogger] = None,
        db: Optional[IDatabase] = None,
        vectorstore: Optional[IVectorStore] = None,
    ):
        """Initialize the session manager.

        Args:
            working_dir: Working directory containing the codebase
            config_path: Optional path to configuration file
            log_level: Optional logging level override
            log_file: Optional log file path
            config: Optional configuration instance
            logger: Optional logger instance
            db: Optional database instance
            vectorstore: Optional vectorstore instance
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
        self.db = db
        self.vectorstore = vectorstore

        # Create persistence directory
        self.persist_dir = self.working_dir / self.config.persist_directory
        self.persist_dir.mkdir(exist_ok=True, parents=True)

        # Initialize database if not provided
        if not self.db:
            from docstra.core.database import create_database

            db_path = self.persist_dir / "sessions.db"
            self.db = create_database(str(db_path))

        # Initialize sessions
        self.sessions = {}
        self._load_sessions()

    def _load_sessions(self) -> None:
        """Load sessions from database."""
        try:
            # Create sessions table if it doesn't exist
            self.db.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    created_at TEXT,
                    config TEXT,
                    name TEXT
                )
                """
            )

            # Check if name column exists
            cursor = self.db.execute("PRAGMA table_info(sessions)")
            columns = {row["name"] for row in cursor.fetchall()}
            if "name" not in columns:
                self.db.execute("ALTER TABLE sessions ADD COLUMN name TEXT")

            # Load sessions
            rows = self.db.fetch_all(
                "SELECT session_id, created_at, config, name FROM sessions"
            )
            for row in rows:
                session = DocstraSession.from_database(
                    session_id=row["session_id"],
                    created_at=row["created_at"],
                    config_json=row["config"],
                    name=row.get("name"),  # Use get() to handle missing name
                )
                self.sessions[session.session_id] = session

            self.logger.debug(f"Loaded {len(self.sessions)} sessions from database")
        except Exception as e:
            self.logger.error(f"Error loading sessions: {str(e)}")

    def create_session(self, name: Optional[str] = None) -> str:
        """Create a new session.

        Args:
            name: Optional name for the session

        Returns:
            Session ID
        """
        # Create session
        session = DocstraSession(config=self.config)
        session.name = name

        # Save to database
        self.db.execute(
            """
            INSERT INTO sessions (session_id, created_at, config, name)
            VALUES (:session_id, :created_at, :config, :name)
            """,
            {
                "session_id": session.session_id,
                "created_at": session.created_at,
                "config": json.dumps(session.config.__dict__),
                "name": name,
            },
        )

        # Add to memory
        self.sessions[session.session_id] = session

        return session.session_id

    def get_session(self, session_id: str) -> Optional[DocstraSession]:
        """Get a session by ID.

        Args:
            session_id: Session ID

        Returns:
            Session object or None if not found
        """
        return self.sessions.get(session_id)

    def update_session_config(self, session_id: str, config: DocstraConfig) -> bool:
        """Update a session's configuration.

        Args:
            session_id: Session ID
            config: New configuration

        Returns:
            True if successful, False otherwise
        """
        # Check if session exists
        session = self.get_session(session_id)
        if not session:
            return False

        # Update session
        session.config = config

        # Update database
        self.db.execute(
            """
            UPDATE sessions
            SET config = :config
            WHERE session_id = :session_id
            """,
            {
                "session_id": session_id,
                "config": json.dumps(config.__dict__),
            },
        )

        return True

    def rename_session(self, session_id: str, name: str) -> bool:
        """Rename a session.

        Args:
            session_id: Session ID
            name: New name for the session

        Returns:
            True if successful, False otherwise
        """
        # Check if session exists
        session = self.get_session(session_id)
        if not session:
            return False

        # Update session
        session.name = name

        # Update database
        self.db.execute(
            """
            UPDATE sessions
            SET name = :name
            WHERE session_id = :session_id
            """,
            {
                "session_id": session_id,
                "name": name,
            },
        )

        return True

    def delete_session(self, session_id: str) -> bool:
        """Delete a session.

        Args:
            session_id: Session ID

        Returns:
            True if successful, False otherwise
        """
        # Check if session exists
        if session_id not in self.sessions:
            return False

        # Delete from database
        self.db.execute(
            """
            DELETE FROM sessions
            WHERE session_id = :session_id
            """,
            {"session_id": session_id},
        )

        # Delete from memory
        del self.sessions[session_id]

        return True

    def get_all_sessions(self) -> List[DocstraSession]:
        """Get all sessions.

        Returns:
            List of session objects
        """
        return list(self.sessions.values())
