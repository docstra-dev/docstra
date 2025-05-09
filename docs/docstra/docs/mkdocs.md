---
language: documenttype.other
source_file: /Users/jorgenosberg/development/docstra/docs/mkdocs.yml
summary: 'MkDocs Configuration File

  ====================================='
title: mkdocs

---

# MkDocs Configuration File
=====================================

## Overview
------------

This configuration file defines the settings for a MkDocs project. It specifies the extra CSS and JavaScript files to include in the project, markdown extensions to use, navigation menu items, documentation directory, and theme settings.

## Extra CSS and JavaScript Files
-------------------------------

The following CSS and JavaScript files are included as extra assets:

```markdown
extra_css:
  - assets/css/custom.css
extra_javascript:
  - assets/js/custom.js
```

These files can be used to add custom styles or scripts to the project.

## Markdown Extensions
---------------------

The following markdown extensions are enabled:

```markdown
markdown_extensions:
  - pymdownx.highlight
  - pymdownx.superfences
  - pymdownx.inlinehilite
  - pymdownx.tabbed
  - pymdownx.critic
  - pymdownx.tasklist
  - admonition
  - toc
  - tables
```

These extensions provide additional features for formatting and rendering markdown content.

## Navigation Menu
------------------

The following navigation menu items are defined:

```markdown
nav:
  - Home: index.md
  - Development:
      - GENERATOR: development/docstra/GENERATOR.md
      - pyproject: development/docstra/pyproject.md
      - README: development/docstra/README.md
  - Docstra:
      - repo_map: docstra/.docstra/repo_map.md
      - docs_config: docstra/.docstra/docs_config.md
      - __init__: docstra/docstra/__init__.md
      - __init__: docstra/core/__init__.md
      - cli: docstra/core/cli.md
      - app: docstra/core/app.md
  - .Docstra:
      - class_index: .docstra/index/class_index.md
      - symbol_index: .docstra/index/symbol_index.md
      - import_index: .docstra/index/import_index.md
      - function_index: .docstra/index/function_index.md
      - file_index: .docstra/index/file_index.md
  - Core:
      - __init__: core/documentation/__init__.md
      - wizard: core/documentation/wizard.md
      - generator: core/documentation/generator.md
      - setup: core/documentation/setup.md
      - __init__: core/ingestion/__init__.md
      - embeddings: core/ingestion/embeddings.md
      - storage: core/ingestion/storage.md
      - local: core/llm/local.md
      - __init__: core/llm/__init__.md
      - openai: core/llm/openai.md
      - anthropic: core/llm/anthropic.md
      - prompt: core/llm/prompt.md
      - ollama: core/llm/ollama.md
      - __init__: core/config/__init__.md
      - wizard: core/config/wizard.md
      - settings: core/config/settings.md
      - __init__: core/utils/__init__.md
      - file_collector: core/utils/file_collector.md
      - chunking: core/document_processing/chunking.md
      - __init__: core/document_processing/__init__.md
      - extractor: core/document_processing/extractor.md
      - parser: core/document_processing/parser.md
      - document: core/document_processing/document.md
      - hybrid: core/retrieval/hybrid.md
      - __init__: core/retrieval/__init__.md
      - chroma: core/retrieval/chroma.md
      - code_index: core/indexing/code_index.md
      - repo_map: core/indexing/repo_map.md
      - __init__: core/indexing/__init__.md
```

This navigation menu provides access to various documentation sections, including development, Docstra, and Core.

## Theme Settings
-----------------

The following theme settings are defined:

```markdown
theme:
  features:
    - navigation.instant
    - navigation.tracking
    - navigation.expand
    - navigation.indexes
    - search.highlight
    - search.share
    - toc.follow
    - content.code.copy
  icon:
    repo: fontawesome/brands/github
  name: material
  palette:
    accent: indigo
    primary: indigo
```

These theme settings customize the appearance of the documentation site, including navigation and search features.

## Important Dependencies
-------------------------

This configuration file depends on the following modules:

* MkDocs
* Material theme
* Pymdownx markdown extensions

These dependencies are required to render the documentation site correctly.


## Source Code

```documenttype.other
extra_css:
  - assets/css/custom.css
extra_javascript:
  - assets/js/custom.js
markdown_extensions:
  - pymdownx.highlight
  - pymdownx.superfences
  - pymdownx.inlinehilite
  - pymdownx.tabbed
  - pymdownx.critic
  - pymdownx.tasklist
  - admonition
  - toc
  - tables
docs_dir: .
nav:
  - Home: index.md
  - Development:
      - GENERATOR: development/docstra/GENERATOR.md
      - pyproject: development/docstra/pyproject.md
      - README: development/docstra/README.md
  - Docstra:
      - repo_map: docstra/.docstra/repo_map.md
      - docs_config: docstra/.docstra/docs_config.md
      - __init__: docstra/docstra/__init__.md
      - __init__: docstra/core/__init__.md
      - cli: docstra/core/cli.md
      - app: docstra/core/app.md
  - .Docstra:
      - class_index: .docstra/index/class_index.md
      - symbol_index: .docstra/index/symbol_index.md
      - import_index: .docstra/index/import_index.md
      - function_index: .docstra/index/function_index.md
      - file_index: .docstra/index/file_index.md
  - Core:
      - __init__: core/documentation/__init__.md
      - wizard: core/documentation/wizard.md
      - generator: core/documentation/generator.md
      - setup: core/documentation/setup.md
      - __init__: core/ingestion/__init__.md
      - embeddings: core/ingestion/embeddings.md
      - storage: core/ingestion/storage.md
      - local: core/llm/local.md
      - __init__: core/llm/__init__.md
      - openai: core/llm/openai.md
      - anthropic: core/llm/anthropic.md
      - prompt: core/llm/prompt.md
      - ollama: core/llm/ollama.md
      - __init__: core/config/__init__.md
      - wizard: core/config/wizard.md
      - settings: core/config/settings.md
      - __init__: core/utils/__init__.md
      - file_collector: core/utils/file_collector.md
      - chunking: core/document_processing/chunking.md
      - __init__: core/document_processing/__init__.md
      - extractor: core/document_processing/extractor.md
      - parser: core/document_processing/parser.md
      - document: core/document_processing/document.md
      - hybrid: core/retrieval/hybrid.md
      - __init__: core/retrieval/__init__.md
      - chroma: core/retrieval/chroma.md
      - code_index: core/indexing/code_index.md
      - repo_map: core/indexing/repo_map.md
      - __init__: core/indexing/__init__.md
plugins:
  - search
  - mkdocstrings
site_name: Project Documentation
theme:
  features:
    - navigation.instant
    - navigation.tracking
    - navigation.expand
    - navigation.indexes
    - search.highlight
    - search.share
    - toc.follow
    - content.code.copy
  icon:
    repo: fontawesome/brands/github
  name: material
  palette:
    accent: indigo
    primary: indigo

```
