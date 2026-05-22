"""Application service orchestrating orders, transitions, and event rules."""

from aws_lambda_powertools.metrics import MetricUnit

from src.domain.events import EventType
from src.domain.exceptions import InvalidTransitionError, OrderNotFoundError
from src.domain.order import Order
from src.domain.state_machine import StateMachine
from src.domain.states import OrderState
from src.observability.powertools import logger, metrics, tracer
from src.repositories.base import OrderRepository
from src.services.event_handlers.base import EventHandlerRegistry


class OrderService:
    """Coordinates the state machine, persistence, and event business logic."""

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
        """Create a new order in the Pending state."""
        order = Order(product_ids=product_ids, amount=amount)
        self._orders.save(order)
        logger.info("Order created", extra={"order_id": order.order_id})
        metrics.add_metric(name="OrdersCreated", unit=MetricUnit.Count, value=1)
        return order

    @tracer.capture_method
    def apply_event(self, order_id: str, event_type: str, metadata: dict) -> Order:
        """Apply an event to an order, running business rules and transitioning.

        Args:
            order_id: Identifier of the target order.
            event_type: Name of the triggering event.
            metadata: Event-specific data.

        Returns:
            The updated order.

        Raises:
            OrderNotFoundError: If the order does not exist.
            InvalidTransitionError: If the transition is not allowed.
        """
        order = self._orders.get_by_id(order_id)
        if order is None:
            raise OrderNotFoundError(order_id)

        try:
            event = EventType(event_type)
        except ValueError as exc:
            metrics.add_metric(name="TransitionErrors", unit=MetricUnit.Count, value=1)
            raise InvalidTransitionError(order.state.value, event_type) from exc

        try:
            next_state = self._state_machine.next_state(order.state, event)
        except InvalidTransitionError:
            metrics.add_metric(name="TransitionErrors", unit=MetricUnit.Count, value=1)
            raise

        # Run event-specific business rules (Open/Closed extension point).
        handler = self._handlers.get(event_type)
        if handler is not None:
            handler.handle(order, metadata)

        order.apply_transition(next_state, event_type, metadata)
        self._orders.save(order)

        logger.info(
            "Order transitioned",
            extra={
                "order_id": order_id,
                "event_type": event_type,
                "new_state": next_state.value,
            },
        )
        return order

    def get_order(self, order_id: str) -> Order:
        """Return an order by id or raise if missing."""
        order = self._orders.get_by_id(order_id)
        if order is None:
            raise OrderNotFoundError(order_id)
        return order

    def list_orders(self) -> list[Order]:
        """Return all orders."""
        return self._orders.list_all()

    def available_events(
        self, order_id: str
    ) -> tuple[OrderState, list[EventType]]:
        """Return the current state and valid next events for an order."""
        order = self.get_order(order_id)
        return order.state, self._state_machine.available_events(order.state)