# File: ./docstra/core/cli.py

"""
Command-line interface for the code documentation assistant.
"""

from __future__ import annotations

import os
import sys
from typing import List, Optional, Union, Dict, Any, cast

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Confirm
from rich.panel import Panel
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
)
from rich.table import Table
from rich.text import Text
from rich.align import Align

from docstra.core.config.settings import (
    ConfigManager,
    ModelProvider,
    ProcessingConfig,
    UserConfig,
)
from docstra.core.document_processing.chunking import (
    ChunkingPipeline,
    SemanticChunking,
    SyntaxAwareChunking,
)
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
from docstra.core.services.initialization_service import InitializationService
from docstra.core.services.ingestion_service import IngestionService
from docstra.core.services.query_service import QueryService
from docstra.core.services.chat_service import ChatService
from docstra.core.services.documentation_service import DocumentationService
from docstra.core.services.config_service import ConfigService
from docstra.core.tracking.llm_tracker import LLMTracker, UniversalLLMTracker
from docstra.core.utils.language_detector import LanguageDetector
from urllib.parse import quote
import re
from pathlib import Path


def display_docstra_header() -> None:
    """Display the DOCSTRA ASCII art header with 3D effect."""
    ascii_art = """
██████╗  ██████╗  ██████╗███████╗████████╗██████╗  █████╗ 
██╔══██╗██╔═══██╗██╔════╝██╔════╝╚══██╔══╝██╔══██╗██╔══██╗
██║  ██║██║   ██║██║     ███████╗   ██║   ██████╔╝███████║
██║  ██║██║   ██║██║     ╚════██║   ██║   ██╔══██╗██╔══██║
██████╔╝╚██████╔╝╚██████╗███████║   ██║   ██║  ██║██║  ██║
╚═════╝  ╚═════╝  ╚═════╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝
"""
    
    # Create a rich Text object with gradient colors for 3D effect
    header_text = Text()
    
    # Split into lines and add gradient coloring
    lines = ascii_art.strip().split('\n')
    for i, line in enumerate(lines):
        # Create a gradient effect from bright cyan to dim cyan
        if i < 2:
            style = "bright_cyan bold"
        elif i < 4:
            style = "cyan bold"
        else:
            style = "dim cyan"
        
        header_text.append(line + "\n", style=style)
    
    # Add tagline
    tagline = Text("LLM-Powered Code Documentation Assistant", style="dim white italic")
    
    # Center the header and tagline
    console.print()
    console.print(Align.center(header_text))
    console.print(Align.center(tagline))
    console.print()


def serve_documentation(docs_dir: str, port: int = 8000) -> None:
    """Serve documentation using a simple HTTP server."""
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import HTMLResponse, FileResponse
    from fastapi.staticfiles import StaticFiles
    import uvicorn

    app = FastAPI(title="Documentation Server")

    # Mount static files
    app.mount(
        "/static",
        StaticFiles(directory=os.path.join(docs_dir, "static")),
        name="static",
    )

    @app.get("/", response_class=HTMLResponse)
    async def read_index() -> HTMLResponse:
        index_path = os.path.join(docs_dir, "index.html")
        if os.path.exists(index_path):
            with open(index_path, "r") as f:
                return HTMLResponse(f.read())
        else:
            # Try other formats
            md_path = os.path.join(docs_dir, "index.md")
            if os.path.exists(md_path):
                # Convert markdown to HTML
                import markdown

                with open(md_path, "r") as f:
                    content = f.read()
                html_content = markdown.markdown(content)
                return HTMLResponse(
                    f"""
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
                )

            # If all else fails
            raise HTTPException(status_code=404, detail="Index not found")

    @app.get("/{path:path}")
    async def read_file(path: str) -> Union[FileResponse, HTMLResponse]:
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
                    return HTMLResponse(
                        f"""
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
                    )
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


def get_llm_client(
    config_manager: ConfigManager,
) -> Union[AnthropicClient, OpenAIClient, OllamaClient, LocalModelClient]:
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
            validate_connection=False,  # Don't validate during CLI operations
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
) -> None:
    """Initialize the code documentation assistant for a codebase."""
    from docstra.core.utils.file_collector import collect_files, FileCollector
    from docstra.core.config.wizard import run_init_wizard

    # Display beautiful header for init command
    display_docstra_header()

    # Detect if any options (other than the default positional argument) were provided
    import sys
    provided_options = [
        opt for opt in [
            (config_path, "--config"),
            (exclude, "--exclude"),
            (include, "--include"),
            (force, "--force"),
            (wizard is False, "--no-wizard"),
        ]
        if (opt[0] and opt[1] != "--no-wizard") or (opt[1] == "--no-wizard" and opt[0])
    ]
    # If no options were provided, run the wizard (UX-friendly default)
    run_wizard = False
    if not provided_options:
        run_wizard = True
    # If --no-wizard is explicitly set, never run the wizard
    if wizard is False:
        run_wizard = False

    # Initialize configuration
    config_manager = ConfigManager(config_path)

    # Always pass exclude patterns to initialization service so they are written to .docstraignore
    from docstra.core.services.initialization_service import InitializationService
    init_service = InitializationService(console=console)
    abs_codebase_path = os.path.abspath(codebase_path)
    init_service.initialize_project(
        codebase_path=abs_codebase_path,
        config_file_path=config_path,
        run_wizard=run_wizard,
        initial_include_patterns=include if include else None,
        initial_exclude_patterns=exclude if exclude else None,
    )

    # Reload config after initialization
    config_manager = ConfigManager(config_path)

    # Create a clean summary panel
    console.print("\n" + "─" * 60)
    console.print(f"[bold cyan]✓ Project initialized successfully![/]")
    console.print("─" * 60)
    console.print(f"📁 [bold]Codebase:[/] {abs_codebase_path}")
    console.print(f"⚙️  [bold]Configuration:[/] {config_manager.config_path}")
    console.print(f"💾 [bold]Storage:[/] {config_manager.config.storage.persist_directory}")
    console.print(f"🤖 [bold]Model:[/] {config_manager.config.model.provider} - {config_manager.config.model.model_name}")
    console.print("─" * 60)

    # Next steps with cleaner formatting
    console.print("\n[bold]📋 Next Steps:[/]")
    console.print("   1️⃣  [cyan]docstra ingest[/] - Process and index your codebase")
    console.print("   2️⃣  [cyan]docstra query[/] \"your question\" - Ask questions about your code")
    console.print("   3️⃣  [cyan]docstra chat[/] - Start an interactive chat session")

    # Optionally prompt to run ingestion now
    console.print()
    if Confirm.ask("🚀 Would you like to ingest and index your codebase now?", default=False):
        console.print()  # Add spacing before ingestion
        ingest(
            codebase_path=abs_codebase_path,
            config_path=config_path,
            exclude=exclude,
            include=include,
            force=force,
        )
    else:
        console.print("[dim]💡 Run [cyan]docstra ingest[/] when ready to process your codebase[/]")


@app.command()
def document(
    file_path: str = typer.Argument(..., help="Path to the file to document"),
    config_path: Optional[str] = typer.Option(
        None, "--config", "-c", help="Path to the configuration file"
    ),
    output_file: Optional[str] = typer.Option(
        None, "--output", "-o", help="Path to save the generated documentation"
    ),
) -> None:
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
        # Ensure documentation is a string
        documentation_str = str(documentation)

    # Output the documentation
    if output_file:
        with open(output_file, "w") as f:
            f.write(documentation_str)
        console.print(f"Documentation saved to [bold]{output_file}[/]")
    else:
        console.print(
            Panel(
                Markdown(documentation_str),
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
) -> None:
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
        # Ensure explanation is a string
        explanation_str = str(explanation)

    # Output the explanation
    if output_file:
        with open(output_file, "w") as f:
            f.write(explanation_str)
        console.print(f"Explanation saved to [bold]{output_file}[/]")
    else:
        console.print(
            Panel(
                Markdown(explanation_str),
                title=f"Explanation for {os.path.basename(file_path)}",
            )
        )


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
) -> None:
    """Generate code examples."""
    # Initialize configuration
    config_manager = ConfigManager(config_path)

    # Get LLM client
    llm_client = get_llm_client(config_manager)

    # Generate examples
    console.print(f"Generating {language} code examples for: [bold]{query}[/]")

    with console.status("[cyan]Generating examples...", spinner="dots"):
        examples = llm_client.generate_examples(request=query, language=language)
        # Ensure examples is a string
        examples_str = str(examples)

    # Output the examples
    if output_file:
        with open(output_file, "w") as f:
            f.write(examples_str)
        console.print(f"Examples saved to [bold]{output_file}[/]")
    else:
        console.print(
            Panel(Markdown(examples_str), title=f"{language} Examples for {query}")
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
) -> None:
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
) -> None:
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
        except Exception:
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
        # Ensure analysis is a string
        analysis_str = str(analysis)

    # Output the analysis
    line_info = f" (lines {start_line}-{end_line})" if lines else ""
    console.print(
        Panel(
            Markdown(analysis_str),
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
) -> None:
    """Generate comprehensive documentation for a file or directory."""
    from docstra.core.documentation.wizard import run_documentation_wizard
    from docstra.core.utils.file_collector import collect_files, FileCollector

    # Initialize config with default values
    config = {
        "name": os.path.basename(os.path.abspath(path)),
        "description": "",
        "version": "0.1.0",
        "include_dirs": [],
        # Create ProcessingConfig with required parameters
        "exclude_dirs": ProcessingConfig(
            chunk_size=800, chunk_overlap=100
        ).exclude_patterns,
        "exclude_files": [],
        "theme": "default",
        "output_dir": "./docs",
        "format": "html",
    }

    # Try to load saved config if requested
    if use_saved_config:
        # Create a helper function to simulate load_wizard_config
        # In the real implementation, this would be part of the wizard module
        def load_saved_config(path: str) -> Optional[Dict[str, Any]]:
            """Load saved configuration from a file."""
            config_path = os.path.join(path, ".docstra", "docs_config.json")
            if os.path.exists(config_path):
                import json

                with open(config_path) as f:
                    # Cast the result to Dict[str, Any] to satisfy mypy
                    return cast(Dict[str, Any], json.load(f))
            return None  # Explicitly return None

        saved_config = load_saved_config(path)
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
        # Convert glob patterns to gitignore patterns
        config["exclude_dirs"] = [
            pattern.replace("**/", "").replace("/**", "") for pattern in exclude
        ]
    if include:
        config["include_dirs"] = include
    if theme:
        config["theme"] = theme

    # Run the wizard if requested and not overridden by CLI args
    if wizard and not (
        output_dir and format and name and description and (exclude or include)
    ):
        try:
            # Create a config manager for the wizard
            config_manager = ConfigManager()
            # Assume wizard updates config in-place and doesn't return anything
            # This is a safe assumption based on the error message
            run_documentation_wizard(console, path, config_manager)
            # Since run_documentation_wizard doesn't return a value, no update needed
        except KeyboardInterrupt:
            console.print("\n[yellow]Wizard cancelled, using default/CLI values[/]")
        except Exception as e:
            console.print(f"\n[red]Error in wizard: {e}[/]")
            console.print("[yellow]Proceeding with default/CLI values[/]")

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

    # Create output directory - ensure string type
    output_dir_str = str(config["output_dir"])
    os.makedirs(output_dir_str, exist_ok=True)

    # Initialize components
    config_manager = ConfigManager()
    llm_client = get_llm_client(config_manager)
    doc_processor = DocumentProcessor()

    # Use our file collection utility to gather files
    # Convert to proper List[str] types
    include_dirs_list: List[str] = list(config["include_dirs"])
    exclude_dirs_list: List[str] = list(config["exclude_dirs"])
    exclude_files_list: List[str] = list(config["exclude_files"])

    file_paths = collect_files(
        base_path=path,
        include_dirs=include_dirs_list,
        exclude_dirs=exclude_dirs_list,
        exclude_files=exclude_files_list,
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
                # Convert Path to str for document processor
                document = doc_processor.process(str(file_path))
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
        llm_client,
        # Convert config values to the expected types
        output_dir=(
            str(config["output_dir"][0])
            if isinstance(config["output_dir"], list)
            else str(config["output_dir"])
        ),
        format=(
            str(config["format"][0])
            if isinstance(config["format"], list)
            else str(config["format"])
        ),
    )

    # Update generator with additional config - use setattr for attributes that might not exist
    # This is a temporary solution until the DocumentationGenerator class is updated
    try:
        setattr(doc_generator, "project_name", config["name"])
        setattr(doc_generator, "project_description", config["description"])
        setattr(doc_generator, "project_version", config["version"])
        setattr(doc_generator, "theme", config["theme"])
    except AttributeError:
        # If these attributes don't exist, log a warning but continue
        console.print("[yellow]Warning: Unable to set all documentation attributes.[/]")
        console.print("[yellow]Some customization options may not be applied.[/]")

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

    # Ensure output_dir is a string for os.path.abspath
    output_dir_abs = os.path.abspath(output_dir_str)
    console.print(
        f"\n[bold green]Documentation generated successfully at:[/] {output_dir_abs}"
    )
    console.print(f"[green]Documented {len(documents)} files[/]")

    # Serve documentation if requested
    if serve:
        serve_documentation_from_generator(output_dir_str, port)


# Update the serve_documentation function to use the new DocumentationGenerator
def serve_documentation_from_generator(docs_dir: str, port: int = 8000) -> None:
    """Serve documentation using MkDocs or a simple HTTP server."""
    from docstra.core.documentation.generator import DocumentationGenerator

    # Create a minimal generator instance just for serving
    dummy_gen = DocumentationGenerator(None, docs_dir)
    dummy_gen.serve_documentation(port)


# Helper function to load or initialize config
def load_or_init_config(config_path: Optional[str] = None) -> UserConfig:
    """Loads configuration or initializes if it doesn't exist."""
    try:
        # ConfigManager handles loading or creating the default config during init
        config_manager = ConfigManager(config_path=config_path)
        return config_manager.config
    except Exception as e:
        console.print(f"[bold red]Error loading or initializing configuration:[/] {e}")
        raise typer.Exit(code=1)


def get_llm_tracker() -> Optional[UniversalLLMTracker]:
    """Get LLM tracker instance, creating it if needed."""
    try:
        from docstra.core.tracking.llm_tracker import get_global_tracker
        return get_global_tracker()
    except Exception as e:
        console.print(f"[yellow]Warning: Failed to initialize LLM tracking: {e}[/]")
        return None


def create_services_for_config(user_config: UserConfig) -> tuple:
    """Create service instances for the given configuration.
    
    Returns:
        Tuple of (ingestion_service, query_service, chat_service, documentation_service)
    """
    llm_tracker = get_llm_tracker()
    callbacks = [llm_tracker] if llm_tracker else None
    
    ingestion_service = IngestionService(
        console=console, callbacks=callbacks
    )
    query_service = QueryService(
        user_config=user_config,
        console=console,
        callbacks=callbacks,
    )
    chat_service = ChatService(
        user_config=user_config,
        console=console,
        callbacks=callbacks,
    )
    documentation_service = DocumentationService(
        user_config=user_config,
        console=console,
        callbacks=callbacks,
    )
    
    return ingestion_service, query_service, chat_service, documentation_service


# Initialize non-LLM services that don't require configuration
config_service = ConfigService(console=console)
init_service = InitializationService(console=console)

# Add ingest command - separate from init according to refactoring plan
@app.command()
def ingest(
    codebase_path: str = typer.Argument(".", help="Path to the codebase to ingest"),
    config_path: Optional[str] = typer.Option(
        None, "--config", "-c", help="Path to the configuration file"
    ),
    exclude: List[str] = typer.Option(
        [], "--exclude", "-e", help="Patterns to exclude from ingestion"
    ),
    include: List[str] = typer.Option(
        [], "--include", "-i", help="Directories to specifically include"
    ),
    force: bool = typer.Option(
        False, "--force", "-f", help="Force reindexing of the codebase"
    ),
) -> None:
    """Ingest and index a codebase for querying and documentation.
    
    This command processes your codebase files, generates embeddings, and creates
    searchable indexes. For OpenAI embeddings, token usage and costs are tracked
    and displayed during the process.
    """
    # Show initial information
    abs_codebase_path = Path(codebase_path).resolve()
    
    user_config = load_or_init_config(config_path)

    # Update config with command-line overrides
    if exclude or include:
        # Make a copy of the user_config for modification
        updated_config = user_config

        # Create or get the ingestion configuration
        if updated_config.ingestion is None:
            from docstra.core.config.settings import IngestionConfig

            # Create with default values and override as needed
            updated_config.ingestion = IngestionConfig(
                include_dirs=None, exclude_patterns=[]
            )

        # Update exclude patterns
        if exclude:
            updated_config.ingestion.exclude_patterns = exclude

        # Update include dirs
        if include:
            updated_config.ingestion.include_dirs = include

        # Use the updated config
        user_config = updated_config

    # Create a clean header for ingestion
    console.print(Panel(
        f"[bold]🚀 Processing Codebase[/]\n"
        f"📁 [dim]{abs_codebase_path}[/]\n"
        f"🤖 [dim]{user_config.model.provider} - {user_config.model.model_name}[/]\n"
        f"🔗 [dim]{user_config.embedding.provider} - {user_config.embedding.model_name}[/]" +
        (f"\n⚠️  [yellow]OpenAI embeddings - API costs will apply[/]" if user_config.embedding.provider.lower() == "openai" else "") +
        (f"\n🔄 [yellow]Force mode - will reindex existing data[/]" if force else ""),
        style="bold blue",
        expand=False
    ))

    # Create ingestion service for this operation
    ingestion_service, _, _, _ = create_services_for_config(user_config)
    
    # Run ingestion using the service
    success = ingestion_service.ingest_codebase(
        codebase_path=codebase_path, user_config=user_config, force=force
    )

    if not success:
        console.print("[bold red]Ingestion failed.[/]")
        raise typer.Exit(code=1)
    
    # Show next steps with emojis and cleaner formatting
    console.print("\n" + "─" * 50)
    console.print("[bold green]🎉 Ingestion Complete![/]")
    console.print("─" * 50)
    console.print("[bold]🔍 Try these commands:[/]")
    console.print("   • [cyan]docstra query[/] \"your question\" - Ask questions about your code")
    console.print("   • [cyan]docstra chat[/] - Start an interactive chat session")
    console.print("   • [cyan]docstra generate[/] - Generate comprehensive documentation")
    console.print("─" * 50)


def format_file_link(abs_path: str, start_line, end_line) -> str:
    """Format a link with line numbers for Rich clickable links."""
    file_url = f"{quote(abs_path)}"
    output = f"{file_url}"
    if start_line != "?" and end_line != "?":
        output += f":{start_line}"
        if start_line == end_line:
            output += f" (#L{start_line})"
        elif start_line < end_line:
            output += f" (#L{start_line}-L{end_line})"
    
    return f"[cyan]{output}[/cyan]"


def postprocess_llm_output_with_links(answer: str, sources: list) -> str:
    """
    Postprocess the LLM output to replace file/method/class references with clickable Rich links if possible.
    This scans for file references in the answer and replaces them with [link=...]...[/link] using the sources' metadata.
    """
    # Build a mapping from file/method/class names to file links
    file_links = {}
    for source in sources:
        meta = source.get("metadata", {})
        filepath = meta.get("document_id", "")
        start_line = meta.get("start_line", "?")
        end_line = meta.get("end_line", "?")
        try:
            abs_path = str(Path(filepath).resolve())
        except Exception:
            abs_path = filepath
        display = abs_path
        if start_line != "?" and end_line != "?":
            if start_line == end_line:
                display = f"{abs_path}:{start_line}"
            else:
                display = f"{abs_path}:{start_line}-{end_line}"
        file_url = format_file_link(abs_path, start_line, end_line)
        # Add by filename
        file_links[os.path.basename(abs_path)] = (file_url, display)
        # Add by full path
        file_links[abs_path] = (file_url, display)
        # Add by method/class name if available
        for key in ("symbol", "function", "class"):
            if key in meta:
                file_links[meta[key]] = (file_url, display)

    # Regex to find file references (filenames, file.py:123, etc.)
    file_ref_pattern = re.compile(r"([\w\-/]+\.py(?::\d+(?:-\d+)?)?)")

    def replacer(match):
        ref = match.group(1)
        # Try to find a link for this reference
        for key, (url, display) in file_links.items():
            if ref == key or ref in display or ref in key:
                return f"[link={url}][cyan]{ref}[/cyan][/link]"
        return ref  # No link found

    # Replace file references in the answer
    processed = file_ref_pattern.sub(replacer, answer)
    return processed


# Add query command - refactored from ask
@app.command()
def query(
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
) -> None:
    """Ask a question about the codebase and get a precise answer."""
    # Get configuration
    user_config = load_or_init_config(config_path)

    # Create query service for this operation
    _, query_service_with_config, _, _ = create_services_for_config(user_config)

    # Validate LLM connection if using Ollama
    if user_config.model.provider == ModelProvider.OLLAMA:
        from docstra.core.llm.ollama import OllamaClient
        if isinstance(query_service_with_config.llm_client, OllamaClient):
            is_connected, message = query_service_with_config.llm_client.validate_connection()
            if not is_connected:
                console.print(f"[bold red]Error:[/] {message}")
                raise typer.Exit(code=1)

    # Call answer_question with the right parameters
    answer, sources = query_service_with_config.answer_question(
        question=question, codebase_path_str=codebase_path, n_results=n_results
    )

    # Postprocess the answer to add clickable links
    processed_answer = postprocess_llm_output_with_links(str(answer), sources)

    # Display the answer
    console.print(Panel(Markdown(processed_answer), title="Answer"))

    # Show sources if available
    if sources:
        console.print("\n[bold]Sources:[/]")
        for i, source in enumerate(sources[:5]):
            meta = source.get("metadata", {})
            filepath = meta.get("document_id", "Unknown")
            start_line = meta.get("start_line", "?")
            end_line = meta.get("end_line", "?")
            try:
                abs_path = str(Path(filepath).resolve())
            except Exception:
                abs_path = filepath
            link_str = format_file_link(abs_path, start_line, end_line)
            console.print(f"[bold]{i + 1}.[/] {link_str}")

    # Display token usage statistics if tracking is enabled
    llm_tracker = get_llm_tracker()
    if llm_tracker and llm_tracker.session_stats:
        console.print("\n[dim]LLM Usage:[/dim]")
        # Get the last usage from session stats
        usage = llm_tracker.session_stats[-1]
        console.print(f"[dim]Input tokens: {usage.get('input_tokens', 'N/A')}[/dim]")
        console.print(f"[dim]Output tokens: {usage.get('output_tokens', 'N/A')}[/dim]")
        if "cost_usd" in usage:
            console.print(f"[dim]Approximate cost: ${usage.get('cost_usd', 0):.5f}[/dim]")


# Add chat command - new functionality per refactoring plan
@app.command()
def chat(
    codebase_path: str = typer.Argument(
        ".", help="Path to the codebase for the chat session"
    ),
    config_path: Optional[str] = typer.Option(
        None, "--config", "-c", help="Path to the configuration file"
    ),
    session_id: Optional[str] = typer.Option(
        None, "--session-id", "-s", help="Resume an existing chat session by ID"
    ),
    new_session: bool = typer.Option(
        False, "--new", "-n", help="Start a new session even if session-id is provided"
    ),
    list_sessions: bool = typer.Option(
        False, "--list", "-l", help="List available chat sessions"
    ),
    delete_session: Optional[str] = typer.Option(
        None, "--delete", "-d", help="Delete a chat session by ID"
    ),
) -> None:
    """Start an interactive chat session with the codebase assistant."""
    # Get configuration
    user_config = load_or_init_config(config_path)

    # Create chat service for this operation
    _, _, chat_service, _ = create_services_for_config(user_config)

    # Validate LLM connection if using Ollama
    if user_config.model.provider == ModelProvider.OLLAMA:
        from docstra.core.llm.ollama import OllamaClient
        if hasattr(chat_service, 'llm_client') and isinstance(chat_service.llm_client, OllamaClient):
            is_connected, message = chat_service.llm_client.validate_connection()
            if not is_connected:
                console.print(f"[bold red]Error:[/] {message}")
                raise typer.Exit(code=1)

    # Handle session management options
    if list_sessions:
        sessions = chat_service.list_sessions()
        if not sessions:
            console.print("[yellow]No chat sessions found.[/]")
        return

        console.print("[bold]Available chat sessions:[/]")
        for i, session in enumerate(sessions):
            console.print(
                f"[bold]{i + 1}.[/] [cyan]{session['name']}[/] "
                f"(ID: {session['id']}, Last accessed: {session['last_accessed_at']})"
            )
        return

    if delete_session:
        success = chat_service.delete_session(delete_session)
        if success:
            console.print(f"[green]Session {delete_session} deleted successfully.[/]")
        else:
            console.print(f"[red]Failed to delete session {delete_session}.[/]")
        return

    # Start or resume a session
    chat_service.start_new_session(codebase_path)

    # Interactive chat loop
    console.print(
        "[bold]Chat session started. Type 'exit' or 'quit' to end the session.[/]"
    )
    console.print("[bold]Type 'help' for available commands.[/]")

    while True:
        try:
            # Get user input
            user_input = input("\n[You]: ")

            # Check for exit/quit command
            if user_input.lower() in ["exit", "quit"]:
                console.print("[bold]Ending chat session.[/]")
                break

            # Check for help command
            if user_input.lower() == "help":
                console.print("\n[bold]Available commands:[/]")
                console.print("  [cyan]exit/quit[/] - End the chat session")
                console.print("  [cyan]help[/] - Show this help message")
                console.print("  [cyan]clear[/] - Clear the screen")
                console.print("  [cyan]stats[/] - Show token usage statistics")
                continue

            # Check for clear command
            if user_input.lower() == "clear":
                os.system("cls" if os.name == "nt" else "clear")
                continue

            # Check for stats command
            if user_input.lower() == "stats":
                llm_tracker = get_llm_tracker()
                if llm_tracker:
                    session_summary = llm_tracker.get_session_summary()
                    if "message" in session_summary:
                        console.print(f"\n[yellow]{session_summary['message']}[/]")
                    else:
                        console.print("\n[bold]Session Statistics:[/]")
                        session_stats = session_summary.get("session_summary", {})
                        console.print(
                            f"Total requests: {session_stats.get('total_requests', 0)}"
                        )
                        console.print(
                            f"Total input tokens: {session_stats.get('total_input_tokens', 0)}"
                        )
                        console.print(
                            f"Total output tokens: {session_stats.get('total_output_tokens', 0)}"
                        )
                        console.print(f"Total cost: ${session_stats.get('total_cost', 0):.5f}")
                        console.print(f"Total duration: {session_stats.get('total_duration_ms', 0):.0f} ms")
                else:
                    console.print("\n[yellow]LLM tracking not available.[/yellow]")
                continue

            # Get response from the chat service
            with console.status("[cyan]Thinking...[/]", spinner="dots"):
                response = chat_service.get_response(user_input)

            # Display the response
            console.print(f"\n[Assistant]: {response}")

        except KeyboardInterrupt:
            console.print("\n[bold]Chat session interrupted.[/]")
            break
        except EOFError:
            console.print("\n[bold]Chat session ended.[/]")
            break
        except Exception as e:
            console.print(f"\n[bold red]Error in chat: {e}[/]")


@app.command()
def detect(
    codebase_path: str = typer.Argument(".", help="Path to the codebase to analyze"),
    show_patterns: bool = typer.Option(
        False, "--show-patterns", help="Show generated ignore patterns"
    ),
) -> None:
    """Detect languages and frameworks in a codebase and show recommended ignore patterns."""
    console.print(Panel("Codebase Language & Framework Detection", expand=False))
    
    # Initialize detector
    detector = LanguageDetector(codebase_path)
    
    # Get detection summary
    with console.status("[cyan]Analyzing codebase...", spinner="dots"):
        summary = detector.get_detection_summary()
    
    # Display results
    console.print(f"\n[bold]Codebase Analysis Results for:[/] {Path(codebase_path).resolve()}")
    console.print(f"[bold]Primary Language:[/] [green]{summary['primary_language']}[/]")
    console.print(f"[bold]Codebase Type:[/] [green]{summary['codebase_type']}[/]")
    
    # Show language breakdown
    if summary['languages']:
        console.print("\n[bold]Languages Detected:[/]")
        for language, count in sorted(summary['languages'].items(), key=lambda x: x[1], reverse=True):
            console.print(f"  • [cyan]{language}[/]: {count} files")
    
    # Show frameworks
    if summary['frameworks']:
        console.print("\n[bold]Frameworks/Tools Detected:[/]")
        for framework in sorted(summary['frameworks']):
            console.print(f"  • [yellow]{framework}[/]")
    
    # Show pattern count
    console.print(f"\n[bold]Recommended Ignore Patterns:[/] {summary['total_patterns']} patterns")
    
    # Show patterns if requested
    if show_patterns:
        console.print("\n[bold]Generated Ignore Patterns:[/]")
        for pattern in summary['ignore_patterns']:
            console.print(f"  {pattern}")
    else:
        console.print("[dim]Use --show-patterns to see the full list[/]")
    
    # Show recommendations
    console.print("\n[bold]Recommendations:[/]")
    if summary['total_patterns'] < 20:
        console.print("  • [green]Lightweight pattern set - good for performance[/]")
    elif summary['total_patterns'] > 50:
        console.print("  • [yellow]Large pattern set - consider reviewing for optimization[/]")
    else:
        console.print("  • [green]Balanced pattern set for your project type[/]")
    
    if summary['codebase_type'] == "web_frontend":
        console.print("  • [blue]Consider adding framework-specific build directories to .gitignore[/]")
    elif summary['codebase_type'] == "python":
        console.print("  • [blue]Virtual environment directories are automatically excluded[/]")
    elif summary['codebase_type'] == "mobile":
        console.print("  • [blue]Platform-specific build artifacts are excluded[/]")


@app.command()
def usage(
    config_path: Optional[str] = typer.Option(
        None, "--config", "-c", help="Path to the configuration file"
    ),
    days: int = typer.Option(
        30, "--days", "-d", help="Number of days to include in usage summary"
    ),
    detailed: bool = typer.Option(
        False, "--detailed", help="Show detailed usage breakdown"
    ),
) -> None:
    """Show LLM and embedding usage statistics and costs."""
    console.print(Panel("Usage Statistics", expand=False))
    
    # Get LLM usage from tracker
    llm_tracker = get_llm_tracker()
    if llm_tracker:
        # Get session summary from the new tracker
        session_summary = llm_tracker.get_session_summary()
        
        if "message" in session_summary:
            console.print(f"[yellow]{session_summary['message']}[/]")
        else:
            # Create LLM usage table
            llm_table = Table(title="LLM Usage Summary", show_header=True, header_style="bold cyan")
            llm_table.add_column("Metric", style="cyan")
            llm_table.add_column("Value", justify="right", style="green")
            
            session_stats = session_summary.get("session_summary", {})
            llm_table.add_row("Total requests", str(session_stats.get("total_requests", 0)))
            llm_table.add_row("Input tokens", f"{session_stats.get('total_input_tokens', 0):,}")
            llm_table.add_row("Output tokens", f"{session_stats.get('total_output_tokens', 0):,}")
            llm_table.add_row("Total cost", f"${session_stats.get('total_cost', 0):.4f}")
            llm_table.add_row("Total duration", f"{session_stats.get('total_duration_ms', 0):.0f} ms")
            
            console.print(llm_table)
            
            # Show breakdown by provider if detailed
            if detailed:
                by_provider = session_summary.get("by_provider", {})
                
                if by_provider:
                    console.print("\n[bold]Breakdown by Provider:[/]")
                    provider_table = Table(show_header=True, header_style="bold blue")
                    provider_table.add_column("Provider", style="cyan")
                    provider_table.add_column("Requests", justify="right")
                    provider_table.add_column("Input Tokens", justify="right")
                    provider_table.add_column("Output Tokens", justify="right")
                    provider_table.add_column("Cost", justify="right", style="green")
                    
                    for provider, stats in sorted(by_provider.items()):
                        provider_table.add_row(
                            provider,
                            str(stats.get("requests", 0)),
                            f"{stats.get('input_tokens', 0):,}",
                            f"{stats.get('output_tokens', 0):,}",
                            f"${stats.get('cost', 0):.4f}"
                        )
                    
                    console.print(provider_table)
    else:
        console.print("[yellow]LLM usage tracking not available.[/]")
    
    # Show embedding usage information
    console.print("\n[dim]Note: Embedding usage during ingestion is shown at the end of the ingestion process.[/]")
    console.print("[dim]For current session embedding costs, check the output of 'docstra ingest'.[/]")


if __name__ == "__main__":
    app()
