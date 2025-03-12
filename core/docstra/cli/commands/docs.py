"""Documentation generator command for Docstra."""

import click
from pathlib import Path

from rich.progress import Progress

from docstra.service import DocstraService
from docstra.cli.base import DocstraCommand


class DocsGeneratorCommand(DocstraCommand):
    """Command to generate documentation for Docstra."""

    def execute(
        self,
        output_dir: str = "docs",
        format: str = "markdown",
        log_level: str = None,
        log_file: str = None,
    ):
        """Execute the docs-generate command.

        Args:
            output_dir: Directory to output documentation
            format: Documentation format (markdown, rst)
            log_level: Log level to use
            log_file: Log file path
        """
        self.console.print(f"Generating documentation in [bold]{output_dir}[/bold]")

        # Initialize service
        service = self.initialize_service(log_level=log_level, log_file=log_file)

        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True, parents=True)

        # Create subdirectories
        (output_path / "api").mkdir(exist_ok=True)
        (output_path / "guides").mkdir(exist_ok=True)
        (output_path / "reference").mkdir(exist_ok=True)

        # Generate documentation structure
        with Progress() as progress:
            task = progress.add_task("Generating documentation...", total=5)

            # 1. Generate introductory docs
            progress.update(task, description="Generating introduction...")
            self._generate_introduction(service, output_path)
            progress.update(task, advance=1)

            # 2. Generate installation guide
            progress.update(task, description="Generating installation guide...")
            self._generate_installation_guide(service, output_path)
            progress.update(task, advance=1)

            # 3. Generate CLI command reference
            progress.update(task, description="Generating CLI reference...")
            self._generate_command_reference(service, output_path)
            progress.update(task, advance=1)

            # 4. Generate API reference
            progress.update(task, description="Generating API reference...")
            self._generate_api_reference(service, output_path)
            progress.update(task, advance=1)

            # 5. Generate advanced guides
            progress.update(task, description="Generating advanced guides...")
            self._generate_advanced_guides(service, output_path)
            progress.update(task, advance=1)

        self.console.print(
            f"[green]Documentation generated successfully in {output_path}[/green]"
        )

    def _generate_introduction(self, service: DocstraService, output_path: Path):
        """Generate introduction documentation.

        Args:
            service: Initialized DocstraService
            output_path: Output directory path
        """
        session_id = service.create_session()

        # Add core files to context
        service.add_context(session_id, "README.md")
        service.add_context(session_id, "__init__.py")

        # Generate introduction with LLM
        prompt = """
        Based on the provided README and code files, create an introduction 
        document for the Docstra project. Include:
        
        1. Overview of what Docstra is and its purpose
        2. Key features and capabilities
        3. How it compares to other documentation tools
        4. Intended audience and use cases
        
        Format as a well-structured Markdown document with proper headers, 
        sections, and emphasis on important points.
        """

        response = service.process_message(session_id, prompt)

        # Write to file
        with open(output_path / "index.md", "w") as f:
            f.write(self._add_frontmatter("Introduction", 1) + response)

    def _generate_installation_guide(self, service: DocstraService, output_path: Path):
        """Generate installation guide.

        Args:
            service: Initialized DocstraService
            output_path: Output directory path
        """
        session_id = service.create_session()

        # Add relevant files to context
        service.add_context(session_id, "pyproject.toml")
        service.add_context(session_id, "README.md")

        # Generate installation guide with LLM
        prompt = """
        Based on the provided pyproject.toml and README, create a detailed 
        installation guide for Docstra. Include:
        
        1. Prerequisites (Python version, etc.)
        2. Installation methods (pip, from source, etc.)
        3. Verification steps to ensure installation worked
        4. Common installation issues and troubleshooting
        5. Environment setup including API keys
        
        Format as a well-structured Markdown document with proper code blocks 
        for commands.
        """

        response = service.process_message(session_id, prompt)

        # Write to file
        with open(output_path / "guides" / "installation.md", "w") as f:
            f.write(self._add_frontmatter("Installation Guide", 2) + response)

    def _generate_command_reference(self, service: DocstraService, output_path: Path):
        """Generate CLI command reference.

        Args:
            service: Initialized DocstraService
            output_path: Output directory path
        """
        session_id = service.create_session()

        # Add CLI command files to context
        cli_files = [
            "cli/main.py",
            "cli/commands/init.py",
            "cli/commands/chat.py",
            "cli/commands/query.py",
            "cli/commands/serve.py",
            "cli/commands/reindex.py",
            "cli/commands/ingest.py",
        ]

        for file in cli_files:
            service.add_context(session_id, file)

        # Generate command reference with LLM
        prompt = """
        Based on the provided CLI implementation files, create a comprehensive
        command reference guide for Docstra. For each command:
        
        1. Provide the command syntax and all available options/arguments
        2. Explain what the command does
        3. Show example usage with sample outputs
        4. Explain any important notes or caveats
        
        Include all commands: init, chat, query, serve, reindex, ingest, etc.
        
        Format as a well-structured Markdown document with proper sections for
        each command and code blocks for examples.
        """

        response = service.process_message(session_id, prompt)

        # Write to file
        with open(output_path / "reference" / "commands.md", "w") as f:
            f.write(self._add_frontmatter("Command Reference", 2) + response)

    def _generate_api_reference(self, service: DocstraService, output_path: Path):
        """Generate API reference documentation.

        Args:
            service: Initialized DocstraService
            output_path: Output directory path
        """
        # Core API components to document
        components = [
            ("service.py", "DocstraService", "The main service class"),
            ("config.py", "DocstraConfig", "Configuration handling"),
            ("database.py", "Database", "Database abstraction"),
            ("session.py", "DocstraSession", "Session management"),
            ("retriever.py", "DocstraRetriever", "Enhanced retrieval system"),
        ]

        # Generate docs for each component
        for file, class_name, description in components:
            session_id = service.create_session()
            service.add_context(session_id, file)

            prompt = f"""
            Based on the provided code for {class_name}, create detailed API 
            reference documentation. Include:
            
            1. Class overview and purpose ({description})
            2. All public methods with their signatures, parameters, return types
            3. Important attributes
            4. Usage examples
            5. Any important notes or caveats
            
            Format as a well-structured Markdown document with proper code blocks.
            """

            response = service.process_message(session_id, prompt)

            # Clean up the class name for the filename
            filename = class_name.lower().replace("docstra", "")

            # Write to file
            with open(output_path / "api" / f"{filename}.md", "w") as f:
                f.write(
                    self._add_frontmatter(f"{class_name} API Reference", 3) + response
                )

    def _generate_advanced_guides(self, service: DocstraService, output_path: Path):
        """Generate advanced usage guides.

        Args:
            service: Initialized DocstraService
            output_path: Output directory path
        """
        # Advanced topics to cover
        topics = [
            ("Custom Model Providers", "model_provider.py"),
            ("Using the API Server", "api.py"),
            ("File Monitoring and Auto-Indexing", "file_watcher.py"),
        ]

        # Generate docs for each topic
        for topic, file in topics:
            session_id = service.create_session()
            service.add_context(session_id, file)

            # Create filename from topic
            filename = topic.lower().replace(" ", "-")

            prompt = f"""
            Based on the provided code file, create an advanced guide for "{topic}" 
            in Docstra. Include:
            
            1. Overview of the feature
            2. When and why to use it
            3. Detailed configuration options
            4. Step-by-step usage instructions
            5. Example scenarios with code samples
            6. Best practices and tips
            7. Troubleshooting common issues
            
            Format as a well-structured Markdown document with proper code blocks
            and examples.
            """

            response = service.process_message(session_id, prompt)

            # Write to file
            with open(output_path / "guides" / f"{filename}.md", "w") as f:
                f.write(self._add_frontmatter(topic, 3) + response)

    def _add_frontmatter(self, title: str, sidebar_position: int) -> str:
        """Add frontmatter to markdown files for documentation generators.

        Args:
            title: Page title
            sidebar_position: Position in sidebar

        Returns:
            Frontmatter string
        """
        return f"""---
title: {title}
sidebar_position: {sidebar_position}
---

"""


@click.command("docs-generate")
@click.option("--output", default="docs", help="Output directory for documentation")
@click.option(
    "--format",
    default="markdown",
    type=click.Choice(["markdown", "rst"]),
    help="Documentation format",
)
@click.option("--log-level", help="Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)")
@click.option("--log-file", help="Path to log file")
def docs_generate(output, format, log_level, log_file):
    """Generate documentation for Docstra using the LLM.

    This command analyzes the codebase and uses Docstra's own LLM capabilities
    to generate comprehensive documentation in the specified format.
    """
    command = DocsGeneratorCommand(working_dir=".")
    command.execute(
        output_dir=output,
        format=format,
        log_level=log_level,
        log_file=log_file,
    )
