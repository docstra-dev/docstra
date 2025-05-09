---
language: documenttype.markdown
source_file: /Users/jorgenosberg/development/docstra/docs/core/llm/prompt.md
summary: 'Prompt Documentation

  =========================='
title: prompt

---

**Prompt Documentation**
==========================

The `prompt.py` module provides a set of classes and functions for generating prompts for various tasks related to code documentation. The primary goal is to assist in creating high-quality, well-structured documentation that explains code effectively.

**Overview**
------------

This module uses natural language processing (NLP) techniques to generate prompts for different documentation tasks. It includes two main classes: `PromptTemplate` and `PromptBuilder`. The `PromptTemplate` class represents a template for formatting prompts, while the `PromptBuilder` class is a builder that constructs prompts for specific tasks.

**Classes**
-----------

### PromptTemplate

Represents a template for formatting prompts for LLM interactions.

#### Attributes

*   `template`: A string containing placeholders for values to be filled in.

#### Methods

*   `__init__(self, template: str)`: Initializes the prompt template with a given string.
*   `format(self, **kwargs) -> str`: Formats the template with provided values and returns the resulting prompt.

### PromptBuilder

A builder class for constructing prompts for different documentation tasks.

#### Attributes

*   `templates`: A dictionary containing default templates for various tasks (e.g., document code, explain code, answer question, generate examples).

#### Methods

*   `__init__(self, custom_templates: Optional[Dict[str, str]] = None)`: Initializes the prompt builder with optional custom templates.
*   `build_document_code_prompt(self, code: str, language: str, additional_context: str = "") -> str`: Builds a prompt for code documentation.
*   `build_explain_code_prompt(self, code: str, language: str, additional_context: str = "") -> str`: Builds a prompt for code explanation.
*   `build_answer_question_prompt(self, question: str, context: Union[str, List[Dict[str, Any]]]) -> str`: Builds a prompt for answering a question.
*   `build_generate_examples_prompt(self, request: str, language: str, additional_context: str = "") -> str`: Builds a prompt for generating code examples.
*   `build_custom_prompt(self, template_name: str, **kwargs) -> str`: Builds a prompt using a custom template.
*   `add_template(self, name: str, template: str) -> None`: Adds a new template or overrides an existing one.

**Functions**
-------------

### build_document_code_prompt

Builds a prompt for code documentation.

#### Parameters

*   `code`: The code to be documented.
*   `language`: The programming language of the code.
*   `additional_context`: Additional context for the prompt (optional).

#### Returns

A formatted prompt for code documentation.

### build_explain_code_prompt

Builds a prompt for code explanation.

#### Parameters

*   `code`: The code to be explained.
*   `language`: The programming language of the code.
*   `additional_context`: Additional context for the prompt (optional).

#### Returns

A formatted prompt for code explanation.

### build_answer_question_prompt

Builds a prompt for answering a question.

#### Parameters

*   `question`: The question to be answered.
*   `context`: The context for answering the question (string or list of chunks).

#### Returns

A formatted prompt for answering a question.

### build_generate_examples_prompt

Builds a prompt for generating code examples.

#### Parameters

*   `request`: The request for examples.
*   `language`: The programming language of the code.
*   `additional_context`: Additional context for the prompt (optional).

#### Returns

A formatted prompt for generating code examples.

### build_custom_prompt

Builds a prompt using a custom template.

#### Parameters

*   `template_name`: The name of the template to use.
*   `**kwargs`: Values for template placeholders.

#### Returns

A formatted prompt using the specified template.

### add_template

Adds a new template or overrides an existing one.

#### Parameters

*   `name`: The name of the template to add or override.
*   `template`: The string containing the template.

#### Returns

None

**Usage Examples**
-------------------

```python
from prompt import PromptBuilder, PromptTemplate

# Create a prompt builder with default templates
builder = PromptBuilder()

# Build a prompt for code documentation
prompt = builder.build_document_code_prompt("example_code", "python")
print(prompt)

# Build a prompt for code explanation
prompt = builder.build_explain_code_prompt("example_code", "python")
print(prompt)

# Build a prompt for answering a question
question = "What is the purpose of this function?"
context = {"code": "example_code"}
prompt = builder.build_answer_question_prompt(question, context)
print(prompt)

# Build a prompt for generating code examples
request = "Write a function to calculate the sum of two numbers."
language = "python"
prompt = builder.build_generate_examples_prompt(request, language)
print(prompt)

# Create a custom template and build a prompt using it
template_name = "custom_template"
kwargs = {"key": "value"}
prompt = builder.build_custom_prompt(template_name, **kwargs)
print(prompt)

# Add a new template to the builder
builder.add_template("new_template", "This is a new template.")
```

**Important Dependencies and Relationships**
--------------------------------------------

The `prompt.py` module depends on the following:

*   The `PromptBuilder` class uses the `templates` dictionary, which contains default templates for various tasks.
*   The `build_custom_prompt` method relies on the existence of a custom template with the specified name.

**Notes and Limitations**
-------------------------

*   The `prompt.py` module is designed to work with LLM interactions, but it can be adapted for other use cases as well.
*   The templates used in this module are just examples and may need to be modified or extended to suit specific requirements.
*   The `build_custom_prompt` method raises a `ValueError` if the specified template does not exist.


## Source Code

```documenttype.markdown
---
language: documenttype.python
source_file: /Users/jorgenosberg/development/docstra/docstra/core/llm/prompt.py
summary: 'Prompt Documentation

  =========================='
title: prompt

---

**Prompt Documentation**
==========================

**Overview**
------------

The `prompt.py` module provides a set of classes and functions for generating prompts for various tasks related to code documentation. The primary goal is to assist in creating high-quality, well-structured documentation that explains code effectively.

**Classes**
-----------

### PromptTemplate

Represents a template for formatting prompts for LLM interactions.

#### Attributes

*   `template`: A string containing placeholders for values to be filled in.

#### Methods

*   `__init__(self, template: str)`: Initializes the prompt template with a given string.
*   `format(self, **kwargs) -> str`: Formats the template with provided values and returns the resulting prompt.

### PromptBuilder

A builder class for constructing prompts for different documentation tasks.

#### Attributes

*   `templates`: A dictionary containing default templates for various tasks (e.g., document code, explain code, answer question, generate examples).

#### Methods

*   `__init__(self, custom_templates: Optional[Dict[str, str]] = None)`: Initializes the prompt builder with optional custom templates.
*   `build_document_code_prompt(self, code: str, language: str, additional_context: str = "") -> str`: Builds a prompt for code documentation.
*   `build_explain_code_prompt(self, code: str, language: str, additional_context: str = "") -> str`: Builds a prompt for code explanation.
*   `build_answer_question_prompt(self, question: str, context: Union[str, List[Dict[str, Any]]]) -> str`: Builds a prompt for answering a question.
*   `build_generate_examples_prompt(self, request: str, language: str, additional_context: str = "") -> str`: Builds a prompt for generating code examples.
*   `build_custom_prompt(self, template_name: str, **kwargs) -> str`: Builds a prompt using a custom template.
*   `add_template(self, name: str, template: str) -> None`: Adds a new template or overrides an existing one.

**Functions**
-------------

### build_document_code_prompt

Builds a prompt for code documentation.

#### Parameters

*   `code`: The code to be documented.
*   `language`: The programming language of the code.
*   `additional_context`: Additional context for the prompt (optional).

#### Returns

A formatted prompt for code documentation.

### build_explain_code_prompt

Builds a prompt for code explanation.

#### Parameters

*   `code`: The code to be explained.
*   `language`: The programming language of the code.
*   `additional_context`: Additional context for the prompt (optional).

#### Returns

A formatted prompt for code explanation.

### build_answer_question_prompt

Builds a prompt for answering a question.

#### Parameters

*   `question`: The question to be answered.
*   `context`: The context for the prompt (e.g., code snippet, error message).

#### Returns

A formatted prompt for answering a question.

### build_generate_examples_prompt

Builds a prompt for generating code examples.

#### Parameters

*   `request`: The request for examples.
*   `language`: The programming language of the code.
*   `additional_context`: Additional context for the prompt (optional).

#### Returns

A formatted prompt for generating code examples.

### build_custom_prompt

Builds a prompt using a custom template.

#### Parameters

*   `template_name`: The name of the template to use.
*   `**kwargs`: Values for template placeholders.

#### Returns

A formatted prompt using the specified template.

### add_template

Adds a new template or overrides an existing one.

#### Parameters

*   `name`: The name of the template to add or override.
*   `template`: The string containing the template.

#### Returns

None

**Usage Examples**
-------------------

```python
from prompt import PromptBuilder, PromptTemplate

# Create a prompt builder with default templates
builder = PromptBuilder()

# Build a prompt for code documentation
prompt = builder.build_document_code_prompt("example_code", "python")
print(prompt)

# Build a prompt for code explanation
prompt = builder.build_explain_code_prompt("example_code", "python")
print(prompt)

# Build a prompt for answering a question
question = "What is the purpose of this function?"
context = {"code": "example_code"}
prompt = builder.build_answer_question_prompt(question, context)
print(prompt)

# Build a prompt for generating code examples
request = "Write a function to calculate the sum of two numbers."
language = "python"
prompt = builder.build_generate_examples_prompt(request, language)
print(prompt)

# Create a custom template and build a prompt using it
template_name = "custom_template"
kwargs = {"key": "value"}
prompt = builder.build_custom_prompt(template_name, **kwargs)
print(prompt)

# Add a new template to the builder
builder.add_template("new_template", "This is a new template.")
```

**Important Dependencies and Relationships**
--------------------------------------------

The `prompt.py` module depends on the following:

*   The `PromptBuilder` class uses the `templates` dictionary, which contains default templates for various tasks.
*   The `build_custom_prompt` method relies on the existence of a custom template with the specified name.

**Notes and Limitations**
-------------------------

*   The `prompt.py` module is designed to work with LLM interactions, but it can be adapted for other use cases as well.
*   The templates used in this module are just examples and may need to be modified or extended to suit specific requirements.
*   The `build_custom_prompt` method raises a `ValueError` if the specified template does not exist.


## Source Code

```documenttype.python
# File: ./docstra/core/llm/prompt.py

"""
Prompt formatting for LLM interactions.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union


class PromptTemplate:
    """Template for formatting prompts for LLM interactions."""

    def __init__(self, template: str):
        """Initialize the prompt template.

        Args:
            template: Template string with placeholders
        """
        self.template = template

    def format(self, **kwargs) -> str:
        """Format the template with provided values.

        Args:
            **kwargs: Values for template placeholders

        Returns:
            Formatted prompt
        """
        return self.template.format(**kwargs)


class PromptBuilder:
    """Builder for constructing prompts for different documentation tasks."""

    # Default templates for different tasks
    DEFAULT_TEMPLATES = {
        "document_code": """
You are a helpful assistant that generates high-quality code documentation.
Your task is to document the following code according to best practices.

CODE TO DOCUMENT:
```{language}
{code}
```

{additional_context}

Please provide clear and concise documentation that explains:
1. What the code does (overview)
2. How it works (implementation details)
3. How to use it (usage examples if applicable)
4. Any important parameters, return values, or side effects

Format your response as properly formatted documentation following {language} best practices.
""",
        "explain_code": """
You are a helpful assistant that explains code clearly.
Please explain the following code in a way that's easy to understand:

```{language}
{code}
```

{additional_context}

Your explanation should cover:
1. The purpose of this code
2. How it works step by step
3. Any important concepts or patterns used
4. Potential edge cases or limitations

Use clear language and provide a thorough explanation.
""",
        "answer_question": """
You are a helpful assistant that answers questions about codebases.
The user has asked the following question:

USER QUESTION: {question}

Based on the context from the codebase provided below, please answer the question:

{context}

If the context doesn't contain enough information to provide a complete answer, 
acknowledge the limitations and provide the best answer you can based on the available context.
""",
        "generate_examples": """
You are a helpful assistant that generates code examples.
Please generate example code for: {request}

The examples should be:
1. Clear and well-commented
2. Follow best practices
3. Demonstrate practical usage
4. Be complete enough to run

{additional_context}

Provide the example in {language} and explain key aspects of how it works.
""",
    }

    def __init__(self, custom_templates: Optional[Dict[str, str]] = None):
        """Initialize the prompt builder.

        Args:
            custom_templates: Optional custom templates to override defaults
        """
        self.templates = self.DEFAULT_TEMPLATES.copy()

        if custom_templates:
            self.templates.update(custom_templates)

    def build_document_code_prompt(
        self, code: str, language: str, additional_context: str = ""
    ) -> str:
        """Build a prompt for code documentation.

        Args:
            code: Code to document
            language: Programming language
            additional_context: Additional context about the code

        Returns:
            Formatted prompt
        """
        template = PromptTemplate(self.templates["document_code"])
        return template.format(
            code=code, language=language, additional_context=additional_context
        )

    def build_explain_code_prompt(
        self, code: str, language: str, additional_context: str = ""
    ) -> str:
        """Build a prompt for code explanation.

        Args:
            code: Code to explain
            language: Programming language
            additional_context: Additional context about the code

        Returns:
            Formatted prompt
        """
        template = PromptTemplate(self.templates["explain_code"])
        return template.format(
            code=code, language=language, additional_context=additional_context
        )

    def build_answer_question_prompt(
        self, question: str, context: Union[str, List[Dict[str, Any]]]
    ) -> str:
        """Build a prompt for answering a question.

        Args:
            question: User question
            context: Context for answering the question (string or list of chunks)

        Returns:
            Formatted prompt
        """
        template = PromptTemplate(self.templates["answer_question"])

        # Format context if it's a list of chunks
        if isinstance(context, list):
            formatted_context = "\n\n".join(
                [
                    f"--- {chunk.get('metadata', {}).get('document_id', 'Unknown')} "
                    f"(lines {chunk.get('metadata', {}).get('start_line', '?')}-"
                    f"{chunk.get('metadata', {}).get('end_line', '?')}) ---\n"
                    f"{chunk.get('content', '')}"
                    for chunk in context
                ]
            )
        else:
            formatted_context = context

        return template.format(question=question, context=formatted_context)

    def build_generate_examples_prompt(
        self, request: str, language: str, additional_context: str = ""
    ) -> str:
        """Build a prompt for generating code examples.

        Args:
            request: Request for examples
            language: Programming language
            additional_context: Additional context for the examples

        Returns:
            Formatted prompt
        """
        template = PromptTemplate(self.templates["generate_examples"])
        return template.format(
            request=request, language=language, additional_context=additional_context
        )

    def build_custom_prompt(self, template_name: str, **kwargs) -> str:
        """Build a prompt using a custom template.

        Args:
            template_name: Name of the template to use
            **kwargs: Values for template placeholders

        Returns:
            Formatted prompt

        Raises:
            ValueError: If the template doesn't exist
        """
        if template_name not in self.templates:
            raise ValueError(f"Template '{template_name}' not found")

        template = PromptTemplate(self.templates[template_name])
        return template.format(**kwargs)

    def add_template(self, name: str, template: str) -> None:
        """Add a new template or override an existing one.

        Args:
            name: Template name
            template: Template string
        """
        self.templates[name] = template

```

```
