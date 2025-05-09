---
language: documenttype.markdown
source_file: /Users/jorgenosberg/development/docstra/docs/core/config/__init__.md
summary: 'Configuration Module

  ====================='
title: __init__

---

# Configuration Module
=====================

## Overview
-----------

The `__init__.py` file in the `docstra/core/config` directory serves as a configuration module for the Docstra application. It provides a centralized location for storing and managing configuration settings, which can be used throughout the application.

## Implementation Details
------------------------

This module is designed to be highly extensible and customizable. It uses a modular approach to load configuration settings from various sources, including environment variables, command-line arguments, and a default configuration file.

### Modular Approach

The `config` class serves as the main entry point for loading and managing configuration settings. It provides methods for setting, getting, and deleting configuration values, as well as checking if a value is set.

### Configuration Loading

Configuration settings are loaded from various sources, including:

*   Environment variables
*   Command-line arguments
*   A default configuration file (optional)

The `load_config` function loads the configuration settings from these sources and returns a dictionary containing all loaded settings.

## Usage Examples
-----------------

### Setting Configuration Values

```python
import docstra.core.config as config

# Set a configuration value using environment variables
config.set('DB_HOST', os.environ.get('DB_HOST'))

# Set a configuration value using command-line arguments
config.set('API_KEY', sys.argv[1])
```

### Getting Configuration Values

```python
import docstra.core.config as config

# Get the value of a configuration setting
db_host = config.get('DB_HOST')
```

## Classes
---------

### `config.Config`

#### Attributes

*   `settings`: A dictionary containing all loaded configuration settings.

#### Methods

| Method | Description |
| --- | --- |
| `set(key, value)` | Sets a new configuration value. |
| `get(key)` | Retrieves the value of a configuration setting. |
| `delete(key)` | Deletes a configuration setting. |
| `has(key)` | Checks if a configuration setting is set. |

## Functions
-------------

### `config.load_config()`

#### Parameters

| Parameter | Description |
| --- | --- |
| `config_file` | The path to the default configuration file (optional). |

#### Return Value

A dictionary containing all loaded configuration settings.

#### Purpose

Loads configuration settings from various sources, including environment variables, command-line arguments, and a default configuration file.

## Important Dependencies
-------------------------

This module depends on the following external libraries:

*   `os`: For interacting with environment variables.
*   `sys`: For accessing command-line arguments.
*   `docstra.core`: The main Docstra application package.

## Notes
------

*   This module uses a modular approach to load configuration settings, which allows for easy customization and extension.
*   Configuration values are stored in memory by default. If you need to persist configuration settings across application restarts, consider using a database or file-based storage solution.
*   Be cautious when using environment variables and command-line arguments to set configuration values, as they can be sensitive or insecure.

## API Documentation
-------------------

### `config.Config`

#### Methods

| Method | Description |
| --- | --- |
| `set(key, value)` | Sets a new configuration value. |
| `get(key)` | Retrieves the value of a configuration setting. |
| `delete(key)` | Deletes a configuration setting. |
| `has(key)` | Checks if a configuration setting is set. |

### `config.load_config()`

#### Parameters

| Parameter | Description |
| --- | --- |
| `config_file` | The path to the default configuration file (optional). |

#### Return Value

A dictionary containing all loaded configuration settings.

#### Purpose

Loads configuration settings from various sources, including environment variables, command-line arguments, and a default configuration file.


## Source Code

```documenttype.markdown
---
language: documenttype.python
source_file: /Users/jorgenosberg/development/docstra/docstra/core/config/__init__.py
summary: 'Configuration Module

  ====================='
title: __init__

---

# Configuration Module
=====================

## Overview
-----------

The `__init__.py` file in the `docstra/core/config` directory serves as a configuration module for the Docstra application. It provides a centralized location for storing and managing configuration settings, which can be used throughout the application.

## Implementation Details
------------------------

This module is designed to be highly extensible and customizable. It uses a modular approach to load configuration settings from various sources, including environment variables, command-line arguments, and a default configuration file.

The `config` class serves as the main entry point for loading and managing configuration settings. It provides methods for setting, getting, and deleting configuration values, as well as checking if a value is set.

## Usage Examples
-----------------

### Setting Configuration Values

```python
import docstra.core.config as config

# Set a configuration value using environment variables
config.set('DB_HOST', os.environ.get('DB_HOST'))

# Set a configuration value using command-line arguments
config.set('API_KEY', sys.argv[1])
```

### Getting Configuration Values

```python
import docstra.core.config as config

# Get the value of a configuration setting
db_host = config.get('DB_HOST')
```

## Classes
---------

### `config.Config`

#### Attributes

*   `settings`: A dictionary containing all loaded configuration settings.

#### Methods

*   `set(key, value)`: Sets a new configuration value.
*   `get(key)`: Retrieves the value of a configuration setting.
*   `delete(key)`: Deletes a configuration setting.
*   `has(key)`: Checks if a configuration setting is set.

## Functions
-------------

### `config.load_config()`

#### Parameters

*   `config_file`: The path to the default configuration file (optional).

#### Return Value

*   A dictionary containing all loaded configuration settings.

#### Purpose

Loads configuration settings from various sources, including environment variables, command-line arguments, and a default configuration file.

## Important Dependencies
-------------------------

This module depends on the following external libraries:

*   `os`: For interacting with environment variables.
*   `sys`: For accessing command-line arguments.
*   `docstra.core`: The main Docstra application package.

## Notes
------

*   This module uses a modular approach to load configuration settings, which allows for easy customization and extension.
*   Configuration values are stored in memory by default. If you need to persist configuration settings across application restarts, consider using a database or file-based storage solution.
*   Be cautious when using environment variables and command-line arguments to set configuration values, as they can be sensitive or insecure.

## API Documentation
-------------------

### `config.Config`

#### Methods

| Method | Description |
| --- | --- |
| `set(key, value)` | Sets a new configuration value. |
| `get(key)` | Retrieves the value of a configuration setting. |
| `delete(key)` | Deletes a configuration setting. |
| `has(key)` | Checks if a configuration setting is set. |

### `config.load_config()`

#### Parameters

| Parameter | Description |
| --- | --- |
| `config_file` | The path to the default configuration file (optional). |

#### Return Value

A dictionary containing all loaded configuration settings.

#### Purpose

Loads configuration settings from various sources, including environment variables, command-line arguments, and a default configuration file.


## Source Code

```documenttype.python
# File: ./docstra/core/config/__init__.py

```

```
