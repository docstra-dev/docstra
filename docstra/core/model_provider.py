from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_community.llms.llamacpp import LlamaCpp
from langchain_community.llms.huggingface_pipeline import HuggingFacePipeline
from langchain_core.language_models import BaseChatModel

from docstra.core.errors import ModelProviderError


class ModelProvider:
    """Factory for creating LLM instances from different providers."""

    @staticmethod
    def create_model(
        provider: str, model_name: str, temperature: float = 0.0, **kwargs
    ) -> BaseChatModel:
        """Create an LLM instance based on provider.

        Args:
            provider: The LLM provider (openai, anthropic, huggingface, llama)
            model_name: Name of the model to use
            temperature: Sampling temperature
            **kwargs: Additional provider-specific arguments

        Returns:
            A LangChain chat model instance

        Raises:
            ModelProviderError: If the provider is not supported or if model initialization fails
        """
        provider = provider.lower()

        try:
            if provider == "openai":
                return ChatOpenAI(
                    model_name=model_name, temperature=temperature, **kwargs
                )

            elif provider == "anthropic":
                return ChatAnthropic(
                    model=model_name, temperature=temperature, **kwargs
                )

            elif provider == "huggingface":
                return HuggingFacePipeline(
                    model_id=model_name, temperature=temperature, **kwargs
                )

            elif provider == "llama":
                return LlamaCpp(
                    model_path=model_name, temperature=temperature, **kwargs
                )

            else:
                raise ModelProviderError(f"Unsupported model provider: {provider}")
        except Exception as e:
            raise ModelProviderError(
                f"Failed to initialize model from provider {provider}: {str(e)}",
                cause=e,
            )
