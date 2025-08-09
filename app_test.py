import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from app import app  

client = TestClient(app)

@pytest.fixture
def mock_openai_response():
    class Choice:
        def __init__(self):
            self.message = type("Message", (), {"content": "This is a generated response"})
    class Response:
        def __init__(self):
            self.choices = [Choice()]
    return Response()

def test_read_index():
    response = client.get("/")
    assert response.status_code == 200
    assert "<html" in response.text.lower()  

@patch("app.client.chat.completions.create")
def test_generate_text_success(mock_create, mock_openai_response):
    mock_create.return_value = mock_openai_response

    response = client.post("/generate", data={"prompt": "Hello"})
    assert response.status_code == 200
    assert "Your Prompt:" in response.text
    assert "Hello" in response.text
    assert "This is a generated response" in response.text

@patch("app.client.chat.completions.create")
def test_generate_text_no_response(mock_create):
    class EmptyResponse:
        choices = []
    mock_create.return_value = EmptyResponse()

    response = client.post("/generate", data={"prompt": "Hello"})
    assert response.status_code == 500
    assert "No response from the model" in response.text

@patch("app.client.chat.completions.create")
def test_generate_text_exception(mock_create):
    mock_create.side_effect = Exception("API error")

    response = client.post("/generate", data={"prompt": "Hello"})
    assert response.status_code == 500
    assert "An error occured" in response.text
