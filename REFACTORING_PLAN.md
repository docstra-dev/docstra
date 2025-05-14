# Docstra Refactoring Plan

## 1. Introduction & Goal

This document outlines the plan to refactor the `docstra` Python package core logic and CLI. The primary goals are:

- Align the CLI with a revised set of commands (`init`, `ingest`, `query`, `chat`, `generate`, `config`).
- Improve code modularity by introducing a service layer.
- Implement interactive chat functionality with session persistence (SQLite).
- Enhance documentation generation to support incremental updates.
- Define a clear, robust API suitable for external integrations (VSCode, IntelliJ extensions).

## 2. Initial Code Analysis Summary

- **`docstra/core/__init__.py`:** Contains a monolithic `docstraant` class initializing all components and exposing core methods. Needs decomposition.
- **`docstra/core/app.py`:** Implements a basic FastAPI app primarily for a web UI use case, calling the CLI via `subprocess`. Unsuitable for direct API integration.
- **`docstra/core/cli.py`:** Uses `typer`.
  - `init` command currently combines setup and indexing. Needs splitting.
  - Existing commands (`document`, `explain`, `ask`, `examples`, `analyze`) don't map directly to the new `query`/`chat` flow. `ask` is closest to `query`.
  - `generate` command exists but needs verification for incremental updates.
  - `config` command is broadly aligned.
  - No `chat` command exists.
  - Commands often re-initialize components inefficiently.

## 3. Key Refactoring Areas

1.  **CLI Structure:** Reorganize `typer` commands in `cli.py`.
2.  **Core Logic Separation:** Break down `docstraant` into focused service modules.
3.  **Chat Implementation:** Add `ChatService` using SQLite for session persistence and history.
4.  **API Layer:** Redesign `app.py` (or create `api.py`) with clean FastAPI endpoints using the service layer.
5.  **Configuration & Initialization:** Streamline component initialization (context or DI).
6.  **Incremental Generation:** Verify/enhance `DocumentationGenerator`.

## 4. Detailed Refactoring Plan

### Phase 1: Core Logic Refactoring & CLI Alignment

1.  **Define Core Service Interfaces:** Create classes/modules (e.g., `InitializationService`, `IngestionService`, `QueryService`, `ChatService`, `DocumentationService`, `ConfigurationService`) to encapsulate logic for each command, interacting with underlying components (Storage, Indexers, Embeddings, LLMs).
2.  **Refactor CLI (`cli.py`):**
    - Restructure `typer` commands to match `init`, `ingest`, `query`, `chat`, `generate`, `config`.
    - Split `init` (setup only) and `ingest` (processing/indexing).
    - Create `query` (from `ask`), `chat` (new), `generate` (adapt existing), `config` (adapt existing).
    - Update arguments/options.
    - Use Core Services instead of direct component initialization.
3.  **Implement Chat Functionality (`ChatService`):**
    - Design session management (create, list, load).
    - Use SQLite for chat history storage.
    - Implement conversation history context management for LLMs.
4.  **Refine Configuration (`ConfigManager`):** Ensure clean loading, CLI overrides, and central accessibility.
5.  **Streamline Initialization:** Use application context or DI to manage component lifecycles.

### Phase 2: API Layer for External Use

1.  **Design API Endpoints:** Define FastAPI endpoints (see Section 6) mapping to Core Services. Use Pydantic for schemas.
2.  **Implement API Logic:** Have endpoint handlers call Core Service methods. Ensure proper error handling. Remove `subprocess` calls.
3.  **Authentication/Authorization:** Note as future consideration if needed beyond localhost.

### Phase 3: Documentation Generation Enhancements

1.  **Review `DocumentationGenerator`:** Examine `generate_for_repository`.
2.  **Implement Incremental Updates:** Add logic to compare file states (mtime/hash) and regenerate only changed files and affected overviews/indices.

### Phase 4: Testing and Refinement

1.  **Unit & Integration Tests:** Add/update tests for services, CLI, and API.
2.  **Manual Testing:** Test CLI and API against user flows.
3.  **Refinement:** Address issues found.

## 5. High-Level Architecture Diagram

```mermaid
graph TD
    subgraph CLI [Command Line Interface (cli.py)]
        CmdInit[init]
        CmdIngest[ingest]
        CmdQuery[query]
        CmdChat[chat]
        CmdGenerate[generate]
        CmdConfig[config]
    end

    subgraph API [External API (api.py/app.py)]
        EpInit[/init]
        EpIngest[/ingest]
        EpQuery[/query]
        EpChat[/chat/...]
        EpGenerate[/generate]
        EpConfig[/config]
    end

    subgraph CoreServices [Core Services Layer]
        InitSvc(InitializationService)
        IngestSvc(IngestionService)
        QuerySvc(QueryService)
        ChatSvc(ChatService)
        DocSvc(DocumentationService)
        ConfigSvc(ConfigurationService)
    end

    subgraph Components [Underlying Components]
        ConfigMgr([ConfigManager])
        LLMClients([LLM Clients])
        EmbedGen([EmbeddingGenerator])
        Storage([ChromaDBStorage])
        CodeIdx([CodebaseIndexer])
        SessionDB[(SQLite Session DB)]
        DocGen([DocumentationGenerator])
        FileSys[/File System (.docstra, codebase)/]
    end

    CLI -- Uses --> CoreServices
    API -- Uses --> CoreServices

    CoreServices -- Interacts with --> Components

    InitSvc --> ConfigMgr
    InitSvc --> FileSys

    IngestSvc --> ConfigMgr
    IngestSvc --> EmbedGen
    IngestSvc --> Storage
    IngestSvc --> CodeIdx
    IngestSvc --> FileSys

    QuerySvc --> ConfigMgr
    QuerySvc --> LLMClients
    QuerySvc --> EmbedGen
    QuerySvc --> Storage
    QuerySvc --> CodeIdx

    ChatSvc --> ConfigMgr
    ChatSvc --> LLMClients
    ChatSvc --> EmbedGen
    ChatSvc --> Storage
    ChatSvc --> CodeIdx
    ChatSvc --> SessionDB

    DocSvc --> ConfigMgr
    DocSvc --> LLMClients
    DocSvc --> DocGen
    DocSvc --> Storage
    DocSvc --> CodeIdx
    DocSvc --> FileSys

    ConfigSvc --> ConfigMgr
    ConfigSvc --> FileSys
```

## 6. Refined API Specification

**(Base URL: `/api/v1`)**

**1. Status & Context**

- **`GET /status`**
  - **Description:** Checks if `docstra` is initialized and provides basic status.
  - **Response (200 OK):** `{"initialized": bool, "config_path": str, "storage_path": str, "last_ingested": Optional[str]}`
  - **Response (404 Not Found):** `{"detail": "Docstra not initialized..."}`

**2. Initialization**

- **`POST /init`**
  - **Description:** Initializes `docstra`. Idempotent.
  - **Request Body:** `Optional[dict]` (Initial config values)
  - **Response (200 OK):** `{"status": "success", "message": "...", "config_path": str}`

**3. Configuration**

- **`GET /config`**
  - **Description:** Retrieves current configuration.
  - **Response (200 OK):** `{"status": "success", "config": dict}`
- **`PUT /config`**
  - **Description:** Updates configuration.
  - **Request Body:** `{"updates": dict}`
  - **Response (200 OK):** `{"status": "success", "config": dict}`

**4. Ingestion (Asynchronous)**

- **`POST /ingest`**
  - **Description:** Starts ingestion process.
  - **Request Body:** `Optional[dict]` (e.g., `{"force": bool, "include": list, "exclude": list}`)
  - **Response (202 Accepted):** `{"status": "pending", "task_id": str, "message": "..."}`
- **`GET /ingest/status/{task_id}`**
  - **Description:** Polls ingestion task status.
  - **Response (200 OK):** `{"task_id": str, "status": str, "progress": Optional[float], "message": Optional[str]}`

**5. Query**

- **`POST /query`**
  - **Description:** Sends a single question to RAG.
  - **Request Body:** `{"question": str, "n_results": Optional[int], "llm_override": Optional[dict], "embedding_override": Optional[dict]}`
  - **Response (200 OK):** `{"status": "success", "answer": str, "sources": list[dict]}`

**6. Chat (Session-based)**

- **`GET /chat/sessions`**
  - **Description:** Lists chat sessions.
  - **Response (200 OK):** `{"status": "success", "sessions": list[dict]}`
- **`POST /chat/start`**
  - **Description:** Starts a new chat session.
  - **Request Body:** `Optional[dict]` (e.g., `{"initial_message": str}`)
  - **Response (201 Created):** `{"status": "success", "session_id": str, "response": Optional[str]}`
- **`GET /chat/history/{session_id}`**
  - **Description:** Retrieves session history.
  - **Response (200 OK):** `{"status": "success", "history": list[dict]}`
- **`POST /chat/message/{session_id}`**
  - **Description:** Sends message to session.
  - **Request Body:** `{"message": str, "llm_override": Optional[dict]}`
  - **Response (200 OK):** `{"status": "success", "response": str, "sources": Optional[list[dict]]}`
- **`DELETE /chat/session/{session_id}`**
  - **Description:** Deletes a chat session.
  - **Response (200 OK):** `{"status": "success", "message": "..."}`

**7. Documentation Generation (Asynchronous)**

- **`POST /generate`**
  - **Description:** Starts documentation generation.
  - **Request Body:** `{"target_path": Optional[str], "output_dir": Optional[str], "format": Optional[str], "incremental": Optional[bool], "config_overrides": Optional[dict]}`
  - **Response (202 Accepted):** `{"status": "pending", "task_id": str, "message": "..."}`
- **`GET /generate/status/{task_id}`**
  - **Description:** Polls generation task status.
  - **Response (200 OK):** `{"task_id": str, "status": str, "progress": Optional[float], "output_path": Optional[str], "message": Optional[str]}`

**Error Handling:**

- Use standard HTTP status codes (4xx/5xx).
- Consistent error body: `{"detail": str, "error_code": Optional[str]}`
