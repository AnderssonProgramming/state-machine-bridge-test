from fastapi.testclient import TestClient

DEMO_RULE = {
    "name": "High-value payment failure review",
    "trigger": "event:paymentFailed",
    "condition": {
        "type": "comparison",
        "field": "amount",
        "operator": "gt",
        "value": 1000,
    },
    "actions": [
        {
            "type": "create_support_ticket",
            "params": {"reason": "High-value payment failure requires manual review."},
        }
    ],
    "priority": 100,
    "enabled": True,
}


def test_create_rule_returns_201(client: TestClient) -> None:
    resp = client.post("/rules", json=DEMO_RULE)
    assert resp.status_code == 201
    body = resp.json()
    assert body["ruleId"].startswith("rule-")
    assert body["version"] == 1


def test_list_rules_filters_by_trigger(client: TestClient) -> None:
    client.post("/rules", json=DEMO_RULE)
    client.post(
        "/rules", json={**DEMO_RULE, "name": "other", "trigger": "order_created"}
    )
    resp = client.get("/rules", params={"trigger": "event:paymentFailed"})
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_dry_run_matches(client: TestClient) -> None:
    rule_id = client.post("/rules", json=DEMO_RULE).json()["ruleId"]
    resp = client.post(
        f"/rules/{rule_id}/dry-run", json={"productIds": ["p1"], "amount": 2000.0}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["matched"] is True
    assert body["actions"][0]["details"]["dryRun"] is True


def test_dry_run_no_match(client: TestClient) -> None:
    rule_id = client.post("/rules", json=DEMO_RULE).json()["ruleId"]
    resp = client.post(
        f"/rules/{rule_id}/dry-run", json={"productIds": ["p1"], "amount": 500.0}
    )
    assert resp.json()["matched"] is False


def test_toggle_enabled_bumps_version(client: TestClient) -> None:
    rule_id = client.post("/rules", json=DEMO_RULE).json()["ruleId"]
    resp = client.patch(f"/rules/{rule_id}/enabled", json={"enabled": False})
    assert resp.status_code == 200
    assert resp.json()["enabled"] is False
    assert resp.json()["version"] == 2


def test_invalid_condition_returns_422(client: TestClient) -> None:
    bad = {**DEMO_RULE, "condition": {"type": "comparison"}}
    resp = client.post("/rules", json=bad)
    assert resp.status_code == 422


def test_delete_rule(client: TestClient) -> None:
    rule_id = client.post("/rules", json=DEMO_RULE).json()["ruleId"]
    assert client.delete(f"/rules/{rule_id}").status_code == 204
    assert client.get(f"/rules/{rule_id}").status_code == 404


def test_end_to_end_rule_fires_on_payment_failed(client: TestClient) -> None:
    client.post("/rules", json=DEMO_RULE)
    order_id = client.post(
        "/orders", json={"productIds": ["p1"], "amount": 1500.0}
    ).json()["orderId"]
    resp = client.post(
        f"/orders/{order_id}/events", json={"eventType": "paymentFailed"}
    )
    assert resp.status_code == 200
    assert resp.json()["currentState"] == "Cancelled"
    logs = client.get(f"/rules/_logs/by-order/{order_id}").json()
    assert any(log["matched"] for log in logs)
