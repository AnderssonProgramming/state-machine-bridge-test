from typing import Any

from aws_lambda_powertools.metrics import MetricUnit

from src.domain.order import Order
from src.observability.powertools import logger, metrics
from src.repositories.base import SupportRepository
from src.services.event_handlers.base import EventHandler

SUPPORT_REVIEW_THRESHOLD_USD = 1000.0


class PaymentFailedHandler(EventHandler):
    def __init__(self, support_repository: SupportRepository) -> None:
        self._support_repository = support_repository

    def handle(self, order: Order, metadata: dict[str, Any]) -> None:
        if order.amount <= SUPPORT_REVIEW_THRESHOLD_USD:
            return
        ticket_id = self._support_repository.create_ticket(
            order_id=order.order_id,
            reason="High-value payment failure requires manual review.",
            amount=order.amount,
        )
        logger.info("Support ticket created", extra={"ticket_id": ticket_id, "order_id": order.order_id})
        metrics.add_metric(name="SupportTicketsCreated", unit=MetricUnit.Count, value=1)
