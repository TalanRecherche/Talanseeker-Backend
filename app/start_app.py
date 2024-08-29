"""Used to start the FastAPI application."""

import logging

from fastapi import FastAPI

from app.exceptions.handlers import exception_handler
from app.middleware import add_middleware
from app.models import create_all_tables

from .api import router as api_router


def init_app() -> FastAPI:
    """Initialize the FastAPI application.
    Load all the routes and exception handlers.
    """
    log_file_path = "logging.conf"

    logging.config.fileConfig(log_file_path, disable_existing_loggers=False)
    logging.getLogger().setLevel(level=logging.ERROR)

    fastapi_app = FastAPI()
    fastapi_app.include_router(api_router)
    exception_handler(fastapi_app)
    add_middleware(fastapi_app)
    create_all_tables()

    return fastapi_app


app = init_app()
