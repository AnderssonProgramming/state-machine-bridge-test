"""Business rule for the paymentFailed event"""

from aws_lambda_powertools.metrics import MetricUnit

from src.domain.order import Order
from src.observability.powertools import logger, metrics
from src.repositories.base import SupportRepository
from src.services.event_handlers.base import EventHandler

# Orders above this amount (USD) require a manual support review.
SUPPORT_REVIEW_THRESHOLD_USD = 1000.0
HIGH_VALUE_REASON = "High-value payment failure requires manual review."


class PaymentFailedHandler(EventHandler):
    """Creates a support ticket for high-value failed payments."""

    def __init__(self, support_repository: SupportRepository) -> None:
        self._support_repository = support_repository

    def handle(self, order: Order, metadata: dict) -> None:
        """Open a support ticket when the order amount exceeds the threshold."""
        if order.amount <= SUPPORT_REVIEW_THRESHOLD_USD:
            return
        ticket_id = self._support_repository.create_ticket(
            order_id=order.order_id,
            reason=HIGH_VALUE_REASON,
            amount=order.amount,
        )
        logger.info(
            "Support ticket created for failed payment",
            extra={"ticket_id": ticket_id, "order_id": order.order_id},
        )
        metrics.add_metric(name="SupportTicketsCreated", unit=MetricUnit.Count, value=1)