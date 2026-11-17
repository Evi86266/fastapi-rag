# FastAPI 技术文档助手

面向 Python 开发者，使用 FastAPI 官方简体中文资料回答接口开发问题，并提供可核对的出处。

## 从这里读起

1. [requirements.md](requirements.md) · 产品范围、费用和空间上限、正式验收标准。
2. [architecture.md](architecture.md) · Windows 应用与 CPU 模型、Linux 虚拟机服务、Qwen API，以及流程和待验证事项。
3. [plan.md](plan.md) · 阶段 3 任务顺序、每项输入输出、验收方法和完成记录。
4. [AGENTS.md](AGENTS.md) · PyCharm 内置 Codex 的协作、变更、验证与提交规则。
5. [docs/data-feasibility.md](docs/data-feasibility.md) · 资料来源、覆盖范围和核查结果。
6. [evaluation/sample-review.md](evaluation/sample-review.md) · 三个代表问题与评分方法。
7. [docs/environment.md](docs/environment.md) · uv、PyCharm、环境变量和本地启动方法。

## 当前状态

阶段 4 已开始。基础依赖、项目骨架、配置加载、日志和健康接口已搭建。入库、检索、问答图和外部服务仍需按任务实现。

用户已确认：保留页面与 SSE 的架构设计，在核心问答通过后作为可选任务；历史和业务归档同样可选。核心首版通过问答 API、接口文档或命令演示。

在 PyCharm 中选择项目的 .venv 解释器，按环境说明验证启动。后续每次做一个可验证任务，由用户运行检查并确认后再提交 Git。完整复现和正式独立题验收安排在阶段 5。

## 已有目录用途

| 路径 | 用途 |
|---|---|
| requirements.md | 决定做什么、资源边界和验收标准。 |
| architecture.md | 说明模块、技术与数据流；设计不代表已部署验证。 |
| plan.md | 说明先做什么、每次交付和验收什么。 |
| AGENTS.md | 约束 Codex 的协作方式及操作边界。 |
| docs/ | 数据调研；后续补充环境与复现说明。 |
| corpus/README.md | 语料说明。 |
| corpus/manifest.json | 固定版本语料清单与来源校验信息。 |
| corpus/raw/docs/zh/docs/tutorial/ | 10 篇官方简体中文 Markdown 教程。 |
| corpus/raw/docs_src/ | 64 个配套 Python 示例，属于建库素材。 |
| corpus/raw/LICENSE | 上游许可证。 |
| evaluation/ | 开发诊断题与评分说明；后续管理独立验收材料，禁止入库。 |
| .idea/ | PyCharm 项目设置，不是应用代码或知识库输入。 |

当前 corpus 没有本地 PDF 或图片文件；正文中的图片链接不代表图片已下载或参与理解。

## 应用骨架与运行产物

| 路径 | 用途 |
|---|---|
| app/ | API、LangGraph 编排、入库与问答、模型/存储适配，以及可选页面。 |
| scripts/ | 最小验证与辅助入口。 |
| tests/ | 必要的模块和集成测试。 |
| data/index/ | 可重建片段、构建元数据与活动版本记录。 |
| data/reports/ | 环境、资源、费用、性能及运行报告。 |
| logs/ | 有保留限制的运行日志。 |

app/、scripts/ 和 tests/ 已建立基础骨架。data/ 与 logs/ 随对应任务或运行配置生成。项目新增占用不超过 10 GB，已有模型与虚拟机基础占用单列；服务器和模型 API 每月合计不超过 100 元。详细口径以 requirements.md 为准。
