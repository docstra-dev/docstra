"""Shared API dependencies."""
from typing import Any, Callable, TypeVar, Awaitable, Optional

from fastapi import HTTPException, Request, Depends
from pydantic import BaseModel

from docstra.core import (
    IDocstraService,
    IIndexer,
    ILLMChain,
    ISessionManager,
    IContextManager,
    IRetriever,
    Container,
    create_container,
)

T = TypeVar('T')


def get_container() -> Container:
    """Get the dependency injection container.

    Returns:
        The dependency injection container.
    """
    return create_container()


def get_indexer(container: Container = Depends(get_container)) -> IIndexer:
    """Get the indexer service.

    Args:
        container: The dependency injection container.

    Returns:
        The indexer service.
    """
    return container.resolve(IIndexer)


def get_llm_chain(container: Container = Depends(get_container)) -> ILLMChain:
    """Get the LLM chain service.

    Args:
        container: The dependency injection container.

    Returns:
        The LLM chain service.
    """
    return container.resolve(ILLMChain)


def get_session_manager(
    container: Container = Depends(get_container),
) -> ISessionManager:
    """Get the session manager service.

    Args:
        container: The dependency injection container.

    Returns:
        The session manager service.
    """
    return container.resolve(ISessionManager)


def get_context_manager(
    container: Container = Depends(get_container),
) -> IContextManager:
    """Get the context manager service.

    Args:
        container: The dependency injection container.

    Returns:
        The context manager service.
    """
    return container.resolve(IContextManager)


def get_retriever(container: Container = Depends(get_container)) -> IRetriever:
    """Get the retriever service.

    Args:
        container: The dependency injection container.

    Returns:
        The retriever service.
    """
    return container.resolve(IRetriever)


def get_docstra_service(container: Container = Depends(get_container)) -> IDocstraService:
    """Get the Docstra service.

    Args:
        container: The dependency injection container.

    Returns:
        The Docstra service.
    """
    return container.resolve(IDocstraService)


def handle_exceptions(
    status_code: int = 500,
    error_message: str = "An error occurred"
) -> Callable[[Callable[..., Awaitable[T]]], Callable[..., Awaitable[T]]]:
    """Decorator to handle exceptions in endpoint handlers.

    Args:
        status_code: HTTP status code to return
        error_message: Error message prefix

    Returns:
        Decorator function
    """
    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                raise HTTPException(
                    status_code=status_code,
                    detail=f"{error_message}: {str(e)}"
                ) from e
        return wrapper
    return decorator