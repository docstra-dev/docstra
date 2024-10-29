# Docstra: LLM-Powered Software Documentation Generator & Chatbot

**Docstra** is an AI-powered tool designed to automatically generate in-depth, contextual documentation for code repositories. Using **LangChain** and **ChromaDB**, Docstra can analyze and link together various elements in a codebase, creating searchable, organized, and meaningful documentation that enhances the developer experience.

This project is a component of a master’s thesis at the **University of Oslo**, exploring the potential of Large Language Models (LLMs) in improving software documentation processes.

## Key Features

- **Automated Documentation**: Scans and indexes code repositories to generate rich documentation with logical links between files, functions, classes, and modules.
- **Multi-Platform Accessibility**: Available as a local CLI and a FastAPI server, allowing integration into other applications.
- **VSCode and IntelliJ Plugin Support**: In development to enable seamless access within popular IDEs.
- **Electron-based GUI Companion App**: A cross-platform desktop application to view and interact with generated documentation.
- **LLM-Powered Chatbot**: Provides an interactive way to query the codebase and explore documentation.

## Getting Started

### Prerequisites

- **Python 3.8+**
- **Poetry** for dependency management. [Install Poetry](https://python-poetry.org/docs/#installation)
- **OpenAI API Key** for access to LLM features (set up as an environment variable)

### Installation

Clone this repository and install dependencies via Poetry.

```bash
git clone https://github.uio.no/docstra/docstra.git
cd docstra
poetry install
```

### Environment Variables and Project Files

Docstra is designed to integrate smoothly into your existing project environment. When run from within an active repository, Docstra creates a dedicated `.docstra` folder in the root directory to store all generated embeddings and essential project files, keeping your documentation assets organized and easily accessible. This `.docstra` folder also houses a `.env` file for environment variables, including the required OpenAI API key. If the user has not yet added an API key, Docstra will prompt for one when the tool is run; the key can also be provided as a command-line argument. Once entered, the key is securely stored in `.docstra/.env`, allowing for streamlined future usage without additional prompts.

### Running Docstra

Docstra offers both CLI and FastAPI server options.

#### Command Line Interface (CLI)

Run Docstra directly from the command line:

```bash
poetry run docstra --help
```

Example of generating documentation:

```bash
poetry run docstra generate-docs path/to/your/codebase
```

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