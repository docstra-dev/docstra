"""Factory module for creating Docstra components."""

from typing import Optional

from docstra.core.interfaces import (
    IContextManager,
    IDocstraService,
    IIndexer,
    ILLMChain,
    ILogger,
    IRetriever,
    ISessionManager,
)
from docstra.core.context import DocstraContextManager
from docstra.core.indexer import DocstraIndexer
from docstra.core.llm import DocstraLLMChain
from docstra.core.retriever import DocstraRetriever
from docstra.core.session import DocstraSessionManager


def create_context_manager(
    working_dir: str,
    config_path: Optional[str] = None,
    log_level: Optional[str] = None,
    log_file: Optional[str] = None,
    config: Optional[dict] = None,
    logger: Optional[ILogger] = None,
) -> IContextManager:
    """Create a context manager instance."""
    return DocstraContextManager(
        working_dir=working_dir,
        config_path=config_path,
        log_level=log_level,
        log_file=log_file,
        config=config,
        logger=logger,
    )


def create_indexer(
    working_dir: str,
    config_path: Optional[str] = None,
    log_level: Optional[str] = None,
    log_file: Optional[str] = None,
    config: Optional[dict] = None,
    logger: Optional[ILogger] = None,
) -> IIndexer:
    """Create an indexer instance."""
    return DocstraIndexer(
        working_dir=working_dir,
        config_path=config_path,
        log_level=log_level,
        log_file=log_file,
        config=config,
        logger=logger,
    )


def create_llm_chain(
    working_dir: str,
    config_path: Optional[str] = None,
    log_level: Optional[str] = None,
    log_file: Optional[str] = None,
    config: Optional[dict] = None,
    logger: Optional[ILogger] = None,
) -> ILLMChain:
    """Create an LLM chain instance."""
    return DocstraLLMChain(
        working_dir=working_dir,
        config_path=config_path,
        log_level=log_level,
        log_file=log_file,
        config=config,
        logger=logger,
    )


def create_retriever(
    working_dir: str,
    config_path: Optional[str] = None,
    log_level: Optional[str] = None,
    log_file: Optional[str] = None,
    config: Optional[dict] = None,
    logger: Optional[ILogger] = None,
) -> IRetriever:
    """Create a retriever instance."""
    return DocstraRetriever(
        working_dir=working_dir,
        config_path=config_path,
        log_level=log_level,
        log_file=log_file,
        config=config,
        logger=logger,
    )


def create_session_manager(
    working_dir: str,
    config_path: Optional[str] = None,
    log_level: Optional[str] = None,
    log_file: Optional[str] = None,
    config: Optional[dict] = None,
    logger: Optional[ILogger] = None,
) -> ISessionManager:
    """Create a session manager instance."""
    return DocstraSessionManager(
        working_dir=working_dir,
        config_path=config_path,
        log_level=log_level,
        log_file=log_file,
        config=config,
        logger=logger,
    )


def create_service(
    working_dir: str,
    config_path: Optional[str] = None,
    log_level: Optional[str] = None,
    log_file: Optional[str] = None,
    config: Optional[dict] = None,
    logger: Optional[ILogger] = None,
) -> IDocstraService:
    """Create a Docstra service instance."""
    from docstra.core.service import DocstraService
    from docstra.core.config import DocstraConfig

    # Convert dict config to DocstraConfig if needed
    config_obj = None
    if config is not None:
        if not isinstance(config, DocstraConfig):
            # Handle plain dictionary by converting to DocstraConfig
            config_obj = DocstraConfig(**config) if config else None
        else:
            config_obj = config

    return DocstraService(
        working_dir=working_dir,
        config_path=config_path,
        log_level=log_level,
        log_file=log_file,
        config=config_obj,
        logger=logger,
    )
