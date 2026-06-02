from src.domain.order import Order
from src.domain.rules.conditions import Comparison, Operator
from src.domain.rules.rule import ActionSpec, Rule
from src.repositories.memory import InMemoryRuleLogRepository, InMemoryRuleRepository
from src.services.rules.engine import RuleEngineService


def _high_value_payment_rule() -> Rule:
    return Rule(
        name="High-value payment failure review",
        trigger="event:paymentFailed",
        condition=Comparison(field="amount", operator=Operator.GT, value=1000),
        actions=[
            ActionSpec(
                type="create_support_ticket",
                params={"reason": "High-value payment failure requires manual review."},
            )
        ],
    )


def test_rule_matches_and_creates_ticket(
    rule_repo: InMemoryRuleRepository,
    support_repo: "InMemorySupportRepository",  # noqa: F821
    rule_engine: RuleEngineService,
) -> None:
    rule_repo.save(_high_value_payment_rule())
    order = Order(product_ids=["p1"], amount=1500.0)
    results = rule_engine.evaluate_for("event:paymentFailed", order)
    assert len(results) == 1
    assert results[0].success is True
    assert results[0].action_type == "create_support_ticket"


def test_rule_does_not_match_low_amount(
    rule_repo: InMemoryRuleRepository,
    support_repo: "InMemorySupportRepository",  # noqa: F821
    rule_engine: RuleEngineService,
) -> None:
    rule_repo.save(_high_value_payment_rule())
    order = Order(product_ids=["p1"], amount=500.0)
    results = rule_engine.evaluate_for("event:paymentFailed", order)
    assert results == []


def test_disabled_rule_does_not_fire(
    rule_repo: InMemoryRuleRepository,
    rule_engine: RuleEngineService,
) -> None:
    rule = _high_value_payment_rule()
    rule_repo.save(rule.model_copy(update={"enabled": False}))
    order = Order(product_ids=["p1"], amount=5000.0)
    results = rule_engine.evaluate_for("event:paymentFailed", order)
    assert results == []


def test_rule_for_different_trigger_does_not_fire(
    rule_repo: InMemoryRuleRepository,
    rule_engine: RuleEngineService,
) -> None:
    rule_repo.save(_high_value_payment_rule())
    order = Order(product_ids=["p1"], amount=5000.0)
    results = rule_engine.evaluate_for("event:orderCancelled", order)
    assert results == []


def test_audit_log_records_match_and_miss(
    rule_repo: InMemoryRuleRepository,
    log_repo: InMemoryRuleLogRepository,
    rule_engine: RuleEngineService,
) -> None:
    rule_repo.save(_high_value_payment_rule())
    rule_engine.evaluate_for(
        "event:paymentFailed", Order(product_ids=["p1"], amount=5000.0)
    )
    rule_engine.evaluate_for(
        "event:paymentFailed", Order(product_ids=["p1"], amount=50.0)
    )
    logs = log_repo._logs
    assert len(logs) == 2
    assert any(log.matched for log in logs)
    assert any(not log.matched for log in logs)


def test_stop_on_match_short_circuits(
    rule_repo: InMemoryRuleRepository,
    rule_engine: RuleEngineService,
) -> None:
    first = Rule(
        name="first",
        trigger="order_created",
        priority=10,
        stop_on_match=True,
        condition=Comparison(field="amount", operator=Operator.GT, value=0),
        actions=[ActionSpec(type="add_fee", params={"amount": 1.0})],
    )
    second = Rule(
        name="second",
        trigger="order_created",
        priority=20,
        condition=Comparison(field="amount", operator=Operator.GT, value=0),
        actions=[ActionSpec(type="add_fee", params={"amount": 2.0})],
    )
    rule_repo.save(first)
    rule_repo.save(second)
    order = Order(product_ids=["p1"], amount=100.0)
    rule_engine.evaluate_for("order_created", order)
    assert len(order.adjustments) == 1
    assert order.adjustments[0].source_rule_id == first.rule_id


def test_dry_run_does_not_persist_side_effects(
    rule_repo: InMemoryRuleRepository,
    log_repo: InMemoryRuleLogRepository,
    rule_engine: RuleEngineService,
    support_repo: "InMemorySupportRepository",  # noqa: F821
) -> None:
    rule = _high_value_payment_rule()
    order = Order(product_ids=["p1"], amount=5000.0)
    matched, results = rule_engine.dry_run(rule, order)
    assert matched is True
    assert results[0].details.get("dryRun") is True
    assert len(support_repo._tickets) == 0
    assert len(log_repo._logs) == 0
