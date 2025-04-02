import pytest

# Import the Flask application from the backend
from back.app import app


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


def test_dosha_valid_input(client):
    # Valid payload with all required responses
    payload = {
        "responses": {
            "body_frame": "thin",
            "skin_type": "dry",
            "hair_type": "dry",
            "appetite": "variable",
            "digestion": "irregular",
            "weight_tendency": "difficult_to_gain",
            "temperature_preference": "warm",
            "sleep_pattern": "light",
            "energy_level": "variable",
            "mental_activity": "restless",
            "emotional_tendency": "anxious",
            "speech_pattern": "fast"
        }
    }
    response = client.post('/api/dosha', json=payload)
    data = response.get_json()
    
    # Ensure that a valid response is returned
    assert response.status_code == 200
    assert 'dosha' in data
    assert 'message' in data


def test_dosha_missing_responses(client):
    # Payload without the 'responses' key
    payload = {"no_responses": {}}
    response = client.post('/api/dosha', json=payload)
    data = response.get_json()

    # Expect 400 for missing valid input
    assert response.status_code == 400
    assert 'error' in data


def test_dosha_empty_responses(client):
    # Payload with an empty dictionary for responses
    payload = {"responses": {}}
    response = client.post('/api/dosha', json=payload)
    data = response.get_json()

    # Expect 400 for empty responses
    assert response.status_code == 400
    assert 'error' in data


def test_dosha_non_dict_responses(client):
    # Payload where responses is not a dictionary
    payload = {"responses": "not a dict"}
    response = client.post('/api/dosha', json=payload)
    data = response.get_json()

    # Expect 400 error for invalid type of responses
    assert response.status_code == 400
    assert 'error' in data


def test_dosha_invalid_json(client):
    # Sending invalid JSON payload
    response = client.post('/api/dosha', data="not a json")

    # The endpoint should handle invalid JSON and return 400
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
