from typing import Annotated

from fastapi import APIRouter, Depends

from src.handlers.dependencies import get_chat_service
from src.models.schemas import ChatRequest, ChatResponse
from src.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("")
def chat(
    payload: ChatRequest,
    service: Annotated[ChatService, Depends(get_chat_service)],
) -> ChatResponse:
    return ChatResponse(
        reply=service.reply(payload.message, payload.conversation_history)
    )
