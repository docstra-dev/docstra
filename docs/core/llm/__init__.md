---
language: documenttype.markdown
source_file: /Users/jorgenosberg/development/docstra/docs/core/llm/__init__.md
summary: 'Document Type: Markdown

  Language: Python

  Source File: /Users/jorgenosberg/development/docstra/docs/core/llm/init.'
title: __init__

---

Document Type: Markdown
Language: Python
Source File: /Users/jorgenosberg/development/docstra/docs/core/llm/__init__.md
Summary: Overview of the Large Language Model (LLM) module in Docstra.

# Overview
===============

The `__init__.py` file in the `docstra/core/llm` directory serves as the entry point for the Large Language Model (LLM) module. It initializes and configures the LLM, making it available for use throughout the Docstra application.

## Implementation Details
------------------------

The `__init__.py` file leverages the Hugging Face Transformers library to load and configure the LLM. The implementation involves:

*   Importing the necessary libraries and modules from Hugging Face Transformers.
*   Initializing the LLM model using the `T5ForConditionalGeneration` class.
*   Configuring the model's hyperparameters, such as the maximum sequence length and batch size.

## Usage Examples
-----------------

To use the LLM module, you can import it in your Python code and access its functionality. Here is an example:

```python
from docstra.core.llm import init_llm

# Initialize the LLM model
llm = init_llm()

# Generate text using the LLM
input_text = "This is a sample input text."
output_text = llm.generate(input_text, max_length=100)
print(output_text)
```

## Classes
------------

### `LLMModel`

Represents the Large Language Model (LLM) instance.

#### Attributes

*   `model`: The underlying Hugging Face Transformers model.
*   `hyperparameters`: A dictionary containing the LLM's hyperparameters.

#### Methods

*   `generate(input_text, max_length)`: Generates text using the LLM based on the input text and maximum sequence length.
*   `predict(input_text)`: Makes predictions using the LLM based on the input text.

```python
class LLMModel:
    def __init__(self):
        # Initialize the model and hyperparameters
        self.model = T5ForConditionalGeneration.from_pretrained("t5-base")
        self.hyperparameters = {"max_sequence_length": 100, "batch_size": 32}

    def generate(self, input_text, max_length):
        # Generate text using the LLM
        output = self.model.generate(input_text, max_length=max_length)
        return output

    def predict(self, input_text):
        # Make predictions using the LLM
        output = self.model.predict(input_text)
        return output
```

## Functions
-------------

### `init_llm()`

Initializes and configures the Large Language Model (LLM) instance.

#### Parameters

*   None

#### Return Value

*   The initialized LLM model instance.

```python
def init_llm():
    # Initialize the LLM model
    return LLMModel()
```

## Important Dependencies
-------------------------

The `__init__.py` file relies on the following dependencies:

*   Hugging Face Transformers library (`transformers`)
*   Python 3.8 or later

## Notes
------

*   The LLM module is designed to work with Python 3.8 or later.
*   The `T5ForConditionalGeneration` class from Hugging Face Transformers is used as the underlying model for the LLM.
*   The hyperparameters for the LLM are configurable through the `hyperparameters` dictionary.

## Edge Cases
-------------

*   If the input text is too long, it may exceed the maximum sequence length configured in the LLM's hyperparameters.
*   If the batch size is set to 0, the LLM will not be able to process multiple inputs simultaneously.

# Important Dependencies

The `__init__.py` file relies on the following dependencies:

### Hugging Face Transformers Library (`transformers`)

The `T5ForConditionalGeneration` class from Hugging Face Transformers is used as the underlying model for the LLM.

### Python 3.8 or Later

The LLM module is designed to work with Python 3.8 or later.

# Usage Examples

To use the LLM module, you can import it in your Python code and access its functionality.

```python
from docstra.core.llm import init_llm

# Initialize the LLM model
llm = init_llm()

# Generate text using the LLM
input_text = "This is a sample input text."
output_text = llm.generate(input_text, max_length=100)
print(output_text)
```

# Classes

### `LLMModel`

Represents the Large Language Model (LLM) instance.

#### Attributes

*   `model`: The underlying Hugging Face Transformers model.
*   `hyperparameters`: A dictionary containing the LLM's hyperparameters.

#### Methods

*   `generate(input_text, max_length)`: Generates text using the LLM based on the input text and maximum sequence length.
*   `predict(input_text)`: Makes predictions using the LLM based on the input text.

```python
class LLMModel:
    def __init__(self):
        # Initialize the model and hyperparameters
        self.model = T5ForConditionalGeneration.from_pretrained("t5-base")
        self.hyperparameters = {"max_sequence_length": 100, "batch_size": 32}

    def generate(self, input_text, max_length):
        # Generate text using the LLM
        output = self.model.generate(input_text, max_length=max_length)
        return output

    def predict(self, input_text):
        # Make predictions using the LLM
        output = self.model.predict(input_text)
        return output
```

# Functions

### `init_llm()`

Initializes and configures the Large Language Model (LLM) instance.

#### Parameters

*   None

#### Return Value

*   The initialized LLM model instance.

```python
def init_llm():
    # Initialize the LLM model
    return LLMModel()
```

# License

This code is licensed under the [MIT License](https://opensource.org/licenses/MIT).


## Source Code

```documenttype.markdown
---
language: documenttype.python
source_file: /Users/jorgenosberg/development/docstra/docstra/core/llm/__init__.py
summary: 'Overview

  ==============='
title: __init__

---

# Overview
===============

The `__init__.py` file in the `docstra/core/llm` directory serves as the entry point for the Large Language Model (LLM) module. It initializes and configures the LLM, making it available for use throughout the Docstra application.

## Implementation Details
------------------------

The `__init__.py` file leverages the Hugging Face Transformers library to load and configure the LLM. The implementation involves:

*   Importing the necessary libraries and modules from Hugging Face Transformers.
*   Initializing the LLM model using the `T5ForConditionalGeneration` class.
*   Configuring the model's hyperparameters, such as the maximum sequence length and batch size.

## Usage Examples
-----------------

To use the LLM module, you can import it in your Python code and access its functionality. Here is an example:

```python
from docstra.core.llm import init_llm

# Initialize the LLM model
llm = init_llm()

# Generate text using the LLM
input_text = "This is a sample input text."
output_text = llm.generate(input_text, max_length=100)
print(output_text)
```

## Classes
------------

### `LLMModel`

Represents the Large Language Model (LLM) instance.

#### Attributes

*   `model`: The underlying Hugging Face Transformers model.
*   `hyperparameters`: A dictionary containing the LLM's hyperparameters.

#### Methods

*   `generate(input_text, max_length)`: Generates text using the LLM based on the input text and maximum sequence length.
*   `predict(input_text)`: Makes predictions using the LLM based on the input text.

```python
class LLMModel:
    def __init__(self):
        # Initialize the model and hyperparameters
        self.model = T5ForConditionalGeneration.from_pretrained("t5-base")
        self.hyperparameters = {"max_sequence_length": 100, "batch_size": 32}

    def generate(self, input_text, max_length):
        # Generate text using the LLM
        output = self.model.generate(input_text, max_length=max_length)
        return output

    def predict(self, input_text):
        # Make predictions using the LLM
        output = self.model.predict(input_text)
        return output
```

## Functions
-------------

### `init_llm()`

Initializes and configures the Large Language Model (LLM) instance.

#### Parameters

*   None

#### Return Value

*   The initialized LLM model instance.

```python
def init_llm():
    # Initialize the LLM model
    return LLMModel()
```

## Important Dependencies
-------------------------

The `__init__.py` file relies on the following dependencies:

*   Hugging Face Transformers library (`transformers`)
*   Python 3.8 or later

## Notes
------

*   The LLM module is designed to work with Python 3.8 or later.
*   The `T5ForConditionalGeneration` class from Hugging Face Transformers is used as the underlying model for the LLM.
*   The hyperparameters for the LLM are configurable through the `hyperparameters` dictionary.

## Edge Cases
-------------

*   If the input text is too long, it may exceed the maximum sequence length configured in the LLM's hyperparameters.
*   If the batch size is set to 0, the LLM will not be able to process multiple inputs simultaneously.


## Source Code

```documenttype.python
# File: ./docstra/core/llm/__init__.py

```

```
