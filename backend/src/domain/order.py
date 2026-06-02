from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from src.domain.states import OrderState

INITIAL_EVENT = "init"
ORDER_ID_PREFIX = "ord-"
ORDER_ID_LENGTH = 12


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


def _generate_order_id() -> str:
    return f"{ORDER_ID_PREFIX}{uuid.uuid4().hex[:ORDER_ID_LENGTH]}"


@dataclass
class TransitionLog:
    from_state: str | None
    to_state: str
    event_type: str
    timestamp: str = field(default_factory=_utc_now)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Adjustment:
    kind: str
    label: str
    amount: float
    source_rule_id: str


@dataclass
class Order:
    product_ids: list[str]
    amount: float
    state: OrderState = OrderState.PENDING
    order_id: str = field(default_factory=_generate_order_id)
    created_at: str = field(default_factory=_utc_now)
    updated_at: str = field(default_factory=_utc_now)
    history: list[TransitionLog] = field(default_factory=list)
    attributes: dict[str, Any] = field(default_factory=dict)
    adjustments: list[Adjustment] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.history:
            self.history.append(
                TransitionLog(
                    from_state=None, to_state=self.state.value, event_type=INITIAL_EVENT
                )
            )

    @property
    def total_amount(self) -> float:
        return self.amount + sum(a.amount for a in self.adjustments)

    def apply_transition(
        self, new_state: OrderState, event_type: str, metadata: dict[str, Any]
    ) -> None:
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

    def add_adjustment(self, adjustment: Adjustment) -> bool:
        already = any(
            a.source_rule_id == adjustment.source_rule_id and a.kind == adjustment.kind
            for a in self.adjustments
        )
        if already:
            return False
        self.adjustments.append(adjustment)
        self.updated_at = _utc_now()
        return True
