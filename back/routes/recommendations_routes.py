"""
Recommendations Routes Module

This module defines the API endpoints for retrieving Ayurvedic recommendations
based on user queries or dosha profiles using Pinecone vector similarity search.
"""

from flask import Blueprint, request, jsonify
from ..service.recommendation_service import get_recommendations
from ..service.weather_service import get_weather_data, determine_season

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
