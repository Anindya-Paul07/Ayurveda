"""
Weather API Endpoints

This module handles all weather-related API endpoints including:
- Current weather conditions
- Weather forecasts
- Seasonal recommendations based on weather
"""

from flask import request, jsonify, current_app
from ..service.weather_service import WeatherService
from . import api_v1
from functools import wraps
import logging

logger = logging.getLogger(__name__)
weather_service = WeatherService()

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

@api_v1.route('/weather/current', methods=['GET'])
@handle_errors
def get_current_weather():
    """
    Get current weather for a location.
    
    Query Parameters:
        location: City name or coordinates (lat,lon)
        units: Units of measurement (metric/imperial)
        
    Returns:
        Current weather data for the specified location
    """
    location = request.args.get('location')
    units = request.args.get('units', 'metric')
    
    if not location:
        return jsonify({
            'status': 'error',
            'message': 'Location parameter is required'
        }), 400
    
    try:
        weather_data = weather_service.get_current_weather(location, units=units)
        return jsonify({
            'status': 'success',
            'data': weather_data
        })
    except Exception as e:
        logger.error(f"Error fetching current weather: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': 'Failed to fetch current weather',
            'error': str(e)
        }), 500

@api_v1.route('/weather/forecast', methods=['GET'])
@handle_error
def get_weather_forecast():
    """
    Get weather forecast for a location.
    
    Query Parameters:
        location: City name or coordinates (lat,lon)
        days: Number of days to forecast (1-10)
        units: Units of measurement (metric/imperial)
        
    Returns:
        Weather forecast data for the specified location
    """
    location = request.args.get('location')
    days = request.args.get('days', 5, type=int)
    units = request.args.get('units', 'metric')
    
    if not location:
        return jsonify({
            'status': 'error',
            'message': 'Location parameter is required'
        }), 400
    
    # Validate days parameter
    days = max(1, min(days, 10))  # Clamp between 1 and 10
    
    try:
        forecast_data = weather_service.get_forecast(location, days=days, units=units)
        return jsonify({
            'status': 'success',
            'data': forecast_data
        })
    except Exception as e:
        logger.error(f"Error fetching weather forecast: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': 'Failed to fetch weather forecast',
            'error': str(e)
        }), 500

@api_v1.route('/weather/seasonal/recommendations', methods=['GET'])
@handle_errors
def get_seasonal_recommendations():
    """
    Get seasonal recommendations based on current weather and location.
    
    Query Parameters:
        location: City name or coordinates (lat,lon)
        dosha: User's dosha type (vata, pitta, kapha)
        
    Returns:
        Seasonal recommendations for diet, lifestyle, and health
    """
    location = request.args.get('location')
    dosha = request.args.get('dosha')
    
    if not location:
        return jsonify({
            'status': 'error',
            'message': 'Location parameter is required'
        }), 400
    
    try:
        recommendations = weather_service.get_seasonal_recommendations(
            location=location,
            dosha=dosha
        )
        
        return jsonify({
            'status': 'success',
            'data': recommendations
        })
    except Exception as e:
        logger.error(f"Error generating seasonal recommendations: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': 'Failed to generate seasonal recommendations',
            'error': str(e)
        }), 500

@api_v1.route('/weather/health/advisory', methods=['GET'])
@handle_errors
def get_health_advisory():
    """
    Get health advisory based on current and forecasted weather.
    
    Query Parameters:
        location: City name or coordinates (lat,lon)
        health_conditions: Comma-separated list of health conditions
        
    Returns:
        Health advisory based on weather conditions
    """
    location = request.args.get('location')
    health_conditions = request.args.get('health_conditions', '').split(',')
    
    if not location:
        return jsonify({
            'status': 'error',
            'message': 'Location parameter is required'
        }), 400
    
    try:
        advisory = weather_service.get_health_advisory(
            location=location,
            health_conditions=[h for h in health_conditions if h]
        )
        
        return jsonify({
            'status': 'success',
            'data': advisory
        })
    except Exception as e:
        logger.error(f"Error generating health advisory: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': 'Failed to generate health advisory',
            'error': str(e)
        }), 500
