from src.domain.order import Order
from src.repositories.memory import InMemorySupportRepository
from src.services.rules.action_handlers.add_fee import AddFeeHandler
from src.services.rules.action_handlers.add_tax import AddTaxHandler
from src.services.rules.action_handlers.base import ActionContext
from src.services.rules.action_handlers.create_support_ticket import (
    CreateSupportTicketHandler,
)

CTX = ActionContext(rule_id="rule-abc", rule_version=1, trigger="order_created")


def test_create_support_ticket(support_repo: InMemorySupportRepository) -> None:
    handler = CreateSupportTicketHandler(support_repo)
    order = Order(product_ids=["p1"], amount=1500.0)
    result = handler.execute(order, {"reason": "test"}, CTX)
    assert result.success is True
    assert result.details["ticketId"].startswith("ticket-")


def test_add_tax_appends_adjustment() -> None:
    handler = AddTaxHandler()
    order = Order(product_ids=["p1"], amount=1000.0)
    result = handler.execute(order, {"percentage": 19, "label": "VAT"}, CTX)
    assert result.success is True
    assert len(order.adjustments) == 1
    assert order.adjustments[0].amount == 190.0
    assert order.total_amount == 1190.0


def test_add_tax_is_idempotent() -> None:
    handler = AddTaxHandler()
    order = Order(product_ids=["p1"], amount=1000.0)
    handler.execute(order, {"percentage": 19}, CTX)
    handler.execute(order, {"percentage": 19}, CTX)
    assert len(order.adjustments) == 1


def test_add_fee_supports_negative_amounts() -> None:
    handler = AddFeeHandler()
    order = Order(product_ids=["p1"], amount=100.0)
    result = handler.execute(order, {"amount": -10.0, "label": "promo"}, CTX)
    assert result.success is True
    assert order.total_amount == 90.0
