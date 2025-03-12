# Docstra

**Docstra** is an AI-powered tool designed to automatically generate in-depth, contextual documentation for code repositories. Leveraging Large Language Models (LLMs) through LangChain and ChromaDB, Docstra analyzes and links together various elements in a codebase, creating searchable, organized, and meaningful documentation that enhances the developer experience.

This project is part of a Master's Thesis at the **University of Oslo** which will be completed in June 2025. It explores open-source tooling for LLMs and code, with a focus on understanding and code documentation.

## Key Features

- **Automated Documentation**: Scans and indexes code repositories to generate rich documentation with logical links between files, functions, classes, and modules
- **LLM-Powered Chatbot**: Provides an interactive way to query the codebase and explore documentation
- **Contextual Understanding**: Creates connections between different parts of your codebase for more meaningful documentation
- **Simplified Installation**: Easy to set up and use in any Python environment

## Installation

### Option 1: Install via pip

```bash
pip install docstra
```

### Option 2: Install from GitHub release

Download the latest wheel file from the GitHub repository releases and install it:

```bash
pip install docstra-x.x.x-py3-none-any.whl
```

## Getting Started

### 1. Initialize Docstra in your project

Run the initialization command in your project directory:

```bash
docstra init
```

This will create a `.docstra` directory in your project and prompt you for any required configuration, such as your OpenAI API key.

### 2. Ingest your codebase

Process and generate embeddings for your codebase:

```bash
docstra ingest
```

This command scans your repository, analyzes the code, and creates a searchable index of your codebase components.

### 3. Interact with your documentation

#### Chat mode

Start an interactive chat session to explore your codebase:

```bash
docstra chat
```

This launches a conversational interface where you can ask questions about your code.

#### Query mode

Ask specific questions directly from the command line:

```bash
docstra query "How does the authentication system work?"
```

## Environment Variables

Docstra looks for a `.env` file in the `.docstra` directory or for environment variables:

- `OPENAI_API_KEY`: Your OpenAI API key (required for LLM functionality)

## Use Cases

- **Onboarding New Developers**: Help new team members quickly understand complex codebases
- **Code Discovery**: Easily find how different components interact within your project
- **Documentation Maintenance**: Keep documentation up-to-date with minimal effort
- **Knowledge Exploration**: Explore codebases through natural language queries

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

For questions or feedback about Docstra, please reach out to the project team at the **University of Oslo**.

**Project Repository**: [https://github.uio.no/docstra/docstra](https://github.uio.no/docstra/docstra)

---

Docstra is continually evolving to better serve developers, researchers, and educators in the field of software engineering. The project aims to bridge the gap between code and documentation through the power of Large Language Models.
