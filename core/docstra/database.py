import sqlite3
import threading
import logging
import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Union
from abc import ABC, abstractmethod

from docstra.errors import DatabaseError


class Database(ABC):
    """Abstract database interface for Docstra."""

    @abstractmethod
    def init_schema(self) -> None:
        """Initialize the database schema."""
        pass

    @abstractmethod
    def save_session(self, session_id: str, created_at: str, config: str) -> None:
        """Save a session to the database."""
        pass
    
    @abstractmethod
    def update_session_config(self, session_id: str, config: str) -> bool:
        """Update config for an existing session."""
        pass

    @abstractmethod
    def get_session(self, session_id: str) -> Optional[Tuple[str, str]]:
        """Get a session from the database."""
        pass

    @abstractmethod
    def get_all_sessions(self) -> List[str]:
        """Get all session IDs from the database."""
        pass

    @abstractmethod
    def delete_session(self, session_id: str) -> bool:
        """Delete a session from the database."""
        pass

    @abstractmethod
    def save_message(
        self, session_id: str, role: str, content: str, timestamp: str
    ) -> None:
        """Save a message to the database."""
        pass

    @abstractmethod
    def get_messages(self, session_id: str) -> List[Dict[str, str]]:
        """Get all messages for a session."""
        pass

    @abstractmethod
    def save_file_metadata(
        self, file_path: str, last_modified: str, indexed_at: str, chunk_count: int
    ) -> None:
        """Save file indexing metadata to the database."""
        pass

    @abstractmethod
    def get_file_metadata(self) -> Dict[str, Dict[str, str]]:
        """Get metadata for all indexed files."""
        pass

    @abstractmethod
    def delete_file_metadata(self, file_path: str) -> None:
        """Delete file metadata from the database."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Close all database connections."""
        pass


class SQLiteDatabase(Database):
    """SQLite implementation of the Database interface."""

    def __init__(self, db_path: str):
        """Initialize the SQLite database.

        Args:
            db_path: Path to the SQLite database file
        """
        self.logger = logging.getLogger("docstra.database")
        self.db_path = db_path
        self._connections = {}
        self._lock = threading.RLock()

        # Ensure directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        # Initialize schema
        self.init_schema()

    def get_connection(self) -> sqlite3.Connection:
        """Get a SQLite connection for the current thread.

        Returns:
            An open SQLite connection
        """
        thread_id = threading.get_ident()

        with self._lock:
            if thread_id not in self._connections:
                # Create a new connection for this thread
                self.logger.debug(
                    f"Creating new SQLite connection for thread {thread_id}"
                )
                conn = sqlite3.connect(self.db_path, check_same_thread=False)
                conn.execute("PRAGMA foreign_keys = ON")
                conn.row_factory = (
                    sqlite3.Row
                )  # Enable row_factory for dict-like access
                self._connections[thread_id] = conn

            return self._connections[thread_id]

    def init_schema(self) -> None:
        """Initialize the SQLite database schema."""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Create sessions table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                config TEXT NOT NULL
            )
        """
        )

        # Create messages table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions (session_id) ON DELETE CASCADE
            )
        """
        )

        # Create index metadata table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS index_metadata (
                file_path TEXT PRIMARY KEY,
                last_modified TEXT NOT NULL,
                last_indexed TEXT NOT NULL,
                chunk_count INTEGER DEFAULT 0
            )
        """
        )

        # Enable foreign keys
        cursor.execute("PRAGMA foreign_keys = ON")

        # Commit changes
        conn.commit()
        self.logger.info(f"SQLite database schema initialized at {self.db_path}")

    def save_session(self, session_id: str, created_at: str, config: str) -> None:
        """Save a session to the database.
        
        Args:
            session_id: Unique identifier for the session
            created_at: Timestamp when the session was created
            config: JSON string representing the session configuration
            
        Raises:
            DatabaseError: If there's an error saving the session
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT OR REPLACE INTO sessions (session_id, created_at, config) VALUES (?, ?, ?)",
                (session_id, created_at, config),
            )
            conn.commit()
            self.logger.debug(f"Saved session {session_id} to database")
        except sqlite3.Error as e:
            self.logger.error(f"Error saving session to database: {str(e)}")
            raise DatabaseError(f"Failed to save session {session_id}: {str(e)}", cause=e)
            
    def update_session_config(self, session_id: str, config: str) -> bool:
        """Update config for an existing session.
        
        Args:
            session_id: The session to update
            config: The new config JSON string
            
        Returns:
            True if successful, False if session not found
            
        Raises:
            DatabaseError: On database errors
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "UPDATE sessions SET config = ? WHERE session_id = ?",
                (config, session_id)
            )
            conn.commit()
            
            if cursor.rowcount > 0:
                self.logger.debug(f"Updated config for session {session_id}")
                return True
            else:
                self.logger.debug(f"Session {session_id} not found for config update")
                return False
        except sqlite3.Error as e:
            self.logger.error(f"Error updating session config: {str(e)}")
            raise DatabaseError(f"Failed to update config for session {session_id}: {str(e)}", cause=e)

    def get_session(self, session_id: str) -> Optional[Tuple[str, str]]:
        """Get a session from the database.
        
        Args:
            session_id: Unique identifier of the session to retrieve
            
        Returns:
            Tuple containing (created_at, config) if found, None otherwise
            
        Raises:
            DatabaseError: If there's an error accessing the database
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT created_at, config FROM sessions WHERE session_id = ?",
                (session_id,),
            )
            result = cursor.fetchone()

            if not result:
                self.logger.debug(f"Session {session_id} not found in database")
                return None

            return (result["created_at"], result["config"])
        except sqlite3.Error as e:
            self.logger.error(f"Error retrieving session from database: {str(e)}")
            raise DatabaseError(f"Failed to retrieve session {session_id}: {str(e)}", cause=e)

    def get_all_sessions(self) -> List[str]:
        """Get all session IDs from the database."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT session_id FROM sessions")
            return [row["session_id"] for row in cursor.fetchall()]
        except sqlite3.Error as e:
            self.logger.error(f"Error retrieving sessions from database: {str(e)}")
            return []

    def delete_session(self, session_id: str) -> bool:
        """Delete a session from the database."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
            deleted = cursor.rowcount > 0
            conn.commit()

            if deleted:
                self.logger.debug(f"Deleted session {session_id} from database")
            else:
                self.logger.debug(f"Session {session_id} not found for deletion")

            return deleted
        except sqlite3.Error as e:
            self.logger.error(f"Error deleting session from database: {str(e)}")
            return False

    def save_message(
        self, session_id: str, role: str, content: str, timestamp: str
    ) -> None:
        """Save a message to the database."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO messages (session_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
                (session_id, role, content, timestamp),
            )
            conn.commit()
            self.logger.debug(f"Saved message for session {session_id} to database")
        except sqlite3.Error as e:
            self.logger.error(f"Error saving message to database: {str(e)}")
            raise

    def get_messages(self, session_id: str) -> List[Dict[str, str]]:
        """Get all messages for a session."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT role, content, timestamp FROM messages WHERE session_id = ? ORDER BY timestamp",
                (session_id,),
            )
            messages = []
            for row in cursor.fetchall():
                messages.append(
                    {
                        "role": row["role"],
                        "content": row["content"],
                        "timestamp": row["timestamp"],
                    }
                )
            return messages
        except sqlite3.Error as e:
            self.logger.error(f"Error retrieving messages from database: {str(e)}")
            return []

    def save_file_metadata(
        self, file_path: str, last_modified: str, indexed_at: str, chunk_count: int
    ) -> None:
        """Save file indexing metadata to the database."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT OR REPLACE INTO index_metadata (file_path, last_modified, last_indexed, chunk_count) VALUES (?, ?, ?, ?)",
                (file_path, last_modified, indexed_at, chunk_count),
            )
            conn.commit()
            self.logger.debug(f"Saved metadata for file {file_path} to database")
        except sqlite3.Error as e:
            self.logger.error(f"Error saving file metadata to database: {str(e)}")
            raise

    def get_file_metadata(self) -> Dict[str, Dict[str, str]]:
        """Get metadata for all indexed files."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT file_path, last_modified, last_indexed, chunk_count FROM index_metadata"
            )
            result = {}
            for row in cursor.fetchall():
                result[row["file_path"]] = {
                    "last_modified": row["last_modified"],
                    "last_indexed": row["last_indexed"],
                    "chunk_count": row["chunk_count"],
                }
            return result
        except sqlite3.Error as e:
            self.logger.error(f"Error retrieving file metadata from database: {str(e)}")
            return {}

    def delete_file_metadata(self, file_path: str) -> None:
        """Delete file metadata from the database."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "DELETE FROM index_metadata WHERE file_path = ?", (file_path,)
            )
            conn.commit()
            self.logger.debug(f"Deleted metadata for file {file_path} from database")
        except sqlite3.Error as e:
            self.logger.error(f"Error deleting file metadata from database: {str(e)}")
            raise

    def close(self) -> None:
        """Close all database connections."""
        with self._lock:
            for conn in self._connections.values():
                try:
                    conn.close()
                except Exception as e:
                    self.logger.warning(f"Error closing database connection: {str(e)}")
            self._connections.clear()
        self.logger.debug("All database connections closed")

    def __del__(self):
        """Ensure connections are closed when the manager is deleted."""
        self.close()


# Factory function to create database based on config
def create_database(db_path: str) -> Database:
    """Create a database instance based on the given path."""
    return SQLiteDatabase(db_path)
