import os
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, event
from sqlalchemy.orm import relationship, scoped_session, sessionmaker
from datetime import datetime
from functools import wraps
import logging
from dotenv import load_dotenv

from extensions import db

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get database URLs from environment variables
USER_DATABASE_URL = os.getenv('USER_DATABASE_URL', 'postgresql://user:password@localhost:5432/ayurveda_users')
ARTICLE_DATABASE_URL = os.getenv('ARTICLE_DATABASE_URL', 'sqlite:///data/ayurveda.db')

# Create database engines
user_engine = db.create_engine(USER_DATABASE_URL, pool_pre_ping=True, pool_recycle=3600)
article_engine = db.create_engine(ARTICLE_DATABASE_URL, pool_pre_ping=True, pool_recycle=3600)

# Create session factories
UserSession = scoped_session(sessionmaker(bind=user_engine, autocommit=False, autoflush=False))
ArticleSession = scoped_session(sessionmaker(bind=article_engine, autocommit=False, autoflush=False))

# Create base classes for each database
UserBase = db.Model
ArticleBase = db.Model

def get_user_db():
    """Get a database session for user data."""
    db = UserSession()
    try:
        yield db
    finally:
        db.close()

def get_article_db():
    """Get a database session for article data."""
    db = ArticleSession()
    try:
        yield db
    finally:
        db.close()

# User Database Models (PostgreSQL)
class UserConversation(UserBase):
    __tablename__ = 'conversations'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    messages = relationship('UserMessage', back_populates='conversation', cascade='all, delete-orphan')
    context = relationship('UserContext', back_populates='conversation', uselist=False, cascade='all, delete-orphan')

class UserMessage(UserBase):
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey('conversations.id', ondelete='CASCADE'), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # 'user', 'assistant', 'tool'
    content = Column(Text, nullable=False)
    tool_name = Column(String(100))  # If message is from a tool
    tool_response = Column(Text)  # If message is a tool response
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    conversation = relationship('UserConversation', back_populates='messages')

class UserContext(UserBase):
    __tablename__ = 'contexts'
    
    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey('conversations.id', ondelete='CASCADE'), unique=True, nullable=False)
    vector_store_context = Column(JSON)  # Context from vector store
    tool_usage = Column(JSON)  # Tool usage statistics
    user_profile = Column(JSON)  # User-specific context
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    conversation = relationship('UserConversation', back_populates='context')

# Article Database Models (SQLite)
class Article(ArticleBase):
    __tablename__ = 'articles'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False, index=True)
    content = Column(Text, nullable=False)
    summary = Column(Text)
    description = Column(Text)
    source = Column(String(100), nullable=False)
    source_url = Column(String(255))
    image_url = Column(String(255))
    author = Column(String(100))
    published_at = Column(DateTime, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_published = Column(Integer, default=1, index=True)
    category = Column(String(100), index=True)
    tags = Column(Text)
    featured = Column(Integer, default=0, index=True)
    slug = Column(String(255), unique=True, index=True)
    
    metrics = relationship('ArticleMetrics', back_populates='article', uselist=False, cascade='all, delete-orphan')
    keywords = relationship('ArticleKeyword', back_populates='article', cascade='all, delete-orphan')
    tag_mappings = relationship('ArticleTagMapping', back_populates='article', cascade='all, delete-orphan')

class ArticleKeyword(ArticleBase):
    __tablename__ = 'article_keywords'
    
    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, ForeignKey('articles.id', ondelete='CASCADE'), nullable=False, index=True)
    keyword = Column(String(100), nullable=False, index=True)
    score = Column(Integer, nullable=False)
    
    article = relationship('Article', back_populates='keywords')

class ArticleMetrics(ArticleBase):
    __tablename__ = 'article_metrics'
    
    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, ForeignKey('articles.id', ondelete='CASCADE'), unique=True, nullable=False, index=True)
    view_count = Column(Integer, default=0, index=True)
    share_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    last_viewed = Column(DateTime)
    
    article = relationship('Article', back_populates='metrics')

class ArticleTag(ArticleBase):
    __tablename__ = 'article_tags'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    slug = Column(String(100), unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    mappings = relationship('ArticleTagMapping', back_populates='tag', cascade='all, delete-orphan')

class ArticleTagMapping(ArticleBase):
    __tablename__ = 'article_tag_mapping'
    
    article_id = Column(Integer, ForeignKey('articles.id', ondelete='CASCADE'), primary_key=True)
    tag_id = Column(Integer, ForeignKey('article_tags.id', ondelete='CASCADE'), primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    article = relationship('Article', back_populates='tag_mappings')
    tag = relationship('ArticleTag', back_populates='mappings')

def init_databases():
    """Initialize all database tables."""
    # This function is kept for backward compatibility
    # Actual table creation is now handled by Flask-Migrate
    logger.info("Database initialization is now handled by Flask-Migrate")

def get_db_session(session_type='user'):
    """Get a database session for the specified type.
    
    Args:
        session_type (str): Type of session to get ('user' or 'article')
        
    Returns:
        Session: Database session
    """
    if session_type == 'article':
        return ArticleSession()
    return UserSession()

def close_session(exception=None):
    """Close the database session after each request."""
    UserSession.remove()
    ArticleSession.remove()
