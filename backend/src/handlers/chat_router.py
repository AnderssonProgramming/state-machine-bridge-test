"""FastAPI route for the AI chatbot."""

from fastapi import APIRouter, Depends

from src.handlers.dependencies import get_chat_service
from src.models.schemas import ChatRequest, ChatResponse
from src.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    service: ChatService = Depends(get_chat_service),
) -> ChatResponse:
    """Return an AI assistant reply grounded in Sainapsis context."""
    reply = service.reply(payload.message, payload.conversation_history)
    return ChatResponse(reply=reply)
