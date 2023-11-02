from fastapi import FastAPI, HTTPException, Depends
from .api import router as api_router

def init_app():


    app = FastAPI()
    app.include_router(api_router)

    return app

app = init_app()