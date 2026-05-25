"""FastAPI application entrypoint and AWS Lambda handler.

 ██████╗ ██████╗ ██████╗ ███████╗██████╗
██╔═══██╗██╔══██╗██╔══██╗██╔════╝██╔══██╗
██║   ██║██████╔╝██║  ██║█████╗  ██████╔╝
██║   ██║██╔══██╗██║  ██║██╔══╝  ██╔══██╗
╚██████╔╝██║  ██║██████╔╝███████╗██║  ██║
 ╚═════╝ ╚═╝  ╚═╝╚═════╝ ╚══════╝╚═╝  ╚═╝

Order Processing State Machine — Sainapsis Technical Test
Author: Andersson David Sánchez Méndez · ECI
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from mangum import Mangum

from src.domain.exceptions import InvalidTransitionError, OrderNotFoundError
from src.handlers import chat_router, order_router
from src.observability.powertools import logger

app = FastAPI(
    title="Order Processing State Machine",
    description="Sainapsis Backend Technical Test — Andersson Sánchez",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(order_router.router)
app.include_router(chat_router.router)


@app.exception_handler(InvalidTransitionError)
async def handle_invalid_transition(
    request: Request, exc: InvalidTransitionError
) -> JSONResponse:
    """Return 422 for invalid state transitions."""
    logger.warning("Invalid transition", extra={"error": str(exc)})
    return JSONResponse(
        status_code=422,
        content={"error": "InvalidTransitionError", "detail": str(exc)},
    )


@app.exception_handler(OrderNotFoundError)
async def handle_order_not_found(
    request: Request, exc: OrderNotFoundError
) -> JSONResponse:
    """Return 404 when an order does not exist."""
    return JSONResponse(
        status_code=404,
        content={"error": "OrderNotFoundError", "detail": str(exc)},
    )


@app.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}


# AWS Lambda ASGI handler
handler = Mangum(app, lifespan="off")
