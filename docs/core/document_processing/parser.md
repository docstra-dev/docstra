---
language: documenttype.markdown
source_file: /Users/jorgenosberg/development/docstra/docs/core/document_processing/parser.md
summary: 'Parser Module

  ================'
title: parser

---

**Parser Module**
================

The parser module is responsible for parsing the source code of a Docstra application and extracting relevant information such as imports, classes, functions, and more.

**Classes**
-----------

### `CodeChunk`

Represents a chunk of code extracted from the parsed source code.

*   **Attributes:**
    *   `content`: The actual code content.
    *   `start_line`: The line number where this chunk starts.
    *   `end_line`: The line number where this chunk ends.
    *   `symbols`: A list of symbol names (e.g., function or class names) associated with this chunk.
    *   `chunk_type`: The type of code chunk (e.g., import, function definition).
    *   `parent_symbols`: A list of parent symbols.

### `Parser`

The main parser class responsible for parsing the source code and extracting relevant information.

*   **Attributes:**
    *   `node`: The current node being processed.
    *   `types`: A list of node types to collect (e.g., import statements, function definitions).
    *   `result`: A list to store collected nodes.

**Functions**
-------------

### `_extract_python_imports`

Extracts Python imports from a parsed tree.

*   **Parameters:**
    *   `node`: The root node.
*   **Returns:** A list of import statements.

### `_extract_python_classes`

Extracts Python class names from a parsed tree.

*   **Parameters:**
    *   `node`: The root node.
*   **Returns:** A list of class names.

### `_extract_python_functions`

Extracts Python function names from a parsed tree.

*   **Parameters:**
    *   `node`: The root node.
*   **Returns:** A list of function names.

### `_extract_js_imports`

Extracts JavaScript/TypeScript imports from a parsed tree.

*   **Parameters:**
    *   `node`: The root node.
*   **Returns:** A list of import statements.

### `_extract_js_classes`

Extracts JavaScript/TypeScript class names from a parsed tree.

*   **Parameters:**
    *   `node`: The root node.
*   **Returns:** A list of class names.

### `_extract_js_functions`

Extracts JavaScript/TypeScript function names from a parsed tree.

*   **Parameters:**
    *   `node`: The root node.
*   **Returns:** A list of function names.

**Usage Examples**
-----------------

```python
# Create a parser instance
parser = Parser()

# Parse the source code and extract imports
imports = parser._extract_python_imports(node)

# Parse the source code and extract classes
classes = parser._extract_python_classes(node)

# Parse the source code and extract functions
functions = parser._extract_python_functions(node)
```

**Important Dependencies**
-------------------------

The parser module depends on the `tree_sitter` library for parsing the source code.

**Notes**
-------

*   The parser module assumes that the input source code is in a format compatible with the `tree_sitter` library.
*   The parser module may not work correctly for all edge cases or invalid input.


## Source Code

```documenttype.markdown
---
language: documenttype.python
source_file: /Users/jorgenosberg/development/docstra/docstra/core/document_processing/parser.py
summary: 'Parser Module

  ================'
title: parser

---

**Parser Module**
================

Overview
--------

The `parser` module is a core component of the Docstra framework, responsible for parsing and extracting relevant information from documents. This module provides language-specific extractors for various document types, including Python, JavaScript/TypeScript, and others.

**Classes**
---------

### `DocumentProcessor`

Represents a processor that extracts information from a parsed document.

#### Attributes

*   `language`: The language of the document being processed.
*   `extractor`: An instance of a language-specific extractor class.

#### Methods

*   `process_document(document)`: Processes a given document and returns extracted information.
*   `_get_extractor()`: Returns an instance of a language-specific extractor class based on the `language` attribute.

### `LanguageExtractor`

Base class for language-specific extractors.

#### Attributes

*   `language`: The language being processed.

#### Methods

*   `extract(document)`: Extracts relevant information from a given document.
*   `_get_class()`: Returns an instance of a language-specific extractor class based on the `language` attribute.

**Functions**
-------------

### `extract_python_imports`

Extracts Python import statements from a parsed document.

#### Parameters

*   `node`: The root node of the parsed document.

#### Return Value

A list of extracted import statements as strings.

#### Example Usage
```python
import parser

document = ...  # Load or create a parsed document
extracted_imports = parser.extract_python_imports(document)
print(extracted_imports)  # Output: ['import module1', 'from module2 import function']
```

### `extract_python_classes`

Extracts Python class names from a parsed document.

#### Parameters

*   `node`: The root node of the parsed document.

#### Return Value

A list of extracted class names as strings.

#### Example Usage
```python
import parser

document = ...  # Load or create a parsed document
extracted_classes = parser.extract_python_classes(document)
print(extracted_classes)  # Output: ['Class1', 'Class2']
```

### `extract_js_imports`

Extracts JavaScript/TypeScript import statements from a parsed document.

#### Parameters

*   `node`: The root node of the parsed document.

#### Return Value

A list of extracted import statements as strings.

#### Example Usage
```python
import parser

document = ...  # Load or create a parsed document
extracted_imports = parser.extract_js_imports(document)
print(extracted_imports)  # Output: ['import module1', 'from module2 import function']
```

### `extract_js_classes`

Extracts JavaScript/TypeScript class names from a parsed document.

#### Parameters

*   `node`: The root node of the parsed document.

#### Return Value

A list of extracted class names as strings.

#### Example Usage
```python
import parser

document = ...  # Load or create a parsed document
extracted_classes = parser.extract_js_classes(document)
print(extracted_classes)  # Output: ['Class1', 'Class2']
```

### `extract_js_functions`

Extracts JavaScript/TypeScript function names from a parsed document.

#### Parameters

*   `node`: The root node of the parsed document.

#### Return Value

A list of extracted function names as strings.

#### Example Usage
```python
import parser

document = ...  # Load or create a parsed document
extracted_functions = parser.extract_js_functions(document)
print(extracted_functions)  # Output: ['function1', 'function2']
```

**Important Dependencies**
-------------------------

The `parser` module depends on the following modules:

*   `docstra.core.document`: Provides the base class for documents.
*   `docstra.core.parser`: Provides language-specific parser classes.

**Notes**
------

*   The `extractor` attribute of the `DocumentProcessor` class is an instance of a language-specific extractor class. This class should be initialized with the correct language code to extract relevant information from the document.
*   The `_get_extractor()` method returns an instance of a language-specific extractor class based on the `language` attribute of the `DocumentProcessor` class.
*   The `extract()` method is responsible for extracting relevant information from a given document. This method should be implemented by the language-specific extractor classes to provide the actual extraction logic.
*   The `_get_class()` method returns an instance of a language-specific extractor class based on the `language` attribute of the `LanguageExtractor` base class.


## Source Code

```documenttype.python
# File: ./docstra/core/document_processing/parser.py
"""
Code parser using Tree-sitter for extracting structure and metadata from code files.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Dict, List, Optional

import tree_sitter
from tree_sitter import Language, Parser, Tree
from tree_sitter_language_pack import get_binding, get_language, get_parser

from docstra.core.document_processing.document import (
    CodeChunk,
    Document,
    DocumentMetadata,
    DocumentType,
)


class CodeParser:
    """Parser for code files using Tree-sitter."""

    # Language to parser mapping
    LANGUAGES: Dict[DocumentType, str] = {
        DocumentType.PYTHON: "python",
        DocumentType.JAVASCRIPT: "javascript",
        DocumentType.TYPESCRIPT: "typescript",
        DocumentType.JAVA: "java",
        DocumentType.GO: "go",
        DocumentType.RUST: "rust",
        DocumentType.CPP: "cpp",
        DocumentType.C: "c",
        DocumentType.CSHARP: "c_sharp",
        DocumentType.PHP: "php",
        DocumentType.RUBY: "ruby",
    }

    def __init__(self, languages_dir: Optional[str] = None):
        """Initialize the parser with Tree-sitter languages.

        Args:
            languages_dir: Directory containing Tree-sitter language libraries.
                If None, will attempt to download and build languages.
        """
        self._parsers: Dict[DocumentType, Parser] = {}
        self._languages: Dict[DocumentType, Language] = {}

        # Check which languages are available in the language pack
        self._available_languages = set()
        try:
            for lang_name in self.LANGUAGES.values():
                try:
                    # Check if we can get this language
                    get_language(lang_name)
                    self._available_languages.add(lang_name)
                except Exception:
                    # Language not available in the pack
                    pass
        except Exception as e:
            print(f"Warning: tree_sitter_language_pack not fully accessible: {str(e)}")

    def parse_document(self, document: Document) -> Document:
        """Parse a document to extract structure and metadata.

        Args:
            document: The document to parse

        Returns:
            The document with updated metadata and chunks
        """
        # Get parser for this document's language
        parser = self._get_parser_for_language(document.metadata.language)

        if not parser:
            # Skip parsing for unsupported languages
            return document

        # Parse the document
        tree = parser.parse(bytes(document.content, "utf-8"))

        # Extract metadata and chunks
        metadata = self._extract_metadata(tree, document.metadata)
        chunks = self._extract_chunks(tree, document.content)

        # Update the document
        document.metadata = metadata
        document.chunks = chunks

        return document

    def _get_parser_for_language(self, doc_type: DocumentType) -> Optional[Parser]:
        """Get a parser for the specified language type.

        Args:
            doc_type: Document type to get parser for

        Returns:
            Parser for the language, or None if not available
        """
        # Return cached parser if available
        if doc_type in self._parsers:
            return self._parsers[doc_type]

        # Get language name from mapping
        lang_name = self.LANGUAGES.get(doc_type)
        if not lang_name or lang_name not in self._available_languages:
            return None

        try:
            # Get parser from language pack
            parser = get_parser(lang_name)

            # Cache the parser and language for future use
            self._parsers[doc_type] = parser
            self._languages[doc_type] = get_language(lang_name)

            return parser
        except Exception as e:
            print(f"Error loading parser for {lang_name}: {str(e)}")
            return None

    def _extract_metadata(
        self, tree: Tree, metadata: DocumentMetadata
    ) -> DocumentMetadata:
        """Extract metadata from a parsed tree.

        Args:
            tree: The parsed tree
            metadata: The existing metadata to update

        Returns:
            Updated metadata
        """
        root_node = tree.root_node

        # Extract imports, classes, and functions based on language
        if metadata.language == DocumentType.PYTHON:
            metadata.imports = self._extract_python_imports(root_node)
            metadata.classes = self._extract_python_classes(root_node)
            metadata.functions = self._extract_python_functions(root_node)
            metadata.symbols = self._build_symbol_table(
                root_node, ["class_definition", "function_definition"]
            )

        elif metadata.language in [DocumentType.JAVASCRIPT, DocumentType.TYPESCRIPT]:
            metadata.imports = self._extract_js_imports(root_node)
            metadata.classes = self._extract_js_classes(root_node)
            metadata.functions = self._extract_js_functions(root_node)
            metadata.symbols = self._build_symbol_table(
                root_node,
                ["class_declaration", "function_declaration", "method_definition"],
            )

        # Add more language-specific extractors as needed

        return metadata

    def _extract_chunks(self, tree: Tree, content: str) -> List[CodeChunk]:
        """Extract code chunks from a parsed tree.

        Args:
            tree: The parsed tree
            content: The document content

        Returns:
            List of code chunks
        """
        chunks: List[CodeChunk] = []
        root_node = tree.root_node

        # Find chunking points (functions, classes, etc.)
        chunking_nodes = []
        self._collect_nodes_by_type(
            root_node,
            [
                "function_definition",
                "class_definition",
                "method_definition",
                "function_declaration",
                "class_declaration",
            ],
            chunking_nodes,
        )

        # Create chunks from nodes
        for node in chunking_nodes:
            chunk_content = content[node.start_byte : node.end_byte]
            start_line = node.start_point[0] + 1  # Tree-sitter is 0-indexed
            end_line = node.end_point[0] + 1

            # Determine chunk type and name
            chunk_type = node.type.replace("_definition", "").replace(
                "_declaration", ""
            )
            name_node = self._find_name_node(node)
            symbols = [name_node.text.decode("utf-8")] if name_node else []

            # Find parent symbols
            parent_symbols = self._find_parent_symbols(node)

            chunks.append(
                CodeChunk(
                    content=chunk_content,
                    start_line=start_line,
                    end_line=end_line,
                    symbols=symbols,
                    chunk_type=chunk_type,
                    parent_symbols=parent_symbols,
                )
            )

        # If no chunks were found, create a single chunk for the whole document
        if not chunks:
            chunks.append(
                CodeChunk(
                    content=content,
                    start_line=1,
                    end_line=root_node.end_point[0] + 1,
                    symbols=[],
                    chunk_type="module",
                    parent_symbols=[],
                )
            )

        return chunks

    def _collect_nodes_by_type(
        self, node: tree_sitter.Node, types: List[str], result: List[tree_sitter.Node]
    ) -> None:
        """Collect nodes of specified types from a tree.

        Args:
            node: The current node
            types: Types of nodes to collect
            result: List to store collected nodes
        """
        if node.type in types:
            result.append(node)

        for child in node.children:
            self._collect_nodes_by_type(child, types, result)

    def _find_name_node(self, node: tree_sitter.Node) -> Optional[tree_sitter.Node]:
        """Find the name node of a definition or declaration.

        Args:
            node: The node to find the name for

        Returns:
            The name node if found, None otherwise
        """
        # Different node types have different patterns for where the name is
        if node.type == "function_definition":  # Python
            for child in node.children:
                if child.type == "identifier":
                    return child

        elif node.type == "class_definition":  # Python
            for child in node.children:
                if child.type == "identifier":
                    return child

        elif node.type in ["function_declaration", "class_declaration"]:  # JS/TS
            for child in node.children:
                if child.type == "identifier":
                    return child

        elif node.type == "method_definition":  # JS/TS
            for child in node.children:
                if child.type == "property_identifier":
                    return child

        return None

    def _find_parent_symbols(self, node: tree_sitter.Node) -> List[str]:
        """Find parent symbols of a node.

        Args:
            node: The node to find parents for

        Returns:
            List of parent symbol names
        """
        parents: List[str] = []
        current = node.parent

        while current:
            if current.type in ["class_definition", "class_declaration"]:
                name_node = self._find_name_node(current)
                if name_node:
                    parents.append(name_node.text.decode("utf-8"))

            current = current.parent

        return parents

    def _build_symbol_table(
        self, node: tree_sitter.Node, types: List[str]
    ) -> Dict[str, List[int]]:
        """Build a table mapping symbols to line numbers.

        Args:
            node: The root node
            types: Types of nodes to include

        Returns:
            Dictionary mapping symbol names to line numbers
        """
        symbols: Dict[str, List[int]] = {}
        nodes: List[tree_sitter.Node] = []

        self._collect_nodes_by_type(node, types, nodes)

        for node in nodes:
            name_node = self._find_name_node(node)
            if name_node:
                symbol_name = name_node.text.decode("utf-8")
                line_number = node.start_point[0] + 1

                if symbol_name in symbols:
                    symbols[symbol_name].append(line_number)
                else:
                    symbols[symbol_name] = [line_number]

        return symbols

    # Language-specific extractors

    def _extract_python_imports(self, node: tree_sitter.Node) -> List[str]:
        """Extract Python imports from a parsed tree.

        Args:
            node: The root node

        Returns:
            List of import statements
        """
        imports: List[str] = []
        import_nodes: List[tree_sitter.Node] = []

        self._collect_nodes_by_type(
            node, ["import_statement", "import_from_statement"], import_nodes
        )

        for import_node in import_nodes:
            imports.append(import_node.text.decode("utf-8").strip())

        return imports

    def _extract_python_classes(self, node: tree_sitter.Node) -> List[str]:
        """Extract Python class names from a parsed tree.

        Args:
            node: The root node

        Returns:
            List of class names
        """
        classes: List[str] = []
        class_nodes: List[tree_sitter.Node] = []

        self._collect_nodes_by_type(node, ["class_definition"], class_nodes)

        for class_node in class_nodes:
            name_node = self._find_name_node(class_node)
            if name_node:
                classes.append(name_node.text.decode("utf-8"))

        return classes

    def _extract_python_functions(self, node: tree_sitter.Node) -> List[str]:
        """Extract Python function names from a parsed tree.

        Args:
            node: The root node

        Returns:
            List of function names
        """
        functions: List[str] = []
        function_nodes: List[tree_sitter.Node] = []

        self._collect_nodes_by_type(node, ["function_definition"], function_nodes)

        for function_node in function_nodes:
            name_node = self._find_name_node(function_node)
            if name_node:
                functions.append(name_node.text.decode("utf-8"))

        return functions

    def _extract_js_imports(self, node: tree_sitter.Node) -> List[str]:
        """Extract JavaScript/TypeScript imports from a parsed tree.

        Args:
            node: The root node

        Returns:
            List of import statements
        """
        imports: List[str] = []
        import_nodes: List[tree_sitter.Node] = []

        self._collect_nodes_by_type(node, ["import_statement"], import_nodes)

        for import_node in import_nodes:
            imports.append(import_node.text.decode("utf-8").strip())

        return imports

    def _extract_js_classes(self, node: tree_sitter.Node) -> List[str]:
        """Extract JavaScript/TypeScript class names from a parsed tree.

        Args:
            node: The root node

        Returns:
            List of class names
        """
        classes: List[str] = []
        class_nodes: List[tree_sitter.Node] = []

        self._collect_nodes_by_type(node, ["class_declaration"], class_nodes)

        for class_node in class_nodes:
            name_node = self._find_name_node(class_node)
            if name_node:
                classes.append(name_node.text.decode("utf-8"))

        return classes

    def _extract_js_functions(self, node: tree_sitter.Node) -> List[str]:
        """Extract JavaScript/TypeScript function names from a parsed tree.

        Args:
            node: The root node

        Returns:
            List of function names
        """
        functions: List[str] = []
        function_nodes: List[tree_sitter.Node] = []

        self._collect_nodes_by_type(
            node, ["function_declaration", "method_definition"], function_nodes
        )

        for function_node in function_nodes:
            name_node = self._find_name_node(function_node)
            if name_node:
                functions.append(name_node.text.decode("utf-8"))

        return functions

```

```
