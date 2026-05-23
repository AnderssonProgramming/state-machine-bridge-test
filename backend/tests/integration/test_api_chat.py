"""Integration tests for the AI chatbot endpoint."""

from fastapi.testclient import TestClient

BASE = "/chat"


def test_chat_returns_200(client: TestClient) -> None:
    """The /chat endpoint must return 200 and a mocked reply."""
    resp = client.post(BASE, json={"message": "Hello", "conversationHistory": []})
    assert resp.status_code == 200
    assert resp.json()["reply"] == "Mock reply."


def test_chat_with_history_returns_200(client: TestClient) -> None:
    """The /chat endpoint should handle conversation history."""
    resp = client.post(
        BASE,
        json={
            "message": "What is the next step?",
            "conversationHistory": [
                {"role": "user", "content": "How does this work?"},
                {"role": "assistant", "content": "It works via a state machine."},
            ],
        },
    )
    assert resp.status_code == 200
    assert resp.json()["reply"] == "Mock reply."


def test_chat_invalid_payload_returns_422(client: TestClient) -> None:
    """Missing message must be rejected by Pydantic validation."""
    resp = client.post(BASE, json={"conversationHistory": []})
    assert resp.status_code == 422
