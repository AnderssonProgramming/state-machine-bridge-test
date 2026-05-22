"""Unit tests for the state machine transition table and logic."""

import pytest

from src.domain.events import EventType
from src.domain.exceptions import InvalidTransitionError
from src.domain.state_machine import (
    TERMINAL_FOR_CANCELLATION,
    TRANSITIONS,
    StateMachine,
)
from src.domain.states import OrderState

# ── Parametrize valid transitions directly from the canonical table ────────────

VALID_CASES = [
    (state, event, next_s)
    for state, events in TRANSITIONS.items()
    for event, next_s in events.items()
]


@pytest.mark.parametrize("current_state,event,expected", VALID_CASES)
def test_valid_transition(
    current_state: OrderState,
    event: EventType,
    expected: OrderState,
) -> None:
    """Every entry in the TRANSITIONS table must resolve correctly."""
    result = StateMachine().next_state(current_state, event)
    assert result == expected


# ── Invalid transitions ────────────────────────────────────────────────────────

INVALID_CASES = [
    (OrderState.PENDING, EventType.ITEM_DISPATCHED),
    (OrderState.PENDING, EventType.PAYMENT_SUCCESSFUL),
    (OrderState.ON_HOLD, EventType.PREPARING_SHIPMENT),
    (OrderState.PENDING_PAYMENT, EventType.DELIVERY_ISSUE),
    (OrderState.CONFIRMED, EventType.RETURN_INITIATED_BY_CUSTOMER),
    (OrderState.SHIPPED, EventType.REFUND_PROCESSED),
]


@pytest.mark.parametrize("current_state,event", INVALID_CASES)
def test_invalid_transition_raises(
    current_state: OrderState, event: EventType
) -> None:
    """Events with no defined transition must raise InvalidTransitionError."""
    with pytest.raises(InvalidTransitionError) as exc_info:
        StateMachine().next_state(current_state, event)
    assert current_state.value in str(exc_info.value)
    assert event.value in str(exc_info.value)


# ── Universal cancellation ─────────────────────────────────────────────────────

NON_TERMINAL_STATES = [s for s in OrderState if s not in TERMINAL_FOR_CANCELLATION]


@pytest.mark.parametrize("state", NON_TERMINAL_STATES)
def test_order_cancelled_by_user_allowed_from_non_terminal(state: OrderState) -> None:
    """orderCancelledByUser must transition any non-terminal state to Cancelled."""
    result = StateMachine().next_state(state, EventType.ORDER_CANCELLED_BY_USER)
    assert result == OrderState.CANCELLED


@pytest.mark.parametrize("state", list(TERMINAL_FOR_CANCELLATION))
def test_order_cancelled_by_user_blocked_from_terminal(state: OrderState) -> None:
    """orderCancelledByUser must be rejected from terminal states."""
    with pytest.raises(InvalidTransitionError):
        StateMachine().next_state(state, EventType.ORDER_CANCELLED_BY_USER)


# ── available_events ───────────────────────────────────────────────────────────

def test_available_events_includes_cancellation_for_pending() -> None:
    """Pending state must offer its normal transitions plus cancellation."""
    events = StateMachine().available_events(OrderState.PENDING)
    assert EventType.ORDER_CANCELLED_BY_USER in events
    assert EventType.NO_VERIFICATION_NEEDED in events
    assert EventType.PENDING_BIOMETRICAL_VERIFICATION in events


def test_available_events_excludes_cancellation_for_delivered() -> None:
    """Delivered is terminal — cancellation must NOT appear in available events."""
    events = StateMachine().available_events(OrderState.DELIVERED)
    assert EventType.ORDER_CANCELLED_BY_USER not in events


def test_available_events_empty_for_refunded() -> None:
    """Refunded is a terminal sink — no events must be available."""
    events = StateMachine().available_events(OrderState.REFUNDED)
    assert events == []
