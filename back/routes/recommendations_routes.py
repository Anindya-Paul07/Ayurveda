"""
Recommendations Routes Module

This module defines the API endpoints for retrieving Ayurvedic recommendations
based on user queries or dosha profiles using Pinecone vector similarity search.
It includes both separate and unified endpoints for recommendations that can
integrate dosha determination and weather data.
"""

from flask import Blueprint, request, jsonify
from service.recommendation_service import get_recommendations
from service.weather_service import get_weather_data, determine_season
from service.dosha_service import determine_dosha

# Create a Blueprint for recommendations routes
recommendations_bp = Blueprint('recommendations', __name__)


@recommendations_bp.route('/api/recommendations', methods=['GET'])
def get_ayurvedic_recommendations():
    """
    Retrieve Ayurvedic recommendations based on query parameters.
    
    Query Parameters:
        dosha (str, required): User's dosha type (vata, pitta, kapha, or combinations)
        query (str, optional): Free text query for recommendation search
        season (str, optional): Current season
        time_of_day (str, optional): Time of day
        health_concern (str, optional): Specific health concern
        city (str, optional): City name for real-time weather-based recommendations
        country (str, optional): Country code for the city (e.g., 'US', 'IN')
        limit (int, optional): Maximum number of recommendations to return (default: 5)
        
    Returns:
        JSON response with recommendations or error message
        
    Example:
        GET /api/recommendations?query=digestion&dosha=vata-pitta
        GET /api/recommendations?dosha=kapha&season=winter
        GET /api/recommendations?dosha=pitta&city=Mumbai&country=IN&limit=10
    """
    try:
        # Extract query parameters
        query = request.args.get('query', '')
        dosha = request.args.get('dosha', '')
        season = request.args.get('season', '')
        time_of_day = request.args.get('time_of_day', '')
        health_concern = request.args.get('health_concern', '')
        city = request.args.get('city', '')
        country = request.args.get('country', None)
        
        # Get limit parameter with default of 5
        try:
            limit = int(request.args.get('limit', 5))
            if limit < 1:
                limit = 5  # Ensure positive value
        except ValueError:
            limit = 5  # Default if conversion fails
        
        # Validate that dosha parameter is provided
        if not dosha:
            return jsonify({
                'error': 'The dosha parameter is required'
            }), 400
        
        # If city is provided, get weather data regardless of season parameter
        weather_data = None
        if city:
            try:
                weather_data = get_weather_data(city, country)
                # If season is not specified, derive it from weather data
                if not season:
                    season = determine_season(weather_data)
            except Exception as weather_error:
                # Log the error but continue with other parameters
                print(f"Weather data fetch error: {weather_error}")
            
        # Call the recommendation service to get recommendations
        recommendations = get_recommendations(
            query=query,
            dosha=dosha,
            season=season,
            time_of_day=time_of_day,
            health_concern=health_concern,
            weather_data=weather_data,
            top_k=limit
        )
        
        # Return recommendations as JSON
        response_data = {
            'recommendations': recommendations,
            'query_params': {
                'query': query,
                'dosha': dosha,
                'season': season,
                'time_of_day': time_of_day,
                'health_concern': health_concern,
                'limit': limit
            }
        }
        
        # Include weather data in response if available
        if weather_data:
            response_data['weather_data'] = weather_data
            
        return jsonify(response_data)
        
    except Exception as e:
        # Handle any errors that occur during processing
        return jsonify({
            'error': 'Failed to retrieve recommendations',
            'message': str(e)
        }), 500


@recommendations_bp.route('/api/unified_recommendations', methods=['POST'])
def get_unified_recommendations():
    """
    Unified endpoint that integrates dosha determination, weather data, and recommendations.
    
    This endpoint accepts a JSON payload and can determine the user's dosha from quiz responses,
    fetch real-time weather data based on location, and provide personalized Ayurvedic 
    recommendations by combining all these factors.
    
    Request Body (JSON):
        dosha (str, optional): User's dosha type (vata, pitta, kapha, or combinations)
        quiz_responses (dict, optional): Responses to dosha questionnaire (used if dosha is not provided)
        query (str, optional): Free text query for recommendation search
        season (str, optional): Current season (will be derived from weather if not provided)
        time_of_day (str, optional): Time of day (morning, afternoon, evening, night)
        health_concern (str, optional): Specific health concern or condition
        city (str, optional): City name for real-time weather-based recommendations
        country (str, optional): Country code for the city (e.g., 'US', 'IN')
        limit (int, optional): Maximum number of recommendations to return (default: 5)
        
    Returns:
        JSON response containing:
            - recommendations: List of personalized Ayurvedic recommendations
            - dosha_result: Results of dosha determination (if quiz_responses was provided)
            - weather_data: Current weather information (if city was provided)
            - season: Determined or provided season
            - query_params: The parameters used for the recommendation search
            
    Example:
        POST /api/unified_recommendations
        {
            "quiz_responses": {"body_frame": "thin", "skin_type": "dry", ...},
            "city": "Mumbai",
            "country": "IN",
            "health_concern": "digestion",
            "time_of_day": "morning",
            "limit": 10
        }
    """
    try:
        # Parse JSON payload from request
        try:
            data = request.get_json()
            if data is None:
                return jsonify({ 'error': 'Request must contain a valid JSON payload with Content-Type set to application/json' }), 400
        except Exception as json_error:
            return jsonify({ 'error': f'Invalid JSON format: {str(json_error)}' }), 400
            
        # Extract parameters from the request
        dosha = data.get('dosha', '')
        quiz_responses = data.get('quiz_responses')
        query = data.get('query', '')
        season = data.get('season', '')
        time_of_day = data.get('time_of_day', '')
        health_concern = data.get('health_concern', '')
        city = data.get('city', '')
        country = data.get('country')
        
        # Get limit parameter with default of 5
        try:
            limit = int(data.get('limit', 5))
            if limit < 1:
                limit = 5  # Ensure positive value
        except (ValueError, TypeError):
            limit = 5  # Default if conversion fails
        
        # Determine dosha if quiz_responses provided and dosha not specified
        dosha_result = None
        if not dosha and quiz_responses:
            dosha_result = determine_dosha(quiz_responses)
            dosha = dosha_result.get('dosha', '')
            
        # Validate that we have a dosha (either provided or determined)
        if not dosha:
            return jsonify({
                'error': 'Either dosha parameter or valid quiz_responses must be provided'
            }), 400
        
        # Get weather data if city is provided
        weather_data = None
        if city:
            try:
                weather_data = get_weather_data(city, country)
                # If season is not specified, derive it from weather data
                if not season:
                    season = determine_season(weather_data)
            except Exception as weather_error:
                # Log the error but continue with other parameters
                print(f"Weather data fetch error: {weather_error}")
        
        # Get recommendations based on all available parameters
        recommendations = get_recommendations(
            query=query,
            dosha=dosha,
            season=season,
            time_of_day=time_of_day,
            health_concern=health_concern,
            weather_data=weather_data,
            top_k=limit
        )
        
        # Prepare response data
        response_data = {
            'recommendations': recommendations,
            'query_params': {
                'query': query,
                'dosha': dosha,
                'season': season,
                'time_of_day': time_of_day,
                'health_concern': health_concern,
                'limit': limit
            }
        }
        
        # Include dosha determination results if available
        if dosha_result:
            response_data['dosha_result'] = dosha_result
            
        # Include weather data in response if available
        if weather_data:
            response_data['weather_data'] = weather_data
            response_data['season'] = season
            
        return jsonify(response_data), 200
        
    except Exception as e:
        # Handle any errors that occur during processing
        return jsonify({
            'error': 'Failed to retrieve unified recommendations',
            'message': str(e)
        }), 500
