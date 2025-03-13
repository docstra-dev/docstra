"""Docstra: A tool for semantic code search and documentation."""

__version__ = "0.1.0"

# Expose error classes
from docstra.core.errors import (
    DocstraError,
    ConfigError,
    DatabaseError,
    ModelProviderError,
    EmbeddingError,
    IndexingError,
    SessionError,
    APIError,
    FileWatcherError,
    ChunkingError,
    RetrievalError,
    AuthenticationError,
    NotFoundError,
    ValidationError,
    RequestError,
)

# Import core components for direct API usage
from docstra.core.services import (
    ConfigurationService,
)
from docstra.core.config import DocstraConfig
from docstra.core.service import DocstraService
from docstra.core.session import DocstraSessionManager

__all__ = [
    "DocstraConfig",
    "DocstraService",
    "DocstraSessionManager",
]
