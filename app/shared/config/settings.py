"""集中加载应用配置，进程环境变量优先于项目 .env。"""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, HttpUrl, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=PROJECT_ROOT / ".env", env_file_encoding="utf-8", env_ignore_empty=True)

    app_name: str = "FastAPI RAG"
    app_host: str = "127.0.0.1"
    app_port: int = Field(default=8000, ge=1, le=65535)
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    log_file_enable: bool = False

    milvus_url: HttpUrl = HttpUrl("http://192.168.10.150:19530")
    milvus_collection_prefix: str = "fastapi_doc_chunks"
    bge_m3_path: Path = Path("D:/S/zhangguizhiku/BAAI/bge-m3")
    bge_device: Literal["cpu"] = "cpu"
    bge_fp16: bool = False
    bge_reranker_large: Path = Path("D:/S/zhangguizhiku/BAAI/bge-reranker-large")
    bge_reranker_device: Literal["cpu"] = "cpu"
    bge_reranker_fp16: bool = False
    rerank_enabled: bool = False

    qwen_model: str = "qwen-flash"
    qwen_base_url: str = ""
    qwen_api_key: SecretStr | None = None
    history_enabled: bool = False
    corpus_archive_enabled: bool = False


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
