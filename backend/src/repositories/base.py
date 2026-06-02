from abc import ABC, abstractmethod

from src.domain.order import Order
from src.domain.rules.execution_log import RuleExecutionLog
from src.domain.rules.rule import Rule


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


class RuleRepository(ABC):
    @abstractmethod
    def save(self, rule: Rule) -> None: ...

    @abstractmethod
    def get_by_id(self, rule_id: str) -> Rule | None: ...

    @abstractmethod
    def list_all(self) -> list[Rule]: ...

    @abstractmethod
    def list_active_for(self, trigger: str) -> list[Rule]: ...

    @abstractmethod
    def delete(self, rule_id: str) -> bool: ...


class RuleLogRepository(ABC):
    @abstractmethod
    def record(self, log: RuleExecutionLog) -> None: ...

    @abstractmethod
    def list_for_order(self, order_id: str) -> list[RuleExecutionLog]: ...
