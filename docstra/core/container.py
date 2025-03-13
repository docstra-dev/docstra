"""Container module for dependency injection."""

from typing import Dict, Any, Optional, Type, TypeVar, Callable

from docstra.core.logger import DocstraLogger
from docstra.core.interfaces import (
    IContextManager,
    IDatabase,
    IDocstraService,
    IIndexer,
    ILLMChain,
    ILogger,
    IRetriever,
    ISessionManager,
    IVectorStore,
)

T = TypeVar("T")


class Container:
    """Container for dependency injection."""

    def __init__(self):
        """Initialize the container."""
        self._services: Dict[Type, Any] = {}
        self._factories: Dict[Type, Callable] = {}

    def register(self, service_type: Type[T], implementation: T) -> None:
        """Register a service implementation.

        Args:
            service_type: The service interface type
            implementation: The service implementation
        """
        self._services[service_type] = implementation

    def register_factory(
        self, service_type: Type[T], factory: Callable[..., T]
    ) -> None:
        """Register a service factory.

        Args:
            service_type: The service interface type
            factory: The factory function
        """
        self._factories[service_type] = factory

    def resolve(self, service_type: Type[T]) -> T:
        """Resolve a service instance.

        Args:
            service_type: The service interface type

        Returns:
            The service instance

        Raises:
            KeyError: If the service is not registered
        """
        if service_type in self._services:
            return self._services[service_type]

        if service_type in self._factories:
            return self._factories[service_type]()

        raise KeyError(f"Service {service_type.__name__} not registered")


def create_container(
    working_dir: Optional[str] = None,
    config_path: Optional[str] = None,
    log_level: Optional[str] = None,
    log_file: Optional[str] = None,
) -> Container:
    """Create a container with default services.

    Args:
        working_dir: Working directory
        config_path: Path to configuration file
        log_level: Logging level
        log_file: Path to log file

    Returns:
        Container instance
    """
    from docstra.core.context import DocstraContextManager
    from docstra.core.indexer import DocstraIndexer
    from docstra.core.llm import DocstraLLMChain
    from docstra.core.retriever import DocstraRetriever
    from docstra.core.session import DocstraSessionManager
    from docstra.core.service import DocstraService
    from docstra.core.loader import DocstraLoader
    from docstra.core.vectorstore import create_vectorstore

    container = Container()

    # Register services
    container.register_factory(ILogger, lambda: DocstraLogger(log_level=log_level, log_file=log_file))
    container.register_factory(
        IContextManager,
        lambda: DocstraContextManager(
            working_dir=working_dir,
            config_path=config_path,
            log_level=log_level,
            log_file=log_file,
        ),
    )
    container.register_factory(
        IIndexer,
        lambda: DocstraIndexer(
            working_dir=working_dir,
            config_path=config_path,
            log_level=log_level,
            log_file=log_file,
        ),
    )
    container.register_factory(
        ILLMChain,
        lambda: DocstraLLMChain(
            working_dir=working_dir,
            config_path=config_path,
            log_level=log_level,
            log_file=log_file,
        ),
    )
    container.register_factory(
        IRetriever,
        lambda: DocstraRetriever(
            working_dir=working_dir,
            config_path=config_path,
            log_level=log_level,
            log_file=log_file,
        ),
    )
    container.register_factory(
        ISessionManager,
        lambda: DocstraSessionManager(
            working_dir=working_dir,
            config_path=config_path,
            log_level=log_level,
            log_file=log_file,
        ),
    )
    container.register_factory(
        IDocstraService,
        lambda: DocstraService(
            working_dir=working_dir,
            config_path=config_path,
            log_level=log_level,
            log_file=log_file,
        ),
    )

    return container
