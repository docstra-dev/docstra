# File: ./docstra/core/document_processing/extractor.py
"""
Metadata extraction from code documents.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import List, Optional

from docstra.core.document_processing.document import (
    Document,
    DocumentMetadata,
    DocumentType,
)


class MetadataExtractor:
    """Extract metadata from code documents."""

    def extract_metadata(self, document: Document) -> DocumentMetadata:
        """Extract metadata from a document.

        This method enhances the existing metadata with additional information
        extracted from the document content.

        Args:
            document: The document to extract metadata from

        Returns:
            Enhanced metadata
        """
        metadata = document.metadata

        # Extract additional metadata based on language
        if metadata.language == DocumentType.PYTHON:
            self._extract_python_metadata(document.content, metadata)
        elif metadata.language in [DocumentType.JAVASCRIPT, DocumentType.TYPESCRIPT]:
            self._extract_js_metadata(document.content, metadata)
        elif metadata.language == DocumentType.JAVA:
            self._extract_java_metadata(document.content, metadata)
        # Add more language-specific extractors as needed

        return metadata

    def _extract_python_metadata(
        self, content: str, metadata: DocumentMetadata
    ) -> None:
        """Extract metadata from Python code.

        Args:
            content: The document content
            metadata: The metadata to update
        """
        # Extract imports if not already present
        if not metadata.imports:
            import_pattern = r"(?:from\s+[\w.]+\s+import\s+(?:[\w.]+(?:\s+as\s+\w+)?(?:\s*,\s*[\w.]+(?:\s+as\s+\w+)?)*)|import\s+(?:[\w.]+(?:\s+as\s+\w+)?(?:\s*,\s*[\w.]+(?:\s+as\s+\w+)?)*))"
            metadata.imports = [
                m.group(0) for m in re.finditer(import_pattern, content)
            ]

        # Extract classes if not already present
        if not metadata.classes:
            class_pattern = r"class\s+(\w+)(?:\s*\([^)]*\))?\s*:"
            metadata.classes = [m.group(1) for m in re.finditer(class_pattern, content)]

        # Extract functions if not already present
        if not metadata.functions:
            func_pattern = r"def\s+(\w+)\s*\("
            metadata.functions = [
                m.group(1) for m in re.finditer(func_pattern, content)
            ]

        # Extract docstrings
        docstring_pattern = r'"""(.*?)"""'
        docstrings = re.findall(docstring_pattern, content, re.DOTALL)
        if docstrings:
            # Store the module docstring if present
            metadata.module_docstring = docstrings[0].strip()

    def _extract_js_metadata(self, content: str, metadata: DocumentMetadata) -> None:
        """Extract metadata from JavaScript/TypeScript code.

        Args:
            content: The document content
            metadata: The metadata to update
        """
        # Extract imports if not already present
        if not metadata.imports:
            import_pattern = r"(?:import\s+(?:[\w{},$\s*]+\s+from\s+)?['\"][\w./]+['\"])|(?:const|let|var)\s+\w+\s*=\s*require\(['\"][\w./]+['\"]\)"
            metadata.imports = [
                m.group(0) for m in re.finditer(import_pattern, content)
            ]

        # Extract classes if not already present
        if not metadata.classes:
            class_pattern = r"class\s+(\w+)"
            metadata.classes = [m.group(1) for m in re.finditer(class_pattern, content)]

        # Extract functions if not already present
        if not metadata.functions:
            # Match both regular functions and arrow functions
            func_pattern = r"(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:function|\([^)]*\)\s*=>))"

            for m in re.finditer(func_pattern, content):
                # Group 1 is for regular functions, group 2 is for variable assignments
                func_name = m.group(1) if m.group(1) else m.group(2)
                if func_name:
                    metadata.functions.append(func_name)

        # Extract JSDoc comments
        jsdoc_pattern = r"/\*\*(.*?)\*/"
        jsdocs = re.findall(jsdoc_pattern, content, re.DOTALL)
        if jsdocs:
            # Store the module JSDoc if present (assume first one is module doc)
            metadata.module_docstring = jsdocs[0].strip()

    def _extract_java_metadata(self, content: str, metadata: DocumentMetadata) -> None:
        """Extract metadata from Java code.

        Args:
            content: The document content
            metadata: The metadata to update
        """
        # Extract imports if not already present
        if not metadata.imports:
            import_pattern = r"import\s+[\w.]*(?:\.\*)?"
            metadata.imports = [
                m.group(0) for m in re.finditer(import_pattern, content)
            ]

        # Extract classes if not already present
        if not metadata.classes:
            class_pattern = (
                r"(?:public|private|protected)?\s*(?:abstract|final)?\s*class\s+(\w+)"
            )
            metadata.classes = [m.group(1) for m in re.finditer(class_pattern, content)]

            # Also look for interfaces
            interface_pattern = r"(?:public|private|protected)?\s*interface\s+(\w+)"
            metadata.classes.extend(
                [m.group(1) for m in re.finditer(interface_pattern, content)]
            )

        # Extract methods if not already present
        if not metadata.functions:
            method_pattern = r"(?:public|private|protected)?\s*(?:static|final|abstract)?\s*(?:[\w<>[\],\s]+)\s+(\w+)\s*\([^)]*\)"
            metadata.functions = [
                m.group(1) for m in re.finditer(method_pattern, content)
            ]

        # Extract JavaDoc comments
        javadoc_pattern = r"/\*\*(.*?)\*/"
        javadocs = re.findall(javadoc_pattern, content, re.DOTALL)
        if javadocs:
            # Store the class/interface JavaDoc if present (assume first one is class doc)
            metadata.module_docstring = javadocs[0].strip()


class DocumentProcessor:
    """Process documents to extract metadata and create structured representations."""

    def __init__(self):
        """Initialize the document processor."""
        self.extractor = MetadataExtractor()

    def process(self, filepath: str) -> Document:
        """Process a single file.

        Args:
            filepath: Path to the file to process

        Returns:
            Processed document
        """
        # Create document from file
        document = Document.from_file(filepath)

        # Extract enhanced metadata
        document.metadata = self.extractor.extract_metadata(document)

        return document

    def process_directory(
        self, directory: str, file_extensions: Optional[List[str]] = None
    ) -> List[Document]:
        """Process all files in a directory.

        Args:
            directory: Path to the directory to process
            file_extensions: Optional list of file extensions to include

        Returns:
            List of processed documents
        """
        path = Path(directory)
        if not path.is_dir():
            raise ValueError(f"{directory} is not a directory")

        documents: List[Document] = []

        # Process all files with given extensions recursively
        for file_path in path.rglob("*"):
            if file_path.is_file():
                # Skip if not in file_extensions
                if file_extensions and file_path.suffix.lower() not in file_extensions:
                    continue

                try:
                    document = self.process(str(file_path))
                    documents.append(document)
                except Exception as e:
                    print(f"Error processing {file_path}: {str(e)}")

        return documents
