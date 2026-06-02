from functools import lru_cache

from src.config import RepositoryBackend, get_settings
from src.domain.events import EventType
from src.domain.state_machine import StateMachine
from src.repositories.base import (
    OrderRepository,
    RuleLogRepository,
    RuleRepository,
    SupportRepository,
)
from src.repositories.memory import (
    InMemoryOrderRepository,
    InMemoryRuleLogRepository,
    InMemoryRuleRepository,
    InMemorySupportRepository,
)
from src.services.chat_service import ChatService
from src.services.event_handlers.base import EventHandlerRegistry
from src.services.event_handlers.payment_failed import PaymentFailedHandler
from src.services.order_service import OrderService
from src.services.rules.action_handlers.add_fee import AddFeeHandler
from src.services.rules.action_handlers.add_tax import AddTaxHandler
from src.services.rules.action_handlers.base import ActionHandlerRegistry
from src.services.rules.action_handlers.create_support_ticket import (
    CreateSupportTicketHandler,
)
from src.services.rules.engine import RuleEngineService


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
def get_rule_repository() -> RuleRepository:
    return InMemoryRuleRepository()


@lru_cache
def get_rule_log_repository() -> RuleLogRepository:
    return InMemoryRuleLogRepository()


@lru_cache
def get_handler_registry() -> EventHandlerRegistry:
    registry = EventHandlerRegistry()
    registry.register(
        EventType.PAYMENT_FAILED.value, PaymentFailedHandler(get_support_repository())
    )
    return registry


@lru_cache
def get_action_registry() -> ActionHandlerRegistry:
    registry = ActionHandlerRegistry()
    registry.register(
        CreateSupportTicketHandler.ACTION_TYPE,
        CreateSupportTicketHandler(get_support_repository()),
    )
    registry.register(AddTaxHandler.ACTION_TYPE, AddTaxHandler())
    registry.register(AddFeeHandler.ACTION_TYPE, AddFeeHandler())
    return registry


@lru_cache
def get_rule_engine() -> RuleEngineService:
    return RuleEngineService(
        rule_repository=get_rule_repository(),
        log_repository=get_rule_log_repository(),
        action_registry=get_action_registry(),
    )


@lru_cache
def get_order_service() -> OrderService:
    return OrderService(
        order_repository=get_order_repository(),
        state_machine=StateMachine(),
        handler_registry=get_handler_registry(),
        rule_engine=get_rule_engine(),
    )


@lru_cache
def get_chat_service() -> ChatService:
    return ChatService()
