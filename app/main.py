"""FastAPI 入口：创建应用加载环境，启动时初始化日志。"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.shared.config.settings import load_environment
from app.shared.runtime.logger import init_logger, logger


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_logger()
    try:
        logger.debug("应用日志 DEBUG 已启用")
        logger.info("应用启动")
        yield
    finally:
        logger.info("应用停止")
        await logger.complete()
        logger.remove()


def create_app() -> FastAPI:
    load_environment()
    app = FastAPI(title=os.getenv("APP_NAME", "FastAPI RAG"), lifespan=lifespan)
    app.include_router(health_router)
    return app
