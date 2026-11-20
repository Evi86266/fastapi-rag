"""可选 CPU 重排：离线加载 → 成对 token 长度校验 → 有限分数 → 释放。
仅提供模型能力，不实现业务候选排序；通过 Providers 串行执行。
"""
import gc,math
from app.infra.models.embedding import offline_runtime
from app.shared.config.model_config import model_path
from app.shared.config.runtime_config import env_positive_int
from app.shared.errors import ExternalError


class BgeReranker:
    """关闭重排时不创建实例；资源由生命周期统一释放。"""
    def __init__(self): self.model=None
    def start(self):
        if self.model is not None: return
        path=model_path("BGE_RERANKER_LARGE","BGE_RERANKER_DEVICE","BGE_RERANKER_FP16")
        offline_runtime()
        try:
            import torch
            from FlagEmbedding import FlagReranker
            torch.set_num_threads(env_positive_int("MODEL_CPU_THREADS",2,16))
            self.model=FlagReranker(str(path),devices="cpu",use_fp16=False,local_files_only=True)
        except ImportError: raise ExternalError("sdk_missing","reranker") from None
        except Exception: raise ExternalError("model_load_failed","reranker") from None
    def probe(self): return self.model is not None
    def score(self,pairs):
        """不静默截断问题/证据；默认最大 512 token，批量固定为 1。"""
        if not self.probe(): raise ExternalError("not_loaded","reranker")
        if not isinstance(pairs,list) or not pairs or len(pairs)>16 or any(not isinstance(p,(tuple,list)) or len(p)!=2 or any(not isinstance(t,str) or not t.strip() or len(t)>32768 for t in p) for p in pairs): raise ExternalError("invalid_input","reranker")
        limit=env_positive_int("RERANK_MAX_LENGTH",512,512)
        try:
            tokens=self.model.tokenizer([p[0] for p in pairs],[p[1] for p in pairs],truncation=False)
            if any(len(t)>limit for t in tokens["input_ids"]): raise ExternalError("input_too_long","reranker")
            out=self.model.compute_score(pairs,batch_size=1,max_length=limit,normalize=True)
            if isinstance(out,(float,int)): out=[out]
            result=[float(v) for v in out]
            if len(result)!=len(pairs) or not all(math.isfinite(v) for v in result): raise ValueError
            return result
        except ExternalError: raise
        except Exception: raise ExternalError("model_inference_failed","reranker") from None
    def close(self):
        self.model=None
        gc.collect()
