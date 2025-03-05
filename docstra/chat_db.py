from pathlib import Path
import sqlite3
import json
import time

class ChatDB:
    def __init__(self):
        # Initialize the chat database inside .docstra/db/.
        self.base_dir = Path(__file__).resolve().parent / ".docstra"
        self.db_dir = self.base_dir / "db"
        self.db_path = self.db_dir / "chat_sessions.db"

        # Ensure the .docstra/db/ folder exists
        self.db_dir.mkdir(parents=True, exist_ok=True)

        # Initialize the database
        self._initialize_db()

    def _initialize_db(self):
        # Create tables if they don't exist.
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_name TEXT UNIQUE,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                messages TEXT
            )
        """)
        conn.commit()
        conn.close()

    def create_session(self, session_name=None):
        # Create a new chat session with a custom name and return its ID.
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if session_name is None or session_name.strip() == "":
            session_name = f"Session {int(time.time())}"  # Fallback name

        cursor.execute("INSERT INTO chat_sessions (session_name, messages) VALUES (?, ?)", (session_name, json.dumps([])))
        conn.commit()
        session_id = cursor.lastrowid
        conn.close()
        return session_id, session_name  # Return session ID and name

    def save_message(self, session_id, question, response):
        # Save a message to the session.
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT messages FROM chat_sessions WHERE id = ?", (session_id,))
        result = cursor.fetchone()

        messages = json.loads(result[0]) if result and result[0] else []
        messages.append({"question": question, "response": response})

        cursor.execute("UPDATE chat_sessions SET messages = ? WHERE id = ?", (json.dumps(messages), session_id))
        conn.commit()
        conn.close()

    def list_sessions(self):
        # Retrieve all stored chat sessions.
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, session_name, created_at FROM chat_sessions ORDER BY created_at DESC")
        sessions = cursor.fetchall()
        conn.close()
        return [{"id": s[0], "name": s[1], "created_at": s[2]} for s in sessions]

    def get_chat_history(self, session_id):
        # Retrieve chat history for a given session.
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT messages FROM chat_sessions WHERE id = ?", (session_id,))
        result = cursor.fetchone()
        conn.close()
        if result:
            return json.loads(result[0])
        return None

    def get_session_id_by_name(self, session_name):
        # Retrieve a session ID by its name.
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM chat_sessions WHERE session_name = ?", (session_name,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
