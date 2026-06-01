from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from mangum import Mangum

from src.config import get_settings
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
    allow_origins=get_settings().allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(order_router.router)
app.include_router(chat_router.router)


@app.exception_handler(InvalidTransitionError)
async def handle_invalid_transition(request: Request, exc: InvalidTransitionError) -> JSONResponse:
    logger.warning("Invalid transition", extra={"error": str(exc)})
    return JSONResponse(status_code=422, content={"error": "InvalidTransitionError", "detail": str(exc)})


@app.exception_handler(OrderNotFoundError)
async def handle_order_not_found(request: Request, exc: OrderNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"error": "OrderNotFoundError", "detail": str(exc)})


@app.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    return {"status": "ok"}


handler = Mangum(app, lifespan="off")
