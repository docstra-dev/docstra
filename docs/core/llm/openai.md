---
language: documenttype.markdown
source_file: /Users/jorgenosberg/development/docstra/docs/core/llm/openai.md
summary: 'OpenAI API Integration for LLM Interactions

  ============================================='
title: openai

---

OpenAI API Integration for LLM Interactions
=============================================

Overview
--------

This module provides an interface for interacting with OpenAI's models using the `openai` library. It allows users to generate responses, explain code, answer questions, and more.

Implementation Details
---------------------

The module uses the `openai` library to interact with OpenAI's models. The `OpenAIClient` class is used to initialize the client and perform various operations such as generating responses, explaining code, answering questions, and generating examples.

### Classes

#### `OpenAIClient`

Attributes:

*   `model_name`: The name of the OpenAI model to use (default: "gpt-4-turbo")
*   `api_key`: The OpenAI API key (if None, uses `OPENAI_API_KEY` environment variable)
*   `max_tokens`: The maximum number of tokens to generate (default: 4000)
*   `temperature`: The temperature for generation (default: 0.7)

Methods:

### `__init__(model_name, api_key, max_tokens, temperature)`

Initialize the OpenAI client.

*   Args:
    *   `model_name` (str): Name of the OpenAI model to use
    *   `api_key` (Optional[str]): OpenAI API key (if None, uses `OPENAI_API_KEY` environment variable)
    *   `max_tokens` (int): Maximum number of tokens to generate
    *   `temperature` (float): Temperature for generation (0.0 to 1.0)

### `generate(prompt)`

Generate a response from OpenAI.

*   Args:
    *   `prompt` (str): Prompt for generation

Returns:

*   Generated response

### `document_code(code, language, additional_context="")`

Generate documentation for code.

*   Args:
    *   `code` (str): Code to document
    *   `language` (str): Programming language
    *   `additional_context` (Optional[str]): Additional context about the code (default: "")

Returns:

*   Generated documentation

### `explain_code(code, language, additional_context="")`

Generate an explanation for code.

*   Args:
    *   `code` (str): Code to explain
    *   `language` (str): Programming language
    *   `additional_context` (Optional[str]): Additional context about the code (default: "")

Returns:

*   Generated explanation

### `answer_question(question, context=[{"key": "value"}])`

Answer a question based on context.

*   Args:
    *   `question` (str): User question
    *   `context` (Optional[Union[str, List[Dict[str, Any]]]]): Context for answering the question

Returns:

*   Generated answer

### `generate_examples(request, language, additional_context="")`

Generate code examples.

*   Args:
    *   `request` (str): Request for examples
    *   `language` (str): Programming language
    *   `additional_context` (Optional[str]): Additional context for the examples (default: "")

Returns:

*   Generated examples

### `custom_request(template_name, **kwargs)`

Make a custom request using a template.

*   Args:
    *   `template_name` (str): Name of the template to use
    *   **kwargs: Values for template placeholders

Returns:

*   Generated response

### `add_template(name, template)`

Add a new template or override an existing one.

*   Args:
    *   `name` (str): Template name
    *   `template` (str): Template string

Usage Examples
-------------

```python
# Initialize the OpenAI client with default settings
client = OpenAIClient()

# Generate a response from OpenAI
response = client.generate("What is the meaning of life?")
print(response)

# Generate documentation for code
code = "def hello_world():\n    print('Hello, World!')\n"
language = "python"
additional_context = ""
documentation = client.document_code(code, language, additional_context)
print(documentation)

# Answer a question based on context
question = "What is the capital of France?"
context = [{"key": "value"}]
answer = client.answer_question(question, context)
print(answer)
```

Important Dependencies and Relationships
--------------------------------------

This module depends on the `openai` library. It also uses the `prompt_toolkit` library for generating prompts.

Notes
-----

*   This module is designed to work with OpenAI's models, but it may not be compatible with all models or versions.
*   The `generate` method can return responses that are not always accurate or relevant.
*   The `document_code` and `explain_code` methods may not generate high-quality documentation or explanations.

Source Code
------------

```python
# File: ./docstra/core/llm/openai.py

"""
OpenAI API integration for LLM interactions.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional, Union

import openai
from tenacity import retry, stop_after_attempt, wait_exponential

from docstra.core.llm.prompt import PromptBuilder


class OpenAIClient:
    """Client for interacting with OpenAI's models."""

    def __init__(
        self,
        model_name: str = "gpt-4-turbo",
        api_key: Optional[str] = None,
        max_tokens: int = 4000,
        temperature: float = 0.7,
    ):
        """Initialize the OpenAI client.

        Args:
            model_name: Name of the OpenAI model to use
            api_key: OpenAI API key (if None, uses OPENAI_API_KEY env var)
            max_tokens: Maximum number of tokens to generate
            temperature: Temperature for generation (0.0 to 1.0)
        """
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature

        # Get API key from parameter or environment variable
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required")

        # Initialize OpenAI client
        self.client = openai.OpenAI(api_key=self.api_key)

        # Initialize prompt builder
        self.prompt_builder = PromptBuilder()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    def generate(self, prompt: str) -> str:
        """Generate a response from OpenAI.

        Args:
            prompt: Prompt for generation

        Returns:
            Generated response
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[{"role": "user", "content": prompt}],
            )

            return response.choices[0].message.content
        except Exception as e:
            # Log the error and re-raise for retry
            print(f"Error in OpenAI API call: {str(e)}")
            raise

    def document_code(
        self, code: str, language: str, additional_context: str = ""
    ) -> str:
        """Generate documentation for code.

        Args:
            code: Code to document
            language: Programming language
            additional_context: Additional context about the code (default: "")

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
            additional_context: Additional context about the code (default: "")

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
        # ...

    def generate_examples(request, language, additional_context=""):
        # ...

    def custom_request(template_name, **kwargs):
        # ...

    def add_template(name, template):
        # ...
```

Note that this is a basic implementation and may need to be modified or extended based on your specific requirements.


## Source Code

```documenttype.markdown
---
language: documenttype.python
source_file: /Users/jorgenosberg/development/docstra/docstra/core/llm/openai.py
summary: 'OpenAI API Integration for LLM Interactions

  ============================================='
title: openai

---

# OpenAI API Integration for LLM Interactions
=============================================

## Overview

This module provides an interface for interacting with OpenAI's models using the `openai` library. It allows users to generate responses, explain code, answer questions, and more.

## Classes

### `OpenAIClient`

#### Attributes

*   `model_name`: The name of the OpenAI model to use (default: "gpt-4-turbo")
*   `api_key`: The OpenAI API key (if None, uses `OPENAI_API_KEY` environment variable)
*   `max_tokens`: The maximum number of tokens to generate (default: 4000)
*   `temperature`: The temperature for generation (default: 0.7)

#### Methods

### `__init__(model_name, api_key, max_tokens, temperature)`

Initialize the OpenAI client.

*   Args:
    *   `model_name` (str): Name of the OpenAI model to use
    *   `api_key` (Optional[str]): OpenAI API key (if None, uses `OPENAI_API_KEY` environment variable)
    *   `max_tokens` (int): Maximum number of tokens to generate
    *   `temperature` (float): Temperature for generation (0.0 to 1.0)

### `generate(prompt)`

Generate a response from OpenAI.

*   Args:
    *   `prompt` (str): Prompt for generation

Returns:

*   Generated response

### `document_code(code, language, additional_context="")`

Generate documentation for code.

*   Args:
    *   `code` (str): Code to document
    *   `language` (str): Programming language
    *   `additional_context` (Optional[str]): Additional context about the code (default: "")

Returns:

*   Generated documentation

### `explain_code(code, language, additional_context="")`

Generate an explanation for code.

*   Args:
    *   `code` (str): Code to explain
    *   `language` (str): Programming language
    *   `additional_context` (Optional[str]): Additional context about the code (default: "")

Returns:

*   Generated explanation

### `answer_question(question, context=[{"key": "value"}])`

Answer a question based on context.

*   Args:
    *   `question` (str): User question
    *   `context` (Optional[Union[str, List[Dict[str, Any]]]]): Context for answering the question

Returns:

*   Generated answer

### `generate_examples(request, language, additional_context="")`

Generate code examples.

*   Args:
    *   `request` (str): Request for examples
    *   `language` (str): Programming language
    *   `additional_context` (Optional[str]): Additional context for the examples (default: "")

Returns:

*   Generated examples

### `custom_request(template_name, **kwargs)`

Make a custom request using a template.

*   Args:
    *   `template_name` (str): Name of the template to use
    *   **kwargs: Values for template placeholders

Returns:

*   Generated response

### `add_template(name, template)`

Add a new template or override an existing one.

*   Args:
    *   `name` (str): Template name
    *   `template` (str): Template string

## Usage Examples

```python
# Initialize the OpenAI client with default settings
client = OpenAIClient()

# Generate a response from OpenAI
response = client.generate("What is the meaning of life?")
print(response)

# Generate documentation for code
code = "def hello_world():\n    print('Hello, World!')\n"
language = "python"
additional_context = ""
documentation = client.document_code(code, language, additional_context)
print(documentation)

# Answer a question based on context
question = "What is the capital of France?"
context = [{"key": "value"}]
answer = client.answer_question(question, context)
print(answer)
```

## Important Dependencies and Relationships

This module depends on the `openai` library. It also uses the `prompt_toolkit` library for generating prompts.

## Notes

*   This module is designed to work with OpenAI's models, but it may not be compatible with all models or versions.
*   The `generate` method can return responses that are not always accurate or relevant.
*   The `document_code` and `explain_code` methods may not generate high-quality documentation or explanations.


## Source Code

```documenttype.python
# File: ./docstra/core/llm/openai.py

"""
OpenAI API integration for LLM interactions.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional, Union

import openai
from tenacity import retry, stop_after_attempt, wait_exponential

from docstra.core.llm.prompt import PromptBuilder


class OpenAIClient:
    """Client for interacting with OpenAI's models."""

    def __init__(
        self,
        model_name: str = "gpt-4-turbo",
        api_key: Optional[str] = None,
        max_tokens: int = 4000,
        temperature: float = 0.7,
    ):
        """Initialize the OpenAI client.

        Args:
            model_name: Name of the OpenAI model to use
            api_key: OpenAI API key (if None, uses OPENAI_API_KEY env var)
            max_tokens: Maximum number of tokens to generate
            temperature: Temperature for generation (0.0 to 1.0)
        """
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature

        # Get API key from parameter or environment variable
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required")

        # Initialize OpenAI client
        self.client = openai.OpenAI(api_key=self.api_key)

        # Initialize prompt builder
        self.prompt_builder = PromptBuilder()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    def generate(self, prompt: str) -> str:
        """Generate a response from OpenAI.

        Args:
            prompt: Prompt for generation

        Returns:
            Generated response
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[{"role": "user", "content": prompt}],
            )

            return response.choices[0].message.content
        except Exception as e:
            # Log the error and re-raise for retry
            print(f"Error in OpenAI API call: {str(e)}")
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
