"""
Context Manager for maintaining and utilizing conversation context.

This module provides functionality to manage conversation context, including:
- Tracking conversation history
- Managing context window size
- Extracting relevant context for responses
- Handling follow-up questions and references
"""

import re
from typing import List, Dict, Any, Optional, Tuple
import tiktoken
from datetime import datetime, timedelta

from langchain.schema import BaseMessage, HumanMessage, AIMessage, SystemMessage


class ContextManager:
    """Manages conversation context for generating context-aware responses."""
    
    def __init__(
        self,
        max_tokens: int = 4000,
        max_messages: int = 20,
        min_recent_messages: int = 3,
        context_decay: float = 0.9,
        model_name: str = "gpt-3.5-turbo"
    ):
        """Initialize the context manager.
        
        Args:
            max_tokens: Maximum number of tokens to keep in context window
            max_messages: Maximum number of messages to keep in history
            min_recent_messages: Minimum number of recent messages to always keep
            context_decay: Decay factor for older messages' importance (0-1)
            model_name: Name of the model being used (for token counting)
        """
        self.max_tokens = max_tokens
        self.max_messages = max_messages
        self.min_recent_messages = min_recent_messages
        self.context_decay = context_decay
        self.encoder = tiktoken.encoding_for_model(model_name)
        self.conversation_history: List[Dict[str, Any]] = []
        self.context_summary: str = ""
        
    def add_message(self, role: str, content: str, **metadata) -> None:
        """Add a message to the conversation history.
        
        Args:
            role: 'user', 'assistant', or 'system'
            content: The message content
            **metadata: Additional metadata to store with the message
        """
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.utcnow().isoformat(),
            'tokens': self._count_tokens(content),
            'metadata': metadata or {}
        }
        self.conversation_history.append(message)
        self._prune_history()
    
    def get_context(self, include_recent: bool = True, include_summary: bool = True) -> List[Dict[str, Any]]:
        """Get the most relevant context for generating a response.
        
        Args:
            include_recent: Whether to include recent messages
            include_summary: Whether to include the conversation summary
            
        Returns:
            List of message dictionaries with context information
        """
        context = []
        
        # Always include system messages if present
        system_messages = [
            msg for msg in self.conversation_history 
            if msg['role'] == 'system'
        ]
        context.extend(system_messages)
        
        # Include conversation summary if available
        if include_summary and self.context_summary:
            context.append({
                'role': 'system',
                'content': f'Conversation summary: {self.context_summary}',
                'is_summary': True
            })
        
        # Include recent messages if requested
        if include_recent:
            recent_messages = self._get_recent_messages()
            context.extend(recent_messages)
        
        return context
    
    def update_summary(self, summary: str) -> None:
        """Update the conversation summary.
        
        Args:
            summary: New summary of the conversation
        """
        self.context_summary = summary
    
    def handle_follow_up(self, message: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Check if the message is a follow-up to a previous message.
        
        Args:
            message: The user's message
            
        Returns:
            Tuple of (is_follow_up, referenced_message)
        """
        # Check for explicit references (e.g., "about that", "as you mentioned")
        reference_phrases = [
            'as you mentioned', 'you said', 'earlier you said',
            'about that', 'regarding', 'you mentioned'
        ]
        
        if any(phrase in message.lower() for phrase in reference_phrases):
            # Return the most recent message that's not the current one
            for msg in reversed(self.conversation_history[:-1]):
                if msg['role'] in ['assistant', 'user']:
                    return True, msg
        
        # Check for pronoun references (e.g., "it", "that", "this")
        pronoun_pattern = r'\b(it|that|this|they|them|those|these)\b'
        if re.search(pronoun_pattern, message, re.IGNORECASE):
            # Return the most recent non-system message
            for msg in reversed(self.conversation_history):
                if msg['role'] in ['assistant', 'user']:
                    return True, msg
        
        return False, None
    
    def _get_recent_messages(self, n: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get the most recent messages, up to n or self.max_messages."""
        n = n or self.max_messages
        return self.conversation_history[-min(n, len(self.conversation_history)):]
    
    def _prune_history(self) -> None:
        """Prune the conversation history to stay within token limits."""
        # First, ensure we don't exceed max_messages
        if len(self.conversation_history) > self.max_messages:
            # Always keep system messages and recent messages
            system_msgs = [m for m in self.conversation_history if m['role'] == 'system']
            recent_msgs = self.conversation_history[-self.min_recent_messages:]
            other_msgs = [
                m for m in self.conversation_history 
                if m not in system_msgs and m not in recent_msgs
            ]
            
            # Apply decay factor to older messages' importance
            other_msgs = sorted(
                other_msgs,
                key=lambda x: x.get('timestamp', ''),
                reverse=True
            )
            
            # Keep the most important messages
            keep_count = min(
                len(other_msgs),
                max(0, self.max_messages - len(system_msgs) - self.min_recent_messages)
            )
            
            # Rebuild conversation history
            self.conversation_history = system_msgs + other_msgs[:keep_count] + recent_msgs
        
        # Then ensure we don't exceed max_tokens
        total_tokens = sum(m.get('tokens', 0) for m in self.conversation_history)
        while total_tokens > self.max_tokens and len(self.conversation_history) > 1:
            # Remove the oldest non-system message that's not in the recent messages
            for i, msg in enumerate(self.conversation_history):
                if msg['role'] != 'system' and i < len(self.conversation_history) - self.min_recent_messages:
                    total_tokens -= msg.get('tokens', 0)
                    self.conversation_history.pop(i)
                    break
            else:
                # If we can't remove any more messages without violating constraints, break
                break
    
    def _count_tokens(self, text: str) -> int:
        """Count the number of tokens in a text string."""
        return len(self.encoder.encode(text)) if text else 0
    
    def clear(self) -> None:
        """Clear the conversation history and summary."""
        self.conversation_history = []
        self.context_summary = ""
