"""BGE-M3 适配：本地离线加载 → 长度检查 → 稠密/稀疏编码 → 普通结构。
同步推理应在受限线程中执行；门面与生命周期复用同一实例，不联网、不复制模型。
"""
import os, math, gc
from dataclasses import dataclass
from app.shared.config.settings import PROJECT_ROOT
from app.shared.config.model_config import model_path
from app.shared.config.runtime_config import env_positive_int
from app.shared.errors import ExternalError
from threading import RLock


@dataclass(frozen=True)
class EncodedText:
    """项目向量结构，不向业务层暴露 NumPy 或模型 SDK 对象。"""
    dense: list[float]
    sparse: dict[int,float]


def offline_runtime():
    """SDK 导入前禁止 Hub 下载；所有可配置缓存固定到 D 盘项目。"""
    os.environ.update(HF_HUB_OFFLINE="1",TRANSFORMERS_OFFLINE="1",HF_HOME=str(PROJECT_ROOT/".cache/huggingface"),TORCH_HOME=str(PROJECT_ROOT/".cache/torch"))


class BgeEmbedding:
    """单实例编码器；锁保护门面与生命周期对加载、编码和释放的并发访问。"""
    def __init__(self):
        self.model=None
        self._lock=RLock()

    def start(self):
        """幂等加载，强制 CPU/float32 和本地文件；失败不透传 SDK 原文。"""
        with self._lock:
            if self.model is not None: return
            path=model_path("BGE_M3_PATH","BGE_DEVICE","BGE_FP16")
            if not all((path/f).is_file() for f in ("sparse_linear.pt","colbert_linear.pt")): raise ExternalError("model_files_missing","embedding")
            offline_runtime()
            try:
                import torch
                from FlagEmbedding import BGEM3FlagModel
                torch.set_num_threads(env_positive_int("MODEL_CPU_THREADS",2,16))
                self.model=BGEM3FlagModel(str(path),devices="cpu",use_fp16=False,local_files_only=True)
            except ImportError: raise ExternalError("sdk_missing","embedding") from None
            except Exception: raise ExternalError("model_load_failed","embedding") from None

    def probe(self): return self.model is not None

    def _encode(self,texts):
        with self._lock:
            if not self.probe(): raise ExternalError("not_loaded","embedding")
            if not isinstance(texts,list) or not texts or len(texts)>16 or any(not isinstance(t,str) or not t.strip() or len(t)>32768 for t in texts): raise ExternalError("invalid_input","embedding")
            limit=env_positive_int("BGE_MAX_LENGTH",512,8192)
            try:
                # 不能依靠 SDK 截断代码片段；超长内容交由 T04 切块。
                if any(len(x)>limit for x in self.model.tokenizer(texts,truncation=False)["input_ids"]): raise ExternalError("input_too_long","embedding")
                out=self.model.encode(texts,batch_size=1,max_length=limit,return_dense=True,return_sparse=True,return_colbert_vecs=False)
                if len(out["dense_vecs"])!=len(texts) or len(out["lexical_weights"])!=len(texts): raise ValueError
                result=[]
                for dense,sparse in zip(out["dense_vecs"],out["lexical_weights"]):
                    d=[float(v) for v in dense]; s={int(k):float(v) for k,v in sparse.items()}
                    if len(d)!=1024 or not all(math.isfinite(v) for v in d) or not any(d) or any(k<0 or not math.isfinite(v) or v<=0 for k,v in s.items()): raise ValueError
                    result.append(EncodedText(d,s))
                return result
            except ExternalError: raise
            except Exception: raise ExternalError("model_inference_failed","embedding") from None

    def encode_queries(self,texts):
        """BGE-M3 查询与文档使用相同归一化参数，不添加查询指令。"""
        return self._encode(texts)
    def encode_documents(self,texts): return self._encode(texts)
    def close(self):
        with self._lock:
            self.model=None
            gc.collect()

    def get_model(self):
        """复用本适配器的已加载模型；首次获取才加载，不创建第二份权重。"""
        with self._lock:
            self.start()
            return self.model
