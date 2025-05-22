"""
Recommendations API Endpoints

This module handles all recommendation-related API endpoints including:
- Personalized health recommendations
- Diet and lifestyle suggestions
- Herbal remedies and treatments
"""

from flask import request, jsonify, current_app
from ..service.recommendation_service import RecommendationService
from . import api_v1
from functools import wraps
import logging

logger = logging.getLogger(__name__)
recommendation_service = RecommendationService()

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

@api_v1.route('/recommendations', methods=['GET'])
@handle_errors
def get_recommendations():
    """
    Get personalized recommendations based on user profile and context.
    
    Query Parameters:
        user_id: Optional user ID for personalized recommendations
        context: Context for recommendations (e.g., current_health, goals)
        limit: Maximum number of recommendations to return (default: 5)
        
    Returns:
        List of personalized recommendations
    """
    user_id = request.args.get('user_id')
    context = request.args.get('context')
    limit = request.args.get('limit', 5, type=int)
    
    try:
        recommendations = recommendation_service.get_personalized_recommendations(
            user_id=user_id,
            context=context,
            limit=limit
        )
        
        return jsonify({
            'status': 'success',
            'data': recommendations
        })
    except Exception as e:
        logger.error(f"Error fetching recommendations: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': 'Failed to fetch recommendations',
            'error': str(e)
        }), 500

@api_v1.route('/recommendations/diet', methods=['GET'])
@handle_errors
def get_diet_recommendations():
    """
    Get personalized diet recommendations.
    
    Query Parameters:
        user_id: Optional user ID
        dosha: Dosha type (vata, pitta, kapha)
        health_goals: Comma-separated health goals
        dietary_restrictions: Comma-separated dietary restrictions
        
    Returns:
        List of diet recommendations
    """
    user_id = request.args.get('user_id')
    dosha = request.args.get('dosha')
    health_goals = request.args.get('health_goals', '').split(',')
    dietary_restrictions = request.args.get('dietary_restrictions', '').split(',')
    
    try:
        recommendations = recommendation_service.get_diet_recommendations(
            user_id=user_id,
            dosha=dosha,
            health_goals=[g for g in health_goals if g],
            dietary_restrictions=[r for r in dietary_restrictions if r]
        )
        
        return jsonify({
            'status': 'success',
            'data': recommendations
        })
    except Exception as e:
        logger.error(f"Error fetching diet recommendations: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': 'Failed to fetch diet recommendations',
            'error': str(e)
        }), 500

@api_v1.route('/recommendations/lifestyle', methods=['GET'])
@handle_errors
def get_lifestyle_recommendations():
    """
    Get personalized lifestyle recommendations.
    
    Query Parameters:
        user_id: Optional user ID
        dosha: Dosha type (vata, pitta, kapha)
        current_routine: Current daily routine
        goals: Comma-separated lifestyle goals
        
    Returns:
        List of lifestyle recommendations
    """
    user_id = request.args.get('user_id')
    dosha = request.args.get('dosha')
    current_routine = request.args.get('current_routine')
    goals = request.args.get('goals', '').split(',')
    
    try:
        recommendations = recommendation_service.get_lifestyle_recommendations(
            user_id=user_id,
            dosha=dosha,
            current_routine=current_routine,
            goals=[g for g in goals if g]
        )
        
        return jsonify({
            'status': 'success',
            'data': recommendations
        })
    except Exception as e:
        logger.error(f"Error fetching lifestyle recommendations: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': 'Failed to fetch lifestyle recommendations',
            'error': str(e)
        }), 500

@api_v1.route('/recommendations/herbs', methods=['GET'])
@handle_errors
def get_herb_recommendations():
    """
    Get personalized herbal remedy recommendations.
    
    Query Parameters:
        user_id: Optional user ID
        symptoms: Comma-separated list of symptoms
        conditions: Comma-separated list of health conditions
        current_medications: Comma-separated list of current medications
        
    Returns:
        List of herb recommendations with usage instructions
    """
    user_id = request.args.get('user_id')
    symptoms = request.args.get('symptoms', '').split(',')
    conditions = request.args.get('conditions', '').split(',')
    current_medications = request.args.get('current_medications', '').split(',')
    
    try:
        recommendations = recommendation_service.get_herb_recommendations(
            user_id=user_id,
            symptoms=[s for s in symptoms if s],
            conditions=[c for c in conditions if c],
            current_medications=[m for m in current_medications if m]
        )
        
        return jsonify({
            'status': 'success',
            'data': recommendations
        })
    except Exception as e:
        logger.error(f"Error fetching herb recommendations: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': 'Failed to fetch herb recommendations',
            'error': str(e)
        }), 500

@api_v1.route('/recommendations/yoga', methods=['GET'])
@handle_errors
def get_yoga_recommendations():
    """
    Get personalized yoga and pranayama recommendations.
    
    Query Parameters:
        user_id: Optional user ID
        dosha: Dosha type (vata, pitta, kapha)
        fitness_level: Beginner, intermediate, or advanced
        health_concerns: Comma-separated health concerns
        
    Returns:
        List of yoga and pranayama recommendations
    """
    user_id = request.args.get('user_id')
    dosha = request.args.get('dosha')
    fitness_level = request.args.get('fitness_level', 'beginner')
    health_concerns = request.args.get('health_concerns', '').split(',')
    
    try:
        recommendations = recommendation_service.get_yoga_recommendations(
            user_id=user_id,
            dosha=dosha,
            fitness_level=fitness_level,
            health_concerns=[h for h in health_concerns if h]
        )
        
        return jsonify({
            'status': 'success',
            'data': recommendations
        })
    except Exception as e:
        logger.error(f"Error fetching yoga recommendations: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': 'Failed to fetch yoga recommendations',
            'error': str(e)
        }), 500
