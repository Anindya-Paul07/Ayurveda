"""
Tool Usage Tracker

This module provides functionality to track and analyze the usage of tools in the agent service.
It records metrics such as invocation counts, success rates, and response times.
"""

import json
import logging
import time
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple, Union

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ToolUsageTracker:
    """
    Tracks and analyzes the usage of tools in the agent service.
    
    This class provides methods to record tool invocations, track metrics,
    and generate usage statistics. It can store data in memory and optionally
    persist it to disk.
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize the ToolUsageTracker with enhanced metrics.
        
        Args:
            storage_path: Optional path to a JSON file for persisting usage data.
                         If not provided, data will only be stored in memory.
        """
        self.storage_path = Path(storage_path) if storage_path else None
        self.usage_data = self._load_usage_data() if self.storage_path else {}
        self.current_session = str(int(time.time()))
        
        # Initialize metrics tracking
        self.metrics = {
            'invocations': defaultdict(int),          # Total invocations per tool
            'errors': defaultdict(int),               # Error counts per tool
            'response_times': defaultdict(list),      # Response time history
            'last_used': dict(),                      # Last usage timestamp
            'user_engagement': defaultdict(set),      # Users per tool
            'concurrent_usage': defaultdict(set)      # Tools used together
        }
        self.user_sessions = defaultdict(dict)       # User session data
        self.article_metrics = defaultdict(dict)      # Article-specific metrics
        self.last_tool_used = {}                     # For tracking tool sequences
    
    def _load_usage_data(self) -> Dict[str, Any]:
        """
        Load usage data from the storage file if it exists.
        
        Returns:
            Dict containing the loaded usage data or an empty dict if the file doesn't exist.
        """
        if not self.storage_path or not self.storage_path.exists():
            return {}
            
        try:
            with open(self.storage_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Could not load usage data: {e}")
            return {}
    
    def _save_usage_data(self) -> None:
        """Save the current usage data to the storage file if a path is configured."""
        if not self.storage_path:
            return
            
        try:
            # Ensure the directory exists
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write the data
            with open(self.storage_path, 'w') as f:
                json.dump(self.usage_data, f, indent=2, default=str)
        except IOError as e:
            logger.error(f"Could not save usage data: {e}")
    
    def log_tool_use(
        self,
        tool_name: str,
        user_id: Optional[str] = None,
        success: bool = True,
        error: Optional[str] = None,
        response_time: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log the use of a tool with enhanced tracking.
        
        Args:
            tool_name: Name of the tool being used
            user_id: Optional user ID for user-specific tracking
            success: Whether the tool execution was successful
            error: Error message if the tool execution failed
            response_time: Time taken for the tool to execute in seconds
            metadata: Additional metadata about the tool usage
        """
        timestamp = datetime.utcnow()
        
        # Update basic metrics
        self.metrics['invocations'][tool_name] += 1
        self.metrics['last_used'][tool_name] = timestamp.isoformat()
        
        if not success and error:
            self.metrics['errors'][tool_name] += 1
            logger.warning(f"Tool error ({tool_name}): {error}")
        
        if response_time is not None:
            self.metrics['response_times'][tool_name].append(response_time)
            # Keep only the last 1000 response times for performance
            self.metrics['response_times'][tool_name] = self.metrics['response_times'][tool_name][-1000:]
        
        # Track user engagement
        if user_id:
            self.metrics['user_engagement'][tool_name].add(user_id)
            
            # Initialize user session if it doesn't exist
            if user_id not in self.user_sessions:
                self.user_sessions[user_id] = {
                    'first_seen': timestamp,
                    'last_seen': timestamp,
                    'tool_usage': defaultdict(int),
                    'tool_sequences': [],
                    'session_count': 0,
                    'current_session_start': timestamp
                }
            
            # Update user session
            user_session = self.user_sessions[user_id]
            user_session['last_seen'] = timestamp
            user_session['tool_usage'][tool_name] += 1
            
            # Track tool sequences (what tools are used together)
            if user_id in self.last_tool_used and self.last_tool_used[user_id] != tool_name:
                tool_pair = tuple(sorted([self.last_tool_used[user_id], tool_name]))
                self.metrics['concurrent_usage'][tool_name].add(tool_pair[0] if tool_pair[0] != tool_name else tool_pair[1])
            
            self.last_tool_used[user_id] = tool_name
            
            # Track article interactions specifically
            if tool_name == 'article_recommender' and metadata and 'article_id' in metadata:
                article_id = metadata['article_id']
                if 'views' not in self.article_metrics[article_id]:
                    self.article_metrics[article_id] = {
                        'views': 0,
                        'likes': 0,
                        'shares': 0,
                        'saves': 0,
                        'avg_read_time': 0,
                        'last_viewed': None
                    }
                
                self.article_metrics[article_id]['views'] += 1
                self.article_metrics[article_id]['last_viewed'] = timestamp.isoformat()
                
                if metadata.get('interaction_type') == 'like':
                    self.article_metrics[article_id]['likes'] += 1
                elif metadata.get('interaction_type') == 'share':
                    self.article_metrics[article_id]['shares'] += 1
                elif metadata.get('interaction_type') == 'save':
                    self.article_metrics[article_id]['saves'] += 1
                
                if 'read_time_seconds' in metadata:
                    current_avg = self.article_metrics[article_id]['avg_read_time']
                    total_views = self.article_metrics[article_id]['views']
                    self.article_metrics[article_id]['avg_read_time'] = (
                        (current_avg * (total_views - 1) + metadata['read_time_seconds']) / total_views
                    )
    
    def get_tool_metrics(self, tool_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get detailed metrics for a specific tool or all tools.
        
        Args:
            tool_name: Optional name of the tool to get metrics for
            
        Returns:
            Dictionary containing tool metrics
        """
        if tool_name:
            if tool_name not in self.metrics['invocations']:
                return {}
                
            response_times = self.metrics['response_times'][tool_name]
            return {
                'invocations': self.metrics['invocations'][tool_name],
                'errors': self.metrics['errors'][tool_name],
                'error_rate': (
                    self.metrics['errors'][tool_name] / 
                    max(1, self.metrics['invocations'][tool_name])
                ),
                'avg_response_time': (
                    sum(response_times) / len(response_times)
                ) if response_times else 0,
                'p95_response_time': (
                    sorted(response_times)[int(len(response_times) * 0.95)]
                ) if response_times else 0,
                'unique_users': len(self.metrics['user_engagement'][tool_name]),
                'frequently_used_with': list(
                    self.metrics['concurrent_usage'][tool_name]
                )[:10],  # Top 10 tools used with this one
                'last_used': self.metrics['last_used'].get(tool_name)
            }
        
        # Return metrics for all tools
        return {
            tool: self.get_tool_metrics(tool)
            for tool in self.metrics['invocations']
        }
    
    def get_article_metrics(self, article_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get metrics for article interactions.
        
        Args:
            article_id: Optional article ID to filter by
            
        Returns:
            Dictionary containing article metrics
        """
        if article_id:
            return self.article_metrics.get(article_id, {})
        return dict(self.article_metrics)
    
    def get_user_engagement(
        self, 
        user_id: Optional[str] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get user engagement metrics.
        
        Args:
            user_id: Optional user ID to filter by
            days: Number of days of data to include
            
        Returns:
            Dictionary containing user engagement data
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        if user_id:
            if user_id not in self.user_sessions:
                return {}
                
            user_data = self.user_sessions[user_id]
            if user_data['last_seen'] < cutoff_date:
                return {}
                
            return {
                'user_id': user_id,
                'first_seen': user_data['first_seen'].isoformat(),
                'last_seen': user_data['last_seen'].isoformat(),
                'total_sessions': user_data['session_count'] + 1,
                'current_session_duration': (
                    datetime.utcnow() - user_data['current_session_start']
                ).total_seconds() if 'current_session_start' in user_data else 0,
                'tool_usage': dict(user_data['tool_usage']),
                'favorite_tool': (
                    max(user_data['tool_usage'].items(), key=lambda x: x[1])[0]
                    if user_data['tool_usage'] else None
                )
            }
        
        # Return data for all active users
        return {
            user_id: self.get_user_engagement(user_id, days)
            for user_id, data in self.user_sessions.items()
            if data['last_seen'] >= cutoff_date
        }
    
    def log_article_interaction(
        self, 
        user_id: str, 
        article_id: str, 
        interaction_type: str, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log a user's interaction with an article.
        
        Args:
            user_id: ID of the user
            article_id: ID of the article
            interaction_type: Type of interaction (view, like, share, save)
            metadata: Additional metadata about the interaction
        """
        self.log_tool_use(
            tool_name='article_recommender',
            user_id=user_id,
            metadata={
                'article_id': article_id,
                'interaction_type': interaction_type,
                **(metadata or {})
            }
        )
        
        logger.info(
            f"Article interaction: user={user_id}, article={article_id}, "
            f"type={interaction_type}"
        )
    
    def get_article_recommendations(
        self, 
        user_id: str, 
        limit: int = 5,
        exclude_viewed: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Generate article recommendations for a user.
        
        Args:
            user_id: ID of the user
            limit: Maximum number of recommendations to return
            exclude_viewed: Whether to exclude previously viewed articles
            
        Returns:
            List of recommended articles with scores
        """
        # Get user's viewed articles
        viewed_articles = set()
        if user_id in self.user_sessions and exclude_viewed:
            viewed_articles = {
                meta['article_id']
                for tool_use in self.user_sessions[user_id].get('tool_usage', {})
                if tool_use == 'article_recommender' and 'article_id' in tool_use.get('metadata', {})
            }
        
        # Simple popularity-based recommendation
        # In production, this would use collaborative filtering or content-based filtering
        article_scores = []
        for article_id, metrics in self.article_metrics.items():
            if article_id in viewed_articles:
                continue
                
            # Calculate a simple popularity score
            score = (
                metrics.get('likes', 0) * 2 +
                metrics.get('shares', 0) * 3 +
                metrics.get('saves', 0) * 2.5 +
                min(metrics.get('views', 0) / 10, 10)  # Cap view contribution
            )
            
            # Apply time decay (older articles get lower scores)
            if 'last_viewed' in metrics:
                days_old = (datetime.utcnow() - datetime.fromisoformat(metrics['last_viewed'])).days
                score *= 0.95 ** days_old
            
            article_scores.append((article_id, score))
        
        # Sort by score and return top N
        return [
            {'article_id': article_id, 'score': score}
            for article_id, score in sorted(article_scores, key=lambda x: x[1], reverse=True)[:limit]
        ]
    
    def export_usage_data(self, output_format: str = 'json') -> Union[str, Dict[str, Any]]:
        """
        Export the usage data in the specified format.
        
        Args:
            output_format: The output format ('json' or 'dict').
            
        Returns:
            The usage data in the requested format.
            
        Raises:
            ValueError: If an unsupported format is specified.
        """
        if output_format == 'json':
            return json.dumps(self.usage_data, indent=2)
        elif output_format == 'dict':
            return self.usage_data.copy()
        else:
            raise ValueError(f"Unsupported output format: {output_format}")


# Create a default instance for easy importing
default_tracker = ToolUsageTracker()
