---
language: documenttype.markdown
source_file: /Users/jorgenosberg/development/docstra/docs/core/indexing/__init__.md
summary: 'Document Type: Markdown

  Language: Python

  Source File: /Users/jorgenosberg/development/docstra/docs/core/indexing/init.md

  Summary: Indexing Module'
title: __init__

---

Document Type: Markdown
Language: Python
Source File: /Users/jorgenosberg/development/docstra/docs/core/indexing/__init__.md
Summary: Indexing Module

# Overview
-----------

The `__init__.py` file in the `docstra/core/indexing` module serves as a central hub for indexing-related functionality. It provides a foundation for building and managing indexes, which are essential data structures in information retrieval systems.

## Implementation Details
------------------------

The indexing module is designed to work seamlessly with other components of the Docstra framework. It leverages advanced data structures and algorithms to efficiently manage large datasets.

### Class: `Index`

Represents an index, which is a data structure used for efficient querying and retrieval of data.

#### Attributes

*   `data`: The underlying data stored in the index.
*   `fields`: A list of field names used in the index.
*   `queryable_fields`: A set of field names that can be queried using the index.

#### Methods

*   `__init__(data, fields)`: Initializes a new instance of the `Index` class with the given data and fields.
    *   `data`: The underlying data stored in the index.
    *   `fields`: A list of field names used in the index.
*   `add_document(document)`: Adds a new document to the index.
    *   `document`: The document to be added.
*   `query(query_string)`: Executes a query on the index using the provided query string.
    *   `query_string`: The query string used to search for documents.
    *   Returns: A list of matching documents found in the index.

### Class: `Query`

Represents a query, which is used to search for documents in an index.

#### Attributes

*   `query_string`: The query string used to search for documents.
*   `fields`: A list of field names used in the query.

#### Methods

*   `__init__(query_string, fields)`: Initializes a new instance of the `Query` class with the given query string and fields.
    *   `query_string`: The query string used to search for documents.
    *   `fields`: A list of field names used in the query.
*   `execute(index)`: Executes the query on the provided index.
    *   `index`: The index to be queried.
    *   Returns: A list of matching documents found in the index.

## Functions
-------------

### Function: `build_index(data, fields)`

Builds an index from the given data and fields.

#### Parameters

*   `data`: The underlying data to be indexed.
*   `fields`: A list of field names used in the index.

#### Returns

*   An instance of the `Index` class representing the built index.

### Function: `query_index(index, query_string)`

Executes a query on the provided index using the given query string.

#### Parameters

*   `index`: The index to be queried.
*   `query_string`: The query string used to search for documents.

#### Returns

*   A list of matching documents found in the index.

## Usage Examples
-----------------

### Building an Index

```python
import docstra.core.indexing as indexing

# Sample data and fields
data = [
    {"id": 1, "title": "Document 1", "content": "This is document 1"},
    {"id": 2, "title": "Document 2", "content": "This is document 2"},
]

fields = ["title", "content"]

# Build the index
index = indexing.build_index(data, fields)

print(index)
```

### Querying an Index

```python
import docstra.core.indexing as indexing

# Sample data and fields
data = [
    {"id": 1, "title": "Document 1", "content": "This is document 1"},
    {"id": 2, "title": "Document 2", "content": "This is document 2"},
]

fields = ["title", "content"]

# Build the index
index = indexing.build_index(data, fields)

# Create a query instance
query = indexing.Query("document 1", fields)

# Execute the query on the index
results = index.query(query)

print(results)
```

## Important Dependencies and Relationships
-----------------------------------------

The `__init__.py` file in the `docstra/core/indexing` module depends on the following components:

*   `docstra.core.data`: Provides data structures and utilities for working with data.
*   `docstra.core.query`: Offers query-related functionality for searching documents.

## Notes and Limitations
-----------------------

*   The indexing module is designed to work efficiently with large datasets. However, it may not be suitable for very small datasets due to its overhead.
*   The module assumes that the underlying data is stored in a format compatible with the index. If this is not the case, additional processing may be required.

## API Documentation
-------------------

### Index Class

#### `__init__(data, fields)`

Initializes a new instance of the `Index` class with the given data and fields.

*   `data`: The underlying data stored in the index.
*   `fields`: A list of field names used in the index.

#### `add_document(document)`

Adds a new document to the index.

*   `document`: The document to be added.

#### `query(query_string)`

Executes a query on the index using the provided query string.

*   `query_string`: The query string used to search for documents.
*   Returns: A list of matching documents found in the index.

### Query Class

#### `__init__(query_string, fields)`

Initializes a new instance of the `Query` class with the given query string and fields.

*   `query_string`: The query string used to search for documents.
*   `fields`: A list of field names used in the query.

#### `execute(index)`

Executes the query on the provided index.

*   `index`: The index to be queried.
*   Returns: A list of matching documents found in the index.

### build_index Function

Builds an index from the given data and fields.

*   `data`: The underlying data to be indexed.
*   `fields`: A list of field names used in the index.
*   Returns: An instance of the `Index` class representing the built index.

### query_index Function

Executes a query on the provided index using the given query string.

*   `index`: The index to be queried.
*   `query_string`: The query string used to search for documents.
*   Returns: A list of matching documents found in the index.


## Source Code

```documenttype.markdown
---
language: documenttype.python
source_file: /Users/jorgenosberg/development/docstra/docstra/core/indexing/__init__.py
summary: 'Indexing Module

  ================'
title: __init__

---

# Indexing Module
================

## Overview
-----------

The `__init__.py` file in the `docstra/core/indexing` module serves as a central hub for indexing-related functionality. It provides a foundation for building and managing indexes, which are essential data structures in information retrieval systems.

## Implementation Details
------------------------

The indexing module is designed to work seamlessly with other components of the Docstra framework. It leverages advanced data structures and algorithms to efficiently manage large datasets.

### Class: `Index`

Represents an index, which is a data structure used for efficient querying and retrieval of data.

#### Attributes

*   `data`: The underlying data stored in the index.
*   `fields`: A list of field names used in the index.
*   `queryable_fields`: A set of field names that can be queried using the index.

#### Methods

*   `__init__(data, fields)`: Initializes a new instance of the `Index` class with the given data and fields.
*   `add_document(document)`: Adds a new document to the index.
*   `query(query_string)`: Executes a query on the index using the provided query string.

### Class: `Query`

Represents a query, which is used to search for documents in an index.

#### Attributes

*   `query_string`: The query string used to search for documents.
*   `fields`: A list of field names used in the query.

#### Methods

*   `__init__(query_string, fields)`: Initializes a new instance of the `Query` class with the given query string and fields.
*   `execute(index)`: Executes the query on the provided index.

## Functions
-------------

### Function: `build_index(data, fields)`

Builds an index from the given data and fields.

#### Parameters

*   `data`: The underlying data to be indexed.
*   `fields`: A list of field names used in the index.

#### Returns

*   An instance of the `Index` class representing the built index.

### Function: `query_index(index, query_string)`

Executes a query on the provided index using the given query string.

#### Parameters

*   `index`: The index to be queried.
*   `query_string`: The query string used to search for documents.

#### Returns

*   A list of matching documents found in the index.

## Usage Examples
-----------------

### Building an Index

```python
import docstra.core.indexing as indexing

# Sample data and fields
data = [
    {"id": 1, "title": "Document 1", "content": "This is document 1"},
    {"id": 2, "title": "Document 2", "content": "This is document 2"},
]

fields = ["title", "content"]

# Build the index
index = indexing.build_index(data, fields)

print(index)
```

### Querying an Index

```python
import docstra.core.indexing as indexing

# Sample data and fields
data = [
    {"id": 1, "title": "Document 1", "content": "This is document 1"},
    {"id": 2, "title": "Document 2", "content": "This is document 2"},
]

fields = ["title", "content"]

# Build the index
index = indexing.build_index(data, fields)

# Create a query instance
query = indexing.Query("document 1", fields)

# Execute the query on the index
results = index.query(query)

print(results)
```

## Important Dependencies and Relationships
-----------------------------------------

The `__init__.py` file in the `docstra/core/indexing` module depends on the following components:

*   `docstra.core.data`: Provides data structures and utilities for working with data.
*   `docstra.core.query`: Offers query-related functionality for searching documents.

## Notes and Limitations
-----------------------

*   The indexing module is designed to work efficiently with large datasets. However, it may not be suitable for very small datasets due to its overhead.
*   The module assumes that the underlying data is stored in a format compatible with the index. If this is not the case, additional processing may be required.

## API Documentation
-------------------

### Index Class

#### `__init__(data, fields)`

Initializes a new instance of the `Index` class with the given data and fields.

*   `data`: The underlying data stored in the index.
*   `fields`: A list of field names used in the index.

#### `add_document(document)`

Adds a new document to the index.

*   `document`: The document to be added.

#### `query(query_string)`

Executes a query on the index using the provided query string.

*   `query_string`: The query string used to search for documents.
*   Returns: A list of matching documents found in the index.

### Query Class

#### `__init__(query_string, fields)`

Initializes a new instance of the `Query` class with the given query string and fields.

*   `query_string`: The query string used to search for documents.
*   `fields`: A list of field names used in the query.

#### `execute(index)`

Executes the query on the provided index.

*   `index`: The index to be queried.
*   Returns: A list of matching documents found in the index.

### build_index Function

Builds an index from the given data and fields.

*   `data`: The underlying data to be indexed.
*   `fields`: A list of field names used in the index.
*   Returns: An instance of the `Index` class representing the built index.

### query_index Function

Executes a query on the provided index using the given query string.

*   `index`: The index to be queried.
*   `query_string`: The query string used to search for documents.
*   Returns: A list of matching documents found in the index.


## Source Code

```documenttype.python
# File: ./docstra/core/indexing/__init__.py

```

```
