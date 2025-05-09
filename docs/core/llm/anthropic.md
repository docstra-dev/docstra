---
language: documenttype.markdown
source_file: /Users/jorgenosberg/development/docstra/docs/core/llm/anthropic.md
summary: 'Anthropic API Integration for LLM Interactions

  ============================================='
title: anthropic

---

Anthropic API Integration for LLM Interactions
=============================================

Overview
--------

This module provides an interface for interacting with Anthropic's Claude models using the Anthropic API. It allows users to generate responses, explain code, answer questions, and more.

Classes
-------

### `AnthropicClient`

A client for interacting with Anthropic's Claude models.

#### Attributes

*   `model_name`: The name of the Anthropic model to use (default: "claude-3-opus-20240229")
*   `api_key`: The Anthropic API key (if None, uses ANTHROPIC_API_KEY environment variable)
*   `max_tokens`: The maximum number of tokens to generate
*   `temperature`: The temperature for generation (0.0 to 1.0)

#### Methods

### `__init__(model_name: str = "claude-3-opus-20240229", api_key: Optional[str] = None, max_tokens: int = 4000, temperature: float = 0.7)`

Initialize the Anthropic client.

*   Args:
    *   `model_name`: The name of the Anthropic model to use
    *   `api_key`: The Anthropic API key (if None, uses ANTHROPIC_API_KEY environment variable)
    *   `max_tokens`: The maximum number of tokens to generate
    *   `temperature`: The temperature for generation (0.0 to 1.0)

### `generate(prompt: str) -> str`

Generate a response from Claude.

*   Args:
    *   `prompt`: The prompt for generation

### `document_code(code: str, language: str, additional_context: str = "") -> str`

Generate documentation for code.

*   Args:
    *   `code`: The code to document
    *   `language`: The programming language
    *   `additional_context`: Additional context about the code (default: "")

### `explain_code(code: str, language: str, additional_context: str = "") -> str`

Generate an explanation for code.

*   Args:
    *   `code`: The code to explain
    *   `language`: The programming language
    *   `additional_context`: Additional context about the code (default: "")

### `answer_question(question: str, context: Union[str, List[Dict[str, Any]]]) -> str`

Answer a question based on context.

*   Args:
    *   `question`: The user question
    *   `context`: The context for answering the question

### `generate_examples(request: str, language: str, additional_context: str = "") -> str`

Generate code examples.

*   Args:
    *   `request`: The request for examples
    *   `language`: The programming language
    *   `additional_context`: Additional context for the examples (default: "")

### `custom_request(template_name: str, **kwargs) -> str`

Make a custom request using a template.

*   Args:
    *   `template_name`: The name of the template to use
    *   `**kwargs`: Values for template placeholders

### `add_template(name: str, template: str) -> None`

Add a new template or override an existing one.

*   Args:
    *   `name`: The template name
    *   `template`: The template string

Implementation Details
--------------------

The Anthropic client uses the `anthropic` library to interact with the Anthropic API. It also uses the `prompt` library to generate responses and explanations.

Usage Examples
-------------

### Generating a Response

```python
client = AnthropicClient()
response = client.generate("What is the meaning of life?")
print(response)
```

### Documenting Code

```python
client = AnthropicClient()
code = "def hello_world():\n    print('Hello, World!')\n"
documentation = client.document_code(code, "Python")
print(documentation)
```

Important Parameters and Return Values
--------------------------------------

*   `api_key`: The Anthropic API key. Required for all methods.
*   `max_tokens`: The maximum number of tokens to generate. Defaults to 4000.
*   `temperature`: The temperature for generation. Defaults to 0.7.

Side Effects
------------

*   The `generate` method may take some time to respond due to the nature of the Anthropic API.
*   The `document_code` and `explain_code` methods may return large amounts of data, depending on the complexity of the code.

Notes
-----

*   This module assumes that the `anthropic` library is installed and configured properly.
*   This module uses the `prompt` library to generate responses and explanations.

Dependencies
------------

This module depends on the following libraries:

*   `anthropic`: For interacting with the Anthropic API
*   `prompt`: For generating responses and explanations


## Source Code

```documenttype.markdown
---
language: documenttype.python
source_file: /Users/jorgenosberg/development/docstra/docstra/core/llm/anthropic.py
summary: 'Anthropic API Integration for LLM Interactions

  ============================================='
title: anthropic

---

# Anthropic API Integration for LLM Interactions
=============================================

## Overview

This module provides an interface for interacting with Anthropic's Claude models using the Anthropic API. It allows users to generate responses, explain code, answer questions, and more.

## Classes

### `AnthropicClient`

A client for interacting with Anthropic's Claude models.

#### Attributes

*   `model_name`: The name of the Anthropic model to use (default: "claude-3-opus-20240229")
*   `api_key`: The Anthropic API key (if None, uses ANTHROPIC_API_KEY environment variable)
*   `max_tokens`: The maximum number of tokens to generate
*   `temperature`: The temperature for generation (0.0 to 1.0)

#### Methods

### `__init__(model_name: str = "claude-3-opus-20240229", api_key: Optional[str] = None, max_tokens: int = 4000, temperature: float = 0.7)`

Initialize the Anthropic client.

*   Args:
    *   `model_name`: The name of the Anthropic model to use
    *   `api_key`: The Anthropic API key (if None, uses ANTHROPIC_API_KEY environment variable)
    *   `max_tokens`: The maximum number of tokens to generate
    *   `temperature`: The temperature for generation (0.0 to 1.0)

### `generate(prompt: str) -> str`

Generate a response from Claude.

*   Args:
    *   `prompt`: The prompt for generation

### `document_code(code: str, language: str, additional_context: str = "") -> str`

Generate documentation for code.

*   Args:
    *   `code`: The code to document
    *   `language`: The programming language
    *   `additional_context`: Additional context about the code (default: "")

### `explain_code(code: str, language: str, additional_context: str = "") -> str`

Generate an explanation for code.

*   Args:
    *   `code`: The code to explain
    *   `language`: The programming language
    *   `additional_context`: Additional context about the code (default: "")

### `answer_question(question: str, context: Union[str, List[Dict[str, Any]]]) -> str`

Answer a question based on context.

*   Args:
    *   `question`: The user question
    *   `context`: The context for answering the question

### `generate_examples(request: str, language: str, additional_context: str = "") -> str`

Generate code examples.

*   Args:
    *   `request`: The request for examples
    *   `language`: The programming language
    *   `additional_context`: Additional context for the examples (default: "")

### `custom_request(template_name: str, **kwargs) -> str`

Make a custom request using a template.

*   Args:
    *   `template_name`: The name of the template to use
    *   `**kwargs`: Values for template placeholders

### `add_template(name: str, template: str) -> None`

Add a new template or override an existing one.

*   Args:
    *   `name`: The template name
    *   `template`: The template string

## Implementation Details

The Anthropic client uses the `anthropic` library to interact with the Anthropic API. It also uses the `prompt` library to generate responses and explanations.

## Usage Examples

### Generating a Response

```python
client = AnthropicClient()
response = client.generate("What is the meaning of life?")
print(response)
```

### Documenting Code

```python
client = AnthropicClient()
code = "def hello_world():\n    print('Hello, World!')\n"
documentation = client.document_code(code, "Python")
print(documentation)
```

## Important Parameters and Return Values

*   `api_key`: The Anthropic API key. Required for all methods.
*   `max_tokens`: The maximum number of tokens to generate. Defaults to 4000.
*   `temperature`: The temperature for generation. Defaults to 0.7.

## Side Effects

*   The `generate` method may take some time to respond due to the nature of the Anthropic API.
*   The `document_code` and `explain_code` methods may return large amounts of data, depending on the complexity of the code.

## Notes

*   This module assumes that the `anthropic` library is installed and configured properly.
*   This module uses the `prompt` library to generate responses and explanations.


## Source Code

```documenttype.python
# File: ./docstra/core/llm/anthropic.py

"""
Anthropic API integration for LLM interactions.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional, Union

import anthropic
from tenacity import retry, stop_after_attempt, wait_exponential

from docstra.core.llm.prompt import PromptBuilder


class AnthropicClient:
    """Client for interacting with Anthropic's Claude models."""

    def __init__(
        self,
        model_name: str = "claude-3-opus-20240229",
        api_key: Optional[str] = None,
        max_tokens: int = 4000,
        temperature: float = 0.7,
    ):
        """Initialize the Anthropic client.

        Args:
            model_name: Name of the Anthropic model to use
            api_key: Anthropic API key (if None, uses ANTHROPIC_API_KEY env var)
            max_tokens: Maximum number of tokens to generate
            temperature: Temperature for generation (0.0 to 1.0)
        """
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature

        # Get API key from parameter or environment variable
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key is required")

        # Initialize Anthropic client
        self.client = anthropic.Anthropic(api_key=self.api_key)

        # Initialize prompt builder
        self.prompt_builder = PromptBuilder()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    def generate(self, prompt: str) -> str:
        """Generate a response from Claude.

        Args:
            prompt: Prompt for generation

        Returns:
            Generated response
        """
        try:
            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[{"role": "user", "content": prompt}],
            )

            return response.content[0].text
        except Exception as e:
            # Log the error and re-raise for retry
            print(f"Error in Anthropic API call: {str(e)}")
            raise

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
        prompt = self.prompt_builder.build_document_code_prompt(
            code=code, language=language, additional_context=additional_context
        )

        return self.generate(prompt)

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
        prompt = self.prompt_builder.build_explain_code_prompt(
            code=code, language=language, additional_context=additional_context
        )

        return self.generate(prompt)

    def answer_question(
        self, question: str, context: Union[str, List[Dict[str, Any]]]
    ) -> str:
        """Answer a question based on context.

        Args:
            question: User question
            context: Context for answering the question

        Returns:
            Generated answer
        """
        prompt = self.prompt_builder.build_answer_question_prompt(
            question=question, context=context
        )

        return self.generate(prompt)

    def generate_examples(
        self, request: str, language: str, additional_context: str = ""
    ) -> str:
        """Generate code examples.

        Args:
            request: Request for examples
            language: Programming language
            additional_context: Additional context for the examples

        Returns:
            Generated examples
        """
        prompt = self.prompt_builder.build_generate_examples_prompt(
            request=request, language=language, additional_context=additional_context
        )

        return self.generate(prompt)

    def custom_request(self, template_name: str, **kwargs) -> str:
        """Make a custom request using a template.

        Args:
            template_name: Name of the template to use
            **kwargs: Values for template placeholders

        Returns:
            Generated response
        """
        prompt = self.prompt_builder.build_custom_prompt(
            template_name=template_name, **kwargs
        )

        return self.generate(prompt)

    def add_template(self, name: str, template: str) -> None:
        """Add a new template or override an existing one.

        Args:
            name: Template name
            template: Template string
        """
        self.prompt_builder.add_template(name, template)

```

```
