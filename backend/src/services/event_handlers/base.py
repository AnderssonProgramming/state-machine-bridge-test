"""Event handler protocol and registry (Open/Closed for business rules).

Adding a new event-specific rule = create one EventHandler subclass and
register it. No existing code changes.
"""

from abc import ABC, abstractmethod

from src.domain.order import Order


class EventHandler(ABC):
    """Side-effect business logic bound to a specific event type."""

    @abstractmethod
    def handle(self, order: Order, metadata: dict) -> None:
        """Execute business logic for an event during processing."""


class EventHandlerRegistry:
    """Maps event type names to their handlers."""

    def __init__(self) -> None:
        self._handlers: dict[str, EventHandler] = {}

    def register(self, event_type: str, handler: EventHandler) -> None:
        """Register a handler for an event type."""
        self._handlers[event_type] = handler

    def get(self, event_type: str) -> EventHandler | None:
        """Return the handler for an event type, if any."""
        return self._handlers.get(event_type)
