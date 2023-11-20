import logging

from fastapi import FastAPI

from app.exceptions.handlers import exception_handler
from .api import router as api_router

logging.basicConfig(
    format="%(levelname) -10s %(asctime)s %(module)s:%(lineno)s                                                          "
    "%(funcName)s %(message)s",
    level=logging.INFO,
)


def init_app():
    fastapi_app = FastAPI()
    fastapi_app.include_router(api_router)
    exception_handler(fastapi_app)

    return fastapi_app


app = init_app()
