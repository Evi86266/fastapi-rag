"""FastAPI 应用入口。"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.shared.config.settings import get_settings
from app.shared.runtime.logger import configure_logging


@asynccontextmanager
async def lifespan(_app: FastAPI):
    configure_logging(get_settings())
    yield


def create_app() -> FastAPI:
    app = FastAPI(title=get_settings().app_name, lifespan=lifespan)
    app.include_router(health_router)
    return app
