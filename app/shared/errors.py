"""公共技术错误；提供稳定错误码，不在此绑定 HTTP 或业务状态。

流程：底层能力抛出分类错误 → 调用方依据 code 处理 → 后续接口层转换响应。
消息只使用受控说明；不要传入凭据、原始供应商响应或用户全文。
"""


class AppError(Exception):
    """技术错误基类；与 answered/clarify/insufficient_evidence 等业务结果分离。"""

    code = "technical_error"


class PathBoundaryError(AppError, ValueError):
    """路径不符合受限相对路径规则。"""

    code = "invalid_path"


class BudgetExceededError(AppError):
    """新请求的预留额超出剩余预算。"""

    code = "budget_exceeded"


class UsageStateError(AppError):
    """用量记录不存在或发生重复核销等状态冲突。"""

    code = "usage_state_error"


class ResourceBusyError(AppError):
    """执行容量已满；调用方决定何时重试，本层不自动重试。"""

    code = "resource_busy"


class ResourceClosedError(AppError):
    """执行器已经关闭，不再接收新任务。"""

    code = "resource_closed"


class ExternalError(AppError):
    """外部能力受控错误；detail 仅允许模块名/字段名，不传原始响应。"""
    def __init__(self, code, detail):
        self.code=code
        super().__init__(f"{code}: {detail}")
