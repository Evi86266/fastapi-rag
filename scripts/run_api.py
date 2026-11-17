"""使用项目配置启动本地 HTTP 服务。"""

import uvicorn

from app.shared.config.settings import get_settings


if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run("app.main:create_app", factory=True, host=settings.app_host, port=settings.app_port)
