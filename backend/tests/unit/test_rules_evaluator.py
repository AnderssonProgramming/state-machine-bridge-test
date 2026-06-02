import pytest
from src.domain.rules.conditions import AndNode, Comparison, NotNode, Operator, OrNode
from src.services.rules.evaluator import evaluate

CTX = {
    "amount": 1500.0,
    "origin_country": "CO",
    "customer": {"tier": "gold"},
    "product_ids": ["p1", "p2", "p3"],
    "promo_code": None,
}


@pytest.mark.parametrize(
    "op, value, expected",
    [
        (Operator.EQ, 1500.0, True),
        (Operator.EQ, 1499.0, False),
        (Operator.NEQ, 1499.0, True),
        (Operator.GT, 1000, True),
        (Operator.GT, 1500, False),
        (Operator.GTE, 1500, True),
        (Operator.LT, 2000, True),
        (Operator.LTE, 1500, True),
    ],
)
def test_numeric_operators(op: Operator, value: float, expected: bool) -> None:
    cond = Comparison(field="amount", operator=op, value=value)
    assert evaluate(cond, CTX) is expected


def test_in_operator() -> None:
    cond = Comparison(field="origin_country", operator=Operator.IN, value=["CO", "US"])
    assert evaluate(cond, CTX) is True


def test_not_in_operator() -> None:
    cond = Comparison(
        field="origin_country", operator=Operator.NOT_IN, value=["BR", "AR"]
    )
    assert evaluate(cond, CTX) is True


def test_contains_on_list() -> None:
    cond = Comparison(field="product_ids", operator=Operator.CONTAINS, value="p2")
    assert evaluate(cond, CTX) is True


def test_starts_with() -> None:
    cond = Comparison(field="origin_country", operator=Operator.STARTS_WITH, value="C")
    assert evaluate(cond, CTX) is True


def test_is_null_for_explicit_none() -> None:
    cond = Comparison(field="promo_code", operator=Operator.IS_NULL, value=None)
    assert evaluate(cond, CTX) is True


def test_is_null_for_missing_field() -> None:
    cond = Comparison(field="nonexistent", operator=Operator.IS_NULL, value=None)
    assert evaluate(cond, CTX) is True


def test_is_not_null() -> None:
    cond = Comparison(field="amount", operator=Operator.IS_NOT_NULL, value=None)
    assert evaluate(cond, CTX) is True


def test_missing_field_returns_false_for_other_ops() -> None:
    cond = Comparison(field="nonexistent", operator=Operator.GT, value=0)
    assert evaluate(cond, CTX) is False


def test_type_mismatch_is_false_not_exception() -> None:
    cond = Comparison(field="origin_country", operator=Operator.GT, value=100)
    assert evaluate(cond, CTX) is False


def test_and_node_all_true() -> None:
    cond = AndNode(
        children=[
            Comparison(field="amount", operator=Operator.GT, value=1000),
            Comparison(field="origin_country", operator=Operator.EQ, value="CO"),
        ]
    )
    assert evaluate(cond, CTX) is True


def test_and_node_short_circuits_on_false() -> None:
    cond = AndNode(
        children=[
            Comparison(field="amount", operator=Operator.LT, value=0),
            Comparison(field="origin_country", operator=Operator.EQ, value="CO"),
        ]
    )
    assert evaluate(cond, CTX) is False


def test_or_node() -> None:
    cond = OrNode(
        children=[
            Comparison(field="amount", operator=Operator.LT, value=0),
            Comparison(field="origin_country", operator=Operator.EQ, value="CO"),
        ]
    )
    assert evaluate(cond, CTX) is True


def test_not_node() -> None:
    cond = NotNode(child=Comparison(field="amount", operator=Operator.LT, value=0))
    assert evaluate(cond, CTX) is True


def test_nested_tree() -> None:
    cond = AndNode(
        children=[
            Comparison(field="amount", operator=Operator.GT, value=1000),
            OrNode(
                children=[
                    Comparison(
                        field="origin_country", operator=Operator.IN, value=["CO", "US"]
                    ),
                    Comparison(
                        field="customer.tier", operator=Operator.EQ, value="gold"
                    ),
                ]
            ),
        ]
    )
    assert evaluate(cond, CTX) is True


def test_dotted_path_resolution() -> None:
    cond = Comparison(field="customer.tier", operator=Operator.EQ, value="gold")
    assert evaluate(cond, CTX) is True


def test_list_count_resolution() -> None:
    cond = Comparison(field="product_ids.count", operator=Operator.EQ, value=3)
    assert evaluate(cond, CTX) is True
