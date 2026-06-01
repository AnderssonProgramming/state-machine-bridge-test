from typing import Any

from aws_lambda_powertools.metrics import MetricUnit

from src.domain.events import EventType
from src.domain.exceptions import OrderNotFoundError
from src.domain.order import Order
from src.domain.state_machine import StateMachine
from src.observability.powertools import logger, metrics, tracer
from src.repositories.base import OrderRepository
from src.services.event_handlers.base import EventHandlerRegistry


class OrderService:
    def __init__(
        self,
        order_repository: OrderRepository,
        state_machine: StateMachine,
        handler_registry: EventHandlerRegistry,
    ) -> None:
        self._orders = order_repository
        self._state_machine = state_machine
        self._handlers = handler_registry

    @tracer.capture_method
    def create_order(self, product_ids: list[str], amount: float) -> Order:
        order = Order(product_ids=product_ids, amount=amount)
        self._orders.save(order)
        logger.info("Order created", extra={"order_id": order.order_id})
        metrics.add_metric(name="OrdersCreated", unit=MetricUnit.Count, value=1)
        return order

    @tracer.capture_method
    def apply_event(self, order_id: str, event_type: str, metadata: dict[str, Any]) -> tuple[str, Order]:
        order = self._get_or_raise(order_id)
        previous_state = order.state.value
        event = EventType(event_type)
        next_state = self._state_machine.next_state(order.state, event)

        handler = self._handlers.get(event_type)
        if handler is not None:
            handler.handle(order, metadata)

        order.apply_transition(next_state, event_type, metadata)
        self._orders.save(order)
        logger.info(
            "Order transitioned",
            extra={"order_id": order_id, "event_type": event_type, "new_state": next_state.value},
        )
        return previous_state, order

    def get_order(self, order_id: str) -> Order:
        return self._get_or_raise(order_id)

    def list_orders(self) -> list[Order]:
        return self._orders.list_all()

    def available_events(self, order_id: str) -> list[EventType]:
        order = self._get_or_raise(order_id)
        return self._state_machine.available_events(order.state)

    def _get_or_raise(self, order_id: str) -> Order:
        order = self._orders.get_by_id(order_id)
        if order is None:
            raise OrderNotFoundError(order_id)
        return order
