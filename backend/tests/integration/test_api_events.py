"""Integration tests for order event transitions and available-events endpoint."""

from fastapi.testclient import TestClient

BASE = "/orders"


def _create_order(client: TestClient, amount: float = 100.0) -> str:
    """Helper: create an order and return its id."""
    return client.post(
        BASE, json={"productIds": ["p1"], "amount": amount}
    ).json()["orderId"]


# ── Single valid transition ────────────────────────────────────────────────────


def test_valid_transition_returns_200(client: TestClient) -> None:
    order_id = _create_order(client)
    resp = client.post(
        f"{BASE}/{order_id}/events",
        json={"eventType": "noVerificationNeeded"},
    )
    assert resp.status_code == 200


def test_valid_transition_returns_correct_states(client: TestClient) -> None:
    order_id = _create_order(client)
    resp = client.post(
        f"{BASE}/{order_id}/events",
        json={"eventType": "noVerificationNeeded"},
    )
    body = resp.json()
    assert body["previousState"] == "Pending"
    assert body["currentState"] == "PendingPayment"
    assert body["eventType"] == "noVerificationNeeded"


def test_invalid_transition_returns_422(client: TestClient) -> None:
    """Firing an event with no defined transition must return 422."""
    order_id = _create_order(client)
    resp = client.post(
        f"{BASE}/{order_id}/events",
        json={"eventType": "itemDispatched"},  # not valid from Pending
    )
    assert resp.status_code == 422
    assert resp.json()["error"] == "InvalidTransitionError"


def test_unknown_event_type_returns_422(client: TestClient) -> None:
    """An event type not in the enum must also return 422."""
    order_id = _create_order(client)
    resp = client.post(
        f"{BASE}/{order_id}/events",
        json={"eventType": "completelyMadeUp"},
    )
    assert resp.status_code == 422


def test_event_on_nonexistent_order_returns_404(client: TestClient) -> None:
    resp = client.post(
        f"{BASE}/ghost-order/events",
        json={"eventType": "noVerificationNeeded"},
    )
    assert resp.status_code == 404


# ── paymentFailed business rule ───────────────────────────────────────────────


def test_payment_failed_low_value_transitions_to_cancelled(
    client: TestClient,
) -> None:
    """paymentFailed on a ≤ $1,000 order must reach Cancelled (no side effects)."""
    order_id = _create_order(client, amount=500.0)
    resp = client.post(
        f"{BASE}/{order_id}/events", json={"eventType": "paymentFailed"}
    )
    assert resp.status_code == 200
    assert resp.json()["currentState"] == "Cancelled"


def test_payment_failed_high_value_still_transitions_to_cancelled(
    client: TestClient,
) -> None:
    """paymentFailed on a > $1,000 order must also reach Cancelled (+ ticket side effect)."""
    order_id = _create_order(client, amount=1500.0)
    resp = client.post(
        f"{BASE}/{order_id}/events", json={"eventType": "paymentFailed"}
    )
    assert resp.status_code == 200
    assert resp.json()["currentState"] == "Cancelled"


# ── Full happy-path lifecycle ─────────────────────────────────────────────────


def test_full_order_lifecycle_to_delivered(client: TestClient) -> None:
    """An order must be able to travel the complete path to Delivered."""
    order_id = _create_order(client)

    lifecycle = [
        ("pendingBiometricalVerification", "OnHold"),
        ("biometricalVerificationSuccessful", "PendingPayment"),
        ("paymentSuccessful", "Confirmed"),
        ("preparingShipment", "Processing"),
        ("itemDispatched", "Shipped"),
        ("itemReceivedByCustomer", "Delivered"),
    ]

    for event_type, expected_state in lifecycle:
        resp = client.post(
            f"{BASE}/{order_id}/events",
            json={"eventType": event_type},
        )
        assert resp.status_code == 200, f"failed on {event_type}: {resp.json()}"
        assert resp.json()["currentState"] == expected_state


def test_history_grows_with_each_transition(client: TestClient) -> None:
    """The history log must record every transition (Requirement 6)."""
    order_id = _create_order(client)
    events = ["noVerificationNeeded", "paymentSuccessful", "preparingShipment"]
    for event_type in events:
        client.post(f"{BASE}/{order_id}/events", json={"eventType": event_type})

    order = client.get(f"{BASE}/{order_id}").json()
    # init + 3 events = 4 entries
    assert len(order["history"]) == 4


def test_cancellation_from_shipped(client: TestClient) -> None:
    """Universal cancellation must work from any non-terminal state, e.g. Shipped."""
    order_id = _create_order(client)
    for event_type in [
        "noVerificationNeeded",
        "paymentSuccessful",
        "preparingShipment",
        "itemDispatched",
    ]:
        client.post(f"{BASE}/{order_id}/events", json={"eventType": event_type})

    resp = client.post(
        f"{BASE}/{order_id}/events", json={"eventType": "orderCancelledByUser"}
    )
    assert resp.status_code == 200
    assert resp.json()["currentState"] == "Cancelled"


def test_cancellation_blocked_from_delivered(client: TestClient) -> None:
    """orderCancelledByUser must be rejected once the order is Delivered."""
    order_id = _create_order(client)
    for event_type in [
        "noVerificationNeeded",
        "paymentSuccessful",
        "preparingShipment",
        "itemDispatched",
        "itemReceivedByCustomer",
    ]:
        client.post(f"{BASE}/{order_id}/events", json={"eventType": event_type})

    resp = client.post(
        f"{BASE}/{order_id}/events", json={"eventType": "orderCancelledByUser"}
    )
    assert resp.status_code == 422


# ── available-events endpoint ─────────────────────────────────────────────────


def test_available_events_for_pending_order(client: TestClient) -> None:
    order_id = _create_order(client)
    resp = client.get(f"{BASE}/{order_id}/available-events")
    assert resp.status_code == 200
    body = resp.json()
    assert body["state"] == "Pending"
    assert "noVerificationNeeded" in body["availableEvents"]
    assert "orderCancelledByUser" in body["availableEvents"]


def test_available_events_after_transition(client: TestClient) -> None:
    order_id = _create_order(client)
    client.post(
        f"{BASE}/{order_id}/events", json={"eventType": "noVerificationNeeded"}
    )
    resp = client.get(f"{BASE}/{order_id}/available-events")
    body = resp.json()
    assert body["state"] == "PendingPayment"
    assert "paymentSuccessful" in body["availableEvents"]
    assert "noVerificationNeeded" not in body["availableEvents"]
