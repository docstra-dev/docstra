from datetime import datetime

from langchain_community.chat_message_histories import ChatMessageHistory

from docstra.config import DocstraConfig


class DocstraSession:
    """Manages a single session with the Docstra service."""

    def __init__(self, session_id: str, config: DocstraConfig):
        self.session_id = session_id
        self.config = config
        self.created_at = datetime.now()
        self.messages = []
        self.chat_history = ChatMessageHistory()
