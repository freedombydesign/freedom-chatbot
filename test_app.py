import json
import pytest
from app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_chat_empty_message(client):
    response = client.post("/chat", json={"message": "   "})
    assert response.status_code == 400
    assert response.get_json()["error"] == "Empty message."

def test_chat_valid_message(monkeypatch, client):
    class DummyResponse:
        choices = [type("c", (), {"message": {"content": "Hello back!"}})()]

    def fake_create(**kwargs):
        return DummyResponse()

    monkeypatch.setattr("openai.ChatCompletion.create", fake_create)

    response = client.post("/chat", json={"message": "Hello"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["reply"] == "Hello back!"

def test_index_route(client):
    response = client.get("/")
    # If index.html exists in your project root, this will return 200
    assert response.status_code in (200, 404)
    # You can adjust this once you confirm index.html is deployed
