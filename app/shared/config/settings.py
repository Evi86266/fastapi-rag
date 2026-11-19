"""只负责定位与加载项目 .env；不再定义 Settings 对象。"""

from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]


def load_environment() -> None:
    """启动时调用；进程变量优先，不依赖工作目录，不展开配置中的变量。"""
    load_dotenv(PROJECT_ROOT / ".env", override=False, interpolate=False, encoding="utf-8")
