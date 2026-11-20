"""按需校验外部配置：读取环境 → 校验类型/路径 → 返回普通值。
不定义 Settings 对象，不在导入时加载环境，错误只包含字段名。
"""
import os
from pathlib import Path
from decimal import Decimal, InvalidOperation
from urllib.parse import urlsplit
from app.shared.config.runtime_config import env_bool
from app.shared.errors import ExternalError


def required(name):
    value=os.getenv(name, "").strip()
    if not value: raise ExternalError("missing_config", name)
    return value


def url(name):
    value=required(name)
    try:
        u=urlsplit(value)
        if not u.hostname or u.scheme not in {"http","https"} or u.username or u.password or u.query or u.fragment or u.port==0: raise ValueError
        if name=="QWEN_BASE_URL" and (u.scheme!="https" or u.path.rstrip("/")!="/compatible-mode/v1"): raise ValueError
    except ValueError: raise ExternalError("invalid_config",name) from None
    return value.rstrip("/")


def money(name, maximum=None, positive=False):
    try:
        v=Decimal(required(name))
        if not v.is_finite() or v<0 or (positive and v==0) or (maximum is not None and v>Decimal(maximum)): raise ValueError
        return v
    except (ValueError,InvalidOperation): raise ExternalError("invalid_config",name) from None


def model_path(field,device,fp16):
    path=Path(required(field))
    if not path.is_absolute() or not path.is_dir(): raise ExternalError("model_path_missing",field)
    if os.getenv(device,"cpu")!="cpu" or env_bool(fp16,False): raise ExternalError("invalid_config",device)
    for f in ("config.json","tokenizer.json","tokenizer_config.json"):
        if not (path/f).is_file(): raise ExternalError("model_files_missing",field)
    if not any((path/f).is_file() for f in ("model.safetensors","pytorch_model.bin")): raise ExternalError("model_files_missing",field)
    return path
