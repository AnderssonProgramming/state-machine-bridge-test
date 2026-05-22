"""Order states for the processing state machine."""

from enum import Enum


class OrderState(str, Enum):
    """All possible states an order can be in."""

    PENDING = "Pending"
    ON_HOLD = "OnHold"
    PENDING_PAYMENT = "PendingPayment"
    CONFIRMED = "Confirmed"
    PROCESSING = "Processing"
    SHIPPED = "Shipped"
    DELIVERED = "Delivered"
    RETURNING = "Returning"
    RETURNED = "Returned"
    REFUNDED = "Refunded"
    CANCELLED = "Cancelled"