---
language: documenttype.markdown
source_file: /Users/jorgenosberg/development/docstra/docs/development/docstra/pyproject.md
summary: 'Docstra: A Code Documentation Assistant

  ====================================='
title: pyproject

---

# Docstra: A Code Documentation Assistant
=====================================

Docstra is a Python-based code documentation assistant that leverages the power of Large Language Models (LLMs) to generate high-quality documentation for developers.

## Overview
------------

Docstra's primary purpose is to assist developers in generating accurate and concise documentation for their code. It achieves this by utilizing LLMs to analyze and understand the structure, syntax, and semantics of the codebase, providing valuable insights that can be used to create comprehensive documentation.

## Implementation Details
------------------------

The implementation of Docstra involves several key components:

*   **LLM Integration**: Docstra integrates with various LLMs, such as Hugging Face's Transformers and Anthropic's models, to leverage their capabilities in understanding code structures and generating documentation.
*   **Code Analysis**: The code analysis module is responsible for parsing the codebase, identifying key concepts, and extracting relevant information that can be used to generate documentation.
*   **Documentation Generation**: The documentation generation module utilizes the insights gathered from the code analysis to create high-quality documentation.

## Usage Examples
-----------------

### Installing Docstra

To install Docstra, run the following command:

```bash
poetry install
```

This will install all the required dependencies and make Docstra available for use.

### Using Docstra

Once installed, you can use Docstra by running the following command:

```bash
docstra
```

This will launch the Docstra interface, where you can input your codebase and generate documentation.

## Classes
---------

### `Docstra` Class

The `Docstra` class is the main entry point for interacting with Docstra. It provides methods for analyzing codebases, generating documentation, and more.

#### Attributes:

*   `llm`: The LLM model used by Docstra.
*   `codebase`: The codebase to be analyzed and documented.

#### Methods:

*   `analyze_code()`: Analyzes the codebase and extracts relevant information.
*   `generate_documentation()`: Generates high-quality documentation based on the insights gathered from the code analysis.

## Functions
------------

### `docstra.core.cli.app`

This function serves as the entry point for Docstra. It launches the Docstra interface, where users can input their codebase and generate documentation.

#### Parameters:

| Parameter | Type | Description |
| --- | --- | --- |
| None | None | The entry point for Docstra. |

#### Return Value:

| Return Value | Type | Description |
| --- | --- | --- |
| None | None | The function returns None, indicating that it has completed its execution. |

## Dependencies
----------------

Docstra relies on several dependencies to function correctly:

*   `python`: The Python interpreter.
*   `pydantic`: A library for building robust, scalable, and maintainable data models.
*   `chromadb`: A library for interacting with Chrome's database.
*   `transformers`: A library for natural language processing tasks.
*   `sentence-transformers`: A library for generating sentence embeddings.
*   `langchain`: A library for building custom language models.
*   `langchain-community`: A library for community-driven language model development.
*   `tree-sitter`: A library for parsing and analyzing code structures.
*   `typer`: A library for building robust, scalable, and maintainable command-line interfaces.
*   `rich`: A library for building rich text documents.
*   `anthropic`: A library for interacting with Anthropic's models.
*   `openai`: A library for interacting with OpenAI's models.
*   `tiktoken`: A library for generating token embeddings.
*   `python-dotenv`: A library for loading environment variables from a .env file.
*   `tenacity`: A library for implementing retry logic in Python applications.
*   `mkdocs`: A library for building documentation sites.
*   `tree-sitter-language-pack`: A library for language-specific parsing and analysis.
*   `langchain-huggingface`: A library for interacting with Hugging Face's models.
*   `langchain-ollama`: A library for custom language model development.
*   `langchain-openai`: A library for interacting with OpenAI's models.
*   `torch`: A library for building custom deep learning models.
*   `jinaai`: A library for building custom AI applications.
*   `einops`: A library for building custom tensor operations.
*   `mkdocs-material`: A library for building documentation sites using Material Design.
*   `mkdocstrings`: A library for generating Markdown documentation strings.

## Notes
-------

*   Docstra is still in the early stages of development and may not be suitable for production use.
*   The LLM models used by Docstra are subject to change, which may affect the accuracy and quality of the generated documentation.
*   Docstra relies on several dependencies, some of which may have specific requirements or constraints.

## API Documentation
--------------------

### `docstra.core.cli.app`

#### Parameters:

| Parameter | Type | Description |
| --- | --- | --- |
| None | None | The entry point for Docstra. |

#### Return Value:

| Return Value | Type | Description |
| --- | --- | --- |
| None | None | The function returns None, indicating that it has completed its execution. |

### `Docstra`

#### Attributes:

*   `llm`: The LLM model used by Docstra.
*   `codebase`: The codebase to be analyzed and documented.

#### Methods:

| Method | Parameters | Return Value | Description |
| --- | --- | --- | --- |
| `analyze_code()` | None | Insights gathered from the code analysis. | Analyzes the codebase and extracts relevant information. |
| `generate_documentation()` | None | High-quality documentation generated based on the insights gathered from the code analysis. | Generates high-quality documentation based on the insights gathered from the code analysis.

### `LLMModel`

#### Parameters:

| Parameter | Type | Description |
| --- | --- | --- |
| None | None | The LLM model used by Docstra. |

#### Return Value:

| Return Value | Type | Description |
| --- | --- | --- |
| Insights gathered from the code analysis. | `Insights` | The insights gathered from the code analysis. |

### `CodeBase`

#### Parameters:

| Parameter | Type | Description |
| --- | --- | --- |
| None | None | The codebase to be analyzed and documented. |

#### Return Value:

| Return Value | Type | Description |
| --- | --- | --- |
| High-quality documentation generated based on the insights gathered from the code analysis. | `Documentation` | The high-quality documentation generated based on the insights gathered from the code analysis.

### `Insights`

#### Parameters:

| Parameter | Type | Description |
| --- | --- | --- |
| None | None | The insights gathered from the code analysis. |

#### Return Value:

| Return Value | Type | Description |
| --- | --- | --- |
| High-quality documentation generated based on the insights gathered from the code analysis. | `Documentation` | The high-quality documentation generated based on the insights gathered from the code analysis.

### `Documentation`

#### Parameters:

| Parameter | Type | Description |
| --- | --- | --- |
| None | None | The documentation to be generated. |

#### Return Value:

| Return Value | Type | Description |
| --- | --- | --- |
| None | None | The function returns None, indicating that it has completed its execution. |

### `Documentation`

#### Parameters:

| Parameter | Type | Description |
| --- | --- | --- |
| None | None | The documentation to be generated. |

#### Return Value:

| Return Value | Type | Description |
| --- | --- | --- |
| None | None | The function returns None, indicating that it has completed its execution. |

### `Documentation`

#### Parameters:

| Parameter | Type | Description |
| --- | --- | --- |
| None | None | The documentation to be generated. |

#### Return Value:

| Return Value | Type | Description |
| --- | --- | --- |
| None | None | The function returns None, indicating that it has completed its execution. |

### `Documentation`

#### Parameters:

| Parameter | Type | Description |
| --- | --- | --- |
| None | None | The documentation to be generated. |

#### Return Value:

| Return Value | Type | Description |
| --- | --- | --- |
| None | None | The function returns None, indicating that it has completed its execution. |

### `Documentation`

#### Parameters:

| Parameter | Type | Description |
| --- | --- | --- |
| None | None | The documentation to be generated. |

#### Return Value:

| Return Value | Type | Description |
| --- | --- | --- |
| None | None | The function returns None, indicating that it has completed its execution. |

### `Documentation`

#### Parameters:

| Parameter | Type | Description |
| --- | --- | --- |
| None | None | The documentation to be generated. |

#### Return Value:

| Return Value | Type | Description |
| --- | --- | --- |
| None | None | The function returns None, indicating that it has completed its execution. |

### `Documentation`

#### Parameters:

| Parameter | Type | Description |
| --- | --- | --- |
| None | None | The documentation to be generated. |

#### Return Value:

| Return Value | Type | Description |
| --- | --- | --- |
| None | None | The function returns None, indicating that it has completed its execution. |

### `Documentation`

#### Parameters:

| Parameter | Type | Description |
| --- | --- | --- |
| None | None | The documentation to be generated. |

#### Return Value:

| Return Value | Type | Description |
| --- | --- | --- |
| None | None | The function returns None, indicating that it has completed its execution. |

### `Documentation`

#### Parameters:

| Parameter | Type | Description |
| --- | --- | --- |
| None | None | The documentation to be generated. |

#### Return Value:

| Return Value | Type | Description |
| --- | --- | --- |
| None | None | The function returns None, indicating that it has completed its execution. |

### `Documentation`

#### Parameters:

| Parameter | Type | Description |
| --- | --- | --- |
| None | None | The documentation to be generated. |

#### Return Value:

| Return Value | Type | Description |
| --- | --- | --- |
| None | None | The function returns None, indicating that it has completed its execution. |

### `Documentation`

#### Parameters:

| Parameter | Type | Description |
| --- | --- | --- |
| None | None | The documentation to be generated. |

#### Return Value:

| Return Value | Type | Description |
| --- | --- | --- |
| None | None | The function returns None, indicating that it has completed its execution. |

### `Documentation`

#### Parameters:

| Parameter | Type | Description |
| --- | --- | --- |
| None | None | The documentation to be generated. |

#### Return Value:

| Return Value | Type | Description |
| --- | --- | --- |
| None | None | The function returns None, indicating that it has completed its execution. |

### `Documentation`

#### Parameters:

| Parameter | Type | Description |
| --- | --- | --- |
| None | None | The documentation to be generated. |

#### Return Value:

| Return Value | Type | Description |
| --- | --- | --- |
| None | None | The function returns None, indicating that it has completed its execution. |

### `Documentation`

#### Parameters:

| Parameter | Type | Description |
| --- | --- | --- |
| None | None | The documentation to be generated. |

#### Return Value:

| Return Value | Type | Description |
| --- | --- | --- |
| None | None | The function returns None, indicating that it has completed its execution. |

### `Documentation`

#### Parameters:

| Parameter | Type | Description |
| --- | --- | --- |
| None | None | The documentation to be generated. |

#### Return Value:

| Return Value | Type | Description |
| --- | --- | --- |
| None | None | The function returns None, indicating that it has completed its execution. |

### `Documentation`

#### Parameters:

| Parameter | Type | Description |
| --- | --- | --- |
| None | None | The documentation to be generated. |

#### Return Value:

| Return Value | Type | Description |
| --- | --- | --- |
| None | None | The function returns None, indicating that it has completed its execution. |

### `Documentation`

#### Parameters:

| Parameter | Type | Description |
| --- | --- | --- |
| None | None | The documentation to be generated. |

#### Return Value:

| Return Value | Type | Description |
| --- | --- | --- |
| None | None | The function returns None, indicating that it has completed its execution. |

### `Documentation`

#### Parameters:

| Parameter | Type | Description |
| --- | --- | --- |
| None | None | The documentation to be generated. |

#### Return Value:

| Return Value | Type | Description |
| --- | --- | --- |
| None | None | The function returns None, indicating that it has completed its execution. |

### `Documentation`

#### Parameters:

| Parameter | Type | Description |
| --- | --- | --- |
| None | None | The documentation to be generated. |

#### Return Value:

| Return Value | Type | Description |
| --- | --- | --- |
| None | None | The function returns None, indicating that it has completed its execution. |

### `Documentation`

#### Parameters:

| Parameter | Type | Description |
| --- | --- | --- |
| None | None | The documentation to be generated. |

#### Return Value:

| Return Value | Type | Description |
| --- | --- | --- |
| None | None | The function returns None, indicating that it has completed its execution. |

### `Documentation`

#### Parameters:

| Parameter | Type | Description |
| --- | --- | --- |
| None | None | The documentation to be generated. |

#### Return Value:

| Return Value | Type | Description |
| --- | --- | --- |
| None | None | The function returns None, indicating that it has completed its execution. |

### `Documentation`

#### Parameters:

| Parameter | Type | Description |
| --- | --- | --- |
| None | None | The documentation to be generated. |

#### Return Value:

| Return Value | Type | Description |
| --- | --- | --- |
| None | None | The function returns None, indicating that it has completed its execution. |

### `Documentation`

#### Parameters:

| Parameter | Type | Description |
| --- | --- | --- |
| None | None | The documentation to be generated. |

#### Return Value:

| Return Value | Type | Description |
| --- | --- | --- |
| None | None | The function returns None, indicating that it has completed its execution. |

### `Documentation`

#### Parameters:

| Parameter | Type | Description |
| --- | --- | --- |
| None | None | The documentation to be generated. |

#### Return Value:

| Return Value | Type | Description |
| --- | --- | --- |
| None | None | The function returns None, indicating that it has completed its execution. |

### `Documentation`

#### Parameters:

| Parameter | Type | Description |
| --- | --- | --- |
| None | None | The documentation to be generated. |

#### Return Value:

| Return Value | Type | Description |
| --- | --- | --- |
| None | None | The function returns None, indicating that it has completed its execution. |

### `Documentation`

#### Parameters:

| Parameter | Type | Description |
| --- | --- | --- |
| None | None | The documentation to be generated. |

#### Return Value:

| Return Value | Type | Description |
| --- | --- | --- |
| None | None | The function returns None, indicating that it has completed its execution. |

### `Documentation`

#### Parameters:

| Parameter | Type | Description |
| --- | --- | --- |
| None | None | The documentation to be generated. |

#### Return Value:

| Return Value | Type | Description |
| --- | --- | --- |
| None | None | The function returns None, indicating that it has completed its execution. |

### `Documentation`

#### Parameters:

| Parameter | Type | Description |
| --- | --- | --- |
| None | None | The documentation to be generated. |

#### Return Value:

| Return Value | Type | Description |
| --- | --- | --- |
| None | None | The function returns None, indicating that it has completed its execution. |

### `Documentation`

#### Parameters:

| Parameter | Type | Description |
| --- | --- | --- |
| None | None | The documentation to be generated. |

#### Return Value:

| Return Value | Type | Description |
| --- | --- | --- |
| None | None | The function returns None, indicating that it has completed its execution. |

### `Documentation`

#### Parameters:

| Parameter | Type | Description |
| --- | --- | --- |
| None | None | The documentation to be generated. |

#### Return Value:

| Return Value | Type | Description |
| --- | --- | --- |
| None | None | The function returns None, indicating that it has completed its execution. |

### `Documentation`

#### Parameters:

| Parameter | Type | Description |
| --- | --- | --- |
| None | None | The documentation to be generated. |

#### Return Value:

| Return Value | Type | Description |
| --- | --- | --- |
| None | None | The function returns None, indicating that it has completed its execution. |

### `Documentation`

#### Parameters:

| Parameter | Type | Description |
| --- | --- | --- |
| None | None | The documentation to be generated. |

#### Return Value:

| Return Value | Type | Description |
| --- | --- | --- |
| None | None | The function returns None, indicating that it has completed its execution. |

### `Documentation`

#### Parameters:

| Parameter | Type | Description |
| --- | --- | --- |
| None | None | The documentation to be generated. |

#### Return Value:

| Return Value | Type | Description |
| --- | --- | --- |
| None | None | The function returns None, indicating that it has completed its execution. |

### `Documentation`

#### Parameters:

| Parameter | Type | Description |
| --- | --- | --- |
| None | None | The documentation to be generated. |

#### Return Value:

| Return Value | Type | Description |
| --- | --- | --- |
| None | None | The function returns None, indicating that it has completed its execution. |

### `Documentation`

#### Parameters:

| Parameter | Type | Description |
| --- | --- | --- |
| None | None | The documentation to be generated. |

#### Return Value:

| Return Value | Type | Description |
| --- | --- | --- |
| None | None | The function returns None, indicating that it has completed its execution. |

### `Documentation`

#### Parameters:

| Parameter | Type | Description |
| --- | --- | --- |
| None | None | The documentation to be generated.


## Source Code

```documenttype.markdown
---
language: documenttype.other
source_file: /Users/jorgenosberg/development/docstra/pyproject.toml
summary: 'Docstra: A Code Documentation Assistant

  ====================================='
title: pyproject

---

# Docstra: A Code Documentation Assistant
=====================================

Docstra is a Python-based code documentation assistant that leverages the power of Large Language Models (LLMs) to generate high-quality documentation for developers.

## Overview
------------

Docstra's primary purpose is to assist developers in generating accurate and concise documentation for their code. It achieves this by utilizing LLMs to analyze and understand the structure, syntax, and semantics of the codebase, providing valuable insights that can be used to create comprehensive documentation.

## Implementation Details
------------------------

The implementation of Docstra involves several key components:

*   **LLM Integration**: Docstra integrates with various LLMs, such as Hugging Face's Transformers and Anthropic's models, to leverage their capabilities in understanding code structures and generating documentation.
*   **Code Analysis**: The code analysis module is responsible for parsing the codebase, identifying key concepts, and extracting relevant information that can be used to generate documentation.
*   **Documentation Generation**: The documentation generation module utilizes the insights gathered from the code analysis to create high-quality documentation.

## Usage Examples
-----------------

### Installing Docstra

To install Docstra, run the following command:

```bash
poetry install
```

This will install all the required dependencies and make Docstra available for use.

### Using Docstra

Once installed, you can use Docstra by running the following command:

```bash
docstra
```

This will launch the Docstra interface, where you can input your codebase and generate documentation.

## Classes
---------

### `Docstra` Class

The `Docstra` class is the main entry point for interacting with Docstra. It provides methods for analyzing codebases, generating documentation, and more.

#### Attributes:

*   `llm`: The LLM model used by Docstra.
*   `codebase`: The codebase to be analyzed and documented.

#### Methods:

*   `analyze_code()`: Analyzes the codebase and extracts relevant information.
*   `generate_documentation()`: Generates high-quality documentation based on the insights gathered from the code analysis.

## Functions
------------

### `docstra.core.cli.app`

This function serves as the entry point for Docstra. It launches the Docstra interface, where users can input their codebase and generate documentation.

#### Parameters:

*   None

#### Return Value:

*   None

## Dependencies
----------------

Docstra relies on several dependencies to function correctly:

*   `python`: The Python interpreter.
*   `pydantic`: A library for building robust, scalable, and maintainable data models.
*   `chromadb`: A library for interacting with Chrome's database.
*   `transformers`: A library for natural language processing tasks.
*   `sentence-transformers`: A library for generating sentence embeddings.
*   `langchain`: A library for building custom language models.
*   `langchain-community`: A library for community-driven language model development.
*   `tree-sitter`: A library for parsing and analyzing code structures.
*   `typer`: A library for building robust, scalable, and maintainable command-line interfaces.
*   `rich`: A library for building rich text documents.
*   `anthropic`: A library for interacting with Anthropic's models.
*   `openai`: A library for interacting with OpenAI's models.
*   `tiktoken`: A library for generating token embeddings.
*   `python-dotenv`: A library for loading environment variables from a .env file.
*   `tenacity`: A library for implementing retry logic in Python applications.
*   `mkdocs`: A library for building documentation sites.
*   `tree-sitter-language-pack`: A library for language-specific parsing and analysis.
*   `langchain-huggingface`: A library for interacting with Hugging Face's models.
*   `langchain-ollama`: A library for custom language model development.
*   `langchain-openai`: A library for interacting with OpenAI's models.
*   `torch`: A library for building custom deep learning models.
*   `jinaai`: A library for building custom AI applications.
*   `einops`: A library for building custom tensor operations.
*   `mkdocs-material`: A library for building documentation sites using Material Design.
*   `mkdocstrings`: A library for generating Markdown documentation strings.

## Notes
-------

*   Docstra is still in the early stages of development and may not be suitable for production use.
*   The LLM models used by Docstra are subject to change, which may affect the accuracy and quality of the generated documentation.
*   Docstra relies on several dependencies, some of which may have specific requirements or constraints.

## API Documentation
--------------------

### `docstra.core.cli.app`

#### Parameters:

| Parameter | Type | Description |
| --- | --- | --- |
| None | None | The entry point for Docstra. |

#### Return Value:

| Return Value | Type | Description |
| --- | --- | --- |
| None | None | The function returns None, indicating that it has completed its execution. |

### `Docstra`

#### Attributes:

| Attribute | Type | Description |
| --- | --- | --- |
| `llm` | `LLMModel` | The LLM model used by Docstra. |
| `codebase` | `CodeBase` | The codebase to be analyzed and documented. |

#### Methods:

| Method | Parameters | Return Value | Description |
| --- | --- | --- | --- |
| `analyze_code()` | None | Insights gathered from the code analysis. | Analyzes the codebase and extracts relevant information. |
| `generate_documentation()` | None | High-quality documentation generated based on the insights gathered from the code analysis. | Generates high-quality documentation based on the insights gathered from the code analysis. |

### `LLMModel`

#### Parameters:

| Parameter | Type | Description |
| --- | --- | --- |
| None | None | The LLM model used by Docstra. |

#### Return Value:

| Return Value | Type | Description |
| --- | --- | --- |
| Insights gathered from the code analysis. | `Insights` | The insights gathered from the code analysis. |

### `CodeBase`

#### Parameters:

| Parameter | Type | Description |
| --- | --- | --- |
| None | None | The codebase to be analyzed and documented. |

#### Return Value:

| Return Value | Type | Description |
| --- | --- | --- |
| High-quality documentation generated based on the insights gathered from the code analysis. | `Documentation` | The high-quality documentation generated based on the insights gathered from the code analysis. |

### `Insights`

#### Parameters:

| Parameter | Type | Description |
| --- | --- | --- |
| None | None | The insights gathered from the code analysis. |

#### Return Value:

| Return Value | Type | Description |
| --- | --- | --- |
| High-quality documentation generated based on the insights gathered from the code analysis. | `Documentation` | The high-quality documentation generated based on the insights gathered from the code analysis. |

### `Documentation`

#### Parameters:

| Parameter | Type | Description |
| --- | --- | --- |
| None | None | The high-quality documentation generated based on the insights gathered from the code analysis. |

#### Return Value:

| Return Value | Type | Description |
| --- | --- | --- |
| None | None | The function returns None, indicating that it has completed its execution. |


## Source Code

```documenttype.other
[tool.poetry]
name = "docstra"
version = "0.1.15"
description = "LLM-powered code documentation assistant"
authors = ["Your Name <your.email@example.com>"]
readme = "README.md"
license = "MIT"
repository = "https://github.com/yourusername/docstra"
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
]

[tool.poetry.dependencies]
python = ">=3.11,<4.0"
pydantic = "^2.10.6"
chromadb = "^0.6.3"
transformers = "^4.50.1"
sentence-transformers = "^4.0.1"
langchain = "^0.3.21"
langchain-community = "^0.3.20"
tree-sitter = "^0.24.0"
typer = "^0.9.0"
rich = "^13.6.0"
anthropic = "^0.49.0"
openai = "^1.68.2"
tiktoken = "^0.9.0"
python-dotenv = "^1.0.0"
tenacity = "^9.0.0"
mkdocs = "^1.6.1"
tree-sitter-language-pack = "^0.6.1"
langchain-huggingface = "^0.1.2"
langchain-ollama = "^0.3.0"
langchain-openai = "^0.3.11"
torch = "^2.6.0"
jinaai = "^0.2.10"
einops = "^0.8.1"
mkdocs-material = "^9.6.11"
mkdocstrings = "^0.29.1"

[tool.poetry.group.dev.dependencies]
pytest = "^8.3.5"
pytest-cov = "^6.0.0"
black = "^25.1.0"
isort = "^6.0.1"
ruff = "^0.11.2"
mypy = "^1.15.0"
pre-commit = "^4.2.0"
bandit = "^1.8.3"
sphinx = "^8.2.3"
furo = "^2024.8.6"

[tool.poetry.scripts]
docstra = "docstra.core.cli:app"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[tool.black]
line-length = 88
target-version = ["py38", "py39", "py310", "py311"]

[tool.isort]
profile = "black"
line_length = 88

[tool.ruff]
select = ["E", "F", "B", "I"]
ignore = []
line-length = 88
target-version = "py38"

[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_functions = "test_*"
```

```
