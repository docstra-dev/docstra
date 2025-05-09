---
language: documenttype.markdown
source_file: /Users/jorgenosberg/development/docstra/docs/core/llm/ollama.md
summary: 'Ollama Integration for LLM Interactions

  ====================================='
title: ollama

---

Ollama Integration for LLM Interactions
=====================================

Overview
--------

This module provides an integration with Ollama models for generating responses to user input. It utilizes the Ollama API to generate text based on a given prompt.

Implementation Details
---------------------

The `OllamaClient` class serves as the main interface for interacting with Ollama models. It initializes the client with a specified model name, API base URL, maximum number of tokens, and temperature.

### Attributes

*   `model_name`: The name of the Ollama model to use.
*   `api_base`: The base URL for the Ollama API.
*   `max_tokens`: The maximum number of tokens to generate.
*   `temperature`: The temperature for generation (0.0 to 1.0).
*   `prompt_builder`: An instance of `PromptBuilder` used to construct prompts.

### Methods

#### `__init__(model_name, api_base, max_tokens, temperature)`

Initializes the Ollama client with the specified parameters.

#### `generate(prompt, stream=False)`

Generates a response based on the provided prompt. The `stream` parameter determines whether to return a generator or a single string.

#### `explain_code(code, language, additional_context, stream=False)`

Generates an explanation for the given code snippet.

#### `answer_question(question, context, stream=False)`

Answers a question based on the provided context.

#### `generate_examples(request, language, additional_context, stream=False)`

Generates code examples based on the specified request.

#### `custom_request(template_name, stream=False, **kwargs)`

Makes a custom request using a template. The `stream` parameter determines whether to return a generator or a single string.

#### `add_template(name, template)`

Adds a new template or overrides an existing one.

Usage Examples
-------------

### Generating a Response

```python
from ollama import OllamaClient

# Initialize the client with default parameters
client = OllamaClient()

# Construct a prompt for generating a response
prompt = "Write a short story about a character who discovers a hidden world."

# Generate a response
response = client.generate(prompt)

print(response)
```

### Explaining Code

```python
from ollama import OllamaClient

# Initialize the client with default parameters
client = OllamaClient()

# Construct a prompt for explaining code
prompt = "Explain the purpose of the `if` statement in Python."

# Generate an explanation
explanation = client.explain_code(code="if x > 5: print('x is greater than 5')", language="Python")

print(explanation)
```

Important Dependencies and Relationships
--------------------------------------

This module relies on the Ollama API for generating responses. It also utilizes the `PromptBuilder` class to construct prompts.

Dependencies:

*   `ollama`: The main library for interacting with Ollama models.
*   `prompt_builder`: A utility class for constructing prompts.

Relationships:

*   This module is part of the `docstra` package, which provides a suite of tools for generating documentation and explanations.
*   The `OllamaClient` class is designed to be used in conjunction with other modules in the `docstra` package.

Notes
-----

*   Edge cases: The Ollama API may return errors or unexpected responses if the input prompt is malformed or outside the model's capabilities. This module provides a basic error handling mechanism, but further customization may be necessary for specific use cases.
*   Limitations: The Ollama models have limitations in terms of their understanding and generation capabilities. This module should not be relied upon for critical applications requiring high accuracy or nuance.

API Documentation
-----------------

### `OllamaClient`

#### `__init__(model_name, api_base, max_tokens, temperature)`

Initializes the Ollama client with the specified parameters.

#### `generate(prompt, stream=False)`

Generates a response based on the provided prompt. The `stream` parameter determines whether to return a generator or a single string.

#### `explain_code(code, language, additional_context, stream=False)`

Generates an explanation for the given code snippet.

#### `answer_question(question, context, stream=False)`

Answers a question based on the provided context.

#### `generate_examples(request, language, additional_context, stream=False)`

Generates code examples based on the specified request.

#### `custom_request(template_name, stream=False, **kwargs)`

Makes a custom request using a template. The `stream` parameter determines whether to return a generator or a single string.

#### `add_template(name, template)`

Adds a new template or overrides an existing one.

### `PromptBuilder`

#### `build_prompt(prompt_type, prompt_data)`

Constructs a prompt based on the specified type and data.

#### `add_template(name, template)`

Adds a new template or overrides an existing one.


## Source Code

```documenttype.markdown
---
language: documenttype.python
source_file: /Users/jorgenosberg/development/docstra/docstra/core/llm/ollama.py
summary: 'Ollama Integration for LLM Interactions

  ====================================='
title: ollama

---

Ollama Integration for LLM Interactions
=====================================

Overview
--------

This module provides an integration with Ollama models for generating responses to user input. It utilizes the Ollama API to generate text based on a given prompt.

Implementation Details
---------------------

The `OllamaClient` class serves as the main interface for interacting with Ollama models. It initializes the client with a specified model name, API base URL, maximum number of tokens, and temperature.

### Attributes

*   `model_name`: The name of the Ollama model to use.
*   `api_base`: The base URL for the Ollama API.
*   `max_tokens`: The maximum number of tokens to generate.
*   `temperature`: The temperature for generation (0.0 to 1.0).
*   `prompt_builder`: An instance of `PromptBuilder` used to construct prompts.

### Methods

#### `__init__(model_name, api_base, max_tokens, temperature)`

Initializes the Ollama client with the specified parameters.

#### `generate(prompt, stream=False)`

Generates a response based on the provided prompt. The `stream` parameter determines whether to return a generator or a single string.

#### `explain_code(code, language, additional_context, stream=False)`

Generates an explanation for the given code snippet.

#### `answer_question(question, context, stream=False)`

Answers a question based on the provided context.

#### `generate_examples(request, language, additional_context, stream=False)`

Generates code examples based on the specified request.

#### `custom_request(template_name, stream=False, **kwargs)`

Makes a custom request using a template. The `stream` parameter determines whether to return a generator or a single string.

#### `add_template(name, template)`

Adds a new template or overrides an existing one.

Usage Examples
-------------

### Generating a Response

```python
from ollama import OllamaClient

# Initialize the client with default parameters
client = OllamaClient()

# Construct a prompt for generating a response
prompt = "Write a short story about a character who discovers a hidden world."

# Generate a response
response = client.generate(prompt)

print(response)
```

### Explaining Code

```python
from ollama import OllamaClient

# Initialize the client with default parameters
client = OllamaClient()

# Construct a prompt for explaining code
prompt = "Explain the purpose of the `if` statement in Python."

# Generate an explanation
explanation = client.explain_code(code="if x > 5: print('x is greater than 5')", language="Python")

print(explanation)
```

Important Dependencies and Relationships
--------------------------------------

This module relies on the Ollama API for generating responses. It also utilizes the `PromptBuilder` class to construct prompts.

Dependencies:

*   `ollama`: The main library for interacting with Ollama models.
*   `prompt_builder`: A utility class for constructing prompts.

Relationships:

*   This module is part of the `docstra` package, which provides a suite of tools for generating documentation and explanations.
*   The `OllamaClient` class is designed to be used in conjunction with other modules in the `docstra` package.

Notes
-----

*   Edge cases: The Ollama API may return errors or unexpected responses if the input prompt is malformed or outside the model's capabilities. This module provides a basic error handling mechanism, but further customization may be necessary for specific use cases.
*   Limitations: The Ollama models have limitations in terms of their understanding and generation capabilities. This module should not be relied upon for critical applications requiring high accuracy or nuance.

API Documentation
-----------------

### `OllamaClient`

#### `__init__(model_name, api_base, max_tokens, temperature)`

Initializes the Ollama client with the specified parameters.

#### `generate(prompt, stream=False)`

Generates a response based on the provided prompt. The `stream` parameter determines whether to return a generator or a single string.

#### `explain_code(code, language, additional_context, stream=False)`

Generates an explanation for the given code snippet.

#### `answer_question(question, context, stream=False)`

Answers a question based on the provided context.

#### `generate_examples(request, language, additional_context, stream=False)`

Generates code examples based on the specified request.

#### `custom_request(template_name, stream=False, **kwargs)`

Makes a custom request using a template. The `stream` parameter determines whether to return a generator or a single string.

#### `add_template(name, template)`

Adds a new template or overrides an existing one.

### `PromptBuilder`

#### `build_prompt(prompt_type, prompt_data)`

Constructs a prompt based on the specified type and data.

#### `add_template(name, template)`

Adds a new template or overrides an existing one.


## Source Code

```documenttype.python
# File: ./docstra/core/llm/ollama.py

"""
Ollama integration for LLM interactions.
"""

from __future__ import annotations

import json
from typing import Any, Dict, Generator, List, Union

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from docstra.core.llm.prompt import PromptBuilder


class OllamaClient:
    """Client for interacting with Ollama models."""

    def __init__(
        self,
        model_name: str = "deepseek-r1",
        api_base: str = "http://localhost:11434",
        max_tokens: int = 2000,
        temperature: float = 0.7,
    ):
        """Initialize the Ollama client.

        Args:
            model_name: Name of the Ollama model to use
            api_base: Base URL for the Ollama API
            max_tokens: Maximum number of tokens to generate
            temperature: Temperature for generation (0.0 to 1.0)
        """
        self.model_name = model_name
        self.api_base = api_base
        self.max_tokens = max_tokens
        self.temperature = temperature

        # Initialize prompt builder
        self.prompt_builder = PromptBuilder()

        # Check if Ollama is running
        self._check_ollama()

    def _check_ollama(self) -> None:
        """Check if Ollama is running."""
        try:
            response = requests.get(f"{self.api_base}/api/tags")
            if response.status_code != 200:
                raise ConnectionError(
                    f"Ollama API returned status code {response.status_code}"
                )
        except requests.RequestException as e:
            raise ConnectionError(f"Failed to connect to Ollama API: {str(e)}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    def generate(
        self, prompt: str, stream: bool = False
    ) -> Union[str, Generator[str, None, None]]:
        """Generate a response from Ollama.

        Args:
            prompt: Prompt for generation
            stream: Whether to stream the response

        Returns:
            Generated response or stream
        """
        url = f"{self.api_base}/api/generate"

        data = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": stream,
            "options": {
                "num_predict": self.max_tokens,
                "temperature": self.temperature,
            },
        }

        if stream:
            return self._stream_response(url, data)
        else:
            return self._generate_response(url, data)

    def _generate_response(self, url: str, data: Dict[str, Any]) -> str:
        """Generate a complete response.

        Args:
            url: API endpoint URL
            data: Request data

        Returns:
            Generated response
        """
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()

            result = response.json()
            return result.get("response", "")
        except Exception as e:
            print(f"Error in Ollama API call: {str(e)}")
            raise

    def _stream_response(
        self, url: str, data: Dict[str, Any]
    ) -> Generator[str, None, None]:
        """Stream the response from Ollama.

        Args:
            url: API endpoint URL
            data: Request data

        Returns:
            Generator yielding response chunks
        """
        try:
            with requests.post(url, json=data, stream=True) as response:
                response.raise_for_status()

                for line in response.iter_lines():
                    if line:
                        chunk = json.loads(line)
                        if "response" in chunk:
                            yield chunk["response"]

                        if chunk.get("done", False):
                            break
        except Exception as e:
            print(f"Error in Ollama streaming API call: {str(e)}")
            raise

    def document_code(
        self,
        code: str,
        language: str,
        additional_context: str = "",
        stream: bool = False,
    ) -> Union[str, Generator[str, None, None]]:
        """Generate documentation for code.

        Args:
            code: Code to document
            language: Programming language
            additional_context: Additional context about the code
            stream: Whether to stream the response

        Returns:
            Generated documentation
        """
        prompt = self.prompt_builder.build_document_code_prompt(
            code=code, language=language, additional_context=additional_context
        )

        return self.generate(prompt, stream=stream)

    def explain_code(
        self,
        code: str,
        language: str,
        additional_context: str = "",
        stream: bool = False,
    ) -> Union[str, Generator[str, None, None]]:
        """Generate an explanation for code.

        Args:
            code: Code to explain
            language: Programming language
            additional_context: Additional context about the code
            stream: Whether to stream the response

        Returns:
            Generated explanation
        """
        prompt = self.prompt_builder.build_explain_code_prompt(
            code=code, language=language, additional_context=additional_context
        )

        return self.generate(prompt, stream=stream)

    def answer_question(
        self,
        question: str,
        context: Union[str, List[Dict[str, Any]]],
        stream: bool = False,
    ) -> Union[str, Generator[str, None, None]]:
        """Answer a question based on context.

        Args:
            question: User question
            context: Context for answering the question
            stream: Whether to stream the response

        Returns:
            Generated answer
        """
        prompt = self.prompt_builder.build_answer_question_prompt(
            question=question, context=context
        )

        return self.generate(prompt, stream=stream)

    def generate_examples(
        self,
        request: str,
        language: str,
        additional_context: str = "",
        stream: bool = False,
    ) -> Union[str, Generator[str, None, None]]:
        """Generate code examples.

        Args:
            request: Request for examples
            language: Programming language
            additional_context: Additional context for the examples
            stream: Whether to stream the response

        Returns:
            Generated examples
        """
        prompt = self.prompt_builder.build_generate_examples_prompt(
            request=request, language=language, additional_context=additional_context
        )

        return self.generate(prompt, stream=stream)

    def custom_request(
        self, template_name: str, stream: bool = False, **kwargs
    ) -> Union[str, Generator[str, None, None]]:
        """Make a custom request using a template.

        Args:
            template_name: Name of the template to use
            stream: Whether to stream the response
            **kwargs: Values for template placeholders

        Returns:
            Generated response
        """
        prompt = self.prompt_builder.build_custom_prompt(
            template_name=template_name, **kwargs
        )

        return self.generate(prompt, stream=stream)

    def add_template(self, name: str, template: str) -> None:
        """Add a new template or override an existing one.

        Args:
            name: Template name
            template: Template string
        """
        self.prompt_builder.add_template(name, template)

```

```
