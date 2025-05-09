---
language: documenttype.markdown
source_file: /Users/jorgenosberg/development/docstra/docs/core/utils/__init__.md
summary: 'Module: init.py

  ====================='
title: __init__

---

# Module: `__init__.py`
=====================

## Overview
-----------

This module serves as the entry point for the `docstra` project's utility functions. It provides a centralized location for importing and utilizing various helper classes, functions, and variables throughout the application.

## Implementation Details
------------------------

The contents of this module are generated automatically by Python's `__init__.py` file mechanism. This allows the `docstra.core.utils` package to be treated as a directory containing an initialization file, rather than a single executable file.

## Classes
---------

### `DocstraUtils`

*   **Attributes:**
    *   `__init__`: Initializes the utility class.
    *   `_utils`: A dictionary of available utility functions.
*   **Methods:**

    *   `add_utility(func)`: Registers a new utility function with the `_utils` dictionary.

        ```python
def add_utility(self, func):
    """
    Registers a new utility function with the _utils dictionary.

    Args:
        func (function): The utility function to register.
    """
    self._utils[func.__name__] = func
```

### `DocstraConfig`

*   **Attributes:**
    *   `_config`: A dictionary of configuration settings.
*   **Methods:**

    *   `load_config(config_file)`: Loads configuration settings from a file.

        ```python
def load_config(self, config_file):
    """
    Loads configuration settings from a file.

    Args:
        config_file (str): The path to the configuration file.
    """
    with open(config_file, 'r') as f:
        self._config = json.load(f)
```

## Functions
------------

### `get_utility(func_name)`

*   **Parameters:**
    *   `func_name` (str): The name of the utility function to retrieve.

*   **Return Value:**
    *   A reference to the registered utility function.

        ```python
def get_utility(self, func_name):
    """
    Retrieves a registered utility function by its name.

    Args:
        func_name (str): The name of the utility function to retrieve.

    Returns:
        function: The registered utility function.
    """
    return self._utils.get(func_name)
```

## Usage Examples
-----------------

### Importing Utility Functions

To utilize the utility functions, import them from this module:

```python
from docstra.core.utils import get_utility

# Example usage:
utility_func = get_utility('my_utility')
result = utility_func()
```

### Registering New Utility Functions

To register a new utility function, use the `add_utility` method:

```python
from docstra.core.utils import DocstraUtils

utils = DocstraUtils()

def my_new_utility():
    # Implementation of the new utility function
    pass

utils.add_utility(my_new_utility)
```

## Important Dependencies and Relationships
-----------------------------------------

This module relies on the following dependencies:

*   `json`: For loading configuration settings from files.
*   `docstra.core.config`: For accessing configuration settings.

It is recommended to import these dependencies in the main application file (`__main__.py`) or other initialization modules.

## Notes and Limitations
-----------------------

*   This module is designed to be a centralized location for utility functions, but it does not provide any specific functionality itself.
*   The `add_utility` method allows registering new utility functions, but it does not enforce any validation or sanitization of the registered functions.
*   The `_utils` dictionary stores all registered utility functions, which can lead to performance issues if the number of registered functions grows excessively.

## Source Code
-------------

```python
# File: ./docstra/core/utils/__init__.py

import json
from .config import DocstraConfig

class DocstraUtils:
    def __init__(self):
        self._utils = {}

    def add_utility(self, func):
        """
        Registers a new utility function with the _utils dictionary.

        Args:
            func (function): The utility function to register.
        """
        self._utils[func.__name__] = func

class DocstraConfig(DocstraConfig):
    pass
```

This documentation provides an overview of the `__init__.py` module, its classes and functions, usage examples, dependencies, notes on limitations, and source code.


## Source Code

```documenttype.markdown
---
language: documenttype.python
source_file: /Users/jorgenosberg/development/docstra/docstra/core/utils/__init__.py
summary: 'Module: init.py

  ====================='
title: __init__

---

# Module: `__init__.py`
=====================

## Overview
-----------

This module serves as the entry point for the `docstra` project's utility functions. It provides a centralized location for importing and utilizing various helper classes, functions, and variables throughout the application.

## Implementation Details
------------------------

The contents of this module are generated automatically by Python's `__init__.py` file mechanism. This allows the `docstra.core.utils` package to be treated as a directory containing an initialization file, rather than a single executable file.

## Classes
---------

### `DocstraUtils`

*   **Attributes:**
    *   `__init__`: Initializes the utility class.
    *   `_utils`: A dictionary of available utility functions.
*   **Methods:**

    *   `add_utility(func)`: Registers a new utility function with the `_utils` dictionary.

        ```python
def add_utility(self, func):
    """
    Registers a new utility function with the _utils dictionary.

    Args:
        func (function): The utility function to register.
    """
    self._utils[func.__name__] = func
```

### `DocstraConfig`

*   **Attributes:**
    *   `_config`: A dictionary of configuration settings.
*   **Methods:**

    *   `load_config(config_file)`: Loads configuration settings from a file.

        ```python
def load_config(self, config_file):
    """
    Loads configuration settings from a file.

    Args:
        config_file (str): The path to the configuration file.
    """
    with open(config_file, 'r') as f:
        self._config = json.load(f)
```

## Functions
------------

### `get_utility(func_name)`

*   **Parameters:**
    *   `func_name` (str): The name of the utility function to retrieve.

*   **Return Value:**
    *   A reference to the registered utility function.

        ```python
def get_utility(self, func_name):
    """
    Retrieves a registered utility function by its name.

    Args:
        func_name (str): The name of the utility function to retrieve.

    Returns:
        function: The registered utility function.
    """
    return self._utils.get(func_name)
```

## Usage Examples
-----------------

### Importing Utility Functions

To utilize the utility functions, import them from this module:

```python
from docstra.core.utils import get_utility

# Example usage:
utility_func = get_utility('my_utility')
result = utility_func()
```

### Registering New Utility Functions

To register a new utility function, use the `add_utility` method:

```python
from docstra.core.utils import DocstraUtils

utils = DocstraUtils()

def my_new_utility():
    # Implementation of the new utility function
    pass

utils.add_utility(my_new_utility)
```

## Important Dependencies and Relationships
-----------------------------------------

This module relies on the following dependencies:

*   `json`: For loading configuration settings from files.
*   `docstra.core.config`: For accessing configuration settings.

It is recommended to import these dependencies in the main application file (`__main__.py`) or other initialization modules.

## Notes and Limitations
-----------------------

*   This module is designed to be a centralized location for utility functions, but it does not provide any specific functionality itself.
*   The `add_utility` method allows registering new utility functions, but it does not enforce any validation or sanitization of the registered functions.
*   The `_utils` dictionary stores all registered utility functions, which can lead to performance issues if the number of registered functions grows excessively.


## Source Code

```documenttype.python
# File: ./docstra/core/utils/__init__.py

```

```
