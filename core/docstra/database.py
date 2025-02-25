import sqlite3
import threading


class DocstraDatabaseManager:
    """Manages database connections and operations for Docstra.

    This class provides a connection pool for SQLite, ensuring that
    connections remain open across different operations and threads.
    """

    def __init__(self, db_path: str):
        """Initialize the database manager.

        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self._connections = {}
        self._lock = threading.RLock()

    def get_connection(self) -> sqlite3.Connection:
        """Get a SQLite connection for the current thread.

        Returns:
            An open SQLite connection
        """
        thread_id = threading.get_ident()

        with self._lock:
            if thread_id not in self._connections:
                # Create a new connection for this thread
                conn = sqlite3.connect(self.db_path, check_same_thread=False)
                conn.execute("PRAGMA foreign_keys = ON")
                self._connections[thread_id] = conn

            return self._connections[thread_id]

    def close(self):
        """Close all open database connections."""
        with self._lock:
            for conn in self._connections.values():
                try:
                    conn.close()
                except Exception:
                    pass
            self._connections.clear()

    def __del__(self):
        """Ensure connections are closed when the manager is deleted."""
        self.close()
