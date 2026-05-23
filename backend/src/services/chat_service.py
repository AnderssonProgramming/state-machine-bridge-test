"""AI chatbot service backed by the Anthropic Claude API."""

from functools import lru_cache
from pathlib import Path

from anthropic import Anthropic

from src.config import get_settings

CONTEXT_FILE = Path(__file__).resolve().parents[2] / "context" / "sainapsis_context.txt"
MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 1024

SYSTEM_PREAMBLE = (
    "You are the assistant for the Sainapsis Order Processing State Machine. "
    "Answer questions about Sainapsis, the Bridge product, and the order state "
    "machine using ONLY the context below. Be concise and accurate. If a "
    "question falls outside this context, say so politely.\n\n=== CONTEXT ===\n"
)


@lru_cache
def _load_context() -> str:
    """Load the Sainapsis context file once and cache it."""
    if not CONTEXT_FILE.exists():
        return ""
    return CONTEXT_FILE.read_text(encoding="utf-8")


class ChatService:
    """Answers user questions using Claude with Sainapsis domain context."""

    def __init__(self) -> None:
        settings = get_settings()
        self._client = Anthropic(api_key=settings.anthropic_api_key)

    def reply(self, message: str, conversation_history: list[dict]) -> str:
        """Generate an assistant reply for a user message.

        Args:
            message: The latest user message.
            conversation_history: Prior messages as {role, content} dicts.

        Returns:
            The assistant's text reply.
        """
        messages = [*conversation_history, {"role": "user", "content": message}]
        response = self._client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=f"{SYSTEM_PREAMBLE}{_load_context()}",
            messages=messages,
        )
        return "".join(block.text for block in response.content if block.type == "text")
