import json
import pytest

from back.app import app, rag_chain

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_valid_message(monkeypatch, client):
    # Monkey patch rag_chain.invoke to return a valid answer
    def fake_invoke(self, data):
        return {"answer": "Test answer"}
    monkeypatch.setattr(type(rag_chain), 'invoke', fake_invoke)

    response = client.post("/api/general", json={"message": "Hello"})
    assert response.status_code == 200
    data = response.get_json()
    assert "response" in data
    assert data["response"] == "Test answer"


def test_invalid_json(client):
    # Send invalid JSON data
    response = client.post("/api/general", data="not a json", content_type="application/json")
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_missing_message_field(client):
    # Valid JSON but missing required 'message' field
    response = client.post("/api/general", json={"msg": "Hello"})
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_rag_invoke_error(monkeypatch, client):
    # Simulate an exception in rag_chain.invoke
    def raise_exception(self, data):
        raise Exception("Test Exception")
    monkeypatch.setattr(type(rag_chain), 'invoke', raise_exception)

    response = client.post("/api/general", json={"message": "Hello"})
    assert response.status_code == 500
    data = response.get_json()
    assert "error" in data
