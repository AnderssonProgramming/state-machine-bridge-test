from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from src.domain.rules.conditions import ConditionNode
from src.domain.rules.execution_log import ActionResult
from src.domain.rules.rule import ActionSpec


class CreateRuleRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    name: str = Field(..., min_length=1, max_length=200)
    description: str = ""
    trigger: str = Field(..., min_length=1)
    condition: ConditionNode
    actions: list[ActionSpec] = Field(..., min_length=1)
    priority: int = 100
    enabled: bool = True
    stop_on_match: bool = Field(default=False, alias="stopOnMatch")


class UpdateRuleRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    name: str | None = None
    description: str | None = None
    trigger: str | None = None
    condition: ConditionNode | None = None
    actions: list[ActionSpec] | None = None
    priority: int | None = None
    enabled: bool | None = None
    stop_on_match: bool | None = Field(default=None, alias="stopOnMatch")


class ToggleEnabledRequest(BaseModel):
    enabled: bool


class DryRunRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    product_ids: list[str] = Field(default_factory=list, alias="productIds")
    amount: float = Field(..., gt=0)
    attributes: dict[str, Any] = Field(default_factory=dict)


class DryRunResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    matched: bool
    actions: list[ActionResult]
