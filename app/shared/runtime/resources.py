"""受限同步执行基础：把阻塞函数放到线程并限制未完成任务数。

流程：显式创建执行器 → 非阻塞争取容量 → 复制追踪上下文并提交 →
异步等待 → 真实线程结束释放容量 → 显式关闭并等待收尾。
本模块不创建全局执行器、不接入模型、不加载环境或初始化日志。
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from contextvars import copy_context
from functools import partial
import inspect
from threading import BoundedSemaphore, Lock
from typing import Callable, TypeVar

from app.shared.errors import ResourceBusyError, ResourceClosedError

T = TypeVar("T")


class BoundedExecutor:
    """单进程线程执行器；容量等于线程数，不建立无界等待队列。

    max_workers 必须由启动层根据配置显式传入。取消/超时只停止等待，
    无法杀死正在执行的线程；容量直到线程真实结束才释放。
    """

    def __init__(self, max_workers: int):
        if type(max_workers) is not int or max_workers < 1:
            raise ValueError("max_workers 必须为正整数")
        self._pool = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="rag-worker")
        self._slots = BoundedSemaphore(max_workers)
        self._lock = Lock()
        self._closed = False

    async def run(self, function: Callable[..., T], /, *args, **kwargs) -> T:
        """运行同步函数并传播结果/原始异常，线程继承提交时的 ContextVar。"""
        if inspect.iscoroutinefunction(function) or inspect.isasyncgenfunction(function):
            raise TypeError("执行器只接受同步函数")
        with self._lock:
            if self._closed:
                raise ResourceClosedError("执行器已关闭")
            if not self._slots.acquire(blocking=False):
                raise ResourceBusyError("执行容量已满")
            try:
                call = partial(function, *args, **kwargs)
                future = self._pool.submit(copy_context().run, call)
            except BaseException:
                self._slots.release()
                raise
            # 绑定底层 future，而非等待它的协程，避免取消时提前释放容量。
            future.add_done_callback(lambda _: self._slots.release())
        wrapped = asyncio.wrap_future(future)
        # 等待者取消后仍读取后台异常，避免未获取异常告警；正常 await 仍原样抛出。
        wrapped.add_done_callback(lambda done: None if done.cancelled() else done.exception())
        return await asyncio.shield(wrapped)

    def close(self) -> None:
        """拒绝新任务并同步等候在途任务；应由所属线程在生命周期末尾调用。"""
        with self._lock:
            self._closed = True
        self._pool.shutdown(wait=True)

    async def aclose(self) -> None:
        """异步生命周期收尾，不在事件循环线程中阻塞等待工作线程。"""
        with self._lock:
            self._closed = True
        await asyncio.to_thread(self._pool.shutdown, wait=True)
