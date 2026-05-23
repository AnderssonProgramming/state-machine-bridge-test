"""Integration tests for order creation and retrieval endpoints."""

import pytest
from fastapi.testclient import TestClient

BASE = "/orders"


def test_create_order_returns_201(client: TestClient) -> None:
    resp = client.post(BASE, json={"productIds": ["p1", "p2"], "amount": 100.0})
    assert resp.status_code == 201


def test_create_order_returns_pending_state(client: TestClient) -> None:
    resp = client.post(BASE, json={"productIds": ["p1"], "amount": 50.0})
    assert resp.json()["state"] == "Pending"


def test_create_order_returns_order_id(client: TestClient) -> None:
    resp = client.post(BASE, json={"productIds": ["p1"], "amount": 50.0})
    assert "orderId" in resp.json()
    assert resp.json()["orderId"].startswith("ord-")


def test_create_order_returns_init_history(client: TestClient) -> None:
    resp = client.post(BASE, json={"productIds": ["p1"], "amount": 50.0})
    history = resp.json()["history"]
    assert len(history) == 1
    assert history[0]["eventType"] == "init"
    assert history[0]["fromState"] is None
    assert history[0]["toState"] == "Pending"


def test_create_order_invalid_payload_returns_422(client: TestClient) -> None:
    """Missing productIds must be rejected by Pydantic validation."""
    resp = client.post(BASE, json={"amount": 100.0})
    assert resp.status_code == 422


def test_create_order_negative_amount_returns_422(client: TestClient) -> None:
    resp = client.post(BASE, json={"productIds": ["p1"], "amount": -10.0})
    assert resp.status_code == 422


def test_get_order_returns_200(client: TestClient) -> None:
    order_id = client.post(BASE, json={"productIds": ["p1"], "amount": 50.0}).json()[
        "orderId"
    ]
    resp = client.get(f"{BASE}/{order_id}")
    assert resp.status_code == 200
    assert resp.json()["orderId"] == order_id


def test_get_order_nonexistent_returns_404(client: TestClient) -> None:
    resp = client.get(f"{BASE}/does-not-exist")
    assert resp.status_code == 404
    assert resp.json()["error"] == "OrderNotFoundError"


def test_list_orders_returns_all_created(client: TestClient) -> None:
    client.post(BASE, json={"productIds": ["p1"], "amount": 10.0})
    client.post(BASE, json={"productIds": ["p2"], "amount": 20.0})
    resp = client.get(BASE)
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_list_orders_empty_by_default(client: TestClient) -> None:
    resp = client.get(BASE)
    assert resp.status_code == 200
    assert resp.json() == []
