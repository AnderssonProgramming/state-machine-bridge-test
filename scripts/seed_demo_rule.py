"""
Seeds the demo rule that expresses Requirement 4 as data instead of code.

Usage:
    python scripts/seed_demo_rule.py
    python scripts/seed_demo_rule.py https://your-api-gateway-url.amazonaws.com
"""
import json
import sys
import urllib.request

DEMO_RULE = {
    "name": "High-value payment failure review",
    "description": (
        "Creates a support ticket when a payment fails on an order whose "
        "amount is greater than $1,000 USD. "
        "This rule replaces the hardcoded PaymentFailedHandler from the original test."
    ),
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


def main() -> None:
    base_url = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://localhost:8000"
    req = urllib.request.Request(
        f"{base_url}/rules",
        data=json.dumps(DEMO_RULE).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        body = json.loads(resp.read().decode())
    print(f"Seeded rule {body['ruleId']} (v{body['version']})")


if __name__ == "__main__":
    main()
