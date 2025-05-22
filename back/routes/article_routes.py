"""
Article Routes

This module defines the API endpoints for article management and discovery.
"""
from flask import Blueprint, jsonify, request
from service.article_service import ArticleManager, ArticleAgent
import os
import sqlite3

# Initialize Blueprint
article_bp = Blueprint('articles', __name__)

# Initialize database connection
def get_db_connection():
    """Create and return a database connection."""
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'ayurveda.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    return sqlite3.connect(db_path)

# Initialize services
def get_article_manager():
    """Initialize and return the article manager."""
    conn = get_db_connection()
    return ArticleManager(conn)

def get_article_agent():
    """Initialize and return the article agent."""
    return ArticleAgent(get_article_manager())

# Routes
@article_bp.route('/api/articles/discover', methods=['GET'])
def discover_articles():
    """
    Discover new articles from various sources.
    
    Query Parameters:
        query (str): Search query (default: 'Ayurveda')
        limit (int): Maximum number of articles to return (default: 10)
    """
    try:
        query = request.args.get('query', 'Ayurveda')
        limit = int(request.args.get('limit', 10))
        
        agent = get_article_agent()
        articles = agent.discover_articles(query)[:limit]
        
        return jsonify({
            'success': True,
            'count': len(articles),
            'articles': articles
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@article_bp.route('/api/articles', methods=['GET'])
def get_articles():
    """
    Get published articles with optional filtering.
    
    Query Parameters:
        limit (int): Maximum number of articles to return (default: 10)
        offset (int): Number of articles to skip (default: 0)
        sort (str): Sort field (default: 'published_at')
        order (str): Sort order ('asc' or 'desc', default: 'desc')
    """
    try:
        limit = int(request.args.get('limit', 10))
        offset = int(request.args.get('offset', 0))
        sort = request.args.get('sort', 'published_at')
        order = 'DESC' if request.args.get('order', 'desc').lower() == 'desc' else 'ASC'
        
        # Validate sort field to prevent SQL injection
        valid_sort_fields = ['id', 'title', 'source', 'published_at', 'created_at', 'view_count']
        sort = sort if sort in valid_sort_fields else 'published_at'
        
        manager = get_article_manager()
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get total count
        cursor.execute('SELECT COUNT(*) FROM articles WHERE is_published = 1')
        total = cursor.fetchone()[0]
        
        # Get paginated articles
        query = f'''
            SELECT a.*, am.view_count, am.share_count, am.like_count
            FROM articles a
            LEFT JOIN article_metrics am ON a.id = am.article_id
            WHERE a.is_published = 1
            ORDER BY {sort} {order}
            LIMIT ? OFFSET ?
        '''
        
        cursor.execute(query, (limit, offset))
        columns = [column[0] for column in cursor.description]
        articles = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        return jsonify({
            'success': True,
            'count': len(articles),
            'total': total,
            'articles': articles
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@article_bp.route('/api/articles/<int:article_id>', methods=['GET'])
def get_article(article_id):
    """Get a single article by ID."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get article
        cursor.execute('''
            SELECT a.*, am.view_count, am.share_count, am.like_count
            FROM articles a
            LEFT JOIN article_metrics am ON a.id = am.article_id
            WHERE a.id = ?
        ''', (article_id,))
        
        article = cursor.fetchone()
        if not article:
            return jsonify({
                'success': False,
                'error': 'Article not found'
            }), 404
        
        # Convert to dict
        columns = [column[0] for column in cursor.description]
        article_dict = dict(zip(columns, article))
        
        # Update view count
        cursor.execute('''
            INSERT OR IGNORE INTO article_metrics (article_id, view_count, share_count, like_count)
            VALUES (?, 1, 0, 0)
            ON CONFLICT(article_id) DO UPDATE 
            SET view_count = view_count + 1
        ''', (article_id,))
        conn.commit()
        
        # Get recommendations
        agent = get_article_agent()
        recommendations = agent.get_article_recommendations(article_id)
        
        return jsonify({
            'success': True,
            'article': article_dict,
            'recommendations': recommendations
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@article_bp.route('/api/articles/<int:article_id>/like', methods=['POST'])
def like_article(article_id):
    """Increment the like count for an article."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Update like count
        cursor.execute('''
            INSERT OR IGNORE INTO article_metrics (article_id, view_count, share_count, like_count)
            VALUES (?, 0, 0, 1)
            ON CONFLICT(article_id) DO UPDATE 
            SET like_count = like_count + 1
        ''', (article_id,))
        
        # Get updated count
        cursor.execute('SELECT like_count FROM article_metrics WHERE article_id = ?', (article_id,))
        result = cursor.fetchone()
        like_count = result[0] if result else 0
        
        conn.commit()
        
        return jsonify({
            'success': True,
            'like_count': like_count
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@article_bp.route('/api/articles/<int:article_id>/share', methods=['POST'])
def share_article(article_id):
    """Increment the share count for an article."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Update share count
        cursor.execute('''
            INSERT OR IGNORE INTO article_metrics (article_id, view_count, share_count, like_count)
            VALUES (?, 0, 1, 0)
            ON CONFLICT(article_id) DO UPDATE 
            SET share_count = share_count + 1
        ''', (article_id,))
        
        # Get updated count
        cursor.execute('SELECT share_count FROM article_metrics WHERE article_id = ?', (article_id,))
        result = cursor.fetchone()
        share_count = result[0] if result else 0
        
        conn.commit()
        
        return jsonify({
            'success': True,
            'share_count': share_count
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
