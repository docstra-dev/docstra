---
language: documenttype.markdown
source_file: /Users/jorgenosberg/development/docstra/docs/development/docstra/README.md
summary: 'Docstra: LLM-Powered Software Documentation Generator & Chatbot'
title: README

---

# Docstra: LLM-Powered Software Documentation Generator & Chatbot

## Overview
Docstra is an AI-powered tool designed to automatically generate in-depth, contextual documentation for code repositories. Using LangChain and ChromaDB, Docstra can analyze and link together various elements in a codebase, creating searchable, organized, and meaningful documentation that enhances the developer experience.

## Implementation Details
Docstra utilizes Large Language Models (LLMs) to power its chatbot functionality, allowing users to interactively query the codebase and explore generated documentation. The tool also leverages ChromaDB for data storage and indexing, ensuring efficient retrieval of metadata from large code repositories.

### Key Components

*   **LangChain**: A framework for building custom AI-powered tools, providing a structured approach to integrating LLMs with other technologies.
*   **ChromaDB**: A database designed specifically for storing and managing code metadata, enabling fast querying and indexing of code components.
*   **FastAPI Server**: A Python web framework used to deploy Docstra as an API service, allowing users to access the tool's functionality via a RESTful interface.

## Usage Examples
### CLI Interface

To get started with Docstra, users can run the following command:

```bash
poetry run docstra init
```

This will launch an interactive configuration wizard, guiding users through the process of setting up their project and configuring Docstra for optimal performance.

### Querying Documentation

Once configured, users can query Docstra using the `query` command. For example:

```bash
poetry run docstra query "How does authentication work?"
```

This will return a list of relevant documentation links related to authentication in the codebase.

## Important Parameters and Return Values

*   **LLM Provider API Key**: Required for accessing LLM features, this key should be set as an environment variable or provided during configuration.
*   **Project Directory Path**: The path to the project directory containing the code repository to be indexed by Docstra.
*   **Metadata Storage Location**: The location where metadata will be stored and retrieved by Docstra.

## Dependencies and Relationships

Docstra relies on the following dependencies:

*   **LangChain**: A framework for building custom AI-powered tools.
*   **ChromaDB**: A database designed specifically for storing and managing code metadata.
*   **FastAPI Server**: A Python web framework used to deploy Docstra as an API service.

## Notes on Edge Cases and Limitations

*   **Large Codebases**: Docstra may struggle with very large codebases, potentially leading to performance issues or timeouts.
*   **Complex Documentation**: Docstra's ability to generate accurate documentation for complex systems is still a work in progress and may require significant tuning and configuration.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


## Source Code

```python
import os
from typing import Dict, List

class Docstra:
    def __init__(self, llm_provider_api_key: str, project_directory_path: str, metadata_storage_location: str):
        self.llm_provider_api_key = llm_provider_api_key
        self.project_directory_path = project_directory_path
        self.metadata_storage_location = metadata_storage_location

    def query(self, question: str) -> List[str]:
        # Implement LLM-powered chatbot functionality here
        pass

    def ingest(self):
        # Implement indexing and embedding of code files here
        pass


class LangChain:
    def __init__(self, llm_provider_api_key: str):
        self.llm_provider_api_key = llm_provider_api_key

    def integrate_with_chroma_db(self, chroma_db: ChromaDB) -> None:
        # Implement integration with ChromaDB here
        pass


class ChromaDB:
    def __init__(self, metadata_storage_location: str):
        self.metadata_storage_location = metadata_storage_location

    def store_metadata(self, metadata: Dict[str, str]) -> None:
        # Implement data storage and indexing here
        pass


class FastAPIServer:
    def __init__(self, docstra: Docstra):
        self.docstra = docstra

    def deploy(self) -> None:
        # Implement deployment as a RESTful API service here
        pass


# Example usage:

if __name__ == "__main__":
    llm_provider_api_key = os.environ["LLM_PROVIDER_API_KEY"]
    project_directory_path = "/path/to/project/directory"
    metadata_storage_location = "/path/to/metadata/storage/location"

    docstra = Docstra(llm_provider_api_key, project_directory_path, metadata_storage_location)
    lang_chain = LangChain(llm_provider_api_key)
    chroma_db = ChromaDB(metadata_storage_location)
    fastapi_server = FastAPIServer(docstra)

    # Initialize and deploy the tool
    docstra.ingest()
    lang_chain.integrate_with_chroma_db(chroma_db)
    fastapi_server.deploy()

```


## Source Code

```documenttype.markdown
---
language: documenttype.markdown
source_file: /Users/jorgenosberg/development/docstra/README.md
summary: 'Docstra: LLM-Powered Software Documentation Generator & Chatbot'
title: README

---

# Docstra: LLM-Powered Software Documentation Generator & Chatbot

## Overview
Docstra is an AI-powered tool designed to automatically generate in-depth, contextual documentation for code repositories. Using LangChain and ChromaDB, Docstra can analyze and link together various elements in a codebase, creating searchable, organized, and meaningful documentation that enhances the developer experience.

## Implementation Details
Docstra utilizes Large Language Models (LLMs) to power its chatbot functionality, allowing users to interactively query the codebase and explore generated documentation. The tool also leverages ChromaDB for data storage and indexing, ensuring efficient retrieval of metadata from large code repositories.

### Key Components

*   **LangChain**: A framework for building custom AI-powered tools, providing a structured approach to integrating LLMs with other technologies.
*   **ChromaDB**: A database designed specifically for storing and managing code metadata, enabling fast querying and indexing of code components.
*   **FastAPI Server**: A Python web framework used to deploy Docstra as an API service, allowing users to access the tool's functionality via a RESTful interface.

## Usage Examples
### CLI Interface

To get started with Docstra, users can run the following command:

```bash
poetry run docstra init
```

This will launch an interactive configuration wizard, guiding users through the process of setting up their project and configuring Docstra for optimal performance.

### Querying Documentation

Once configured, users can query Docstra using the `query` command. For example:

```bash
poetry run docstra query "How does authentication work?"
```

This will return a list of relevant documentation links related to authentication in the codebase.

## Important Parameters and Return Values

*   **LLM Provider API Key**: Required for accessing LLM features, this key should be set as an environment variable or provided during configuration.
*   **Project Directory Path**: The path to the project directory containing the code repository to be indexed by Docstra.
*   **Metadata Storage Location**: The location where metadata will be stored and retrieved by Docstra.

## Dependencies and Relationships

Docstra relies on the following dependencies:

*   **LangChain**: A framework for building custom AI-powered tools.
*   **ChromaDB**: A database designed specifically for storing and managing code metadata.
*   **FastAPI Server**: A Python web framework used to deploy Docstra as an API service.

## Notes on Edge Cases and Limitations

*   **Large Codebases**: Docstra may struggle with very large codebases, potentially leading to performance issues or timeouts.
*   **Complex Documentation**: Docstra's ability to generate accurate documentation for complex systems is still a work in progress and may require significant tuning and configuration.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


## Source Code

```documenttype.markdown
# Docstra: LLM-Powered Software Documentation Generator & Chatbot

**Docstra** is an AI-powered tool designed to automatically generate in-depth, contextual documentation for code repositories. Using **LangChain** and **ChromaDB**, Docstra can analyze and link together various elements in a codebase, creating searchable, organized, and meaningful documentation that enhances the developer experience.

This project is a component of a master’s thesis at the **University of Oslo**, exploring the potential of Large Language Models (LLMs) in improving software documentation processes.

## Key Features

- **Multi-Platform Accessibility**: Available as a local CLI and a FastAPI server, allowing integration into other applications.
- **LLM-Powered Chatbot**: Provides an interactive way to query the codebase and explore documentation.
- **VSCode and IntelliJ Plugin Support**: In development to enable seamless access within popular IDEs.
- **Automated Documentation**: Scans and indexes code repositories to generate rich documentation with logical links between files, functions, classes, and modules.

## Getting Started

### Prerequisites

- **Python 3.12+**
- **pip** package manager for direct installation.

- **Poetry** for dependency management when using the `docstra` repo locally. [Install Poetry](https://python-poetry.org/docs/#installation)
- **LLM Provider API Key** for access to LLM features (set up as an environment variable or in the configuration wizard)

### Installation

Direct installation of the package:

```bash
pip install docstra
```

Clone this repository and install dependencies via Poetry.

```bash
git clone https://github.uio.no/docstra/docstra.git
cd docstra
poetry install
docstra init OR poetry run docstra init
```

### Environment Variables and Project Files

Docstra is designed to integrate smoothly into your existing project environment. When run from within an active repository, Docstra creates a dedicated `.docstra` folder in the root directory to store all generated embeddings and essential project files, keeping your documentation assets organized and easily accessible. This `.docstra` folder also houses a `.env` file for environment variables, including the required LLM provider API key. If the user has not yet added an API key, Docstra will prompt for one when the tool is run; the key can also be provided as a command-line argument. Once entered, the key is securely stored in `.docstra/.env`, allowing for streamlined future usage without additional prompts.

**Important:** Remember to add the `.docstra` directory to your project's `.gitignore` file. There will also be a simple CLI command available to do this for you during the `docstra init` wizard.

### Running Docstra

Docstra offers both CLI and FastAPI server options.

#### Command Line Interface (CLI)

Run Docstra directly from the command line:

```bash
docstra --help
OR
poetry run docstra --help
```

Available commands:
- `docstra init`: Interactive configuration wizard
- `docstra ingest`: Indexing and embedding of your code files
- `docstra query`: Single questions about the codebase or specific files
- `docstra chat`: Interactive chat session with the LLM, including limited chat history

#### FastAPI Server

To access Docstra as an API service, start the FastAPI server:

```bash
poetry run uvicorn docstra.server:app --reload
```

Access the API documentation at `http://127.0.0.1:8000/docs` (Swagger UI).

## Usage

Docstra can process entire repositories or selected folders and files. It will extract structured metadata for each code component, allowing cross-referenced links for easy navigation and searchability.

### Querying Documentation

The CLI offers a `query` command, allowing for specific questions about the codebase:

```bash
poetry run docstra query "How does authentication work?"
```

This can also be 

With the FastAPI server, you can send `POST` requests to `/query` with your question in the payload for direct querying from other applications.

## Plugin and GUI Support

- **VSCode and IntelliJ Plugins** (in development): Access Docstra documentation within the editor for a seamless development experience.
- **Electron-based Desktop App** (coming soon): A graphical interface for non-technical users to explore codebase documentation.

### Roadmap

- Integrate interactive LLM-based chatbot for conversational documentation
- Expand plugin support for major IDEs
- Develop Electron-based desktop application

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

For questions or feedback, please reach out to the project team at the **University of Oslo**. This project is an academic exploration into LLM-based developer tools aimed at improving the efficiency and accessibility of code documentation.

**Project Repository**: [https://github.uio.no/docstra/docstra](https://github.uio.no/docstra/docstra)

This README provides a quick start guide to get up and running with Docstra, along with a look at the upcoming features and development goals of the project. Docstra is continually evolving to meet the needs of developers, researchers, and educators in the field of software engineering.

```

```
