"""
Chat API Endpoints

This module handles all chat-related API endpoints including:
- Sending and receiving messages
- Managing conversation history
- WebSocket connections for real-time chat
"""

from flask import request, jsonify, current_app
from flask_socketio import emit
from ..service.agent_service import agent_service
from . import api_v1
from .. import socketio
from functools import wraps
import json
import logging

logger = logging.getLogger(__name__)

def handle_errors(f):
    """Decorator to handle errors in API endpoints."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {f.__name__}: {str(e)}", exc_info=True)
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
    return wrapper

@api_v1.route('/chat', methods=['POST'])
@handle_errors
def chat():
    """
    Handle chat messages from the client.
    
    Request Body:
        {
            "message": "User's message",
            "session_id": "optional-session-id",
            "context": {}
        }
    
    Returns:
        Response with AI's reply and metadata
    """
    data = request.get_json()
    user_message = data.get('message', '').strip()
    session_id = data.get('session_id')
    context = data.get('context', {})
    
    if not user_message:
        return jsonify({
            'status': 'error',
            'message': 'Message cannot be empty'
        }), 400
    
    try:
        # Process the message through the agent service
        response = agent_service.invoke({
            'message': user_message,
            'session_id': session_id,
            'metadata': {
                'ip': request.remote_addr,
                'user_agent': request.user_agent.string,
                **context
            }
        })
        
        return jsonify({
            'status': 'success',
            'data': response
        })
    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': 'Failed to process message',
            'error': str(e)
        }), 500

@api_v1.route('/chat/history', methods=['GET'])
@handle_errors
def get_chat_history():
    """
    Get chat history for the current user/session.
    
    Query Parameters:
        session_id: Optional session ID
        limit: Maximum number of messages to return
        
    Returns:
        List of messages in the conversation history
    """
    session_id = request.args.get('session_id')
    limit = request.args.get('limit', 50, type=int)
    
    try:
        history = agent_service.get_conversation_history(limit=limit)
        return jsonify({
            'status': 'success',
            'data': history
        })
    except Exception as e:
        logger.error(f"Error retrieving chat history: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': 'Failed to retrieve chat history',
            'error': str(e)
        }), 500

@api_v1.route('/chat/sessions', methods=['GET'])
@handle_errors
def list_sessions():
    """
    List all chat sessions for the current user.
    
    Returns:
        List of session objects with metadata
    """
    try:
        sessions = agent_service.list_sessions()
        return jsonify({
            'status': 'success',
            'data': sessions
        })
    except Exception as e:
        logger.error(f"Error listing chat sessions: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': 'Failed to list chat sessions',
            'error': str(e)
        }), 500

# WebSocket event handlers
@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection."""
    logger.info("Client connected: %s", request.sid)
    emit('connection_response', {'data': 'Connected'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection."""
    logger.info("Client disconnected: %s", request.sid)

@socketio.on('chat_message')
def handle_chat_message(data):
    """
    Handle incoming chat messages over WebSocket.
    
    Args:
        data: Dictionary containing message data
    """
    try:
        message = data.get('message', '').strip()
        session_id = data.get('session_id')
        context = data.get('context', {})
        
        if not message:
            emit('error', {'message': 'Message cannot be empty'})
            return
        
        # Process the message
        response = agent_service.invoke({
            'message': message,
            'session_id': session_id,
            'metadata': {
                'ip': request.remote_addr,
                'user_agent': request.headers.get('User-Agent', ''),
                **context
            }
        })
        
        # Send the response back to the client
        emit('chat_response', {
            'status': 'success',
            'data': response
        })
        
    except Exception as e:
        logger.error(f"Error in WebSocket chat: {str(e)}", exc_info=True)
        emit('error', {
            'status': 'error',
            'message': 'Failed to process message',
            'error': str(e)
        })
