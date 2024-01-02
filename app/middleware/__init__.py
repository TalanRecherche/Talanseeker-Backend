from fastapi import FastAPI

from app.middleware.db_middleware import DbMiddleware
from app.middleware.logging_middleware import LoggingMiddleware


def add_middleware(app: FastAPI) -> None:
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(DbMiddleware)
