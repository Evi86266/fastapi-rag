"""存活与就绪接口：存活为常量，就绪读取生命周期管理的分项快照。

流程：/health 返回进程存活；/ready 读取缓存依赖状态并选择 200/503。
请求不加载模型、不访问数据库、不生成文本，也不修改资源状态。
"""
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from app.api.dependencies import get_providers
from app.infra.providers import Providers

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    """存活检查不代表外部服务或知识库可用。"""
    return {"status": "ok"}


@router.get("/ready")
def ready(providers: Providers | None = Depends(get_providers)) -> JSONResponse:
    """完整索引尚未接入时必须保持 503，具体缺项由 dependencies 列出。"""
    if providers is None:
        content = {"status": "not_ready", "lifecycle": "not_started", "dependencies": {}}
    else:
        content = providers.snapshot()
    return JSONResponse(status_code=200 if content["status"] == "ready" else 503, content=content)
