from src.domain.events import EventType
from src.domain.exceptions import InvalidTransitionError
from src.domain.states import OrderState

TERMINAL_FOR_CANCELLATION: frozenset[OrderState] = frozenset(
    {OrderState.DELIVERED, OrderState.RETURNED, OrderState.REFUNDED}
)

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
    def next_state(self, current_state: OrderState, event_type: EventType) -> OrderState:
        if event_type == EventType.ORDER_CANCELLED_BY_USER:
            if current_state in TERMINAL_FOR_CANCELLATION:
                raise InvalidTransitionError(current_state.value, event_type.value)
            return OrderState.CANCELLED

        next_state = TRANSITIONS.get(current_state, {}).get(event_type)
        if next_state is None:
            raise InvalidTransitionError(current_state.value, event_type.value)
        return next_state

    def available_events(self, current_state: OrderState) -> list[EventType]:
        events = list(TRANSITIONS.get(current_state, {}).keys())
        if current_state not in TERMINAL_FOR_CANCELLATION:
            events.append(EventType.ORDER_CANCELLED_BY_USER)
        return events
