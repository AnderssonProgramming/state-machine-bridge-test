from __future__ import annotations

import time
from typing import Any

from aws_lambda_powertools.metrics import MetricUnit

from src.domain.order import Order
from src.domain.rules.execution_log import ActionResult, RuleExecutionLog
from src.domain.rules.rule import Rule
from src.observability.powertools import logger, metrics, tracer
from src.repositories.base import RuleLogRepository, RuleRepository
from src.services.rules.action_handlers.base import ActionContext, ActionHandlerRegistry
from src.services.rules.evaluator import evaluate


class RuleEngineService:
    def __init__(
        self,
        rule_repository: RuleRepository,
        log_repository: RuleLogRepository,
        action_registry: ActionHandlerRegistry,
    ) -> None:
        self._rules = rule_repository
        self._logs = log_repository
        self._actions = action_registry

    @tracer.capture_method
    def evaluate_for(self, trigger: str, order: Order) -> list[ActionResult]:
        ctx_data = self._build_context(order)
        all_results: list[ActionResult] = []

        for rule in self._rules.list_active_for(trigger):
            matched, results = self._run_rule(
                rule, trigger=trigger, ctx_data=ctx_data, order=order, dry_run=False
            )
            all_results.extend(results)
            if matched and rule.stop_on_match:
                break

        return all_results

    @tracer.capture_method
    def dry_run(self, rule: Rule, order: Order) -> tuple[bool, list[ActionResult]]:
        ctx_data = self._build_context(order)
        return self._run_rule(
            rule, trigger=rule.trigger, ctx_data=ctx_data, order=order, dry_run=True
        )

    def _run_rule(
        self,
        rule: Rule,
        trigger: str,
        ctx_data: dict[str, Any],
        order: Order,
        dry_run: bool,
    ) -> tuple[bool, list[ActionResult]]:
        start = time.perf_counter()
        matched = evaluate(rule.condition, ctx_data)
        executed: list[ActionResult] = []

        if matched:
            action_ctx = ActionContext(
                rule_id=rule.rule_id,
                rule_version=rule.version,
                trigger=trigger,
                dry_run=dry_run,
            )
            for spec in rule.actions:
                try:
                    handler = self._actions.get(spec.type)
                    executed.append(handler.execute(order, spec.params, action_ctx))
                except Exception as exc:  # noqa: BLE001
                    logger.exception(
                        "Action execution failed",
                        extra={"rule_id": rule.rule_id, "action_type": spec.type},
                    )
                    executed.append(
                        ActionResult(
                            action_type=spec.type, success=False, error=str(exc)
                        )
                    )

        duration_ms = (time.perf_counter() - start) * 1000.0

        if not dry_run:
            self._logs.record(
                RuleExecutionLog(
                    rule_id=rule.rule_id,
                    rule_version=rule.version,
                    order_id=order.order_id,
                    trigger=trigger,
                    matched=matched,
                    actions_executed=executed,
                    duration_ms=duration_ms,
                )
            )
            metrics.add_metric(name="RuleEvaluations", unit=MetricUnit.Count, value=1)
            if matched:
                metrics.add_metric(name="RuleMatches", unit=MetricUnit.Count, value=1)

        return matched, executed

    @staticmethod
    def _build_context(order: Order) -> dict[str, Any]:
        builtins: dict[str, Any] = {
            "order_id": order.order_id,
            "amount": order.amount,
            "total_amount": order.total_amount,
            "state": order.state.value,
            "product_ids": order.product_ids,
            "products": order.product_ids,
            "created_at": order.created_at,
            "updated_at": order.updated_at,
            "adjustments": [
                {"kind": a.kind, "label": a.label, "amount": a.amount}
                for a in order.adjustments
            ],
        }
        return {**order.attributes, **builtins}
