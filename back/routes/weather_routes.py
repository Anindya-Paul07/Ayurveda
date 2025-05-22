from flask import Blueprint, request, jsonify
from service.weather_service import get_weather_data

# Create a blueprint for weather routes
weather_bp = Blueprint('weather', __name__)

@weather_bp.route('/api/weather', methods=['GET'])
def get_weather():
    """
    Retrieve real-time weather data based on location parameters.
    
    Query Parameters:
        city (str, required): The name of the city
        country (str, optional): The country code (e.g., 'US', 'IN')
    
    Returns:
        JSON response with the following structure:
        {
            "temperature": float,
            "humidity": float,
            "weather_condition": str,
            "location": str,
            "timestamp": str
        }
        
    Status Codes:
        200: Weather data successfully retrieved
        400: Missing required parameters
        500: Error fetching weather data
    """
    # Extract query parameters
    city = request.args.get('city')
    country = request.args.get('country')
    
    # Validate required parameters
    if not city:
        return jsonify({
            'error': 'Missing required parameter: city'
        }), 400
    
    try:
        # Call the weather service to get weather data
        weather_data = get_weather_data(city, country)
        
        # Return the weather data as JSON
        return jsonify(weather_data), 200
    
    except Exception as e:
        # Handle any errors from the weather service
        return jsonify({
            'error': f'Failed to fetch weather data: {str(e)}'
        }), 500
