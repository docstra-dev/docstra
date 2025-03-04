import logging
import os
import json
import uuid
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime
from pathlib import Path

import chromadb
from chromadb.config import Settings
from langchain_chroma.vectorstores import Chroma
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import ChatMessage
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_message_histories import ChatMessageHistory

from docstra.config import DocstraConfig
from docstra.session import DocstraSession
from docstra.database import Database, create_database
from docstra.errors import (
    ConfigError, 
    DatabaseError, 
    ModelProviderError, 
    EmbeddingError, 
    IndexingError,
    SessionError,
    DocstraError
)

def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None, console_output: bool = True):
    """Configure logging for Docstra.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path to write logs to
        console_output: Whether to output logs to console
        
    Returns:
        Logger instance configured for docstra
        
    Raises:
        ConfigError: If the log level is invalid or if there's an issue setting up logging
    """
    try:
        numeric_level = getattr(logging, log_level.upper(), None)
        if not isinstance(numeric_level, int):
            raise ConfigError(f"Invalid log level: {log_level}")

        # Create logger
        logger = logging.getLogger("docstra")
        logger.setLevel(numeric_level)
        
        # Remove any existing handlers to avoid duplicates
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # Define formatter
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        formatter = logging.Formatter(log_format)
        
        # Add file handler if specified
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(numeric_level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        # Add console handler if requested
        if console_output:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(numeric_level)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
            
        return logger
    except Exception as e:
        if isinstance(e, ConfigError):
            raise e
        raise ConfigError(f"Failed to setup logging: {str(e)}", cause=e)


class DocstraService:
    """Main service for Docstra, handling code indexing and LLM interactions."""

    def __init__(
        self, working_dir: str | Path = None, config_path: str | Path = None, log_level: str = None
    ):
        """Initialize the Docstra service.

        Args:
            working_dir: The directory to index and operate in
            config_path: Path to configuration file
            log_level: Override the logging level
        """
        # Set working directory first
        self.working_dir = Path(working_dir) if working_dir else Path.cwd()
        
        # Create base persistence directory
        base_persist_dir = self.working_dir / ".docstra"
        base_persist_dir.mkdir(exist_ok=True, parents=True)
        
        # Load configuration
        config_path = Path(config_path) if config_path else base_persist_dir / "config.json"
        self.config = DocstraConfig.from_file(str(config_path))
        
        # Set final persist directory using the config's persist_directory
        self.persist_dir = self.working_dir / self.config.persist_directory
        self.persist_dir.mkdir(exist_ok=True, parents=True)
        
        # Set up logging from config
        log_level = log_level or self.config.log_level
        self.logger = setup_logging(
            log_level=log_level, 
            log_file=self.config.log_file, 
            console_output=self.config.console_logging
        )
        self.logger.info(f"Initializing DocstraService in {self.working_dir}")

        # Initialize the database
        db_path = self.persist_dir / "sessions.db"
        self.db = create_database(str(db_path))

        # Save config if it doesn't exist
        saved_config_path = self.persist_dir / "config.json"
        if not saved_config_path.exists():
            self.logger.debug(f"Saving configuration to {saved_config_path}")
            self.config.to_file(str(saved_config_path))

        # Initialize components
        self.logger.debug("Initializing vector store...")
        self._init_vectorstore()
        
        self.logger.debug("Initializing language model...")
        self._init_llm()

        # Sessions storage
        self.sessions: Dict[str, DocstraSession] = {}

        # Load existing sessions
        self.logger.debug("Loading existing sessions...")
        self.load_sessions()

    # Removing _init_db_schema since database initialization is now handled by the Database class

    def _init_vectorstore(self) -> None:
        """Initialize the vector store for code storage and retrieval."""
        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(model=self.config.embedding_model)

        # Initialize ChromaDB client
        self.chroma_client = chromadb.PersistentClient(
            path=str(self.persist_dir / "chromadb"),
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

    def _format_context_with_links(self, documents):
        """Format retrieved documents with clickable links.
        
        Args:
            documents: List of document objects from retriever
            
        Returns:
            Formatted string with clickable links to files
        """
        formatted_docs = []
        
        for doc in documents:
            if hasattr(doc, "metadata") and "file_path" in doc.metadata:
                file_path = doc.metadata["file_path"]
                file_url = f"file://{self.working_dir}/{file_path}"
                
                # Format the content with a clickable link to the file and line numbers
                content = doc.page_content if hasattr(doc, "page_content") else str(doc)
                
                # Add line numbers to content
                lines = content.strip().split('\n')
                numbered_content = '\n'.join(f"{i+1:4d} | {line}" for i, line in enumerate(lines))
                
                formatted_doc = f"From file [{file_path}]({file_url}):\n```\n{numbered_content}\n```"
                formatted_docs.append(formatted_doc)
            else:
                # If no file_path in metadata, just use the content with line numbers
                content = doc.page_content if hasattr(doc, "page_content") else str(doc)
                
                # Add line numbers to content
                lines = content.strip().split('\n')
                numbered_content = '\n'.join(f"{i+1:4d} | {line}" for i, line in enumerate(lines))
                
                formatted_docs.append(f"```\n{numbered_content}\n```")
                
        return "\n\n".join(formatted_docs)
        
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
                context=lambda x: self._format_context_with_links(
                    self.retriever.invoke(
                        contextualize_question_chain.invoke(
                            {
                                "input": x["question"],
                                "chat_history": x.get("chat_history", []),
                            }
                        )
                    )
                ),
            )
            | self.qa_prompt
            | self.llm
            | StrOutputParser()
        )

    def update_index(self, force: bool = False) -> None:
        """Update the codebase index, only reindexing changed files.
        
        Args:
            force: If True, force reindexing of all files regardless of modification time
        """
        # Check if lazy indexing is enabled and we're not forcing an update
        if getattr(self.config, 'lazy_indexing', False) and not force:
            self.logger.info("Lazy indexing mode is enabled. Files will be indexed on-demand.")
            return
            
        self.logger.info(f"Checking for code changes in {self.working_dir}...")

        # Get all code files
        code_files = self._collect_code_files()
        if not code_files:
            self.logger.warning("No code files found to index.")
            return

        # Get indexed files metadata from database
        indexed_files = self._get_indexed_files_metadata()

        # Track new, modified, and deleted files
        new_files = []
        modified_files = []
        deleted_file_paths = set(indexed_files.keys())

        # Check each file
        for file_path in code_files:
            relative_path = file_path.relative_to(self.working_dir).as_posix()
            mtime = file_path.stat().st_mtime

            if relative_path in deleted_file_paths:
                # File exists, remove from deleted set
                deleted_file_paths.remove(relative_path)

                # Check if modified or if forced reindex
                if force or str(mtime) != indexed_files[relative_path]["last_modified"]:
                    modified_files.append(file_path)
            else:
                # New file
                new_files.append(file_path)

        # Process new and modified files
        if new_files or modified_files:
            self.logger.info(f"Processing {len(new_files)} new and {len(modified_files)} modified files")
            self._process_files_for_indexing(new_files + modified_files)

        # Remove deleted files from index
        if deleted_file_paths:
            self.logger.info(f"Removing {len(deleted_file_paths)} deleted files from index")
            self._remove_files_from_index(deleted_file_paths)

        self.logger.info(
            f"Index updated: {len(new_files)} new files, {len(modified_files)} modified files, {len(deleted_file_paths)} deleted files"
        )

    def _get_indexed_files_metadata(self) -> Dict[str, Dict]:
        """Get metadata for all indexed files from the database."""
        # First try to get from database
        indexed_files = self.db.get_file_metadata()
        
        # If database has no records, try to get from vectorstore
        if not indexed_files:
            self.logger.debug("No file metadata in database, trying to extract from vectorstore")
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
                    self.db.save_file_metadata(
                        file_path,
                        metadata["last_modified"],
                        metadata["last_indexed"],
                        metadata["chunk_count"]
                    )
                    
                self.logger.debug(f"Extracted and saved metadata for {len(indexed_files)} files from vectorstore")
            except Exception as e:
                self.logger.error(f"Error retrieving indexed files from vectorstore: {str(e)}")

        return indexed_files

    def _collect_code_files(self) -> List[Path]:
        """Collect all code files in the working directory based on configuration."""
        # Get file extensions from config if available
        extensions = getattr(self.config, 'included_extensions', [
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
        ])
        
        # Get excluded patterns from config if available
        excluded_patterns = getattr(self.config, 'excluded_patterns', [
            ".git",
            "node_modules",
            "venv",
            ".venv",
            "build",
            "dist",
            "__pycache__",
        ])
        
        # Collect code files
        code_files = []
        for ext in extensions:
            code_files.extend(Path(self.working_dir).glob(f"**/*{ext}"))

        # Filter out files matching excluded patterns
        filtered_files = []
        for file_path in code_files:
            # Check if file should be excluded
            should_exclude = False
            for pattern in excluded_patterns:
                # Handle both directory name patterns and glob patterns
                if '**' in pattern or '*' in pattern:
                    # This is a glob pattern
                    import fnmatch
                    rel_path = file_path.relative_to(self.working_dir).as_posix()
                    if fnmatch.fnmatch(rel_path, pattern):
                        should_exclude = True
                        break
                else:
                    # This is a directory name to exclude
                    if pattern in str(file_path):
                        should_exclude = True
                        break
                        
            if not should_exclude:
                filtered_files.append(file_path)

        return filtered_files
        
    def get_or_index_file(self, file_path: str) -> bool:
        """Check if file is indexed, index on-demand if not.
        
        Args:
            file_path: Relative path to the file
            
        Returns:
            True if file was already indexed or successfully indexed
        """
        if getattr(self.config, 'lazy_indexing', False):
            try:
                # Convert to Path object
                if isinstance(file_path, str):
                    if os.path.isabs(file_path):
                        full_path = Path(file_path)
                        rel_path = Path(file_path).relative_to(self.working_dir).as_posix()
                    else:
                        full_path = Path(self.working_dir) / file_path
                        rel_path = file_path
                else:
                    full_path = file_path
                    rel_path = file_path.relative_to(self.working_dir).as_posix()
                    
                if not full_path.exists():
                    self.logger.warning(f"File does not exist: {rel_path}")
                    return False
                    
                # Check if file is in index
                indexed_files = self._get_indexed_files_metadata()
                
                if rel_path not in indexed_files:
                    # File not indexed, add it now
                    self.logger.info(f"Lazy indexing file: {rel_path}")
                    self._process_files_for_indexing([full_path])
                    return True
                    
                # Check if file was modified since last indexed
                file_mtime = full_path.stat().st_mtime
                if str(file_mtime) != indexed_files[rel_path]["last_modified"]:
                    self.logger.info(f"File modified, reindexing: {rel_path}")
                    self._process_files_for_indexing([full_path])
                    
                return True
            except Exception as e:
                self.logger.error(f"Error in lazy indexing file {file_path}: {str(e)}")
                return False
        else:
            # In non-lazy mode, just return True as all files should already be indexed
            return True

    def _process_files_for_indexing(self, file_paths: List[Path]) -> None:
        """Process and index a list of files."""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.chunk_size, chunk_overlap=self.config.chunk_overlap
        )

        for file_path in file_paths:
            try:
                content = file_path.read_text(encoding="utf-8")

                # Skip empty files
                if not content.strip():
                    continue

                # Prepare metadata with last_modified time
                relative_path = file_path.relative_to(self.working_dir).as_posix()
                mtime = file_path.stat().st_mtime
                indexed_at = datetime.now().isoformat()

                file_metadata = {
                    "file_path": relative_path,
                    "file_type": file_path.suffix,
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
                self.db.save_file_metadata(
                    relative_path, 
                    str(mtime), 
                    indexed_at, 
                    len(docs)
                )

                # Add to vectorstore
                self.vectorstore.add_documents(docs)

                self.logger.info(f"Indexed: {relative_path} ({len(docs)} chunks)")
            except Exception as e:
                self.logger.error(f"Error indexing {file_path}: {str(e)}")

    def _remove_files_from_index(self, file_paths: List[str]) -> None:
        """Remove files from the index."""
        try:
            for path in file_paths:
                # Use the Chroma API to filter and delete by metadata
                self.vectorstore.delete(where={"file_path": path})

                # Remove from database
                self.db.delete_file_metadata(path)

                self.logger.info(f"Removed from index: {path}")
        except Exception as e:
            self.logger.error(f"Error removing files from index: {str(e)}")

    def create_session(self) -> str:
        """Create a new session and return its ID."""
        # Create session object with new UUID
        session = DocstraSession(config=self.config)
        session_id = session.session_id
        
        try:
            # Prepare config data to save
            config_json = json.dumps({
                key: value for key, value in session.config.__dict__.items()
                if not key.startswith('_') and not callable(value)
            })
            
            # Store session in database
            self.db.save_session(
                session_id, 
                session.created_at.isoformat(), 
                config_json
            )
            
            # Store in memory
            self.sessions[session_id] = session

            self.logger.info(
                f"Created session: {session_id}, Total sessions: {len(self.sessions)}"
            )
            return session_id
        except Exception as e:
            self.logger.error(f"Error creating session: {str(e)}")
            raise

    def get_session(self, session_id: str) -> Optional[DocstraSession]:
        """Get a session by ID."""
        # Allow partial ID matches if the ID is at least 6 characters
        if len(session_id) >= 6 and session_id not in self.sessions:
            matching_sessions = [sid for sid in self.sessions.keys() if sid.startswith(session_id)]
            if len(matching_sessions) == 1:
                session_id = matching_sessions[0]
        
        # First check memory cache
        if session_id in self.sessions:
            self.logger.debug(f"Found session in memory: {session_id}")
            return self.sessions[session_id]

        try:
            # Get session data from database
            session_data = self.db.get_session(session_id)
            
            if not session_data:
                # Try partial ID match in database
                if len(session_id) >= 6:
                    all_sessions = self.db.get_all_sessions()
                    matching_sessions = [sid for sid in all_sessions if sid.startswith(session_id)]
                    if len(matching_sessions) == 1:
                        session_data = self.db.get_session(matching_sessions[0])
                        session_id = matching_sessions[0]
            
            if not session_data:
                self.logger.warning(f"Session not found: {session_id}")
                return None
                
            created_at, config_json = session_data
            
            # Get messages for this session
            messages = self.db.get_messages(session_id)
            
            # Create session object from database data
            session = DocstraSession.from_database(
                session_id=session_id,
                created_at=created_at,
                config_json=config_json,
                messages=messages
            )
            
            # Store in memory
            self.sessions[session_id] = session

            self.logger.info(
                f"Loaded session from database: {session_id} with {len(session.messages)} messages"
            )
            return session
        except Exception as e:
            self.logger.error(f"Error loading session: {str(e)}")
            return None

    def load_sessions(self) -> None:
        """Load existing sessions from the database."""
        try:
            # Get all session IDs
            session_ids = self.db.get_all_sessions()
            
            # Only load a few sessions initially (to avoid memory pressure)
            # More sessions will be loaded on-demand when accessed
            for session_id in session_ids[:5]:  # Only load the 5 most recent sessions
                # This will load the session into memory
                self.get_session(session_id)
                
            self.logger.info(f"Found {len(session_ids)} sessions in database, loaded {min(5, len(session_ids))}")
        except Exception as e:
            self.logger.error(f"Error loading sessions: {str(e)}")

    def add_message(self, session_id: str, role: str, content: str) -> None:
        """Add a message to a session and save to database."""
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        try:
            # Add message to session object
            message = session.add_message(role, content)
            
            # Save to database
            self.db.save_message(
                session_id=session_id,
                role=role,
                content=content,
                timestamp=message["timestamp"]
            )
            
            self.logger.debug(f"Added {role} message to session {session_id}")
        except Exception as e:
            self.logger.error(f"Error adding message: {str(e)}")
            raise

    async def process_message_stream(self, session_id: str, message: str):
        """Process a user message and stream the assistant's response.
        
        Args:
            session_id: ID of the session to use
            message: User message to process
            
        Yields:
            Chunks of the response as they are generated
        """
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        # Add user message
        self.add_message(session_id, "user", message)

        # Process message with LLM chain
        try:
            # Get the chat history from the session
            chat_history = session.chat_history.messages

            # Prepare the input for the chain
            chain_input = {
                "question": message,
                "chat_history": chat_history,
                "cwd": self.working_dir,
            }

            # Build a streaming chain
            self.logger.debug(f"Processing streaming message for session {session_id}")
            
            # Stream the response chunks
            full_response = ""
            try:
                async for chunk in self.chain.astream(chain_input):
                    if chunk:  # Skip empty chunks
                        full_response += chunk
                        yield chunk
                
                # Add the complete assistant response to the session
                if full_response:
                    self.add_message(session_id, "assistant", full_response)
            except Exception as e:
                self.logger.error(f"Error during streaming: {str(e)}")
                error_msg = f"Error generating response: {str(e)}"
                yield error_msg
                # Add error message to session
                self.add_message(session_id, "assistant", full_response + error_msg)

        except Exception as e:
            self.logger.error(f"Chain streaming error: {str(e)}")
            # Fallback to direct LLM call if chain fails
            self.logger.info("Using fallback direct LLM call")
            
            error_response = f"Error processing message: {str(e)}"
            yield error_response
            
            # Add error message to session
            self.add_message(session_id, "assistant", error_response)

    def process_message(self, session_id: str, message: str) -> str:
        """Process a user message and return the assistant's response."""
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        # Add user message
        self.add_message(session_id, "user", message)

        # Process message with LLM chain
        try:
            # Get the chat history from the session
            chat_history = session.chat_history.messages

            # Invoke the chain
            self.logger.debug(f"Processing message for session {session_id}")
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
            self.logger.error(f"Chain execution error: {str(e)}")
            # Fallback to direct LLM call if chain fails
            self.logger.info("Using fallback direct LLM call")
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
                full_path = self.working_dir / file_path
                content = full_path.read_text(encoding="utf-8")
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

        # Keep track of file in session for reference
        if not hasattr(session, "context_files"):
            session.context_files = []
        if file_path not in session.context_files:
            session.context_files.append(file_path)
            
        # Add context as a system message with clickable link to file
        file_url = f"file://{self.working_dir}/{file_path}"
        context_message = (
            f"Additional context from file [{file_path}]({file_url}):\n```\n{content}\n```"
        )
        self.add_message(session_id, "system", context_message)
        
    def get_context_files(self, session_id: str) -> List[str]:
        """Get the list of files that have been added to a session's context."""
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
            
        if not hasattr(session, "context_files"):
            session.context_files = []
            
        return session.context_files
        
    def remove_context_file(self, session_id: str, file_path: str) -> bool:
        """Remove a file from a session's context list."""
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
            
        if not hasattr(session, "context_files"):
            session.context_files = []
            
        if file_path in session.context_files:
            session.context_files.remove(file_path)
            # Add a system message indicating the file was removed
            self.add_message(
                session_id, 
                "system", 
                f"File removed from context: {file_path}"
            )
            return True
        return False

    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        try:
            # Delete from database
            deleted = self.db.delete_session(session_id)
            
            # Remove from memory if it was there
            if session_id in self.sessions:
                del self.sessions[session_id]
                
            if deleted:
                self.logger.info(f"Deleted session: {session_id}")
            else:
                self.logger.warning(f"Session {session_id} not found for deletion")
                
            return deleted
        except Exception as e:
            self.logger.error(f"Error deleting session: {str(e)}")
            return False
            
    def get_all_session_ids(self) -> List[str]:
        """Get all session IDs from the database."""
        try:
            return self.db.get_all_sessions()
        except Exception as e:
            self.logger.error(f"Error retrieving session IDs: {str(e)}")
            return []
            
    def get_all_sessions(self) -> List[DocstraSession]:
        """Get all sessions as DocstraSession objects."""
        try:
            session_ids = self.db.get_all_sessions()
            sessions = []
            
            for session_id in session_ids:
                session = self.get_session(session_id)
                if session:
                    sessions.append(session)
                    
            return sessions
        except Exception as e:
            self.logger.error(f"Error retrieving sessions: {str(e)}")
            return []
            
    def rename_session(self, session_id: str, new_name: str) -> bool:
        """Rename a session by storing a name in its config.
        
        Args:
            session_id: ID of the session to rename
            new_name: New name for the session
            
        Returns:
            True if successful, False otherwise
        """
        try:
            session = self.get_session(session_id)
            if not session:
                return False
                
            # Add name to session config
            session.config.name = new_name
            
            # Update in database
            config_json = json.dumps({
                key: value for key, value in session.config.__dict__.items()
                if not key.startswith('_') and not callable(value)
            })
            
            # For now, just re-save the session
            self.db.save_session(session_id, session.created_at.isoformat(), config_json)
            
            self.logger.info(f"Renamed session {session_id} to '{new_name}'")
            return True
        except Exception as e:
            self.logger.error(f"Error renaming session: {str(e)}")
            return False

    def cleanup(self):
        """Clean up resources when shutting down."""
        try:
            # Close database connections
            if hasattr(self, "db"):
                self.db.close()
                
            # Clear memory caches
            self.sessions.clear()

            self.logger.info("Resources cleaned up")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {str(e)}")
