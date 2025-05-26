# File: ./docstra/core/llm/ollama.py

"""
Ollama integration for LLM interactions.
"""

from __future__ import annotations

import json
from typing import Any, Dict, Generator, List, Union

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from docstra.core.llm.prompt import PromptBuilder


class OllamaClient:
    """Client for interacting with Ollama models."""

    def __init__(
        self,
        model_name: str = "deepseek-r1",
        api_base: str = "http://localhost:11434",
        max_tokens: int = 2000,
        temperature: float = 0.7,
        validate_connection: bool = True,
    ):
        """Initialize the Ollama client.

        Args:
            model_name: Name of the Ollama model to use
            api_base: Base URL for the Ollama API
            max_tokens: Maximum number of tokens to generate
            temperature: Temperature for generation (0.0 to 1.0)
            validate_connection: Whether to validate connection during initialization
        """
        self.model_name = model_name
        self.api_base = api_base
        self.max_tokens = max_tokens
        self.temperature = temperature

        # Initialize prompt builder
        self.prompt_builder = PromptBuilder()

        # Check if Ollama is running, but don't fail hard if it's not
        self.connected = False
        self.connection_error = None
        
        if validate_connection:
            try:
                self._check_ollama()
                self.connected = True
            except ConnectionError as e:
                self.connection_error = str(e)
                # Don't print warnings during initialization - let the caller handle this
        else:
            # Skip connection validation during initialization
            pass

    def _check_ollama(self) -> None:
        """Check if Ollama is running."""
        try:
            response = requests.get(
                f"{self.api_base}/api/tags", timeout=2.0
            )  # Add a timeout
            if response.status_code != 200:
                raise ConnectionError(
                    f"Ollama API returned status code {response.status_code}"
                )
        except requests.RequestException as e:
            raise ConnectionError(f"Failed to connect to Ollama API: {str(e)}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    def generate(
        self, prompt: str, stream: bool = False
    ) -> Union[str, Generator[str, None, None]]:
        """Generate a response from Ollama.

        Args:
            prompt: Prompt for generation
            stream: Whether to stream the response

        Returns:
            Generated response or stream
        """
        # Check connection before generating
        if not self.connected:
            is_connected, message = self.validate_connection()
            if not is_connected:
                return f"Error: {message}"

        url = f"{self.api_base}/api/generate"

        data = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": stream,
            "options": {
                "num_predict": self.max_tokens,
                "temperature": self.temperature,
            },
        }

        if stream:
            return self._stream_response(url, data)
        else:
            return self._generate_response(url, data)

    def _generate_response(self, url: str, data: Dict[str, Any]) -> str:
        """Generate a complete response.

        Args:
            url: API endpoint URL
            data: Request data

        Returns:
            Generated response
        """
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()

            result = response.json()
            return result.get("response", "")
        except Exception as e:
            print(f"Error in Ollama API call: {str(e)}")
            raise

    def _stream_response(
        self, url: str, data: Dict[str, Any]
    ) -> Generator[str, None, None]:
        """Stream the response from Ollama.

        Args:
            url: API endpoint URL
            data: Request data

        Returns:
            Generator yielding response chunks
        """
        try:
            with requests.post(url, json=data, stream=True) as response:
                response.raise_for_status()

                for line in response.iter_lines():
                    if line:
                        chunk = json.loads(line)
                        if "response" in chunk:
                            yield chunk["response"]

                        if chunk.get("done", False):
                            break
        except Exception as e:
            print(f"Error in Ollama streaming API call: {str(e)}")
            raise

    def document_code(
        self,
        code: str,
        language: str,
        additional_context: str = "",
        stream: bool = False,
    ) -> Union[str, Generator[str, None, None]]:
        """Generate documentation for code.

        Args:
            code: Code to document
            language: Programming language
            additional_context: Additional context about the code
            stream: Whether to stream the response

        Returns:
            Generated documentation
        """
        prompt = self.prompt_builder.build_document_code_prompt(
            code=code, language=language, additional_context=additional_context
        )

        return self.generate(prompt, stream=stream)

    def explain_code(
        self,
        code: str,
        language: str,
        additional_context: str = "",
        stream: bool = False,
    ) -> Union[str, Generator[str, None, None]]:
        """Generate an explanation for code.

        Args:
            code: Code to explain
            language: Programming language
            additional_context: Additional context about the code
            stream: Whether to stream the response

        Returns:
            Generated explanation
        """
        prompt = self.prompt_builder.build_explain_code_prompt(
            code=code, language=language, additional_context=additional_context
        )

        return self.generate(prompt, stream=stream)

    def answer_question(
        self,
        question: str,
        context: Union[str, List[Dict[str, Any]]],
        stream: bool = False,
    ) -> Union[str, Generator[str, None, None]]:
        """Answer a question based on context.

        Args:
            question: User question
            context: Context for answering the question
            stream: Whether to stream the response

        Returns:
            Generated answer
        """
        prompt = self.prompt_builder.build_answer_question_prompt(
            question=question, context=context
        )

        return self.generate(prompt, stream=stream)

    def generate_examples(
        self,
        request: str,
        language: str,
        additional_context: str = "",
        stream: bool = False,
    ) -> Union[str, Generator[str, None, None]]:
        """Generate code examples.

        Args:
            request: Request for examples
            language: Programming language
            additional_context: Additional context for the examples
            stream: Whether to stream the response

        Returns:
            Generated examples
        """
        prompt = self.prompt_builder.build_generate_examples_prompt(
            request=request, language=language, additional_context=additional_context
        )

        return self.generate(prompt, stream=stream)

    def custom_request(
        self, template_name: str, stream: bool = False, **kwargs
    ) -> Union[str, Generator[str, None, None]]:
        """Make a custom request using a template.

        Args:
            template_name: Name of the template to use
            stream: Whether to stream the response
            **kwargs: Values for template placeholders

        Returns:
            Generated response
        """
        prompt = self.prompt_builder.build_custom_prompt(
            template_name=template_name, **kwargs
        )

        return self.generate(prompt, stream=stream)

    def add_template(self, name: str, template: str) -> None:
        """Add a new template or override an existing one.

        Args:
            name: Template name
            template: Template string
        """
        self.prompt_builder.add_template(name, template)

    def validate_connection(self) -> tuple[bool, str]:
        """Validate connection to Ollama and return status with helpful message.
        
        Returns:
            Tuple of (is_connected, message)
        """
        try:
            self._check_ollama()
            self.connected = True
            self.connection_error = None
            return True, "Connected to Ollama successfully"
        except ConnectionError as e:
            self.connected = False
            self.connection_error = str(e)
            
            # Provide helpful error message
            if "Connection refused" in str(e):
                message = (
                    "Could not connect to Ollama. Please ensure Ollama is running.\n"
                    "To start Ollama:\n"
                    "  1. Install Ollama from https://ollama.ai\n"
                    "  2. Run 'ollama serve' in a terminal\n"
                    "  3. Or try a different model provider with 'docstra config --model openai' or 'docstra config --model anthropic'"
                )
            else:
                message = f"Ollama connection error: {e}"
            
            return False, message

    def get_connection_status(self) -> tuple[bool, str]:
        """Get current connection status without attempting to reconnect.
        
        Returns:
            Tuple of (is_connected, status_message)
        """
        if self.connected:
            return True, "Connected to Ollama"
        elif self.connection_error:
            return False, f"Connection error: {self.connection_error}"
        else:
            return False, "Connection not tested"
