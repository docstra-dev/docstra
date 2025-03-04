from langchain_text_splitters import Language, RecursiveCharacterTextSplitter
import os


class CodeAwareChunker:
    """A code-aware text chunker that respects code structure.

    This chunker uses language-specific chunking strategies to ensure that
    code is split in a way that preserves function and class boundaries when possible.
    """

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 100):
        """Initialize the code chunker.

        Args:
            chunk_size: Target size of each chunk
            chunk_overlap: Overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        # Map file extensions to languages
        self.ext_to_language = {
            ".py": Language.PYTHON,
            ".js": Language.JS,
            ".ts": Language.TS,
            ".java": Language.JAVA,
            ".go": Language.GO,
            ".rs": Language.RUST,
            ".cpp": Language.CPP,
            ".c": Language.CPP,
            ".cs": Language.CSHARP,
        }

    def create_chunks(self, file_path: str, content: str) -> list:
        """Split code content into chunks, respecting code structure.

        Args:
            file_path: Path to the code file
            content: Code content to chunk

        Returns:
            List of document chunks
        """
        # Get file extension
        ext = os.path.splitext(file_path)[1].lower()

        # Default to generic chunking if language not supported
        language = self.ext_to_language.get(ext)

        # Create appropriate text splitter
        if language:
            splitter = RecursiveCharacterTextSplitter.from_language(
                language=language,
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
            )
        else:
            # Generic chunking for unsupported languages
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap
            )

        # Split the content
        return splitter.create_documents(
            [content], metadatas=[{"file_path": file_path, "language": language}]
        )

    def enhance_chunks_with_metadata(self, chunks, file_metadata):
        """Add file metadata to all chunks."""
        for chunk in chunks:
            chunk.metadata.update(file_metadata)
        return chunks
