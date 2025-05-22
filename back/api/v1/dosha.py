"""
Dosha API Endpoints

This module handles all dosha-related API endpoints including:
- Dosha analysis and determination
- Dosha-based recommendations
- Dosha information and education
"""

from flask import request, jsonify, current_app
from ..service.dosha_service import DoshaService
from . import api_v1
from functools import wraps
import logging

logger = logging.getLogger(__name__)
dosha_service = DoshaService()

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

@api_v1.route('/dosha/analyze', methods=['POST'])
@handle_errors
def analyze_dosha():
    """
    Analyze user responses to determine their dosha type.
    
    Request Body:
        {
            "responses": [
                {"question_id": 1, "answer": 3},
                {"question_id": 2, "answer": 2},
                ...
            ],
            "user_id": "optional-user-id"
        }
        
    Returns:
        Dosha analysis results with primary and secondary doshas
    """
    data = request.get_json()
    responses = data.get('responses', [])
    user_id = data.get('user_id')
    
    if not responses:
        return jsonify({
            'status': 'error',
            'message': 'No responses provided'
        }), 400
    
    try:
        # Process the dosha analysis
        result = dosha_service.analyze_responses(responses, user_id)
        
        return jsonify({
            'status': 'success',
            'data': result
        })
    except Exception as e:
        logger.error(f"Error analyzing dosha: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': 'Failed to analyze dosha',
            'error': str(e)
        }), 500

@api_v1.route('/dosha/info', methods=['GET'])
@handle_errors
def get_dosha_info():
    """
    Get information about all dosha types.
    
    Returns:
        Information about Vata, Pitta, and Kapha doshas
    """
    try:
        doshas = dosha_service.get_dosha_info()
        return jsonify({
            'status': 'success',
            'data': doshas
        })
    except Exception as e:
        logger.error(f"Error fetching dosha info: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': 'Failed to fetch dosha information',
            'error': str(e)
        }), 500

@api_v1.route('/dosha/<string:dosha_type>', methods=['GET'])
@handle_errors
def get_dosha_detail(dosha_type):
    """
    Get detailed information about a specific dosha type.
    
    Path Parameters:
        dosha_type: Type of dosha (vata, pitta, kapha)
        
    Returns:
        Detailed information about the specified dosha
    """
    try:
        dosha_info = dosha_service.get_dosha_detail(dosha_type.lower())
        if not dosha_info:
            return jsonify({
                'status': 'error',
                'message': 'Invalid dosha type'
            }), 404
            
        return jsonify({
            'status': 'success',
            'data': dosha_info
        })
    except Exception as e:
        logger.error(f"Error fetching {dosha_type} info: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': f'Failed to fetch {dosha_type} information',
            'error': str(e)
        }), 500

@api_v1.route('/dosha/recommendations', methods=['GET'])
@handle_errors
def get_dosha_recommendations():
    """
    Get personalized recommendations based on dosha type.
    
    Query Parameters:
        dosha: Primary dosha type (vata, pitta, kapha)
        secondary_dosha: Secondary dosha type (optional)
        category: Filter recommendations by category (diet, lifestyle, etc.)
        
    Returns:
        List of personalized recommendations
    """
    primary_dosha = request.args.get('dosha')
    secondary_dosha = request.args.get('secondary_dosha')
    category = request.args.get('category')
    
    if not primary_dosha:
        return jsonify({
            'status': 'error',
            'message': 'Primary dosha type is required'
        }), 400
    
    try:
        recommendations = dosha_service.get_recommendations(
            primary_dosha=primary_dosha,
            secondary_dosha=secondary_dosha,
            category=category
        )
        
        return jsonify({
            'status': 'success',
            'data': recommendations
        })
    except Exception as e:
        logger.error(f"Error fetching dosha recommendations: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': 'Failed to fetch recommendations',
            'error': str(e)
        }), 500

@api_v1.route('/dosha/balance', methods=['GET'])
@handle_errors
def get_dosha_balance():
    """
    Get information about balancing a specific dosha.
    
    Query Parameters:
        dosha: The dosha to get balancing information for
        
    Returns:
        Information on how to balance the specified dosha
    """
    dosha = request.args.get('dosha')
    
    if not dosha:
        return jsonify({
            'status': 'error',
            'message': 'Dosha type is required'
        }), 400
    
    try:
        balance_info = dosha_service.get_balance_info(dosha.lower())
        if not balance_info:
            return jsonify({
                'status': 'error',
                'message': 'Invalid dosha type'
            }), 404
            
        return jsonify({
            'status': 'success',
            'data': balance_info
        })
    except Exception as e:
        logger.error(f"Error fetching balance info for {dosha}: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': f'Failed to fetch balance information for {dosha}',
            'error': str(e)
        }), 500
