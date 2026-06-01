from functools import lru_cache

from src.config import RepositoryBackend, get_settings
from src.domain.events import EventType
from src.domain.state_machine import StateMachine
from src.repositories.base import OrderRepository, SupportRepository
from src.repositories.memory import InMemoryOrderRepository, InMemorySupportRepository
from src.services.chat_service import ChatService
from src.services.event_handlers.base import EventHandlerRegistry
from src.services.event_handlers.payment_failed import PaymentFailedHandler
from src.services.order_service import OrderService


@lru_cache
def get_order_repository() -> OrderRepository:
    if get_settings().repository_backend == RepositoryBackend.DYNAMODB:
        from src.repositories.dynamodb import DynamoDBOrderRepository

        return DynamoDBOrderRepository()
    return InMemoryOrderRepository()


@lru_cache
def get_support_repository() -> SupportRepository:
    if get_settings().repository_backend == RepositoryBackend.DYNAMODB:
        from src.repositories.dynamodb import DynamoDBSupportRepository

        return DynamoDBSupportRepository()
    return InMemorySupportRepository()


@lru_cache
def get_handler_registry() -> EventHandlerRegistry:
    registry = EventHandlerRegistry()
    registry.register(
        EventType.PAYMENT_FAILED.value, PaymentFailedHandler(get_support_repository())
    )
    return registry


@lru_cache
def get_order_service() -> OrderService:
    return OrderService(
        order_repository=get_order_repository(),
        state_machine=StateMachine(),
        handler_registry=get_handler_registry(),
    )


@lru_cache
def get_chat_service() -> ChatService:
    return ChatService()
