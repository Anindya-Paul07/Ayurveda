"""
Models Package

This package contains all the database models for the application.
"""

# Import models to make them available when importing from models package
from .user import User  # noqa: F401

# This makes the models discoverable by Flask-Migrate
__all__ = ['User']
