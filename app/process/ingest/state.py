"""入库图状态契约及独立默认状态工厂。

流程：入口创建状态并覆盖输入；I01～I07 读取字典并返回状态增量。
产物用路径引用，避免在图中反复复制全库正文和向量；不保存客户端或密钥。
此模块不执行节点、不验证阶段转换、不生成构建 ID，也没有导入副作用。
"""

from copy import deepcopy
from typing import Literal, TypedDict, Unpack

from pydantic import JsonValue

from app.rag.schemas import ValidatedCorpus

IngestStatus = Literal[
    "created", "validated", "parsed", "split", "embedded", "written",
    "verified", "activated", "failed",
]


class IngestError(TypedDict):
    """受控错误信息；message 不得直接保存原始异常、凭据或供应商响应。"""

    node: str
    code: str
    message: str


class IngestState(TypedDict, total=False):
    """允许节点返回部分更新；完整初始状态应通过 create_ingest_state 创建。

    TypedDict 仅提供类型提示，不做运行时校验。节点不得原地修改嵌套对象。
    T05 三个索引结构暂用 JSON 对象预留，具体强类型契约留待 T05。
    """

    task_id: str | None
    build_id: str | None
    manifest_path: str | None
    # I01 输出，I02 消费。
    validated_manifest: ValidatedCorpus | None
    source_commit: str | None
    knowledge_version: str | None
    manifest_digest: str | None
    # I02 / I03 / I04 产物路径，相对项目根；None 表示尚未产生。
    parsed_artifact: str | None
    chunks_artifact: str | None
    vectors_artifact: str | None
    document_count: int
    chunk_count: int
    vector_count: int
    # I05 / I06 / I07 输出；T04 不提前实现索引业务。
    collection_name: str | None
    build_metadata: dict[str, JsonValue] | None
    validation_report: dict[str, JsonValue] | None
    previous_active_build_id: str | None
    active_index: dict[str, JsonValue] | None
    status: IngestStatus
    timings: dict[str, float]  # 各节点实际耗时，单位毫秒。
    error: IngestError | None


def create_ingest_state(**overrides: Unpack[IngestState]) -> IngestState:
    """创建新字典并按字段覆盖；覆盖值深拷贝，嵌套容器也与调用方隔离。

    CLI 后续负责提供唯一 build_id 和 manifest_path；task_id 可单独指定。
    None 表示尚未获得结果，0 表示初始计数，不代表节点已经成功。
    未知键拒绝以发现拼写错误；值及阶段前置条件由业务边界校验。
    """
    state: IngestState = {
        "task_id": None, "build_id": None, "manifest_path": None,
        "validated_manifest": None, "source_commit": None,
        "knowledge_version": None, "manifest_digest": None,
        "parsed_artifact": None, "chunks_artifact": None, "vectors_artifact": None,
        "document_count": 0, "chunk_count": 0, "vector_count": 0,
        "collection_name": None, "build_metadata": None, "validation_report": None,
        "previous_active_build_id": None, "active_index": None,
        "status": "created", "timings": {}, "error": None,
    }
    if overrides.keys() - state.keys():
        raise TypeError("unknown ingest state field")
    state.update(deepcopy(overrides))
    return state
