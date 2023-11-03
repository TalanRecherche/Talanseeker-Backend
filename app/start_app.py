from fastapi import FastAPI
from .api import router as api_router

def init_app():


    app = FastAPI()
    app.include_router(api_router)

    return app

app = init_app()