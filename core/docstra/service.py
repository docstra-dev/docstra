import os
import json
import uuid
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path

import chromadb
from chromadb.config import Settings
from langchain_chroma.vectorstores import Chroma
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_message_histories import ChatMessageHistory

from docstra.config import DocstraConfig
from docstra.core import DocstraSession
from docstra.database import DocstraDatabaseManager


class DocstraService:
    """Main service for Docstra, handling code indexing and LLM interactions."""

    def __init__(self, working_dir: str = None, config_path: str = None):
        """Initialize the Docstra service.

        Args:
            working_dir: The directory to index and operate in
            config_path: Path to configuration file
        """
        self.working_dir = working_dir or os.getcwd()
        self.config = DocstraConfig.from_file(
            config_path or os.path.join(self.working_dir, ".docstra", "config.json")
        )

        # Create persistence directory
        self.persist_dir = os.path.join(self.working_dir, self.config.persist_directory)
        os.makedirs(self.persist_dir, exist_ok=True)

        # Initialize the database manager
        self.db_path = os.path.join(self.persist_dir, "sessions.db")
        self.db_manager = DocstraDatabaseManager(self.db_path)

        # Initialize the database schema
        self._init_db_schema()

        # Save config if it doesn't exist
        if not os.path.exists(os.path.join(self.persist_dir, "config.json")):
            self.config.to_file(os.path.join(self.persist_dir, "config.json"))

        # Initialize components
        self._init_vectorstore()
        self._init_llm()

        # Sessions storage
        self.sessions: Dict[str, DocstraSession] = {}

        # Session-specific message history store
        self.message_histories = {}

        # Load existing sessions
        self.load_sessions()

    def _init_db_schema(self):
        """Initialize the SQLite database schema."""
        # Get connection from manager
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        # Create sessions table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                config TEXT NOT NULL
            )
        """
        )

        # Create messages table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions (session_id) ON DELETE CASCADE
            )
        """
        )

        # Create index metadata table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS index_metadata (
                file_path TEXT PRIMARY KEY,
                last_modified TEXT NOT NULL,
                last_indexed TEXT NOT NULL,
                chunk_count INTEGER DEFAULT 0
            )
        """
        )

        # Enable foreign keys
        cursor.execute("PRAGMA foreign_keys = ON")

        # Commit changes
        conn.commit()

        print(f"SQLite database schema initialized at {self.db_path}")

    def _init_vectorstore(self) -> None:
        """Initialize the vector store for code storage and retrieval."""
        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(model=self.config.embedding_model)

        # Initialize ChromaDB client
        self.chroma_client = chromadb.PersistentClient(
            path=os.path.join(self.persist_dir, "chromadb"),
            settings=Settings(anonymized_telemetry=False),
        )

        # Check if collection exists, create if not
        collection_name = "docstra_code"
        collections = self.chroma_client.list_collections()
        collection_exists = any(c.name == collection_name for c in collections)

        if not collection_exists:
            self.chroma_client.create_collection(collection_name)
            # Index code after creating collection
            self.update_index()

        # Initialize Chroma vector store
        self.vectorstore = Chroma(
            client=self.chroma_client,
            collection_name=collection_name,
            embedding_function=self.embeddings,
        )

    def _init_llm(self) -> None:
        """Initialize the LLM and related components."""
        self.llm = ChatOpenAI(
            model_name=self.config.model_name,
            temperature=self.config.temperature,
        )

        # Create retriever
        self.retriever = self.vectorstore.as_retriever(
            search_kwargs={"k": self.config.max_context_chunks}
        )

        # Contextualize question system prompt
        contextualize_q_system_prompt = (
            "Given a chat history and the latest user question "
            "which might reference context in the chat history, "
            "formulate a standalone question which can be understood "
            "without the chat history. Do NOT answer the question, just "
            "reformulate it if needed and otherwise return it as is."
        )

        # Create contextualize question prompt
        self.contextualize_q_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", contextualize_q_system_prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
            ]
        )

        # QA prompt
        self.qa_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.config.system_prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "Current working directory: {cwd}"),
                ("human", "{question}"),
                ("human", "Relevant documents:\n{context}"),
            ]
        )

        # Define the chain
        # First define how we process the user input with chat history
        contextualize_question_chain = (
            self.contextualize_q_prompt | self.llm | StrOutputParser()
        )

        # Then define the complete retrieval and answer chain
        self.chain = (
            RunnablePassthrough.assign(
                context=lambda x: self.retriever.invoke(
                    contextualize_question_chain.invoke(
                        {
                            "input": x["question"],
                            "chat_history": x.get("chat_history", []),
                        }
                    )
                ),
            )
            | self.qa_prompt
            | self.llm
            | StrOutputParser()
        )

    def update_index(self) -> None:
        """Update the codebase index, only reindexing changed files."""
        print(f"Checking for code changes in {self.working_dir}...")

        # Get all code files
        code_files = self._collect_code_files()
        if not code_files:
            print("No code files found to index.")
            return

        # Get indexed files metadata from database
        indexed_files = self._get_indexed_files_metadata()

        # Track new, modified, and deleted files
        new_files = []
        modified_files = []
        deleted_file_paths = set(indexed_files.keys())

        # Check each file
        for file_path in code_files:
            relative_path = os.path.relpath(file_path, self.working_dir)
            mtime = os.path.getmtime(file_path)

            if relative_path in deleted_file_paths:
                # File exists, remove from deleted set
                deleted_file_paths.remove(relative_path)

                # Check if modified
                if str(mtime) != indexed_files[relative_path]["last_modified"]:
                    modified_files.append(file_path)
            else:
                # New file
                new_files.append(file_path)

        # Process new and modified files
        if new_files or modified_files:
            self._process_files_for_indexing(new_files + modified_files)

        # Remove deleted files from index
        if deleted_file_paths:
            self._remove_files_from_index(deleted_file_paths)

        print(
            f"Index updated: {len(new_files)} new files, {len(modified_files)} modified files, {len(deleted_file_paths)} deleted files"
        )

    def _get_indexed_files_metadata(self) -> Dict[str, Dict]:
        """Get metadata for all indexed files from the database."""
        indexed_files = {}

        # Get from index_metadata table
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT file_path, last_modified, last_indexed, chunk_count FROM index_metadata"
        )
        rows = cursor.fetchall()

        for file_path, last_modified, last_indexed, chunk_count in rows:
            indexed_files[file_path] = {
                "last_modified": last_modified,
                "last_indexed": last_indexed,
                "chunk_count": chunk_count,
            }

        # If database has no records, try to get from vectorstore
        if not indexed_files:
            try:
                # Query all documents to get metadata
                indexed_docs = self.vectorstore.get()
                for i, metadata in enumerate(indexed_docs["metadatas"]):
                    if "file_path" in metadata and "last_modified" in metadata:
                        file_path = metadata["file_path"]
                        if file_path not in indexed_files:
                            indexed_files[file_path] = {
                                "last_modified": metadata["last_modified"],
                                "last_indexed": metadata.get(
                                    "indexed_at", datetime.now().isoformat()
                                ),
                                "chunk_count": 0,  # We don't know the count yet
                            }

                        # Update count for this file
                        indexed_files[file_path]["chunk_count"] += 1

                # Save to database for future use
                for file_path, metadata in indexed_files.items():
                    cursor.execute(
                        "INSERT OR REPLACE INTO index_metadata (file_path, last_modified, last_indexed, chunk_count) VALUES (?, ?, ?, ?)",
                        (
                            file_path,
                            metadata["last_modified"],
                            metadata["last_indexed"],
                            metadata["chunk_count"],
                        ),
                    )
                conn.commit()

            except Exception as e:
                print(f"Error retrieving indexed files from vectorstore: {str(e)}")

        return indexed_files

    def _collect_code_files(self) -> List[Path]:
        """Collect all code files in the working directory."""
        # Collect code files
        code_files = []
        for ext in [
            ".py",
            ".js",
            ".ts",
            ".java",
            ".kt",
            ".cs",
            ".go",
            ".rs",
            ".cpp",
            ".c",
            ".h",
            ".hpp",
        ]:
            code_files.extend(Path(self.working_dir).glob(f"**/*{ext}"))

        # Filter out .git, node_modules, etc.
        ignored_dirs = [
            ".git",
            "node_modules",
            "venv",
            ".venv",
            "build",
            "dist",
            "__pycache__",
        ]
        code_files = [
            f for f in code_files if not any(d in str(f) for d in ignored_dirs)
        ]

        return code_files

    def _process_files_for_indexing(self, file_paths: List[Path]) -> None:
        """Process and index a list of files."""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.chunk_size, chunk_overlap=self.config.chunk_overlap
        )

        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        for file_path in file_paths:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Skip empty files
                if not content.strip():
                    continue

                # Prepare metadata with last_modified time
                relative_path = os.path.relpath(file_path, self.working_dir)
                mtime = os.path.getmtime(file_path)
                indexed_at = datetime.now().isoformat()

                file_metadata = {
                    "file_path": str(relative_path),
                    "file_type": os.path.splitext(file_path)[1],
                    "indexed_at": indexed_at,
                    "last_modified": str(mtime),
                }

                # First remove any existing chunks for this file
                self._remove_files_from_index([relative_path])

                # Split and add to vectorstore
                docs = text_splitter.create_documents(
                    [content], metadatas=[file_metadata]
                )

                # Update database with file metadata
                cursor.execute(
                    "INSERT OR REPLACE INTO index_metadata (file_path, last_modified, last_indexed, chunk_count) VALUES (?, ?, ?, ?)",
                    (relative_path, str(mtime), indexed_at, len(docs)),
                )
                conn.commit()

                # Add to vectorstore
                self.vectorstore.add_documents(docs)

                print(f"Indexed: {relative_path} ({len(docs)} chunks)")
            except Exception as e:
                print(f"Error indexing {file_path}: {str(e)}")

    def _remove_files_from_index(self, file_paths: List[str]) -> None:
        """Remove files from the index."""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()

            for path in file_paths:
                # Use the Chroma API to filter and delete by metadata
                self.vectorstore.delete(where={"file_path": path})

                # Remove from database
                cursor.execute(
                    "DELETE FROM index_metadata WHERE file_path = ?", (path,)
                )

                print(f"Removed from index: {path}")

            conn.commit()
        except Exception as e:
            print(f"Error removing files from index: {str(e)}")

    def create_session(self) -> str:
        """Create a new session and return its ID."""
        session_id = str(uuid.uuid4())

        # Create session object
        session = DocstraSession(session_id, self.config)

        try:
            # Get connection from manager
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()

            # Store session
            config_json = json.dumps(
                {
                    "model_name": self.config.model_name,
                    "temperature": self.config.temperature,
                    "system_prompt": self.config.system_prompt,
                }
            )

            cursor.execute(
                "INSERT INTO sessions (session_id, created_at, config) VALUES (?, ?, ?)",
                (session_id, session.created_at.isoformat(), config_json),
            )

            conn.commit()

            # Store in memory
            self.sessions[session_id] = session
            self.message_histories[session_id] = session.chat_history

            print(
                f"Created session: {session_id}, Total sessions: {len(self.sessions)}"
            )
            return session_id
        except Exception as e:
            print(f"Error creating session: {str(e)}")
            raise

    def get_session(self, session_id: str) -> Optional[DocstraSession]:
        """Get a session by ID."""
        # First check memory cache
        if session_id in self.sessions:
            print(f"Found session in memory: {session_id}")
            return self.sessions[session_id]

        try:
            # Get connection from manager
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()

            # Get session data
            cursor.execute(
                "SELECT created_at, config FROM sessions WHERE session_id = ?",
                (session_id,),
            )
            result = cursor.fetchone()

            if not result:
                print(f"Session not found: {session_id}")
                return None

            created_at, config_json = result

            # Create session object
            config_data = json.loads(config_json)
            config = DocstraConfig()
            config.model_name = config_data.get("model_name", self.config.model_name)
            config.temperature = config_data.get("temperature", self.config.temperature)
            config.system_prompt = config_data.get(
                "system_prompt", self.config.system_prompt
            )

            session = DocstraSession(session_id, config)
            session.created_at = datetime.fromisoformat(created_at)

            # Get messages
            cursor.execute(
                "SELECT role, content, timestamp FROM messages WHERE session_id = ? ORDER BY timestamp",
                (session_id,),
            )
            messages = cursor.fetchall()

            # Create chat history
            chat_history = ChatMessageHistory()

            # Add messages to session and chat history
            session.messages = []
            for role, content, timestamp in messages:
                # Add to session messages
                session.messages.append(
                    {"role": role, "content": content, "timestamp": timestamp}
                )

                # Add to chat history
                if role == "user":
                    chat_history.add_user_message(content)
                elif role == "assistant":
                    chat_history.add_ai_message(content)
                elif role == "system":
                    chat_history.add_system_message(content)

            # Store in memory
            session.chat_history = chat_history
            self.sessions[session_id] = session
            self.message_histories[session_id] = chat_history

            print(
                f"Loaded session from database: {session_id} with {len(session.messages)} messages"
            )
            return session
        except Exception as e:
            print(f"Error loading session: {str(e)}")
            return None

    def load_sessions(self) -> None:
        """Load existing sessions from the database."""
        try:
            # Get connection from manager
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()

            # Get all sessions
            cursor.execute("SELECT session_id FROM sessions")
            session_ids = [row[0] for row in cursor.fetchall()]

            for session_id in session_ids:
                # This will load the session into memory
                self.get_session(session_id)

            print(f"Loaded {len(session_ids)} sessions from database")
        except Exception as e:
            print(f"Error loading sessions: {str(e)}")

    def add_message(self, session_id: str, role: str, content: str) -> None:
        """Add a message to a session and save to database."""
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        timestamp = datetime.now().isoformat()

        try:
            # Get connection from manager
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO messages (session_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
                (session_id, role, content, timestamp),
            )

            conn.commit()

            # Add to session
            message = {"role": role, "content": content, "timestamp": timestamp}
            session.messages.append(message)

            # Add to chat history
            if role == "user":
                session.chat_history.add_user_message(content)
            elif role == "assistant":
                session.chat_history.add_ai_message(content)
            elif role == "system":
                session.chat_history.add_system_message(content)

        except Exception as e:
            print(f"Error adding message: {str(e)}")
            raise

    def process_message(self, session_id: str, message: str) -> str:
        """Process a user message and return the assistant's response."""
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        # Add user message
        self.add_message(session_id, "user", message)

        # Process message with LLM chain
        try:
            # Get the chat history
            chat_history = self.message_histories[session_id].messages

            # Invoke the chain
            response = self.chain.invoke(
                {
                    "question": message,
                    "chat_history": chat_history,
                    "cwd": self.working_dir,
                }
            )

            # Response is now a string from the StrOutputParser
            answer = response

        except Exception as e:
            print(f"Chain execution error: {str(e)}")
            # Fallback to direct LLM call if chain fails
            response = self.llm.invoke(
                f"Question about codebase: {message}\nWorking directory: {self.working_dir}"
            )
            answer = response.content

        # Add assistant response
        self.add_message(session_id, "assistant", answer)

        return answer

    def add_context(
        self,
        session_id: str,
        file_path: str,
        content: str = None,
        selection_range: Dict = None,
    ) -> None:
        """Add additional context to a session."""
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        # If content not provided, try to read from file
        if content is None and file_path:
            try:
                full_path = os.path.join(self.working_dir, file_path)
                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception as e:
                raise ValueError(f"Could not read file {file_path}: {str(e)}")

        if not content:
            return

        # If selection range provided, extract that part of the content
        if selection_range and content:
            lines = content.split("\n")
            start_line = max(0, selection_range.get("startLine", 0))
            end_line = min(len(lines), selection_range.get("endLine", len(lines)))
            content = "\n".join(lines[start_line : end_line + 1])

        # Add context as a system message
        context_message = (
            f"Additional context from file {file_path}:\n```\n{content}\n```"
        )
        self.add_message(session_id, "system", context_message)

    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        try:
            # Get connection from manager
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()

            # Delete session (will cascade to messages)
            cursor.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))

            deleted = cursor.rowcount > 0

            conn.commit()

            # Remove from memory
            if session_id in self.sessions:
                del self.sessions[session_id]

            if session_id in self.message_histories:
                del self.message_histories[session_id]

            if deleted:
                print(f"Deleted session: {session_id}")
            else:
                print(f"Session not found for deletion: {session_id}")

            return deleted
        except Exception as e:
            print(f"Error deleting session: {str(e)}")
            return False

    def cleanup(self):
        """Clean up resources when shutting down."""
        try:
            # Close database connections
            if hasattr(self, "db_manager"):
                self.db_manager.close()

            print("Resources cleaned up")
        except Exception as e:
            print(f"Error during cleanup: {str(e)}")
