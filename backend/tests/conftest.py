"""Shared pytest fixtures for unit and integration tests."""

import pytest
from fastapi.testclient import TestClient
from src.domain.state_machine import StateMachine
from src.handlers.dependencies import get_chat_service, get_order_service
from src.main import app
from src.repositories.memory import (
    InMemoryOrderRepository,
    InMemorySupportRepository,
)
from src.services.chat_service import ChatService
from src.services.event_handlers.base import EventHandlerRegistry
from src.services.event_handlers.payment_failed import PaymentFailedHandler
from src.services.order_service import OrderService

# ── Unit test fixtures ─────────────────────────────────────────────────────────


@pytest.fixture
def order_repo() -> InMemoryOrderRepository:
    """Fresh in-memory order repository per test."""
    return InMemoryOrderRepository()


@pytest.fixture
def support_repo() -> InMemorySupportRepository:
    """Fresh in-memory support ticket repository per test."""
    return InMemorySupportRepository()


@pytest.fixture
def state_machine() -> StateMachine:
    """StateMachine instance (stateless — shared is fine)."""
    return StateMachine()


@pytest.fixture
def handler_registry(support_repo: InMemorySupportRepository) -> EventHandlerRegistry:
    """Registry wired with the paymentFailed handler."""
    registry = EventHandlerRegistry()
    registry.register("paymentFailed", PaymentFailedHandler(support_repo))
    return registry


@pytest.fixture
def order_service(
    order_repo: InMemoryOrderRepository,
    state_machine: StateMachine,
    handler_registry: EventHandlerRegistry,
) -> OrderService:
    """Fully assembled OrderService with in-memory collaborators."""
    return OrderService(
        order_repository=order_repo,
        state_machine=state_machine,
        handler_registry=handler_registry,
    )


# ── Integration test fixtures ──────────────────────────────────────────────────


class _MockChatService(ChatService):
    """Stub that never calls the real Anthropic API."""

    def __init__(self) -> None:  # skip super().__init__()
        pass

    def reply(self, message: str, conversation_history: list) -> str:  # type: ignore[override]
        return "Mock reply."


@pytest.fixture
def client() -> TestClient:
    """
    TestClient with dependency overrides.

    Each test receives a fresh in-memory store and a mocked chat service,
    so tests are fully isolated and require no real AWS/Anthropic credentials.
    """
    test_order_repo = InMemoryOrderRepository()
    test_support_repo = InMemorySupportRepository()
    test_registry = EventHandlerRegistry()
    test_registry.register("paymentFailed", PaymentFailedHandler(test_support_repo))
    test_service = OrderService(
        order_repository=test_order_repo,
        state_machine=StateMachine(),
        handler_registry=test_registry,
    )

    app.dependency_overrides[get_order_service] = lambda: test_service
    app.dependency_overrides[get_chat_service] = lambda: _MockChatService()

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
