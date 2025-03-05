"""Context manager for handling code context in Docstra."""

import logging
from pathlib import Path
from typing import Dict, List, Optional

from langchain_core.documents import Document


class DocstraContextManager:
    """Manages code context formatting and extraction for Docstra."""

    def __init__(self, working_dir: Path, logger: Optional[logging.Logger] = None):
        """Initialize the context manager.

        Args:
            working_dir: The project working directory
            logger: Optional logger instance
        """
        self.working_dir = working_dir
        self.logger = logger or logging.getLogger("docstra.context")

    def format_context_with_links(self, documents: List[Document]) -> str:
        """Format retrieved documents with enhanced context and clickable links.

        Args:
            documents: List of document objects from retriever

        Returns:
            Formatted string with clickable links to files and code segments
        """
        from docstra.loader import locate_in_file

        formatted_docs = []

        for doc in documents:
            if hasattr(doc, "metadata") and "file_path" in doc.metadata:
                file_path = doc.metadata["file_path"]
                file_url = f"file://{self.working_dir}/{file_path}"

                # Get content
                content = doc.page_content if hasattr(doc, "page_content") else str(doc)

                # Get line range from metadata if available
                line_range = doc.metadata.get("line_range")
                # Handle the case where line_range is stored as a JSON string
                if isinstance(line_range, str):
                    try:
                        import json
                        line_range = json.loads(line_range)
                    except (json.JSONDecodeError, ValueError):
                        line_range = None

                # If no line range in metadata, try to locate content in file
                if not line_range:
                    abs_path = Path(
                        doc.metadata.get(
                            "absolute_path", str(self.working_dir / file_path)
                        )
                    )
                    line_range = locate_in_file(content, abs_path)

                # Format line info
                line_info = (
                    f"lines {line_range[0]}-{line_range[1]}" if line_range else ""
                )

                # Extract code units if available
                units = doc.metadata.get("units", [])
                unit_types = doc.metadata.get("unit_types", [])

                # Create unit description
                if units and unit_types:
                    # Combine unit names with their types
                    unit_descriptions = []
                    for i, unit in enumerate(units):
                        unit_type = unit_types[i] if i < len(unit_types) else "code"
                        unit_descriptions.append(f"{unit_type} `{unit}`")
                    unit_info = (
                        "Contains: " + ", ".join(unit_descriptions)
                        if unit_descriptions
                        else ""
                    )
                else:
                    unit_info = ""

                # Format content with line numbers
                lines = content.strip().split("\n")

                # Use detected line numbers if available
                if line_range:
                    start_line = line_range[0]
                    numbered_content = "\n".join(
                        f"{start_line+i:4d} | {line}" for i, line in enumerate(lines)
                    )
                else:
                    # Fall back to relative numbering
                    numbered_content = "\n".join(
                        f"{i+1:4d} | {line}" for i, line in enumerate(lines)
                    )

                # Create header with file link and line info
                header = f"From file [{file_path}]({file_url})"
                if line_info:
                    # Make the line number range also clickable with a specific line anchor
                    line_url = (
                        f"{file_url}#L{line_range[0]}" if line_range else file_url
                    )
                    header += f" ([{line_info}]({line_url}))"

                # Assemble the formatted document
                formatted_parts = [header]
                if unit_info:
                    formatted_parts.append(unit_info)
                formatted_parts.append(f"```\n{numbered_content}\n```")

                formatted_doc = "\n".join(formatted_parts)
                formatted_docs.append(formatted_doc)
            else:
                # Fallback formatting for documents without metadata
                content = doc.page_content if hasattr(doc, "page_content") else str(doc)
                lines = content.strip().split("\n")
                numbered_content = "\n".join(
                    f"{i+1:4d} | {line}" for i, line in enumerate(lines)
                )
                formatted_docs.append(f"```\n{numbered_content}\n```")

        return "\n\n".join(formatted_docs)

    def add_context_to_session(
        self,
        file_path: str,
        content: Optional[str] = None,
        selection_range: Optional[Dict] = None,
    ) -> str:
        """Format file context as a system message with clickable links.

        Args:
            file_path: Path to the file to add
            content: Optional file content (if not provided, read from file)
            selection_range: Optional selection range to focus on (dict with startLine and endLine)

        Returns:
            Formatted context message
        """
        # If content not provided, try to read from file
        if content is None and file_path:
            try:
                full_path = self.working_dir / file_path
                content = full_path.read_text(encoding="utf-8")
            except Exception as e:
                self.logger.error(f"Could not read file {file_path}: {str(e)}")
                return f"Error reading file {file_path}: {str(e)}"

        if not content:
            return "Empty content provided"

        # If selection range provided, extract that part of the content
        if selection_range and content:
            lines = content.split("\n")
            start_line = max(0, selection_range.get("startLine", 0))
            end_line = min(
                len(lines) - 1, selection_range.get("endLine", len(lines) - 1)
            )
            content = "\n".join(lines[start_line : end_line + 1])

        # Add clickable link to file
        file_url = f"file://{self.working_dir}/{file_path}"

        # Add line numbers to content for better readability
        lines = content.splitlines()
        numbered_content = "\n".join(
            f"{i+1:4d} | {line}" for i, line in enumerate(lines)
        )

        # Determine line range if selection_range is provided
        line_info = ""
        if selection_range:
            start_line = selection_range.get("startLine", 0) + 1  # Convert to 1-based
            end_line = selection_range.get("endLine", len(lines) - 1) + 1
            line_info = f"lines {start_line}-{end_line}"
            # Add anchor to URL for line jumping
            file_url = f"{file_url}#L{start_line}"

        # Create enhanced context message
        header = f"Additional context from file [{file_path}]({file_url})"
        if line_info:
            header += f" ({line_info})"

        context_message = f"{header}:\n```\n{numbered_content}\n```"
        return context_message
