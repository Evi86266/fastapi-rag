"""参考培训日志格式；.env + os.getenv 配置，仅由入口显式初始化。"""

import os
import re
import sys
from datetime import timedelta

from loguru import logger

from app.shared.config.settings import PROJECT_ROOT, load_environment
from app.shared.config.runtime_config import env_bool, env_log_level, env_positive_int

LOG_FILE_NAME = "app_{time:YYYYMMDD}.log"
LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>"
)


def init_logger():
    """读取环境并替换 sink；重复调用不叠加输出，导入模块不初始化。"""
    load_environment()
    console_enabled = env_bool("LOG_CONSOLE_ENABLE", True)
    file_enabled = env_bool("LOG_FILE_ENABLE", False)
    console_level = env_log_level("LOG_CONSOLE_LEVEL")
    file_level = env_log_level("LOG_FILE_LEVEL")
    rotation_bytes = env_positive_int("LOG_ROTATION_BYTES", 5_000_000)
    # 兼容上一版天数字段；新配置使用参考文件的 LOG_FILE_RETENTION。
    retention = os.getenv("LOG_FILE_RETENTION")
    if retention is None:
        retention_days = env_positive_int("LOG_RETENTION_DAYS", 7, 36500)
    else:
        match = re.fullmatch(r"([1-9][0-9]*) days?", retention.strip(), re.IGNORECASE)
        if not match or int(match[1]) > 36500:
            raise ValueError("LOG_FILE_RETENTION 必须为 1～36500 days，例如 7 days")
        retention_days = int(match[1])
    # 先完成校验，错误配置不破坏当前 sink。
    logger.remove()
    if console_enabled:
        logger.add(
            sys.stdout, level=console_level, format=LOG_FORMAT,
            colorize=True, enqueue=True, diagnose=False,
        )
    if file_enabled:
        logger.add(
            PROJECT_ROOT / "logs" / LOG_FILE_NAME,
            level=file_level, format=LOG_FORMAT, encoding="utf-8",
            rotation=["00:00", rotation_bytes],
            retention=timedelta(days=retention_days),
            colorize=False, enqueue=True, diagnose=False,
        )
    return logger


# 保留旧导入入口；追踪实现独立于日志初始化，避免维护两套装饰器。
from app.shared.runtime.tracing import node_log, step_log  # noqa: E402,F401
