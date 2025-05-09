# File: ./docstra/core/document_processing/chunking.py
"""
Chunking strategies for splitting code documents into smaller, meaningful chunks.
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from typing import List

from docstra.core.document_processing.document import CodeChunk, Document


class ChunkingStrategy(ABC):
    """Abstract base class for chunking strategies."""

    @abstractmethod
    def chunk_document(self, document: Document) -> Document:
        """Chunk a document according to the strategy.

        Args:
            document: The document to chunk

        Returns:
            The document with updated chunks
        """
        pass


class SyntaxAwareChunking(ChunkingStrategy):
    """Chunking strategy that uses syntax information from the parser.

    This strategy preserves the natural structure of the code by chunking
    at meaningful boundaries like function and class definitions.
    """

    def chunk_document(self, document: Document) -> Document:
        """Chunk a document according to syntax information.

        If the document has already been parsed and has chunks, this method
        will do nothing. Otherwise, it will create basic chunks.

        Args:
            document: The document to chunk

        Returns:
            The document with updated chunks
        """
        # If the document already has chunks from the parser, use those
        if document.chunks:
            return document

        # Otherwise, create a basic chunk for the whole document
        document.chunks = [
            CodeChunk(
                content=document.content,
                start_line=1,
                end_line=document.metadata.line_count,
                symbols=[],
                chunk_type="module",
                parent_symbols=[],
            )
        ]

        return document


class SlidingWindowChunking(ChunkingStrategy):
    """Chunking strategy that uses a sliding window over the document.

    This strategy is useful for long documents where syntax-aware chunking
    might produce chunks that are too large.
    """

    def __init__(self, chunk_size: int = 100, chunk_overlap: int = 20):
        """Initialize the sliding window chunking strategy.

        Args:
            chunk_size: Maximum size of each chunk (in lines)
            chunk_overlap: Number of lines of overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_document(self, document: Document) -> Document:
        """Chunk a document using a sliding window approach.

        Args:
            document: The document to chunk

        Returns:
            The document with updated chunks
        """
        # If the document is smaller than the chunk size, don't chunk it
        if document.metadata.line_count <= self.chunk_size:
            # Create a single chunk for the whole document if none exist
            if not document.chunks:
                document.chunks = [
                    CodeChunk(
                        content=document.content,
                        start_line=1,
                        end_line=document.metadata.line_count,
                        symbols=[],
                        chunk_type="module",
                        parent_symbols=[],
                    )
                ]
            return document

        # Split the document into lines
        lines = document.content.splitlines()

        # Create chunks with overlap
        chunks: List[CodeChunk] = []
        start_line = 1

        while start_line <= len(lines):
            end_line = min(start_line + self.chunk_size - 1, len(lines))
            chunk_content = "\n".join(lines[start_line - 1 : end_line])

            # Find symbols in this chunk
            symbols = self._extract_symbols_in_range(document, start_line, end_line)

            chunks.append(
                CodeChunk(
                    content=chunk_content,
                    start_line=start_line,
                    end_line=end_line,
                    symbols=symbols,
                    chunk_type="sliding_window",
                    parent_symbols=[],
                )
            )

            # Move the window forward, accounting for overlap
            start_line = end_line - self.chunk_overlap + 1

        document.chunks = chunks
        return document

    def _extract_symbols_in_range(
        self, document: Document, start_line: int, end_line: int
    ) -> List[str]:
        """Extract symbols that appear in a given line range.

        Args:
            document: The document containing symbols
            start_line: Start line of the range
            end_line: End line of the range

        Returns:
            List of symbols in the range
        """
        symbols: List[str] = []

        # If document has a symbol table, check which symbols are in this range
        for symbol, line_numbers in document.metadata.symbols.items():
            for line in line_numbers:
                if start_line <= line <= end_line:
                    symbols.append(symbol)
                    break

        return symbols


class SemanticChunking(ChunkingStrategy):
    """Chunking strategy that attempts to preserve semantic units.

    This strategy tries to keep related code together by analyzing imports,
    dependencies, and semantic relationships.
    """

    def __init__(self, max_chunk_size: int = 200):
        """Initialize the semantic chunking strategy.

        Args:
            max_chunk_size: Maximum size of each chunk (in lines)
        """
        self.max_chunk_size = max_chunk_size

    def chunk_document(self, document: Document) -> Document:
        """Chunk a document according to semantic boundaries.

        Args:
            document: The document to chunk

        Returns:
            The document with updated chunks
        """
        # If the document already has chunks from the parser, refine those
        if document.chunks:
            # Check if any chunks are too large and need further splitting
            refined_chunks: List[CodeChunk] = []

            for chunk in document.chunks:
                if chunk.end_line - chunk.start_line + 1 > self.max_chunk_size:
                    # Split large chunks
                    sub_chunks = self._split_large_chunk(chunk, document)
                    refined_chunks.extend(sub_chunks)
                else:
                    refined_chunks.append(chunk)

            document.chunks = refined_chunks
            return document

        # If no chunks exist, fall back to a basic semantic split
        return self._basic_semantic_split(document)

    def _split_large_chunk(
        self, chunk: CodeChunk, document: Document
    ) -> List[CodeChunk]:
        """Split a large chunk into smaller chunks.

        Args:
            chunk: The chunk to split
            document: The document containing the chunk

        Returns:
            List of smaller chunks
        """
        # Split the chunk content into lines
        lines = chunk.content.splitlines()

        # Try to find semantic boundaries within the chunk
        boundaries = self._find_semantic_boundaries(lines)

        if not boundaries or len(boundaries) <= 1:
            # Fall back to size-based splitting if no good boundaries found
            return self._size_based_split(chunk, self.max_chunk_size)

        # Create chunks based on identified boundaries
        sub_chunks: List[CodeChunk] = []
        last_boundary = 0

        for boundary in boundaries:
            if boundary - last_boundary >= 10:  # Minimum chunk size
                sub_content = "\n".join(lines[last_boundary:boundary])
                start_line = chunk.start_line + last_boundary
                end_line = chunk.start_line + boundary - 1

                sub_chunks.append(
                    CodeChunk(
                        content=sub_content,
                        start_line=start_line,
                        end_line=end_line,
                        symbols=chunk.symbols,  # Simplified - ideally would identify specific symbols
                        chunk_type=chunk.chunk_type,
                        parent_symbols=chunk.parent_symbols,
                    )
                )

                last_boundary = boundary

        # Add the final section if needed
        if last_boundary < len(lines):
            sub_content = "\n".join(lines[last_boundary:])
            start_line = chunk.start_line + last_boundary
            end_line = chunk.end_line

            sub_chunks.append(
                CodeChunk(
                    content=sub_content,
                    start_line=start_line,
                    end_line=end_line,
                    symbols=chunk.symbols,  # Simplified
                    chunk_type=chunk.chunk_type,
                    parent_symbols=chunk.parent_symbols,
                )
            )

        return sub_chunks

    def _find_semantic_boundaries(self, lines: List[str]) -> List[int]:
        """Find semantic boundaries within a list of code lines.

        Args:
            lines: Lines of code

        Returns:
            List of line indices that represent good semantic boundaries
        """
        boundaries: List[int] = []

        # Look for patterns that indicate semantic boundaries
        # This is a simplified approach - a real implementation would use more
        # sophisticated heuristics or NLP techniques

        # Track indentation levels
        current_indent = -1

        for i, line in enumerate(lines):
            if not line.strip():
                continue

            # Calculate indentation level
            indent = len(line) - len(line.lstrip())

            # Check for potential boundary conditions
            if indent == 0 and current_indent > 0:
                # End of an indented block
                boundaries.append(i)
            elif re.match(r"^\s*(def|class|if __name__ == ['\"]__main__['\"])", line):
                # Function/class definition or main block
                boundaries.append(i)
            elif re.match(r"^\s*#\s*", line) and len(line.strip()) > 2:
                # Comment line (potential section divider)
                boundaries.append(i)

            current_indent = indent

        return boundaries

    def _size_based_split(self, chunk: CodeChunk, max_size: int) -> List[CodeChunk]:
        """Split a chunk based on size.

        Args:
            chunk: The chunk to split
            max_size: Maximum chunk size in lines

        Returns:
            List of smaller chunks
        """
        lines = chunk.content.splitlines()
        sub_chunks: List[CodeChunk] = []

        for i in range(0, len(lines), max_size):
            end_idx = min(i + max_size, len(lines))
            sub_content = "\n".join(lines[i:end_idx])
            start_line = chunk.start_line + i
            end_line = chunk.start_line + end_idx - 1

            sub_chunks.append(
                CodeChunk(
                    content=sub_content,
                    start_line=start_line,
                    end_line=end_line,
                    symbols=[],  # Simplified
                    chunk_type="size_based",
                    parent_symbols=chunk.parent_symbols,
                )
            )

        return sub_chunks

    def _basic_semantic_split(self, document: Document) -> Document:
        """Perform a basic semantic split on a document without existing chunks.

        Args:
            document: The document to split

        Returns:
            Document with semantic chunks
        """
        lines = document.content.splitlines()
        chunks: List[CodeChunk] = []

        # Find all potential semantic boundaries
        boundaries = [0] + self._find_semantic_boundaries(lines) + [len(lines)]

        # Create chunks from boundaries
        for i in range(len(boundaries) - 1):
            start_idx = boundaries[i]
            end_idx = boundaries[i + 1]

            # Skip if the chunk would be too small
            if end_idx - start_idx < 5 and len(boundaries) > 2:
                continue

            sub_content = "\n".join(lines[start_idx:end_idx])
            start_line = start_idx + 1
            end_line = end_idx

            chunks.append(
                CodeChunk(
                    content=sub_content,
                    start_line=start_line,
                    end_line=end_line,
                    symbols=[],  # Would be populated in a more sophisticated implementation
                    chunk_type="semantic",
                    parent_symbols=[],
                )
            )

        document.chunks = chunks
        return document


class ChunkingPipeline:
    """Pipeline for applying multiple chunking strategies in sequence."""

    def __init__(self, strategies: List[ChunkingStrategy]):
        """Initialize the chunking pipeline.

        Args:
            strategies: List of chunking strategies to apply in order
        """
        self.strategies = strategies

    def process(self, document: Document) -> Document:
        """Process a document through the chunking pipeline.

        Args:
            document: The document to process

        Returns:
            The chunked document
        """
        result = document

        for strategy in self.strategies:
            result = strategy.chunk_document(result)

        return result
