"""Core state machine: transition table and transition logic."""

from src.domain.events import EventType
from src.domain.exceptions import InvalidTransitionError
from src.domain.states import OrderState

# States from which a user-initiated cancellation is NOT allowed.
TERMINAL_FOR_CANCELLATION: frozenset[OrderState] = frozenset(
    {OrderState.DELIVERED, OrderState.RETURNED, OrderState.REFUNDED}
)

# Explicit transition table: {current_state: {event: next_state}}.
TRANSITIONS: dict[OrderState, dict[EventType, OrderState]] = {
    OrderState.PENDING: {
        EventType.PENDING_BIOMETRICAL_VERIFICATION: OrderState.ON_HOLD,
        EventType.NO_VERIFICATION_NEEDED: OrderState.PENDING_PAYMENT,
        EventType.PAYMENT_FAILED: OrderState.CANCELLED,
        EventType.ORDER_CANCELLED: OrderState.CANCELLED,
    },
    OrderState.ON_HOLD: {
        EventType.BIOMETRICAL_VERIFICATION_SUCCESSFUL: OrderState.PENDING_PAYMENT,
        EventType.VERIFICATION_FAILED: OrderState.CANCELLED,
    },
    OrderState.PENDING_PAYMENT: {
        EventType.PAYMENT_SUCCESSFUL: OrderState.CONFIRMED,
    },
    OrderState.CONFIRMED: {
        EventType.PREPARING_SHIPMENT: OrderState.PROCESSING,
    },
    OrderState.PROCESSING: {
        EventType.ITEM_DISPATCHED: OrderState.SHIPPED,
    },
    OrderState.SHIPPED: {
        EventType.ITEM_RECEIVED_BY_CUSTOMER: OrderState.DELIVERED,
        EventType.DELIVERY_ISSUE: OrderState.ON_HOLD,
    },
    OrderState.DELIVERED: {
        EventType.RETURN_INITIATED_BY_CUSTOMER: OrderState.RETURNING,
    },
    OrderState.RETURNING: {
        EventType.ITEM_RECEIVED_BACK: OrderState.RETURNED,
    },
    OrderState.RETURNED: {
        EventType.REFUND_PROCESSED: OrderState.REFUNDED,
    },
}


class StateMachine:
    """Resolves the next order state for a given current state and event."""

    def next_state(
        self, current_state: OrderState, event_type: EventType
    ) -> OrderState:
        """Return the resulting state for an event, or raise if undefined.

        Args:
            current_state: The order's current state.
            event_type: The event being applied.

        Returns:
            The next state of the order.

        Raises:
            InvalidTransitionError: If no transition is defined.
        """
        # Universal cancellation: allowed from any non-terminal state.
        if event_type == EventType.ORDER_CANCELLED_BY_USER:
            if current_state in TERMINAL_FOR_CANCELLATION:
                raise InvalidTransitionError(current_state.value, event_type.value)
            return OrderState.CANCELLED

        transitions_for_state = TRANSITIONS.get(current_state, {})
        next_state = transitions_for_state.get(event_type)
        if next_state is None:
            raise InvalidTransitionError(current_state.value, event_type.value)
        return next_state

    def available_events(self, current_state: OrderState) -> list[EventType]:
        """Return all events that have a defined transition from a state."""
        events = list(TRANSITIONS.get(current_state, {}).keys())
        if current_state not in TERMINAL_FOR_CANCELLATION:
            events.append(EventType.ORDER_CANCELLED_BY_USER)
        return events