import pytest
from fastapi.testclient import TestClient
from src.domain.state_machine import StateMachine
from src.handlers.dependencies import (
    get_chat_service,
    get_order_service,
    get_rule_engine,
    get_rule_log_repository,
    get_rule_repository,
)
from src.main import app
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


@pytest.fixture
def order_repo() -> InMemoryOrderRepository:
    return InMemoryOrderRepository()


@pytest.fixture
def support_repo() -> InMemorySupportRepository:
    return InMemorySupportRepository()


@pytest.fixture
def rule_repo() -> InMemoryRuleRepository:
    return InMemoryRuleRepository()


@pytest.fixture
def log_repo() -> InMemoryRuleLogRepository:
    return InMemoryRuleLogRepository()


@pytest.fixture
def state_machine() -> StateMachine:
    return StateMachine()


@pytest.fixture
def handler_registry(support_repo: InMemorySupportRepository) -> EventHandlerRegistry:
    registry = EventHandlerRegistry()
    registry.register("paymentFailed", PaymentFailedHandler(support_repo))
    return registry


@pytest.fixture
def action_registry(support_repo: InMemorySupportRepository) -> ActionHandlerRegistry:
    registry = ActionHandlerRegistry()
    registry.register(
        CreateSupportTicketHandler.ACTION_TYPE, CreateSupportTicketHandler(support_repo)
    )
    registry.register(AddTaxHandler.ACTION_TYPE, AddTaxHandler())
    registry.register(AddFeeHandler.ACTION_TYPE, AddFeeHandler())
    return registry


@pytest.fixture
def rule_engine(
    rule_repo: InMemoryRuleRepository,
    log_repo: InMemoryRuleLogRepository,
    action_registry: ActionHandlerRegistry,
) -> RuleEngineService:
    return RuleEngineService(rule_repo, log_repo, action_registry)


@pytest.fixture
def order_service(
    order_repo: InMemoryOrderRepository,
    state_machine: StateMachine,
    handler_registry: EventHandlerRegistry,
    rule_engine: RuleEngineService,
) -> OrderService:
    return OrderService(
        order_repository=order_repo,
        state_machine=state_machine,
        handler_registry=handler_registry,
        rule_engine=rule_engine,
    )


class _MockChatService(ChatService):
    def __init__(self) -> None:  # skip Anthropic client init
        pass

    def reply(self, message: str, conversation_history: list) -> str:  # type: ignore[override]
        return "Mock reply."


@pytest.fixture
def client() -> TestClient:
    test_order_repo = InMemoryOrderRepository()
    test_support_repo = InMemorySupportRepository()
    test_rule_repo = InMemoryRuleRepository()
    test_log_repo = InMemoryRuleLogRepository()

    test_legacy = EventHandlerRegistry()
    test_legacy.register("paymentFailed", PaymentFailedHandler(test_support_repo))

    test_actions = ActionHandlerRegistry()
    test_actions.register(
        CreateSupportTicketHandler.ACTION_TYPE,
        CreateSupportTicketHandler(test_support_repo),
    )
    test_actions.register(AddTaxHandler.ACTION_TYPE, AddTaxHandler())
    test_actions.register(AddFeeHandler.ACTION_TYPE, AddFeeHandler())

    test_engine = RuleEngineService(test_rule_repo, test_log_repo, test_actions)

    test_service = OrderService(
        order_repository=test_order_repo,
        state_machine=StateMachine(),
        handler_registry=test_legacy,
        rule_engine=test_engine,
    )

    app.dependency_overrides[get_order_service] = lambda: test_service
    app.dependency_overrides[get_chat_service] = lambda: _MockChatService()
    app.dependency_overrides[get_rule_repository] = lambda: test_rule_repo
    app.dependency_overrides[get_rule_log_repository] = lambda: test_log_repo
    app.dependency_overrides[get_rule_engine] = lambda: test_engine

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
