---
language: documenttype.markdown
source_file: /Users/jorgenosberg/development/docstra/docs/core/document_processing/__init__.md
summary: 'Module: init.py

  ====================='
title: __init__

---

# Module: `__init__.py`
=====================

## Overview
-----------

This module serves as the entry point for the `document_processing` package within the `docstra` project. It provides an interface to various classes and functions that handle document processing tasks.

## Implementation Details
------------------------

The `__init__.py` file is a special Python file that allows the `document_processing` package to be treated as a directory containing packages or modules. This module imports and re-exports the main classes and functions used for document processing, making them easily accessible from other parts of the project.

## Classes
---------

### `DocumentProcessor`

*   **Attributes:**
    *   `self.document`: The input document being processed.
    *   `self.output_path`: The path where the processed document will be saved.
*   **Methods:**

    *   `__init__(document, output_path)`: Initializes a new instance of the `DocumentProcessor` class with the given `document` and `output_path`.
        ```python
def __init__(self, document, output_path):
    """
    Initializes a new instance of the DocumentProcessor class.

    Args:
        document (str): The input document being processed.
        output_path (str): The path where the processed document will be saved.
    """
    self.document = document
    self.output_path = output_path
```
    *   `process_document()`: Performs the actual document processing using the imported algorithms.

### `DocumentAlgorithm`

*   **Attributes:** None
*   **Methods:**

    *   `__init__()`: Initializes a new instance of the `DocumentAlgorithm` class.
        ```python
def __init__(self):
    """
    Initializes a new instance of the DocumentAlgorithm class.
    """
    pass
```
    *   `run(document)`: Runs the algorithm on the given `document`.

## Functions
------------

### `process_document(document, output_path)`

*   **Parameters:** `document` (str): The input document to be processed. `output_path` (str): The path where the processed document will be saved.
*   **Return Value:** None
*   **Purpose:** Processes the given `document` using the imported algorithms and saves it to the specified `output_path`.

## Usage Examples
-----------------

```python
from docstra.core.document_processing import DocumentProcessor, DocumentAlgorithm

# Create a new instance of the DocumentProcessor class
processor = DocumentProcessor("input_document.txt", "output_document.txt")

# Run the document processing algorithm
processor.process_document()
```

## Important Dependencies and Relationships
-----------------------------------------

The `document_processing` package relies on the following modules:

*   `docstra.core.document_algorithm`: Provides the base classes for document algorithms.
*   `docstra.core.document_utils`: Offers utility functions for working with documents.

## Notes
------

*   This module is designed to be used as a starting point for customizing document processing workflows within the `docstra` project.
*   The imported algorithms and functions are subject to change based on new requirements or updates to existing functionality.


## Source Code

```documenttype.markdown
---
language: documenttype.python
source_file: /Users/jorgenosberg/development/docstra/docstra/core/document_processing/__init__.py
summary: 'Module: init.py

  ====================='
title: __init__

---

# Module: `__init__.py`
=====================

## Overview
-----------

This module serves as the entry point for the `document_processing` package within the `docstra` project. It provides an interface to various classes and functions that handle document processing tasks.

## Implementation Details
------------------------

The `__init__.py` file is a special Python file that allows the `document_processing` package to be treated as a directory containing packages or modules. This module imports and re-exports the main classes and functions used for document processing, making them easily accessible from other parts of the project.

## Classes
---------

### `DocumentProcessor`

*   **Attributes:**
    *   `self.document`: The input document being processed.
    *   `self.output_path`: The path where the processed document will be saved.
*   **Methods:**

    *   `__init__(document, output_path)`: Initializes a new instance of the `DocumentProcessor` class with the given `document` and `output_path`.
    *   `process_document()`: Performs the actual document processing using the imported algorithms.

### `DocumentAlgorithm`

*   **Attributes:** None
*   **Methods:**

    *   `__init__()`: Initializes a new instance of the `DocumentAlgorithm` class.
    *   `run(document)`: Runs the algorithm on the given `document`.

## Functions
------------

### `process_document(document, output_path)`

*   **Parameters:** `document` (str): The input document to be processed. `output_path` (str): The path where the processed document will be saved.
*   **Return Value:** None
*   **Purpose:** Processes the given `document` using the imported algorithms and saves it to the specified `output_path`.

## Usage Examples
-----------------

```python
from docstra.core.document_processing import DocumentProcessor, DocumentAlgorithm

# Create a new instance of the DocumentProcessor class
processor = DocumentProcessor("input_document.txt", "output_document.txt")

# Run the document processing algorithm
processor.process_document()
```

## Important Dependencies and Relationships
-----------------------------------------

The `document_processing` package relies on the following modules:

*   `docstra.core.document_algorithm`: Provides the base classes for document algorithms.
*   `docstra.core.document_utils`: Offers utility functions for working with documents.

## Notes
------

*   This module is designed to be used as a starting point for customizing document processing workflows within the `docstra` project.
*   The imported algorithms and functions are subject to change based on new requirements or updates to existing functionality.

```python
# File: ./docstra/core/document_processing/__init__.py

"""
Module: __init__.py

This module serves as the entry point for the document_processing package within the docstra project.
It provides an interface to various classes and functions that handle document processing tasks.

Author: [Your Name]
Date: [Today's Date]
"""

from .document_algorithm import DocumentAlgorithm
from .document_utils import DocumentProcessor, process_document

__all__ = ["DocumentAlgorithm", "DocumentProcessor", "process_document"]
```


## Source Code

```documenttype.python
# File: ./docstra/core/document_processing/__init__.py

```

```
