from abc import ABC, abstractmethod

from src.domain.order import Order


class OrderRepository(ABC):
    @abstractmethod
    def save(self, order: Order) -> None: ...

    @abstractmethod
    def get_by_id(self, order_id: str) -> Order | None: ...

    @abstractmethod
    def list_all(self) -> list[Order]: ...


class SupportRepository(ABC):
    @abstractmethod
    def create_ticket(self, order_id: str, reason: str, amount: float) -> str: ...
