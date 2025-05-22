"""
Enhanced conversation memory with persistence and context management.

This module provides an enhanced conversation memory implementation that extends
LangChain's ConversationBufferMemory with additional features like persistence,
context window management, summarization, and metadata support.
"""

import json
import os
import logging
from typing import Dict, List, Any, Optional, Union, Tuple, Any
from datetime import datetime
from pathlib import Path

from langchain.memory import ConversationBufferMemory
from langchain.schema import BaseMessage, HumanMessage, AIMessage, SystemMessage
from pydantic import BaseModel, Field, PrivateAttr

# Import the summarizer
from .conversation_summarizer import ConversationSummarizer

logger = logging.getLogger(__name__)


class MessageMetadata(BaseModel):
    """Metadata for a conversation message."""
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    message_id: str = Field(default_factory=lambda: str(hash(datetime.utcnow())))
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_results: Optional[List[Dict[str, Any]]] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    custom_metadata: Dict[str, Any] = Field(default_factory=dict)


class ConversationMemory(ConversationBufferMemory):
    """Enhanced conversation memory with persistence and context management.
    
    This class extends LangChain's ConversationBufferMemory with:
    - Persistent storage to disk
    - Context window management
    - Metadata support for messages
    - Conversation history retrieval
    - Automatic pruning of old messages
    """
    
    # Define Pydantic model fields
    user_id: str = "default_user"
    session_id: str = ""
    persist_dir: Optional[Path] = None
    max_messages: int = 20
    max_tokens: Optional[int] = 4000
    enable_summarization: bool = True
    
    # Private attributes (not part of the model schema)
    _summarizer: Any = PrivateAttr(default=None)
    _history_file: Optional[Path] = PrivateAttr(default=None)
    _metadata_store: List[Dict[str, Any]] = PrivateAttr(default_factory=list)
    
    @property
    def summarizer(self) -> Any:
        return self._summarizer
        
    @summarizer.setter
    def summarizer(self, value: Any) -> None:
        self._summarizer = value
        
    @property
    def history_file(self) -> Optional[Path]:
        return self._history_file
        
    @history_file.setter
    def history_file(self, value: Optional[Path]) -> None:
        self._history_file = value
        
    @property
    def metadata_store(self) -> List[Dict[str, Any]]:
        return self._metadata_store
        
    @metadata_store.setter
    def metadata_store(self, value: List[Dict[str, Any]]) -> None:
        self._metadata_store = value
    
    def __init__(
        self,
        user_id: str = "default_user",
        session_id: Optional[str] = None,
        persist_dir: Optional[Union[str, Path]] = None,
        max_messages: int = 20,
        max_tokens: Optional[int] = 4000,
        enable_summarization: bool = True,
        summarizer_kwargs: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """Initialize the conversation memory.
        
        Args:
            user_id: ID of the user
            session_id: Optional session ID. If not provided, one will be generated.
            persist_dir: Directory to persist conversation history.
            max_messages: Maximum number of messages to keep in memory.
            max_tokens: Maximum number of tokens to keep in context window.
            enable_summarization: Whether to enable conversation summarization.
            summarizer_kwargs: Additional arguments for the ConversationSummarizer.
            **kwargs: Additional arguments for the parent class.
        """
        # Process persist_dir before passing to parent
        persist_path = Path(persist_dir) if persist_dir else None
        
        # Generate session_id if not provided
        session_id = session_id or f"session_{int(datetime.now().timestamp())}"
        
        # Initialize parent class first
        super().__init__(**kwargs)
        
        # Set model fields
        self.user_id = user_id
        self.session_id = session_id
        self.persist_dir = persist_path
        self.max_messages = max_messages
        self.max_tokens = max_tokens
        self.enable_summarization = enable_summarization
        
        # Initialize summarizer if enabled
        if self.enable_summarization:
            summarizer_kwargs = summarizer_kwargs or {}
            if 'max_tokens' not in summarizer_kwargs and self.max_tokens:
                summarizer_kwargs['max_tokens'] = self.max_tokens
            self.summarizer = ConversationSummarizer(**summarizer_kwargs)
        
        # Create persist directory if it doesn't exist
        if self.persist_dir:
            self.persist_dir.mkdir(parents=True, exist_ok=True)
            self.history_file = self.persist_dir / "history.json"
        
        # Initialize metadata store
        self.metadata_store = []
        
        # Load existing history if it exists
        self._load_history()
    
    def _load_history(self) -> None:
        """Load conversation history from disk."""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.chat_memory.messages = [
                        self._deserialize_message(msg) for msg in data.get('messages', [])
                    ]
                    self.metadata_store = [
                        MessageMetadata(**meta) for meta in data.get('metadata', [])
                    ]
            except Exception as e:
                print(f"Error loading conversation history: {e}")
    
    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, Any]) -> None:
        """Save context from this conversation to buffer.
        
        Args:
            inputs: Dictionary of inputs (typically contains 'input' key)
            outputs: Dictionary of outputs (typically contains 'output' key)
        """
        # Call parent to save the basic context
        super().save_context(inputs, outputs)
        
        # Update metadata
        human_message = inputs.get(self.input_key, "")
        ai_message = outputs.get(self.output_key, "")
        
        # Add metadata for human message
        if human_message:
            self.metadata_store.append(
                MessageMetadata(
                    user_id=self.user_id,
                    session_id=self.session_id,
                    tool_calls=None,
                    tool_results=None,
                    custom_metadata={"role": "human"}
                )
            )
        
        # Add metadata for AI message
        if ai_message:
            self.metadata_store.append(
                MessageMetadata(
                    user_id=self.user_id,
                    session_id=self.session_id,
                    tool_calls=outputs.get('tool_calls'),
                    tool_results=outputs.get('tool_results'),
                    custom_metadata={"role": "ai"}
                )
            )
        
        # Process for summarization if enabled
        if self.enable_summarization and self.summarizer:
            self._process_for_summarization()
        
        # Prune if needed
        self._prune_messages()
        
        # Persist to disk if configured
        self._persist()
    
    def _prune_messages(self) -> None:
        """Prune messages if we exceed the maximum number of messages or tokens."""
        # Prune by message count
        if len(self.chat_memory.messages) > self.max_messages:
            excess = len(self.chat_memory.messages) - self.max_messages
            self.chat_memory.messages = self.chat_memory.messages[excess:]
            self.metadata_store = self.metadata_store[excess:]
        
        # Prune by token count if tokenizer is available
        if self.max_tokens:
            try:
                from transformers import AutoTokenizer
                tokenizer = AutoTokenizer.from_pretrained("gpt2")
                
                while True:
                    total_tokens = sum(
                        len(tokenizer.encode(msg.content))
                        for msg in self.chat_memory.messages
                    )
                    
                    if total_tokens <= self.max_tokens or len(self.chat_memory.messages) <= 1:
                        break
                        
                    # Remove the oldest message pair
                    self.chat_memory.messages = self.chat_memory.messages[2:]
                    self.metadata_store = self.metadata_store[2:]
            except ImportError:
                pass  # Skip token-based pruning if transformers not available
    
    def _persist(self) -> None:
        """Persist the conversation history to disk."""
        try:
            data = {
                'messages': [
                    self._serialize_message(msg) 
                    for msg in self.chat_memory.messages
                ],
                'metadata': [meta.dict() for meta in self.metadata_store]
            }
            
            # Write to a temporary file first, then rename to avoid corruption
            temp_file = self.history_file.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # On POSIX systems, this is atomic
            temp_file.replace(self.history_file)
            
        except Exception as e:
            print(f"Error persisting conversation history: {e}")
    
    @staticmethod
    def _serialize_message(message: BaseMessage) -> Dict[str, Any]:
        """Serialize a message to a dictionary."""
        return {
            'type': message.__class__.__name__,
            'content': message.content,
            'additional_kwargs': message.additional_kwargs
        }
    
    @classmethod
    def _deserialize_message(cls, data: Dict[str, Any]) -> BaseMessage:
        """Deserialize a message from a dictionary."""
        msg_type = data.get('type', 'HumanMessage')
        content = data.get('content', '')
        additional_kwargs = data.get('additional_kwargs', {})
        
        if msg_type == 'HumanMessage':
            return HumanMessage(content=content, additional_kwargs=additional_kwargs)
        elif msg_type == 'AIMessage':
            return AIMessage(content=content, additional_kwargs=additional_kwargs)
        elif msg_type == 'SystemMessage':
            return SystemMessage(content=content, additional_kwargs=additional_kwargs)
        else:
            return BaseMessage(content=content, additional_kwargs=additional_kwargs)
    
    def get_conversation_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get the conversation history with metadata.
        
        Args:
            limit: Maximum number of messages to return (default: all)
            
        Returns:
            List of message dictionaries with content and metadata
        """
        messages = self.chat_memory.messages
        metadata_list = self.metadata_store
        
        if limit is not None:
            messages = messages[-limit:]
            metadata_list = metadata_list[-limit:]
        
        return [
            {
                'content': msg.content,
                'type': msg.__class__.__name__,
                'metadata': meta.dict() if meta else {}
            }
            for msg, meta in zip(messages, metadata_list)
        ]
    
    def _process_for_summarization(self) -> None:
        """Process messages for summarization if needed."""
        if not self.enable_summarization or not self.summarizer:
            return
            
        try:
            # Get current messages
            messages = self.get_messages()
            
            # Convert to dict format for summarizer
            messages_dict = [
                {
                    "role": "user" if isinstance(msg, HumanMessage) else "assistant" if isinstance(msg, AIMessage) else "system",
                    "content": msg.content,
                    "metadata": getattr(msg, "metadata", {})
                }
                for msg in messages
            ]
            
            # Process messages with summarizer
            processed_messages = self.summarizer.process_messages(
                messages_dict,
                user_id=self.user_id,
                session_id=self.session_id
            )
            
            # If summarization occurred, update the chat memory
            if len(processed_messages) < len(messages_dict):
                self.clear()
                for msg in processed_messages:
                    if msg.get("metadata", {}).get("type") == "summary":
                        self.chat_memory.add_ai_message(
                            content=msg["content"],
                            metadata=msg.get("metadata", {})
                        )
                    else:
                        role = msg.get("role", "user")
                        if role == "user":
                            self.chat_memory.add_user_message(
                                content=msg["content"],
                                metadata=msg.get("metadata", {})
                            )
                        else:
                            self.chat_memory.add_ai_message(
                                content=msg["content"],
                                metadata=msg.get("metadata", {})
                            )
                
                logger.info(f"Conversation summarized from {len(messages_dict)} to {len(processed_messages)} messages")
                
        except Exception as e:
            logger.error(f"Error during conversation summarization: {str(e)}")
            # Continue without summarization if there's an error
    
    def get_messages(self) -> List[BaseMessage]:
        """Get all messages in the conversation."""
        return self.chat_memory.messages if hasattr(self, 'chat_memory') else []
    
    def clear(self) -> None:
        """Clear memory contents."""
        super().clear()
        self.metadata_store = []
        self._persist()
