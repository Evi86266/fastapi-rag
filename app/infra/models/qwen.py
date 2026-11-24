"""Qwen 的 ChatOpenAI 接入：懒建客户端 → 回调预留费用 → SDK 生成 → 原台账核销。
默认/JSON 客户端共用 HTTP 连接与费用回调；不保留手写 HTTP 生成分支。
"""
from dataclasses import dataclass
from decimal import Decimal
from threading import RLock
from urllib.parse import urlsplit

import httpx
from langchain_core.callbacks import BaseCallbackHandler
from langchain_openai import ChatOpenAI
from openai import APITimeoutError

from app.shared.config.model_config import required, url, money
from app.shared.config.runtime_config import env_positive_int
from app.shared.config.settings import PROJECT_ROOT
from app.shared.errors import ExternalError, ResourceClosedError
from app.shared.usage_store import PersistentUsage, month_now


@dataclass(frozen=True)
class Generation:
    """保留现有验证入口的返回契约；业务门面 chat() 直接返回 ChatOpenAI。"""
    text: str
    input_tokens: int
    output_tokens: int
    estimated_cost_cny: Decimal
    reservation_id: str


class _UsageCallback(BaseCallbackHandler):
    """将原来的预留/核销逻辑接到 ChatOpenAI 生命周期，覆盖 invoke/ainvoke。

    不存提示词；只按 run_id 暂存预留 ID。异常时保留未知费用，复用原持久台账。
    raise_error 确保预算失败立即中断，不能被 LangChain 当成普通回调告警忽略。
    """
    raise_error = True
    run_inline = True

    def __init__(self, owner):
        self.owner = owner
        self._pending = {}
        self._lock = RLock()

    def on_chat_model_start(self, serialized, messages, *, run_id, **kwargs):
        owner = self.owner
        if owner.client is None or owner.client.is_closed or self is not owner._usage_callback:
            raise ResourceClosedError("聊天客户端已关闭，请重新从门面获取")
        params = kwargs.get("invocation_params", {})
        model = params.get("model", params.get("model_name", owner.model))
        limits = [params[name] for name in ("max_completion_tokens", "max_tokens") if name in params]
        extra = params.get("extra_body") or {}
        if (model != owner.model
                or any(type(limit) is not int or not 0 < limit <= owner.max_output for limit in limits)
                or params.get("n", 1) != 1 or extra.get("enable_thinking", False)
                or set(extra) - {"enable_thinking"}
                or params.get("tools") or params.get("functions")):
            raise ExternalError("unsupported_generation_options", "qwen")
        if len(messages) != 1 or not messages[0]:
            raise ExternalError("invalid_input", "qwen")
        contents = [message.content for message in messages[0]]
        if any(not isinstance(text, str) for text in contents):
            raise ExternalError("invalid_input", "qwen")
        # 保留 UTF-8 字节上界与消息开销检查，适配 LangChain 的普通文本消息列表。
        if (not any(text.strip() for text in contents)
                or sum(len(text.encode("utf-8")) + 256 for text in contents) > owner.max_input):
            raise ExternalError("input_too_long", "qwen")
        key = owner.ledger.reserve(owner.maximum_cost())
        with self._lock:
            self._pending[run_id] = key

    def on_llm_end(self, response, *, run_id, **kwargs):
        with self._lock:
            key = self._pending.pop(run_id, None)
        if key is None:
            return
        owner = self.owner
        try:
            usage = (response.llm_output or {})["token_usage"]
            incoming, outgoing = usage["prompt_tokens"], usage["completion_tokens"]
            message = response.generations[0][0].message
            if (any(type(v) is not int or v < 0 for v in (incoming, outgoing))
                    or not isinstance(message.content, str) or not message.content.strip()):
                raise ValueError
        except (KeyError, IndexError, TypeError, ValueError, AttributeError):
            owner.ledger.settle(key, status="failed", actual_cost=None)
            raise ExternalError("api_failed_or_invalid_response", "qwen") from None
        cost = (incoming * owner.in_rate + outgoing * owner.out_rate) / Decimal(1000000)
        owner.ledger.settle(key, status="succeeded", actual_cost=cost,
                           input_tokens=incoming, output_tokens=outgoing)
        message.response_metadata.update(reservation_id=key, estimated_cost_cny=str(cost))
        if incoming > owner.max_input or outgoing > owner.max_output:
            raise ExternalError("provider_exceeded_token_bound", "qwen")

    def on_llm_error(self, error, *, run_id, **kwargs):
        with self._lock:
            key = self._pending.pop(run_id, None)
        if key is None:
            return
        self.owner.ledger.settle(key, status="failed", actual_cost=None)
        self.owner.authenticated = False
        code = "api_timeout" if isinstance(error, (APITimeoutError, httpx.TimeoutException)) else "api_failed_or_invalid_response"
        raise ExternalError(code, "qwen") from None


class QwenClient:
    """拥有一组 ChatOpenAI 及共享连接；模型/JSON 选项不重复创建费用台账。"""
    def __init__(self):
        self.client = None
        self.async_client = None
        self.ledger = None
        self.authenticated = False
        self._chats = {}
        self._lock = RLock()

    def start(self):
        with self._lock:
            if self.client is not None:
                return
            self.base_url = url("QWEN_BASE_URL")
            host = urlsplit(self.base_url).hostname
            if host != "dashscope.aliyuncs.com" and not host.endswith(".cn-beijing.maas.aliyuncs.com"):
                raise ExternalError("unpriced_region", "QWEN_BASE_URL")
            self.model = required("QWEN_MODEL")
            if self.model != "qwen-flash":
                raise ExternalError("unpriced_model", "QWEN_MODEL")
            self._key = required("QWEN_API_KEY")
            self.in_rate = money("QWEN_INPUT_CNY_PER_MILLION", positive=True)
            self.out_rate = money("QWEN_OUTPUT_CNY_PER_MILLION", positive=True)
            self.max_input = env_positive_int("QWEN_MAX_INPUT_TOKENS", 4096, 4096)
            self.max_output = env_positive_int("QWEN_MAX_OUTPUT_TOKENS", 128, 512)
            if required("QWEN_MAX_RETRIES") != "0":
                raise ExternalError("invalid_config", "QWEN_MAX_RETRIES")
            self.ledger = PersistentUsage(PROJECT_ROOT / "data/reports/qwen-usage.sqlite3",
                month=required("COST_MONTH"), monthly=money("MONTHLY_BUDGET_CNY", "100", True),
                opening=money("MONTH_OPENING_SPENT_CNY"), sample=money("QWEN_SAMPLE_BUDGET_CNY", "1", True))
            self.timeout = env_positive_int("QWEN_TIMEOUT_SECONDS", 30, 120)
            self.client = httpx.Client(timeout=self.timeout, follow_redirects=False, trust_env=False)
            self.async_client = httpx.AsyncClient(timeout=self.timeout, follow_redirects=False, trust_env=False)
            self._usage_callback = _UsageCallback(self)

    def chat(self, model: str | None = None, json_mode: bool = False) -> ChatOpenAI:
        """返回缓存的 ChatOpenAI；JSON 模式以 response_format 配置，计费入口一致。

        model 为空用配置默认值；未核价的模型明确拒绝。当前仍为非流式，
        disable_streaming 使 stream/astream 回退到完整回复，不宣称 token 流支持。
        """
        with self._lock:
            self.start()
            selected = self.model if model is None else model
            if selected != self.model:
                raise ExternalError("unpriced_model", "QWEN_MODEL")
            if type(json_mode) is not bool:
                raise TypeError("json_mode 必须为 bool")
            key = (selected, json_mode)
            if key not in self._chats:
                self._chats[key] = ChatOpenAI(
                    model=selected, api_key=self._key, base_url=self.base_url,
                    temperature=0, max_tokens=self.max_output, timeout=self.timeout,
                    max_retries=0, use_responses_api=False, disable_streaming=True,
                    cache=False, extra_body={"enable_thinking": False},
                    model_kwargs={"response_format": {"type": "json_object"}} if json_mode else {},
                    http_client=self.client, http_async_client=self.async_client,
                    callbacks=[self._usage_callback])
            return self._chats[key]

    def probe(self):
        if self.client is None:
            return False
        try:
            self.authenticated = any(item.id == self.model for item in self.chat().root_client.models.list())
        except Exception:
            self.authenticated = False
            raise ExternalError("authentication_or_probe_failed", "qwen") from None
        summary = self.ledger.summary()
        return (self.authenticated and summary["unresolved_calls"] == 0
                and Decimal(summary["remaining_cny"]) >= self.maximum_cost()
                and self.ledger.month == month_now())

    def maximum_cost(self):
        return (self.max_input * self.in_rate + self.max_output * self.out_rate) / Decimal(1000000)

    def generate(self, text):
        """兼容已存在的生命周期检查入口；真正生成统一走 ChatOpenAI，无第二套协议。"""
        if self.client is None:
            raise ExternalError("not_initialized", "qwen")
        if not isinstance(text, str):
            raise ExternalError("invalid_input", "qwen")
        message = self.chat().invoke(text)
        usage = message.usage_metadata
        return Generation(message.content, usage["input_tokens"], usage["output_tokens"],
                          Decimal(message.response_metadata["estimated_cost_cny"]),
                          message.response_metadata["reservation_id"])

    def usage(self):
        return self.ledger.summary()

    def close(self):
        """释放同步连接和客户端缓存；异步连接由 aclose 在所属事件循环中收尾。"""
        with self._lock:
            if self.client is not None:
                self.client.close()
                self.client = None
            self._chats.clear()

    async def aclose(self):
        """生命周期统一调用，确保 ainvoke 使用的连接也被关闭。"""
        if self.async_client is not None:
            await self.async_client.aclose()
            self.async_client = None
        self.close()
