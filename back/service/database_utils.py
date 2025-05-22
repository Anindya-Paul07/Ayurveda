"""
Database utility functions for the Ayurveda AI application.

This module provides utility functions for common database operations,
including session management, query building, and error handling.
"""
from contextlib import contextmanager
from typing import Any, Dict, List, Optional, Type, TypeVar, Union
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging

from .database import get_user_db, get_article_db, UserSession, ArticleSession

logger = logging.getLogger(__name__)

T = TypeVar('T')

@contextmanager
def get_db_session(session_type: str = 'user'):
    """Get a database session with proper error handling and cleanup.
    
    Args:
        session_type: Type of session to get ('user' or 'article')
        
    Yields:
        Session: A SQLAlchemy database session
        
    Raises:
        SQLAlchemyError: If there's an error creating or using the session
    """
    if session_type == 'article':
        db = ArticleSession()
    else:
        db = UserSession()
        
    try:
        yield db
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise
    finally:
        db.close()

def get_object_or_404(model: Type[T], object_id: Any, session_type: str = 'user') -> T:
    """Get an object by ID or return 404 if not found.
    
    Args:
        model: SQLAlchemy model class
        object_id: ID of the object to retrieve
        session_type: Type of session to use ('user' or 'article')
        
    Returns:
        The requested object
        
    Raises:
        HTTPException: 404 if object not found
    """
    with get_db_session(session_type) as db:
        obj = db.query(model).get(object_id)
        if obj is None:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail=f"{model.__name__} not found")
        return obj

def get_objects(
    model: Type[T],
    filters: Optional[Dict] = None,
    order_by: Optional[Any] = None,
    limit: Optional[int] = None,
    offset: int = 0,
    session_type: str = 'user'
) -> List[T]:
    """Get a list of objects with optional filtering and pagination.
    
    Args:
        model: SQLAlchemy model class
        filters: Dictionary of filters to apply (column=value)
        order_by: Column to order by
        limit: Maximum number of results to return
        offset: Number of results to skip
        session_type: Type of session to use ('user' or 'article')
        
    Returns:
        List of model instances
    """
    with get_db_session(session_type) as db:
        query = db.query(model)
        
        # Apply filters
        if filters:
            for key, value in filters.items():
                if hasattr(model, key):
                    query = query.filter(getattr(model, key) == value)
        
        # Apply ordering
        if order_by is not None:
            query = query.order_by(order_by)
            
        # Apply pagination
        if limit is not None:
            query = query.limit(limit).offset(offset)
            
        return query.all()

def create_object(
    model: Type[T],
    data: Dict[str, Any],
    session_type: str = 'user'
) -> T:
    """Create a new object in the database.
    
    Args:
        model: SQLAlchemy model class
        data: Dictionary of attributes to set on the new object
        session_type: Type of session to use ('user' or 'article')
        
    Returns:
        The newly created object
    """
    with get_db_session(session_type) as db:
        obj = model(**data)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

def update_object(
    model: Type[T],
    object_id: Any,
    data: Dict[str, Any],
    session_type: str = 'user'
) -> T:
    """Update an existing object in the database.
    
    Args:
        model: SQLAlchemy model class
        object_id: ID of the object to update
        data: Dictionary of attributes to update
        session_type: Type of session to use ('user' or 'article')
        
    Returns:
        The updated object
        
    Raises:
        HTTPException: 404 if object not found
    """
    with get_db_session(session_type) as db:
        obj = db.query(model).get(object_id)
        if obj is None:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail=f"{model.__name__} not found")
            
        for key, value in data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
                
        db.commit()
        db.refresh(obj)
        return obj

def delete_object(
    model: Type[T],
    object_id: Any,
    session_type: str = 'user'
) -> bool:
    """Delete an object from the database.
    
    Args:
        model: SQLAlchemy model class
        object_id: ID of the object to delete
        session_type: Type of session to use ('user' or 'article')
        
    Returns:
        bool: True if the object was deleted, False if not found
    """
    with get_db_session(session_type) as db:
        obj = db.query(model).get(object_id)
        if obj is None:
            return False
            
        db.delete(obj)
        db.commit()
        return True
