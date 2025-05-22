import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_weather_service():
    """Test weather service functionality"""
    response = requests.get('http://localhost:8080/api/weather', params={'city': 'New York'})
    assert response.status_code == 200
    data = response.json()
    assert 'temperature' in data
    assert 'humidity' in data
    print("Weather service test passed")

def test_dosha_service():
    """Test dosha service functionality"""
    response = requests.post('http://localhost:8080/api/dosha', json={
        'questions': {
            'body_type': 'slim',
            'digestion': 'good',
            'sleep': 'light'
        }
    })
    assert response.status_code == 200
    data = response.json()
    assert 'dosha' in data
    print("Dosha service test passed")

def test_recommendation_service():
    """Test recommendation service functionality"""
    response = requests.get('http://localhost:8080/api/recommendations', params={'dosha': 'vata'})
    assert response.status_code == 200
    data = response.json()
    assert 'recommendations' in data
    print("Recommendation service test passed")

def test_chat_service():
    """Test chat service functionality"""
    response = requests.post('http://localhost:8080/api/chat', json={
        'message': 'What are some ayurvedic remedies for cold?'
    })
    assert response.status_code == 200
    data = response.json()
    assert 'rag_response' in data
    assert 'agent_response' in data
    print("Chat service test passed")

def test_metrics_service():
    """Test metrics service functionality"""
    response = requests.get('http://localhost:8080/api/metrics/visualization')
    assert response.status_code == 200
    data = response.json()
    assert 'performance_metrics' in data
    assert 'user_engagement' in data
    print("Metrics service test passed")

def main():
    print("Starting component tests...")
    test_weather_service()
    test_dosha_service()
    test_recommendation_service()
    test_chat_service()
    test_metrics_service()
    print("All component tests passed!")

if __name__ == "__main__":
    main()
