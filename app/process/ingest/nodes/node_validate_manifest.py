"""I01 节点：读取清单路径、调用唯一业务服务、返回独立状态增量。

失败由追踪器记录并向入口抛出，不修改输入状态，不返回伪成功结果。
入库图的失败状态落地和路由在后续图任务中接入。
"""

from pathlib import Path
from time import perf_counter

from app.process.ingest.state import IngestState
from app.rag.ingest.manifest_service import validate_manifest
from app.shared.config.settings import PROJECT_ROOT
from app.shared.runtime.tracing import node_log


@node_log("validate_manifest")
def node_validate_manifest(state: IngestState, *, project_root: Path = PROJECT_ROOT) -> IngestState:
    """返回已校验来源、版本、文档数和毫秒耗时；不原地更新 timings。"""
    started = perf_counter()
    corpus = validate_manifest(state.get("manifest_path"), project_root=project_root)
    return {
        "validated_manifest": corpus,
        "manifest_digest": corpus.manifest_digest,
        "source_commit": corpus.source_commit,
        "knowledge_version": corpus.knowledge_version,
        "document_count": sum(entry.kind == "document" for entry in corpus.files),
        "status": "validated", "error": None,
        "timings": {**state.get("timings", {}), "validate_manifest": (perf_counter() - started) * 1000},
    }
