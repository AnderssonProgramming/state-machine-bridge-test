"""FastAPI routes for order creation and lifecycle events."""

from typing import Annotated

from fastapi import APIRouter, Depends, status

from src.domain.order import Order, TransitionLog
from src.handlers.dependencies import get_order_service
from src.models.schemas import (
    AvailableEventsResponse,
    CreateOrderRequest,
    EventRequest,
    OrderResponse,
    TransitionLogResponse,
    TransitionResponse,
)
from src.services.order_service import OrderService

router = APIRouter(prefix="/orders", tags=["orders"])


def _map_log(entry: TransitionLog) -> TransitionLogResponse:
    """Map a domain TransitionLog to its response model."""
    return TransitionLogResponse(
        from_state=entry.from_state,
        to_state=entry.to_state,
        event_type=entry.event_type,
        timestamp=entry.timestamp,
        metadata=entry.metadata,
    )


def _to_response(order: Order) -> OrderResponse:
    """Map an Order entity to its API response model."""
    return OrderResponse(
        order_id=order.order_id,
        product_ids=order.product_ids,
        amount=order.amount,
        state=order.state,
        created_at=order.created_at,
        updated_at=order.updated_at,
        history=[_map_log(entry) for entry in order.history],
    )


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=True,
)
def create_order(
    payload: CreateOrderRequest,
    service: Annotated[OrderService, Depends(get_order_service)],
) -> OrderResponse:
    """Create a new order in the Pending state."""
    return _to_response(service.create_order(payload.product_ids, payload.amount))


@router.post(
    "/{order_id}/events",
    response_model_by_alias=True,
)
def apply_event(
    order_id: str,
    payload: EventRequest,
    service: Annotated[OrderService, Depends(get_order_service)],
) -> TransitionResponse:
    """Apply an event to an order, transitioning its state."""
    previous_state = service.get_order(order_id).state.value
    order = service.apply_event(order_id, payload.event_type, payload.metadata)
    return TransitionResponse(
        order_id=order.order_id,
        previous_state=previous_state,
        current_state=order.state.value,
        event_type=payload.event_type,
        timestamp=order.updated_at,
    )


@router.get(
    "/{order_id}",
    response_model_by_alias=True,
)
def get_order(
    order_id: str,
    service: Annotated[OrderService, Depends(get_order_service)],
) -> OrderResponse:
    """Return a single order with its full history."""
    return _to_response(service.get_order(order_id))


@router.get(
    "",
    response_model_by_alias=True,
)
def list_orders(
    service: Annotated[OrderService, Depends(get_order_service)],
) -> list[OrderResponse]:
    """Return all orders."""
    return [_to_response(order) for order in service.list_orders()]


@router.get(
    "/{order_id}/available-events",
    response_model_by_alias=True,
)
def available_events(
    order_id: str,
    service: Annotated[OrderService, Depends(get_order_service)],
) -> AvailableEventsResponse:
    """Return valid next events for an order (powers the frontend dropdown)."""
    state, events = service.available_events(order_id)
    return AvailableEventsResponse(
        order_id=order_id,
        state=state,
        available_events=[event.value for event in events],
    )
