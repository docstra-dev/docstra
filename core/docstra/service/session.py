"""Session management for Docstra."""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from docstra.session import DocstraSession
from docstra.config import DocstraConfig


class DocstraSessionManager:
    """Manages chat sessions for Docstra."""

    def __init__(
        self,
        working_dir: Path,
        config: DocstraConfig,
        db: "Database",  # type: ignore
        retriever: Optional["DocstraRetriever"] = None,  # type: ignore
        context_manager: Optional["DocstraContextManager"] = None,  # type: ignore
        logger: Optional[logging.Logger] = None,
    ):
        """Initialize the session manager.

        Args:
            working_dir: The project working directory
            config: Docstra configuration
            db: Database instance
            retriever: Optional DocstraRetriever instance for context management
            context_manager: Optional context manager for formatting
            logger: Optional logger instance
        """
        self.working_dir = working_dir
        self.config = config
        self.db = db
        self.retriever = retriever
        self.context_manager = context_manager
        self.logger = logger or logging.getLogger("docstra.sessions")

        # Sessions storage
        self.sessions: Dict[str, DocstraSession] = {}

        # Load existing sessions
        self.logger.debug("Loading existing sessions...")
        self.load_sessions()

    def create_session(self) -> str:
        """Create a new session and return its ID."""
        # Create session object with new UUID
        session = DocstraSession(config=self.config)
        session_id = session.session_id

        try:
            # Initialize empty context files list
            session.context_files = []

            # Clear any specific context in the retriever
            if self.retriever and hasattr(
                self.retriever, "clear_specific_context_files"
            ):
                self.retriever.clear_specific_context_files()
                self.logger.debug("Cleared retriever specific context for new session")

            # Prepare config data to save
            config_json = json.dumps(
                {
                    key: value
                    for key, value in session.config.__dict__.items()
                    if not key.startswith("_") and not callable(value)
                }
            )

            # Store session in database
            self.db.save_session(
                session_id, session.created_at.isoformat(), config_json
            )

            # Store in memory
            self.sessions[session_id] = session

            self.logger.info(
                f"Created session: {session_id}, Total sessions: {len(self.sessions)}"
            )
            return session_id
        except Exception as e:
            self.logger.error(f"Error creating session: {str(e)}")
            raise

    def get_session(self, session_id: str) -> Optional[DocstraSession]:
        """Get a session by ID."""
        # Allow partial ID matches if the ID is at least 6 characters
        if len(session_id) >= 6 and session_id not in self.sessions:
            matching_sessions = [
                sid for sid in self.sessions.keys() if sid.startswith(session_id)
            ]
            if len(matching_sessions) == 1:
                session_id = matching_sessions[0]

        # First check memory cache
        if session_id in self.sessions:
            self.logger.debug(f"Found session in memory: {session_id}")
            return self.sessions[session_id]

        try:
            # Get session data from database
            session_data = self.db.get_session(session_id)

            if not session_data:
                # Try partial ID match in database
                if len(session_id) >= 6:
                    all_sessions = self.db.get_all_sessions()
                    matching_sessions = [
                        sid for sid in all_sessions if sid.startswith(session_id)
                    ]
                    if len(matching_sessions) == 1:
                        session_data = self.db.get_session(matching_sessions[0])
                        session_id = matching_sessions[0]

            if not session_data:
                self.logger.warning(f"Session not found: {session_id}")
                return None

            created_at, config_json = session_data

            # Get messages for this session
            messages = self.db.get_messages(session_id)

            # Create session object from database data
            session = DocstraSession.from_database(
                session_id=session_id,
                created_at=created_at,
                config_json=config_json,
                messages=messages,
            )

            # Initialize empty context_files if not already set
            if not hasattr(session, "context_files"):
                session.context_files = []

            # Update retriever with context files if this is the active session
            if self.retriever and hasattr(self.retriever, "set_specific_context_files"):
                # This ensures the retriever's context is updated when a session is loaded
                if session.context_files:
                    self.retriever.set_specific_context_files(session.context_files)
                    self.logger.debug(
                        f"Set retriever context for loaded session {session_id} with files: {session.context_files}"
                    )
                else:
                    self.retriever.clear_specific_context_files()

            # Store in memory
            self.sessions[session_id] = session

            self.logger.info(
                f"Loaded session from database: {session_id} with {len(session.messages)} messages"
            )
            return session
        except Exception as e:
            self.logger.error(f"Error loading session: {str(e)}")
            return None

    def load_sessions(self) -> None:
        """Load existing sessions from the database."""
        try:
            # Get all session IDs
            session_ids = self.db.get_all_sessions()

            # Only load a few sessions initially (to avoid memory pressure)
            # More sessions will be loaded on-demand when accessed
            for session_id in session_ids[:5]:  # Only load the 5 most recent sessions
                # This will load the session into memory
                self.get_session(session_id)

            self.logger.info(
                f"Found {len(session_ids)} sessions in database, loaded {min(5, len(session_ids))}"
            )
        except Exception as e:
            self.logger.error(f"Error loading sessions: {str(e)}")

    def add_message(self, session_id: str, role: str, content: str) -> None:
        """Add a message to a session and save to database."""
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        try:
            # Add message to session object
            message = session.add_message(role, content)

            # Save to database
            self.db.save_message(
                session_id=session_id,
                role=role,
                content=content,
                timestamp=message["timestamp"],
            )

            self.logger.debug(f"Added {role} message to session {session_id}")
        except Exception as e:
            self.logger.error(f"Error adding message: {str(e)}")
            raise

    def add_context(
        self,
        session_id: str,
        file_path: str,
        content: Optional[str] = None,
        selection_range: Optional[Dict] = None,
    ) -> None:
        """Add additional context to a session.

        Args:
            session_id: The session ID to add context to
            file_path: Path to the file to add
            content: Optional file content (if not provided, read from file)
            selection_range: Optional selection range to focus on
        """
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        # Format context message using context manager
        if self.context_manager:
            context_message = self.context_manager.add_context_to_session(
                file_path=file_path, content=content, selection_range=selection_range
            )
        else:
            # Fallback if context manager not available
            context_message = f"Additional context from file {file_path}"
            if content:
                context_message += f":\n```\n{content}\n```"

        # Keep track of file in session for reference
        if not hasattr(session, "context_files"):
            session.context_files = []
        if file_path not in session.context_files:
            session.context_files.append(file_path)

            # Update retriever to add this file to specific context
            if self.retriever and hasattr(self.retriever, "set_specific_context_files"):
                self.retriever.set_specific_context_files(session.context_files)
                self.logger.debug(
                    f"Updated retriever context for session {session_id} with files: {session.context_files}"
                )

        # Add the formatted context message to the session
        self.add_message(session_id, "system", context_message)

    def get_context_files(self, session_id: str) -> List[str]:
        """Get the list of files that have been added to a session's context."""
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        if not hasattr(session, "context_files"):
            session.context_files = []

        return session.context_files

    def remove_context_file(self, session_id: str, file_path: str) -> bool:
        """Remove a file from a session's context list.

        Args:
            session_id: The session ID to remove context from
            file_path: Path to the file to remove

        Returns:
            True if the file was in the context and removed, False otherwise
        """
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        if not hasattr(session, "context_files"):
            session.context_files = []

        if file_path in session.context_files:
            # Remove from session's context files list
            session.context_files.remove(file_path)

            # Update retriever's specific context files
            if self.retriever and hasattr(self.retriever, "set_specific_context_files"):
                if session.context_files:
                    # Update with remaining files
                    self.retriever.set_specific_context_files(session.context_files)
                else:
                    # Clear specific context if no files remain
                    self.retriever.clear_specific_context_files()

                self.logger.debug(
                    f"Updated retriever context for session {session_id} after removing {file_path}"
                )

            # Add a system message indicating the file was removed
            self.add_message(
                session_id, "system", f"File removed from context: {file_path}"
            )
            return True
        return False

    def rename_session(self, session_id: str, new_name: str) -> bool:
        """Rename a session by storing a name in its config.

        Args:
            session_id: ID of the session to rename
            new_name: New name for the session

        Returns:
            True if successful, False otherwise
        """
        try:
            session = self.get_session(session_id)
            if not session:
                return False

            # Add name to session config
            session.config.name = new_name

            # Update in database
            config_json = json.dumps(
                {
                    key: value
                    for key, value in session.config.__dict__.items()
                    if not key.startswith("_") and not callable(value)
                }
            )

            # For now, just re-save the session
            self.db.save_session(
                session_id, session.created_at.isoformat(), config_json
            )

            self.logger.info(f"Renamed session {session_id} to '{new_name}'")
            return True
        except Exception as e:
            self.logger.error(f"Error renaming session: {str(e)}")
            return False

    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        try:
            # Delete from database
            deleted = self.db.delete_session(session_id)

            # Remove from memory if it was there
            if session_id in self.sessions:
                del self.sessions[session_id]

            if deleted:
                self.logger.info(f"Deleted session: {session_id}")
            else:
                self.logger.warning(f"Session {session_id} not found for deletion")

            return deleted
        except Exception as e:
            self.logger.error(f"Error deleting session: {str(e)}")
            return False

    def get_all_session_ids(self) -> List[str]:
        """Get all session IDs from the database."""
        try:
            return self.db.get_all_sessions()
        except Exception as e:
            self.logger.error(f"Error retrieving session IDs: {str(e)}")
            return []

    def get_all_sessions(self) -> List[DocstraSession]:
        """Get all sessions as DocstraSession objects."""
        try:
            session_ids = self.db.get_all_sessions()
            sessions = []

            for session_id in session_ids:
                session = self.get_session(session_id)
                if session:
                    sessions.append(session)

            return sessions
        except Exception as e:
            self.logger.error(f"Error retrieving sessions: {str(e)}")
            return []
