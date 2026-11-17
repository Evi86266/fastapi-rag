# 数据可行性调研

本项目采用 FastAPI 官方简体中文教程，资料固定到 [0.135.1 对应的提交](https://github.com/fastapi/fastapi/blob/ca5f60ee72f35fb2134d8b5d26bbb75965bcff66/docs/zh/docs/tutorial)。版本号用于标识知识库快照，应用依赖版本在架构阶段选择。

## 已归档的资料

| 编号 | 主题 | 官方来源 |
|---|---|---|
| D01 | 路径参数 | [固定版本原文](https://github.com/fastapi/fastapi/blob/ca5f60ee72f35fb2134d8b5d26bbb75965bcff66/docs/zh/docs/tutorial/path-params.md) |
| D02 | 查询参数 | [固定版本原文](https://github.com/fastapi/fastapi/blob/ca5f60ee72f35fb2134d8b5d26bbb75965bcff66/docs/zh/docs/tutorial/query-params.md) |
| D03 | 请求体 | [固定版本原文](https://github.com/fastapi/fastapi/blob/ca5f60ee72f35fb2134d8b5d26bbb75965bcff66/docs/zh/docs/tutorial/body.md) |
| D04 | 查询参数和字符串校验 | [固定版本原文](https://github.com/fastapi/fastapi/blob/ca5f60ee72f35fb2134d8b5d26bbb75965bcff66/docs/zh/docs/tutorial/query-params-str-validations.md) |
| D05 | 请求体 - 多个参数 | [固定版本原文](https://github.com/fastapi/fastapi/blob/ca5f60ee72f35fb2134d8b5d26bbb75965bcff66/docs/zh/docs/tutorial/body-multiple-params.md) |
| D06 | 处理错误 | [固定版本原文](https://github.com/fastapi/fastapi/blob/ca5f60ee72f35fb2134d8b5d26bbb75965bcff66/docs/zh/docs/tutorial/handling-errors.md) |
| D07 | 依赖项 | [固定版本原文](https://github.com/fastapi/fastapi/blob/ca5f60ee72f35fb2134d8b5d26bbb75965bcff66/docs/zh/docs/tutorial/dependencies/index.md) |
| D08 | 响应模型 - 返回类型 | [固定版本原文](https://github.com/fastapi/fastapi/blob/ca5f60ee72f35fb2134d8b5d26bbb75965bcff66/docs/zh/docs/tutorial/response-model.md) |
| D09 | 请求表单与文件 | [固定版本原文](https://github.com/fastapi/fastapi/blob/ca5f60ee72f35fb2134d8b5d26bbb75965bcff66/docs/zh/docs/tutorial/request-forms-and-files.md) |
| D10 | 测试 | [固定版本原文](https://github.com/fastapi/fastapi/blob/ca5f60ee72f35fb2134d8b5d26bbb75965bcff66/docs/zh/docs/tutorial/testing.md) |

10 篇中文文档共 48,992 个 UTF-16 代码单元，含 Markdown 标记。正文包含 82 处代码引用，指向 64 个不同的 Python 示例。原资料路径与代码均保留，方便按同一快照追溯。上游采用 MIT 许可，归档保留原版权与许可证。[上游许可证](https://github.com/fastapi/fastapi/blob/ca5f60ee72f35fb2134d8b5d26bbb75965bcff66/LICENSE)

## 建库所需保留的内容

保留标题层级、正文、代码、警告和版本条件。上游 Markdown 的代码包含指令需要关联到对应示例，才能保留实际代码。来源记录应含文档标题、章节、版本与固定链接。首批只收这 10 篇官方中文教程，扩充看实际覆盖缺口。

## 诊断题覆盖

已有 17 道有据题，每题标注中文原文行号及相关示例。另有 3 道边界题，分别检查信息不足、超范围和跨版本保证。详见 [完整诊断题](../evaluation/diagnostic-questions.json) 和 [评分说明](../evaluation/sample-review.md)。

本阶段完成资料与证据的静态核查。建库清洗结果、检索命中、回答质量、API 费用与部署表现由后续实验验证。
