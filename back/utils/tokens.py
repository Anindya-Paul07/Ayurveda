"""
Token Utilities

This module provides functions for generating and verifying JWT tokens.
"""

import jwt
import datetime
from functools import wraps
from flask import jsonify, request, current_app
from ..models.user import User

def generate_token(user_id, expires_in=3600, token_type='access'):
    """
    Generate a JWT token.
    
    Args:
        user_id (int): The user's ID
        expires_in (int): Token expiration time in seconds (default: 1 hour)
        token_type (str): Type of token (e.g., 'access', 'refresh', 'verify', 'reset')
        
    Returns:
        str: Encoded JWT token
    """
    payload = {
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=expires_in),
        'iat': datetime.datetime.utcnow(),
        'type': token_type
    }
    return jwt.encode(
        payload,
        current_app.config['SECRET_KEY'],
        algorithm='HS256'
    )

def verify_token(token, token_type='access'):
    """
    Verify a JWT token.
    
    Args:
        token (str): The JWT token to verify
        token_type (str): Expected token type
        
    Returns:
        tuple: (is_valid, user_id, message)
    """
    try:
        payload = jwt.decode(
            token,
            current_app.config['SECRET_KEY'],
            algorithms=['HS256']
        )
        
        # Check token type
        if payload.get('type') != token_type:
            return False, None, 'Invalid token type'
            
        # Check if user exists
        user = User.query.get(payload['user_id'])
        if not user or not user.is_active:
            return False, None, 'User not found or inactive'
            
        return True, user, 'Token is valid'
        
    except jwt.ExpiredSignatureError:
        return False, None, 'Token has expired'
    except jwt.InvalidTokenError:
        return False, None, 'Invalid token'
    except Exception as e:
        current_app.logger.error(f"Token verification error: {str(e)}")
        return False, None, 'Could not verify token'

def generate_reset_token(user_id, expires_in=3600):
    """Generate a password reset token."""
    return generate_token(user_id, expires_in, 'reset')

def verify_reset_token(token):
    """Verify a password reset token."""
    is_valid, user, message = verify_token(token, 'reset')
    if is_valid:
        return user
    return None

def generate_email_verification_token(user_id, expires_in=86400):  # 24 hours
    """Generate an email verification token."""
    return generate_token(user_id, expires_in, 'verify')

def verify_email_token(token):
    """Verify an email verification token."""
    is_valid, user, message = verify_token(token, 'verify')
    if is_valid:
        return user
    return None

def generate_refresh_token(user_id, expires_in=2592000):  # 30 days
    """Generate a refresh token."""
    return generate_token(user_id, expires_in, 'refresh')

def verify_refresh_token(token):
    """Verify a refresh token."""
    is_valid, user, message = verify_token(token, 'refresh')
    if is_valid:
        return user
    return None

def token_required(f):
    """
    Decorator to protect routes that require authentication.
    
    The token should be included in the Authorization header as:
    Authorization: Bearer <token>
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({
                'status': 'error',
                'message': 'Token is missing!'
            }), 401
            
        is_valid, user, message = verify_token(token)
        if not is_valid or not user:
            return jsonify({
                'status': 'error',
                'message': message or 'Invalid token!'
            }), 401
            
        # Add user to request context
        request.user = user
        request.user_id = user.id
        
        return f(*args, **kwargs)
    
    return decorated

def admin_required(f):
    """
    Decorator to protect routes that require admin privileges.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # First check for valid token
        token = None
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({
                'status': 'error',
                'message': 'Token is missing!'
            }), 401
            
        is_valid, user, message = verify_token(token)
        if not is_valid or not user:
            return jsonify({
                'status': 'error',
                'message': message or 'Invalid token!'
            }), 401
            
        # Then check for admin role
        if not user.is_admin:
            return jsonify({
                'status': 'error',
                'message': 'Admin privileges required!'
            }), 403
            
        # Add user to request context
        request.user = user
        request.user_id = user.id
        
        return f(*args, **kwargs)
    
    return decorated
