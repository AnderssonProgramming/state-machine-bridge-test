import threading
import uuid
from typing import Any

from src.domain.order import Order
from src.domain.rules.execution_log import RuleExecutionLog
from src.domain.rules.rule import Rule
from src.repositories.base import (
    OrderRepository,
    RuleLogRepository,
    RuleRepository,
    SupportRepository,
)

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


class InMemoryRuleRepository(RuleRepository):
    def __init__(self) -> None:
        self._rules: dict[str, Rule] = {}
        self._lock = threading.Lock()

    def save(self, rule: Rule) -> None:
        with self._lock:
            self._rules[rule.rule_id] = rule

    def get_by_id(self, rule_id: str) -> Rule | None:
        with self._lock:
            return self._rules.get(rule_id)

    def list_all(self) -> list[Rule]:
        with self._lock:
            return list(self._rules.values())

    def list_active_for(self, trigger: str) -> list[Rule]:
        with self._lock:
            matching = [
                r for r in self._rules.values() if r.enabled and r.trigger == trigger
            ]
        matching.sort(key=lambda r: r.priority)
        return matching

    def delete(self, rule_id: str) -> bool:
        with self._lock:
            return self._rules.pop(rule_id, None) is not None


class InMemoryRuleLogRepository(RuleLogRepository):
    def __init__(self) -> None:
        self._logs: list[RuleExecutionLog] = []
        self._lock = threading.Lock()

    def record(self, log: RuleExecutionLog) -> None:
        with self._lock:
            self._logs.append(log)

    def list_for_order(self, order_id: str) -> list[RuleExecutionLog]:
        with self._lock:
            return [log for log in self._logs if log.order_id == order_id]
