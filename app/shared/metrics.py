"""单进程内存用量台账：原子预留、核销和未知费用对账。

流程：创建显式预算 → 每次尝试独立 reserve → settle 记录成功或失败 →
未知用量继续占用预留 → reconcile 后释放差额。无网络、定价或自动重试。
不持久化、不自动按月清零；重启前须由后续接入层完成账单对账与恢复。
"""

from dataclasses import dataclass, replace
from decimal import Decimal
from threading import Lock
from uuid import uuid4

from app.shared.errors import BudgetExceededError, UsageStateError


def _money(value: Decimal) -> Decimal:
    """仅接收有限非负 Decimal，避免浮点舍入及 NaN 绕过预算比较。"""
    if not isinstance(value, Decimal) or not value.is_finite() or value < 0:
        raise ValueError("金额必须是有限非负 Decimal")
    return value


@dataclass(frozen=True)
class UsageRecord:
    """不可变调用快照；None 表示未知，0 表示已确认没有用量。"""

    reservation_id: str
    reserved_cost: Decimal
    status: str = "pending"
    actual_cost: Decimal | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None


class UsageLedger:
    """以人民币记账；预算及已知历史支出由调用方显式注入，不硬编码部署额度。"""

    def __init__(self, limit: Decimal, *, opening_spent: Decimal = Decimal("0")):
        self._limit = _money(limit)
        self._opening_spent = _money(opening_spent)
        self._records: dict[str, UsageRecord] = {}
        self._lock = Lock()

    def _committed(self) -> Decimal:
        """锁内统计已花费金额及未决预留；实际超支也如实计入。"""
        return self._opening_spent + sum(
            (r.actual_cost if r.actual_cost is not None else r.reserved_cost
             for r in self._records.values()), Decimal("0")
        )

    @property
    def remaining(self) -> Decimal:
        """剩余额度可能为负，表示事后确认的实际费用超过预算。"""
        with self._lock:
            return self._limit - self._committed()

    def reserve(self, estimated_max_cost: Decimal) -> str:
        """每次调用/重试先预留最大费用；并发预留在同一把锁内完成。"""
        amount = _money(estimated_max_cost)
        with self._lock:
            if amount > self._limit - self._committed():
                raise BudgetExceededError("剩余预算不足，拒绝新调用")
            key = uuid4().hex
            self._records[key] = UsageRecord(key, amount)
            return key

    def get(self, reservation_id: str) -> UsageRecord:
        """返回不可变快照，防止外部绕过核销修改账目。"""
        with self._lock:
            return self._get(reservation_id)

    def _get(self, key: str) -> UsageRecord:
        if key not in self._records:
            raise UsageStateError("预留记录不存在")
        return self._records[key]

    def settle(self, reservation_id: str, *, status: str,
               actual_cost: Decimal | None,
               input_tokens: int | None = None,
               output_tokens: int | None = None) -> UsageRecord:
        """成功/失败都可有费用；未知费用传 None，确认免费才传 Decimal('0')。"""
        if status not in {"succeeded", "failed"}:
            raise ValueError("status 必须为 succeeded 或 failed")
        if actual_cost is not None:
            _money(actual_cost)
        for value in (input_tokens, output_tokens):
            if value is not None and (type(value) is not int or value < 0):
                raise ValueError("token 数必须为非负整数或 None")
        with self._lock:
            record = self._get(reservation_id)
            if record.status != "pending":
                raise UsageStateError("调用已经核销")
            record = replace(record, status=status, actual_cost=actual_cost,
                             input_tokens=input_tokens, output_tokens=output_tokens)
            self._records[reservation_id] = record
            return record

    def reconcile(self, reservation_id: str, actual_cost: Decimal) -> UsageRecord:
        """只对已结束但费用未知的调用补记实际金额，不伪造零费用。"""
        amount = _money(actual_cost)
        with self._lock:
            record = self._get(reservation_id)
            if record.status == "pending" or record.actual_cost is not None:
                raise UsageStateError("仅可对已结束且费用未知的调用对账")
            record = replace(record, actual_cost=amount)
            self._records[reservation_id] = record
            return record
