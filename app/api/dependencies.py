"""HTTP 依赖入口：从应用生命周期获取资源拥有者。

流程：读取 app.state → 返回既有 Providers；绝不在请求内创建模型或数据库连接。
应用未完成生命周期初始化时返回 None，由就绪路由明确报告未启动。
"""
from fastapi import Request
from app.infra.providers import Providers


def get_providers(request: Request) -> Providers | None:
    """只读取当前应用的对象，避免模块全局单例在测试或多应用间串用。"""
    return getattr(request.app.state, "providers", None)
