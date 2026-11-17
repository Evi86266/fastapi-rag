# 开发诊断题与验收口径

[诊断题 JSON](diagnostic-questions.json) 包含 20 道开发题，17 道有据题与 3 道边界题。题目用中文，证据定位到同一提交中的官方简体中文教程。

## 三个已确认的代表案例

### Q05 接口同时接收路径中的 item_id、普通字符串 q 和 Pydantic 模型 item，分别从哪里取值？

在没有其他显式声明时，分别来自路径、查询和请求体。

[请求体 + 路径 + 查询参数](https://github.com/fastapi/fastapi/blob/ca5f60ee72f35fb2134d8b5d26bbb75965bcff66/docs/zh/docs/tutorial/body.md#L138-L161)

### Q11 工具函数抛出且未被业务代码捕获的 HTTPException 后，调用它的接口函数还会继续正常执行吗？

在题设未捕获异常时，正常执行中断，由框架生成相应错误响应；区分 raise 与 return，不推广成任何被捕获异常都必定结束请求。

[在代码中触发 `HTTPException`](https://github.com/fastapi/fastapi/blob/ca5f60ee72f35fb2134d8b5d26bbb75965bcff66/docs/zh/docs/tutorial/handling-errors.md#L30-L43)

### Q16 一个请求能否同时用 File/Form 上传文件，又把 Body 参数当作 application/json 接收？

应说明此声明组合下的编码冲突；可建议把元数据作为表单字段，不声称 multipart 永远不能携带 JSON 文本。

[定义 `File` 与 `Form` 参数](https://github.com/fastapi/fastapi/blob/ca5f60ee72f35fb2134d8b5d26bbb75965bcff66/docs/zh/docs/tutorial/request-forms-and-files.md#L21-L38)

## 逐题检查

| 维度 | 判定 |
|---|---|
| 证据召回 | 记录必要证据是否进入模型上下文，多证据题记录覆盖情况。 |
| 回答正确 | 0 分为核心错误，1 分为遗漏关键条件，2 分为关键要点与条件齐全。 |
| 引用支持 | 0 分为缺失、错链或不支持核心结论，1 分为部分支持，2 分为核心事实均有来源支持。 |
| 无依据断言 | 单独记录实质性无依据的断言。 |
| 边界处理 | 按预期行为判定通过或失败。 |
| 性能和成本 | 记录延迟与实际调用费用。 |

有据题严格通过要求正确性与引用支持均为 2 分，且没有实质性无依据断言。正式验收另备 20 道独立题，16 道有据题至少通过 13 道，4 道边界题全部通过。开发诊断题用于定位和调试，独立题在调参前冻结。使用同一模型和可比生成参数比较直接回答与 RAG，并记录证据命中。

Q04 只检查文档明确举例的 `yes`。其他布尔输入应以固定依赖环境实测为准。
