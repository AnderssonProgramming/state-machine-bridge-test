"""Pydantic request and response schemas (presentation contracts)."""

from pydantic import BaseModel, ConfigDict, Field

from src.domain.states import OrderState

_CAMEL = ConfigDict(populate_by_name=True)


class CreateOrderRequest(BaseModel):
    """Payload to create a new order."""

    model_config = _CAMEL

    product_ids: list[str] = Field(..., alias="productIds", min_length=1)
    amount: float = Field(..., gt=0)


class EventRequest(BaseModel):
    """Payload to apply an event to an existing order."""

    model_config = _CAMEL

    event_type: str = Field(..., alias="eventType")
    metadata: dict = Field(default_factory=dict)


class TransitionLogResponse(BaseModel):
    """A single transition entry in the order history."""

    model_config = _CAMEL

    from_state: str | None = Field(..., alias="fromState")
    to_state: str = Field(..., alias="toState")
    event_type: str = Field(..., alias="eventType")
    timestamp: str
    metadata: dict


class OrderResponse(BaseModel):
    """Full order representation returned to clients."""

    model_config = _CAMEL

    order_id: str = Field(..., alias="orderId")
    product_ids: list[str] = Field(..., alias="productIds")
    amount: float
    state: OrderState
    created_at: str = Field(..., alias="createdAt")
    updated_at: str = Field(..., alias="updatedAt")
    history: list[TransitionLogResponse]


class TransitionResponse(BaseModel):
    """Response after a successful transition."""

    model_config = _CAMEL

    order_id: str = Field(..., alias="orderId")
    previous_state: str = Field(..., alias="previousState")
    current_state: str = Field(..., alias="currentState")
    event_type: str = Field(..., alias="eventType")
    timestamp: str


class AvailableEventsResponse(BaseModel):
    """The list of events currently valid for an order."""

    model_config = _CAMEL

    order_id: str = Field(..., alias="orderId")
    state: OrderState
    available_events: list[str] = Field(..., alias="availableEvents")


class ChatRequest(BaseModel):
    """Chatbot message payload."""

    model_config = _CAMEL

    message: str
    conversation_history: list[dict] = Field(
        default_factory=list, alias="conversationHistory"
    )


class ChatResponse(BaseModel):
    """Chatbot reply payload."""

    reply: str