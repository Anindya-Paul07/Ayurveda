"""
Articles API Endpoints

This module handles all article-related API endpoints including:
- Fetching articles with filtering and pagination
- Article search and recommendations
- Article interactions (likes, bookmarks, shares)
"""

from flask import request, jsonify, current_app
from ..service.article_service import ArticleService
from . import api_v1
from functools import wraps
import logging

logger = logging.getLogger(__name__)
article_service = ArticleService()

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

@api_v1.route('/articles', methods=['GET'])
@handle_errors
def get_articles():
    """
    Get paginated list of articles with filtering and sorting.
    
    Query Parameters:
        page: Page number (default: 1)
        per_page: Items per page (default: 10, max: 100)
        category: Filter by category
        tag: Filter by tag
        search: Search query
        sort: Field to sort by (default: published_at)
        order: Sort order (asc/desc, default: desc)
        
    Returns:
        Paginated list of articles with metadata
    """
    # Get query parameters with defaults
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    category = request.args.get('category')
    tag = request.args.get('tag')
    search = request.args.get('search')
    sort = request.args.get('sort', 'published_at')
    order = request.args.get('order', 'desc')
    
    # Build filters
    filters = {}
    if category:
        filters['category'] = category
    if tag:
        filters['tag'] = tag
    if search:
        filters['search'] = search
    
    try:
        # Get paginated articles
        result = article_service.get_articles(
            page=page,
            per_page=per_page,
            sort=sort,
            order=order,
            **filters
        )
        
        return jsonify({
            'status': 'success',
            'data': {
                'articles': result.items,
                'total': result.total,
                'pages': result.pages,
                'current_page': page,
                'per_page': per_page
            }
        })
    except Exception as e:
        logger.error(f"Error fetching articles: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': 'Failed to fetch articles',
            'error': str(e)
        }), 500

@api_v1.route('/articles/<int:article_id>', methods=['GET'])
@handle_errors
def get_article(article_id):
    """
    Get a single article by ID.
    
    Path Parameters:
        article_id: ID of the article to retrieve
        
    Returns:
        Article details
    """
    try:
        article = article_service.get_article(article_id)
        if not article:
            return jsonify({
                'status': 'error',
                'message': 'Article not found'
            }), 404
            
        return jsonify({
            'status': 'success',
            'data': article
        })
    except Exception as e:
        logger.error(f"Error fetching article {article_id}: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': 'Failed to fetch article',
            'error': str(e)
        }), 500

@api_v1.route('/articles/<int:article_id>/view', methods=['POST'])
@handle_errors
def track_article_view(article_id):
    """
    Track an article view.
    
    Path Parameters:
        article_id: ID of the article being viewed
        
    Returns:
        Success/error status
    """
    try:
        user_id = getattr(request, 'user_id', None)
        article_service.track_view(article_id, user_id)
        
        return jsonify({
            'status': 'success',
            'message': 'View tracked successfully'
        })
    except Exception as e:
        logger.error(f"Error tracking article view: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': 'Failed to track article view',
            'error': str(e)
        }), 500

@api_v1.route('/articles/<int:article_id>/like', methods=['POST'])
@handle_errors
def like_article(article_id):
    """
    Like or unlike an article.
    
    Path Parameters:
        article_id: ID of the article to like/unlike
        
    Returns:
        Updated like status and count
    """
    try:
        user_id = getattr(request, 'user_id', None)
        if not user_id:
            return jsonify({
                'status': 'error',
                'message': 'Authentication required'
            }), 401
            
        result = article_service.toggle_like(article_id, user_id)
        
        return jsonify({
            'status': 'success',
            'data': {
                'liked': result['liked'],
                'like_count': result['count']
            }
        })
    except Exception as e:
        logger.error(f"Error toggling article like: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': 'Failed to update like status',
            'error': str(e)
        }), 500

@api_v1.route('/articles/<int:article_id>/bookmark', methods=['POST'])
@handle_errors
def bookmark_article(article_id):
    """
    Bookmark or unbookmark an article.
    
    Path Parameters:
        article_id: ID of the article to bookmark/unbookmark
        
    Returns:
        Updated bookmark status
    """
    try:
        user_id = getattr(request, 'user_id', None)
        if not user_id:
            return jsonify({
                'status': 'error',
                'message': 'Authentication required'
            }), 401
            
        result = article_service.toggle_bookmark(article_id, user_id)
        
        return jsonify({
            'status': 'success',
            'data': {
                'bookmarked': result['bookmarked']
            }
        })
    except Exception as e:
        logger.error(f"Error toggling article bookmark: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': 'Failed to update bookmark status',
            'error': str(e)
        }), 500

@api_v1.route('/articles/categories', methods=['GET'])
@handle_errors
def get_categories():
    """
    Get list of article categories.
    
    Returns:
        List of category names
    """
    try:
        categories = article_service.get_categories()
        return jsonify({
            'status': 'success',
            'data': categories
        })
    except Exception as e:
        logger.error(f"Error fetching categories: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': 'Failed to fetch categories',
            'error': str(e)
        }), 500

@api_v1.route('/articles/tags', methods=['GET'])
@handle_errors
def get_tags():
    """
    Get list of article tags with counts.
    
    Returns:
        List of tags with counts
    """
    try:
        tags = article_service.get_tags()
        return jsonify({
            'status': 'success',
            'data': tags
        })
    except Exception as e:
        logger.error(f"Error fetching tags: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': 'Failed to fetch tags',
            'error': str(e)
        }), 500

@api_v1.route('/articles/<int:article_id>/related', methods=['GET'])
@handle_errors
def get_related_articles(article_id):
    """
    Get articles related to the specified article.
    
    Path Parameters:
        article_id: ID of the article to find related content for
        
    Query Parameters:
        limit: Maximum number of related articles to return (default: 5)
        
    Returns:
        List of related articles
    """
    limit = request.args.get('limit', 5, type=int)
    
    try:
        related = article_service.get_related_articles(article_id, limit=limit)
        return jsonify({
            'status': 'success',
            'data': related
        })
    except Exception as e:
        logger.error(f"Error fetching related articles: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': 'Failed to fetch related articles',
            'error': str(e)
        }), 500
