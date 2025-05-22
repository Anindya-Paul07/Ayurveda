"""
Authentication API Endpoints

This module handles all authentication and user management endpoints including:
- User registration and login
- Password reset
- Email verification
- Profile management
"""

from flask import request, jsonify, current_app, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
import re
from functools import wraps
import logging
from ..models.user import User
from ..extensions import db
from . import api_v1
from ..utils.email import send_email
from ..utils.password import validate_password_strength

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

def token_required(f):
    """Decorator to require a valid JWT token for protected routes."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check for token in Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({
                'status': 'error',
                'message': 'Token is missing'
            }), 401
            
        try:
            # Decode the token
            data = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256']
            )
            
            # Get user from database
            current_user = User.query.get(data['user_id'])
            if not current_user:
                raise Exception('User not found')
                
            # Add user to request context
            request.user = current_user
            request.user_id = current_user.id
            
        except jwt.ExpiredSignatureError:
            return jsonify({
                'status': 'error',
                'message': 'Token has expired. Please log in again.'
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                'status': 'error',
                'message': 'Invalid token. Please log in again.'
            }), 401
        except Exception as e:
            logger.error(f"Token validation error: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': 'Could not validate token. Please log in again.'
            }), 401
            
        return f(*args, **kwargs)
    return decorated

@api_v1.route('/auth/register', methods=['POST'])
@handle_errors
def register():
    """
    Register a new user.
    
    Request Body:
        {
            "username": "user123",
            "email": "user@example.com",
            "password": "SecurePassword123!",
            "first_name": "John",
            "last_name": "Doe"
        }
        
    Returns:
        User data and JWT token on success
    """
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['username', 'email', 'password']
    if not all(field in data for field in required_fields):
        return jsonify({
            'status': 'error',
            'message': 'Missing required fields: username, email, and password are required'
        }), 400
    
    # Validate email format
    if not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', data['email']):
        return jsonify({
            'status': 'error',
            'message': 'Invalid email format'
        }), 400
    
    # Validate password strength
    is_valid, message = validate_password_strength(data['password'])
    if not is_valid:
        return jsonify({
            'status': 'error',
            'message': f'Password validation failed: {message}'
        }), 400
    
    # Check if username or email already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({
            'status': 'error',
            'message': 'Username already exists'
        }), 409
        
    if User.query.filter_by(email=data['email']).first():
        return jsonify({
            'status': 'error',
            'message': 'Email already registered'
        }), 409
    
    try:
        # Create new user
        user = User(
            username=data['username'],
            email=data['email'],
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            password=data['password']  # Password hashing is handled in the setter
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Generate tokens
        access_token = user.generate_auth_token(expires_in=3600)  # 1 hour
        refresh_token = user.generate_auth_token(expires_in=2592000, token_type='refresh')  # 30 days
        
        # Send welcome and verification emails
        if current_app.config.get('SEND_WELCOME_EMAIL', True):
            send_email(
                to=user.email,
                subject='Welcome to Our App!',
                template='welcome_email.html',
                username=user.username
            )
        
        if current_app.config.get('EMAIL_VERIFICATION_REQUIRED', True):
            verification_token = user.generate_email_verification_token()
            verification_url = f"{current_app.config['FRONTEND_URL']}/verify-email?token={verification_token}"
            send_email(
                to=user.email,
                subject='Verify Your Email',
                template='verify_email.html',
                username=user.username,
                verification_url=verification_url
            )
        
        response_data = {
            'status': 'success',
            'message': 'User registered successfully. Please check your email to verify your account.',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict(),
            'requires_verification': current_app.config.get('EMAIL_VERIFICATION_REQUIRED', True)
        }
        
        return jsonify(response_data), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error during registration: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': 'Failed to register user',
            'error': str(e)
        }), 500

@api_v1.route('/auth/login', methods=['POST'])
@handle_errors
def login():
    """
    Authenticate a user and return access and refresh tokens.
    
    Request Body:
        {
            "email_or_username": "user@example.com",
            "password": "SecurePassword123!"
        }
        
    Returns:
        Access token, refresh token, and user data on success
    """
    data = request.get_json()
    
    # Validate required fields
    if not data.get('email_or_username') or not data.get('password'):
        return jsonify({
            'status': 'error',
            'message': 'Email/username and password are required'
        }), 400
    
    try:
        # Find user by email or username
        user = User.query.filter(
            (User.email == data['email_or_username']) | 
            (User.username == data['email_or_username'])
        ).first()
        
        # Check if user exists and password is correct
        if not user or not user.verify_password(data['password']):
            return jsonify({
                'status': 'error',
                'message': 'Invalid email/username or password'
            }), 401
        
        # Check if account is active
        if not user.is_active:
            return jsonify({
                'status': 'error',
                'message': 'Account is deactivated. Please contact support.'
            }), 403
        
        # Check if email verification is required and email is not verified
        if current_app.config.get('EMAIL_VERIFICATION_REQUIRED', True) and not user.is_verified:
            return jsonify({
                'status': 'error',
                'message': 'Please verify your email before logging in',
                'requires_verification': True,
                'resend_verification': True
            }), 403
        
        # Update login info
        user.update_login_info(request.remote_addr)
        
        # Generate tokens
        access_token = user.generate_auth_token(expires_in=3600)  # 1 hour
        refresh_token = user.generate_auth_token(expires_in=2592000, token_type='refresh')  # 30 days
        
        # Commit any changes to the database (like login count update)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Login successful',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error during login: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': 'Failed to log in. Please try again.'
        }), 500

@api_v1.route('/auth/verify-email', methods=['POST'])
@handle_errors
def verify_email():
    """
    Verify a user's email address using a verification token.
    
    Request Query Parameters:
        token (str): The verification token sent to the user's email
        
    Returns:
        Success message and user data if verification is successful
    """
    # Get token from query parameters or JSON body
    token = request.args.get('token') or request.json.get('token') if request.json else None
    
    if not token:
        return jsonify({
            'status': 'error',
            'message': 'Verification token is required'
        }), 400
    
    try:
        # Find user by token
        user = User.query.filter_by(email_verification_token=token).first()
        
        if not user:
            return jsonify({
                'status': 'error',
                'message': 'Invalid or expired verification token'
            }), 400
        
        # Check if already verified
        if user.is_verified:
            return jsonify({
                'status': 'success',
                'message': 'Email already verified',
                'user': user.to_dict()
            })
        
        # Verify the token
        if not user.verify_token(token, 'verify'):
            return jsonify({
                'status': 'error',
                'message': 'Invalid or expired verification token'
            }), 400
        
        # Update user's verification status
        user.is_verified = True
        user.email_verified_at = datetime.utcnow()
        user.email_verification_token = None  # Clear the token after verification
        
        # If this is the first verification, you might want to trigger welcome email
        if current_app.config.get('SEND_WELCOME_EMAIL', True) and not user.last_login_at:
            send_email(
                to=user.email,
                subject='Welcome to Our App!',
                template='welcome_email.html',
                username=user.username
            )
        
        db.session.commit()
        
        # Generate new tokens since this might be part of the signup flow
        access_token = user.generate_auth_token(expires_in=3600)  # 1 hour
        refresh_token = user.generate_auth_token(expires_in=2592000, token_type='refresh')  # 30 days
        
        return jsonify({
            'status': 'success',
            'message': 'Email verified successfully',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error verifying email: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': 'Failed to verify email. The link may have expired.'
        }), 500

@api_v1.route('/auth/forgot-password', methods=['POST'])
@handle_errors
def forgot_password():
    """
    Initiate password reset process.
    
    Request Body:
        {
            "email": "user@example.com"
        }
        
    Returns:
        Success message (always returns success to prevent email enumeration)
    """
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({
            'status': 'error',
            'message': 'Email is required'
        }), 400
    
    try:
        user = User.query.filter_by(email=email).first()
        
        # Always return success to prevent email enumeration
        if not user or not user.is_active:
            return jsonify({
                'status': 'success',
                'message': 'If an account exists with this email, a password reset link has been sent.'
            })
        
        # Generate password reset token
        reset_token = user.generate_password_reset_token()
        
        # Send password reset email
        reset_link = f"{current_app.config.get('FRONTEND_URL', '')}/reset-password?token={reset_token}"
        
        send_email(
            to=user.email,
            subject="Password Reset Request",
            template='reset_password.html',
            username=user.username,
            reset_link=reset_link
        )
        
        # Log the reset request
        logger.info(f"Password reset requested for user: {user.id}")
        
        return jsonify({
            'status': 'success',
            'message': 'If an account exists with this email, a password reset link has been sent.'
        })
        
    except Exception as e:
        logger.error(f"Error in forgot password for email {email}: {str(e)}", exc_info=True)
        # Still return success to prevent email enumeration
        return jsonify({
            'status': 'success',
            'message': 'If an account exists with this email, a password reset link has been sent.'
        })

@api_v1.route('/auth/reset-password', methods=['POST'])
@handle_errors
def reset_password():
    """
    Reset user's password using a reset token.
    
    Request Body:
        {
            "token": "reset-token",
            "new_password": "NewSecurePassword123!"
        }
        
    Returns:
        Success message and user data if password reset is successful
    """
    data = request.get_json()
    token = data.get('token')
    new_password = data.get('new_password')
    
    if not token or not new_password:
        return jsonify({
            'status': 'error',
            'message': 'Token and new password are required'
        }), 400
    
    try:
        # Find user by reset token
        user = User.query.filter_by(password_reset_token=token).first()
        
        if not user:
            return jsonify({
                'status': 'error',
                'message': 'Invalid or expired reset token'
            }), 400
            
        # Verify the reset token
        if not user.verify_token(token, 'reset'):
            return jsonify({
                'status': 'error',
                'message': 'Invalid or expired reset token'
            }), 400
        
        # Validate new password strength
        is_valid, message = validate_password_strength(new_password)
        if not is_valid:
            return jsonify({
                'status': 'error',
                'message': f'Password validation failed: {message}'
            }), 400
            
        # Check if the new password is the same as the current one
        if user.verify_password(new_password):
            return jsonify({
                'status': 'error',
                'message': 'New password must be different from the current password'
            }), 400
        
        # Update the password
        user.password = new_password  # Password hashing is handled in the setter
        user.password_reset_token = None  # Clear the reset token
        user.password_changed_at = datetime.utcnow()
        
        # Invalidate all existing refresh tokens (optional but recommended)
        # This would require additional implementation in your token blacklist
        
        db.session.commit()
        
        # Send password changed notification email
        send_email(
            to=user.email,
            subject="Your Password Has Been Changed",
            template='password_changed.html',
            username=user.username,
            timestamp=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'),
            ip_address=request.remote_addr or 'Unknown'
        )
        
        # Generate new tokens since we might want to log the user in after reset
        access_token = user.generate_auth_token(expires_in=3600)  # 1 hour
        refresh_token = user.generate_auth_token(expires_in=2592000, token_type='refresh')  # 30 days
        
        logger.info(f"Password reset successful for user: {user.id}")
        
        return jsonify({
            'status': 'success',
            'message': 'Password has been reset successfully',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error resetting password: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': 'Failed to reset password. Please try again.'
        }), 500

@api_v1.route('/auth/profile', methods=['GET'])
@token_required
@handle_errors
def get_profile():
    """
    Get the authenticated user's profile.
    
    Headers:
        Authorization: Bearer <token>
        
    Returns:
        User profile data
    """
    try:
        user = request.user
        return jsonify({
            'status': 'success',
            'data': {
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_verified': user.is_verified,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'updated_at': user.updated_at.isoformat() if user.updated_at else None
            }
        })
    except Exception as e:
        logger.error(f"Error fetching user profile: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': 'Failed to fetch profile',
            'error': str(e)
        }), 500

@api_v1.route('/auth/profile', methods=['PUT'])
@token_required
@handle_errors
def update_profile():
    """
    Update the authenticated user's profile.
    
    Headers:
        Authorization: Bearer <token>
        
    Request Body (all fields optional):
        {
            "first_name": "John",
            "last_name": "Doe",
            "email": "newemail@example.com"
        }
        
    Returns:
        Updated user profile data
    """
    data = request.get_json()
    user = request.user
    
    try:
        # Update user fields if provided
        if 'first_name' in data:
            user.first_name = data['first_name']
            
        if 'last_name' in data:
            user.last_name = data['last_name']
            
        if 'email' in data and data['email'] != user.email:
            # Check if new email is already in use
            if User.query.filter(User.email == data['email']).first():
                return jsonify({
                    'status': 'error',
                    'message': 'Email is already in use'
                }), 400
                
            user.email = data['email']
            user.is_verified = False
            
            # Generate new verification token
            verification_token = generate_reset_token(user.id)
            
            # Send verification email
            verification_link = f"{current_app.config['FRONTEND_URL']}/verify-email?token={verification_token}"
            send_email(
                to=user.email,
                subject="Verify Your New Email",
                template='verify_email.html',
                username=user.username,
                verification_link=verification_link
            )
        
        user.updated_at = datetime.datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Profile updated successfully',
            'data': {
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_verified': user.is_verified
            }
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating profile: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': 'Failed to update profile',
            'error': str(e)
        }), 500

@api_v1.route('/auth/change-password', methods=['POST'])
@token_required
@handle_errors
def change_password():
    """
    Change the authenticated user's password.
    
    Headers:
        Authorization: Bearer <token>
        
    Request Body:
        {
            "current_password": "oldpassword",
            "new_password": "newsecurepassword"
        }
        
    Returns:
        Success message
    """
    data = request.get_json()
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    user = request.user
    
    if not current_password or not new_password:
        return jsonify({
            'status': 'error',
            'message': 'Current password and new password are required'
        }), 400
    
    # Verify current password
    if not check_password_hash(user.password, current_password):
        return jsonify({
            'status': 'error',
            'message': 'Current password is incorrect'
        }), 401
    
    # Check if new password is different from current password
    if check_password_hash(user.password, new_password):
        return jsonify({
            'status': 'error',
            'message': 'New password must be different from current password'
        }), 400
    
    try:
        # Update password
        user.password = generate_password_hash(new_password, method='sha256')
        user.updated_at = datetime.datetime.utcnow()
        db.session.commit()
        
        # TODO: Send password change notification email
        
        return jsonify({
            'status': 'success',
            'message': 'Password updated successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error changing password: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': 'Failed to change password',
            'error': str(e)
        }), 500
