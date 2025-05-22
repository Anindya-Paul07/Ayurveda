"""
Enhanced Metrics Service Module with Real-time Updates

This module provides comprehensive tracking and visualization capabilities with WebSocket support:
1. Real-time performance metrics (response times, tool usage, error rates)
2. Live user engagement metrics (chat interactions, session duration)
3. Conversation quality metrics with instant updates
4. System health monitoring with WebSocket push
5. Tool usage analytics with live tracking
"""

import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Set, Tuple, Callable, TYPE_CHECKING
import logging
from collections import defaultdict, deque
import json
import os
from pathlib import Path
import psutil
import threading

# Type checking imports
if TYPE_CHECKING:
    from flask import Flask
    from flask_socketio import SocketIO
from flask_socketio import SocketIO

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Type aliases
UpdateCallback = Callable[[str, Dict[str, Any]], None]  # Callback type for metrics updates

# Constants
METRICS_RETENTION_DAYS = 30  # How many days to keep detailed metrics
METRICS_AGGREGATION_INTERVAL = 3600  # 1 hour in seconds
ALERT_THRESHOLDS = {
    'error_rate': 0.05,  # 5% error rate threshold
    'response_time_p99': 5.0,  # 5 seconds P99 response time
    'cpu_usage': 0.8,  # 80% CPU usage
    'memory_usage': 0.8,  # 80% memory usage
}

class AlertManager:
    """Manages alerts and notifications."""
    
    def __init__(self):
        self.active_alerts = {}
        self.alert_history = deque(maxlen=1000)  # Keep last 1000 alerts
    
    def check_thresholds(self, metrics: Dict[str, float]) -> List[Dict[str, Any]]:
        """Check metrics against defined thresholds and trigger alerts if needed."""
        alerts = []
        current_time = datetime.utcnow()
        
        for metric, threshold in ALERT_THRESHOLDS.items():
            value = metrics.get(metric)
            if value is None:
                continue
                
            if value > threshold:
                alert_id = f"{metric}_high"
                if alert_id not in self.active_alerts:
                    alert = {
                        'id': alert_id,
                        'metric': metric,
                        'value': value,
                        'threshold': threshold,
                        'start_time': current_time,
                        'status': 'firing',
                        'severity': 'critical' if metric in ['error_rate', 'cpu_usage', 'memory_usage'] else 'warning'
                    }
                    self.active_alerts[alert_id] = alert
                    self.alert_history.append({
                        **alert,
                        'timestamp': current_time.isoformat(),
                        'type': 'fired'
                    })
                    alerts.append(alert)
            else:
                alert_id = f"{metric}_high"
                if alert_id in self.active_alerts:
                    alert = self.active_alerts.pop(alert_id)
                    alert['end_time'] = current_time
                    alert['status'] = 'resolved'
                    self.alert_history.append({
                        'id': alert_id,
                        'metric': metric,
                        'status': 'resolved',
                        'timestamp': current_time.isoformat(),
                        'type': 'resolved',
                        'duration': (current_time - alert['start_time']).total_seconds()
                    })
        
        return alerts
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get currently active alerts."""
        return list(self.active_alerts.values())
    
    def get_alert_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get alert history."""
        return list(self.alert_history)[-limit:]

class MetricsStorage:
    """Handles storage and retrieval of metrics data."""
    
    def __init__(self, storage_dir: str = "data/metrics"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_metrics_file_path(self, metric_name: str, date: datetime) -> Path:
        """Get file path for storing metrics data."""
        date_str = date.strftime("%Y-%m-%d")
        return self.storage_dir / f"{metric_name}_{date_str}.json"
    
    def save_metrics(self, metric_name: str, data: Dict[str, Any], timestamp: Optional[datetime] = None) -> None:
        """Save metrics data to storage."""
        if timestamp is None:
            timestamp = datetime.utcnow()
            
        file_path = self._get_metrics_file_path(metric_name, timestamp)
        
        # Load existing data
        existing_data = {}
        if file_path.exists():
            try:
                with open(file_path, 'r') as f:
                    existing_data = json.load(f)
            except json.JSONDecodeError:
                logger.warning(f"Corrupted metrics file: {file_path}")
        
        # Update with new data
        existing_data.update(data)
        
        # Save back to file
        with open(file_path, 'w') as f:
            json.dump(existing_data, f, indent=2)
    
    def get_metrics(self, metric_name: str, start_date: datetime, end_date: datetime) -> Dict[datetime, Any]:
        """Retrieve metrics data for a date range."""
        results = {}
        current_date = start_date.date()
        end_date = end_date.date()
        
        while current_date <= end_date:
            file_path = self._get_metrics_file_path(metric_name, current_date)
            if file_path.exists():
                try:
                    with open(file_path, 'r') as f:
                        results.update({
                            datetime.fromisoformat(k): v 
                            for k, v in json.load(f).items()
                        })
                except (json.JSONDecodeError, KeyError) as e:
                    logger.warning(f"Error reading metrics file {file_path}: {e}")
            current_date += timedelta(days=1)
        
        return results
    
    def cleanup_old_metrics(self, retention_days: int = METRICS_RETENTION_DAYS) -> None:
        """Remove metrics data older than retention_days."""
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        cutoff_date = cutoff_date.date()
        
        for file_path in self.storage_dir.glob("*.json"):
            try:
                file_date_str = file_path.stem.split('_')[-1]
                file_date = datetime.strptime(file_date_str, "%Y-%m-%d").date()
                if file_date < cutoff_date:
                    file_path.unlink()
                    logger.info(f"Removed old metrics file: {file_path}")
            except (ValueError, IndexError):
                continue

class MetricsService:
    """Service for tracking and visualizing comprehensive metrics."""
    
    def __init__(self):
        """Initialize the metrics service with enhanced tracking."""
        self.rag_metrics = {
            "total_calls": 0,
            "total_time": 0,
            "average_time": 0,
            "tool_usage": {
                "vector_store_search": 0,
                "google_search": 0
            },
            "response_times": []  # Store individual response times for detailed analysis
        }
        
        self.agent_metrics = {
            "total_calls": 0,
            "total_time": 0,
            "average_time": 0,
            "tool_usage": {
                "vector_store_search": 0,
                "google_search": 0,
                "weather": 0,
                "dosha": 0,
                "recommendations": 0
            },
            "response_times": []
        }
        
        self.user_engagement = {
            "total_interactions": 0,
            "daily_interactions": {},
            "active_users": set(),
            "conversation_length": []
        }
        
        self.disease_tracking = {
            "total_diseases_tracked": 0,
            "disease_frequency": {},
            "remedy_effectiveness": {},
            "user_disease_history": {}
        }
        
        self.recommendation_metrics = {
            "total_recommendations": 0,
            "recommendation_types": {
                "diet": 0,
                "lifestyle": 0,
                "herbs": 0,
                "exercises": 0
            },
            "user_feedback": {
                "positive": 0,
                "negative": 0,
                "neutral": 0
            }
        }
        
        self.system_health = {
            "api_response_times": [],
            "error_count": 0,
            "last_error_time": None,
            "uptime": {
                "total_uptime": 0,
                "downtime": []
            }
        }
    
    def __init__(self):
        """Initialize the metrics service."""
        self.rag_metrics = {
            "total_calls": 0,
            "total_time": 0,
            "average_time": 0,
            "tool_usage": {
                "vector_store_search": 0,
                "google_search": 0
            }
        }
        
        self.agent_metrics = {
            "total_calls": 0,
            "total_time": 0,
            "average_time": 0,
            "tool_usage": {
                "vector_store_search": 0,
                "google_search": 0,
                "weather": 0,
                "dosha": 0,
                "recommendations": 0
            }
        }
        
        self.comparison_metrics = {
            "response_times": [],  # Store individual response times for both implementations
            "tool_usage_patterns": [],  # Store tool usage patterns
            "accuracy_scores": []  # Store accuracy scores if available
        }
    
    def track_rag_request(self, response_time: float, tool_usage: Dict[str, int]):
        """
        Track metrics for a RAG chain request.
        
        Args:
            response_time: Time taken to process the request (in seconds)
            tool_usage: Dictionary of tool usage counts
        """
        with threading.Lock():
            self.rag_metrics["total_calls"] += 1
            self.rag_metrics["total_time"] += response_time
            self.rag_metrics["average_time"] = self.rag_metrics["total_time"] / self.rag_metrics["total_calls"]
            
            # Update tool usage
            for tool, count in tool_usage.items():
                if tool in self.rag_metrics["tool_usage"]:
                    self.rag_metrics["tool_usage"][tool] += count
                else:
                    self.rag_metrics["tool_usage"][tool] = count
            
            # Track response time for detailed analysis
            self.rag_metrics["response_times"].append(response_time)
            
            # Emit update for real-time dashboard
            metrics_service_manager.emit_update('performance', {
                'rag': {
                    'total_calls': self.rag_metrics["total_calls"],
                    'average_time': self.rag_metrics["average_time"],
                    'tool_usage': self.rag_metrics["tool_usage"]
                }
            })
    
    def track_agent_request(self, response_time: float, tool_usage: Dict[str, int]):
        """
        Track metrics for an agent chain request.
        
        Args:
            response_time: Time taken to process the request (in seconds)
            tool_usage: Dictionary of tool usage counts
        """
        with threading.Lock():
            self.agent_metrics["total_calls"] += 1
            self.agent_metrics["total_time"] += response_time
            self.agent_metrics["average_time"] = self.agent_metrics["total_time"] / self.agent_metrics["total_calls"]
            
            # Update tool usage
            for tool, count in tool_usage.items():
                if tool in self.agent_metrics["tool_usage"]:
                    self.agent_metrics["tool_usage"][tool] += count
                else:
                    self.agent_metrics["tool_usage"][tool] = count
            
            # Track response time for detailed analysis
            self.agent_metrics["response_times"].append(response_time)
            
            # Emit update for real-time dashboard
            metrics_service_manager.emit_update('performance', {
                'agent': {
                    'total_calls': self.agent_metrics["total_calls"],
                    'average_time': self.agent_metrics["average_time"],
                    'tool_usage': self.agent_metrics["tool_usage"]
                }
            })
    
    def track_user_interaction(self, user_id: str, interaction_type: str, duration: float):
        """
        Track user interactions for engagement metrics.
        
        Args:
            user_id: Unique identifier for the user
            interaction_type: Type of interaction (chat, disease tracking, etc.)
            duration: Duration of interaction in seconds
        """
        with threading.Lock():
            self.user_engagement["total_interactions"] += 1
            self.user_engagement["active_users"].add(user_id)
            
            # Track daily interactions
            today = datetime.now().strftime("%Y-%m-%d")
            if today in self.user_engagement["daily_interactions"]:
                self.user_engagement["daily_interactions"][today] += 1
            else:
                self.user_engagement["daily_interactions"][today] = 1
            
            # Track conversation length
            self.user_engagement["conversation_length"].append(duration)
            
            # Emit update for real-time dashboard
            metrics_service_manager.emit_update('user_engagement', {
                'total_interactions': self.user_engagement["total_interactions"],
                'active_users': len(self.user_engagement["active_users"]),
                'daily_interactions': self.user_engagement["daily_interactions"]
            })
    
    def track_disease(self, disease_name: str, user_id: str, remedy: str, effectiveness: float) -> None:
        """
        Track disease occurrences and remedy effectiveness.
        
        Args:
            disease_name: Name of the disease
            user_id: User who reported the disease
            remedy: The recommended remedy
            effectiveness: User-rated effectiveness of the remedy (0-1)
        """
        self.disease_tracking["total_diseases_tracked"] += 1
        
        # Update disease frequency
        if disease_name not in self.disease_tracking["disease_frequency"]:
            self.disease_tracking["disease_frequency"][disease_name] = 0
        self.disease_tracking["disease_frequency"][disease_name] += 1
        
        # Track remedy effectiveness
        if disease_name not in self.disease_tracking["remedy_effectiveness"]:
            self.disease_tracking["remedy_effectiveness"][disease_name] = {
                "total_ratings": 0,
                "average_effectiveness": 0
            }
        
        self.disease_tracking["remedy_effectiveness"][disease_name]["total_ratings"] += 1
        current_avg = self.disease_tracking["remedy_effectiveness"][disease_name]["average_effectiveness"]
        new_avg = (current_avg * (self.disease_tracking["remedy_effectiveness"][disease_name]["total_ratings"] - 1) + effectiveness) / self.disease_tracking["remedy_effectiveness"][disease_name]["total_ratings"]
        self.disease_tracking["remedy_effectiveness"][disease_name]["average_effectiveness"] = new_avg
        
        # Track user disease history
        if user_id not in self.disease_tracking["user_disease_history"]:
            self.disease_tracking["user_disease_history"][user_id] = []
        self.disease_tracking["user_disease_history"][user_id].append({
            "disease": disease_name,
            "remedy": remedy,
            "effectiveness": effectiveness,
            "timestamp": time.time()
        })
    
    def track_recommendation(self, recommendation_type: str, user_feedback: str) -> None:
        """
        Track recommendation metrics and user feedback.
        
        Args:
            recommendation_type: Type of recommendation (diet, lifestyle, etc.)
            user_feedback: User's feedback on the recommendation
        """
        self.recommendation_metrics["total_recommendations"] += 1
        
        # Update recommendation type counts
        if recommendation_type in self.recommendation_metrics["recommendation_types"]:
            self.recommendation_metrics["recommendation_types"][recommendation_type] += 1
        
        # Update feedback statistics
        if user_feedback in self.recommendation_metrics["user_feedback"]:
            self.recommendation_metrics["user_feedback"][user_feedback] += 1
    
    def track_system_health(self, response_time: float, error_occurred: bool = False) -> None:
        """
        Track system health metrics.
        
        Args:
            response_time: API response time in seconds
            error_occurred: Whether an error occurred during the request
        """
        self.system_health["api_response_times"].append(response_time)
        
        if error_occurred:
            self.system_health["error_count"] += 1
            self.system_health["last_error_time"] = time.time()
    
    def track_comparison(self, rag_time: float, agent_time: float, rag_tools: Dict[str, int], agent_tools: Dict[str, int]) -> None:
        """
        Track a comparison between RAG and Agent implementations.
        
        Args:
            rag_time: Response time for RAG implementation
            agent_time: Response time for Agent implementation
            rag_tools: Tool usage for RAG implementation
            agent_tools: Tool usage for Agent implementation
        """
        self.comparison_metrics["response_times"].append({
            "rag": rag_time,
            "agent": agent_time,
            "difference": abs(rag_time - agent_time)
        })
        
        self.comparison_metrics["tool_usage_patterns"].append({
            "rag": rag_tools,
            "agent": agent_tools
        })
    
    def get_aggregated_comparison(self) -> Dict[str, Any]:
        """
        Get aggregated comparison metrics.
        
        Returns:
            Dictionary containing aggregated comparison metrics
        """
        if not self.comparison_metrics["response_times"]:
            return {
                "message": "No comparison data available yet"
            }
            
        response_times = self.comparison_metrics["response_times"]
        tool_patterns = self.comparison_metrics["tool_usage_patterns"]
        
        # Calculate averages
        avg_rag_time = sum(rt["rag"] for rt in response_times) / len(response_times)
        avg_agent_time = sum(rt["agent"] for rt in response_times) / len(response_times)
        avg_difference = sum(rt["difference"] for rt in response_times) / len(response_times)
        
        return {
            "aggregated_metrics": {
                "average_response_times": {
                    "rag": avg_rag_time,
                    "agent": avg_agent_time,
                    "difference": avg_difference
                },
                "tool_usage_patterns": {
                    "rag": self._get_average_tool_usage(tool_patterns, "rag"),
                    "agent": self._get_average_tool_usage(tool_patterns, "agent")
                }
            }
        }
    
    def _get_average_tool_usage(self, tool_patterns: list, implementation: str) -> Dict[str, float]:
        """
        Calculate average tool usage for a given implementation.
        
        Args:
            tool_patterns: List of tool usage patterns
            implementation: 'rag' or 'agent'
            
        Returns:
            Dictionary of average tool usage
        """
        if not tool_patterns:
            return {}
            
        tool_sums = {}
        for pattern in tool_patterns:
            for tool, count in pattern[implementation].items():
                if tool not in tool_sums:
                    tool_sums[tool] = 0
                tool_sums[tool] += count
        
        avg_usage = {tool: count / len(tool_patterns) for tool, count in tool_sums.items()}
        return avg_usage

    def initialize(self, app: 'Flask', socketio: Optional['SocketIO'] = None) -> None:
        """Initialize the metrics service with Flask app and Socket.IO.
        
        Args:
            app: The Flask application instance
            socketio: Optional Socket.IO instance for real-time updates
        """
        try:
            # Store app reference
            self.app = app
            
            # Store socketio if provided
            if socketio:
                self._socketio = socketio
                logger.info("MetricsService initialized with Socket.IO support")
            
            # Initialize any required components
            if not hasattr(self, '_initialized') or not self._initialized:
                #self._initialize_metrics()
                #self._schedule_cleanup()
                self._initialized = True
                logger.info("MetricsService initialization complete")
            
        except Exception as e:
            logger.error(f"Error initializing MetricsService: {str(e)}")
            raise

class MetricsServiceManager:
    """Manages the MetricsService instance and WebSocket updates."""
    
    _instance = None
    _lock = threading.Lock()
    _socketio = None
    _update_callbacks = []
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._metrics_service = MetricsService()
        return cls._instance
    
    @property
    def service(self) -> 'MetricsService':
        """Get the metrics service instance."""
        return self._metrics_service
    
    def initialize(self, app, socketio: Optional[SocketIO] = None):
        """Initialize the metrics service with Flask app and Socket.IO."""
        if socketio:
            self._socketio = socketio
            logger.info("MetricsServiceManager initialized with Socket.IO support")
        
        # Register any required routes
        @app.route('/api/metrics/health')
        def health_check():
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'metrics': {
                    'total_interactions': self._metrics_service.user_engagement['total_interactions'],
                    'active_users': len(self._metrics_service.user_engagement['active_users']),
                    'error_count': self._metrics_service.system_health['error_count']
                }
            })
    
    def register_update_callback(self, callback: UpdateCallback):
        """Register a callback for metrics updates."""
        self._update_callbacks.append(callback)
    
    def emit_update(self, metric_type: str, data: Dict[str, Any]):
        """Emit a metrics update to all registered callbacks."""
        for callback in self._update_callbacks:
            try:
                callback(metric_type, data)
            except Exception as e:
                logger.error(f"Error in metrics update callback: {e}")
        
        # Also emit via Socket.IO if available
        if self._socketio:
            self._socketio.emit('metrics_update', {
                'type': metric_type,
                'data': data,
                'timestamp': time.time()
            }, namespace='/metrics')

# Initialize the metrics service manager
metrics_service_manager = MetricsServiceManager()
metrics_service = metrics_service_manager.service  # Backward compatibility
