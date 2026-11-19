"""从项目 .env 与进程环境读取启动参数。"""

import os
from copy import deepcopy

import uvicorn
from uvicorn.config import LOGGING_CONFIG

from app.shared.config.settings import load_environment
from app.shared.config.runtime_config import env_bool, env_log_level, env_positive_int


if __name__ == "__main__":
    load_environment()
    log_config = deepcopy(LOGGING_CONFIG)
    if not env_bool("LOG_CONSOLE_ENABLE", True):
        for config in log_config["loggers"].values():
            config["handlers"] = []
            config["propagate"] = False
    uvicorn.run(
        "app.main:create_app", factory=True,
        host=os.getenv("APP_HOST", "127.0.0.1"),
        port=env_positive_int("APP_PORT", 8000, 65535),
        log_level=env_log_level("LOG_CONSOLE_LEVEL").lower(),
        log_config=log_config,
    )
