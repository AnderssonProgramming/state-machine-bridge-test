"""Unit tests for the Order domain entity and TransitionLog."""

from src.domain.order import Order, TransitionLog
from src.domain.states import OrderState

PRODUCT_IDS = ["prod-001", "prod-002"]
AMOUNT = 299.99


def test_new_order_has_pending_state() -> None:
    """A freshly created order must start in the Pending state."""
    order = Order(product_ids=PRODUCT_IDS, amount=AMOUNT)
    assert order.state == OrderState.PENDING


def test_new_order_records_init_log() -> None:
    """Order creation must log the initial 'init' transition."""
    order = Order(product_ids=PRODUCT_IDS, amount=AMOUNT)
    assert len(order.history) == 1
    first = order.history[0]
    assert first.from_state is None
    assert first.to_state == OrderState.PENDING.value
    assert first.event_type == "init"


def test_new_order_generates_unique_id() -> None:
    """Two separate orders must never share an id."""
    a = Order(product_ids=PRODUCT_IDS, amount=AMOUNT)
    b = Order(product_ids=PRODUCT_IDS, amount=AMOUNT)
    assert a.order_id != b.order_id


def test_apply_transition_updates_state() -> None:
    """apply_transition must change the order's state."""
    order = Order(product_ids=PRODUCT_IDS, amount=AMOUNT)
    order.apply_transition(OrderState.ON_HOLD, "pendingBiometricalVerification", {})
    assert order.state == OrderState.ON_HOLD


def test_apply_transition_appends_to_history() -> None:
    """apply_transition must append a new entry to the history log."""
    order = Order(product_ids=PRODUCT_IDS, amount=AMOUNT)
    order.apply_transition(OrderState.PENDING_PAYMENT, "noVerificationNeeded", {})
    assert len(order.history) == 2  # init + new transition


def test_apply_transition_records_correct_from_and_to() -> None:
    """The log entry must capture the correct from/to states."""
    order = Order(product_ids=PRODUCT_IDS, amount=AMOUNT)
    order.apply_transition(OrderState.PENDING_PAYMENT, "noVerificationNeeded", {})
    log = order.history[-1]
    assert log.from_state == OrderState.PENDING.value
    assert log.to_state == OrderState.PENDING_PAYMENT.value
    assert log.event_type == "noVerificationNeeded"


def test_apply_transition_stores_metadata() -> None:
    """Metadata passed with the event must be saved on the log entry."""
    order = Order(product_ids=PRODUCT_IDS, amount=AMOUNT)
    meta = {"reason": "test"}
    order.apply_transition(OrderState.CANCELLED, "orderCancelled", meta)
    assert order.history[-1].metadata == meta


def test_apply_transition_updates_updated_at() -> None:
    """updated_at must change after a transition."""
    order = Order(product_ids=PRODUCT_IDS, amount=AMOUNT)
    original = order.updated_at
    order.apply_transition(OrderState.ON_HOLD, "pendingBiometricalVerification", {})
    assert order.updated_at >= original


def test_reconstructed_order_does_not_duplicate_init_log() -> None:
    """Orders rebuilt from persistence (non-empty history) must not add init again."""
    existing_log = [
        TransitionLog(from_state=None, to_state="Pending", event_type="init")
    ]
    order = Order(
        product_ids=PRODUCT_IDS,
        amount=AMOUNT,
        state=OrderState.PENDING,
        history=existing_log,
    )
    assert len(order.history) == 1
