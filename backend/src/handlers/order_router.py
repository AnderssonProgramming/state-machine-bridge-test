"""FastAPI routes for order creation and lifecycle events."""

from fastapi import APIRouter, Depends, status

from src.domain.order import Order
from src.handlers.dependencies import get_order_service
from src.models.schemas import (
    AvailableEventsResponse,
    CreateOrderRequest,
    EventRequest,
    OrderResponse,
    TransitionResponse,
)
from src.services.order_service import OrderService

router = APIRouter(prefix="/orders", tags=["orders"])


def _to_response(order: Order) -> OrderResponse:
    """Map an Order entity to its API response model."""
    return OrderResponse(
        orderId=order.order_id,
        productIds=order.product_ids,
        amount=order.amount,
        state=order.state,
        createdAt=order.created_at,
        updatedAt=order.updated_at,
        history=[
            TransitionLogResponse_from(entry) for entry in order.history
        ],
    )


def TransitionLogResponse_from(entry):  # noqa: N802
    """Map a TransitionLog dataclass to a response dict (alias keys)."""
    return {
        "fromState": entry.from_state,
        "toState": entry.to_state,
        "eventType": entry.event_type,
        "timestamp": entry.timestamp,
        "metadata": entry.metadata,
    }


@router.post("", status_code=status.HTTP_201_CREATED, response_model=OrderResponse)
def create_order(
    payload: CreateOrderRequest,
    service: OrderService = Depends(get_order_service),
) -> OrderResponse:
    """Create a new order in the Pending state."""
    order = service.create_order(payload.product_ids, payload.amount)
    return _to_response(order)


@router.post("/{order_id}/events", response_model=TransitionResponse)
def apply_event(
    order_id: str,
    payload: EventRequest,
    service: OrderService = Depends(get_order_service),
) -> TransitionResponse:
    """Apply an event to an order, transitioning its state."""
    previous_state = service.get_order(order_id).state.value
    order = service.apply_event(order_id, payload.event_type, payload.metadata)
    return TransitionResponse(
        orderId=order.order_id,
        previousState=previous_state,
        currentState=order.state.value,
        eventType=payload.event_type,
        timestamp=order.updated_at,
    )


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: str,
    service: OrderService = Depends(get_order_service),
) -> OrderResponse:
    """Return a single order with its full history."""
    return _to_response(service.get_order(order_id))


@router.get("", response_model=list[OrderResponse])
def list_orders(
    service: OrderService = Depends(get_order_service),
) -> list[OrderResponse]:
    """Return all orders."""
    return [_to_response(order) for order in service.list_orders()]


@router.get(
    "/{order_id}/available-events", response_model=AvailableEventsResponse
)
def available_events(
    order_id: str,
    service: OrderService = Depends(get_order_service),
) -> AvailableEventsResponse:
    """Return valid next events for an order (powers the frontend dropdown)."""
    state, events = service.available_events(order_id)
    return AvailableEventsResponse(
        orderId=order_id,
        state=state,
        availableEvents=[event.value for event in events],
    )