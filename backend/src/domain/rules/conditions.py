from __future__ import annotations

from enum import Enum
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class Operator(str, Enum):
    EQ = "eq"
    NEQ = "neq"
    GT = "gt"
    GTE = "gte"
    LT = "lt"
    LTE = "lte"
    IN = "in"
    NOT_IN = "not_in"
    CONTAINS = "contains"
    STARTS_WITH = "starts_with"
    IS_NULL = "is_null"
    IS_NOT_NULL = "is_not_null"


class Comparison(BaseModel):
    model_config = ConfigDict(populate_by_name=True, frozen=True)
    type: Literal["comparison"] = "comparison"
    field: str = Field(..., min_length=1, max_length=200)
    operator: Operator
    value: Any = None


class AndNode(BaseModel):
    model_config = ConfigDict(populate_by_name=True, frozen=True)
    type: Literal["and"] = "and"
    children: list[ConditionNode] = Field(..., min_length=1)


class OrNode(BaseModel):
    model_config = ConfigDict(populate_by_name=True, frozen=True)
    type: Literal["or"] = "or"
    children: list[ConditionNode] = Field(..., min_length=1)


class NotNode(BaseModel):
    model_config = ConfigDict(populate_by_name=True, frozen=True)
    type: Literal["not"] = "not"
    child: ConditionNode


ConditionNode = Annotated[
    Comparison | AndNode | OrNode | NotNode,
    Field(discriminator="type"),
]

AndNode.model_rebuild()
OrNode.model_rebuild()
NotNode.model_rebuild()
