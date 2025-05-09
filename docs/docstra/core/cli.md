---
language: documenttype.markdown
source_file: /Users/jorgenosberg/development/docstra/docs/docstra/core/cli.md
summary: 'docstra/core/cli.md

  ======================'
title: cli

---

**docstra/core/cli.md**
======================

**Overview**
------------

The `cli` module provides a command-line interface for interacting with the Docstra project.

**Classes**
-----------

### `app`

*   **Attributes:**
    *   `__init__(self, console)`: Initializes the application instance.
*   **Methods:**
    *   `__call__(self)`: Runs the application and starts the CLI loop.

### `cli`

*   **Attributes:**
    *   `__init__(self, console)`: Initializes the CLI instance.
*   **Methods:**
    *   `add_command(self, command)`: Adds a new command to the CLI.
    *   `run(self)`: Runs the CLI and executes the commands.

### `command`

*   **Attributes:**
    *   `__init__(self, name, console)`: Initializes the command instance.
*   **Methods:**
    *   `execute(self, args)`: Executes the command with the provided arguments.

**Functions**
-------------

### `get_llm_client(config_manager)`

*   **Parameters:** `config_manager`
*   **Returns:** A Docstra LLM client instance.
*   **Purpose:** Returns a configured Docstra LLM client instance.

### `serve_documentation(docs_dir, port=8000)`

*   **Parameters:**
    *   `docs_dir`: The directory containing the generated documentation.
    *   `port` (optional): The port to serve the documentation on. Defaults to 8000.
*   **Returns:** None
*   **Purpose:** Serves the generated documentation using MkDocs or a simple HTTP server.

**Usage Examples**
-----------------

### Running the CLI

```bash
$ python -m docstra.core.cli
```

### Adding a Command

```python
from docstra.core.cli import cli, command

@cli.add_command
def hello_world(console):
    console.print("Hello, World!")

if __name__ == "__main__":
    cli.run()
```

**Important Dependencies**
-------------------------

The `docstra/core/cli` module depends on the following:

*   `docstra.core.documentation.generator`: Provides the documentation generator functionality.
*   `docstra.core.utils.file_collector`: Collects files for processing.

**Notes**
-------

*   The `cli` module uses a modular design to allow for easy extension and customization of the CLI.
*   The `serve_documentation` function can be used to serve generated documentation using MkDocs or a simple HTTP server.


## Source Code

```documenttype.markdown
---
language: documenttype.python
source_file: /Users/jorgenosberg/development/docstra/docstra/core/cli.py
summary: 'docstra/core/cli.py

  =========================='
title: cli

---

**docstra/core/cli.py**
==========================

Overview
--------

The `cli.py` module provides a command-line interface for interacting with the Docstra project. It contains functions and classes that handle various tasks, such as generating documentation, serving documentation, and processing files.

Classes
-------

### `CLI`

A class representing the command-line interface.

#### Attributes

*   `app`: The application instance.
*   `config`: The configuration object.

#### Methods

*   `__init__`: Initializes the CLI instance with the given application and configuration.
*   `run`: Runs the command-line interface, parsing arguments and executing commands.

### `DocumentationGenerator`

A class responsible for generating documentation.

#### Attributes

*   `llm_client`: The language model client instance.
*   `output_dir`: The output directory for generated documentation.
*   `format`: The format of the generated documentation (e.g., HTML, Markdown).

#### Methods

*   `__init__`: Initializes the generator instance with the given language model client and configuration.
*   `generate_for_document`: Generates documentation for a single document.
*   `build_documentation`: Builds and organizes the generated documentation.
*   `serve_documentation`: Serves the generated documentation using an HTTP server.

### `FileCollector`

A class responsible for collecting files from a directory or base path.

#### Attributes

*   `base_path`: The base path to start searching for files.
*   `include_dirs`: A list of directories to include in the search.
*   `exclude_dirs`: A list of directories to exclude from the search.
*   `exclude_files`: A list of file patterns to exclude from the search.

#### Methods

*   `__init__`: Initializes the collector instance with the given base path and configuration.
*   `collect_files`: Collects files from the directory or base path, applying filters as necessary.

Functions
---------

### `serve_documentation`

Serves the generated documentation using an HTTP server.

#### Parameters

*   `docs_dir`: The output directory for the generated documentation.
*   `port`: The port number to use for serving the documentation (default: 8000).

Usage Examples
-------------

To generate documentation, run the following command:

```bash
python cli.py generate /path/to/base/directory
```

This will create a documentation directory with HTML files in the specified format.

To serve the generated documentation, run the following command:

```bash
python cli.py serve_documentation /path/to/docs/directory 8000
```

This will start an HTTP server serving the generated documentation at `http://localhost:8000`.

Important Dependencies
--------------------

*   `docstra.core.documentation.generator`: The `DocumentationGenerator` class.
*   `docstra.core.file_collector`: The `FileCollector` class.

Implementation Details
---------------------

The `cli.py` module uses a modular design, with separate classes and functions handling different tasks. The `CLI` class serves as the main entry point for the command-line interface, while the `DocumentationGenerator` and `FileCollector` classes handle specific tasks.

The `serve_documentation` function uses an HTTP server to serve the generated documentation, allowing users to access it from a web browser.

Notes
-----

*   The `cli.py` module assumes that the Docstra project is installed and configured properly.
*   The `generate` command may take some time to complete, depending on the size of the input directory and the complexity of the documentation.


## Source Code

```documenttype.python
# File: ./docstra/core/cli.py

"""
Command-line interface for the code documentation assistant.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
)

from docstra.core.config.settings import ConfigManager, ModelProvider
from docstra.core.document_processing.chunking import (
    ChunkingPipeline,
    SemanticChunking,
    SyntaxAwareChunking,
)
from docstra.core.document_processing.document import Document
from docstra.core.document_processing.extractor import DocumentProcessor
from docstra.core.document_processing.parser import CodeParser
from docstra.core.documentation.generator import DocumentationGenerator
from docstra.core.indexing.code_index import CodebaseIndexer
from docstra.core.indexing.repo_map import RepositoryMap
from docstra.core.ingestion.embeddings import EmbeddingFactory
from docstra.core.ingestion.storage import ChromaDBStorage, DocumentIndexer
from docstra.core.llm.anthropic import AnthropicClient
from docstra.core.llm.local import LocalModelClient
from docstra.core.llm.ollama import OllamaClient
from docstra.core.llm.openai import OpenAIClient
from docstra.core.retrieval.chroma import ChromaRetriever
from docstra.core.retrieval.hybrid import HybridRetriever


def serve_documentation(docs_dir, port=8000):
    """Serve documentation using a simple HTTP server."""
    from fastapi import FastAPI, HTTPException, Request
    from fastapi.responses import HTMLResponse, FileResponse
    from fastapi.staticfiles import StaticFiles
    import uvicorn
    from pathlib import Path

    app = FastAPI(title="Documentation Server")

    # Mount static files
    app.mount(
        "/static",
        StaticFiles(directory=os.path.join(docs_dir, "static")),
        name="static",
    )

    @app.get("/", response_class=HTMLResponse)
    async def read_index():
        index_path = os.path.join(docs_dir, "index.html")
        if os.path.exists(index_path):
            with open(index_path, "r") as f:
                return f.read()
        else:
            # Try other formats
            md_path = os.path.join(docs_dir, "index.md")
            if os.path.exists(md_path):
                # Convert markdown to HTML
                import markdown

                with open(md_path, "r") as f:
                    content = f.read()
                html_content = markdown.markdown(content)
                return f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Documentation</title>
                    <link rel="stylesheet" href="/static/style.css">
                </head>
                <body>
                    <div class="container">
                        {html_content}
                    </div>
                </body>
                </html>
                """

            # If all else fails
            raise HTTPException(status_code=404, detail="Index not found")

    @app.get("/{path:path}")
    async def read_file(path: str):
        full_path = os.path.join(docs_dir, path)
        if os.path.exists(full_path):
            return FileResponse(full_path)

        # Try with extensions
        for ext in [".html", ".md", ".rst"]:
            if os.path.exists(full_path + ext):
                if ext == ".md":
                    # Convert markdown to HTML
                    import markdown

                    with open(full_path + ext, "r") as f:
                        content = f.read()
                    html_content = markdown.markdown(content)
                    return f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <title>Documentation</title>
                        <link rel="stylesheet" href="/static/style.css">
                    </head>
                    <body>
                        <div class="container">
                            {html_content}
                        </div>
                    </body>
                    </html>
                    """
                else:
                    return FileResponse(full_path + ext)

        raise HTTPException(status_code=404, detail=f"File {path} not found")

    console.print(
        f"[bold green]Starting documentation server at:[/] http://localhost:{port}"
    )
    uvicorn.run(app, host="0.0.0.0", port=port)


# Initialize typer app
app = typer.Typer(
    name="docstra",
    help="LLM-powered code documentation assistant",
    add_completion=False,
)

# Initialize rich console
console = Console()


def get_llm_client(config_manager: ConfigManager):
    """Get the appropriate LLM client based on configuration.

    Args:
        config_manager: Configuration manager

    Returns:
        LLM client
    """
    config = config_manager.config
    provider = config.model.provider

    if provider == ModelProvider.ANTHROPIC:
        return AnthropicClient(
            model_name=config.model.model_name,
            api_key=config.model.api_key,
            max_tokens=config.model.max_tokens,
            temperature=config.model.temperature,
        )
    elif provider == ModelProvider.OPENAI:
        return OpenAIClient(
            model_name=config.model.model_name,
            api_key=config.model.api_key,
            max_tokens=config.model.max_tokens,
            temperature=config.model.temperature,
        )
    elif provider == ModelProvider.OLLAMA:
        return OllamaClient(
            model_name=config.model.model_name,
            api_base=config.model.api_base or "http://localhost:11434",
            max_tokens=config.model.max_tokens,
            temperature=config.model.temperature,
        )
    elif provider == ModelProvider.LOCAL:
        return LocalModelClient(
            model_name=config.model.model_name,
            model_path=config.model.model_path,
            max_tokens=config.model.max_tokens,
            temperature=config.model.temperature,
            device=config.model.device,
        )
    else:
        raise ValueError(f"Unsupported model provider: {provider}")


@app.command()
def init(
    codebase_path: str = typer.Argument(".", help="Path to the codebase to document"),
    config_path: Optional[str] = typer.Option(
        None, "--config", "-c", help="Path to the configuration file"
    ),
    exclude: List[str] = typer.Option(
        [], "--exclude", "-e", help="Patterns to exclude from processing"
    ),
    include: List[str] = typer.Option(
        [], "--include", "-i", help="Directories to specifically include"
    ),
    force: bool = typer.Option(
        False, "--force", "-f", help="Force reindexing of the codebase"
    ),
    wizard: bool = typer.Option(
        True, "--wizard/--no-wizard", help="Run interactive configuration wizard"
    ),
):
    """Initialize the code documentation assistant for a codebase."""
    from docstra.core.utils.file_collector import collect_files, FileCollector
    from docstra.core.config.wizard import run_init_wizard

    console.print(Panel("Initializing code documentation assistant", expand=False))

    # Initialize configuration
    config_manager = ConfigManager(config_path)

    # Run initialization wizard if requested
    if wizard:
        # Determine absolute path for the codebase
        abs_codebase_path = os.path.abspath(codebase_path)

        # Check if codebase path exists
        if not os.path.exists(abs_codebase_path):
            console.print(
                f"[bold red]Error:[/] Codebase path {abs_codebase_path} does not exist"
            )
            sys.exit(1)

        try:
            run_init_wizard(console, abs_codebase_path, config_path)

            # Reload config after wizard
            config_manager = ConfigManager(config_path)
        except KeyboardInterrupt:
            console.print(
                "\n[yellow]Wizard cancelled, using existing configuration.[/]"
            )

    # Override exclude patterns if provided via command line
    exclude_patterns = exclude or config_manager.config.processing.exclude_patterns

    if exclude:
        config_manager.update(processing={"exclude_patterns": exclude})

    # Get paths
    codebase_path = os.path.abspath(codebase_path)
    persist_directory = config_manager.config.storage.persist_directory

    # Check if codebase path exists
    if not os.path.exists(codebase_path):
        console.print(
            f"[bold red]Error:[/] Codebase path {codebase_path} does not exist"
        )
        sys.exit(1)

    # Print initialization information
    console.print(f"Codebase path: [bold]{codebase_path}[/]")
    console.print(f"Persist directory: [bold]{persist_directory}[/]")
    console.print(
        f"Model: [bold]{config_manager.config.model.provider}[/] - [bold]{config_manager.config.model.model_name}[/]"
    )

    # Check if already initialized and not forcing
    index_path = os.path.join(persist_directory, "index")
    if os.path.exists(index_path) and not force:
        console.print("[yellow]Codebase already indexed. Use --force to reindex.[/]")
        return

    # Process and index the codebase
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        # Initialize components
        task_init = progress.add_task("[cyan]Initializing components...", total=None)

        # Initialize document processor
        doc_processor = DocumentProcessor()

        # Initialize code parser
        code_parser = CodeParser()

        # Initialize chunking pipeline
        chunking_pipeline = ChunkingPipeline(
            [
                SyntaxAwareChunking(),
                SemanticChunking(
                    max_chunk_size=config_manager.config.processing.chunk_size
                ),
            ]
        )

        # Initialize embedding generator
        embedding_generator = EmbeddingFactory.create_embedding_generator(
            embedding_type=config_manager.config.embedding.provider,
            model_name=config_manager.config.embedding.model_name,
        )

        # Initialize storage
        storage = ChromaDBStorage(
            persist_directory=os.path.join(persist_directory, "chroma")
        )

        # Initialize document indexer
        doc_indexer = DocumentIndexer(storage, embedding_generator)

        # Initialize codebase indexer
        code_indexer = CodebaseIndexer(
            index_directory=os.path.join(persist_directory, "index"),
            exclude_patterns=exclude_patterns,
        )

        progress.update(
            task_init, completed=True, description="[green]Components initialized"
        )

        # Use our file collection utility to gather files
        task_collect = progress.add_task("[cyan]Collecting files...", total=None)
        file_paths = collect_files(
            base_path=codebase_path,
            include_dirs=include,
            exclude_dirs=exclude_patterns,
            file_extensions=FileCollector.default_code_file_extensions(),
        )

        progress.update(
            task_collect,
            completed=True,
            description=f"[green]Collected {len(file_paths)} files",
        )

        # Process files
        task_process = progress.add_task(
            "[cyan]Processing files...", total=len(file_paths)
        )

        documents = []
        for file_path in file_paths:
            try:
                document = doc_processor.process(file_path)
                documents.append(document)
            except Exception as e:
                console.print(
                    f"[yellow]Warning:[/] Failed to process {file_path}: {str(e)}"
                )
            progress.update(task_process, advance=1)

        # Parse documents
        task_parse = progress.add_task(
            "[cyan]Parsing code structure...", total=len(documents)
        )

        for document in documents:
            try:
                code_parser.parse_document(document)
            except Exception as e:
                console.print(
                    f"[yellow]Warning:[/] Failed to parse {document.metadata.filepath}: {str(e)}"
                )

            progress.update(task_parse, advance=1)

        # Chunk documents
        task_chunk = progress.add_task(
            "[cyan]Chunking documents...", total=len(documents)
        )

        for document in documents:
            try:
                chunking_pipeline.process(document)
            except Exception as e:
                console.print(
                    f"[yellow]Warning:[/] Failed to chunk {document.metadata.filepath}: {str(e)}"
                )

            progress.update(task_chunk, advance=1)

        # Index documents
        task_index = progress.add_task("[cyan]Indexing documents...", total=None)

        doc_indexer.index_documents(documents)
        code_indexer.index_documents(documents)

        progress.update(
            task_index, completed=True, description="[green]Indexed all documents"
        )

        # Create repository map
        task_map = progress.add_task("[cyan]Creating repository map...", total=None)

        repo_map = RepositoryMap.from_documents(
            documents, codebase_path, code_indexer.index
        )

        # Save repository map
        map_path = os.path.join(persist_directory, "repo_map.json")
        with open(map_path, "w") as f:
            import json

            json.dump(repo_map.to_dict(), f)

        progress.update(
            task_map, completed=True, description="[green]Created repository map"
        )

    console.print("[bold green]Initialization complete![/]")
    console.print(f"Processed and indexed {len(documents)} files")
    console.print("You can now use the code documentation assistant")


@app.command()
def document(
    file_path: str = typer.Argument(..., help="Path to the file to document"),
    config_path: Optional[str] = typer.Option(
        None, "--config", "-c", help="Path to the configuration file"
    ),
    output_file: Optional[str] = typer.Option(
        None, "--output", "-o", help="Path to save the generated documentation"
    ),
):
    """Generate documentation for a file."""
    # Initialize configuration
    config_manager = ConfigManager(config_path)

    # Check if file exists
    if not os.path.exists(file_path):
        console.print(f"[bold red]Error:[/] File {file_path} does not exist")
        sys.exit(1)

    # Process the file
    console.print(f"Generating documentation for [bold]{file_path}[/]")

    # Initialize document processor
    doc_processor = DocumentProcessor()

    # Process the file
    document = doc_processor.process(file_path)

    # Get language
    language = str(document.metadata.language)

    # Get LLM client
    llm_client = get_llm_client(config_manager)

    # Generate documentation
    with console.status("[cyan]Generating documentation...", spinner="dots"):
        documentation = llm_client.document_code(
            code=document.content,
            language=language,
            additional_context=f"File path: {file_path}",
        )

    # Output the documentation
    if output_file:
        with open(output_file, "w") as f:
            f.write(documentation)
        console.print(f"Documentation saved to [bold]{output_file}[/]")
    else:
        console.print(
            Panel(
                Markdown(documentation),
                title=f"Documentation for {os.path.basename(file_path)}",
            )
        )


@app.command()
def explain(
    file_path: str = typer.Argument(..., help="Path to the file to explain"),
    config_path: Optional[str] = typer.Option(
        None, "--config", "-c", help="Path to the configuration file"
    ),
    output_file: Optional[str] = typer.Option(
        None, "--output", "-o", help="Path to save the explanation"
    ),
):
    """Explain a file."""
    # Initialize configuration
    config_manager = ConfigManager(config_path)

    # Check if file exists
    if not os.path.exists(file_path):
        console.print(f"[bold red]Error:[/] File {file_path} does not exist")
        sys.exit(1)

    # Process the file
    console.print(f"Generating explanation for [bold]{file_path}[/]")

    # Initialize document processor
    doc_processor = DocumentProcessor()

    # Process the file
    document = doc_processor.process(file_path)

    # Get language
    language = str(document.metadata.language)

    # Get LLM client
    llm_client = get_llm_client(config_manager)

    # Generate explanation
    with console.status("[cyan]Generating explanation...", spinner="dots"):
        explanation = llm_client.explain_code(
            code=document.content,
            language=language,
            additional_context=f"File path: {file_path}",
        )

    # Output the explanation
    if output_file:
        with open(output_file, "w") as f:
            f.write(explanation)
        console.print(f"Explanation saved to [bold]{output_file}[/]")
    else:
        console.print(
            Panel(
                Markdown(explanation),
                title=f"Explanation for {os.path.basename(file_path)}",
            )
        )


@app.command()
def ask(
    question: str = typer.Argument(..., help="Question about the codebase"),
    codebase_path: str = typer.Option(
        ".", "--codebase", "-C", help="Path to the codebase"
    ),
    config_path: Optional[str] = typer.Option(
        None, "--config", "-c", help="Path to the configuration file"
    ),
    n_results: int = typer.Option(
        5, "--results", "-n", help="Number of results to retrieve"
    ),
):
    """Ask a question about the codebase."""
    # Initialize configuration
    config_manager = ConfigManager(config_path)

    # Get paths
    codebase_path = os.path.abspath(codebase_path)
    persist_directory = config_manager.config.storage.persist_directory

    # Check if codebase is initialized
    index_path = os.path.join(persist_directory, "index")
    chroma_path = os.path.join(persist_directory, "chroma")

    if not os.path.exists(index_path) or not os.path.exists(chroma_path):
        console.print(
            "[bold red]Error:[/] Codebase not initialized. Run 'docstra init' first."
        )
        sys.exit(1)

    # Initialize components
    console.print(f"Searching for: [bold]{question}[/]")

    with console.status("[cyan]Initializing components...", spinner="dots"):
        # Initialize embedding generator
        embedding_generator = EmbeddingFactory.create_embedding_generator(
            embedding_type=config_manager.config.embedding.provider,
            model_name=config_manager.config.embedding.model_name,
        )

        # Initialize storage
        storage = ChromaDBStorage(persist_directory=chroma_path)

        # Initialize retriever
        retriever = ChromaRetriever(storage, embedding_generator)

        # Initialize code index
        code_indexer = CodebaseIndexer(index_directory=index_path)

        # Initialize hybrid retriever
        hybrid_retriever = HybridRetriever(retriever, code_indexer.index)

        # Initialize LLM client
        llm_client = get_llm_client(config_manager)

    # Retrieve relevant chunks
    with console.status("[cyan]Searching codebase...", spinner="dots"):
        results = hybrid_retriever.retrieve(
            query=question, n_results=n_results, use_code_context=True
        )

    # Generate answer
    with console.status("[cyan]Generating answer...", spinner="dots"):
        answer = llm_client.answer_question(question=question, context=results)

    # Display results
    console.print(Panel(Markdown(answer), title="Answer"))

    # Show sources
    console.print("\n[bold]Sources:[/]")
    for i, result in enumerate(results[:5]):
        filepath = result["metadata"].get("document_id", "Unknown")
        start_line = result["metadata"].get("start_line", "?")
        end_line = result["metadata"].get("end_line", "?")

        console.print(
            f"[bold]{i+1}.[/] [cyan]{filepath}[/] (lines {start_line}-{end_line})"
        )


@app.command()
def config(
    config_path: Optional[str] = typer.Option(
        None, "--config", "-c", help="Path to the configuration file"
    ),
    show: bool = typer.Option(False, "--show", help="Show current configuration"),
    reset: bool = typer.Option(False, "--reset", help="Reset configuration to default"),
    set_model: Optional[str] = typer.Option(
        None, "--model", help="Set model provider (anthropic, openai, ollama, local)"
    ),
    set_model_name: Optional[str] = typer.Option(
        None, "--model-name", help="Set model name"
    ),
    set_embedding: Optional[str] = typer.Option(
        None, "--embedding", help="Set embedding provider (huggingface, openai, ollama)"
    ),
):
    """Manage configuration."""
    # Initialize configuration manager
    config_manager = ConfigManager(config_path)

    # Reset configuration if requested
    if reset:
        config_manager.reset_to_default()
        console.print("[bold green]Configuration reset to default[/]")

    # Update configuration if needed
    changes = False

    if set_model:
        try:
            provider = ModelProvider(set_model.lower())
            config_manager.update(model={"provider": provider})
            changes = True
        except ValueError:
            console.print(f"[bold red]Error:[/] Invalid model provider: {set_model}")
            console.print("Available providers: anthropic, openai, ollama, local")

    if set_model_name:
        config_manager.update(model={"model_name": set_model_name})
        changes = True

    if set_embedding:
        config_manager.update(embedding={"provider": set_embedding})
        changes = True

    if changes:
        console.print("[bold green]Configuration updated[/]")

    # Show configuration if requested or if no other action was taken
    if show or (not reset and not changes):
        config = config_manager.config

        console.print("[bold]Current Configuration:[/]")
        console.print(f"Config path: [cyan]{config_manager.config_path}[/]")
        console.print("\n[bold]Model:[/]")
        console.print(f"  Provider: [cyan]{config.model.provider}[/]")
        console.print(f"  Model name: [cyan]{config.model.model_name}[/]")
        console.print(f"  Temperature: [cyan]{config.model.temperature}[/]")
        console.print(f"  Max tokens: [cyan]{config.model.max_tokens}[/]")

        console.print("\n[bold]Embedding:[/]")
        console.print(f"  Provider: [cyan]{config.embedding.provider}[/]")
        console.print(f"  Model name: [cyan]{config.embedding.model_name}[/]")

        console.print("\n[bold]Storage:[/]")
        console.print(
            f"  Persist directory: [cyan]{config.storage.persist_directory}[/]"
        )

        console.print("\n[bold]Processing:[/]")
        console.print(f"  Chunk size: [cyan]{config.processing.chunk_size}[/]")
        console.print(f"  Chunk overlap: [cyan]{config.processing.chunk_overlap}[/]")
        console.print("  Exclude patterns:")
        for pattern in config.processing.exclude_patterns:
            console.print(f"    - [cyan]{pattern}[/]")


@app.command()
def examples(
    query: str = typer.Argument(..., help="What kind of code examples to generate"),
    language: str = typer.Argument(..., help="Programming language for the examples"),
    config_path: Optional[str] = typer.Option(
        None, "--config", "-c", help="Path to the configuration file"
    ),
    output_file: Optional[str] = typer.Option(
        None, "--output", "-o", help="Path to save the generated examples"
    ),
):
    """Generate code examples."""
    # Initialize configuration
    config_manager = ConfigManager(config_path)

    # Get LLM client
    llm_client = get_llm_client(config_manager)

    # Generate examples
    console.print(f"Generating {language} code examples for: [bold]{query}[/]")

    with console.status("[cyan]Generating examples...", spinner="dots"):
        examples = llm_client.generate_examples(request=query, language=language)

    # Output the examples
    if output_file:
        with open(output_file, "w") as f:
            f.write(examples)
        console.print(f"Examples saved to [bold]{output_file}[/]")
    else:
        console.print(
            Panel(Markdown(examples), title=f"{language} Examples for {query}")
        )


def parse_start_end(line_spec: str) -> tuple[int, int]:
    """Parse a line specification (e.g., '10-20')."""
    if "-" in line_spec:
        start, end = line_spec.split("-", 1)
        return int(start), int(end)
    else:
        line = int(line_spec)
        return line, line


@app.command()
def analyze(
    file_path: str = typer.Argument(..., help="Path to the file to analyze"),
    lines: Optional[str] = typer.Option(
        None, "--lines", "-l", help="Line range to analyze (e.g. '10-20')"
    ),
    config_path: Optional[str] = typer.Option(
        None, "--config", "-c", help="Path to the configuration file"
    ),
):
    """Analyze a specific part of a file."""
    # Initialize configuration
    config_manager = ConfigManager(config_path)

    # Check if file exists
    if not os.path.exists(file_path):
        console.print(f"[bold red]Error:[/] File {file_path} does not exist")
        sys.exit(1)

    # Process the file
    console.print(f"Analyzing [bold]{file_path}[/]")

    # Initialize document processor
    doc_processor = DocumentProcessor()

    # Process the file
    document = doc_processor.process(file_path)

    # Get language
    language = str(document.metadata.language)

    # Extract specified lines if provided
    start_line, end_line = 1, document.metadata.line_count
    if lines:
        try:
            start_line, end_line = parse_start_end(lines)

            if start_line < 1 or end_line > document.metadata.line_count:
                console.print(
                    f"[bold red]Error:[/] Line range {start_line}-{end_line} is out of bounds (1-{document.metadata.line_count})"
                )
                sys.exit(1)

            content_lines = document.content.splitlines()
            code_to_analyze = "\n".join(content_lines[start_line - 1 : end_line])
        except Exception as e:
            console.print(f"[bold red]Error:[/] Invalid line range: {lines}")
            sys.exit(1)
    else:
        code_to_analyze = document.content

    # Get LLM client
    llm_client = get_llm_client(config_manager)

    # Analyze the code
    with console.status("[cyan]Analyzing code...", spinner="dots"):
        analysis = llm_client.explain_code(
            code=code_to_analyze,
            language=language,
            additional_context=f"File path: {file_path}, Lines: {start_line}-{end_line}",
        )

    # Output the analysis
    line_info = f" (lines {start_line}-{end_line})" if lines else ""
    console.print(
        Panel(
            Markdown(analysis),
            title=f"Analysis of {os.path.basename(file_path)}{line_info}",
        )
    )


@app.command()
def generate(
    path: str = typer.Argument(
        ".", help="File or directory to generate documentation for"
    ),
    output_dir: str = typer.Option(
        None, "--output", "-o", help="Output directory for documentation"
    ),
    format: str = typer.Option(
        None, "--format", "-f", help="Output format (html, markdown, rst)"
    ),
    serve: bool = typer.Option(
        False, "--serve", "-s", help="Serve documentation after generation"
    ),
    port: int = typer.Option(
        8000, "--port", "-p", help="Port to serve documentation on"
    ),
    wizard: bool = typer.Option(
        True, "--wizard/--no-wizard", help="Run interactive configuration wizard"
    ),
    name: Optional[str] = typer.Option(
        None, "--name", help="Project name for documentation"
    ),
    description: Optional[str] = typer.Option(
        None, "--description", help="Project description"
    ),
    exclude: List[str] = typer.Option(
        [], "--exclude", "-e", help="Patterns to exclude from documentation"
    ),
    include: List[str] = typer.Option(
        [], "--include", "-i", help="Directories to specifically include"
    ),
    theme: Optional[str] = typer.Option(
        None, "--theme", "-t", help="Documentation theme"
    ),
    use_saved_config: bool = typer.Option(
        False, "--use-saved", help="Use previously saved configuration"
    ),
):
    """Generate comprehensive documentation for a file or directory."""
    from docstra.core.documentation.wizard import (
        run_documentation_wizard,
        load_wizard_config,
    )
    from docstra.core.utils.file_collector import collect_files, FileCollector

    # Initialize config with default values
    config = {
        "name": os.path.basename(os.path.abspath(path)),
        "description": "",
        "version": "0.1.0",
        "include_dirs": [],
        "exclude_dirs": [".git", "__pycache__", "node_modules", "venv", ".env"],
        "exclude_files": [],
        "theme": "default",
        "output_dir": "./docs",
        "format": "html",
    }

    # Try to load saved config if requested
    if use_saved_config:
        saved_config = load_wizard_config(path)
        if saved_config:
            config.update(saved_config)
            console.print("[green]Loaded saved configuration[/]")
        else:
            console.print("[yellow]No saved configuration found, using defaults[/]")

    # Override with command line arguments
    if output_dir:
        config["output_dir"] = output_dir
    if format:
        config["format"] = format
    if name:
        config["name"] = name
    if description:
        config["description"] = description
    if exclude:
        config["exclude_dirs"] = exclude
    if include:
        config["include_dirs"] = include
    if theme:
        config["theme"] = theme

    # Run the wizard if requested and not overridden by CLI args
    if wizard and not (
        output_dir and format and name and description and (exclude or include)
    ):
        try:
            wizard_config = run_documentation_wizard(console, path)
            config.update(wizard_config)
        except KeyboardInterrupt:
            console.print("\n[yellow]Wizard cancelled, using default/CLI values[/]")

    # Print configuration summary
    console.print(
        Panel(f"[bold]Generating documentation for:[/] {config['name']}", expand=False)
    )
    console.print(f"[bold]Description:[/] {config['description']}")
    console.print(f"[bold]Output directory:[/] {config['output_dir']}")
    console.print(f"[bold]Format:[/] {config['format']}")

    if config["include_dirs"]:
        console.print(
            f"[bold]Including directories:[/] {', '.join(config['include_dirs'])}"
        )

    console.print(
        f"[bold]Excluding directories:[/] {', '.join(config['exclude_dirs'])}"
    )

    # Create output directory
    os.makedirs(config["output_dir"], exist_ok=True)

    # Initialize components
    config_manager = ConfigManager()
    llm_client = get_llm_client(config_manager)
    doc_processor = DocumentProcessor()

    # Use our file collection utility to gather files
    file_paths = collect_files(
        base_path=path,
        include_dirs=config["include_dirs"],
        exclude_dirs=config["exclude_dirs"],
        exclude_files=config["exclude_files"],
        file_extensions=FileCollector.default_code_file_extensions(),
    )

    # Process collected files
    documents = []
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as progress:
        processing_task = progress.add_task(
            "[cyan]Processing files...", total=len(file_paths)
        )

        for file_path in file_paths:
            try:
                document = doc_processor.process(file_path)
                documents.append(document)
            except Exception as e:
                console.print(f"[yellow]Error processing {file_path}: {str(e)}[/]")
            progress.update(processing_task, advance=1)

    # No files found
    if not documents:
        console.print("[bold yellow]No files found to document![/]")
        return

    # Generate documentation for each document
    doc_generator = DocumentationGenerator(
        llm_client, config["output_dir"], config["format"]
    )

    # Update generator with additional config
    doc_generator.project_name = config["name"]
    doc_generator.project_description = config["description"]
    doc_generator.project_version = config["version"]
    doc_generator.theme = config["theme"]

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Generating documentation...", total=len(documents))

        for document in documents:
            doc_generator.generate_for_document(document)
            progress.update(task, advance=1)

    # Build and organize documentation
    doc_generator.build_documentation()

    console.print(
        f"\n[bold green]Documentation generated successfully at:[/] {os.path.abspath(config['output_dir'])}"
    )
    console.print(f"[green]Documented {len(documents)} files[/]")

    # Serve documentation if requested
    if serve:
        serve_documentation(config["output_dir"], port)


# Update the serve_documentation function to use the new DocumentationGenerator
def serve_documentation(docs_dir, port=8000):
    """Serve documentation using MkDocs or a simple HTTP server."""
    from docstra.core.documentation.generator import DocumentationGenerator

    # Create a minimal generator instance just for serving
    dummy_gen = DocumentationGenerator(None, docs_dir)
    dummy_gen.serve_documentation(port)


if __name__ == "__main__":
    app()

```

```
