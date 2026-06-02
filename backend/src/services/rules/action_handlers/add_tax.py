from typing import Any

from src.domain.order import Adjustment, Order
from src.domain.rules.execution_log import ActionResult
from src.observability.powertools import logger
from src.services.rules.action_handlers.base import ActionContext, ActionHandler


class AddTaxHandler(ActionHandler):
    ACTION_TYPE = "add_tax"

    def execute(
        self, order: Order, params: dict[str, Any], ctx: ActionContext
    ) -> ActionResult:
        try:
            percentage = float(params["percentage"])
            label = str(params.get("label", f"Tax {percentage}%"))
        except (KeyError, TypeError, ValueError) as exc:
            return ActionResult(
                action_type=self.ACTION_TYPE,
                success=False,
                error=f"Invalid params: {exc}",
            )

        tax_amount = round(order.amount * (percentage / 100.0), 2)
        adjustment = Adjustment(
            kind="tax", label=label, amount=tax_amount, source_rule_id=ctx.rule_id
        )

        if ctx.dry_run:
            return ActionResult(
                action_type=self.ACTION_TYPE,
                success=True,
                details={
                    "dryRun": True,
                    "wouldAdd": {"kind": "tax", "label": label, "amount": tax_amount},
                },
            )

        added = order.add_adjustment(adjustment)
        if not added:
            return ActionResult(
                action_type=self.ACTION_TYPE,
                success=True,
                details={"skipped": True, "reason": "tax already applied by this rule"},
            )

        logger.info(
            "Tax adjustment added",
            extra={
                "order_id": order.order_id,
                "rule_id": ctx.rule_id,
                "amount": tax_amount,
            },
        )
        return ActionResult(
            action_type=self.ACTION_TYPE,
            success=True,
            details={"kind": "tax", "label": label, "amount": tax_amount},
        )
