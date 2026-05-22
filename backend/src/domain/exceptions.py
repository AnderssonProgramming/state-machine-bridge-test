"""Domain-specific exceptions."""


class DomainError(Exception):
    """Base class for all domain errors."""


class InvalidTransitionError(DomainError):
    """Raised when an event has no defined transition from the current state."""

    def __init__(self, current_state: str, event_type: str) -> None:
        self.current_state = current_state
        self.event_type = event_type
        super().__init__(
            f"No transition defined for event '{event_type}' "
            f"from state '{current_state}'."
        )


class OrderNotFoundError(DomainError):
    """Raised when an order cannot be found by its identifier."""

    def __init__(self, order_id: str) -> None:
        self.order_id = order_id
        super().__init__(f"Order '{order_id}' not found.")