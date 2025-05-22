"""
Conversation Summarizer Module

This module provides functionality to summarize conversations to manage context length
and maintain important information across long conversations.
"""

from typing import List, Dict, Any, Optional
import tiktoken
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from langchain_openai import ChatOpenAI
import logging

logger = logging.getLogger(__name__)

class ConversationSummarizer:
    """Handles summarization of conversation history to manage context length."""
    
    def __init__(
        self,
        model_name: str = "gpt-3.5-turbo",
        max_tokens: int = 4000,
        summary_threshold: float = 0.7,
        summary_prompt: Optional[str] = None
    ):
        """Initialize the conversation summarizer.
        
        Args:
            model_name: Name of the language model to use for summarization
            max_tokens: Maximum number of tokens to allow before summarizing
            summary_threshold: Ratio of max_tokens at which to trigger summarization (0-1)
            summary_prompt: Optional custom prompt for summarization
        """
        self.llm = ChatOpenAI(model_name=model_name)
        self.max_tokens = max_tokens
        self.summary_threshold = summary_threshold
        self.encoder = tiktoken.encoding_for_model("gpt-3.5-turbo")
        
        self.summary_prompt = summary_prompt or """
        Please summarize the following conversation history concisely while preserving key information,
        decisions, and context. The summary should be in the third person and focus on:
        - Main topics discussed
        - Key decisions or conclusions
        - Important context for future messages
        - Any action items or follow-ups
        
        Conversation:
        {conversation}
        
        Summary:
        """
    
    def count_tokens(self, text: str) -> int:
        """Count the number of tokens in a text string."""
        return len(self.encoder.encode(text))
    
    def should_summarize(self, messages: List[Dict[str, Any]]) -> bool:
        """Determine if the conversation should be summarized based on token count."""
        total_tokens = sum(
            self.count_tokens(msg.get("content", "")) 
            for msg in messages
        )
        return total_tokens > (self.max_tokens * self.summary_threshold)
    
    def summarize_messages(
        self, 
        messages: List[Dict[str, Any]],
        user_id: str,
        session_id: str
    ) -> Dict[str, Any]:
        """Summarize a list of messages.
        
        Args:
            messages: List of message dictionaries
            user_id: ID of the user
            session_id: ID of the conversation session
            
        Returns:
            Dictionary containing the summary and metadata
        """
        try:
            # Convert messages to a conversation string
            conversation = "\n".join(
                f"{msg.get('role', 'unknown').title()}: {msg.get('content', '')}"
                for msg in messages
            )
            
            # Generate summary using the LLM
            prompt = self.summary_prompt.format(conversation=conversation)
            response = self.llm.invoke(prompt)
            summary = response.content if hasattr(response, 'content') else str(response)
            
            return {
                "content": summary,
                "metadata": {
                    "type": "summary",
                    "user_id": user_id,
                    "session_id": session_id,
                    "original_messages_count": len(messages),
                    "summary_tokens": self.count_tokens(summary)
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            # Return a basic summary if summarization fails
            return {
                "content": "[Previous conversation summarized due to length]",
                "metadata": {
                    "type": "summary_error",
                    "error": str(e)
                }
            }
    
    def process_messages(
        self,
        messages: List[Dict[str, Any]],
        user_id: str,
        session_id: str
    ) -> List[Dict[str, Any]]:
        """Process messages and summarize if necessary.
        
        Args:
            messages: List of message dictionaries
            user_id: ID of the user
            session_id: ID of the conversation session
            
        Returns:
            Processed list of messages with summaries if needed
        """
        if not self.should_summarize(messages):
            return messages
            
        # Split messages into chunks if needed for very long conversations
        chunks = self._chunk_messages(messages)
        processed_messages = []
        
        for chunk in chunks:
            if self.should_summarize(chunk):
                summary = self.summarize_messages(chunk, user_id, session_id)
                processed_messages.append(summary)
            else:
                processed_messages.extend(chunk)
                
        return processed_messages
    
    def _chunk_messages(
        self, 
        messages: List[Dict[str, Any]], 
        max_chunk_size: int = 10
    ) -> List[List[Dict[str, Any]]]:
        """Split messages into chunks for processing."""
        return [messages[i:i + max_chunk_size] for i in range(0, len(messages), max_chunk_size)]
