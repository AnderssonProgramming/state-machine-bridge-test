from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from src.domain.rules.conditions import ConditionNode

RULE_ID_PREFIX = "rule-"
RULE_ID_LENGTH = 10


def _generate_rule_id() -> str:
    return f"{RULE_ID_PREFIX}{uuid.uuid4().hex[:RULE_ID_LENGTH]}"


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


class ActionSpec(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    type: str = Field(..., min_length=1)
    params: dict[str, Any] = Field(default_factory=dict)


class Rule(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    rule_id: str = Field(default_factory=_generate_rule_id, alias="ruleId")
    name: str = Field(..., min_length=1, max_length=200)
    description: str = ""
    trigger: str = Field(..., min_length=1, max_length=100)
    condition: ConditionNode
    actions: list[ActionSpec] = Field(..., min_length=1)
    priority: int = 100
    enabled: bool = True
    stop_on_match: bool = Field(default=False, alias="stopOnMatch")
    version: int = 1
    created_at: str = Field(default_factory=_utc_now, alias="createdAt")
    updated_at: str = Field(default_factory=_utc_now, alias="updatedAt")
