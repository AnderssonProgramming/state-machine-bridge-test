from functools import lru_cache
from pathlib import Path
from typing import Any

from anthropic import Anthropic

from src.config import get_settings

CONTEXT_FILE = Path(__file__).resolve().parents[2] / "context" / "sainapsis_context.txt"
MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 1024

SYSTEM_PROMPT = (
    "You are the assistant for the Sainapsis Order Processing State Machine. "
    "Answer questions about Sainapsis, the Bridge product, and the order state "
    "machine using ONLY the context below. Be concise and accurate. If a "
    "question falls outside this context, say so politely.\n\n=== CONTEXT ===\n"
)


@lru_cache
def _load_context() -> str:
    return CONTEXT_FILE.read_text(encoding="utf-8") if CONTEXT_FILE.exists() else ""


class ChatService:
    def __init__(self) -> None:
        self._client = Anthropic(api_key=get_settings().anthropic_api_key)

    def reply(self, message: str, conversation_history: list[dict[str, Any]]) -> str:
        clean_history = [
            {"role": m["role"], "content": m["content"]}
            for m in conversation_history
            if m.get("role") and m.get("content")
        ]
        messages: list[dict[str, Any]] = [
            *clean_history,
            {"role": "user", "content": message},
        ]
        response = self._client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=f"{SYSTEM_PROMPT}{_load_context()}",
            messages=messages,  # type: ignore[arg-type]
        )
        return "".join(block.text for block in response.content if block.type == "text")
