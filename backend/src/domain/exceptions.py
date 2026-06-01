class DomainError(Exception):
    pass


class InvalidTransitionError(DomainError):
    def __init__(self, current_state: str, event_type: str) -> None:
        self.current_state = current_state
        self.event_type = event_type
        super().__init__(
            f"No transition defined for event '{event_type}' from state '{current_state}'."
        )


class OrderNotFoundError(DomainError):
    def __init__(self, order_id: str) -> None:
        self.order_id = order_id
        super().__init__(f"Order '{order_id}' not found.")
