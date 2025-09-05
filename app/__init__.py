from fastapi import FastAPI
from .api import users
from .config import settings


def create_app() -> FastAPI:
    app = FastAPI()

    # Include API routers
    app.include_router(users.router, prefix="/users", tags=["users"])

    return app


app = create_app()
