# File: ./docstra/core/llm/base.py
"""Base LLM client interface for consistent usage across providers."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union


class LLMClient(ABC):
    """Base LLM client interface that all provider implementations should follow."""

    @abstractmethod
    def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate text response from a prompt.

        Args:
            prompt: The prompt to send to the LLM
            system_prompt: Optional system prompt for models that support it

        Returns:
            Generated text
        """
        pass

    @abstractmethod
    def document_code(
        self,
        code: str,
        language: str,
        additional_context: Optional[str] = None,
    ) -> str:
        """Generate documentation for code.

        Args:
            code: The code to document
            language: Programming language of the code
            additional_context: Additional context to include in the prompt

        Returns:
            Generated documentation
        """
        pass

    @abstractmethod
    def explain_code(
        self,
        code: str,
        language: str,
        additional_context: Optional[str] = None,
    ) -> str:
        """Explain the given code.

        Args:
            code: The code to explain
            language: Programming language of the code
            additional_context: Additional context to include in the prompt

        Returns:
            Generated explanation
        """
        pass

    @abstractmethod
    def answer_question(
        self,
        question: str,
        context: Union[str, List[Dict[str, Any]]],
    ) -> str:
        """Answer a question using retrieved context.

        Args:
            question: The question to answer
            context: Retrieved context to use in answering

        Returns:
            Generated answer
        """
        pass

    @abstractmethod
    def generate_examples(
        self,
        request: str,
        language: str,
    ) -> str:
        """Generate code examples.

        Args:
            request: Description of the examples to generate
            language: Programming language for the examples

        Returns:
            Generated code examples
        """
        pass

    @abstractmethod
    def chat(
        self,
        messages: List[Dict[str, str]],
        history: Optional[List[Dict[str, str]]] = None,
        system_prompt: Optional[str] = None,
    ) -> str:
        """Generate a response in a chat conversation.

        Args:
            messages: Chat messages in the format [{"role": "user", "content": "..."}]
            history: Optional chat history
            system_prompt: Optional system prompt

        Returns:
            Generated response
        """
        pass

    def get_last_usage(self) -> Dict[str, Any]:
        """Get token usage information from the last request.

        Returns:
            Dictionary containing token usage information
        """
        return {
            "input_tokens": 0,
            "output_tokens": 0,
            "cost": 0.0,
        }
