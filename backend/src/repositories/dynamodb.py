"""DynamoDB repository implementations for production (AWS Lambda).

Amounts are stored as strings to avoid DynamoDB's Decimal/float friction
and converted back to float on read.
"""

import uuid
from dataclasses import asdict

import boto3

from src.config import get_settings
from src.domain.order import Order, TransitionLog
from src.domain.states import OrderState
from src.repositories.base import OrderRepository, SupportRepository

TICKET_ID_PREFIX = "ticket-"
TICKET_ID_LENGTH = 8


class DynamoDBOrderRepository(OrderRepository):
    """Order store backed by a single DynamoDB table."""

    def __init__(self) -> None:
        settings = get_settings()
        resource = boto3.resource("dynamodb", region_name=settings.aws_region)
        self._table = resource.Table(settings.dynamodb_table_name)

    def save(self, order: Order) -> None:
        """Persist an order item to DynamoDB."""
        self._table.put_item(Item=self._to_item(order))

    def get_by_id(self, order_id: str) -> Order | None:
        """Fetch and deserialize an order by its id."""
        response = self._table.get_item(Key={"orderId": order_id})
        item = response.get("Item")
        if item is None:
            return None
        return self._from_item(item)

    def list_all(self) -> list[Order]:
        """Scan and return all orders (acceptable for MVP scale)."""
        response = self._table.scan()
        return [self._from_item(item) for item in response.get("Items", [])]

    @staticmethod
    def _to_item(order: Order) -> dict:
        """Convert an Order entity into a DynamoDB item."""
        return {
            "orderId": order.order_id,
            "productIds": order.product_ids,
            "amount": str(order.amount),
            "state": order.state.value,
            "createdAt": order.created_at,
            "updatedAt": order.updated_at,
            "history": [asdict(entry) for entry in order.history],
        }

    @staticmethod
    def _from_item(item: dict) -> Order:
        """Reconstruct an Order entity from a DynamoDB item."""
        return Order(
            product_ids=list(item["productIds"]),
            amount=float(item["amount"]),
            state=OrderState(item["state"]),
            order_id=item["orderId"],
            created_at=item["createdAt"],
            updated_at=item["updatedAt"],
            history=[TransitionLog(**entry) for entry in item.get("history", [])],
        )


class DynamoDBSupportRepository(SupportRepository):
    """Support ticket store backed by a DynamoDB table."""

    def __init__(self) -> None:
        settings = get_settings()
        resource = boto3.resource("dynamodb", region_name=settings.aws_region)
        self._table = resource.Table(settings.dynamodb_tickets_table_name)

    def create_ticket(self, order_id: str, reason: str, amount: float) -> str:
        """Create a support ticket item and return its id."""
        ticket_id = f"{TICKET_ID_PREFIX}{uuid.uuid4().hex[:TICKET_ID_LENGTH]}"
        self._table.put_item(
            Item={
                "ticketId": ticket_id,
                "orderId": order_id,
                "reason": reason,
                "amount": str(amount),
            }
        )
        return ticket_id
