import threading
import uuid
from typing import Any

from src.domain.order import Order
from src.repositories.base import OrderRepository, SupportRepository

TICKET_ID_PREFIX = "ticket-"
TICKET_ID_LENGTH = 8


class InMemoryOrderRepository(OrderRepository):
    def __init__(self) -> None:
        self._orders: dict[str, Order] = {}
        self._lock = threading.Lock()

    def save(self, order: Order) -> None:
        with self._lock:
            self._orders[order.order_id] = order

    def get_by_id(self, order_id: str) -> Order | None:
        with self._lock:
            return self._orders.get(order_id)

    def list_all(self) -> list[Order]:
        with self._lock:
            return list(self._orders.values())


class InMemorySupportRepository(SupportRepository):
    def __init__(self) -> None:
        self._tickets: dict[str, dict[str, Any]] = {}
        self._lock = threading.Lock()

    def create_ticket(self, order_id: str, reason: str, amount: float) -> str:
        ticket_id = f"{TICKET_ID_PREFIX}{uuid.uuid4().hex[:TICKET_ID_LENGTH]}"
        with self._lock:
            self._tickets[ticket_id] = {
                "order_id": order_id,
                "reason": reason,
                "amount": amount,
            }
        return ticket_id
