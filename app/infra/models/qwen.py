"""Qwen HTTP 适配：显式初始化 → 免费模型列表探测 → 预算预留 → 单次生成 → 持久核销。
只支持当前已核价的北京 qwen-flash、小输入、非思考模式；不实现业务提示词或问答。
"""
from dataclasses import dataclass
from decimal import Decimal
from urllib.parse import urlsplit
import httpx
from app.shared.config.model_config import required,url,money
from app.shared.config.runtime_config import env_positive_int
from app.shared.config.settings import PROJECT_ROOT
from app.shared.errors import ExternalError,UsageStateError
from app.shared.usage_store import PersistentUsage,month_now


@dataclass(frozen=True)
class Generation:
    text: str
    input_tokens: int
    output_tokens: int
    estimated_cost_cny: Decimal
    reservation_id: str


class QwenClient:
    """HTTPX 无隐式重试，客户端关闭归 Providers；费用按标准价保守估算待账单对账。"""
    def __init__(self): self.client=None;self.ledger=None;self.authenticated=False
    def start(self):
        if self.client is not None: return
        self.base_url=url("QWEN_BASE_URL")
        host=urlsplit(self.base_url).hostname
        if host!="dashscope.aliyuncs.com" and not host.endswith(".cn-beijing.maas.aliyuncs.com"): raise ExternalError("unpriced_region","QWEN_BASE_URL")
        self.model=required("QWEN_MODEL")
        if self.model!="qwen-flash": raise ExternalError("unpriced_model","QWEN_MODEL")
        key=required("QWEN_API_KEY")
        self.in_rate=money("QWEN_INPUT_CNY_PER_MILLION",positive=True)
        self.out_rate=money("QWEN_OUTPUT_CNY_PER_MILLION",positive=True)
        # 单价来自已核对的部署配置；更换计价必须先核对供应商价格及预算。
        self.max_input=env_positive_int("QWEN_MAX_INPUT_TOKENS",4096,4096)
        self.max_output=env_positive_int("QWEN_MAX_OUTPUT_TOKENS",128,512)
        if required("QWEN_MAX_RETRIES")!="0": raise ExternalError("invalid_config","QWEN_MAX_RETRIES")
        self.ledger=PersistentUsage(PROJECT_ROOT/"data/reports/qwen-usage.sqlite3",month=required("COST_MONTH"),monthly=money("MONTHLY_BUDGET_CNY","100",True),opening=money("MONTH_OPENING_SPENT_CNY"),sample=money("QWEN_SAMPLE_BUDGET_CNY","1",True))
        self.client=httpx.Client(timeout=env_positive_int("QWEN_TIMEOUT_SECONDS",30,120),follow_redirects=False,trust_env=False,headers={"Authorization":"Bearer "+key})

    def probe(self):
        """只调用免费模型列表；不在健康接口或启动阶段发起文本生成。"""
        if self.client is None: return False
        try:
            r=self.client.get(self.base_url+"/models");r.raise_for_status()
            self.authenticated=any(x.get("id")==self.model for x in r.json()["data"])
        except Exception:
            self.authenticated=False
            raise ExternalError("authentication_or_probe_failed","qwen") from None
        s=self.ledger.summary()
        return self.authenticated and s["unresolved_calls"]==0 and Decimal(s["remaining_cny"])>=self.maximum_cost() and self.ledger.month==month_now()

    def maximum_cost(self): return (self.max_input*self.in_rate+self.max_output*self.out_rate)/Decimal(1000000)

    def generate(self,text):
        """仅接收一条短文本；按 UTF-8 字节上界加消息开销限制输入，再全额预留。
        返回的金额为标准单价估算，未计优惠/缓存折扣；失败用量未知保留预留。
        """
        if self.client is None: raise ExternalError("not_initialized","qwen")
        if not isinstance(text,str) or not text.strip() or len(text.encode("utf-8"))+256>self.max_input: raise ExternalError("input_too_long","qwen")
        key=self.ledger.reserve(self.maximum_cost())
        try:
            r=self.client.post(self.base_url+"/chat/completions",json={"model":self.model,"messages":[{"role":"user","content":text}],"max_tokens":self.max_output,"temperature":0,"stream":False,"enable_thinking":False})
            r.raise_for_status();data=r.json()
            a,b=data["usage"]["prompt_tokens"],data["usage"]["completion_tokens"]
            if any(type(v) is not int or v<0 for v in (a,b)): raise ValueError
            content=data["choices"][0]["message"]["content"]
            if not isinstance(content,str) or not content.strip(): raise ValueError
        except Exception as exc:
            self.ledger.settle(key,status="failed",actual_cost=None)
            self.authenticated=False
            raise ExternalError("api_timeout" if isinstance(exc,httpx.TimeoutException) else "api_failed_or_invalid_response","qwen") from None
        cost=(a*self.in_rate+b*self.out_rate)/Decimal(1000000)
        self.ledger.settle(key,status="succeeded",actual_cost=cost,input_tokens=a,output_tokens=b)
        if a>self.max_input or b>self.max_output: raise ExternalError("provider_exceeded_token_bound","qwen")
        return Generation(content,a,b,cost,key)

    def usage(self): return self.ledger.summary()
    def close(self):
        if self.client is not None: self.client.close();self.client=None
