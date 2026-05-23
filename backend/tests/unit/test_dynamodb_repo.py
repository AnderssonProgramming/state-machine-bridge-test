"""Unit tests for DynamoDB repository implementations using moto."""

import boto3
import pytest
from moto import mock_aws
from src.domain.order import Order
from src.repositories.dynamodb import DynamoDBOrderRepository, DynamoDBSupportRepository

TABLE_NAME = "orders"
TICKETS_TABLE_NAME = "support-tickets"
REGION = "us-east-1"


@pytest.fixture
def aws_settings(monkeypatch):
    """Mock application settings for DynamoDB tables."""
    # Ensure settings match the created table names
    monkeypatch.setenv("REPOSITORY_BACKEND", "dynamodb")
    monkeypatch.setenv("DYNAMODB_TABLE_NAME", TABLE_NAME)
    monkeypatch.setenv("DYNAMODB_TICKETS_TABLE_NAME", TICKETS_TABLE_NAME)
    monkeypatch.setenv("AWS_REGION", REGION)


@pytest.fixture
def mock_dynamodb():
    """Start moto's mock DynamoDB service."""
    with mock_aws():
        db = boto3.resource("dynamodb", region_name=REGION)

        # Create Orders Table
        db.create_table(
            TableName=TABLE_NAME,
            KeySchema=[{"AttributeName": "orderId", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "orderId", "AttributeType": "S"}],
            ProvisionedThroughput={"ReadCapacityUnits": 1, "WriteCapacityUnits": 1},
        )

        # Create Tickets Table
        db.create_table(
            TableName=TICKETS_TABLE_NAME,
            KeySchema=[{"AttributeName": "ticketId", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "ticketId", "AttributeType": "S"}],
            ProvisionedThroughput={"ReadCapacityUnits": 1, "WriteCapacityUnits": 1},
        )
        yield db


def test_dynamodb_order_save_and_get(aws_settings, mock_dynamodb):
    repo = DynamoDBOrderRepository()
    order = Order(product_ids=["p1", "p2"], amount=150.0)

    repo.save(order)
    result = repo.get_by_id(order.order_id)

    assert result is not None
    assert result.order_id == order.order_id
    assert result.amount == 150.0
    assert result.product_ids == ["p1", "p2"]
    assert len(result.history) == 1


def test_dynamodb_order_get_missing(aws_settings, mock_dynamodb):
    repo = DynamoDBOrderRepository()
    assert repo.get_by_id("missing") is None


def test_dynamodb_order_list_all(aws_settings, mock_dynamodb):
    repo = DynamoDBOrderRepository()
    order1 = Order(product_ids=["p1"], amount=10.0)
    order2 = Order(product_ids=["p2"], amount=20.0)

    repo.save(order1)
    repo.save(order2)

    results = repo.list_all()
    assert len(results) == 2
    ids = [o.order_id for o in results]
    assert order1.order_id in ids
    assert order2.order_id in ids


def test_dynamodb_support_create_ticket(aws_settings, mock_dynamodb):
    repo = DynamoDBSupportRepository()
    ticket_id = repo.create_ticket("ord-123", "Payment failed high value", 1200.0)

    assert ticket_id.startswith("ticket-")

    # Verify in table
    table = mock_dynamodb.Table(TICKETS_TABLE_NAME)
    item = table.get_item(Key={"ticketId": ticket_id})["Item"]
    assert item["orderId"] == "ord-123"
    assert item["amount"] == "1200.0"
