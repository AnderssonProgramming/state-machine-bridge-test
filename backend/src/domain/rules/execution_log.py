from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


def _generate_log_id() -> str:
    return f"rlog-{uuid.uuid4().hex[:10]}"


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


class ActionResult(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    action_type: str = Field(..., alias="actionType")
    success: bool
    details: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None


class RuleExecutionLog(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    log_id: str = Field(default_factory=_generate_log_id, alias="logId")
    rule_id: str = Field(..., alias="ruleId")
    rule_version: int = Field(..., alias="ruleVersion")
    order_id: str = Field(..., alias="orderId")
    trigger: str
    matched: bool
    actions_executed: list[ActionResult] = Field(
        default_factory=list, alias="actionsExecuted"
    )
    evaluated_at: str = Field(default_factory=_utc_now, alias="evaluatedAt")
    duration_ms: float = Field(default=0.0, alias="durationMs")
