"""Docstra - LLM-powered code assistant."""

__version__ = "0.1.0"

# Expose error classes
from docstra.errors import (
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
from docstra.service import DocstraService
from docstra.config import DocstraConfig
from docstra.session import DocstraSession
