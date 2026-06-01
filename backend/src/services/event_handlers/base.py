from abc import ABC, abstractmethod
from typing import Any

from src.domain.order import Order


class EventHandler(ABC):
    @abstractmethod
    def handle(self, order: Order, metadata: dict[str, Any]) -> None: ...


class EventHandlerRegistry:
    def __init__(self) -> None:
        self._handlers: dict[str, EventHandler] = {}

    def register(self, event_type: str, handler: EventHandler) -> None:
        self._handlers[event_type] = handler

    def get(self, event_type: str) -> EventHandler | None:
        return self._handlers.get(event_type)
