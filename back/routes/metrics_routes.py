"""
Metrics Routes and WebSocket Handlers

This module defines routes and WebSocket handlers for real-time metrics visualization and tracking.
"""

from flask import Blueprint, jsonify, request, current_app
from flask_socketio import emit, join_room, leave_room, SocketIO
from service.metrics_service import metrics_service
from datetime import datetime
import json
import time
from threading import Lock

# SocketIO instance will be set by the app
socketio = None

# Initialize Blueprint
metrics_bp = Blueprint('metrics', __name__, url_prefix='/api/metrics')

# Thread-safe metrics update lock
metrics_lock = Lock()

# Active WebSocket clients
active_clients = set()

# Track last update times for each metric type
last_updates = {
    'user_engagement': 0,
    'disease_tracking': 0,
    'recommendations': 0,
    'system_health': 0
}

def emit_metrics_update(metric_type, data):
    """Emit metrics update to all connected clients."""
    with metrics_lock:
        current_time = time.time()
        # Only emit if data has changed since last update
        if current_time - last_updates[metric_type] > 1.0:  # 1 second debounce
            last_updates[metric_type] = current_time
            socketio.emit('metrics_update', {
                'type': metric_type,
                'data': data,
                'timestamp': datetime.utcnow().isoformat()
            }, namespace='/metrics')

def init_metrics_routes(socketio_instance):
    """
    Initialize metrics routes and WebSocket handlers.
    
    Args:
        socketio_instance: The Socket.IO instance to use
    """
    global socketio
    socketio = socketio_instance
    
    # WebSocket event handlers
    @socketio.on('connect', namespace='/metrics')
    def on_connect():
        """Handle new WebSocket connection."""
        client_id = request.sid
        active_clients.add(client_id)
        logger.info(f"Client connected: {client_id}")
        
        # Send initial data to the newly connected client
        emit('metrics_update', {
            'type': 'initial',
            'data': {
                'user_engagement': metrics_service.user_engagement,
                'disease_tracking': metrics_service.disease_tracking,
                'recommendations': metrics_service.recommendation_metrics,
                'system_health': metrics_service.system_health
            }
        }, room=client_id)
        return {'status': 'connected'}

    @socketio.on('disconnect', namespace='/metrics')
    def on_disconnect():
        """Handle WebSocket disconnection."""
        client_id = request.sid
        if client_id in active_clients:
            active_clients.remove(client_id)
        logger.info(f"Client disconnected: {client_id}")
        return {'status': 'disconnected'}
        
    # Background task to push updates
    def background_metrics_update():
        """Background task to push metrics updates to clients."""
        while True:
            try:
                current_time = time.time()
                
                # Check if we have any clients connected
                if not active_clients:
                    time.sleep(1)
                    continue
                    
                # Update user engagement metrics (every 5 seconds)
                if current_time - last_updates['user_engagement'] > 5:
                    last_updates['user_engagement'] = current_time
                    emit_metrics_update('user_engagement', metrics_service.user_engagement)
                
                # Update disease tracking (every 10 seconds)
                if current_time - last_updates['disease_tracking'] > 10:
                    last_updates['disease_tracking'] = current_time
                    emit_metrics_update('disease_tracking', metrics_service.disease_tracking)
                
                # Update recommendations (every 15 seconds)
                if current_time - last_updates['recommendations'] > 15:
                    last_updates['recommendations'] = current_time
                    emit_metrics_update('recommendations', metrics_service.recommendation_metrics)
                
                # Update system health (every 5 seconds)
                if current_time - last_updates['system_health'] > 5:
                    last_updates['system_health'] = current_time
                    emit_metrics_update('system_health', metrics_service.system_health)
                
                # Small sleep to prevent high CPU usage
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error in background metrics update: {e}")
                time.sleep(5)  # Wait longer on error
    
    # Start the background task in a separate thread
    import threading
    threading.Thread(target=background_metrics_update, daemon=True).start()
    
    return metrics_bp

@metrics_bp.route('/visualization', methods=['GET'])
def get_metrics_visualization():
    """
    Get comprehensive visualization data for all metrics.
    
    Returns:
        JSON response with visualization data
    """
    return jsonify(metrics_service.get_visualization_data())

@metrics_bp.route('/user-engagement', methods=['GET'])
def get_user_engagement():
    """
    Get user engagement metrics.
    
    Returns:
        JSON response with user engagement data
    """
    return jsonify({
        "total_interactions": metrics_service.user_engagement["total_interactions"],
        "active_users": len(metrics_service.user_engagement["active_users"]),
        "daily_interactions": metrics_service.user_engagement["daily_interactions"]
    })

@metrics_bp.route('/disease-tracking', methods=['GET'])
def get_disease_tracking():
    """
    Get disease tracking metrics.
    
    Returns:
        JSON response with disease tracking data
    """
    return jsonify({
        "disease_frequency": metrics_service.disease_tracking["disease_frequency"],
        "remedy_effectiveness": metrics_service.disease_tracking["remedy_effectiveness"]
    })

@metrics_bp.route('/recommendations', methods=['GET'])
def get_recommendation_metrics():
    """
    Get recommendation metrics.
    
    Returns:
        JSON response with recommendation metrics
    """
    return jsonify({
        "recommendation_types": metrics_service.recommendation_metrics["recommendation_types"],
        "user_feedback": metrics_service.recommendation_metrics["user_feedback"]
    })

@metrics_bp.route('/system-health', methods=['GET'])
def get_system_health():
    """
    Get system health metrics.
    
    Returns:
        JSON response with system health data
    """
    return jsonify({
        "api_response_times": metrics_service.system_health["api_response_times"],
        "error_count": metrics_service.system_health["error_count"],
        "uptime": metrics_service.system_health["uptime"]
    })