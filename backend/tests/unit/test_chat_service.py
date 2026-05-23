"""Unit tests for the ChatService."""

from unittest.mock import MagicMock, patch

import pytest
from src.services.chat_service import ChatService


@pytest.fixture
def mock_anthropic():
    with patch("src.services.chat_service.Anthropic") as mock:
        yield mock


def test_chat_service_init(mock_anthropic):
    """ChatService should initialize Anthropic with the API key from settings."""
    with patch("src.services.chat_service.get_settings") as mock_settings:
        mock_settings.return_value.anthropic_api_key = "test-key"
        ChatService()
        mock_anthropic.assert_called_once_with(api_key="test-key")


def test_chat_service_reply(mock_anthropic):
    """ChatService.reply should call Anthropic API and return the text content."""
    service = ChatService()

    # Mock the response structure: response.content[0].text
    mock_response = MagicMock()
    mock_text_block = MagicMock()
    mock_text_block.type = "text"
    mock_text_block.text = "Hello from Claude"
    mock_response.content = [mock_text_block]
    service._client.messages.create.return_value = mock_response

    reply = service.reply("Hi", [])

    assert reply == "Hello from Claude"
    assert service._client.messages.create.called


def test_chat_service_load_context_empty_if_missing():
    """_load_context should return empty string if file doesn't exist."""
    from src.services.chat_service import _load_context

    _load_context.cache_clear()
    with patch("src.services.chat_service.CONTEXT_FILE") as mock_file:
        mock_file.exists.return_value = False
        assert _load_context() == ""
    _load_context.cache_clear()
