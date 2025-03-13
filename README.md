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
