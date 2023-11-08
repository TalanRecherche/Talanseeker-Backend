from fastapi import FastAPI
from .api import router as api_router
import logging

logging.basicConfig(
    format="%(levelname) -10s %(asctime)s %(module)s:%(lineno)s %(funcName)s %(message)s",
    level=logging.INFO
)


def init_app():


    app = FastAPI()
    app.include_router(api_router)

    return app

app = init_app()