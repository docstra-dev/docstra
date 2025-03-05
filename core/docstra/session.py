from datetime import datetime
import json
from typing import Dict, List, Optional, Any
import uuid

from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from docstra.config import DocstraConfig


class DocstraSession:
    """Manages a single session with the Docstra service."""

    def __init__(
        self, session_id: Optional[str] = None, config: Optional[DocstraConfig] = None
    ):
        """Initialize a new session.

        Args:
            session_id: Unique identifier for the session (generated if not provided)
            config: Configuration for the session
        """
        self.session_id = session_id or str(uuid.uuid4())
        self.config = config or DocstraConfig()
        self.created_at = datetime.now()
        self.messages: List[Dict[str, str]] = []
        self.chat_history = ChatMessageHistory()

    @classmethod
    def from_database(
        cls,
        session_id: str,
        created_at: str,
        config_json: str,
        messages: List[Dict[str, str]],
        context_files: List[str] = None,
    ) -> "DocstraSession":
        """Create a session from database records."""
        # Create session
        session = cls(session_id)

        # Set creation time
        session.created_at = datetime.fromisoformat(created_at)

        # Load config
        config_data = json.loads(config_json)
        config = DocstraConfig()

        # Override config values from saved config
        for key, value in config_data.items():
            if hasattr(config, key):
                setattr(config, key, value)

        session.config = config

        # Load messages
        session.messages = messages

        # Set context files
        session.context_files = context_files or []

        # Populate chat history
        chat_history = ChatMessageHistory()
        for msg in messages:
            role = msg["role"]
            content = msg["content"]

            # Add to chat history with correct message type
            if role == "user":
                chat_history.add_message(HumanMessage(content=content))
            elif role == "assistant":
                chat_history.add_message(AIMessage(content=content))
            elif role == "system":
                chat_history.add_message(SystemMessage(content=content))

        session.chat_history = chat_history

        return session

    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary for serialization."""
        return {
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "messages": self.messages,
            "context_files": getattr(self, "context_files", []),
            "config": {
                attr: getattr(self.config, attr)
                for attr in dir(self.config)
                if not attr.startswith("_") and not callable(getattr(self.config, attr))
            },
        }

    def add_message(self, role: str, content: str) -> Dict[str, str]:
        """Add a message to the session.

        Args:
            role: Message role (user, assistant, system)
            content: Message content

        Returns:
            The message dictionary
        """
        timestamp = datetime.now().isoformat()
        message = {"role": role, "content": content, "timestamp": timestamp}

        # Add to messages list
        self.messages.append(message)

        # Add to chat history with correct message type
        if role == "user":
            self.chat_history.add_message(HumanMessage(content=content))
        elif role == "assistant":
            self.chat_history.add_message(AIMessage(content=content))
        elif role == "system":
            self.chat_history.add_message(SystemMessage(content=content))

        return message
