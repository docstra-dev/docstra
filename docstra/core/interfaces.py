"""Core interfaces for Docstra."""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, AsyncGenerator

from docstra.core.errors import DocstraError


class ILogger(ABC):
    """Interface for logging."""

    @abstractmethod
    def debug(self, message: str) -> None:
        """Log a debug message."""
        pass

    @abstractmethod
    def info(self, message: str) -> None:
        """Log an info message."""
        pass

    @abstractmethod
    def warning(self, message: str) -> None:
        """Log a warning message."""
        pass

    @abstractmethod
    def error(self, message: str) -> None:
        """Log an error message."""
        pass

    @abstractmethod
    def critical(self, message: str) -> None:
        """Log a critical message."""
        pass


class IVectorStore(ABC):
    """Interface for vector storage functionality."""

    @abstractmethod
    def add_documents(self, documents: List[Any]) -> None:
        """Add documents to the vector store.

        Args:
            documents: List of documents to add
        """
        pass

    @abstractmethod
    def get(self) -> Dict[str, Any]:
        """Get all documents from the vector store.

        Returns:
            Dictionary containing all documents
        """
        pass

    @abstractmethod
    def search(self, query: str, k: int = 5) -> List[Any]:
        """Search for documents similar to the query.

        Args:
            query: Query string
            k: Number of results to return

        Returns:
            List of similar documents
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear all documents from the vector store."""
        pass

    @abstractmethod
    def get_last_modified(self, file_path: str) -> float:
        """Get the last modified timestamp for a file.

        Args:
            file_path: Path to the file

        Returns:
            Last modified timestamp
        """
        pass


class IDatabase(ABC):
    """Interface for database functionality."""

    @abstractmethod
    def execute(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Execute a database query.

        Args:
            query: SQL query
            params: Query parameters

        Returns:
            Query result
        """
        pass

    @abstractmethod
    def fetch_one(
        self, query: str, params: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Fetch a single row from the database.

        Args:
            query: SQL query
            params: Query parameters

        Returns:
            Row as dictionary or None if not found
        """
        pass

    @abstractmethod
    def fetch_all(
        self, query: str, params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Fetch all rows from the database.

        Args:
            query: SQL query
            params: Query parameters

        Returns:
            List of rows as dictionaries
        """
        pass


class ILoader(ABC):
    """Interface for document loading functionality."""

    @abstractmethod
    def get_all_files(self) -> List[str]:
        """Get all files in the codebase.

        Returns:
            List of file paths
        """
        pass

    @abstractmethod
    def load_file(self, file_path: str) -> List[Any]:
        """Load a file and split it into documents.

        Args:
            file_path: Path to the file

        Returns:
            List of documents
        """
        pass

    @abstractmethod
    def load_and_split_file(self, file_path: str) -> List[Any]:
        """Load a file and split it into documents.

        Args:
            file_path: Path to the file

        Returns:
            List of documents
        """
        pass

    @abstractmethod
    def should_exclude(self, file_path: str) -> bool:
        """Check if a file should be excluded.

        Args:
            file_path: Path to the file

        Returns:
            True if the file should be excluded, False otherwise
        """
        pass


class IRetriever(ABC):
    """Interface for document retrieval functionality."""

    @abstractmethod
    async def get_relevant_documents(self, query: str, k: int = 5) -> List[Any]:
        """Get documents relevant to a query.

        Args:
            query: Query string
            k: Number of documents to retrieve

        Returns:
            List of relevant documents
        """
        pass


class IContextManager(ABC):
    """Interface for context management functionality."""

    @abstractmethod
    def get_context(
        self, query: str, chat_history: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        """Get context for a query.

        Args:
            query: Query string
            chat_history: Chat history

        Returns:
            List of context messages
        """
        pass


class ILLMChain(ABC):
    """Interface for LLM chain functionality."""

    @abstractmethod
    async def process_message(
        self, message: str, chat_history: List[Dict[str, str]]
    ) -> str:
        """Process a message and return the response.

        Args:
            message: User message
            chat_history: Chat history

        Returns:
            Assistant response
        """
        pass

    @abstractmethod
    async def process_message_stream(
        self, message: str, chat_history: List[Dict[str, str]]
    ) -> AsyncGenerator[str, None]:
        """Process a message and stream the response.

        Args:
            message: User message
            chat_history: Chat history

        Yields:
            Chunks of the assistant response
        """
        pass


class IIndexer(ABC):
    """Interface for indexing functionality."""

    @abstractmethod
    def update_index(self, force: bool = False) -> None:
        """Update the codebase index.

        Args:
            force: Whether to force reindexing of all files
        """
        pass

    @abstractmethod
    def get_indexed_files(self) -> List[str]:
        """Get list of indexed files.

        Returns:
            List of file paths that have been indexed
        """
        pass

    @abstractmethod
    def get_or_index_file(self, file_path: str) -> bool:
        """Get a file from the index or index it if not present.

        Args:
            file_path: Path to the file to get or index

        Returns:
            True if file was indexed or already in index, False otherwise
        """
        pass

    @abstractmethod
    def clear_index(self) -> None:
        """Clear the entire index."""
        pass


class ISessionManager(ABC):
    """Interface for session management functionality."""

    @abstractmethod
    def create_session(self, name: Optional[str] = None) -> str:
        """Create a new session.

        Args:
            name: Optional name for the session

        Returns:
            Session ID
        """
        pass

    @abstractmethod
    def get_session(self, session_id: str) -> Any:
        """Get a session by ID.

        Args:
            session_id: Session ID

        Returns:
            Session object
        """
        pass

    @abstractmethod
    def delete_session(self, session_id: str) -> bool:
        """Delete a session.

        Args:
            session_id: Session ID

        Returns:
            True if session was deleted, False otherwise
        """
        pass

    @abstractmethod
    def get_all_sessions(self) -> List[Any]:
        """Get all sessions.

        Returns:
            List of session objects
        """
        pass


class IDocstraService(ABC):
    """Interface for the main Docstra service."""

    @abstractmethod
    def create_session(self, name: Optional[str] = None) -> str:
        """Create a new session.

        Args:
            name: Optional name for the session

        Returns:
            Session ID
        """
        pass

    @abstractmethod
    def rename_session(self, session_id: str, name: str) -> None:
        """Rename a session.

        Args:
            session_id: Session ID
            name: New name for the session
        """
        pass
