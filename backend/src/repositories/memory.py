"""In-memory repository implementations for local dev and tests.

A lock guards all dict mutations so the service can safely handle events
for multiple order IDs concurrently.
"""

import threading
import uuid
from typing import Any

from src.domain.order import Order
from src.repositories.base import OrderRepository, SupportRepository

TICKET_ID_PREFIX = "ticket-"
TICKET_ID_LENGTH = 8


class InMemoryOrderRepository(OrderRepository):
    """Thread-safe in-memory order store backed by a dict."""

    def __init__(self) -> None:
        self._orders: dict[str, Order] = {}
        self._lock = threading.Lock()

    def save(self, order: Order) -> None:
        """Persist an order under its id."""
        with self._lock:
            self._orders[order.order_id] = order

    def get_by_id(self, order_id: str) -> Order | None:
        """Return an order by id, or None."""
        with self._lock:
            return self._orders.get(order_id)

    def list_all(self) -> list[Order]:
        """Return all stored orders."""
        with self._lock:
            return list(self._orders.values())


class InMemorySupportRepository(SupportRepository):
    """In-memory support ticket store."""

    def __init__(self) -> None:
        self._tickets: dict[str, dict[str, Any]] = {}
        self._lock = threading.Lock()

    def create_ticket(self, order_id: str, reason: str, amount: float) -> str:
        """Create and store a support ticket, returning its id."""
        ticket_id = f"{TICKET_ID_PREFIX}{uuid.uuid4().hex[:TICKET_ID_LENGTH]}"
        with self._lock:
            self._tickets[ticket_id] = {
                "order_id": order_id,
                "reason": reason,
                "amount": amount,
            }
        return ticket_id
