import json
import os


class DocstraConfig:
    """Configuration for Docstra service."""

    def __init__(
        self,
        model_name: str = "gpt-4",
        temperature: float = 0.0,
        embedding_model: str = "text-embedding-ada-002",
        chunk_size: int = 1000,
        chunk_overlap: int = 100,
        max_context_chunks: int = 5,
        persist_directory: str = ".docstra",
        system_prompt: str = "You are a helpful code assistant that provides concise and accurate information about code.",
    ):
        self.model_name = model_name
        self.temperature = temperature
        self.embedding_model = embedding_model
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.max_context_chunks = max_context_chunks
        self.persist_directory = persist_directory
        self.system_prompt = system_prompt

    @classmethod
    def from_file(cls, config_path: str) -> "DocstraConfig":
        """Load configuration from a JSON file."""
        try:
            with open(config_path, "r") as f:
                config_dict = json.load(f)
            return cls(**config_dict)
        except (FileNotFoundError, json.JSONDecodeError):
            return cls()

    def to_file(self, config_path: str) -> None:
        """Save configuration to a JSON file."""
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, "w") as f:
            json.dump(self.__dict__, f, indent=2)
