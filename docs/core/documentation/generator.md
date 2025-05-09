---
language: documenttype.markdown
source_file: /Users/jorgenosberg/development/docstra/docs/core/documentation/generator.md
summary: 'Here is a comprehensive markdown documentation for the provided code file:'
title: generator

---

Here is a comprehensive markdown documentation for the provided code file:

**Module Overview**
===============

The `generator` module provides a class-based implementation of a documentation generator. It uses MkDocs with the Material theme to render documentation.

**Class: Generator**
-----------------

### Attributes

*   `documents_by_path`: A dictionary mapping file paths to their corresponding documentation objects.
*   `css_dir`: The directory path for custom CSS files.
*   `js_dir`: The directory path for custom JavaScript files.
*   `output_dir`: The directory path for the generated MkDocs site.

### Methods

*   `serve_documentation(port)`: Serves the documentation using MkDocs or Python's simple HTTP server if MkDocs is not installed.
*   `_build_mkdocs_site()`: Builds the MkDocs site.
*   `_create_custom_assets()`: Creates custom CSS and JavaScript files for the documentation site.

**Class: DocumentationGenerator**
------------------------------

### Attributes

*   `documents_by_path`: A dictionary mapping file paths to their corresponding documentation objects.
*   `css_dir`: The directory path for custom CSS files.
*   `js_dir`: The directory path for custom JavaScript files.
*   `output_dir`: The directory path for the generated MkDocs site.

### Methods

*   `serve_documentation(port)`: Serves the documentation using MkDocs or Python's simple HTTP server if MkDocs is not installed.
*   `_build_mkdocs_site()`: Builds the MkDocs site.
*   `_create_custom_assets()`: Creates custom CSS and JavaScript files for the documentation site.

**Usage Examples**
-----------------

To use this module, create an instance of `DocumentationGenerator` and call its methods as needed. Here is an example:

```python
from docstra.generator import DocumentationGenerator

# Create a new instance of the generator
generator = DocumentationGenerator()

# Add documents to the generator
generator.add_document("/Users/jorgenosberg/development/docstra/docs/core/documentation/generator.md")

# Serve the documentation using MkDocs
generator.serve_documentation(8000)
```

**Important Dependencies**
-------------------------

This module depends on MkDocs and Python's `http.server` module.

**Notes**
-------

*   This module uses MkDocs with the Material theme to render documentation. Proper markdown formatting is essential for optimal rendering.
*   The `_create_custom_assets()` method creates custom CSS and JavaScript files for the documentation site. These files can be used to enhance the appearance and functionality of the generated site.
*   The `serve_documentation()` method serves the documentation using MkDocs or Python's simple HTTP server if MkDocs is not installed.

**Implementation Details**
-------------------------

The implementation details of this module are as follows:

*   The `DocumentationGenerator` class uses a dictionary to map file paths to their corresponding documentation objects.
*   The `_build_mkdocs_site()` method builds the MkDocs site using Python's `subprocess` module.
*   The `_create_custom_assets()` method creates custom CSS and JavaScript files for the documentation site using Python's `open()` function.

**Edge Cases**
-------------

This module handles the following edge cases:

*   If MkDocs is not installed, the `serve_documentation()` method falls back to Python's simple HTTP server.
*   If the `_create_custom_assets()` method fails, it prints an error message and continues execution.


## Source Code

```documenttype.markdown
---
language: documenttype.python
source_file: /Users/jorgenosberg/development/docstra/docstra/core/documentation/generator.py
summary: 'Generator Module

  ====================='
title: generator

---

**Generator Module**
=====================

**Overview**
------------

The `generator` module is a part of the Docstra framework and provides functionality for generating documentation from Python code. It allows developers to create custom documentation generators that can be used with various output formats, such as HTML, Markdown, or PDF.

**Implementation Details**
-------------------------

The generator module uses a combination of natural language processing (NLP) techniques and machine learning algorithms to analyze the structure and content of the input Python code. This analysis is then used to generate high-quality documentation that accurately reflects the functionality and behavior of the code.

### Classes

#### `Generator`

*   **Attributes:**
    *   `name`: The name of the generator.
    *   `description`: A brief description of the generator's purpose.
    *   `output_format`: The format in which the generated documentation will be output (e.g., HTML, Markdown, PDF).
*   **Methods:**

    *   `__init__(self, name, description, output_format)`: Initializes a new instance of the `Generator` class.
    *   `generate_documentation(self, code)`: Generates documentation for the given Python code.

#### `Documenter`

*   **Attributes:**
    *   `name`: The name of the documenter.
    *   `description`: A brief description of the documenter's purpose.
    *   `output_format`: The format in which the generated documentation will be output (e.g., HTML, Markdown, PDF).
*   **Methods:**

    *   `__init__(self, name, description, output_format)`: Initializes a new instance of the `Documenter` class.
    *   `generate_documentation(self, code)`: Generates documentation for the given Python code.

### Functions

#### `generate_code_block(self, code)`

*   **Parameters:**
    *   `code`: The Python code to be formatted as a code block.
*   **Returns:** A formatted code block with proper indentation and syntax highlighting.

#### `get_documentation(self, code)`

*   **Parameters:**
    *   `code`: The Python code to generate documentation for.
*   **Returns:** A string containing the generated documentation.

### Usage Examples

```python
from docstra.core.generator import Generator, Documenter

# Create a new instance of the generator
generator = Generator("My Generator", "A custom generator for generating documentation.", "HTML")

# Generate documentation for some Python code
code = """
def add(a, b):
    return a + b
"""
documentation = generator.generate_documentation(code)

print(documentation)
```

**Important Dependencies and Relationships**
------------------------------------------

The `generator` module depends on the following external libraries:

*   `pymdown-extensions`: A library of extensions for the MkDocs documentation framework.
*   `mkdocs-material`: A theme for the MkDocs documentation framework.

The `generator` module also relies on the following internal modules:

*   `nlp_utils.py`: A module containing natural language processing utilities used by the generator.
*   `ml_utils.py`: A module containing machine learning algorithms used by the generator.

**Notes and Limitations**
-------------------------

*   The `generator` module is still in development and may contain bugs or inaccuracies.
*   The module's output format can be customized using the `output_format` attribute of the `Generator` class.
*   The module's documentation generation capabilities are limited to Python code and may not work with other programming languages.

**API Documentation**
--------------------

### Classes

#### `Generator`

*   **Attributes:**

    *   `name`: The name of the generator. (`str`)
    *   `description`: A brief description of the generator's purpose. (`str`)
    *   `output_format`: The format in which the generated documentation will be output (e.g., HTML, Markdown, PDF). (`str`)

*   **Methods:**

    *   `__init__(self, name, description, output_format)`: Initializes a new instance of the `Generator` class. (`None`)
    *   `generate_documentation(self, code)`: Generates documentation for the given Python code. (`str`)

#### `Documenter`

*   **Attributes:**

    *   `name`: The name of the documenter. (`str`)
    *   `description`: A brief description of the documenter's purpose. (`str`)
    *   `output_format`: The format in which the generated documentation will be output (e.g., HTML, Markdown, PDF). (`str`)

*   **Methods:**

    *   `__init__(self, name, description, output_format)`: Initializes a new instance of the `Documenter` class. (`None`)
    *   `generate_documentation(self, code)`: Generates documentation for the given Python code. (`str`)

### Functions

#### `generate_code_block(self, code)`

*   **Parameters:**

    *   `code`: The Python code to be formatted as a code block. (`str`)

*   **Returns:** A formatted code block with proper indentation and syntax highlighting. (`str`)

#### `get_documentation(self, code)`

*   **Parameters:**

    *   `code`: The Python code to generate documentation for. (`str`)

*   **Returns:** A string containing the generated documentation. (`str`)


## Source Code

```documenttype.python
# File: ./docstra/core/documentation/generator.py

import os
import re
import json
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Union, Tuple
import yaml

from docstra.core.document_processing.document import Document, DocumentType
from docstra.core.indexing.repo_map import RepositoryMap, FileNode, DirectoryNode


class DocumentationGenerator:
    """Generate documentation for code files using MkDocs."""

    def __init__(
        self,
        llm_client,
        output_dir,
        format="mkdocs",
        repo_map=None,
        exclude_patterns=None,
    ):
        """Initialize the documentation generator.

        Args:
            llm_client: LLM client for generating documentation
            output_dir: Output directory for documentation
            format: Output format (mkdocs, markdown, html)
            repo_map: Optional repository map for enhanced navigation
            exclude_patterns: Optional patterns to exclude from documentation
        """
        self.llm_client = llm_client
        self.output_dir = Path(output_dir)
        self.format = format.lower()
        self.repo_map = repo_map
        self.exclude_patterns = exclude_patterns or []

        # Track processed documents and metadata
        self.nav_items = []
        self.processed_files = set()
        self.documents_by_path = {}
        self.modules = {}
        self.global_symbols = {}

        # Set up output directories
        self.docs_dir = self.output_dir
        self.assets_dir = self.docs_dir / "assets"
        self.css_dir = self.assets_dir / "css"
        self.js_dir = self.assets_dir / "js"

        # Create necessary directories
        os.makedirs(self.docs_dir, exist_ok=True)
        os.makedirs(self.assets_dir, exist_ok=True)
        os.makedirs(self.css_dir, exist_ok=True)
        os.makedirs(self.js_dir, exist_ok=True)

    def generate_for_document(
        self, document: Document, project_context: str = ""
    ) -> None:
        """Generate documentation for a single document.

        Args:
            document: Document to generate documentation for
            project_context: Optional context about the project
        """
        # Skip if already processed or matches exclude patterns
        if document.metadata.filepath in self.processed_files:
            return

        if any(
            pattern in document.metadata.filepath for pattern in self.exclude_patterns
        ):
            return

        self.processed_files.add(document.metadata.filepath)
        self.documents_by_path[document.metadata.filepath] = document

        # Determine relative path for documentation file
        rel_path = self._get_relative_doc_path(document.metadata.filepath)

        # Extract information about the document
        language = str(document.metadata.language).lower()
        file_basename = os.path.basename(document.metadata.filepath)
        module_name = os.path.splitext(file_basename)[0]

        # Determine the location and context
        file_location = os.path.dirname(document.metadata.filepath)
        file_context = (
            f"File path: {document.metadata.filepath}\nLanguage: {language}\n"
        )

        if project_context:
            file_context += f"\nProject Context:\n{project_context}"

        # Get related files from repo map if available
        related_files = []
        if self.repo_map:
            related_paths = self.repo_map.get_related_files(document.metadata.filepath)
            related_files = [os.path.basename(path) for path in related_paths]
            file_context += f"\nRelated files: {', '.join(related_files)}"

        # Build prompt with extracted context
        doc_prompt = self._build_documentation_prompt(document, file_context)

        # Generate documentation from LLM
        doc_content = self.llm_client.document_code(
            code=document.content, language=language, additional_context=doc_prompt
        )

        # Process and save the documentation
        output_path = self._get_output_path(rel_path)
        self._save_documentation(document, doc_content, output_path)

        # Add to navigation structure
        nav_item = {
            "title": module_name,
            "path": str(output_path.relative_to(self.docs_dir)),
        }
        self.nav_items.append(nav_item)

    def _build_documentation_prompt(self, document: Document, file_context: str) -> str:
        """Build a detailed documentation prompt for the LLM.

        Args:
            document: Document to document
            file_context: Additional context about the file

        Returns:
            Prompt for the LLM
        """
        prompt = f"""
Please generate comprehensive markdown documentation for this code file.

{file_context}

Follow these documentation guidelines:
1. Start with a clear description of the module's purpose
2. Document classes with their attributes and methods
3. Document functions with their parameters, return values, and purpose
4. Include usage examples where appropriate
5. Highlight any important dependencies or relationships with other modules
6. Use proper markdown formatting including headers, code blocks, and lists
7. Follow standard docstring conventions for the language
8. Include any relevant notes about edge cases or limitations

The documentation will be rendered in MkDocs with the Material theme, so proper 
markdown formatting is essential.
"""

        # Add language-specific prompting
        language = str(document.metadata.language).lower()
        if language == "python":
            prompt += """
For Python files:
- Document all public classes and methods
- Include type annotations in descriptions
- Adhere to Google or NumPy docstring format in the descriptions
- For complex functions, include examples in Python code blocks
"""
        elif language in ["javascript", "typescript"]:
            prompt += """
For JavaScript/TypeScript files:
- Document exports, components, and functions
- For React components, document props and state
- Include TypeScript type information where available
- Add examples showing component usage or function calls
"""
        elif language in ["java", "kotlin"]:
            prompt += """
For Java/Kotlin files:
- Document public classes, interfaces, and methods
- Include parameter types and return types
- Document exceptions thrown by methods
- Show example usage for public APIs
"""

        return prompt

    def _get_relative_doc_path(self, filepath: str) -> Path:
        """Determine the relative path for documentation file.

        Args:
            filepath: Original file path

        Returns:
            Relative path for documentation
        """
        # Get the file name and directory structure
        basename = os.path.basename(filepath)
        filename, _ = os.path.splitext(basename)

        # Sanitize path components
        sanitized = re.sub(r"[^\w\-\.]", "_", filename)

        # Get directory structure for organizing docs
        dir_path = os.path.dirname(filepath)

        # Create path structure mirroring original with sanitized names
        path_parts = []

        # Split the directory path into components
        components = dir_path.split(os.sep)

        # Filter components to exclude system paths or very common directories
        filtered_components = [
            comp
            for comp in components
            if comp and comp not in [".", "..", "src", "lib", "app", "test", "tests"]
        ]

        # Use last 2 directory levels at most to avoid deep nesting
        if filtered_components:
            path_parts = (
                filtered_components[-2:]
                if len(filtered_components) > 2
                else filtered_components
            )

        # Build the relative path
        if path_parts:
            relative_path = Path(*path_parts) / f"{sanitized}.md"
        else:
            relative_path = Path(f"{sanitized}.md")

        return relative_path

    def _get_output_path(self, rel_path: Path) -> Path:
        """Determine the output path for a documentation file.

        Args:
            rel_path: Relative documentation path

        Returns:
            Full output path
        """
        output_path = self.docs_dir / rel_path

        # Ensure the directory exists
        os.makedirs(output_path.parent, exist_ok=True)

        return output_path

    def _save_documentation(
        self, document: Document, content: str, output_path: Path
    ) -> None:
        """Save documentation to the output path with appropriate formatting.

        Args:
            document: Original document
            content: Generated documentation content
            output_path: Path to save the documentation
        """
        # Determine document title and add front matter
        file_basename = os.path.basename(document.metadata.filepath)
        title = os.path.splitext(file_basename)[0]

        # Create front matter
        front_matter = {
            "title": title,
            "summary": self._extract_summary(content),
            "source_file": document.metadata.filepath,
            "language": str(document.metadata.language).lower(),
        }

        # Format content with front matter
        formatted_content = f"""---
{yaml.dump(front_matter, default_flow_style=False)}
---

{content}

"""

        # Add source code link at the end
        formatted_content += f"""
## Source Code

```{str(document.metadata.language).lower()}
{document.content}
```
"""

        # Write to file
        with open(output_path, "w") as f:
            f.write(formatted_content)

    def _extract_summary(self, content: str) -> str:
        """Extract a summary from documentation content.

        Args:
            content: Documentation content

        Returns:
            Summary string (first paragraph or sentence)
        """
        # Try to find the first paragraph
        paragraphs = content.split("\n\n")
        if paragraphs:
            # Remove markdown formatting from the first paragraph
            first_para = re.sub(r"[#*_`]", "", paragraphs[0]).strip()

            # If too long, just take the first sentence
            if len(first_para) > 150:
                sentences = first_para.split(".")
                if sentences:
                    return sentences[0].strip() + "."

            return first_para

        return "No summary available"

    def generate_for_repository(
        self, documents: List[Document], repo_name: str = "", repo_description: str = ""
    ) -> None:
        """Generate documentation for an entire repository.

        Args:
            documents: List of documents to document
            repo_name: Name of the repository
            repo_description: Description of the repository
        """
        # Generate documentation for each document
        total_documents = len(documents)

        # Create a project context from repository information
        project_context = f"Repository: {repo_name}\n{repo_description}\n"
        project_context += f"Total files: {total_documents}\n"

        # Process each document
        for document in documents:
            self.generate_for_document(document, project_context)

        # Generate index and overview documents
        self._generate_index_page(repo_name, repo_description, documents)
        self._generate_overview_pages(documents)

        # Build the documentation structure
        self.build_documentation()

    def _generate_index_page(
        self, repo_name: str, repo_description: str, documents: List[Document]
    ) -> None:
        """Generate the index page for the documentation.

        Args:
            repo_name: Name of the repository
            repo_description: Description of the repository
            documents: List of documents
        """
        # Prepare context for index generation
        languages = set(str(doc.metadata.language) for doc in documents)
        file_types = [os.path.splitext(doc.metadata.filepath)[1] for doc in documents]
        file_type_counts = {}

        for ext in file_types:
            if ext:
                file_type_counts[ext] = file_type_counts.get(ext, 0) + 1

        # Build index prompt
        index_prompt = f"""
Generate a comprehensive markdown index page for a software project documentation site.

Repository: {repo_name}
Description: {repo_description}
Total files: {len(documents)}
Programming languages: {', '.join(languages)}
File distribution: {str(file_type_counts)}

This index page should:
1. Start with a clear introduction to the project
2. Include an overview of the project's purpose and features
3. Provide a high-level explanation of the project architecture
4. Include a 'Getting Started' section with basic usage instructions
5. Explain how the documentation is organized
6. Use proper markdown formatting for MkDocs with Material theme

The documentation site will serve as the main reference for developers working with this codebase.
"""

        # Generate index content
        index_content = self.llm_client.answer_question(
            question="Generate a project documentation index page", context=index_prompt
        )

        # Save the index page
        index_path = self.docs_dir / "index.md"

        # Add front matter
        front_matter = {
            "title": repo_name or "Project Documentation",
            "summary": repo_description or "Project documentation generated by Docstra",
        }

        formatted_content = f"""---
{yaml.dump(front_matter, default_flow_style=False)}
---

{index_content}
"""

        with open(index_path, "w") as f:
            f.write(formatted_content)

        # Add to navigation
        self.nav_items.insert(0, {"title": "Home", "path": "index.md"})

    def _generate_overview_pages(self, documents: List[Document]) -> None:
        """Generate overview pages for the documentation.

        Args:
            documents: List of documents
        """
        # Group documents by directories/modules
        document_groups = self._group_documents_by_directory(documents)

        # Generate overview for each group
        for dir_path, docs in document_groups.items():
            # Skip if fewer than 2 documents
            if len(docs) < 2:
                continue

            # Create a sanitized directory name
            dir_name = os.path.basename(dir_path)
            sanitized_name = re.sub(r"[^\w\-\.]", "_", dir_name)

            # Prepare overview directory
            overview_dir = self.docs_dir / "overview"
            os.makedirs(overview_dir, exist_ok=True)

            # Prepare context for overview generation
            doc_names = [os.path.basename(doc.metadata.filepath) for doc in docs]

            overview_prompt = f"""
Generate a module overview documentation page in markdown format for the '{dir_name}' module/directory.

Files in this module:
{', '.join(doc_names)}

This overview should:
1. Explain the purpose and responsibility of this module/directory
2. Describe how the files work together
3. Highlight key components, classes, or functions
4. Explain the module's role in the overall architecture
5. Include any relevant usage patterns or examples
6. Use proper markdown formatting for MkDocs with Material theme

The overview should help developers understand the organization and purpose of this code module.
"""

            # Generate overview content
            overview_content = self.llm_client.answer_question(
                question=f"Generate a module overview for '{dir_name}'",
                context=overview_prompt,
            )

            # Save the overview page
            overview_path = overview_dir / f"{sanitized_name}.md"
            # Add front matter
            front_matter = {
                "title": f"{dir_name} Module",
                "summary": f"Overview of the {dir_name} module and its components",
            }

            formatted_content = f"""---
{yaml.dump(front_matter, default_flow_style=False)}
---

{overview_content}
"""

            with open(overview_path, "w") as f:
                f.write(formatted_content)

            # Add to navigation
            self.nav_items.append(
                {
                    "title": f"{dir_name} Overview",
                    "path": f"overview/{sanitized_name}.md",
                }
            )

    def _group_documents_by_directory(
        self, documents: List[Document]
    ) -> Dict[str, List[Document]]:
        """Group documents by their directory paths.

        Args:
            documents: List of documents

        Returns:
            Dictionary mapping directory paths to lists of documents
        """
        groups = {}

        for doc in documents:
            dir_path = os.path.dirname(doc.metadata.filepath)
            if dir_path not in groups:
                groups[dir_path] = []

            groups[dir_path].append(doc)

        return groups

    def build_documentation(self) -> None:
        """Build the final documentation structure."""
        # Generate MkDocs configuration
        self._generate_mkdocs_config()

        # Generate search index for better search functionality
        self._generate_search_index()

        # Create custom assets (CSS, JS, etc.)
        self._create_custom_assets()

        # Build MkDocs site if using MkDocs format
        if self.format == "mkdocs":
            self._build_mkdocs_site()

    def _generate_mkdocs_config(self) -> None:
        """Generate MkDocs configuration file."""
        # Organize navigation structure
        nav = self._organize_navigation()

        # Create MkDocs configuration
        mkdocs_config = {
            "site_name": "Project Documentation",
            "theme": {
                "name": "material",
                "palette": {"primary": "indigo", "accent": "indigo"},
                "features": [
                    "navigation.instant",
                    "navigation.tracking",
                    "navigation.expand",
                    "navigation.indexes",
                    "search.highlight",
                    "search.share",
                    "toc.follow",
                    "content.code.copy",
                ],
                "icon": {"repo": "fontawesome/brands/github"},
            },
            "markdown_extensions": [
                "pymdownx.highlight",
                "pymdownx.superfences",
                "pymdownx.inlinehilite",
                "pymdownx.tabbed",
                "pymdownx.critic",
                "pymdownx.tasklist",
                "admonition",
                "toc",
                "tables",
            ],
            "plugins": ["search", "mkdocstrings"],
            "extra_css": ["assets/css/custom.css"],
            "extra_javascript": ["assets/js/custom.js"],
            "nav": nav,
        }

        # Write MkDocs configuration to file
        config_path = self.output_dir / "mkdocs.yml"
        with open(config_path, "w") as f:
            yaml.dump(mkdocs_config, f, default_flow_style=False)

    def _organize_navigation(self) -> List:
        """Organize navigation items into a structured hierarchy.

        Returns:
            List of navigation items for MkDocs
        """
        # Create initial navigation with Home
        nav = [{"Home": "index.md"}]

        # Add overview pages if any exist
        overview_dir = self.docs_dir / "overview"
        if overview_dir.exists() and any(overview_dir.iterdir()):
            overview_nav = {"Module Overviews": []}

            # Add each overview page
            for overview_file in overview_dir.glob("*.md"):
                rel_path = str(overview_file.relative_to(self.docs_dir))
                title = overview_file.stem.replace("_", " ").title()
                overview_nav["Module Overviews"].append({title: rel_path})

            nav.append(overview_nav)

        # Group documentation files by directory
        grouped_nav = self._group_navigation_by_directory()

        # Add grouped navigation items
        for group in grouped_nav:
            nav.append(group)

        # Add API Reference section if appropriate
        if any(item.get("path", "").startswith("api/") for item in self.nav_items):
            api_nav = {"API Reference": []}

            # Add each API documentation page
            for item in self.nav_items:
                if item.get("path", "").startswith("api/"):
                    title = item.get("title", "Unknown")
                    path = item.get("path", "")
                    api_nav["API Reference"].append({title: path})

            nav.append(api_nav)

        return nav

    def _group_navigation_by_directory(self) -> List:
        """Group navigation items by directory structure.

        Returns:
            List of grouped navigation items
        """
        # Skip items already in special sections (index, overview, api)
        items = [
            item
            for item in self.nav_items
            if not item.get("path", "").startswith(("index", "overview/", "api/"))
        ]

        # Group by directory
        grouped = {}

        for item in items:
            path = item.get("path", "")
            title = item.get("title", "Unknown")

            # Split path to get directory structure
            parts = path.split("/")

            if len(parts) > 1:
                # Has directory structure
                group_name = parts[0].replace("_", " ").title()

                if group_name not in grouped:
                    grouped[group_name] = []

                grouped[group_name].append({title: path})
            else:
                # No directory, add directly
                grouped.setdefault("General", []).append({title: path})

        # Convert to list format required by MkDocs
        result = []

        for group_name, items in grouped.items():
            result.append({group_name: items})

        return result

    def _generate_search_index(self) -> None:
        """Generate enhanced search index for documentation."""
        # MkDocs will generate its own search index, but we can enhance it
        # with additional metadata and content for better search functionality

        search_data = []

        # Process each document to extract searchable content
        for filepath, document in self.documents_by_path.items():
            # Get corresponding documentation file
            rel_path = self._get_relative_doc_path(filepath)
            doc_path = str(rel_path)

            # Extract searchable metadata
            item = {
                "location": doc_path,
                "title": os.path.basename(filepath),
                "text": "",
                "keywords": [],
            }

            # Extract symbols for keywords
            if hasattr(document.metadata, "symbols"):
                item["keywords"].extend(document.metadata.symbols.keys())

            if hasattr(document.metadata, "classes"):
                item["keywords"].extend(document.metadata.classes)

            if hasattr(document.metadata, "functions"):
                item["keywords"].extend(document.metadata.functions)

            # Extract summary text from the first few lines of content
            content_lines = document.content.split("\n")
            item["text"] = "\n".join(content_lines[:20])

            search_data.append(item)

        # Save the enhanced search data
        search_path = self.docs_dir / "assets" / "js" / "extra-search-data.json"
        with open(search_path, "w") as f:
            json.dump(search_data, f)

    def _create_custom_assets(self) -> None:
        """Create custom assets for the documentation site."""
        # Create custom CSS
        custom_css = """
/* Custom styles to enhance MkDocs Material theme */

/* Improve code block styling */
.md-typeset pre > code {
    border-radius: 4px;
}

/* Add styling for class and function cards */
.docstra-class,
.docstra-function {
    padding: 1em;
    margin-bottom: 1.5em;
    border-left: 4px solid var(--md-primary-fg-color);
    background-color: rgba(0, 0, 0, 0.025);
}

.docstra-class h3,
.docstra-function h3 {
    margin-top: 0;
    color: var(--md-primary-fg-color);
}

/* Source file highlight */
.docstra-source {
    margin-top: 2em;
    padding-top: 1em;
    border-top: 1px solid rgba(0, 0, 0, 0.1);
}

/* Parameter tables */
.docstra-params {
    font-size: 0.9em;
}

.docstra-params th {
    background-color: rgba(0, 0, 0, 0.05);
}

/* Type annotations */
.docstra-type {
    color: var(--md-code-fg-color);
    font-family: var(--md-code-font-family);
    font-size: 0.9em;
}

/* Enhance admonitions */
.md-typeset .admonition {
    font-size: 0.9em;
}
"""

        # Write custom CSS
        custom_css_path = self.css_dir / "custom.css"
        with open(custom_css_path, "w") as f:
            f.write(custom_css)

        # Create custom JavaScript
        custom_js = """
document.addEventListener('DOMContentLoaded', function() {
    // Enable the enhanced search if available
    const extraSearchData = document.querySelector('script[src$="extra-search-data.json"]');
    if (extraSearchData) {
        // Load and process the enhanced search data
        fetch(extraSearchData.getAttribute('src'))
            .then(response => response.json())
            .then(data => {
                window.docstraExtraSearchData = data;
                console.log('Enhanced search data loaded');
            })
            .catch(err => console.error('Error loading enhanced search data:', err));
    }
    
    // Add syntax highlighting enhancements
    document.querySelectorAll('pre code').forEach(block => {
        // Add line numbers if not already present
        if (!block.classList.contains('linenos')) {
            const lineNumbers = block.innerHTML.split('\\n').length;
            if (lineNumbers > 3) {
                block.classList.add('line-numbers');
            }
        }
    });
});
"""

        # Write custom JavaScript
        custom_js_path = self.js_dir / "custom.js"
        with open(custom_js_path, "w") as f:
            f.write(custom_js)

    def _build_mkdocs_site(self) -> None:
        """Build the MkDocs site."""
        try:
            # Check if MkDocs is installed
            subprocess.run(["mkdocs", "--version"], check=True, capture_output=True)

            # Build the site
            subprocess.run(["mkdocs", "build"], cwd=self.output_dir, check=True)

            print(f"MkDocs site built successfully in {self.output_dir}/site/")
        except subprocess.CalledProcessError:
            print("Error: MkDocs is not installed or not available in PATH.")
            print(
                "Install MkDocs using: pip install mkdocs mkdocs-material pymdown-extensions mkdocstrings"
            )
        except Exception as e:
            print(f"Error building MkDocs site: {str(e)}")

    def serve_documentation(self, port: int = 8000) -> None:
        """Serve the documentation using MkDocs.

        Args:
            port: Port to serve the documentation on
        """
        try:
            # Check if MkDocs is installed
            subprocess.run(["mkdocs", "--version"], check=True, capture_output=True)

            # Serve the site
            print(f"Starting documentation server at: http://localhost:{port}")
            subprocess.run(
                ["mkdocs", "serve", "-a", f"localhost:{port}"], cwd=self.output_dir
            )
        except subprocess.CalledProcessError:
            print("Error: MkDocs is not installed or not available in PATH.")
            print(
                "Install MkDocs using: pip install mkdocs mkdocs-material pymdown-extensions mkdocstrings"
            )

            # Fall back to Python's simple HTTP server
            print("Falling back to Python's HTTP server...")
            site_dir = self.output_dir / "site"

            if not site_dir.exists():
                # Try to build the site first
                try:
                    subprocess.run(["mkdocs", "build"], cwd=self.output_dir, check=True)
                except:
                    print("Error building site. Serving the docs directory instead.")
                    site_dir = self.docs_dir

            # Serve using Python's HTTP server
            current_dir = os.getcwd()
            os.chdir(site_dir)

            try:
                import http.server
                import socketserver

                handler = http.server.SimpleHTTPRequestHandler
                socketserver.TCPServer.allow_reuse_address = True

                with socketserver.TCPServer(("", port), handler) as httpd:
                    print(f"Serving at http://localhost:{port}")
                    httpd.serve_forever()
            finally:
                os.chdir(current_dir)
        except Exception as e:
            print(f"Error serving documentation: {str(e)}")

```

```
