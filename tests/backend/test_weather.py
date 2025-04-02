import pytest
from flask import Flask

# Import the blueprint for weather routes
from back.routes.weather_routes import weather_bp


# Dummy implementation for get_weather_data to simulate a valid response

def dummy_get_weather_data(city, country=None):
    return {
        'city': city,
        'temperature': 25.0,
        'humidity': 50,
        'pressure': 1013,
        'weather_description': 'clear sky',
        'wind_speed': 5.5,
        'clouds': 10
    }


@pytest.fixture
def app():
    app = Flask(__name__)
    app.register_blueprint(weather_bp)
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    return app.test_client()


def test_get_weather_valid(client, monkeypatch):
    # Patch the get_weather_data function to use the dummy implementation
    monkeypatch.setattr('back.service.weather_service.get_weather_data', dummy_get_weather_data)
    
    # Send a request with valid city and country parameters
    response = client.get('/api/weather?city=London&country=UK')
    
    assert response.status_code == 200
    data = response.get_json()
    
    # Verify that the response contains expected weather data keys
    expected_keys = ['city', 'temperature', 'humidity', 'pressure', 'weather_description', 'wind_speed', 'clouds']
    for key in expected_keys:
        assert key in data
    
    # Verify that the 'city' field matches the query
    assert data['city'] == 'London'


def test_get_weather_missing_city(client):
    # Send request without the required 'city' parameter
    response = client.get('/api/weather')
    
    assert response.status_code == 400
    data = response.get_json()
    
    # Verify that the error message indicates missing city parameter
    assert 'error' in data
    assert 'Missing required parameter: city' in data['error']
