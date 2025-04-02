import json
import pytest


# Fixtures for the test client
@pytest.fixture
def client():
    from back.app import app
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


# Fake functions for monkeypatching external dependencies

def fake_get_recommendations(query=None, dosha=None, season=None, time_of_day=None, health_concern=None, weather_data=None, top_k=5):
    return [{
        'content': 'Test recommendation',
        'metadata': {},
        'relevance_score': 1.0,
        'classification': 'general'
    }]


def fake_get_weather_data(city, country):
    return {
        "city": city,
        "temperature": 25,
        "humidity": 60,
        "pressure": 1013,
        "weather_description": "clear sky",
        "wind_speed": 5,
        "clouds": 0
    }


def fake_determine_season(weather_data):
    return "summer"


def fake_determine_dosha(quiz_responses):
    return {"dosha": "vata"}


# Test cases for GET /api/recommendations

def test_get_recommendations_missing_dosha(client):
    # When dosha parameter is missing, the endpoint should return error
    response = client.get('/api/recommendations?query=digestion')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'] == 'The dosha parameter is required'


def test_get_recommendations_valid(client, monkeypatch):
    # Monkeypatch the external dependencies
    from back.service.recommendation_service import get_recommendations
    from back.service.weather_service import get_weather_data, determine_season
    monkeypatch.setattr('back.service.recommendation_service.get_recommendations', fake_get_recommendations)
    monkeypatch.setattr('back.routes.recommendations_routes.get_weather_data', fake_get_weather_data)
    monkeypatch.setattr('back.routes.recommendations_routes.determine_season', fake_determine_season)

    # Valid request with dosha and city for weather data simulation
    response = client.get('/api/recommendations?dosha=vata&query=digestion&city=TestCity&country=US&limit=3')
    assert response.status_code == 200
    data = json.loads(response.data)
    # Check that recommendations list is returned
    assert 'recommendations' in data
    assert isinstance(data['recommendations'], list)
    # Check that weather_data is included
    assert 'weather_data' in data
    # Check query_params contains expected values
    assert data['query_params']['dosha'] == 'vata'
    assert data['query_params']['limit'] == 3


# Test cases for POST /api/unified_recommendations

def test_unified_recommendations_missing_payload(client):
    # POST without JSON payload should return an error
    response = client.post('/api/unified_recommendations')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data


def test_unified_recommendations_no_dosha_and_no_quiz(client):
    # POST with empty JSON payload or missing both dosha and quiz_responses
    payload = {"query": "digestion"}
    response = client.post('/api/unified_recommendations', data=json.dumps(payload), content_type='application/json')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    # Since neither dosha nor quiz_responses provided


def test_unified_recommendations_valid_quiz(client, monkeypatch):
    # Monkeypatch the external dependencies for unified endpoint
    from back.service.recommendation_service import get_recommendations
    from back.service.weather_service import get_weather_data, determine_season
    from back.service.dosha_service import determine_dosha
    monkeypatch.setattr('back.service.recommendation_service.get_recommendations', fake_get_recommendations)
    monkeypatch.setattr('back.routes.recommendations_routes.get_weather_data', fake_get_weather_data)
    monkeypatch.setattr('back.routes.recommendations_routes.determine_season', fake_determine_season)
    monkeypatch.setattr('back.service.dosha_service.determine_dosha', fake_determine_dosha)

    # Valid unified recommendations request using quiz_responses
    payload = {
        "quiz_responses": {"some_question": "some_answer"},
        "query": "digestion",
        "city": "TestCity",
        "country": "US",
        "health_concern": "stomach discomfort",
        "time_of_day": "morning",
        "limit": 2
    }
    response = client.post('/api/unified_recommendations', data=json.dumps(payload), content_type='application/json')
    assert response.status_code == 200
    data = json.loads(response.data)
    # Check that recommendations were returned
    assert 'recommendations' in data
    # Check that dosha has been determined
    assert 'dosha_result' in data
    # Check that weather data is included
    assert 'weather_data' in data
    # Validate query parameters
    query_params = data.get('query_params', {})
    assert query_params.get('time_of_day') == 'morning'
    assert query_params.get('limit') == 2
