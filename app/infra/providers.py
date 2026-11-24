"""外部依赖生命周期与就绪状态；统一拥有模型、存储和生成客户端。

流程：显式创建 Providers → 后台串行启动已注册能力 → 缓存分项状态 → 定期只读探测
→ 停止接收任务 → 等待真实线程完成 → 逐个释放实例。接口只读取快照，不触发外部调用。
SDK 仅在后台 start 时导入；请求读取缓存状态，不触发生成调用。
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Protocol, TYPE_CHECKING
from threading import RLock

if TYPE_CHECKING:
    from langchain_openai import ChatOpenAI

from app.shared.config.runtime_config import env_bool
from app.shared.runtime.resources import BoundedExecutor
from app.shared.errors import AppError, ExternalError, ResourceBusyError, ResourceClosedError


class ManagedDependency(Protocol):
    """同步生命周期契约，后续适配器通过注册包装接入。

    start 初始化，probe 只做有超时的免费只读检查（不得生成文本/写数据库），
    close 幂等释放；都由受限线程调用。费用、SDK 异常转换留在各自 infra 适配器。
    """
    def start(self) -> None: ...
    def probe(self) -> bool: ...
    def close(self) -> None: ...


@dataclass(frozen=True)
class DependencySpec:
    """依赖声明；factory=None 表示尚未接入，绝不能据此标为 ready。"""
    name: str
    required: bool
    enabled: bool = True
    factory: Callable[[], ManagedDependency] | None = None
    pending_reason: str = "adapter_not_implemented"


@dataclass(frozen=True)
class DependencyStatus:
    """可公开快照仅保存受控状态，不保存配置值、客户端或异常正文。"""
    required: bool
    state: str
    reason: str
    checked_at: str | None = None

    def as_dict(self) -> dict:
        return {"required": self.required, "state": self.state,
                "reason": self.reason, "checked_at": self.checked_at}


def default_dependencies() -> tuple[DependencySpec, ...]:
    """注册真实适配器；EXTERNAL_ENABLED=false 用于隔离测试或仅健康启动。

    可选功能关闭不阻塞就绪；用户显式开启时，该功能成为本次运行的必需依赖。
    活动索引独立保留 T05 门槛，不以数据库在线代替有效知识库。
    """
    from app.infra.storage.milvus import MilvusStore
    enabled = env_bool("EXTERNAL_ENABLED", True)
    rerank = env_bool("RERANK_ENABLED", False)
    history = env_bool("HISTORY_ENABLED", False)
    archive = env_bool("CORPUS_ARCHIVE_ENABLED", False)
    return (
        DependencySpec("embedding", True, factory=(lambda: llm_provider._adapter("embedding")) if enabled else None, pending_reason="external_disabled"),
        DependencySpec("milvus", True, factory=MilvusStore if enabled else None, pending_reason="external_disabled"),
        DependencySpec("qwen", True, factory=(lambda: llm_provider._adapter("qwen")) if enabled else None, pending_reason="external_disabled"),
        DependencySpec("active_index", True, pending_reason="pending_t05_active_index"),
        DependencySpec("reranker", rerank, enabled=rerank, factory=(lambda: llm_provider._adapter("reranker")) if enabled else None, pending_reason="external_disabled"),
        DependencySpec("history", history, enabled=history, pending_reason="feature_not_implemented"),
        DependencySpec("archive", archive, enabled=archive, pending_reason="feature_not_implemented"),
    )


class Providers:
    """单应用生命周期管理资源与单线程容量；默认模型复用 llm_provider 的实例。

    仅在事件循环中更新状态。工作线程可写实例注册表，关闭前先等线程完成，
    避免取消等待时遗失刚创建的模型或连接。探测失败可在下一轮恢复。
    """
    def __init__(self, specs: tuple[DependencySpec, ...] | None = None, *, probe_interval: float = 30):
        if not isinstance(probe_interval, (int, float)) or not 0 < probe_interval <= 3600:
            raise ValueError("probe_interval 必须在 0～3600 秒内")
        self.specs = default_dependencies() if specs is None else specs
        if not self.specs or len({s.name for s in self.specs}) != len(self.specs):
            raise ValueError("依赖声明必须非空且名称唯一")
        if any(s.required and not s.enabled for s in self.specs):
            raise ValueError("必需依赖不能关闭")
        self._states = {s.name: DependencyStatus(s.required, "not_started", "lifecycle_not_started") for s in self.specs}
        self._instances: dict[str, ManagedDependency] = {}
        self._executor = BoundedExecutor(1)
        self._probe_interval = probe_interval
        self._task: asyncio.Task | None = None
        self._initialized = asyncio.Event()
        self._close_lock = asyncio.Lock()
        self._phase = "created"
        self.shutdown_errors: list[str] = []

    def _set(self, spec: DependencySpec, state: str, reason: str, *, checked: bool = False):
        timestamp = datetime.now(timezone.utc).isoformat() if checked else None
        self._states[spec.name] = DependencyStatus(spec.required, state, reason, timestamp)

    def start(self) -> None:
        """启动后台初始化，立即让出事件循环；重复启动拒绝。"""
        if self._phase != "created":
            raise RuntimeError("Providers 只能启动一次")
        self._phase = "running"
        self._task = asyncio.create_task(self._run(), name="external-dependency-lifecycle")

    def _open(self, spec: DependencySpec) -> bool:
        # 实例先登记再 start；部分初始化失败或等待者取消后仍可释放该实例。
        instance = spec.factory()
        self._instances[spec.name] = instance
        instance.start()
        return instance.probe() is True

    async def _run(self):
        try:
            for spec in self.specs:
                if not spec.enabled:
                    self._set(spec, "disabled", "feature_disabled")
                elif spec.factory is None:
                    self._set(spec, "pending", spec.pending_reason)
                else:
                    self._set(spec, "starting", "initializing")
                    try:
                        healthy = await self._executor.run(self._open, spec)
                        self._set(spec, "ready" if healthy else "unavailable", "probe_ok" if healthy else "probe_failed", checked=True)
                    except AppError as exc:
                        self._set(spec, "error", exc.code, checked=True)
                    except Exception:
                        # 不返回异常正文/参数/堆栈，可能包含供应商密钥或带认证的 URL。
                        self._set(spec, "error", "initialization_failed", checked=True)
            self._initialized.set()
            while True:
                await asyncio.sleep(self._probe_interval)
                await self.refresh()
        finally:
            self._initialized.set()
            if self._phase == "running":
                self._phase = "failed"

    async def wait_initialized(self) -> None:
        """供 CLI 和测试等待第一轮检查；HTTP 健康接口不等待模型初始化。"""
        if self._phase == "created":
            raise RuntimeError("Providers 尚未启动")
        await self._initialized.wait()

    async def refresh(self) -> None:
        """串行刷新已成功初始化的能力；初始化失败需重启，防止重复部分加载。"""
        if self._phase != "running":
            return
        for spec in self.specs:
            current = self._states[spec.name]
            if spec.name not in self._instances or current.state in {"starting", "error"}:
                continue
            try:
                healthy = await self._executor.run(self._instances[spec.name].probe)
                self._set(spec, "ready" if healthy else "unavailable", "probe_ok" if healthy else "probe_failed", checked=True)
            except ResourceBusyError:
                # 正在推理时跳过本轮探测，不能把本地容量占用误报为外部服务故障。
                continue
            except AppError as exc:
                self._set(spec, "unavailable", exc.code, checked=True)
            except Exception:
                self._set(spec, "unavailable", "probe_failed", checked=True)

    async def call(self, name: str, operation: str, *args):
        """所有外部操作复用已启动实例和同一个受限执行器；满容量立即拒绝。"""
        allowed = {"embedding": {"encode_queries", "encode_documents"}, "reranker": {"score"},
                   "milvus": {"server_version"}, "qwen": {"generate", "usage"}}
        if self._phase != "running":
            raise ResourceClosedError("外部能力未运行")
        if operation not in allowed.get(name, set()):
            raise ExternalError("invalid_operation", name)
        if name not in self._instances or self._states[name].state != "ready":
            raise ExternalError("dependency_not_ready", name)
        try:
            return await self._executor.run(getattr(self._instances[name], operation), *args)
        except ResourceBusyError:
            raise
        except ExternalError:
            # 输入错误不破坏已加载模型；探测下一轮刷新服务状态。
            raise

    def snapshot(self) -> dict:
        """便宜且无副作用的 HTTP 快照；仅当所有必需依赖实际 ready 才就绪。"""
        ready = self._phase == "running" and all(not s.required or s.state == "ready" for s in self._states.values())
        return {"status": "ready" if ready else "not_ready", "lifecycle": self._phase,
                "dependencies": {name: state.as_dict() for name, state in self._states.items()}}

    async def aclose(self) -> None:
        """先等待在途线程，再逆序关闭；单个释放失败不跳过其他资源。"""
        async with self._close_lock:
            if self._phase == "closed":
                return
            self._phase = "closing"
            if self._task is not None:
                self._task.cancel()
                try:
                    await self._task
                except asyncio.CancelledError:
                    pass
                except Exception:
                    self.shutdown_errors.append("lifecycle_task")
            await self._executor.aclose()
            for name, instance in reversed(list(self._instances.items())):
                try:
                    await _close_dependency(instance)
                except Exception:
                    self.shutdown_errors.append(name)
            self._instances.clear()
            self._phase = "closed"


async def _close_dependency(instance) -> None:
    """同一收尾入口兼容同步模型及 ChatOpenAI 的异步连接，不遗漏 ainvoke 资源。"""
    close_async = getattr(instance, "aclose", None)
    if close_async is not None:
        await close_async()
    else:
        await asyncio.to_thread(instance.close)


class LLMProvider:
    """模型统一门面：懒建适配器 → 复用模型/聊天客户端 → 转发已有编码逻辑。

    单例在导入时只创建容器，不读环境、不加载模型、不请求网络。
    默认应用生命周期与同步门面共用适配器，业务无需再绑定 Providers。
    同步编码应在同步业务或受限线程中执行；异步聊天使用 chat().ainvoke()。
    """

    def __init__(self):
        self._adapters: dict[str, ManagedDependency] = {}
        self._lock = RLock()

    def _adapter(self, name: str):
        """单进程只构造一份对应适配器，供门面和应用启动层共用。"""
        with self._lock:
            if name not in self._adapters:
                from app.infra.models.embedding import BgeEmbedding
                from app.infra.models.reranker import BgeReranker
                from app.infra.models.qwen import QwenClient
                factories = {"embedding": BgeEmbedding, "reranker": BgeReranker, "qwen": QwenClient}
                self._adapters[name] = factories[name]()
            return self._adapters[name]

    def chat(self, model: str | None = None, json_mode: bool = False) -> ChatOpenAI:
        """获取可 invoke/ainvoke 的 ChatOpenAI；model 为空用配置默认值。

        json_mode=True 配置 JSON 对象输出；费用保护由同一适配器回调执行。
        当前保留非流式边界，未核价模型由底层明确拒绝。
        """
        return self._adapter("qwen").chat(model=model, json_mode=json_mode)

    def embedding_model(self) -> Any:
        """获取复用的本地 BGE-M3 实例，首次访问时由原适配器加载。"""
        return self._adapter("embedding").get_model()

    def reranker_model(self) -> Any:
        """获取复用的本地重排模型；显式调用表示主动请求加载该可选能力。"""
        return self._adapter("reranker").get_model()

    def embed_documents(self, texts: list[str]) -> dict:
        """生成文档向量字典：dense_vecs 与 lexical_weights 按输入顺序对应。

        复用原适配器的长度校验、编码和结果检查，只将 EncodedText 转成统一字典。
        """
        adapter = self._adapter("embedding")
        adapter.get_model()
        encoded = adapter.encode_documents(texts)
        return {"dense_vecs": [item.dense for item in encoded],
                "lexical_weights": [item.sparse for item in encoded]}

    async def aclose(self) -> None:
        """独立脚本的显式收尾；应用内由原 Providers 生命周期关闭同一组实例。"""
        for adapter in reversed(list(self._adapters.values())):
            await _close_dependency(adapter)


llm_provider = LLMProvider()
