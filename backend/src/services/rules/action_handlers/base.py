from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from src.domain.order import Order
from src.domain.rules.exceptions import UnknownActionError
from src.domain.rules.execution_log import ActionResult


@dataclass(frozen=True)
class ActionContext:
    rule_id: str
    rule_version: int
    trigger: str
    dry_run: bool = False


class ActionHandler(ABC):
    @abstractmethod
    def execute(
        self, order: Order, params: dict[str, Any], ctx: ActionContext
    ) -> ActionResult: ...


class ActionHandlerRegistry:
    def __init__(self) -> None:
        self._handlers: dict[str, ActionHandler] = {}

    def register(self, action_type: str, handler: ActionHandler) -> None:
        if action_type in self._handlers:
            raise ValueError(f"Duplicate action handler: '{action_type}'")
        self._handlers[action_type] = handler

    def get(self, action_type: str) -> ActionHandler:
        handler = self._handlers.get(action_type)
        if handler is None:
            raise UnknownActionError(action_type)
        return handler

    def known_types(self) -> list[str]:
        return list(self._handlers.keys())
