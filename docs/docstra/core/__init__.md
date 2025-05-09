---
language: documenttype.markdown
source_file: /Users/jorgenosberg/development/docstra/docs/docstra/core/__init__.md
summary: 'docstra: LLM-powered Code Documentation Assistant

  ============================================='
title: __init__

---

# docstra: LLM-powered Code Documentation Assistant
=============================================

## Overview

The `docstra` module is a Python package that provides an LLM (Large Language Model) powered code documentation assistant. It utilizes various natural language processing techniques to analyze and generate documentation for codebases.

## Classes

### docstraant

#### Attributes

*   `config_manager`: An instance of `ConfigManager`, responsible for managing the configuration file.
*   `config`: The parsed configuration from the `config_manager`.
*   `storage`: An instance of `ChromaDBStorage`, used to store and retrieve data.
*   `embedding_generator`: An instance of `EmbeddingFactory`, generating embeddings for code analysis.
*   `document_processor`: An instance of `DocumentProcessor`, responsible for processing documents.
*   `code_parser`: An instance of `CodeParser`, parsing code into a structured format.
*   `chunking_pipeline`: A pipeline of chunking strategies, used to segment code into smaller units.
*   `document_indexer`: An instance of `DocumentIndexer`, indexing documents in the storage.
*   `code_indexer`: An instance of `CodebaseIndexer`, indexing code in the storage.
*   `retriever`: An instance of `ChromaRetriever`, retrieving relevant chunks from the index.
*   `hybrid_retriever`: A hybrid retriever that combines the strengths of multiple retrieval strategies.
*   `llm_client`: An instance of an LLM client, used to generate documentation and explanations.

#### Methods

*   `__init__(config_path=None)`: Initializes the `docstraant` instance with a configuration file path.
*   `setup_components()`: Sets up components based on the configuration.
*   `_setup_llm_client()`: Sets up the LLM client based on the configuration.
*   `process_file(filepath: str) -> Document`: Processes a file and prepares it for documentation.
*   `index_file(filepath: str) -> str`: Processes and indexes a file.
*   `document_code(code: str, language: str, additional_context: str = "") -> str`: Generates documentation for code.
*   `explain_code(code: str, language: str, additional_context: str = "") -> str`: Generates an explanation for code.
*   `document_file(filepath: str) -> str`: Generates documentation for a file.
*   `explain_file(filepath: str) -> str`: Generates an explanation for a file.
*   `answer_question(question: str, n_results: int = 5) -> str`: Answers a question about the codebase.
*   `generate_examples(request: str, language: str) -> str`: Generates code examples.

## Functions

### process_file(filepath: str) -> Document

Processes a file and prepares it for documentation.

#### Parameters

*   `filepath`: Path to the file to process

#### Returns

*   Processed document

### index_file(filepath: str) -> str

Processes and indexes a file.

#### Parameters

*   `filepath`: Path to the file to index

#### Returns

*   Document ID

### document_code(code: str, language: str, additional_context: str = "") -> str

Generates documentation for code.

#### Parameters

*   `code`: Code to document
*   `language`: Programming language
*   `additional_context`: Additional context about the code (default: "")

#### Returns

*   Generated documentation

### explain_code(code: str, language: str, additional_context: str = "") -> str

Generates an explanation for code.

#### Parameters

*   `code`: Code to explain
*   `language`: Programming language
*   `additional_context`: Additional context about the code (default: "")

#### Returns

*   Generated explanation

### document_file(filepath: str) -> str

Generates documentation for a file.

#### Parameters

*   `filepath`: Path to the file to document

#### Returns

*   Generated documentation

### explain_file(filepath: str) -> str

Generates an explanation for a file.

#### Parameters

*   `filepath`: Path to the file to explain

#### Returns

*   Generated explanation

### answer_question(question: str, n_results: int = 5) -> str

Answers a question about the codebase.

#### Parameters

*   `question`: Question to answer
*   `n_results`: Number of results to retrieve (default: 5)

#### Returns

*   Generated answer

### generate_examples(request: str, language: str) -> str

Generates code examples.

#### Parameters

*   `request`: Request for examples
*   `language`: Programming language

#### Returns

*   Generated examples

## Usage Examples

Here are some example use cases for the `docstra` module:

```python
# Initialize the docstra instance with a configuration file path
docstra = Docstra(config_path='config.json')

# Process a file and prepare it for documentation
document = docstra.process_file('path/to/file.py')

# Generate documentation for code
code_doc = docstra.document_code(document.content, 'Python', 'This is some additional context.')

# Generate an explanation for code
code_exp = docstra.explain_code(code_doc, 'Python')

# Generate documentation for a file
file_doc = docstra.document_file('path/to/file.py')

# Generate an explanation for a file
file_exp = docstra.explain_file('path/to/file.py')
```

## Important Dependencies

The `docstra` module depends on the following libraries:

*   `ChromaDBStorage`: A storage library used to store and retrieve data.
*   `EmbeddingFactory`: An embedding factory library used to generate embeddings for code analysis.
*   `DocumentProcessor`: A document processor library responsible for processing documents.
*   `CodeParser`: A code parser library parsing code into a structured format.
*   `ChunkingPipeline`: A chunking pipeline library used to segment code into smaller units.

## Notes

The `docstra` module has the following limitations and edge cases:

*   The module assumes that the configuration file path is provided correctly.
*   The module may not work properly with very large files due to memory constraints.
*   The module uses a simple chunking strategy, which may not be optimal for all use cases.

## API Documentation

The `docstra` module provides the following APIs:

### `__init__(config_path=None)`

Initializes the `docstra` instance with a configuration file path.

#### Parameters

*   `config_path`: Path to the configuration file (default: None)

#### Returns

*   The initialized `docstra` instance

### `setup_components()`

Sets up components based on the configuration.

#### Returns

*   None

### `process_file(filepath: str) -> Document`

Processes a file and prepares it for documentation.

#### Parameters

*   `filepath`: Path to the file to process

#### Returns

*   Processed document

### `index_file(filepath: str) -> str`

Processes and indexes a file.

#### Parameters

*   `filepath`: Path to the file to index

#### Returns

*   Document ID

### `document_code(code: str, language: str, additional_context: str = "") -> str`

Generates documentation for code.

#### Parameters

*   `code`: Code to document
*   `language`: Programming language
*   `additional_context`: Additional context about the code (default: "")

#### Returns

*   Generated documentation

### `explain_code(code: str, language: str, additional_context: str = "") -> str`

Generates an explanation for code.

#### Parameters

*   `code`: Code to explain
*   `language`: Programming language
*   `additional_context`: Additional context about the code (default: "")

#### Returns

*   Generated explanation

### `document_file(filepath: str) -> str`

Generates documentation for a file.

#### Parameters

*   `filepath`: Path to the file to document

#### Returns

*   Generated documentation

### `explain_file(filepath: str) -> str`

Generates an explanation for a file.

#### Parameters

*   `filepath`: Path to the file to explain

#### Returns

*   Generated explanation

### `answer_question(question: str, n_results: int = 5) -> str`

Answers a question about the codebase.

#### Parameters

*   `question`: Question to answer
*   `n_results`: Number of results to retrieve (default: 5)

#### Returns

*   Generated answer

### `generate_examples(request: str, language: str) -> str`

Generates code examples.

#### Parameters

*   `request`: Request for examples
*   `language`: Programming language

#### Returns

*   Generated examples


## Source Code

```documenttype.markdown
---
language: documenttype.python
source_file: /Users/jorgenosberg/development/docstra/docstra/core/__init__.py
summary: 'docstra: LLM-powered Code Documentation Assistant

  ============================================='
title: __init__

---

# docstra: LLM-powered Code Documentation Assistant
=============================================

## Overview

The `docstra` module is a Python package that provides an LLM (Large Language Model) powered code documentation assistant. It utilizes various natural language processing techniques to analyze and generate documentation for codebases.

## Classes

### docstraant

#### Attributes

*   `config_manager`: An instance of `ConfigManager`, responsible for managing the configuration file.
*   `config`: The parsed configuration from the `config_manager`.
*   `storage`: An instance of `ChromaDBStorage`, used to store and retrieve data.
*   `embedding_generator`: An instance of `EmbeddingFactory`, generating embeddings for code analysis.
*   `document_processor`: An instance of `DocumentProcessor`, responsible for processing documents.
*   `code_parser`: An instance of `CodeParser`, parsing code into a structured format.
*   `chunking_pipeline`: A pipeline of chunking strategies, used to segment code into smaller units.
*   `document_indexer`: An instance of `DocumentIndexer`, indexing documents in the storage.
*   `code_indexer`: An instance of `CodebaseIndexer`, indexing code in the storage.
*   `retriever`: An instance of `ChromaRetriever`, retrieving relevant chunks from the index.
*   `hybrid_retriever`: A hybrid retriever that combines the strengths of multiple retrieval strategies.
*   `llm_client`: An instance of an LLM client, used to generate documentation and explanations.

#### Methods

*   `__init__(config_path=None)`: Initializes the `docstraant` instance with a configuration file path.
*   `setup_components()`: Sets up components based on the configuration.
*   `_setup_llm_client()`: Sets up the LLM client based on the configuration.
*   `process_file(filepath: str) -> Document`: Processes a file and prepares it for documentation.
*   `index_file(filepath: str) -> str`: Processes and indexes a file.
*   `document_code(code: str, language: str, additional_context: str = "") -> str`: Generates documentation for code.
*   `explain_code(code: str, language: str, additional_context: str = "") -> str`: Generates an explanation for code.
*   `document_file(filepath: str) -> str`: Generates documentation for a file.
*   `explain_file(filepath: str) -> str`: Generates an explanation for a file.
*   `answer_question(question: str, n_results: int = 5) -> str`: Answers a question about the codebase.
*   `generate_examples(request: str, language: str) -> str`: Generates code examples.

## Functions

### process_file(filepath: str) -> Document

Processes a file and prepares it for documentation.

#### Parameters

*   `filepath`: Path to the file to process

#### Returns

*   Processed document

### index_file(filepath: str) -> str

Processes and indexes a file.

#### Parameters

*   `filepath`: Path to the file to index

#### Returns

*   Document ID

### document_code(code: str, language: str, additional_context: str = "") -> str

Generates documentation for code.

#### Parameters

*   `code`: Code to document
*   `language`: Programming language
*   `additional_context`: Additional context about the code (default: "")

#### Returns

*   Generated documentation

### explain_code(code: str, language: str, additional_context: str = "") -> str

Generates an explanation for code.

#### Parameters

*   `code`: Code to explain
*   `language`: Programming language
*   `additional_context`: Additional context about the code (default: "")

#### Returns

*   Generated explanation

### document_file(filepath: str) -> str

Generates documentation for a file.

#### Parameters

*   `filepath`: Path to the file to document

#### Returns

*   Generated documentation

### explain_file(filepath: str) -> str

Generates an explanation for a file.

#### Parameters

*   `filepath`: Path to the file to explain

#### Returns

*   Generated explanation

### answer_question(question: str, n_results: int = 5) -> str

Answers a question about the codebase.

#### Parameters

*   `question`: Question to answer
*   `n_results`: Number of results to retrieve (default: 5)

#### Returns

*   Generated answer

### generate_examples(request: str, language: str) -> str

Generates code examples.

#### Parameters

*   `request`: Request for examples
*   `language`: Programming language

#### Returns

*   Generated examples

## Dependencies

The `docstra` module depends on the following external libraries:

*   `ChromaDBStorage`
*   `EmbeddingFactory`
*   `DocumentProcessor`
*   `CodeParser`
*   `ChunkingPipeline`
*   `DocumentIndexer`
*   `CodebaseIndexer`
*   `ChromaRetriever`
*   `HybridRetriever`
*   `LLM clients (Anthropic, OpenAIClient, OllamaClient, LocalModelClient)`

## Notes

The `docstra` module is designed to be highly customizable through its configuration file. The user can adjust various parameters, such as the LLM provider, chunking strategy, and indexing settings, to suit their specific needs.

However, please note that this documentation is subject to change as the project evolves. It's recommended to check the `README.md` file for the most up-to-date information on usage and configuration.


## Source Code

```documenttype.python
# File: ./docstra/core/__init__.py

"""
docstra: LLM-powered code documentation assistant.
"""

__version__ = "0.1.0"

from docstra.core.config.settings import (
    ConfigManager,
    ModelProvider,
    UserConfig,
)
from docstra.core.document_processing.chunking import (
    ChunkingPipeline,
    ChunkingStrategy,
    SemanticChunking,
    SlidingWindowChunking,
    SyntaxAwareChunking,
)
from docstra.core.document_processing.document import (
    CodeChunk,
    Document,
    DocumentMetadata,
    DocumentType,
)
from docstra.core.document_processing.extractor import (
    DocumentProcessor,
    MetadataExtractor,
)
from docstra.core.document_processing.parser import CodeParser
from docstra.core.indexing.code_index import (
    CodebaseIndex,
    CodebaseIndexer,
)
from docstra.core.indexing.repo_map import (
    DirectoryNode,
    FileNode,
    RepositoryMap,
)
from docstra.core.ingestion.embeddings import (
    EmbeddingFactory,
    EmbeddingGenerator,
    HuggingFaceEmbeddingGenerator,
    OllamaEmbeddingGenerator,
    OpenAIEmbeddingGenerator,
)
from docstra.core.ingestion.storage import (
    ChromaDBStorage,
    DocumentIndexer,
)
from docstra.core.llm.anthropic import AnthropicClient
from docstra.core.llm.local import LocalModelClient
from docstra.core.llm.ollama import OllamaClient
from docstra.core.llm.openai import OpenAIClient
from docstra.core.llm.prompt import (
    PromptBuilder,
    PromptTemplate,
)
from docstra.core.retrieval.chroma import ChromaRetriever
from docstra.core.retrieval.hybrid import HybridRetriever


class docstraant:
    """Main entry point for the code documentation assistant."""

    def __init__(self, config_path=None):
        """Initialize the code documentation assistant.

        Args:
            config_path: Optional path to the configuration file
        """
        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.config

        # Initialize components based on configuration
        self.setup_components()

    def setup_components(self):
        """Set up components based on configuration."""
        # Storage
        storage_dir = self.config.storage.persist_directory
        self.storage = ChromaDBStorage(persist_directory=f"{storage_dir}/chroma")

        # Embedding generator
        self.embedding_generator = EmbeddingFactory.create_embedding_generator(
            embedding_type=self.config.embedding.provider,
            model_name=self.config.embedding.model_name,
        )

        # Document processor
        self.document_processor = DocumentProcessor()

        # Code parser
        self.code_parser = CodeParser()

        # Chunking pipeline
        self.chunking_pipeline = ChunkingPipeline(
            [
                SyntaxAwareChunking(),
                SemanticChunking(max_chunk_size=self.config.processing.chunk_size),
            ]
        )

        # Document indexer
        self.document_indexer = DocumentIndexer(self.storage, self.embedding_generator)

        # Code indexer
        self.code_indexer = CodebaseIndexer(
            index_directory=f"{storage_dir}/index",
            exclude_patterns=self.config.processing.exclude_patterns,
        )

        # Retriever
        self.retriever = ChromaRetriever(self.storage, self.embedding_generator)

        # Hybrid retriever
        self.hybrid_retriever = HybridRetriever(
            self.retriever, self.code_indexer.get_index()
        )

        # LLM client
        self._setup_llm_client()

    def _setup_llm_client(self):
        """Set up the LLM client based on configuration."""
        provider = self.config.model.provider

        if provider == ModelProvider.ANTHROPIC:
            self.llm_client = AnthropicClient(
                model_name=self.config.model.model_name,
                api_key=self.config.model.api_key,
                max_tokens=self.config.model.max_tokens,
                temperature=self.config.model.temperature,
            )
        elif provider == ModelProvider.OPENAI:
            self.llm_client = OpenAIClient(
                model_name=self.config.model.model_name,
                api_key=self.config.model.api_key,
                max_tokens=self.config.model.max_tokens,
                temperature=self.config.model.temperature,
            )
        elif provider == ModelProvider.OLLAMA:
            self.llm_client = OllamaClient(
                model_name=self.config.model.model_name,
                api_base=self.config.model.api_base or "http://localhost:11434",
                max_tokens=self.config.model.max_tokens,
                temperature=self.config.model.temperature,
            )
        elif provider == ModelProvider.LOCAL:
            self.llm_client = LocalModelClient(
                model_name=self.config.model.model_name,
                model_path=self.config.model.model_path,
                max_tokens=self.config.model.max_tokens,
                temperature=self.config.model.temperature,
                device=self.config.model.device,
            )
        else:
            raise ValueError(f"Unsupported model provider: {provider}")

        # Add custom templates if defined
        if self.config.custom_templates:
            for name, template in self.config.custom_templates.items():
                self.llm_client.add_template(name, template)

    def process_file(self, filepath: str) -> Document:
        """Process a file and prepare it for documentation.

        Args:
            filepath: Path to the file to process

        Returns:
            Processed document
        """
        # Process the file
        document = self.document_processor.process(filepath)

        # Parse the document
        self.code_parser.parse_document(document)

        # Chunk the document
        self.chunking_pipeline.process(document)

        return document

    def index_file(self, filepath: str) -> str:
        """Process and index a file.

        Args:
            filepath: Path to the file to index

        Returns:
            Document ID
        """
        # Process the file
        document = self.process_file(filepath)

        # Index the document
        doc_id = self.document_indexer.index_document(document)
        self.code_indexer.index_document(document)

        return doc_id

    def document_code(
        self, code: str, language: str, additional_context: str = ""
    ) -> str:
        """Generate documentation for code.

        Args:
            code: Code to document
            language: Programming language
            additional_context: Additional context about the code

        Returns:
            Generated documentation
        """
        return self.llm_client.document_code(
            code=code, language=language, additional_context=additional_context
        )

    def explain_code(
        self, code: str, language: str, additional_context: str = ""
    ) -> str:
        """Generate an explanation for code.

        Args:
            code: Code to explain
            language: Programming language
            additional_context: Additional context about the code

        Returns:
            Generated explanation
        """
        return self.llm_client.explain_code(
            code=code, language=language, additional_context=additional_context
        )

    def document_file(self, filepath: str) -> str:
        """Generate documentation for a file.

        Args:
            filepath: Path to the file to document

        Returns:
            Generated documentation
        """
        # Process the file
        document = self.process_file(filepath)

        # Generate documentation
        return self.document_code(
            code=document.content,
            language=str(document.metadata.language),
            additional_context=f"File path: {filepath}",
        )

    def explain_file(self, filepath: str) -> str:
        """Generate an explanation for a file.

        Args:
            filepath: Path to the file to explain

        Returns:
            Generated explanation
        """
        # Process the file
        document = self.process_file(filepath)

        # Generate explanation
        return self.explain_code(
            code=document.content,
            language=str(document.metadata.language),
            additional_context=f"File path: {filepath}",
        )

    def answer_question(self, question: str, n_results: int = 5) -> str:
        """Answer a question about the codebase.

        Args:
            question: Question to answer
            n_results: Number of results to retrieve

        Returns:
            Generated answer
        """
        # Retrieve relevant chunks
        results = self.hybrid_retriever.retrieve(
            query=question, n_results=n_results, use_code_context=True
        )

        # Generate answer
        return self.llm_client.answer_question(question=question, context=results)

    def generate_examples(self, request: str, language: str) -> str:
        """Generate code examples.

        Args:
            request: Request for examples
            language: Programming language

        Returns:
            Generated examples
        """
        return self.llm_client.generate_examples(request=request, language=language)

```

```
