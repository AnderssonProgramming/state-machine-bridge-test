"""Unit tests for OrderService business logic."""

import pytest
from src.domain.exceptions import InvalidTransitionError, OrderNotFoundError
from src.domain.states import OrderState
from src.repositories.memory import InMemoryOrderRepository, InMemorySupportRepository
from src.services.order_service import OrderService

PRODUCT_IDS = ["p-1", "p-2"]

# ── create_order ──────────────────────────────────────────────────────────────


def test_create_order_returns_pending_state(order_service: OrderService) -> None:
    order = order_service.create_order(PRODUCT_IDS, 100.0)
    assert order.state == OrderState.PENDING


def test_create_order_persists_to_repository(
    order_service: OrderService, order_repo: InMemoryOrderRepository
) -> None:
    order = order_service.create_order(PRODUCT_IDS, 100.0)
    assert order_repo.get_by_id(order.order_id) is not None


def test_create_order_stores_correct_product_ids(order_service: OrderService) -> None:
    order = order_service.create_order(PRODUCT_IDS, 100.0)
    assert order.product_ids == PRODUCT_IDS


def test_create_order_stores_correct_amount(order_service: OrderService) -> None:
    order = order_service.create_order(PRODUCT_IDS, 249.99)
    assert order.amount == 249.99


# ── apply_event ───────────────────────────────────────────────────────────────


def test_apply_event_transitions_state(order_service: OrderService) -> None:
    order = order_service.create_order(PRODUCT_IDS, 100.0)
    _, updated = order_service.apply_event(order.order_id, "noVerificationNeeded", {})
    assert updated.state == OrderState.PENDING_PAYMENT


def test_apply_event_appends_to_history(order_service: OrderService) -> None:
    order = order_service.create_order(PRODUCT_IDS, 100.0)
    order_service.apply_event(order.order_id, "noVerificationNeeded", {})
    persisted = order_service.get_order(order.order_id)
    assert len(persisted.history) == 2


def test_apply_event_raises_for_unknown_order(order_service: OrderService) -> None:
    with pytest.raises(OrderNotFoundError):
        order_service.apply_event("nonexistent-id", "noVerificationNeeded", {})


def test_apply_event_raises_for_invalid_transition(order_service: OrderService) -> None:
    order = order_service.create_order(PRODUCT_IDS, 100.0)
    with pytest.raises(InvalidTransitionError):
        order_service.apply_event(order.order_id, "itemDispatched", {})


def test_apply_event_raises_for_unknown_event_type(order_service: OrderService) -> None:
    order = order_service.create_order(PRODUCT_IDS, 100.0)
    with pytest.raises(ValueError):
        order_service.apply_event(order.order_id, "notARealEvent", {})


# ── paymentFailed business rule (Requirement 4) ───────────────────────────────


def test_payment_failed_below_threshold_creates_no_ticket(
    order_service: OrderService, support_repo: InMemorySupportRepository
) -> None:
    """Orders at or below $1,000 must NOT generate a support ticket."""
    order = order_service.create_order(PRODUCT_IDS, 999.99)
    order_service.apply_event(order.order_id, "paymentFailed", {})
    assert len(support_repo._tickets) == 0


def test_payment_failed_exactly_threshold_creates_no_ticket(
    order_service: OrderService, support_repo: InMemorySupportRepository
) -> None:
    """An order at exactly $1,000 must NOT generate a ticket (> check, not >=)."""
    order = order_service.create_order(PRODUCT_IDS, 1000.0)
    order_service.apply_event(order.order_id, "paymentFailed", {})
    assert len(support_repo._tickets) == 0


def test_payment_failed_above_threshold_creates_ticket(
    order_service: OrderService, support_repo: InMemorySupportRepository
) -> None:
    """Orders above $1,000 must generate exactly one support ticket."""
    order = order_service.create_order(PRODUCT_IDS, 1000.01)
    order_service.apply_event(order.order_id, "paymentFailed", {})
    assert len(support_repo._tickets) == 1


def test_payment_failed_above_threshold_still_transitions(
    order_service: OrderService,
) -> None:
    """Even when a support ticket is created, the order must reach Cancelled."""
    order = order_service.create_order(PRODUCT_IDS, 1500.0)
    _, updated = order_service.apply_event(order.order_id, "paymentFailed", {})
    assert updated.state == OrderState.CANCELLED


# ── get_order / list_orders ───────────────────────────────────────────────────


def test_get_order_returns_order(order_service: OrderService) -> None:
    order = order_service.create_order(PRODUCT_IDS, 100.0)
    fetched = order_service.get_order(order.order_id)
    assert fetched.order_id == order.order_id


def test_get_order_raises_for_missing(order_service: OrderService) -> None:
    with pytest.raises(OrderNotFoundError):
        order_service.get_order("does-not-exist")


def test_list_orders_returns_all(order_service: OrderService) -> None:
    order_service.create_order(["p1"], 10.0)
    order_service.create_order(["p2"], 20.0)
    assert len(order_service.list_orders()) == 2


# ── available_events ──────────────────────────────────────────────────────────


def test_available_events_returns_pending_transitions(
    order_service: OrderService,
) -> None:
    order = order_service.create_order(PRODUCT_IDS, 100.0)
    events = order_service.available_events(order.order_id)
    event_values = [e.value for e in events]
    assert "noVerificationNeeded" in event_values
    assert "pendingBiometricalVerification" in event_values
    assert "orderCancelledByUser" in event_values
