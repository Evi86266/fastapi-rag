"""节点与步骤追踪：负责调用计时、关联标识及失败传播。

流程：绑定显式标识或 state 标识 → 继承调用上下文 → 执行/等待函数 →
记录结束状态与耗时 → 恢复父上下文。仅记录标识与执行元数据，不记录业务输入输出。
"""

from collections.abc import Mapping
from contextlib import contextmanager
from contextvars import ContextVar
from functools import wraps
import inspect
from time import perf_counter

from loguru import logger


_ids = ContextVar("trace_ids", default=(None, None))


@contextmanager
def trace_context(*, request_id=None, build_id=None):
    """为一个调用范围绑定 ID；None 继承父值，退出（包括失败）后恢复。

    标识应由入口提供，不自动生成；使用短且不含敏感信息的标识。
    ContextVar 隔离并发 asyncio 任务；原生新线程需调用方显式传播上下文。
    """
    parent_request, parent_build = _ids.get()
    token = _ids.set((
        parent_request if request_id is None else request_id,
        parent_build if build_id is None else build_id,
    ))
    try:
        yield
    finally:
        _ids.reset(token)


def _trace(kind, name):
    """统一包装节点和步骤；普通函数和 async def 使用不同执行路径。"""
    def decorate(func):
        # 生成器返回不等于执行完成，拒绝装饰以避免制造虚假的完成记录。
        if inspect.isgeneratorfunction(func) or inspect.isasyncgenfunction(func):
            raise TypeError("追踪装饰器不支持生成器函数")
        signature = inspect.signature(func)

        @contextmanager
        def invocation(args, kwargs):
            bound = signature.bind(*args, **kwargs)
            bound.apply_defaults()
            arguments = bound.arguments
            state = arguments.get("state")
            state = state if isinstance(state, Mapping) else {}
            # 明确命名的函数参数优先，其次 state，最后继承；不扫描任意业务字典。
            request_id = arguments.get("request_id")
            build_id = arguments.get("build_id")
            if request_id is None:
                request_id = state.get("request_id")
            if build_id is None:
                build_id = state.get("build_id")
            with trace_context(request_id=request_id, build_id=build_id):
                request_id, build_id = _ids.get()
                traced = logger.bind(
                    trace_kind=kind, trace_name=name,
                    request_id=request_id, build_id=build_id,
                )
                start = perf_counter()

                def emit(event, elapsed_ms=None, error_type=None):
                    # 不记录异常消息/堆栈，避免异常文本和源码行带出凭据或业务内容。
                    traced.bind(event=event, elapsed_ms=elapsed_ms, error_type=error_type).log(
                        "ERROR" if event == "error" else "INFO",
                        "{}={} event={} request_id={} build_id={} elapsed_ms={} error_type={}",
                        kind, name, event, request_id or "-", build_id or "-",
                        "-" if elapsed_ms is None else round(elapsed_ms, 3), error_type or "-",
                    )

                emit("start")
                try:
                    yield
                except BaseException as exc:
                    # 包括 CancelledError/SystemExit；只观测，不吞异常或改变取消语义。
                    emit("error", (perf_counter() - start) * 1000, type(exc).__name__)
                    raise
                else:
                    emit("success", (perf_counter() - start) * 1000)

        if inspect.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                with invocation(args, kwargs):
                    return await func(*args, **kwargs)
            return async_wrapper

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            with invocation(args, kwargs):
                return func(*args, **kwargs)
        return sync_wrapper
    return decorate


def node_log(node_name: str):
    """装饰同步/异步节点；读取 state 中的 request_id/build_id 并传给嵌套步骤。"""
    return _trace("node", node_name)


def step_log(step_name: str):
    """装饰同步/异步步骤；默认继承节点上下文，也可通过命名参数提供 ID。"""
    return _trace("step", step_name)
