"""FastAPI 入口：显式配置、日志和外部能力生命周期。

流程：创建应用读取环境 → lifespan 初始化日志和 Providers → 后台准备依赖
→ HTTP 读取状态 → 关闭资源并等待日志落盘。实际模型/数据库注册待用户确认。
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.routes.health import router as health_router
from app.infra.providers import Providers
from app.shared.config.settings import load_environment
from app.shared.runtime.logger import init_logger, logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """资源所属应用负责关闭，初始化和关闭异常都不能跳过日志收尾。"""
    init_logger()
    providers = None
    try:
        providers = app.state.provider_factory()
        app.state.providers = providers
        providers.start()
        logger.debug("应用日志 DEBUG 已启用")
        logger.info("应用启动")
        yield
    finally:
        try:
            if providers is not None:
                await providers.aclose()
                if providers.shutdown_errors:
                    logger.error("外部资源释放失败数量={}", len(providers.shutdown_errors))
        finally:
            logger.info("应用停止")
            await logger.complete()
            logger.remove()


def create_app(*, provider_factory=Providers) -> FastAPI:
    """测试可注入隔离资源；生产入口始终使用本项目的默认依赖声明。"""
    load_environment()
    app = FastAPI(title=os.getenv("APP_NAME", "FastAPI RAG"), lifespan=lifespan)
    app.state.provider_factory = provider_factory
    app.include_router(health_router)
    return app
