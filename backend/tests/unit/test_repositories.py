"""Unit tests for in-memory repository implementations."""

import threading

import pytest

from src.domain.order import Order
from src.repositories.memory import InMemoryOrderRepository, InMemorySupportRepository

PRODUCT_IDS = ["p-x"]
AMOUNT = 99.0


# ── InMemoryOrderRepository ───────────────────────────────────────────────────


def test_save_and_get_by_id(order_repo: InMemoryOrderRepository) -> None:
    order = Order(product_ids=PRODUCT_IDS, amount=AMOUNT)
    order_repo.save(order)
    result = order_repo.get_by_id(order.order_id)
    assert result is not None
    assert result.order_id == order.order_id


def test_get_by_id_returns_none_for_missing(
    order_repo: InMemoryOrderRepository,
) -> None:
    assert order_repo.get_by_id("nonexistent") is None


def test_list_all_returns_all_saved(order_repo: InMemoryOrderRepository) -> None:
    orders = [Order(product_ids=PRODUCT_IDS, amount=float(i)) for i in range(3)]
    for o in orders:
        order_repo.save(o)
    assert len(order_repo.list_all()) == 3


def test_save_is_idempotent(order_repo: InMemoryOrderRepository) -> None:
    """Saving the same order twice must not create duplicates."""
    order = Order(product_ids=PRODUCT_IDS, amount=AMOUNT)
    order_repo.save(order)
    order_repo.save(order)
    assert len(order_repo.list_all()) == 1


def test_save_overwrites_existing(order_repo: InMemoryOrderRepository) -> None:
    """Re-saving a mutated order must update the stored version."""
    from src.domain.states import OrderState

    order = Order(product_ids=PRODUCT_IDS, amount=AMOUNT)
    order_repo.save(order)
    order.apply_transition(OrderState.ON_HOLD, "pendingBiometricalVerification", {})
    order_repo.save(order)
    stored = order_repo.get_by_id(order.order_id)
    assert stored is not None
    assert stored.state == OrderState.ON_HOLD


def test_concurrent_writes_are_safe(order_repo: InMemoryOrderRepository) -> None:
    """Multiple threads saving different orders must not lose any entry (Req 3)."""
    orders = [Order(product_ids=[f"p{i}"], amount=float(i)) for i in range(20)]

    def save(o: Order) -> None:
        order_repo.save(o)

    threads = [threading.Thread(target=save, args=(o,)) for o in orders]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(order_repo.list_all()) == 20


# ── InMemorySupportRepository ─────────────────────────────────────────────────


def test_create_ticket_returns_id(support_repo: InMemorySupportRepository) -> None:
    ticket_id = support_repo.create_ticket("ord-1", "reason", 1500.0)
    assert ticket_id.startswith("ticket-")


def test_create_ticket_generates_unique_ids(
    support_repo: InMemorySupportRepository,
) -> None:
    id_a = support_repo.create_ticket("ord-1", "r", 1500.0)
    id_b = support_repo.create_ticket("ord-2", "r", 2000.0)
    assert id_a != id_b
