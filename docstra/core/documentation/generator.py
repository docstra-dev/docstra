# File: ./docstra/core/documentation/generator.py

import os
import re
import json
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Union, Tuple
import yaml
import datetime

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
        self.config_dir = self.docs_dir / ".docstra"

        # Create necessary directories
        os.makedirs(self.docs_dir, exist_ok=True)
        os.makedirs(self.assets_dir, exist_ok=True)
        os.makedirs(self.css_dir, exist_ok=True)
        os.makedirs(self.js_dir, exist_ok=True)
        os.makedirs(self.config_dir, exist_ok=True)

        # Load existing configuration if available
        self._load_configuration()

    def _load_configuration(self) -> None:
        """Load existing configuration and state."""
        config_file = self.config_dir / "config.json"
        if config_file.exists():
            try:
                with open(config_file, "r") as f:
                    config = json.load(f)
                    self.processed_files = set(config.get("processed_files", []))
                    self.nav_items = config.get("nav_items", [])
                    self.modules = config.get("modules", {})
                    self.global_symbols = config.get("global_symbols", {})
            except Exception as e:
                print(f"Warning: Could not load configuration: {e}")

    def _save_configuration(self) -> None:
        """Save current configuration and state."""
        config = {
            "processed_files": list(self.processed_files),
            "nav_items": self.nav_items,
            "modules": self.modules,
            "global_symbols": self.global_symbols,
            "last_updated": datetime.datetime.now().isoformat(),
        }

        config_file = self.config_dir / "config.json"
        try:
            with open(config_file, "w") as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save configuration: {e}")

    def _build_comprehensive_context(self, document: Document) -> Dict[str, Any]:
        """Build comprehensive context for documentation generation.

        Args:
            document: Document to generate context for

        Returns:
            Dictionary containing comprehensive context
        """
        context = {
            "file_info": {
                "path": document.metadata.filepath,
                "language": document.metadata.language,
                "size": document.metadata.size_bytes,
                "symbols": document.metadata.classes + document.metadata.functions,
                "imports": document.metadata.imports,
            },
            "module_info": {},
            "dependencies": [],
            "related_files": [],
            "code_quality": {},
            "documentation_stats": {},
        }

        if self.repo_map:
            file_node = self.repo_map.find_file(document.metadata.filepath)
            if file_node:
                # Get module category and related files
                module_category = self.repo_map._categorize_module(
                    document.metadata.filepath
                )
                related_files = self.repo_map.get_related_files(
                    document.metadata.filepath
                )
                dependencies = self.repo_map.get_file_dependencies(
                    document.metadata.filepath
                )

                # Update module information
                context["module_info"] = {
                    "category": module_category,
                    "complexity": file_node.complexity,
                    "line_count": file_node.line_count,
                    "contributors": file_node.contributors,
                    "last_modified": file_node.last_modified,
                    "tags": file_node.tags,
                }

                # Update dependencies and related files
                context["dependencies"] = dependencies
                context["related_files"] = related_files

                # Update code quality metrics
                context["code_quality"] = file_node.analysis["code_quality"]
                context["documentation_stats"] = {
                    "coverage": file_node.analysis["documentation_coverage"],
                    "test_coverage": file_node.analysis["test_coverage"],
                }

                # Get module overview if available
                module_overview = self.repo_map.get_module_overview()
                if module_overview:
                    context["module_overview"] = {
                        "statistics": module_overview["statistics"],
                        "modules": module_overview["modules"].get(module_category, []),
                        "dependencies": module_overview["dependencies"].get(
                            document.metadata.filepath, []
                        ),
                        "complexity": module_overview["complexity"].get(
                            document.metadata.filepath, None
                        ),
                    }

        return context

    def generate_for_document(
        self, document: Document, project_context: str = ""
    ) -> Optional[str]:
        """Generate documentation for a document.

        Args:
            document: Document to generate documentation for
            project_context: Additional context about the project

        Returns:
            Generated documentation if successful, None otherwise
        """
        # Check if document should be excluded
        if any(
            pattern in document.metadata.filepath for pattern in self.exclude_patterns
        ):
            return None

        # Check if document has already been processed
        if document.metadata.filepath in self.processed_files:
            return None

        # Build comprehensive context
        context = self._build_comprehensive_context(document)

        # Build documentation prompt
        prompt = self._build_documentation_prompt(document, context)

        # Generate documentation using LLM
        try:
            documentation = self.llm_client.generate_documentation(prompt)
            if documentation:
                # Save documentation
                self._save_documentation(document, documentation, context)
                self.processed_files.add(document.metadata.filepath)
                return documentation
        except Exception as e:
            print(
                f"Error generating documentation for {document.metadata.filepath}: {str(e)}"
            )

        return None

    def _save_documentation(
        self, document: Document, documentation: str, context: Dict[str, Any]
    ) -> None:
        """Save generated documentation.

        Args:
            document: Original document
            documentation: Generated documentation
            context: Comprehensive context used for generation
        """
        # Create output path
        rel_path = os.path.relpath(
            document.metadata.filepath, self.repo_map.root_path if self.repo_map else ""
        )
        output_path = self.docs_dir / f"{rel_path}.md"

        # Create directory if it doesn't exist
        os.makedirs(output_path.parent, exist_ok=True)

        # Build front matter
        front_matter = {
            "title": os.path.basename(document.metadata.filepath),
            "description": f"Documentation for {document.metadata.filepath}",
            "language": document.metadata.language,
        }

        # Add enhanced metadata from context
        if context["module_info"]:
            front_matter.update(context["module_info"])

        # Add code quality metrics
        if context["code_quality"]:
            front_matter["code_quality"] = context["code_quality"]

        # Add documentation statistics
        if context["documentation_stats"]:
            front_matter["documentation_stats"] = context["documentation_stats"]

        # Write documentation with front matter
        with open(output_path, "w") as f:
            f.write("---\n")
            for key, value in front_matter.items():
                f.write(f"{key}: {value}\n")
            f.write("---\n\n")
            f.write(documentation)

        # Update navigation
        self._update_navigation(document, output_path, context)

    def _needs_update(self, document: Document) -> bool:
        """Check if a document needs to be updated.

        Args:
            document: Document to check

        Returns:
            True if the document needs updating, False otherwise
        """
        # Always update if not previously processed
        if document.metadata.filepath not in self.processed_files:
            return True

        # Check if the source file has been modified
        source_path = Path(document.metadata.filepath)
        if not source_path.exists():
            return False

        # Get the corresponding documentation file
        rel_path = self._get_relative_doc_path(document.metadata.filepath)
        doc_path = self._get_output_path(rel_path)

        if not doc_path.exists():
            return True

        # Compare modification times
        source_mtime = source_path.stat().st_mtime
        doc_mtime = doc_path.stat().st_mtime

        return source_mtime > doc_mtime

    def _update_navigation(
        self, document: Document, output_path: Path, context: Dict[str, Any]
    ) -> None:
        """Update the navigation structure for a document.

        Args:
            document: Document to update navigation for
            output_path: Path to the documentation file
            context: Comprehensive context used for generation
        """
        # Create navigation item
        nav_item = {
            "title": os.path.basename(document.metadata.filepath),
            "path": str(output_path.relative_to(self.docs_dir)),
        }

        # Check if item already exists
        for item in self.nav_items:
            if item.get("path") == nav_item["path"]:
                item.update(nav_item)
                return

        # Add new item
        self.nav_items.append(nav_item)

    def _build_documentation_prompt(self, document: Document, file_context: str) -> str:
        """Build a detailed documentation prompt for the LLM.

        Args:
            document: Document to document
            file_context: Additional context about the file

        Returns:
            Prompt for the LLM
        """
        # Get enhanced metadata from repository map
        file_node = None
        module_context = {}
        if self.repo_map:
            file_node = self.repo_map.find_file(document.metadata.filepath)
            if file_node:
                # Get module category and related files
                module_category = self.repo_map._categorize_module(
                    document.metadata.filepath
                )
                related_files = self.repo_map.get_related_files(
                    document.metadata.filepath
                )
                dependencies = self.repo_map.get_file_dependencies(
                    document.metadata.filepath
                )

                # Build module context
                module_context = {
                    "category": module_category,
                    "related_files": related_files,
                    "dependencies": dependencies,
                    "complexity": file_node.complexity,
                    "line_count": file_node.line_count,
                    "contributors": file_node.contributors,
                    "last_modified": file_node.last_modified,
                    "analysis": file_node.analysis,
                }

        # Build comprehensive context string
        context_str = f"""
File Information:
----------------
Path: {document.metadata.filepath}
Language: {document.metadata.language}
Size: {document.metadata.size_bytes} bytes
"""

        if module_context:
            context_str += f"""
Module Context:
--------------
Category: {module_context['category']}
Complexity: {module_context['complexity']}
Lines of Code: {module_context['line_count']}
Last Modified: {module_context['last_modified']}
Contributors: {', '.join(module_context['contributors'])}

Dependencies:
------------
{chr(10).join(f'- {dep}' for dep in module_context['dependencies'])}

Related Files:
-------------
{chr(10).join(f'- {rel}' for rel in module_context['related_files'])}

Code Quality:
------------
{chr(10).join(f'- {k}: {v}' for k, v in module_context['analysis']['code_quality'].items())}

Documentation Coverage: {module_context['analysis']['documentation_coverage']}
Test Coverage: {module_context['analysis']['test_coverage']}
"""

        # Add additional context if provided
        if file_context:
            context_str += f"\nAdditional Context:\n{file_context}"

        # Build documentation requirements
        requirements = """
Documentation Requirements:
-------------------------
1. Overview
   - Brief description of the file's purpose
   - Key functionality and features
   - Important dependencies and relationships

2. Installation and Setup
   - Required dependencies
   - Configuration requirements
   - Environment setup

3. Usage Guide
   - Basic usage examples
   - Common use cases
   - Best practices

4. API Reference
   - Detailed documentation of classes and functions
   - Parameters and return types
   - Examples for each major component

5. Integration
   - How to integrate with other modules
   - Dependencies and requirements
   - Common integration patterns

6. Advanced Usage
   - Advanced features and capabilities
   - Performance considerations
   - Customization options

7. Troubleshooting
   - Common issues and solutions
   - Error handling
   - Debugging tips

8. Contributing
   - Development setup
   - Code style guidelines
   - Testing requirements

Formatting Guidelines:
--------------------
1. Use clear and concise language
2. Include code examples where relevant
3. Use proper markdown formatting
4. Include cross-references to related documentation
5. Maintain consistent structure across all sections
"""

        # Add language-specific guidelines
        language_guidelines = {
            "python": """
Python-Specific Guidelines:
-------------------------
1. Document classes with:
   - Class purpose and inheritance
   - Public methods and properties
   - Usage examples
   - Type hints and annotations

2. Document functions with:
   - Purpose and behavior
   - Parameters and return types
   - Exceptions and error handling
   - Usage examples

3. Include:
   - Import statements
   - Type hints
   - Docstrings
   - Example usage
""",
            "javascript": """
JavaScript/TypeScript Guidelines:
------------------------------
1. Document classes with:
   - Class purpose and inheritance
   - Public methods and properties
   - TypeScript interfaces/types
   - Usage examples

2. Document functions with:
   - Purpose and behavior
   - Parameters and return types
   - Async/await usage
   - Example usage

3. Include:
   - Import/export statements
   - TypeScript types
   - JSDoc comments
   - Example usage
""",
            "java": """
Java/Kotlin Guidelines:
---------------------
1. Document classes with:
   - Class purpose and inheritance
   - Public methods and properties
   - Generic types
   - Usage examples

2. Document methods with:
   - Purpose and behavior
   - Parameters and return types
   - Exceptions
   - Example usage

3. Include:
   - Package declarations
   - Import statements
   - Javadoc comments
   - Example usage
""",
        }

        # Add language-specific guidelines if available
        if document.metadata.language.lower() in language_guidelines:
            requirements += language_guidelines[document.metadata.language.lower()]

        return f"{context_str}\n\n{requirements}"

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

        # Add Getting Started section
        nav.append(
            {
                "Getting Started": [
                    {"Installation": "getting-started/installation.md"},
                    {"Quick Start": "getting-started/quickstart.md"},
                    {"Configuration": "getting-started/configuration.md"},
                ]
            }
        )

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

        # Group documentation files by directory and type
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

        # Add Advanced Topics section
        nav.append(
            {
                "Advanced Topics": [
                    {"Performance": "advanced/performance.md"},
                    {"Security": "advanced/security.md"},
                    {"Deployment": "advanced/deployment.md"},
                    {"Troubleshooting": "advanced/troubleshooting.md"},
                ]
            }
        )

        # Add Contributing section
        nav.append(
            {
                "Contributing": [
                    {"Development Guide": "contributing/development.md"},
                    {"Code Style": "contributing/code-style.md"},
                    {"Testing": "contributing/testing.md"},
                    {"Documentation": "contributing/documentation.md"},
                ]
            }
        )

        return nav

    def _group_navigation_by_directory(self) -> List:
        """Group navigation items by directory structure and type.

        Returns:
            List of grouped navigation items
        """
        # Skip items already in special sections (index, overview, api)
        items = [
            item
            for item in self.nav_items
            if not item.get("path", "").startswith(("index", "overview/", "api/"))
        ]

        # Group by directory and type
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

                # Categorize items by type
                if "test" in path.lower() or "spec" in path.lower():
                    category = "Testing"
                elif "util" in path.lower() or "helper" in path.lower():
                    category = "Utilities"
                elif "model" in path.lower() or "schema" in path.lower():
                    category = "Models"
                elif "service" in path.lower() or "provider" in path.lower():
                    category = "Services"
                elif "controller" in path.lower() or "handler" in path.lower():
                    category = "Controllers"
                else:
                    category = "Core"

                grouped[group_name].append(
                    {"title": title, "path": path, "category": category}
                )
            else:
                # No directory, add to General
                grouped.setdefault("General", []).append(
                    {"title": title, "path": path, "category": "Core"}
                )

        # Convert to list format required by MkDocs
        result = []

        for group_name, items in grouped.items():
            # Sort items by category and title
            sorted_items = sorted(items, key=lambda x: (x["category"], x["title"]))

            # Group items by category
            category_groups = {}
            for item in sorted_items:
                category = item["category"]
                if category not in category_groups:
                    category_groups[category] = []
                category_groups[category].append({item["title"]: item["path"]})

            # Create navigation structure
            group_nav = {group_name: []}
            for category, category_items in category_groups.items():
                if len(category_items) > 1:
                    group_nav[group_name].append({category: category_items})
                else:
                    group_nav[group_name].extend(category_items)

            result.append(group_nav)

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
