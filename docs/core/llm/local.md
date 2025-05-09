---
language: documenttype.markdown
source_file: /Users/jorgenosberg/development/docstra/docs/core/llm/local.md
summary: 'Local LLM Module

  ====================='
title: local

---

Local LLM Module
=====================

The `local` module provides a local implementation of the Large Language Model (LLM) used for generating code examples, explanations, and answers to user questions.

Overview
--------

This module is designed to be used as a standalone component in the Docstra framework. It allows users to generate high-quality code examples, explanations, and answers to user questions using a local LLM model.

Classes
-------

### `LocalLLM`

Represents the local LLM model used for generating code examples, explanations, and answers to user questions.

#### Attributes

*   `model`: The underlying LLM model used for generation.
*   `prompt_builder`: An instance of `PromptBuilder` used to construct prompts for the LLM model.

#### Methods

*   `generate(prompt)`: Generates a response to the given prompt using the LLM model.
*   `document_code(code, language, additional_context)`: Generates documentation for the given code snippet.
*   `explain_code(code, language, additional_context)`: Generates an explanation for the given code snippet.
*   `answer_question(question, context)`: Answers a user question based on the provided context.
*   `generate_examples(request, language, additional_context)`: Generates code examples for the given request.
*   `custom_request(template_name, **kwargs)`: Makes a custom request using a template.

### `PromptBuilder`

Constructs prompts for the LLM model used in generating code examples, explanations, and answers to user questions.

#### Attributes

*   `templates`: A dictionary of available templates for constructing prompts.

#### Methods

*   `add_template(name, template)`: Adds a new template or overrides an existing one.
*   `build_document_code_prompt(code, language, additional_context)`: Constructs a prompt for generating documentation for the given code snippet.
*   `build_explain_code_prompt(code, language, additional_context)`: Constructs a prompt for generating an explanation for the given code snippet.
*   `build_answer_question_prompt(question, context)`: Constructs a prompt for answering a user question based on the provided context.
*   `build_generate_examples_prompt(request, language, additional_context)`: Constructs a prompt for generating code examples for the given request.
*   `build_custom_prompt(template_name, **kwargs)`: Constructs a prompt using a template.

Functions
---------

### `generate(prompt)`

Generates a response to the given prompt using the LLM model.

#### Parameters

*   `prompt`: The input prompt to generate a response for.

#### Returns

*   A string representing the generated response.

### `document_code(code, language, additional_context)`

Generates documentation for the given code snippet.

#### Parameters

*   `code`: The code snippet to document.
*   `language`: The programming language of the code snippet.
*   `additional_context`: Additional context about the code snippet (optional).

#### Returns

*   A string representing the generated documentation.

### `explain_code(code, language, additional_context)`

Generates an explanation for the given code snippet.

#### Parameters

*   `code`: The code snippet to explain.
*   `language`: The programming language of the code snippet.
*   `additional_context`: Additional context about the code (optional).

#### Returns

*   A string representing the generated explanation.

### `answer_question(question, context)`

Answers a user question based on the provided context.

#### Parameters

*   `question`: The user question to answer.
*   `context`: The context for answering the question.

#### Returns

*   A string representing the generated answer.

### `generate_examples(request, language, additional_context)`

Generates code examples for the given request.

#### Parameters

*   `request`: The request for examples.
*   `language`: The programming language of the request.
*   `additional_context`: Additional context for the examples (optional).

#### Returns

*   A string representing the generated examples.

### `custom_request(template_name, **kwargs)`

Makes a custom request using a template.

#### Parameters

*   `template_name`: The name of the template to use.
*   `**kwargs`: Values for template placeholders.

#### Returns

*   A string representing the generated response.

Usage Examples
-------------

### Generating Code Examples

```python
llm = LocalLLM()
request = "Write a function that takes an integer as input and returns its square."
examples = llm.generate_examples(request, language="Python")
print(examples)
```

### Documenting Code

```python
llm = LocalLLM()
code = """
def greet(name):
    print(f"Hello, {name}!")
"""
documentation = llm.document_code(code, language="Python")
print(documentation)
```

### Explaining Code

```python
llm = LocalLLM()
code = """
def greet(name):
    print(f"Hello, {name}!")
"""
explanation = llm.explain_code(code, language="Python")
print(explanation)
```

Important Dependencies and Relationships
--------------------------------------

The `LocalLLM` module depends on the following:

*   The underlying LLM model for generating responses.
*   The `PromptBuilder` class for constructing prompts.

Relationships with other modules:

*   The `LocalLLM` module is part of the Docstra framework, which provides a comprehensive platform for natural language processing tasks.
*   The `PromptBuilder` class is used in conjunction with the `LocalLLM` model to generate responses.

Notes
-----

*   The `LocalLLM` module uses a local LLM model for generating responses, which may not be as powerful as cloud-based models but provides faster response times and lower latency.
*   The `PromptBuilder` class is used to construct prompts for the LLM model, which can affect the quality of the generated responses.

Edge Cases
----------

*   The `LocalLLM` module may not perform well on very long or complex inputs, as it relies on a local LLM model that may not be able to handle such cases.
*   The `PromptBuilder` class may require additional configuration or tuning to optimize its performance for specific use cases.


## Source Code

```documenttype.markdown
---
language: documenttype.python
source_file: /Users/jorgenosberg/development/docstra/docstra/core/llm/local.py
summary: 'Local LLM Module

  ====================='
title: local

---

**Local LLM Module**
=====================

The `local` module provides a local implementation of the Large Language Model (LLM) used for generating code examples, explanations, and answers to user questions.

**Overview**
------------

This module is designed to be used as a standalone component in the Docstra framework. It allows users to generate high-quality code examples, explanations, and answers to user questions using a local LLM model.

**Classes**
-----------

### `LocalLLM`

Represents the local LLM model used for generating code examples, explanations, and answers to user questions.

#### Attributes

*   `model`: The underlying LLM model used for generation.
*   `prompt_builder`: An instance of `PromptBuilder` used to construct prompts for the LLM model.

#### Methods

*   `generate(prompt)`: Generates a response to the given prompt using the LLM model.
*   `document_code(code, language, additional_context)`: Generates documentation for the given code snippet.
*   `explain_code(code, language, additional_context)`: Generates an explanation for the given code snippet.
*   `answer_question(question, context)`: Answers a user question based on the provided context.
*   `generate_examples(request, language, additional_context)`: Generates code examples for the given request.
*   `custom_request(template_name, **kwargs)`: Makes a custom request using a template.

### `PromptBuilder`

Constructs prompts for the LLM model used in generating code examples, explanations, and answers to user questions.

#### Attributes

*   `templates`: A dictionary of available templates for constructing prompts.

#### Methods

*   `add_template(name, template)`: Adds a new template or overrides an existing one.
*   `build_document_code_prompt(code, language, additional_context)`: Constructs a prompt for generating documentation for the given code snippet.
*   `build_explain_code_prompt(code, language, additional_context)`: Constructs a prompt for generating an explanation for the given code snippet.
*   `build_answer_question_prompt(question, context)`: Constructs a prompt for answering a user question based on the provided context.
*   `build_generate_examples_prompt(request, language, additional_context)`: Constructs a prompt for generating code examples for the given request.
*   `build_custom_prompt(template_name, **kwargs)`: Constructs a prompt using a template.

**Functions**
-------------

### `generate(prompt)`

Generates a response to the given prompt using the LLM model.

#### Parameters

*   `prompt`: The input prompt to generate a response for.

#### Returns

*   A string representing the generated response.

### `document_code(code, language, additional_context)`

Generates documentation for the given code snippet.

#### Parameters

*   `code`: The code snippet to document.
*   `language`: The programming language of the code snippet.
*   `additional_context`: Additional context about the code snippet (optional).

#### Returns

*   A string representing the generated documentation.

### `explain_code(code, language, additional_context)`

Generates an explanation for the given code snippet.

#### Parameters

*   `code`: The code snippet to explain.
*   `language`: The programming language of the code snippet.
*   `additional_context`: Additional context about the code snippet (optional).

#### Returns

*   A string representing the generated explanation.

### `answer_question(question, context)`

Answers a user question based on the provided context.

#### Parameters

*   `question`: The user question to answer.
*   `context`: The context for answering the question.

#### Returns

*   A string representing the generated answer.

### `generate_examples(request, language, additional_context)`

Generates code examples for the given request.

#### Parameters

*   `request`: The request for generating code examples.
*   `language`: The programming language of the code snippet.
*   `additional_context`: Additional context about the code snippet (optional).

#### Returns

*   A string representing the generated code examples.

### `custom_request(template_name, **kwargs)`

Makes a custom request using a template.

#### Parameters

*   `template_name`: The name of the template to use.
*   `**kwargs`: Values for template placeholders.

#### Returns

*   A string representing the generated response.

**Usage Examples**
-----------------

### Generating Code Examples

```python
llm = LocalLLM()
prompt = llm.prompt_builder.build_generate_examples_prompt(
    request="Write a function to calculate the sum of two numbers",
    language="Python",
    additional_context={"example_input": "2 + 3"}
)
print(llm.generate(prompt))
```

### Generating Documentation

```python
llm = LocalLLM()
code = "def add(a, b): return a + b"
language = "Python"
additional_context = {"example_input": "2 + 3"}
prompt = llm.prompt_builder.build_document_code_prompt(code, language, additional_context)
print(llm.generate(prompt))
```

### Generating an Explanation

```python
llm = LocalLLM()
code = "def add(a, b): return a + b"
language = "Python"
additional_context = {"example_input": "2 + 3"}
prompt = llm.prompt_builder.build_explain_code_prompt(code, language, additional_context)
print(llm.generate(prompt))
```

### Answering a User Question

```python
llm = LocalLLM()
question = "What is the sum of 2 and 3?"
context = {"example_input": "2 + 3"}
prompt = llm.prompt_builder.build_answer_question_prompt(question, context)
print(llm.generate(prompt))
```

**Notes**
-------

*   The `LocalLLM` module uses a local LLM model for generating code examples, explanations, and answers to user questions.
*   The `PromptBuilder` class is used to construct prompts for the LLM model.
*   The `generate` method generates a response to the given prompt using the LLM model.
*   The `document_code`, `explain_code`, `answer_question`, and `generate_examples` methods generate documentation, explanations, answers, and code examples, respectively.


## Source Code

```documenttype.python
# File: ./docstra/core/llm/local.py

"""
Local model integration for LLM interactions.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    StoppingCriteria,
    StoppingCriteriaList,
    TextIteratorStreamer,
)

from docstra.core.llm.prompt import PromptBuilder


class KeywordsStoppingCriteria(StoppingCriteria):
    """Custom stopping criteria based on keywords."""

    def __init__(self, keywords, tokenizer):
        """Initialize the stopping criteria.

        Args:
            keywords: List of keywords to stop on
            tokenizer: Tokenizer for the model
        """
        self.keywords = keywords
        self.tokenizer = tokenizer

        # Pre-tokenize keywords for faster comparison
        self.keyword_ids = []
        for keyword in keywords:
            ids = tokenizer.encode(keyword, add_special_tokens=False)
            if len(ids) > 0:
                self.keyword_ids.append(ids)

    def __call__(self, input_ids, scores, **kwargs):
        """Check if any stopping keyword is generated.

        Args:
            input_ids: Current sequence of token IDs
            scores: Scores for each token
            **kwargs: Additional arguments

        Returns:
            True if stopping criteria met, False otherwise
        """
        # Check for each keyword
        for keyword_ids in self.keyword_ids:
            # Check if any keyword appears at the end of the sequence
            if len(keyword_ids) <= len(input_ids[0]):
                # Compare the end of the sequence with the keyword
                if input_ids[0][-len(keyword_ids) :].tolist() == keyword_ids:
                    return True

        return False


class LocalModelClient:
    """Client for interacting with local transformer models."""

    def __init__(
        self,
        model_name: str = "TheBloke/Llama-2-7b-Chat-GGUF",
        model_path: Optional[str] = None,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        device: str = "auto",
    ):
        """Initialize the local model client.

        Args:
            model_name: Name or path of the model to use
            model_path: Optional local path to the model
            max_tokens: Maximum number of tokens to generate
            temperature: Temperature for generation (0.0 to 1.0)
            device: Device to run the model on ('auto', 'cpu', 'cuda', etc.)
        """
        self.model_name = model_name
        self.model_path = model_path or model_name
        self.max_tokens = max_tokens
        self.temperature = temperature

        # Determine device
        if device == "auto":
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

        # Initialize model and tokenizer
        print(f"Loading model {self.model_path} on {self.device}...")

        try:
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_path, trust_remote_code=True
            )

            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                device_map=self.device,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                trust_remote_code=True,
                low_cpu_mem_usage=True,
            )
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            raise

        # Configure stopping criteria
        self.stopping_keywords = ["<|endoftext|>", "<|im_end|>", "</s>"]

        # Initialize prompt builder
        self.prompt_builder = PromptBuilder()

    def generate(self, prompt: str, stream: bool = False) -> str:
        """Generate a response from the local model.

        Args:
            prompt: Prompt for generation
            stream: Whether to stream the response

        Returns:
            Generated response
        """
        # Tokenize the prompt
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)

        # Setup stopping criteria
        stopping_criteria = StoppingCriteriaList(
            [KeywordsStoppingCriteria(self.stopping_keywords, self.tokenizer)]
        )

        # Generate
        if stream:
            # Setup streamer
            streamer = TextIteratorStreamer(
                self.tokenizer, skip_prompt=True, skip_special_tokens=True
            )

            # Start generation in a separate thread
            generation_kwargs = {
                "input_ids": inputs.input_ids,
                "attention_mask": inputs.attention_mask,
                "max_new_tokens": self.max_tokens,
                "temperature": self.temperature,
                "do_sample": self.temperature > 0,
                "stopping_criteria": stopping_criteria,
                "streamer": streamer,
            }

            # Start generation thread
            import threading

            thread = threading.Thread(
                target=self.model.generate, kwargs=generation_kwargs
            )
            thread.start()

            # Stream tokens
            generated_text = ""
            for text in streamer:
                generated_text += text

            return str(generated_text)
        else:
            # Generate in one go
            outputs = self.model.generate(
                inputs.input_ids,
                attention_mask=inputs.attention_mask,
                max_new_tokens=self.max_tokens,
                temperature=self.temperature,
                do_sample=self.temperature > 0,
                stopping_criteria=stopping_criteria,
            )

            # Decode the generated tokens
            generated_text = self.tokenizer.decode(
                outputs[0][inputs.input_ids.shape[1] :], skip_special_tokens=True
            )

            return generated_text

    def document_code(
        self,
        code: str,
        language: str,
        additional_context: str = "",
        stream: bool = False,
    ) -> str:
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
    ) -> str:
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
    ) -> str:
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
    ) -> str:
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

    def custom_request(self, template_name: str, stream: bool = False, **kwargs) -> str:
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
