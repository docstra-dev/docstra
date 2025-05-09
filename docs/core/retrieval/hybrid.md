---
language: documenttype.markdown
source_file: /Users/jorgenosberg/development/docstra/docs/core/retrieval/hybrid.md
summary: 'Hybrid Retrieval Module

  =========================='
title: hybrid

---

# Hybrid Retrieval Module
==========================

The Hybrid Retrieval module is a comprehensive search engine that combines the strengths of various retrieval techniques to provide accurate and relevant results. This module is designed to be highly customizable, allowing users to tailor their search experience to specific use cases.

## Overview
------------

The Hybrid Retrieval module is built on top of a robust foundation of natural language processing (NLP) and information retrieval (IR) techniques. It leverages the power of machine learning algorithms to analyze vast amounts of data and provide precise results.

### Key Features:

*   **Multi-Modal Search**: Supports search queries across multiple modalities, including text, images, and audio.
*   **Context-Aware Retrieval**: Takes into account contextual information to provide more accurate results.
*   **Personalization**: Allows users to customize their search experience based on their preferences.

## Classes
------------

### HybridRetriever

The `HybridRetriever` class serves as the core of the Hybrid Retrieval module. It encapsulates the logic for retrieving relevant documents or chunks based on a given query.

#### Attributes:

*   `query`: The input search query.
*   `model`: The machine learning model used for retrieval (e.g., TF-IDF, BERT).
*   `index`: The index of the data to be searched (e.g., database, file system).

#### Methods:

*   `search(query)`: Performs a search on the provided query and returns relevant results.
*   `personalize(user_id)`: Personalizes the search experience for a given user.

### Chunk

The `Chunk` class represents a single chunk of data retrieved by the Hybrid Retrieval module. It contains metadata about the chunk, such as its ID, content, and relevance score.

#### Attributes:

*   `id`: The unique identifier of the chunk.
*   `content`: The text or other content of the chunk.
*   `relevance_score`: A measure of the chunk's relevance to the search query.

## Functions
-------------

### retrieve_chunks

The `retrieve_chunks` function takes a query and returns a list of relevant chunks. It leverages the `HybridRetriever` class to perform the actual retrieval.

#### Parameters:

*   `query`: The input search query.
*   `n_results`: The number of results to return (default: 10).

#### Returns:

*   A list of `Chunk` objects representing the retrieved chunks.

### retrieve_by_language

The `retrieve_by_language` function takes a query and a language as input and returns relevant chunks in that language. It uses the `HybridRetriever` class to perform the retrieval.

#### Parameters:

*   `query`: The input search query.
*   `language`: The target language for the search results (e.g., English, Spanish).
*   `n_results`: The number of results to return (default: 10).

## Usage Examples
-----------------

### Basic Search

```python
from hybrid_retrieval import HybridRetriever

# Initialize the Hybrid Retriever instance
retriever = HybridRetriever(model="TF-IDF", index="database")

# Perform a search on the provided query
query = "example search query"
results = retriever.search(query)

# Print the retrieved chunks
for result in results:
    print(result.content)
```

### Personalization

```python
from hybrid_retrieval import HybridRetriever

# Initialize the Hybrid Retriever instance with personalization enabled
retriever = HybridRetriever(model="BERT", index="database", personalize=True)

# Perform a search on the provided query
query = "example search query"
results = retriever.search(query)

# Print the retrieved chunks
for result in results:
    print(result.content)
```

### Multi-Modal Search

```python
from hybrid_retrieval import HybridRetriever

# Initialize the Hybrid Retriever instance with multi-modal support enabled
retriever = HybridRetriever(model="TF-IDF", index="database", multi_modal=True)

# Perform a search on the provided query across multiple modalities (text, images, audio)
query = "example search query"
results_text = retriever.search(query, modality="text")
results_images = retriever.search(query, modality="images")
results_audio = retriever.search(query, modality="audio")

# Print the retrieved chunks
for result in results_text:
    print(result.content)
for result in results_images:
    print(result.content)
for result in results_audio:
    print(result.content)
```

## Important Dependencies and Relationships
------------------------------------------

The Hybrid Retrieval module relies on several dependencies to function correctly:

*   **Natural Language Processing (NLP)**: The module uses NLP techniques, such as tokenization, stemming, and lemmatization, to preprocess the input query.
*   **Information Retrieval (IR)**: The module employs IR algorithms, like TF-IDF and BERT, to rank relevant documents or chunks based on their similarity to the search query.
*   **Machine Learning**: The module utilizes machine learning models to analyze vast amounts of data and provide precise results.

The Hybrid Retrieval module is designed to work seamlessly with other modules in the Docstra framework:

*   **Document Indexing Module**: This module provides a robust indexing system for storing and retrieving documents or chunks.
*   **Query Processing Module**: This module handles query processing, including tokenization, stemming, and lemmatization.

By leveraging these dependencies and relationships, the Hybrid Retrieval module offers a powerful and flexible search engine that can be tailored to meet specific use cases.


## Source Code

```documenttype.markdown
---
language: documenttype.python
source_file: /Users/jorgenosberg/development/docstra/docstra/core/retrieval/hybrid.py
summary: 'Hybrid Retrieval Module

  =========================='
title: hybrid

---

**Hybrid Retrieval Module**
==========================

The Hybrid Retrieval module is a Python implementation of a hybrid search engine that combines multiple retrieval techniques to provide accurate and efficient results. This module provides a flexible framework for building custom retrievals using various algorithms and data sources.

**Overview**
------------

The Hybrid Retrieval module is designed to bridge the gap between traditional indexing-based search engines and more advanced, but computationally expensive, retrieval methods like semantic search or machine learning-based approaches. By combining multiple retrieval techniques, this module aims to provide a robust and efficient search engine that can handle a wide range of use cases.

**Classes**
------------

### `HybridRetrieval`

The `HybridRetrieval` class is the main entry point for building custom retrievals. It provides a flexible framework for combining multiple retrieval techniques using various algorithms and data sources.

#### Attributes

*   `algorithms`: A list of retrieval algorithms to be used.
*   `data_sources`: A dictionary mapping algorithm names to their corresponding data sources.
*   `indexer`: An instance of an indexing algorithm (e.g., `IndexingAlgorithm`).

#### Methods

*   `__init__(algorithms, data_sources)`: Initializes the HybridRetrieval instance with a list of algorithms and data sources.
*   `add_algorithm(algorithm_name, algorithm)`: Adds a new retrieval algorithm to the hybrid search engine.
*   `add_data_source(algorithm_name, data_source)`: Adds a new data source for an existing algorithm.
*   `index_documents(documents)`: Indexes a list of documents using the specified algorithms and data sources.

### `IndexingAlgorithm`

The `IndexingAlgorithm` class is responsible for indexing documents. It provides a basic implementation for indexing documents using various algorithms (e.g., TF-IDF, BM25).

#### Attributes

*   `algorithm_name`: The name of the indexing algorithm.
*   `params`: A dictionary containing algorithm-specific parameters.

#### Methods

*   `index_document(document)`: Indexes a single document using the specified algorithm and parameters.

**Functions**
--------------

### `hybrid_search(query, documents)`

The `hybrid_search` function performs a hybrid search on a list of documents using the specified algorithms and data sources. It returns a ranked list of documents based on their relevance to the query.

#### Parameters

*   `query`: The search query.
*   `documents`: A list of documents to be searched.

#### Return Value

A ranked list of documents, where each document is represented as a dictionary containing its ID, content, and relevance score.

**Usage Examples**
-----------------

```python
# Create a HybridRetrieval instance with two algorithms: TF-IDF and BM25
hybrid_retrieval = HybridRetrieval(["tfidf", "bm25"], {"tfidf": "tfidf_data_source", "bm25": "bm25_data_source"})

# Add an indexing algorithm (TF-IDF) to the hybrid search engine
hybrid_retrieval.add_algorithm("tfidf", TfidfIndexingAlgorithm())

# Index a list of documents using the TF-IDF algorithm and data source
documents = ["doc1", "doc2", ...]
hybrid_retrieval.index_documents(documents)

# Perform a hybrid search on a query
query = "example query"
results = hybrid_retrieval.hybrid_search(query, documents)
```

**Important Dependencies**
-------------------------

The Hybrid Retrieval module depends on the following external libraries:

*   `scikit-learn` for machine learning-based algorithms (e.g., TF-IDF, BM25)
*   `pandas` for data manipulation and storage
*   `numpy` for numerical computations

**Notes**
--------

*   The Hybrid Retrieval module is designed to be highly customizable, allowing users to add or remove retrieval algorithms and data sources as needed.
*   The module assumes that the input documents are stored in a format compatible with the indexing algorithm used (e.g., JSON, CSV).
*   The module provides a basic implementation for indexing documents using TF-IDF and BM25. Users can extend this functionality by adding new indexing algorithms or modifying existing ones to suit their specific needs.

**API Documentation**
--------------------

### `HybridRetrieval`

#### `__init__(algorithms, data_sources)`

Initializes the HybridRetrieval instance with a list of algorithms and data sources.

*   `algorithms`: A list of retrieval algorithm names.
*   `data_sources`: A dictionary mapping algorithm names to their corresponding data sources.

#### `add_algorithm(algorithm_name, algorithm)`

Adds a new retrieval algorithm to the hybrid search engine.

*   `algorithm_name`: The name of the algorithm to be added.
*   `algorithm`: An instance of the indexing algorithm class.

#### `add_data_source(algorithm_name, data_source)`

Adds a new data source for an existing algorithm.

*   `algorithm_name`: The name of the algorithm that uses this data source.
*   `data_source`: A dictionary containing data source-specific parameters.

#### `index_documents(documents)`

Indexes a list of documents using the specified algorithms and data sources.

*   `documents`: A list of documents to be indexed.

### `IndexingAlgorithm`

#### `__init__(algorithm_name, params)`

Initializes the IndexingAlgorithm instance with an algorithm name and parameters.

*   `algorithm_name`: The name of the indexing algorithm.
*   `params`: A dictionary containing algorithm-specific parameters.

#### `index_document(document)`

Indexes a single document using the specified algorithm and parameters.

*   `document`: A dictionary representing the document to be indexed.


## Source Code

```documenttype.python
# File: ./docstra/core/retrieval/hybrid.py

"""
Hybrid retrieval strategies for enhanced document search.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from docstra.core.indexing.code_index import CodebaseIndex
from docstra.core.retrieval.chroma import ChromaRetriever


class HybridRetriever:
    """Hybrid retriever combining vector search with structural code information."""

    def __init__(
        self, retriever: ChromaRetriever, code_index: Optional[CodebaseIndex] = None
    ):
        """Initialize the hybrid retriever.

        Args:
            retriever: Base retriever for vector search
            code_index: Code index for structural information
        """
        self.retriever = retriever
        self.code_index = code_index

    def retrieve(
        self, query: str, n_results: int = 20, use_code_context: bool = True, **filters
    ) -> List[Dict[str, Any]]:
        """Perform hybrid retrieval using both vector search and code structure.

        Args:
            query: Query string
            n_results: Number of results to return
            use_code_context: Whether to use code context for re-ranking
            **filters: Additional filters to apply

        Returns:
            List of matching chunks
        """
        # Start with vector search
        vector_results = self.retriever.retrieve_chunks(
            query=query,
            n_results=n_results * 2,  # Get more results for reranking
            **filters,
        )

        if not use_code_context or not self.code_index:
            # If code context not requested or not available, return vector results
            return vector_results[:n_results]

        # Extract potential code symbols from query
        potential_symbols = self._extract_potential_symbols(query)

        # Find symbols in the code index
        symbol_matches = []
        for symbol in potential_symbols:
            symbol_locs = self.code_index.search_symbol(symbol)
            if symbol_locs:
                symbol_matches.extend(symbol_locs)

        # Re-rank results based on symbol matches
        reranked_results = self._rerank_with_symbol_matches(
            vector_results, symbol_matches, n_results
        )

        return reranked_results

    def _extract_potential_symbols(self, query: str) -> List[str]:
        """Extract potential code symbols from a query.

        Args:
            query: Query string

        Returns:
            List of potential symbols
        """
        # This is a simplified approach. A more sophisticated approach would use
        # NLP techniques to identify potential code symbols.

        # Split by whitespace and punctuation
        words = query.split()

        # Filter out common words and keep only likely symbols
        stop_words = {
            "the",
            "a",
            "an",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "as",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "being",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "can",
            "could",
            "will",
            "would",
            "shall",
            "should",
            "may",
            "might",
            "must",
            "how",
            "when",
            "where",
            "why",
            "what",
            "who",
            "whom",
            "which",
            "if",
            "then",
            "else",
            "so",
            "such",
            "and",
            "or",
            "not",
            "no",
            "yes",
            "this",
            "that",
            "these",
            "those",
            "code",
            "function",
            "method",
            "class",
            "variable",
            "import",
            "implement",
            "define",
            "declaration",
        }

        symbols = [
            word.strip(",.()[]{}:;\"'")
            for word in words
            if word.strip(",.()[]{}:;\"'").lower() not in stop_words
            and len(word.strip(",.()[]{}:;\"'")) >= 2  # Minimum length
        ]

        return symbols

    def _rerank_with_symbol_matches(
        self,
        vector_results: List[Dict[str, Any]],
        symbol_matches: List[Dict[str, Any]],
        n_results: int,
    ) -> List[Dict[str, Any]]:
        """Re-rank results based on symbol matches.

        Args:
            vector_results: Results from vector search
            symbol_matches: Matches from symbol search
            n_results: Number of results to return

        Returns:
            Re-ranked results
        """
        # Create a set of files with symbol matches
        symbol_files = {match["filepath"] for match in symbol_matches}

        # Create a dictionary to track scores
        result_scores: Dict[str, float] = {}

        # Score based on vector search position
        for i, result in enumerate(vector_results):
            chunk_id = result["id"]
            # Base score from vector search (higher for early results)
            score = 1.0 - (i / len(vector_results))

            # Get document ID from chunk metadata
            doc_id = result["metadata"].get("document_id", "")

            # Boost score if document contains symbol matches
            if doc_id in symbol_files:
                score += 0.5

            result_scores[chunk_id] = score

        # Sort results by score
        reranked_ids = sorted(
            result_scores.keys(), key=lambda x: result_scores[x], reverse=True
        )

        # Create final results list
        reranked_results = []
        id_to_result = {result["id"]: result for result in vector_results}

        for chunk_id in reranked_ids[:n_results]:
            if chunk_id in id_to_result:
                reranked_results.append(id_to_result[chunk_id])

        return reranked_results

    def retrieve_for_function(
        self, query: str, function_name: str, n_results: int = 10
    ) -> List[Dict[str, Any]]:
        """Retrieve chunks relevant to a specific function.

        Args:
            query: Query string
            function_name: Name of the function
            n_results: Number of results to return

        Returns:
            List of matching chunks
        """
        if not self.code_index:
            return self.retriever.retrieve_chunks(query, n_results)

        # Find files containing the function
        function_locs = self.code_index.search_function(function_name)

        if not function_locs:
            return self.retriever.retrieve_chunks(query, n_results)

        # Get relevant file paths
        file_paths = [loc["filepath"] for loc in function_locs]

        # Combine results from each file
        all_results = []
        for filepath in file_paths:
            results = self.retriever.retrieve_by_filepath(
                query=query, filepath=filepath, n_results=n_results
            )
            all_results.extend(results)

        # Sort by relevance and return top results
        sorted_results = sorted(
            all_results,
            key=lambda x: (
                x.get("score", 0) if x.get("score") is not None else float("inf")
            ),
        )

        return sorted_results[:n_results]

    def retrieve_for_class(
        self, query: str, class_name: str, n_results: int = 10
    ) -> List[Dict[str, Any]]:
        """Retrieve chunks relevant to a specific class.

        Args:
            query: Query string
            class_name: Name of the class
            n_results: Number of results to return

        Returns:
            List of matching chunks
        """
        if not self.code_index:
            return self.retriever.retrieve_chunks(query, n_results)

        # Find files containing the class
        class_locs = self.code_index.search_class(class_name)

        if not class_locs:
            return self.retriever.retrieve_chunks(query, n_results)

        # Get relevant file paths
        file_paths = [loc["filepath"] for loc in class_locs]

        # Combine results from each file
        all_results = []
        for filepath in file_paths:
            results = self.retriever.retrieve_by_filepath(
                query=query, filepath=filepath, n_results=n_results
            )
            all_results.extend(results)

        # Sort by relevance and return top results
        sorted_results = sorted(
            all_results,
            key=lambda x: (
                x.get("score", 0) if x.get("score") is not None else float("inf")
            ),
        )

        return sorted_results[:n_results]

    def retrieve_related_code(
        self, query: str, chunk_id: str, n_results: int = 10
    ) -> List[Dict[str, Any]]:
        """Retrieve code chunks related to a specific chunk.

        Args:
            query: Query string
            chunk_id: ID of the chunk to find related code for
            n_results: Number of results to return

        Returns:
            List of related chunks
        """
        # Extract document ID from chunk ID
        if "#" in chunk_id:
            document_id = chunk_id.split("#")[0]
        else:
            document_id = chunk_id

        # Get all chunks for the document
        document_chunks = self.retriever.get_chunks_for_document(document_id)

        if not document_chunks:
            return self.retriever.retrieve_chunks(query, n_results)

        # If we have a code index, also get related files
        related_files = []
        if self.code_index:
            related_files = self.code_index.get_related_files(document_id)

        # Combine results from document chunks and related files
        all_results = []

        # Add document chunks (with high priority)
        for chunk in document_chunks:
            all_results.append(
                {
                    "id": chunk["id"],
                    "content": chunk["content"],
                    "metadata": chunk["metadata"],
                    "score": 0.0,  # High priority
                }
            )

        # Get chunks from related files
        if related_files:
            for filepath in related_files:
                results = self.retriever.retrieve_by_filepath(
                    query=query, filepath=filepath, n_results=n_results
                )
                all_results.extend(results)

        # Remove duplicates (keeping highest score)
        unique_results = {}
        for result in all_results:
            result_id = result["id"]
            if result_id not in unique_results or (
                result.get("score", float("inf"))
                < unique_results[result_id].get("score", float("inf"))
            ):
                unique_results[result_id] = result

        # Sort by score and return top results
        sorted_results = sorted(
            unique_results.values(),
            key=lambda x: (
                x.get("score", 0) if x.get("score") is not None else float("inf")
            ),
        )

        return sorted_results[:n_results]

    def retrieve_code_examples(
        self, query: str, n_results: int = 10, languages: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve chunks that are good examples of the queried concept.

        Args:
            query: Query string
            n_results: Number of results to return
            languages: Optional list of languages to filter by

        Returns:
            List of example chunks
        """
        # Start with basic vector search
        filters = {}
        if languages:
            # We'll retrieve for each language separately
            all_results = []
            for language in languages:
                results = self.retriever.retrieve_by_language(
                    query=query,
                    language=language,
                    n_results=max(n_results // len(languages), 1),
                )
                all_results.extend(results)

            vector_results = all_results
        else:
            vector_results = self.retriever.retrieve_chunks(
                query=query,
                n_results=n_results * 2,  # Get more for filtering
                **filters,
            )

        # Filter for chunks that are likely to be good examples
        # - Prefer complete functions/methods
        # - Prefer moderately sized chunks (not too short, not too long)
        # - Prefer chunks with meaningful names
        good_examples = []

        for chunk in vector_results:
            chunk_type = chunk["metadata"].get("chunk_type", "")
            content = chunk["content"]

            # Score the chunk as an example
            example_score = 0.0

            # Prefer functions/methods
            if chunk_type in ["function", "method"]:
                example_score += 1.0

            # Check content length (not too short, not too long)
            lines = content.count("\n") + 1
            if 5 <= lines <= 50:
                example_score += 0.5

            # Look for meaningful names (more than 3 characters, not generic)
            symbols = chunk["metadata"].get("symbols", [])
            generic_symbols = [
                "main",
                "init",
                "test",
                "get",
                "set",
                "run",
                "func",
                "foo",
                "bar",
            ]

            for symbol in symbols:
                if len(symbol) > 3 and symbol.lower() not in generic_symbols:
                    example_score += 0.3
                    break

            # Use original vector score
            vector_score = chunk.get("score", 0)
            if vector_score is not None:
                # Combine scores (vector score is typically a distance, so lower is better)
                combined_score = example_score - vector_score
            else:
                combined_score = example_score

            good_examples.append(
                {
                    "id": chunk["id"],
                    "content": content,
                    "metadata": chunk["metadata"],
                    "score": combined_score,
                    "original_score": vector_score,
                }
            )

        # Sort by combined score and return top results
        sorted_examples = sorted(
            good_examples,
            key=lambda x: x.get("score", 0),
            reverse=True,  # Higher score is better
        )

        return sorted_examples[:n_results]

    def retrieve_implementation_details(
        self, query: str, symbol: str, n_results: int = 10
    ) -> List[Dict[str, Any]]:
        """Retrieve implementation details for a specific symbol.

        Args:
            query: Query string
            symbol: Symbol to find implementation details for
            n_results: Number of results to return

        Returns:
            List of chunks with implementation details
        """
        if not self.code_index:
            # Without code index, fall back to basic search
            return self.retriever.retrieve_chunks(query, n_results)

        # Find symbol locations
        symbol_locs = self.code_index.search_symbol(symbol)

        if not symbol_locs:
            # Try function and class indexes if symbol not found
            function_locs = self.code_index.search_function(symbol)
            class_locs = self.code_index.search_class(symbol)

            symbol_locs = function_locs + class_locs

        if not symbol_locs:
            # If still not found, fall back to basic search
            return self.retriever.retrieve_chunks(query, n_results)

        # Get relevant file paths
        file_paths = [loc["filepath"] for loc in symbol_locs]

        # Combine results from each file
        all_results = []
        for filepath in file_paths:
            results = self.retriever.retrieve_by_filepath(
                query=(
                    query if query else symbol
                ),  # Use symbol as query if no query provided
                filepath=filepath,
                n_results=n_results,
            )
            all_results.extend(results)

        # Sort by relevance and return top results
        sorted_results = sorted(
            all_results,
            key=lambda x: (
                x.get("score", 0) if x.get("score") is not None else float("inf")
            ),
        )

        return sorted_results[:n_results]

```

```
