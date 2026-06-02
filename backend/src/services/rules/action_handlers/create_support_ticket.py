from typing import Any

from src.domain.order import Order
from src.domain.rules.execution_log import ActionResult
from src.observability.powertools import logger
from src.repositories.base import SupportRepository
from src.services.rules.action_handlers.base import ActionContext, ActionHandler


class CreateSupportTicketHandler(ActionHandler):
    ACTION_TYPE = "create_support_ticket"

    def __init__(self, support_repository: SupportRepository) -> None:
        self._support_repository = support_repository

    def execute(
        self, order: Order, params: dict[str, Any], ctx: ActionContext
    ) -> ActionResult:
        reason = str(params.get("reason", "Manual review required."))

        if ctx.dry_run:
            return ActionResult(
                action_type=self.ACTION_TYPE,
                success=True,
                details={"dryRun": True, "wouldCreateTicketWithReason": reason},
            )

        try:
            ticket_id = self._support_repository.create_ticket(
                order_id=order.order_id,
                reason=reason,
                amount=order.amount,
            )
            logger.info(
                "Support ticket created by rule",
                extra={
                    "ticket_id": ticket_id,
                    "order_id": order.order_id,
                    "rule_id": ctx.rule_id,
                },
            )
            return ActionResult(
                action_type=self.ACTION_TYPE,
                success=True,
                details={"ticketId": ticket_id, "reason": reason},
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception("Support ticket creation failed")
            return ActionResult(
                action_type=self.ACTION_TYPE, success=False, error=str(exc)
            )
