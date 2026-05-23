"""Repository interfaces (ports) for external interactions."""

from abc import ABC, abstractmethod

from src.domain.order import Order


class OrderRepository(ABC):
    """Port for persisting and retrieving orders."""

    @abstractmethod
    def save(self, order: Order) -> None:
        """Persist an order (create or update)."""

    @abstractmethod
    def get_by_id(self, order_id: str) -> Order | None:
        """Return an order by id, or None if it does not exist."""

    @abstractmethod
    def list_all(self) -> list[Order]:
        """Return all stored orders."""


class SupportRepository(ABC):
    """Port for creating support tickets in an external system."""

    @abstractmethod
    def create_ticket(self, order_id: str, reason: str, amount: float) -> str:
        """Create a support ticket and return its identifier."""
