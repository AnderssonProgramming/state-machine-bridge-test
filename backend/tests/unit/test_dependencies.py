"""Unit tests for dependency injection wiring."""

from unittest.mock import patch

from src.config import RepositoryBackend
from src.handlers import dependencies


def test_get_order_repository_memory():
    """get_order_repository should return InMemoryOrderRepository by default."""
    dependencies.get_order_repository.cache_clear()
    with patch("src.handlers.dependencies.get_settings") as mock_settings:
        mock_settings.return_value.repository_backend = RepositoryBackend.MEMORY
        repo = dependencies.get_order_repository()
        from src.repositories.memory import InMemoryOrderRepository

        assert isinstance(repo, InMemoryOrderRepository)


def test_get_order_repository_dynamodb():
    """get_order_repository should return DynamoDBOrderRepository when configured."""
    dependencies.get_order_repository.cache_clear()
    with patch("src.handlers.dependencies.get_settings") as mock_settings:
        mock_settings.return_value.repository_backend = RepositoryBackend.DYNAMODB
        # We mock the import to avoid actual DynamoDB connection
        with patch("src.repositories.dynamodb.DynamoDBOrderRepository") as mock_repo:
            repo = dependencies.get_order_repository()
            assert repo == mock_repo()


def test_get_support_repository_memory():
    """get_support_repository should return InMemorySupportRepository by default."""
    dependencies.get_support_repository.cache_clear()
    with patch("src.handlers.dependencies.get_settings") as mock_settings:
        mock_settings.return_value.repository_backend = RepositoryBackend.MEMORY
        repo = dependencies.get_support_repository()
        from src.repositories.memory import InMemorySupportRepository

        assert isinstance(repo, InMemorySupportRepository)


def test_get_support_repository_dynamodb():
    """get_support_repository should return DynamoDBSupportRepository when configured."""
    dependencies.get_support_repository.cache_clear()
    with patch("src.handlers.dependencies.get_settings") as mock_settings:
        mock_settings.return_value.repository_backend = RepositoryBackend.DYNAMODB
        with patch("src.repositories.dynamodb.DynamoDBSupportRepository") as mock_repo:
            repo = dependencies.get_support_repository()
            assert repo == mock_repo()


def test_get_chat_service():
    """get_chat_service should return a ChatService instance."""
    dependencies.get_chat_service.cache_clear()
    service = dependencies.get_chat_service()
    from src.services.chat_service import ChatService

    assert isinstance(service, ChatService)


def test_get_handler_registry():
    """get_handler_registry should return a registry with handlers."""
    dependencies.get_handler_registry.cache_clear()
    registry = dependencies.get_handler_registry()
    from src.services.event_handlers.base import EventHandlerRegistry

    assert isinstance(registry, EventHandlerRegistry)


def test_get_order_service():
    """get_order_service should return an OrderService instance."""
    dependencies.get_order_service.cache_clear()
    service = dependencies.get_order_service()
    from src.services.order_service import OrderService

    assert isinstance(service, OrderService)
