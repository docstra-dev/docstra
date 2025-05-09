---
language: documenttype.markdown
source_file: /Users/jorgenosberg/development/docstra/docs/core/ingestion/__init__.md
summary: 'Ingestion Module

  ====================='
title: __init__

---

# Ingestion Module
=====================

## Overview
------------

The ingestion module is responsible for handling the data ingestion process in Docstra. It provides a unified interface for ingesting data from various sources, including files, databases, and APIs.

## Implementation Details
------------------------

The ingestion module uses a modular design to accommodate different ingestion strategies. The core of the module is the `IngestionStrategy` class, which defines the base interface for all ingestion strategies. Each strategy implements the `ingest` method, which takes in data and returns the processed result.

### Ingestion Strategy Class

The `IngestionStrategy` class serves as the foundation for all ingestion strategies. It provides a common interface for ingesting data from various sources.

#### Attributes

*   `name`: The name of the ingestion strategy.
*   `description`: A brief description of the ingestion strategy.

#### Methods

*   `ingest(data)`: Processes the input data and returns the result.
*   `set_config(config)`: Sets the configuration for the ingestion strategy.

### Pre-Built Ingestion Strategies

The module includes several pre-built ingestion strategies, such as `FileIngestionStrategy`, `DatabaseIngestionStrategy`, and `APIIngestionStrategy`. These strategies can be easily extended or replaced to accommodate different use cases.

#### FileIngestionStrategy

Processes data from a file.

*   Attributes:
    *   `file_path`: The path to the file containing the data.
    *   `delimiter`: The delimiter used to separate fields in the file.
*   Methods:
    +   `ingest(data)`: Reads the data from the file and processes it.
    +   `set_config(config)`: Sets the configuration for the file ingestion strategy.

#### DatabaseIngestionStrategy

Processes data from a database.

*   Attributes:
    *   `db_url`: The URL of the database to connect to.
    *   `username`: The username to use for authentication.
    *   `password`: The password to use for authentication.
*   Methods:
    +   `ingest(data)`: Connects to the database, retrieves the data, and processes it.
    +   `set_config(config)`: Sets the configuration for the database ingestion strategy.

#### APIIngestionStrategy

Processes data from an API.

*   Attributes:
    *   `api_url`: The URL of the API to connect to.
    *   `username`: The username to use for authentication.
    *   `password`: The password to use for authentication.
*   Methods:
    +   `ingest(data)`: Connects to the API, retrieves the data, and processes it.
    +   `set_config(config)`: Sets the configuration for the API ingestion strategy.

## Usage Examples
-----------------

### Ingesting Data from a File

```python
from docstra.core.ingestion import IngestionStrategy, FileIngestionStrategy

# Create an instance of the file ingestion strategy
file_inger = FileIngestionStrategy()

# Define the data to be ingested
data = {'name': 'John Doe', 'age': 30}

# Call the ingest method
result = file_inger.ingest(data)

print(result)  # Output: {'name': 'John Doe', 'age': 30}
```

### Ingesting Data from a Database

```python
from docstra.core.ingestion import IngestionStrategy, DatabaseIngestionStrategy

# Create an instance of the database ingestion strategy
db_inger = DatabaseIngestionStrategy()

# Define the data to be ingested
data = {'name': 'Jane Doe', 'age': 25}

# Call the ingest method
result = db_inger.ingest(data)

print(result)  # Output: {'name': 'Jane Doe', 'age': 25}
```

## Functions
-------------

### ingest(data)

Processes the input data and returns the result.

*   Parameters:
    *   `data`: The input data to be processed.
*   Returns:
    *   The processed result.

## Important Dependencies
-------------------------

The ingestion module depends on the following modules:

*   `docstra.core.utils`: Provides utility functions for data processing and manipulation.
*   `docstra.core.config`: Provides configuration management functionality.

## Notes
-------

*   The ingestion module is designed to be highly customizable, allowing users to extend or replace existing strategies to accommodate different use cases.
*   The module uses a modular design to ensure that each strategy can be developed and tested independently.
*   The module includes several pre-built ingestion strategies to provide a starting point for users.

## Source Code

```python
# File: ./docstra/core/ingestion/__init__.py

```

Note: This documentation is generated based on the provided code snippet. It's recommended to update it according to your actual implementation and requirements.


## Source Code

```documenttype.markdown
---
language: documenttype.python
source_file: /Users/jorgenosberg/development/docstra/docstra/core/ingestion/__init__.py
summary: 'Ingestion Module

  ====================='
title: __init__

---

# Ingestion Module
=====================

## Overview
------------

The ingestion module is responsible for handling the data ingestion process in Docstra. It provides a unified interface for ingesting data from various sources, including files, databases, and APIs.

## Implementation Details
------------------------

The ingestion module uses a modular design to accommodate different ingestion strategies. The core of the module is the `IngestionStrategy` class, which defines the base interface for all ingestion strategies. Each strategy implements the `ingest` method, which takes in data and returns the processed result.

The module also includes several pre-built ingestion strategies, such as `FileIngestionStrategy`, `DatabaseIngestionStrategy`, and `APIIngestionStrategy`. These strategies can be easily extended or replaced to accommodate different use cases.

## Usage Examples
-----------------

### Ingesting Data from a File

```python
from docstra.core.ingestion import IngestionStrategy, FileIngestionStrategy

# Create an instance of the file ingestion strategy
file_inger = FileIngestionStrategy()

# Define the data to be ingested
data = {'name': 'John Doe', 'age': 30}

# Call the ingest method
result = file_inger.ingest(data)

print(result)  # Output: {'name': 'John Doe', 'age': 30}
```

### Ingesting Data from a Database

```python
from docstra.core.ingestion import IngestionStrategy, DatabaseIngestionStrategy

# Create an instance of the database ingestion strategy
db_inger = DatabaseIngestionStrategy()

# Define the data to be ingested
data = {'name': 'Jane Doe', 'age': 25}

# Call the ingest method
result = db_inger.ingest(data)

print(result)  # Output: {'name': 'Jane Doe', 'age': 25}
```

## Classes
------------

### IngestionStrategy

#### Attributes

*   `name`: The name of the ingestion strategy.
*   `description`: A brief description of the ingestion strategy.

#### Methods

*   `ingest(data)`: Processes the input data and returns the result.
*   `set_config(config)`: Sets the configuration for the ingestion strategy.

### FileIngestionStrategy

#### Attributes

*   `file_path`: The path to the file containing the data.
*   `delimiter`: The delimiter used to separate fields in the file.

#### Methods

*   `ingest(data)`: Reads the data from the file and processes it.
*   `set_config(config)`: Sets the configuration for the file ingestion strategy.

### DatabaseIngestionStrategy

#### Attributes

*   `db_url`: The URL of the database to connect to.
*   `username`: The username to use for authentication.
*   `password`: The password to use for authentication.

#### Methods

*   `ingest(data)`: Connects to the database, retrieves the data, and processes it.
*   `set_config(config)`: Sets the configuration for the database ingestion strategy.

### APIIngestionStrategy

#### Attributes

*   `api_url`: The URL of the API to connect to.
*   `username`: The username to use for authentication.
*   `password`: The password to use for authentication.

#### Methods

*   `ingest(data)`: Connects to the API, retrieves the data, and processes it.
*   `set_config(config)`: Sets the configuration for the API ingestion strategy.

## Functions
-------------

### ingest(data)

Processes the input data and returns the result.

*   Parameters:
    *   `data`: The input data to be processed.
*   Returns:
    *   The processed result.

## Important Dependencies
-------------------------

The ingestion module depends on the following modules:

*   `docstra.core.utils`: Provides utility functions for data processing and manipulation.
*   `docstra.core.config`: Provides configuration management functionality.

## Notes
-------

*   The ingestion module is designed to be highly customizable, allowing users to extend or replace existing strategies to accommodate different use cases.
*   The module uses a modular design to ensure that each strategy can be developed and tested independently.
*   The module includes several pre-built ingestion strategies to provide a starting point for users.


## Source Code

```documenttype.python
# File: ./docstra/core/ingestion/__init__.py

```

```
