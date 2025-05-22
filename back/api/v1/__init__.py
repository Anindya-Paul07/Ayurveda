"""
API v1 Package

This package contains all version 1 API endpoints and resources.
"""

from flask import Blueprint

api_v1 = Blueprint('api_v1', __name__)

# Import all route modules to register them with the blueprint
from . import chat, articles, dosha, recommendations, weather, auth
