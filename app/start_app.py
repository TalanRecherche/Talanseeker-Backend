"""Used to start the FastAPI application."""

import logging.config

from fastapi import FastAPI

from app.exceptions.handlers import exception_handler

from .api import router as api_router


def init_app() -> FastAPI:
    """Initialize the FastAPI application.
    Load all the routes and exception handlers.
    """
    log_file_path = "logging.conf"

    logging.config.fileConfig(log_file_path, disable_existing_loggers=False)

    fastapi_app = FastAPI(debug=True)
    fastapi_app.include_router(api_router)
    exception_handler(fastapi_app)

    return fastapi_app


app = init_app()
