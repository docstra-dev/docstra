# File: ./docstra/core/tracking/llm_tracker.py
"""
Callback handler and utilities for tracking LLM operation statistics.
"""

import time
import uuid
from typing import Any, Dict, List, Optional, Union, ClassVar
from langchain_core.callbacks.base import BaseCallbackHandler
from langchain_core.outputs import LLMResult
import tiktoken
from pathlib import Path
import json
import datetime

# Global store for LLM stats - can be refactored for more sophisticated storage
_llm_stats_store: List[Dict[str, Any]] = []


# --- Helper functions for stats management ---
def get_llm_stats() -> List[Dict[str, Any]]:
    """Returns a copy of the collected LLM statistics."""
    return list(_llm_stats_store)


def clear_llm_stats() -> None:
    """Clears all collected LLM statistics."""
    _llm_stats_store.clear()


def _estimate_tokens(text: str, model_name: str = "gpt-3.5-turbo") -> int:
    """Estimates token count for a given text using tiktoken.
    Defaults to gpt-3.5-turbo encoding if model-specific encoding is not found.
    """
    try:
        encoding = tiktoken.encoding_for_model(model_name)
    except KeyError:
        # Fallback to a common encoding if the specific model is not found
        # This is a rough estimate.
        encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))


class DocstraStatsCallbackHandler(BaseCallbackHandler):
    """
    Callback Handler for collecting LLM operation statistics.

    Collects:
    - Latency (duration)
    - Token counts (prompt, completion, total) - if provided by LLM/response
    - Estimated input tokens (if not provided by LLM)
    - Model name
    - Cost (placeholder for future implementation)
    """

    def __init__(self):
        super().__init__()
        self.current_call_data: Dict[str, Any] = {}
        self.last_input_tokens = 0
        self.last_output_tokens = 0
        self.last_duration_ms = 0
        self.last_cost = 0.0

    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        """Run when LLM starts running."""
        self.current_call_data = {
            "call_id": str(uuid.uuid4()),
            "start_time": time.perf_counter(),
            "prompts": prompts,
            "model_name": serialized.get(
                "name", serialized.get("id", ["Unknown"])[-1]
            ),  # Try to get model name
            "invocation_params": kwargs.get("invocation_params", {}),
            "estimated_input_tokens": sum(
                _estimate_tokens(
                    p,
                    kwargs.get("invocation_params", {}).get(
                        "model_name", "gpt-3.5-turbo"
                    ),
                )
                for p in prompts
            ),
        }

    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        """Run on new LLM token. (Not typically used for aggregate stats here)"""
        pass

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Run when LLM ends running."""
        end_time = time.perf_counter()
        duration = end_time - self.current_call_data.get(
            "start_time", end_time
        )  # Avoid KeyError if start_time missing

        llm_output = response.llm_output if response.llm_output else {}
        token_usage = llm_output.get("token_usage", {})

        prompt_tokens = token_usage.get("prompt_tokens")
        completion_tokens = token_usage.get("completion_tokens")
        total_tokens = token_usage.get("total_tokens")

        # If prompt_tokens not available from provider, use our estimate
        if prompt_tokens is None:
            prompt_tokens = self.current_call_data.get("estimated_input_tokens")

        # Estimate completion tokens if not available (less accurate)
        if completion_tokens is None and response.generations:
            completion_text = "".join(
                gen.text for run_gens in response.generations for gen in run_gens
            )
            completion_tokens = _estimate_tokens(
                completion_text,
                self.current_call_data.get("model_name", "gpt-3.5-turbo"),
            )

        if (
            total_tokens is None
            and prompt_tokens is not None
            and completion_tokens is not None
        ):
            total_tokens = prompt_tokens + completion_tokens

        # Try to get model name from response if not in serialized
        if self.current_call_data.get("model_name") == "Unknown" and llm_output.get(
            "model_name"
        ):
            self.current_call_data["model_name"] = llm_output.get("model_name")
        elif self.current_call_data.get(
            "model_name"
        ) == "Unknown" and self.current_call_data.get("invocation_params", {}).get(
            "model"
        ):
            self.current_call_data["model_name"] = self.current_call_data.get(
                "invocation_params", {}
            ).get("model")

        self.last_input_tokens = prompt_tokens or 0
        self.last_output_tokens = completion_tokens or 0
        self.last_duration_ms = round(duration * 1000, 2)
        self.last_cost = 0.0  # Placeholder for cost calculation

        stats_entry = {
            "call_id": self.current_call_data.get("call_id"),
            "model_name": self.current_call_data.get("model_name", "Unknown"),
            "duration_ms": self.last_duration_ms,
            "prompt_tokens": self.last_input_tokens,
            "completion_tokens": self.last_output_tokens,
            "total_tokens": total_tokens,
            "cost_usd": self.last_cost,
            "timestamp": time.time(),
            # "prompts": self.current_call_data.get("prompts"), # Optional: for debugging, can be verbose
            # "response": response.generations[0][0].text if response.generations and response.generations[0] else None # Optional
        }
        _llm_stats_store.append(stats_entry)
        self.current_call_data = {}  # Reset for next call

    def on_llm_error(
        self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> None:
        """Run when LLM errors."""
        end_time = time.perf_counter()
        duration = end_time - self.current_call_data.get("start_time", end_time)

        stats_entry = {
            "call_id": self.current_call_data.get("call_id"),
            "model_name": self.current_call_data.get("model_name", "Unknown"),
            "duration_ms": round(duration * 1000, 2),
            "error": str(error),
            "timestamp": time.time(),
        }
        _llm_stats_store.append(stats_entry)
        self.current_call_data = {}  # Reset

    # TODO: Implement handlers for on_chat_model_start, on_chain_start/end, on_tool_start/end if needed for more granular tracking
    # For embeddings, a similar callback or direct wrapping might be needed if LangChain doesn't provide callbacks for them.
    # Or, we can wrap the embedding generation call itself.

    def on_chain_start(
        self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any
    ) -> Any:
        """Run when chain starts running."""
        # For now, just log chain starts for context, can be expanded
        # print(f"Chain started: {serialized.get('name', 'UnknownChain')}")
        pass

    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> Any:
        """Run when chain ends running."""
        # print(f"Chain ended. Outputs: {list(outputs.keys())}")
        pass


# Example of how to potentially track embedding usage (if not covered by LLM callbacks)
# This would require modifying how embeddings are called.
# For now, focusing on LLM calls via the callback handler.

# def track_embedding_call(func):
#     """
#     Decorator or wrapper to track embedding calls.
#     This is a conceptual placeholder.
#     """
#     @functools.wraps(func)
#     def wrapper_track_embedding_call(*args, **kwargs):
#         start_time = time.perf_counter()
#         # Assuming the first arg or a kwarg 'texts' contains the list of texts
#         texts_to_embed = []
#         if args and isinstance(args[0], list): # Simple assumption
#             texts_to_embed = args[0]
#         elif kwargs.get("texts") and isinstance(kwargs.get("texts"), list):
#             texts_to_embed = kwargs.get("texts")

#         estimated_tokens = sum(_estimate_tokens(text) for text in texts_to_embed)

#         result = func(*args, **kwargs)
#         duration = time.perf_counter() - start_time

#         # How to get model_name for embeddings? Needs to be passed or inferred.
#         # Embedding model name might be part of the embedding object itself.
#         embedding_model_name = "unknown_embedding_model"
#         if hasattr(args[0], 'model'): # if 'self' is the embedding client
#             embedding_model_name = getattr(args[0], 'model', embedding_model_name)

#         stats_entry = {
#             "call_id": str(uuid.uuid4()),
#             "type": "embedding",
#             "model_name": embedding_model_name,
#             "duration_ms": round(duration * 1000, 2),
#             "num_texts": len(texts_to_embed),
#             "estimated_input_tokens": estimated_tokens,
#             "cost_usd": 0.0, # Placeholder
#             "timestamp": time.time(),
#         }
#         _llm_stats_store.append(stats_entry)
#         return result
#     return wrapper_track_embedding_call


class LLMTracker:
    """Tracks LLM usage statistics across sessions."""

    # Price constants per 1K tokens (example rates)
    PRICING: ClassVar[Dict[str, Dict[str, Dict[str, float]]]] = {
        "anthropic": {
            "claude-3-haiku": {"input": 0.25, "output": 1.25},
            "claude-3-sonnet": {"input": 3.0, "output": 15.0},
            "claude-3-opus": {"input": 15.0, "output": 75.0},
            "claude-3.5-sonnet": {"input": 3.0, "output": 15.0},
            "default": {"input": 3.0, "output": 15.0},
        },
        "openai": {
            "gpt-4": {"input": 30.0, "output": 60.0},
            "gpt-4o": {"input": 5.0, "output": 15.0},
            "gpt-4o-mini": {"input": 1.0, "output": 3.0},
            "gpt-3.5-turbo": {"input": 0.5, "output": 1.5},
            "default": {"input": 5.0, "output": 15.0},
        },
        "ollama": {
            "default": {"input": 0.0, "output": 0.0},  # Local models have no API cost
        },
        "default": {"default": {"input": 1.0, "output": 2.0}},  # Conservative default
    }

    def __init__(self, stats_file: Optional[str] = None):
        """Initialize the tracker.

        Args:
            stats_file: Optional path to save stats
        """
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_requests = 0
        self.total_duration_ms = 0
        self.total_cost = 0.0
        self.last_usage: Dict[str, Any] = {}
        self.usage_history: List[Dict[str, Any]] = []

        self.stats_file = stats_file
        if not self.stats_file:
            # Default to a stats file in user's home directory
            self.stats_file = str(Path.home() / ".docstra" / "llm_stats.json")

        # Try to load existing stats
        self._load_stats()

    def _load_stats(self) -> None:
        """Load statistics from file if available."""
        try:
            stats_path = Path(self.stats_file)
            if stats_path.exists():
                with open(stats_path, "r") as f:
                    data = json.load(f)
                    self.total_input_tokens = data.get("total_input_tokens", 0)
                    self.total_output_tokens = data.get("total_output_tokens", 0)
                    self.total_requests = data.get("total_requests", 0)
                    self.total_duration_ms = data.get("total_duration_ms", 0)
                    self.total_cost = data.get("total_cost", 0.0)
                    self.usage_history = data.get("usage_history", [])
        except Exception:
            # If loading fails, start with empty stats
            pass

    def _save_stats(self) -> None:
        """Save statistics to file."""
        try:
            stats_path = Path(self.stats_file)
            stats_path.parent.mkdir(parents=True, exist_ok=True)

            data = {
                "total_input_tokens": self.total_input_tokens,
                "total_output_tokens": self.total_output_tokens,
                "total_requests": self.total_requests,
                "total_duration_ms": self.total_duration_ms,
                "total_cost": self.total_cost,
                "usage_history": self.usage_history[-100:],  # Keep last 100 entries
                "last_updated": datetime.datetime.now().isoformat(),
            }

            with open(stats_path, "w") as f:
                json.dump(data, f, indent=2)
        except Exception:
            # If saving fails, continue without error
            pass

    def record_usage(
        self,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        duration_ms: int = 0,
        request_type: str = "unspecified",
    ) -> None:
        """Record LLM usage data.

        Args:
            provider: LLM provider name
            model: Model name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            duration_ms: Request duration in milliseconds
            request_type: Type of request (e.g., "query", "chat", "document")
        """
        # Calculate cost based on provider and model
        provider_rates = self.PRICING.get(provider.lower(), self.PRICING["default"])
        model_rates = provider_rates.get(model.lower(), provider_rates.get("default"))

        input_cost = (input_tokens / 1000) * model_rates["input"]
        output_cost = (output_tokens / 1000) * model_rates["output"]
        total_cost = input_cost + output_cost

        # Update totals
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.total_requests += 1
        self.total_duration_ms += duration_ms
        self.total_cost += total_cost

        # Record this usage
        usage_data = {
            "timestamp": datetime.datetime.now().isoformat(),
            "provider": provider,
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "duration_ms": duration_ms,
            "cost": total_cost,
            "request_type": request_type,
        }

        self.last_usage = usage_data
        self.usage_history.append(usage_data)

        # Save stats
        self._save_stats()

    def get_session_stats(self) -> Dict[str, Any]:
        """Get the current session statistics.

        Returns:
            Dictionary containing session statistics
        """
        return {
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_requests": self.total_requests,
            "total_duration_ms": self.total_duration_ms,
            "total_cost": self.total_cost,
        }

    def get_usage_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get usage summary for the specified period.

        Args:
            days: Number of days to include in the summary

        Returns:
            Dictionary containing usage summary
        """
        # Filter usage history by date
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days)
        cutoff_str = cutoff_date.isoformat()

        recent_usage = [
            entry
            for entry in self.usage_history
            if entry.get("timestamp", "") >= cutoff_str
        ]

        # Calculate summary
        total_input = sum(entry.get("input_tokens", 0) for entry in recent_usage)
        total_output = sum(entry.get("output_tokens", 0) for entry in recent_usage)
        total_cost = sum(entry.get("cost", 0.0) for entry in recent_usage)

        # Group by model and provider
        by_provider = {}
        by_model = {}

        for entry in recent_usage:
            provider = entry.get("provider", "unknown")
            model = entry.get("model", "unknown")
            cost = entry.get("cost", 0.0)

            by_provider[provider] = by_provider.get(provider, 0.0) + cost
            by_model[model] = by_model.get(model, 0.0) + cost

        return {
            "period_days": days,
            "total_requests": len(recent_usage),
            "total_input_tokens": total_input,
            "total_output_tokens": total_output,
            "total_cost": total_cost,
            "cost_by_provider": by_provider,
            "cost_by_model": by_model,
        }
