import json
import os
from os import PathLike
from pathlib import Path
from dotenv import load_dotenv, set_key

DEFAULT_PROJECT_CONFIG = {
    "exclusion_rules": {
        "dirs_to_exclude": [".git", ".venv", "node_modules", "__pycache__", "dist", "build"],
        "files_to_exclude": [".env", "Pipfile.lock", "poetry.lock"],
        "file_extensions_to_include": [".py", ".md", ".txt", ".json", ".yaml", ".sh"]
    },
    "throttling": {
        "max_tokens_per_minute": 60000
    }
}

CORE_CONFIG_FILE = Path.home() / ".docstra_core_config.json"
DEFAULT_CORE_CONFIG = {
    "app_data_dir": str(Path.home() / ".docstra_data"),
    "default_db_dir": str(Path.home() / ".docstra_data/db"),
    "openai_model": "text-embedding-3-small"
}


def load_project_config(repo_path: str | PathLike[str]) -> dict:
    """Loads project-level configuration stored in a '.docstra/config.json' file."""
    config_path = Path(repo_path) / ".docstra/config.json"
    if not config_path.exists():
        save_project_config(repo_path, DEFAULT_PROJECT_CONFIG)  # Save default config if it doesn't exist
    with open(config_path, "r") as f:
        return json.load(f)


def save_project_config(repo_path: str | PathLike[str], config: dict):
    """Saves project-level configuration to a '.docstra/config.json' file."""
    config_path = Path(repo_path) / ".docstra"
    config_path.mkdir(parents=True, exist_ok=True)
    with open(config_path / "config.json", "w") as f:
        json.dump(config, f, indent=4)


def load_core_config() -> dict:
    """Loads core-level configuration from the user's home directory."""
    if not CORE_CONFIG_FILE.exists():
        save_core_config(DEFAULT_CORE_CONFIG)  # Save default config if it doesn't exist
    with open(CORE_CONFIG_FILE, "r") as f:
        return json.load(f)


def save_core_config(config: dict):
    """Saves core-level configuration to a file in the user's home directory."""
    with open(CORE_CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)


def load_env_variables(repo_path: str | PathLike[str]):
    """Loads environment variables from a '.docstra/.env' file."""
    env_path = Path(repo_path) / ".docstra/.env"
    if not env_path.exists():
        set_key(str(env_path), "OPENAI_API_KEY", "")  # Create .env file with an empty API key if it doesn't exist
    load_dotenv(env_path)


def set_env_variable(repo_path: str | PathLike[str], key: str, value: str):
    """Sets an environment variable in the '.docstra/.env' file."""
    env_path = Path(repo_path) / ".docstra/.env"
    env_path.parent.mkdir(parents=True, exist_ok=True)  # Ensure .docstra directory exists
    if not env_path.exists():
        with open(env_path, "w") as f:
            pass  # Create an empty .env file if it doesn't exist
    set_key(str(env_path), key, value)


def get_openai_api_key(repo_path: str | PathLike[str]) -> str:
    """Retrieves the OpenAI API key from the '.docstra/.env' file."""
    load_env_variables(repo_path)
    return os.environ.get("OPENAI_API_KEY", "")


def set_openai_api_key(repo_path: str | PathLike[str], api_key: str):
    """Sets the OpenAI API key in the '.docstra/.env' file."""
    set_env_variable(repo_path, "OPENAI_API_KEY", api_key)

