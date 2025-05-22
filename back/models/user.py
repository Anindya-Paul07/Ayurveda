"""
User Model

This module defines the User model and related functionality for authentication and authorization.
"""

from datetime import datetime, timedelta
import uuid
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import jwt
from ..extensions import db

# Import models to avoid circular imports
# from .health_profile import HealthProfile  # Uncomment when HealthProfile is implemented
# from .dosha_test import DoshaTest  # Uncomment when DoshaTest is implemented
# from .article import Article, ArticleComment, ArticleLike, ArticleBookmark  # Uncomment when Article models are implemented
# from .conversation import Conversation  # Uncomment when Conversation is implemented

class User(UserMixin, db.Model):
    """
    User model representing application users.
    
    Attributes:
        id (int): Primary key
        username (str): Unique username
        email (str): Unique email address
        password_hash (str): Hashed password
        first_name (str): User's first name
        last_name (str): User's last name
        is_verified (bool): Whether the user's email is verified
        email_verified_at (datetime): When the email was verified
        is_active (bool): Whether the user account is active
        is_admin (bool): Whether the user has admin privileges
        created_at (datetime): When the user was created
        updated_at (datetime): When the user was last updated
        last_login_at (datetime): When the user last logged in
        current_login_at (datetime): When the user logged in for the current session
        last_login_ip (str): IP address of last login
        current_login_ip (str): IP address of current login
        login_count (int): Number of times the user has logged in
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    email_verified_at = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login_at = db.Column(db.DateTime, nullable=True)
    current_login_at = db.Column(db.DateTime, nullable=True)
    last_login_ip = db.Column(db.String(45), nullable=True)
    current_login_ip = db.Column(db.String(45), nullable=True)
    login_count = db.Column(db.Integer, default=0, nullable=False)
    
    # Email verification
    email_verification_token = db.Column(db.String(255), index=True, nullable=True)
    email_verification_sent_at = db.Column(db.DateTime, nullable=True)
    
    # Password reset
    password_reset_token = db.Column(db.String(255), index=True, nullable=True)
    password_reset_sent_at = db.Column(db.DateTime, nullable=True)
    password_changed_at = db.Column(db.DateTime, nullable=True)
    
    # Login tracking
    last_login_at = db.Column(db.DateTime, nullable=True)
    current_login_at = db.Column(db.DateTime, nullable=True)
    last_login_ip = db.Column(db.String(45), nullable=True)
    current_login_ip = db.Column(db.String(45), nullable=True)
    login_count = db.Column(db.Integer, default=0, nullable=False)
    
    # Relationships (commented out to avoid circular imports)
    # health_profile = db.relationship('HealthProfile', back_populates='user', uselist=False, lazy=True)
    # dosha_tests = db.relationship('DoshaTest', back_populates='user', lazy=True)
    # articles = db.relationship('Article', back_populates='author', lazy=True)
    # comments = db.relationship('ArticleComment', back_populates='user', lazy=True)
    # likes = db.relationship('ArticleLike', back_populates='user', lazy=True)
    # bookmarks = db.relationship('ArticleBookmark', back_populates='user', lazy=True)
    # conversations = db.relationship('Conversation', back_populates='user', lazy=True)
    
    def __init__(self, **kwargs):
        """Initialize a new user."""
        super(User, self).__init__(**kwargs)
        if self.email:
            self.email = self.email.lower()
        # Initialize default values
        self.is_verified = kwargs.get('is_verified', False)
        self.is_active = kwargs.get('is_active', True)
        self.is_admin = kwargs.get('is_admin', False)
        self.created_at = kwargs.get('created_at', datetime.utcnow())
        self.updated_at = kwargs.get('updated_at', datetime.utcnow())
        self.login_count = kwargs.get('login_count', 0)
    
    @property
    def password(self):
        """Prevent password from being accessed."""
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        """Set password to a hashed password."""
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        """Verify the user's password."""
        return check_password_hash(self.password_hash, password)
        
    def generate_password_reset_token(self):
        """Generate a password reset token for the user."""
        self.password_reset_token = self.generate_auth_token(expires_in=3600, token_type='reset')  # 1 hour
        db.session.commit()
        return self.password_reset_token
        
    def verify_token(self, token, token_type='verify'):
        """
        Verify a token for the user.
        
        Args:
            token (str): The token to verify
            token_type (str): Type of token to verify ('verify' or 'reset')
            
        Returns:
            bool: True if token is valid, False otherwise
        """
        if not token:
            return False
            
        try:
            # Decode the token
            data = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256']
            )
            
            # Check if token is for this user and of the correct type
            if (data.get('user_id') != self.id or 
                data.get('type') != token_type or
                (token_type == 'verify' and token != self.email_verification_token) or
                (token_type == 'reset' and token != self.password_reset_token)):
                return False
                
            return True
            
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return False
    
    def get_full_name(self):
        """Get the user's full name."""
        return f"{self.first_name} {self.last_name}" if self.first_name and self.last_name else self.username
    
    def has_role(self, role_name):
        """Check if user has the specified role."""
        # For simple role management, we can extend this to use a proper role-based access control (RBAC) system
        if role_name == 'admin':
            return self.is_admin
        return False
    
    def update_login_info(self, ip_address):
        """Update user login information."""
        self.last_login_at = self.current_login_at
        self.current_login_at = datetime.utcnow()
        self.last_login_ip = self.current_login_ip
        self.current_login_ip = ip_address
        self.login_count += 1
    
    def generate_auth_token(self, expires_in=3600, token_type='access'):
        """
        Generate a JWT token for the user.
        
        Args:
            expires_in (int): Token expiration time in seconds
            token_type (str): Type of token ('access', 'refresh', 'verify', 'reset')
            
        Returns:
            str: JWT token
        """
        # Create the token payload
        payload = {
            'user_id': self.id,
            'exp': datetime.utcnow() + timedelta(seconds=expires_in),
            'iat': datetime.utcnow(),
            'type': token_type,
            'jti': str(uuid.uuid4())  # Unique identifier for the token
        }
        
        # Generate the token
        token = jwt.encode(
            payload,
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )
        
        # Store the token based on its type
        if token_type == 'verify':
            self.email_verification_token = token
        elif token_type == 'reset':
            self.password_reset_token = token
        
        # For access and refresh tokens, we don't store them in the database
        # as they're short-lived and validated using the JWT signature
        
        return token
    
    def generate_email_verification_token(self, expires_in=86400):  # 24 hours
        """
        Generate and store an email verification token.
        
        Args:
            expires_in (int): Token expiration time in seconds (default: 24 hours)
            
        Returns:
            str: The generated JWT token
        """
        token = self.generate_auth_token(expires_in=expires_in, token_type='verify')
        db.session.commit()  # Commit to save the token to the database
        return token
    
    def generate_password_reset_token(self, expires_in=3600):  # 1 hour
        """
        Generate and store a password reset token.
        
        Args:
            expires_in (int): Token expiration time in seconds (default: 1 hour)
            
        Returns:
            str: The generated JWT token
        """
        token = self.generate_auth_token(expires_in=expires_in, token_type='reset')
        db.session.commit()  # Commit to save the token to the database
        return token
    
    def verify_token(self, token, token_type='access'):
        """
        Verify a JWT token for this user.
        
        Args:
            token (str): The JWT token to verify
            token_type (str): Expected token type ('access', 'refresh', 'verify', 'reset')
            
        Returns:
            bool: True if token is valid, False otherwise
        """
        if not token:
            return False
            
        try:
            # Decode the token
            payload = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256']
            )
            
            # Check if token is for this user and of the correct type
            if payload.get('user_id') != self.id or payload.get('type') != token_type:
                return False
                
            # For verify and reset tokens, ensure they match the stored token
            if token_type == 'verify' and token != self.email_verification_token:
                return False
                
            if token_type == 'reset' and token != self.password_reset_token:
                return False
                
            return True
            
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return False
    
    def to_dict(self):
        """Convert user object to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.get_full_name(),
            'is_verified': self.is_verified,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_login_at': self.last_login_at.isoformat() if self.last_login_at else None
        }
    
    def __repr__(self):
        return f'<User {self.username}>'
