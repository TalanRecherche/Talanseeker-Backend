import logging
from collections.abc import Callable, Coroutine
from typing import Any

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from starlette.types import ASGIApp

from app.exceptions.handlers import db_exception_handler
from app.models import engine


class DbMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> (
            Coroutine[Any, Any, JSONResponse] | JSONResponse):
        try:
            engine.connect()
        except Exception as e:
            logging.exception(e)
            return await db_exception_handler()
        response = await call_next(request)
        return response
