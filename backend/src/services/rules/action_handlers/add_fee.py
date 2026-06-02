from typing import Any

from src.domain.order import Adjustment, Order
from src.domain.rules.execution_log import ActionResult
from src.observability.powertools import logger
from src.services.rules.action_handlers.base import ActionContext, ActionHandler


class AddFeeHandler(ActionHandler):
    ACTION_TYPE = "add_fee"

    def execute(
        self, order: Order, params: dict[str, Any], ctx: ActionContext
    ) -> ActionResult:
        try:
            fee_amount = float(params["amount"])
            label = str(params.get("label", "Additional fee"))
        except (KeyError, TypeError, ValueError) as exc:
            return ActionResult(
                action_type=self.ACTION_TYPE,
                success=False,
                error=f"Invalid params: {exc}",
            )

        adjustment = Adjustment(
            kind="fee", label=label, amount=fee_amount, source_rule_id=ctx.rule_id
        )

        if ctx.dry_run:
            return ActionResult(
                action_type=self.ACTION_TYPE,
                success=True,
                details={
                    "dryRun": True,
                    "wouldAdd": {"kind": "fee", "label": label, "amount": fee_amount},
                },
            )

        added = order.add_adjustment(adjustment)
        if not added:
            return ActionResult(
                action_type=self.ACTION_TYPE,
                success=True,
                details={"skipped": True, "reason": "fee already applied by this rule"},
            )

        logger.info(
            "Fee adjustment added",
            extra={
                "order_id": order.order_id,
                "rule_id": ctx.rule_id,
                "amount": fee_amount,
            },
        )
        return ActionResult(
            action_type=self.ACTION_TYPE,
            success=True,
            details={"kind": "fee", "label": label, "amount": fee_amount},
        )
