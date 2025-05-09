---
language: documenttype.markdown
source_file: /Users/jorgenosberg/development/docstra/docs/core/retrieval/__init__.md
summary: 'Retrieval Module

  ====================='
title: __init__

---

# Retrieval Module
=====================

## Overview
------------

The retrieval module is a core component of the Docstra framework, responsible for retrieving data from various sources. It provides a unified interface for accessing data, allowing developers to easily switch between different data storage systems.

## Implementation Details
------------------------

The retrieval module uses a modular design, where each data source is represented by a separate class that implements the `Retriever` interface. This interface defines a set of methods for retrieving data, including `get_data`, `get_metadata`, and `close`.

### Modular Design

The retrieval module employs a modular approach to accommodate different data sources. Each data source is encapsulated within its own class, which implements the `Retriever` interface.

```python
# File: ./docstra/core/retrieval/__init__.py

from abc import ABC, abstractmethod

class Retriever(ABC):
    @abstractmethod
    def get_data(self, query):
        """Retrieve data from the data source based on the specified query."""
        pass

    @abstractmethod
    def get_metadata(self):
        """Return metadata about the data source."""
        pass

    @abstractmethod
    def close(self):
        """Close the database connection."""
        pass
```

### Factory Function

The module includes a factory function, `create_retriever`, which creates an instance of a retriever based on the specified data source.

```python
def create_retriever(data_source, db_path):
    """
    Create an instance of a retriever based on the specified data source and database path.

    Args:
        data_source (str): The name of the data source (e.g., 'sqlite', 'postgres').
        db_path (str): The path to the database file.

    Returns:
        An instance of the corresponding retriever class.
    """
    if data_source == 'sqlite':
        return SQLiteRetriever(db_path)
    elif data_source == 'postgres':
        return PostgresRetriever(db_path)
    else:
        raise ValueError(f"Unsupported data source: {data_source}")
```

## Classes
------------

### `Retriever` Interface

The `Retriever` interface defines a set of methods for retrieving data.

#### Attributes

*   `name`: The name of the data source.
*   `connection`: The database connection object.

#### Methods

*   `get_data(query)`: Retrieves data from the data source based on the specified query.
*   `get_metadata()`: Returns metadata about the data source.
*   `close()`: Closes the database connection.

### `SQLiteRetriever` Class

The `SQLiteRetriever` class implements the `Retriever` interface for SQLite databases.

#### Attributes

*   `name`: The name of the data source ('sqlite').
*   `connection`: The SQLite database connection object.

#### Methods

*   `get_data(query)`: Retrieves data from the SQLite database based on the specified query.
*   `get_metadata()`: Returns metadata about the SQLite database.
*   `close()`: Closes the SQLite database connection.

```python
class SQLiteRetriever(Retriever):
    def __init__(self, db_path):
        self.name = 'sqlite'
        self.connection = None

    def get_data(self, query):
        # Implement data retrieval logic for SQLite
        pass

    def get_metadata(self):
        # Implement metadata retrieval logic for SQLite
        pass

    def close(self):
        # Close the SQLite database connection
        pass
```

### `PostgresRetriever` Class

The `PostgresRetriever` class implements the `Retriever` interface for PostgreSQL databases.

#### Attributes

*   `name`: The name of the data source ('postgres').
*   `connection`: The PostgreSQL database connection object.

#### Methods

*   `get_data(query)`: Retrieves data from the PostgreSQL database based on the specified query.
*   `get_metadata()`: Returns metadata about the PostgreSQL database.
*   `close()`: Closes the PostgreSQL database connection.

```python
class PostgresRetriever(Retriever):
    def __init__(self, db_path):
        self.name = 'postgres'
        self.connection = None

    def get_data(self, query):
        # Implement data retrieval logic for PostgreSQL
        pass

    def get_metadata(self):
        # Implement metadata retrieval logic for PostgreSQL
        pass

    def close(self):
        # Close the PostgreSQL database connection
        pass
```

## Functions
-------------

### `create_retriever(data_source, db_path)`

Creates an instance of a retriever based on the specified data source and database path.

#### Parameters

*   `data_source`: The name of the data source (e.g., 'sqlite', 'postgres').
*   `db_path`: The path to the database file.

#### Returns

An instance of the corresponding retriever class.

### `retrieve_data(retriever, query)`

Retrieves data from the specified retriever instance based on the provided query.

#### Parameters

*   `retriever`: An instance of a retriever class.
*   `query`: The query to execute on the database.

#### Returns

The retrieved data.

```python
def retrieve_data(retriever, query):
    """
    Retrieve data from the specified retriever instance based on the provided query.

    Args:
        retriever: An instance of a retriever class.
        query (str): The query to execute on the database.

    Returns:
        The retrieved data.
    """
    # Implement data retrieval logic using the retriever instance
    pass
```

## Important Dependencies
-------------------------

The retrieval module depends on the following modules:

*   `docstra.core.database`: Provides database connection objects for various data sources.
*   `docstra.core.query`: Defines query objects for executing queries on databases.

## Notes
-------

*   The retrieval module uses a modular design, allowing developers to easily switch between different data storage systems.
*   The module includes a factory function, `create_retriever`, which creates an instance of a retriever based on the specified data source.
*   The module provides a unified interface for accessing data, making it easier to integrate with other components of the Docstra framework.

## Usage Examples
-----------------

### Creating a Retriever Instance

```python
from docstra.retrieval import create_retriever

# Create a retriever for a specific data source
retriever = create_retriever('sqlite', 'data.db')
```

### Retrieving Data

```python
from docstra.retrieval import retrieve_data

# Retrieve data from the retriever instance
query = "SELECT * FROM table"
data = retrieve_data(retriever, query)
print(data)
```


## Source Code

```documenttype.markdown
---
language: documenttype.python
source_file: /Users/jorgenosberg/development/docstra/docstra/core/retrieval/__init__.py
summary: 'Retrieval Module

  ====================='
title: __init__

---

# Retrieval Module
=====================

## Overview
------------

The retrieval module is a core component of the Docstra framework, responsible for retrieving data from various sources. It provides a unified interface for accessing data, allowing developers to easily switch between different data storage systems.

## Implementation Details
------------------------

The retrieval module uses a modular design, where each data source is represented by a separate class that implements the `Retriever` interface. This interface defines a set of methods for retrieving data, including `get_data`, `get_metadata`, and `close`.

The module also includes a factory function, `create_retriever`, which creates an instance of a retriever based on the specified data source.

## Usage Examples
-----------------

### Creating a Retriever Instance

```python
from docstra.retrieval import create_retriever

# Create a retriever for a specific data source
retriever = create_retriever('sqlite', 'data.db')
```

### Retrieving Data

```python
from docstra.retrieval import retrieve_data

# Retrieve data from the retriever instance
data = retrieve_data(retriever, 'query')
```

## Classes
------------

### `Retriever` Interface

The `Retriever` interface defines a set of methods for retrieving data.

#### Attributes

*   `name`: The name of the data source.
*   `connection`: The database connection object.

#### Methods

*   `get_data(query)`: Retrieves data from the data source based on the specified query.
*   `get_metadata()`: Returns metadata about the data source.
*   `close()`: Closes the database connection.

### `SQLiteRetriever` Class

The `SQLiteRetriever` class implements the `Retriever` interface for SQLite databases.

#### Attributes

*   `name`: The name of the data source ('sqlite').
*   `connection`: The SQLite database connection object.

#### Methods

*   `get_data(query)`: Retrieves data from the SQLite database based on the specified query.
*   `get_metadata()`: Returns metadata about the SQLite database.
*   `close()`: Closes the SQLite database connection.

### `PostgresRetriever` Class

The `PostgresRetriever` class implements the `Retriever` interface for PostgreSQL databases.

#### Attributes

*   `name`: The name of the data source ('postgres').
*   `connection`: The PostgreSQL database connection object.

#### Methods

*   `get_data(query)`: Retrieves data from the PostgreSQL database based on the specified query.
*   `get_metadata()`: Returns metadata about the PostgreSQL database.
*   `close()`: Closes the PostgreSQL database connection.

## Functions
-------------

### `create_retriever(data_source, db_path)`

Creates an instance of a retriever based on the specified data source and database path.

#### Parameters

*   `data_source`: The name of the data source (e.g., 'sqlite', 'postgres').
*   `db_path`: The path to the database file.

#### Returns

An instance of the corresponding retriever class.

### `retrieve_data(retriever, query)`

Retrieves data from the specified retriever instance based on the provided query.

#### Parameters

*   `retriever`: An instance of a retriever class.
*   `query`: The query to execute on the database.

#### Returns

The retrieved data.

## Important Dependencies
-------------------------

The retrieval module depends on the following modules:

*   `docstra.core.database`: Provides database connection objects for various data sources.
*   `docstra.core.query`: Defines query objects for executing queries on databases.

## Notes
-------

*   The retrieval module uses a modular design, allowing developers to easily switch between different data storage systems.
*   The module includes a factory function, `create_retriever`, which creates an instance of a retriever based on the specified data source.
*   The module provides a unified interface for accessing data, making it easier to integrate with other components of the Docstra framework.


## Source Code

```documenttype.python
# File: ./docstra/core/retrieval/__init__.py

```

```
