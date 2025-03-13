"""Core module for Docstra."""

from docstra.core.interfaces import (
    IDocstraService,
    IIndexer,
    ILLMChain,
    IDatabase,
    IContextManager,
    ILoader,
    ILogger,
    IRetriever,
    ISessionManager,
    IVectorStore,
)
from docstra.core.factory import create_service
from docstra.core.container import Container, create_container

__all__ = [
    "IDocstraService",
    "create_service",
    "IIndexer",
    "ILLMChain",
    "IDatabase",
    "IContextManager",
    "ILoader",
    "ILogger",
    "IRetriever",
    "ISessionManager",
    "IVectorStore",
    "Container",
    "create_container",
]
