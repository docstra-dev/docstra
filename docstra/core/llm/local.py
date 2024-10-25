# File: ./docstra/core/llm/local.py

"""
Local model integration for LLM interactions.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    StoppingCriteria,
    StoppingCriteriaList,
    TextIteratorStreamer,
)

from docstra.core.llm.prompt import PromptBuilder


class KeywordsStoppingCriteria(StoppingCriteria):
    """Custom stopping criteria based on keywords."""

    def __init__(self, keywords, tokenizer):
        """Initialize the stopping criteria.

        Args:
            keywords: List of keywords to stop on
            tokenizer: Tokenizer for the model
        """
        self.keywords = keywords
        self.tokenizer = tokenizer

        # Pre-tokenize keywords for faster comparison
        self.keyword_ids = []
        for keyword in keywords:
            ids = tokenizer.encode(keyword, add_special_tokens=False)
            if len(ids) > 0:
                self.keyword_ids.append(ids)

    def __call__(self, input_ids, scores, **kwargs):
        """Check if any stopping keyword is generated.

        Args:
            input_ids: Current sequence of token IDs
            scores: Scores for each token
            **kwargs: Additional arguments

        Returns:
            True if stopping criteria met, False otherwise
        """
        # Check for each keyword
        for keyword_ids in self.keyword_ids:
            # Check if any keyword appears at the end of the sequence
            if len(keyword_ids) <= len(input_ids[0]):
                # Compare the end of the sequence with the keyword
                if input_ids[0][-len(keyword_ids) :].tolist() == keyword_ids:
                    return True

        return False


class LocalModelClient:
    """Client for interacting with local transformer models."""

    def __init__(
        self,
        model_name: str = "TheBloke/Llama-2-7b-Chat-GGUF",
        model_path: Optional[str] = None,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        device: str = "auto",
    ):
        """Initialize the local model client.

        Args:
            model_name: Name or path of the model to use
            model_path: Optional local path to the model
            max_tokens: Maximum number of tokens to generate
            temperature: Temperature for generation (0.0 to 1.0)
            device: Device to run the model on ('auto', 'cpu', 'cuda', etc.)
        """
        self.model_name = model_name
        self.model_path = model_path or model_name
        self.max_tokens = max_tokens
        self.temperature = temperature

        # Determine device
        if device == "auto":
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

        # Initialize model and tokenizer
        print(f"Loading model {self.model_path} on {self.device}...")

        try:
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_path, trust_remote_code=True
            )

            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                device_map=self.device,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                trust_remote_code=True,
                low_cpu_mem_usage=True,
            )
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            raise

        # Configure stopping criteria
        self.stopping_keywords = ["<|endoftext|>", "<|im_end|>", "</s>"]

        # Initialize prompt builder
        self.prompt_builder = PromptBuilder()

    def generate(self, prompt: str, stream: bool = False) -> str:
        """Generate a response from the local model.

        Args:
            prompt: Prompt for generation
            stream: Whether to stream the response

        Returns:
            Generated response
        """
        # Tokenize the prompt
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)

        # Setup stopping criteria
        stopping_criteria = StoppingCriteriaList(
            [KeywordsStoppingCriteria(self.stopping_keywords, self.tokenizer)]
        )

        # Generate
        if stream:
            # Setup streamer
            streamer = TextIteratorStreamer(
                self.tokenizer, skip_prompt=True, skip_special_tokens=True
            )

            # Start generation in a separate thread
            generation_kwargs = {
                "input_ids": inputs.input_ids,
                "attention_mask": inputs.attention_mask,
                "max_new_tokens": self.max_tokens,
                "temperature": self.temperature,
                "do_sample": self.temperature > 0,
                "stopping_criteria": stopping_criteria,
                "streamer": streamer,
            }

            # Start generation thread
            import threading

            thread = threading.Thread(
                target=self.model.generate, kwargs=generation_kwargs
            )
            thread.start()

            # Stream tokens
            generated_text = ""
            for text in streamer:
                generated_text += text

            return str(generated_text)
        else:
            # Generate in one go
            outputs = self.model.generate(
                inputs.input_ids,
                attention_mask=inputs.attention_mask,
                max_new_tokens=self.max_tokens,
                temperature=self.temperature,
                do_sample=self.temperature > 0,
                stopping_criteria=stopping_criteria,
            )

            # Decode the generated tokens
            generated_text = self.tokenizer.decode(
                outputs[0][inputs.input_ids.shape[1] :], skip_special_tokens=True
            )

            return generated_text

    def document_code(
        self,
        code: str,
        language: str,
        additional_context: str = "",
        stream: bool = False,
    ) -> str:
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
    ) -> str:
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
    ) -> str:
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
    ) -> str:
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

    def custom_request(self, template_name: str, stream: bool = False, **kwargs) -> str:
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
