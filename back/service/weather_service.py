"""
Weather Service Module

This module provides functionality to fetch real-time weather data
from the OpenWeatherMap API.
"""
import os
import requests
from typing import Dict, Any, Optional


def get_weather_data(city: str, country: Optional[str] = None) -> Dict[str, Any]:
    """
    Fetches real-time weather data for a specified city using the OpenWeatherMap API.
    
    Args:
        city (str): The name of the city to get weather data for
        country (Optional[str]): The country code (e.g., 'US', 'IN')
        
    Returns:
        Dict[str, Any]: A dictionary containing weather data including:
            - temperature (in Celsius)
            - humidity (percentage)
            - weather description
            - wind speed
            - additional weather parameters
            
    Raises:
        ValueError: If the city name is empty or invalid
        ConnectionError: If there's a network issue connecting to the API
        Exception: For other errors (invalid API key, rate limiting, etc.)
    """
    # Validate input
    if not city or not isinstance(city, str):
        raise ValueError("City name must be a non-empty string")
    
    # Get API key from environment variables
    api_key = os.environ.get('OPENWEATHERMAP_API_KEY')
    if not api_key:
        raise Exception("OpenWeatherMap API key not found in environment variables")
    
    # Build the API request URL
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    
    # Add country to the query if provided
    location_query = city
    if country:
        location_query = f"{city},{country}"
        
    params = {
        'q': location_query,
        'appid': api_key,
        'units': 'metric'  # Get temperature in Celsius
    }
    
    try:
        # Send the GET request to the API
        response = requests.get(base_url, params=params)
        
        # Check if the request was successful
        response.raise_for_status()
        
        # Parse the JSON response
        weather_data = response.json()
        
        # Extract and structure the relevant weather information
        result = {
            'city': city,
            'temperature': weather_data['main']['temp'],
            'humidity': weather_data['main']['humidity'],
            'pressure': weather_data['main']['pressure'],
            'weather_description': weather_data['weather'][0]['description'],
            'wind_speed': weather_data['wind']['speed'],
            'clouds': weather_data['clouds']['all']
        }
        
        # Add feels_like temperature if available
        if 'feels_like' in weather_data['main']:
            result['feels_like'] = weather_data['main']['feels_like']
            
        return result
        
    except requests.exceptions.ConnectionError:
        raise ConnectionError("Failed to connect to the weather API. Please check your internet connection.")
    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors
        if response.status_code == 401:
            raise Exception("Invalid API key or unauthorized access")
        elif response.status_code == 404:
            raise ValueError(f"City '{city}' not found")
        elif response.status_code == 429:
            raise Exception("API rate limit exceeded")
        else:
            raise Exception(f"HTTP error occurred: {e}")
    except requests.exceptions.Timeout:
        raise Exception("Request timed out. The weather service might be experiencing high load.")
    except requests.exceptions.RequestException as e:
        raise Exception(f"An error occurred while fetching weather data: {e}")
    except KeyError as e:
        raise Exception(f"Unexpected response format from weather API: {e}")
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {e}")


def determine_season(weather_data: Dict[str, Any]) -> str:
    """
    Determines the season based on weather data.
    
    Args:
        weather_data (Dict[str, Any]): Weather data dictionary containing at least
                                      'temperature' and 'weather_description' keys
    
    Returns:
        str: The determined season ('summer', 'winter', 'monsoon', or 'spring')
    
    Note:
        Uses simple temperature and weather description heuristics:
        - Temperature >= 30°C: 'summer'
        - Temperature <= 15°C: 'winter'
        - Contains 'rain' in description: 'monsoon'
        - Otherwise: 'spring'
    """
    temperature = weather_data.get('temperature', 20)  # Default to 20°C if not found
    weather_description = weather_data.get('weather_description', '').lower()
    
    if temperature >= 30:
        return 'summer'
    elif temperature <= 15:
        return 'winter'
    elif 'rain' in weather_description:
        return 'monsoon'
    else:
        return 'spring'
