from pathlib import Path
import sqlite3
import threading
import logging
import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Union
from abc import ABC, abstractmethod

from docstra.core.errors import DatabaseError


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
        self,
        file_path: str,
        last_modified: str,
        indexed_at: str,
        chunk_count: int,
        metadata_json: str = None,
        status: str = "INDEXED",
        priority: int = 0,
    ) -> None:
        """Save file indexing metadata to the database."""
        pass

    @abstractmethod
    def get_file_metadata(
        self, file_path: str = None, status: str = None
    ) -> Dict[str, Dict[str, Any]]:
        """Get metadata for indexed files with optional filtering."""
        pass

    @abstractmethod
    def delete_file_metadata(self, file_path: str) -> None:
        """Delete file metadata from the database."""
        pass

    @abstractmethod
    def update_file_status(
        self, file_path: str, status: str, error_message: str = None
    ) -> None:
        """Update the indexing status of a file."""
        pass

    @abstractmethod
    def record_file_access(self, file_path: str) -> None:
        """Record that a file was accessed (for tracking popularity)."""
        pass

    @abstractmethod
    def increment_file_access_count(self, file_path: str) -> None:
        """Increment the access count for a file."""
        pass

    @abstractmethod
    def save_file_dependency(
        self, source_file: str, target_file: str, relationship_type: str
    ) -> None:
        """Save a dependency relationship between files."""
        pass

    @abstractmethod
    def get_file_dependencies(
        self, file_path: str, relationship_type: str = None, as_source: bool = True
    ) -> List[Dict[str, str]]:
        """Get dependencies for a file (either imports or imported-by)."""
        pass

    @abstractmethod
    def save_session_context_file(self, session_id: str, file_path: str) -> None:
        """Save a context file for a session."""
        pass

    @abstractmethod
    def remove_session_context_file(self, session_id: str, file_path: str) -> bool:
        """Remove a context file from a session."""
        pass

    @abstractmethod
    def get_session_context_files(self, session_id: str) -> List[str]:
        """Get all context files for a session."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Close all database connections."""
        pass


class SQLiteDatabase(Database):
    """SQLite implementation of the Database interface."""

    def __init__(self, db_path: Path | str):
        """Initialize the SQLite database.

        Args:
            db_path: Path to the SQLite database file
        """
        self.logger = logging.getLogger("docstra.database")
        self.db_path = db_path
        self._connections = {}
        self._lock = threading.RLock()

        # Ensure directory exists
        os.makedirs(Path(db_path).parent, exist_ok=True)

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

        # Create index metadata table with enhanced tracking
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS index_metadata (
                file_path TEXT PRIMARY KEY,
                last_modified TEXT NOT NULL,
                last_indexed TEXT NOT NULL,
                chunk_count INTEGER DEFAULT 0,
                metadata_json TEXT,
                status TEXT DEFAULT 'INDEXED',
                priority INTEGER DEFAULT 0,
                access_count INTEGER DEFAULT 0,
                last_accessed TEXT,
                index_version INTEGER DEFAULT 1,
                error_message TEXT
            )
        """
        )

        # Create file dependencies table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS file_dependencies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_file TEXT NOT NULL,
                target_file TEXT NOT NULL,
                relationship_type TEXT NOT NULL,
                created_at TEXT NOT NULL,
                UNIQUE (source_file, target_file, relationship_type)
            )
        """
        )

        # Create session context files table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS session_context_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                file_path TEXT NOT NULL,
                added_at TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions (session_id) ON DELETE CASCADE,
                UNIQUE (session_id, file_path)
            )
        """
        )

        # Create indexes for better performance
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_session_context_files_session_id 
            ON session_context_files(session_id)
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_source_file 
            ON file_dependencies(source_file)
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_target_file 
            ON file_dependencies(target_file)
            """
        )

        # Enable foreign keys
        cursor.execute("PRAGMA foreign_keys = ON")

        # Commit changes
        conn.commit()
        self.logger.info(f"SQLite database schema initialized at {self.db_path}")

    def save_session(self, session_id: str, created_at: str, config: str) -> None:
        """Save a session to the database."""
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
            raise DatabaseError(
                f"Failed to save session {session_id}: {str(e)}", cause=e
            )

    def update_session_config(self, session_id: str, config: str) -> bool:
        """Update config for an existing session."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "UPDATE sessions SET config = ? WHERE session_id = ?",
                (config, session_id),
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
            raise DatabaseError(
                f"Failed to update config for session {session_id}: {str(e)}", cause=e
            )

    def get_session(self, session_id: str) -> Optional[Tuple[str, str]]:
        """Get a session from the database."""
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
            raise DatabaseError(
                f"Failed to retrieve session {session_id}: {str(e)}", cause=e
            )

    def get_all_sessions(self) -> List[str]:
        """Get all session IDs from the database."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT session_id FROM sessions ORDER BY created_at DESC")
            return [row["session_id"] for row in cursor.fetchall()]
        except sqlite3.Error as e:
            self.logger.error(f"Error retrieving sessions from database: {str(e)}")
            return []

    def delete_session(self, session_id: str) -> bool:
        """Delete a session from the database."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Due to ON DELETE CASCADE, this will also delete related messages and context files
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
        self,
        file_path: str,
        last_modified: str,
        indexed_at: str,
        chunk_count: int,
        metadata_json: str = None,
        status: str = "INDEXED",
        priority: int = 0,
    ) -> None:
        """Save file indexing metadata to the database."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Check if file already exists in database
            cursor.execute(
                "SELECT file_path FROM index_metadata WHERE file_path = ?", (file_path,)
            )
            exists = cursor.fetchone() is not None

            if exists:
                # Update existing record
                cursor.execute(
                    """
                    UPDATE index_metadata SET
                        last_modified = ?,
                        last_indexed = ?,
                        chunk_count = ?,
                        metadata_json = ?,
                        status = ?,
                        priority = ?,
                        index_version = index_version + 1
                    WHERE file_path = ?
                    """,
                    (
                        last_modified,
                        indexed_at,
                        chunk_count,
                        metadata_json,
                        status,
                        priority,
                        file_path,
                    ),
                )
            else:
                # Insert new record
                cursor.execute(
                    """
                    INSERT INTO index_metadata 
                        (file_path, last_modified, last_indexed, chunk_count, 
                         metadata_json, status, priority, index_version)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 1)
                    """,
                    (
                        file_path,
                        last_modified,
                        indexed_at,
                        chunk_count,
                        metadata_json,
                        status,
                        priority,
                    ),
                )

            conn.commit()
            self.logger.debug(f"Saved metadata for file {file_path} to database")
        except sqlite3.Error as e:
            self.logger.error(f"Error saving file metadata to database: {str(e)}")
            raise

    def get_file_metadata(
        self, file_path: str = None, status: str = None
    ) -> Union[Dict[str, Dict[str, Any]], Dict[str, Any]]:
        """Get metadata for indexed files with optional filtering."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            if file_path:
                # Get metadata for a specific file
                cursor.execute(
                    """
                    SELECT file_path, last_modified, last_indexed, chunk_count, 
                           metadata_json, status, priority, access_count, 
                           last_accessed, index_version, error_message
                    FROM index_metadata WHERE file_path = ?
                    """,
                    (file_path,),
                )
                row = cursor.fetchone()

                if not row:
                    return {}

                result = {
                    "last_modified": row["last_modified"],
                    "last_indexed": row["last_indexed"],
                    "chunk_count": row["chunk_count"],
                    "status": row["status"],
                    "priority": row["priority"],
                    "access_count": row["access_count"] or 0,
                    "last_accessed": row["last_accessed"],
                    "index_version": row["index_version"],
                    "error_message": row["error_message"],
                }

                # Add parsed metadata_json if available
                if row["metadata_json"]:
                    try:
                        metadata = json.loads(row["metadata_json"])
                        result.update(metadata)
                    except json.JSONDecodeError:
                        pass

                return result
            else:
                # Build query based on filters
                query = """
                    SELECT file_path, last_modified, last_indexed, chunk_count, 
                           metadata_json, status, priority, access_count, 
                           last_accessed, index_version, error_message
                    FROM index_metadata
                """
                params = []

                if status:
                    query += " WHERE status = ?"
                    params.append(status)

                cursor.execute(query, params)

                result = {}
                for row in cursor.fetchall():
                    file_data = {
                        "last_modified": row["last_modified"],
                        "last_indexed": row["last_indexed"],
                        "chunk_count": row["chunk_count"],
                        "status": row["status"],
                        "priority": row["priority"],
                        "access_count": row["access_count"] or 0,
                        "last_accessed": row["last_accessed"],
                        "index_version": row["index_version"],
                        "error_message": row["error_message"],
                    }

                    # Add parsed metadata_json if available
                    if row["metadata_json"]:
                        try:
                            metadata = json.loads(row["metadata_json"])
                            file_data.update(metadata)
                        except json.JSONDecodeError:
                            pass

                    result[row["file_path"]] = file_data

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

    def update_file_status(
        self, file_path: str, status: str, error_message: str = None
    ) -> None:
        """Update the indexing status of a file."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                UPDATE index_metadata 
                SET status = ?, error_message = ?
                WHERE file_path = ?
                """,
                (status, error_message, file_path),
            )
            conn.commit()
            self.logger.debug(f"Updated status for file {file_path} to {status}")
        except sqlite3.Error as e:
            self.logger.error(f"Error updating file status in database: {str(e)}")
            raise

    def record_file_access(self, file_path: str) -> None:
        """Record that a file was accessed (for tracking popularity)."""
        conn = self.get_connection()
        cursor = conn.cursor()
        now = datetime.now().isoformat()

        try:
            cursor.execute(
                """
                UPDATE index_metadata 
                SET access_count = COALESCE(access_count, 0) + 1, last_accessed = ?
                WHERE file_path = ?
                """,
                (now, file_path),
            )
            conn.commit()
            self.logger.debug(f"Recorded access for file {file_path}")
        except sqlite3.Error as e:
            self.logger.error(f"Error recording file access in database: {str(e)}")
            # Don't raise an exception for tracking failures

    def increment_file_access_count(self, file_path: str) -> None:
        """Increment the access count for a file.
        
        This method is kept for interface compatibility but simply calls record_file_access.
        
        Args:
            file_path: Path to the file
        """
        # Delegating to record_file_access as they do the same thing
        self.record_file_access(file_path)

    def save_file_dependency(
        self, source_file: str, target_file: str, relationship_type: str
    ) -> None:
        """Save a dependency relationship between files."""
        conn = self.get_connection()
        cursor = conn.cursor()
        now = datetime.now().isoformat()

        try:
            cursor.execute(
                """
                INSERT OR REPLACE INTO file_dependencies
                    (source_file, target_file, relationship_type, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (source_file, target_file, relationship_type, now),
            )
            conn.commit()
            self.logger.debug(
                f"Saved dependency: {source_file} {relationship_type} {target_file}"
            )
        except sqlite3.Error as e:
            self.logger.error(f"Error saving file dependency in database: {str(e)}")
            raise

    def get_file_dependencies(
        self, file_path: str, relationship_type: str = None, as_source: bool = True
    ) -> List[Dict[str, str]]:
        """Get dependencies for a file."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            query = """
                SELECT source_file, target_file, relationship_type, created_at
                FROM file_dependencies
                WHERE {} = ?
            """

            # Determine which field to match based on direction
            match_field = "source_file" if as_source else "target_file"
            query = query.format(match_field)

            params = [file_path]

            # Add relationship type filter if provided
            if relationship_type:
                query += " AND relationship_type = ?"
                params.append(relationship_type)

            cursor.execute(query, params)

            result = []
            for row in cursor.fetchall():
                result.append(
                    {
                        "source_file": row["source_file"],
                        "target_file": row["target_file"],
                        "relationship_type": row["relationship_type"],
                        "created_at": row["created_at"],
                    }
                )

            return result
        except sqlite3.Error as e:
            self.logger.error(
                f"Error retrieving file dependencies from database: {str(e)}"
            )
            return []

    def save_session_context_file(self, session_id: str, file_path: str) -> None:
        """Save a context file for a session."""
        conn = self.get_connection()
        cursor = conn.cursor()
        timestamp = datetime.now().isoformat()

        try:
            cursor.execute(
                """
                INSERT OR REPLACE INTO session_context_files
                    (session_id, file_path, added_at)
                VALUES (?, ?, ?)
                """,
                (session_id, file_path, timestamp),
            )
            conn.commit()
            self.logger.debug(
                f"Saved context file {file_path} for session {session_id}"
            )
        except sqlite3.Error as e:
            self.logger.error(f"Error saving session context file: {str(e)}")
            raise

    def remove_session_context_file(self, session_id: str, file_path: str) -> bool:
        """Remove a context file from a session."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                DELETE FROM session_context_files
                WHERE session_id = ? AND file_path = ?
                """,
                (session_id, file_path),
            )
            conn.commit()
            deleted = cursor.rowcount > 0
            if deleted:
                self.logger.debug(
                    f"Removed context file {file_path} from session {session_id}"
                )
            return deleted
        except sqlite3.Error as e:
            self.logger.error(f"Error removing session context file: {str(e)}")
            return False

    def get_session_context_files(self, session_id: str) -> List[str]:
        """Get all context files for a session."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                SELECT file_path FROM session_context_files
                WHERE session_id = ?
                ORDER BY added_at
                """,
                (session_id,),
            )
            file_paths = [row["file_path"] for row in cursor.fetchall()]
            self.logger.debug(
                f"Retrieved {len(file_paths)} context files for session {session_id}"
            )
            return file_paths
        except sqlite3.Error as e:
            self.logger.error(f"Error retrieving session context files: {str(e)}")
            return []

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

    def execute(
        self, query: str, parameters: Optional[Tuple[Any, ...]] = None
    ) -> sqlite3.Cursor:
        """Execute a SQL query.

        Args:
            query: SQL query to execute
            parameters: Optional query parameters

        Returns:
            SQLite cursor
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            if parameters:
                cursor.execute(query, parameters)
            else:
                cursor.execute(query)
            conn.commit()
            return cursor
        except sqlite3.Error as e:
            self.logger.error(f"Error executing query: {str(e)}")
            raise DatabaseError(f"Error executing query: {str(e)}")

    def fetch_all(
        self, query: str, parameters: Optional[Tuple[Any, ...]] = None
    ) -> List[Dict[str, Any]]:
        """Execute a SQL query and fetch all results.

        Args:
            query: SQL query to execute
            parameters: Optional query parameters

        Returns:
            List of dictionaries containing the results
        """
        cursor = self.execute(query, parameters)
        try:
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            self.logger.error(f"Error fetching results: {str(e)}")
            raise DatabaseError(f"Error fetching results: {str(e)}")


# Factory function to create database based on config
def create_database(db_path: str) -> Database:
    """Create a database instance based on the given path."""
    return SQLiteDatabase(db_path)
