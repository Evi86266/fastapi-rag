"""Milvus 2.4 只读接入：专用 alias 连接 → 实际版本 RPC → 关闭自身连接。
不创建/修改集合，不执行入库或业务查询；schema 与活动索引在 T05 实现。
"""
import os,re
from uuid import uuid4
from app.shared.config.model_config import url,required
from app.shared.config.runtime_config import env_positive_int
from app.shared.errors import ExternalError


class MilvusStore:
    def __init__(self):
        self.alias="fastapi_rag_"+uuid4().hex
        self.connections=None
        self.utility=None
        self.version=None
    def start(self):
        endpoint=url("MILVUS_URL")
        prefix=required("MILVUS_COLLECTION_PREFIX")
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{0,63}",prefix): raise ExternalError("invalid_config","MILVUS_COLLECTION_PREFIX")
        self.timeout=env_positive_int("MILVUS_TIMEOUT_SECONDS",5,60)
        try:
            from pymilvus import connections,utility
            self.connections,self.utility=connections,utility
            connections.connect(alias=self.alias,uri=endpoint,token=os.getenv("MILVUS_TOKEN",""),timeout=self.timeout)
        except ImportError: raise ExternalError("sdk_missing","milvus") from None
        except Exception: raise ExternalError("connection_failed","milvus") from None
    def probe(self):
        if self.utility is None: return False
        try: self.version=self.utility.get_server_version(using=self.alias,timeout=self.timeout)
        except Exception: raise ExternalError("connection_failed","milvus") from None
        if not self.version.lstrip("v").startswith("2.4."): raise ExternalError("unsupported_server_version","milvus")
        return True
    def server_version(self):
        self.probe()
        return self.version
    def close(self):
        if self.connections is not None:
            try: self.connections.disconnect(self.alias)
            finally: self.connections=self.utility=None
