"""Error classes for Docstra."""

from typing import Optional


class DocstraError(Exception):
    """Base exception class for all Docstra errors."""

    def __init__(self, message: str, cause: Optional[Exception] = None):
        """Initialize the exception.

        Args:
            message: Human-readable error description
            cause: Original exception that caused this error, if any
        """
        self.message = message
        self.cause = cause
        super().__init__(message)


class ConfigError(DocstraError):
    """Exception raised when there's an issue with configuration."""


class DatabaseError(DocstraError):
    """Exception raised for database-related errors."""


class ModelProviderError(DocstraError):
    """Exception raised for errors in model providers."""


class EmbeddingError(DocstraError):
    """Exception raised for errors in embedding operations."""


class IndexingError(DocstraError):
    """Exception raised for errors in indexing operations."""


class SessionError(DocstraError):
    """Exception raised for session-related errors."""


class APIError(DocstraError):
    """Exception raised for API-related errors."""


class FileWatcherError(DocstraError):
    """Exception raised for file watcher errors."""


class ChunkingError(DocstraError):
    """Exception raised for errors in text chunking operations."""


class RetrievalError(DocstraError):
    """Exception raised for errors in retrieval operations."""


class AuthenticationError(DocstraError):
    """Exception raised for authentication errors."""


class NotFoundError(DocstraError):
    """Exception raised when a requested resource is not found."""


class ValidationError(DocstraError):
    """Exception raised for validation errors."""


class RequestError(DocstraError):
    """Exception raised for malformed or invalid requests."""