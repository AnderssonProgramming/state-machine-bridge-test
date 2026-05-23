"""Integration tests for main application endpoints."""

from fastapi.testclient import TestClient


def test_health_check(client: TestClient) -> None:
    """The /health endpoint must return OK status."""
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
