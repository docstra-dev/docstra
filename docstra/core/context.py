"""Context management service for Docstra."""

from pathlib import Path
from typing import Dict, List, Optional, Union

from docstra.core.config import DocstraConfig
from docstra.core.base import BaseService
from docstra.core.interfaces import IContextManager, ILogger
from docstra.core.errors import ConfigError


class DocstraContextManager(BaseService, IContextManager):
    """Service for managing context for LLM interactions."""

    def __init__(
        self,
        working_dir: Optional[Union[str, Path]] = None,
        config_path: Optional[Union[str, Path]] = None,
        log_level: Optional[str] = None,
        log_file: Optional[str] = None,
        config: Optional[DocstraConfig] = None,
        logger: Optional[ILogger] = None,
    ):
        """Initialize the context manager.

        Args:
            working_dir: Working directory containing the codebase
            config_path: Optional path to configuration file
            log_level: Optional logging level override
            log_file: Optional log file path
            config: Optional configuration instance
            logger: Optional logger instance
        """
        # Initialize base service
        super().__init__(
            working_dir=working_dir,
            config_path=config_path,
            log_level=log_level,
            log_file=log_file,
            config=config,
            logger=logger,
        )

    def _validate_config(self) -> None:
        """Validate context manager configuration.

        Raises:
            ConfigError: If configuration is invalid
        """
        # Call base validation
        super()._validate_config()

        # Add any additional validation here
        if not self.config.max_context_chunks:
            raise ConfigError("Max context chunks not configured")

    def format_context_with_links(self, documents: List[Dict]) -> str:
        """Format a list of documents with clickable links.

        Args:
            documents: List of documents to format

        Returns:
            Formatted context string with clickable links
        """
        formatted_docs = []
        for doc in documents:
            file_path = doc.metadata.get("file_path", "unknown")
            line_start = doc.metadata.get("line_start", 1)
            line_end = doc.metadata.get("line_end", 1)

            # Create clickable link
            link = (
                f"vscode://file/{self.working_dir}/{file_path}:{line_start}:{line_end}"
            )

            # Format document with link
            formatted_docs.append(
                f"From [{file_path}:{line_start}-{line_end}]({link}):\n{doc.page_content}\n"
            )

        return "\n".join(formatted_docs)

    def format_context_for_llm(self, documents: List[Dict]) -> str:
        """Format a list of documents for LLM consumption.

        Args:
            documents: List of documents to format

        Returns:
            Formatted context string for LLM
        """
        formatted_docs = []
        for doc in documents:
            file_path = doc.metadata.get("file_path", "unknown")
            formatted_docs.append(f"From {file_path}:\n{doc.page_content}\n")

        return "\n".join(formatted_docs)

    def format_context_for_preview(self, documents: List[Dict]) -> str:
        """Format a list of documents for preview display.

        Args:
            documents: List of documents to format

        Returns:
            Formatted context string for preview
        """
        formatted_docs = []
        for doc in documents:
            file_path = doc.metadata.get("file_path", "unknown")
            line_start = doc.metadata.get("line_start", 1)
            line_end = doc.metadata.get("line_end", 1)
            formatted_docs.append(
                f"From {file_path} (lines {line_start}-{line_end}):\n{doc.page_content}\n"
            )

        return "\n".join(formatted_docs)

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
        # TODO: Implement context retrieval based on query and chat history
        # This should analyze query, understand intent, and fetch relevant context
        return []

    def extract_code_references(self, text: str) -> List[Dict[str, str]]:
        """Extract code references from text.

        Args:
            text: Text to extract references from

        Returns:
            List of code references
        """
        # TODO: Implement code reference extraction
        # This should parse text to find references to files, functions, classes
        return []

    def format_code_context(
        self, file_path: str, start_line: int, end_line: int
    ) -> str:
        """Format code context for display.

        Args:
            file_path: Path to the file
            start_line: Start line number
            end_line: End line number

        Returns:
            Formatted code context
        """
        try:
            # Read the file
            file_path_obj = Path(self.working_dir) / file_path
            if not file_path_obj.exists():
                return f"File not found: {file_path}"

            # Read the lines
            with open(file_path_obj, "r") as f:
                lines = f.readlines()

            # Extract the requested lines
            if start_line < 1:
                start_line = 1
            if end_line > len(lines):
                end_line = len(lines)

            # Format the code
            code_lines = lines[start_line - 1 : end_line]
            code = "".join(code_lines)

            return f"```{file_path}:{start_line}-{end_line}\n{code}\n```"
        except Exception as e:
            self.logger.error(f"Error formatting code context: {str(e)}")
            return f"Error reading file: {str(e)}"
