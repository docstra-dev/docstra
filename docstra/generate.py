import os
import time
from pathlib import Path
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from docstra.logger import logger
from tiktoken import get_encoding

from docstra.main import Docstra


def generate_markdown_docs(docstra_instance, output_dir="./.docstra/docs", max_tokens_per_minute=60000, token_encoding_name="cl100k_base"):
    """
    Generate Markdown documentation files for each code file in the repository, with throttling for API calls.

    Args:
        docstra_instance (Docstra): The Docstra instance with an initialized vectorstore and LLM chain.
        output_dir (str): Directory where markdown files will be saved.
        max_tokens_per_minute (int): Maximum token usage allowed per minute.
        token_encoding_name (str): The name of the encoding for calculating tokens.
    """
    # Create output directory if it does not exist
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Token counter and encoding setup for throttling
    total_tokens = 0
    encoding = get_encoding(token_encoding_name)

    # Define a LangChain LLM prompt template for generating documentation
    prompt_template = PromptTemplate(
        input_variables=["file_name", "chunk_content"],
        template="""
        Write detailed documentation for each function and class in the following code chunk.

        Code file: {file_name}

        Code:
        ```
        {chunk_content}
        ```

        Output format:
        - Title of the function or class
        - Brief explanation of its purpose
        - Detailed description of inputs, outputs, and any internal steps
        """
    )

    # Initialize LLMChain with the prompt template
    llm_chain = LLMChain(llm=docstra_instance.llm, prompt=prompt_template)

    # Group documents by file path using the generator
    documents_by_file = {}

    for doc in docstra_instance.get_all_docs():
        file_path = doc.metadata["file_path"]
        if file_path not in documents_by_file:
            documents_by_file[file_path] = []
        documents_by_file[file_path].append(doc)

    # Process each file and generate documentation
    for file_path, file_docs in documents_by_file.items():
        file_name = os.path.basename(file_path)
        md_file_path = output_dir / f"{file_name}.md"

        logger.info(f"Generating documentation for {file_path}")

        # Write content to markdown file
        with open(md_file_path, "w", encoding="utf-8") as md_file:
            md_file.write(f"# Documentation for {file_name}\n\n")

            for doc in file_docs:
                # Calculate token count for the chunk
                chunk_content = doc.page_content
                token_count = len(encoding.encode(chunk_content))

                # Throttle if we approach the token limit
                total_tokens += token_count
                if total_tokens > max_tokens_per_minute:
                    logger.warning("Approaching token limit; throttling...")
                    time.sleep(60)  # Wait for a minute to reset token count
                    total_tokens = token_count  # Reset with the current chunk's tokens

                # Use the OpenAI LLM to generate the documentation for each chunk
                formatted_response = llm_chain.run({
                    "file_name": file_name,
                    "chunk_content": chunk_content
                })

                # Write generated documentation for each chunk to the Markdown file
                md_file.write(formatted_response + "\n\n---\n\n")

        logger.info(f"Generated documentation file: {md_file_path}")

# Example usage
if __name__ == "__main__":
    # Initialize Docstra instance
    docstra = Docstra(repo_path=".")

    # Generate documentation markdown files with throttling
    generate_markdown_docs(docstra_instance=docstra)
