"""Order domain entity and its transition log."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone

from src.domain.states import OrderState

INITIAL_EVENT = "init"
ORDER_ID_PREFIX = "ord-"
ORDER_ID_LENGTH = 12


def _utc_now() -> str:
    """Return the current UTC time as an ISO 8601 string."""
    return datetime.now(timezone.utc).isoformat()


def _generate_order_id() -> str:
    """Generate a unique order identifier."""
    return f"{ORDER_ID_PREFIX}{uuid.uuid4().hex[:ORDER_ID_LENGTH]}"


@dataclass
class TransitionLog:
    """A single recorded state transition (Requirement 6)."""

    from_state: str | None
    to_state: str
    event_type: str
    timestamp: str = field(default_factory=_utc_now)
    metadata: dict = field(default_factory=dict)


@dataclass
class Order:
    """The order aggregate root."""

    product_ids: list[str]
    amount: float
    state: OrderState = OrderState.PENDING
    order_id: str = field(default_factory=_generate_order_id)
    created_at: str = field(default_factory=_utc_now)
    updated_at: str = field(default_factory=_utc_now)
    history: list[TransitionLog] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Record the initial creation transition for new orders."""
        if not self.history:
            self.history.append(
                TransitionLog(
                    from_state=None,
                    to_state=self.state.value,
                    event_type=INITIAL_EVENT,
                )
            )

    def apply_transition(
        self, new_state: OrderState, event_type: str, metadata: dict
    ) -> None:
        """Move the order to a new state and append to its history.

        Args:
            new_state: The state to transition into.
            event_type: The triggering event name.
            metadata: Event-specific data to record.
        """
        self.history.append(
            TransitionLog(
                from_state=self.state.value,
                to_state=new_state.value,
                event_type=event_type,
                metadata=metadata,
            )
        )
        self.state = new_state
        self.updated_at = _utc_now()