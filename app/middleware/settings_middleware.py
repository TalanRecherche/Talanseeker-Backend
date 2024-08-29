import logging
from collections.abc import Callable, Coroutine
from typing import Any

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from starlette.types import ASGIApp

from app.exceptions.exceptions import SettingsError
from app.exceptions.handlers import settings_exception_handler
from app.settings import settings


class SettingsMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> (
            Coroutine[Any, Any, JSONResponse] | JSONResponse):
        try:
            settings.validate()
        except SettingsError as e:
            logging.exception(e)
            return await settings_exception_handler()
        response = await call_next(request)
        return response
