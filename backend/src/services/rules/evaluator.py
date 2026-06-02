from typing import Any

from src.domain.rules.conditions import (
    AndNode,
    Comparison,
    ConditionNode,
    NotNode,
    Operator,
    OrNode,
)
from src.services.rules.attribute_resolver import MISSING, resolve_path


def evaluate(node: ConditionNode, ctx: Any) -> bool:
    if isinstance(node, Comparison):
        actual = resolve_path(ctx, node.field)
        return _apply_operator(node.operator, actual, node.value)
    if isinstance(node, AndNode):
        return all(evaluate(child, ctx) for child in node.children)
    if isinstance(node, OrNode):
        return any(evaluate(child, ctx) for child in node.children)
    if isinstance(node, NotNode):
        return not evaluate(node.child, ctx)
    raise TypeError(f"Unknown condition node type: {type(node).__name__}")


def _apply_operator(op: Operator, actual: Any, expected: Any) -> bool:
    if op == Operator.IS_NULL:
        return actual is MISSING or actual is None
    if op == Operator.IS_NOT_NULL:
        return not (actual is MISSING or actual is None)

    if actual is MISSING:
        return False

    try:
        if op == Operator.EQ:
            return actual == expected  # type: ignore[no-any-return]
        if op == Operator.NEQ:
            return actual != expected  # type: ignore[no-any-return]
        if op == Operator.GT:
            return actual > expected  # type: ignore[no-any-return]
        if op == Operator.GTE:
            return actual >= expected  # type: ignore[no-any-return]
        if op == Operator.LT:
            return actual < expected  # type: ignore[no-any-return]
        if op == Operator.LTE:
            return actual <= expected  # type: ignore[no-any-return]
        if op == Operator.IN:
            return actual in expected
        if op == Operator.NOT_IN:
            return actual not in expected
        if op == Operator.CONTAINS:
            return expected in actual
        if op == Operator.STARTS_WITH:
            return isinstance(actual, str) and actual.startswith(expected)
    except (TypeError, ValueError):
        return False

    raise ValueError(f"Unhandled operator: {op}")
