"""os.getenv 的最小类型校验；不缓存配置、不在导入时读取 .env。"""

import os

LOG_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}


def env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    value = value.strip().lower()
    if value in {"true", "1", "yes", "on"}:
        return True
    if value in {"false", "0", "no", "off"}:
        return False
    raise ValueError(f"{name} 必须为 true/false、1/0、yes/no 或 on/off")


def env_positive_int(name: str, default: int, maximum: int | None = None) -> int:
    raw = os.getenv(name, str(default))
    try:
        value = int(raw)
    except ValueError:
        raise ValueError(f"{name} 必须为正整数") from None
    if value <= 0 or (maximum is not None and value > maximum):
        suffix = f"，且不超过 {maximum}" if maximum is not None else ""
        raise ValueError(f"{name} 必须为正整数{suffix}")
    return value


def env_log_level(name: str) -> str:
    # 分项值未设置或留空时继承 LOG_LEVEL，兼容已有本地 .env。
    value = (os.getenv(name) or os.getenv("LOG_LEVEL", "INFO")).strip().upper()
    if value not in LOG_LEVELS:
        raise ValueError(f"{name}（或 LOG_LEVEL）必须为 DEBUG/INFO/WARNING/ERROR/CRITICAL")
    return value
