# 开发任务、搭建进度与验收计划

阶段 3 制定 · 阶段 4 执行中 · 计划细化更新：2026-11-23

本文件把 [需求](requirements.md) 和 [架构](architecture.md) 转成执行任务。阶段 4 已开始，基础环境、模型/存储适配及目录骨架已有实现；用户本轮确认 T03b-5 模型门面与 ChatOpenAI 重构已验收；配置清理维持原记录。T04 结构/状态实现与检查见文末，完整入库/问答链仍待实现。由 PyCharm 内置 Codex 每次协助完成一个可验证任务；当前状态以本文件进度表和追加记录为准。

## 1. 范围与执行方式

必做：环境验证、中文语料解析、版本化建库、混合检索、可切换重排、LangGraph 问答、非流式 API、开发评测与复现说明。重排默认是否开启由资源与效果实测决定。

页面与 SSE 保留架构设计，在核心问答通过后作为可选任务；不做也不影响核心首版交付。MongoDB 历史、MinIO 业务归档同样可选，启用前另列任务。MinIO 作为 Milvus 底层依赖与业务归档是两回事。PDF、图片理解、真正的模型 token 流、HyDE、WebSearch、多轮指代改写不在当前必做范围。

开发循环：明确本次任务和验收标准 → Codex 实现并做必要检查 → 用户在 PyCharm 运行、调试和检查 → 根据反馈修复复测 → 用户确认后提交 Git → 用户确认开始下一任务。任务含子项时，每个子项都是一次独立工作单元，不在一次对话中默认完成整组。

执行顺序：先验收已有 T01 本机核查、T02a 基础环境和 T03a 入口；再完成 T03a 配置收尾及 T03b-1～T03b-4 公共基础；补齐 T01 虚拟机/空间核查后，结合 T03b-5 实现 infra 并逐项完成 T02b～T02e；然后 T04 → T05（含入库图验收）→ T06 → T07 → T09。基础配置、日志和健康接口不必等待全部外部服务验证通过，但依赖外部能力的业务须先通过对应验证。T08 仅在 T07 通过且用户选择后插入。资源或兼容性失败时暂停依赖该结果的任务，整理证据与替代方案；不自动换架构、升级共享服务或采购服务器。

## 1.1 十步搭建进度（2026-11-19）

状态依据为文件、依赖目录、Git 核对及环境文档；2026-11-18 已完成本轮 T03a 配置收尾和 T03b-1 日志统一的代码及自动检查，包含本地健康服务启动，未运行模型或外部服务。文件存在不等于功能完成，自动检查通过不等于用户验收通过。

| 搭建顺序 | 工作 | 对应任务 | 当前状态与剩余事项 |
|---|---|---|---|
| 1 | 核查 Python、uv、磁盘和现有模型 | T01 | 本机部分已有记录；完整空间基线、虚拟机资源和服务条件未完成 |
| 2 | uv 路径、D 盘缓存、项目镜像 | T02a | 项目镜像及缓存配置说明已有；新终端/PyCharm 实际生效情况待用户核对 |
| 3 | 声明依赖、创建环境、绑定 PyCharm | T02a | .venv、uv.lock 及基础包已有；PyCharm 绑定待确认，模型/存储/生成接入依赖按任务补齐 |
| 4 | 创建六层项目目录 | T03a | 骨架已建立，多数业务文件仅有职责说明和“待实现” |
| 5 | .env.example 与配置加载 | T03a | 按用户最新要求改为 .env + os.getenv，移除 Settings/RuntimeConfig；自动检查通过，用户已确认本次配置收尾验收；模型配置校验已实现，配置清理待用户验收 |
| 6 | 日志、提示词加载、公共工具 | T03b-1～4 | T03b-1 日志统一已通过自动检查及用户验收；T03b-2 用户已确认验收；T03b-3 用户已确认验收；T03b-4 用户已确认验收，并已提交 331c6cc；原有未提交文档/测试保留 |
| 7 | infra 外部服务适配 | T03b-5、T02b～e | T03b-5 通用生命周期与分项就绪已实现；按用户要求，T03b-5 真实适配及本范围自动/实机检查完成，待用户验收；完整 Milvus schema/查询兼容性及活动索引留在 T02d/T05 |
| 8 | 入库状态、节点和业务 | T04、T05 | 文件骨架已有，解析、切块、建库、图和 CLI 尚未实现 |
| 9 | 问答状态、节点和业务 | T06、T07 | 文件骨架已有，完整检索生成链尚未实现 |
| 10 | API、验证与 Git | T03a、T07b/c、T09；贯穿所有任务 | 健康接口已有，/ready 按分项状态判断，当前因活动索引尚未接入返回 503，外部能力状态按实际探测；问答接口待实现；已有初始化提交，本次配置/日志用户验收已记录；其他任务验收按各自范围推进 |

依赖与实测以文末 T03b-5 及环境最新记录为准；配置采用 .env + os.getenv，不使用 Settings 对象。2026-11-23 本次仅修改计划，未复跑应用/模型检查。

## 1.2 当前下一步

1. 核对 T03b-5、配置层清理的用户验收状态及 T01 资源余项，既有实现不重复搭建；完整 Milvus schema/查询兼容性留在 T02d/T05。
2. 按 1.3 节从结构和状态开始，逐节点实现 T04 → T05 → T06 → T07，每次交付一个可验证工作单元。
3. 本次仅授权细化计划；一节点一业务文件是最新设计，代码仍未实现，不据此标记任何业务验收通过。
4. T07 通过后选择 T08 或进入 T09，正式独立评测仍在阶段 5。

## 1.3 细化搭建顺序与文件契约（2026-11-23）

本节按用户最新要求细化 T04～T07；不改变后文业务验收标准。所有路径以完整项目路径列出。已有占位不等于实现；下述新增文件、函数、字段和参数均为待实施设计。本次仅修改 plan.md，不创建、重命名或删除代码。

### 1.3.1 一节点一业务文件

节点只读状态、调用自己对应的一个业务服务、返回状态增量；业务服务处理业务规则，infra 处理模型/数据库，公共工具处理通用能力。主图决定路由，不在节点里调用另一个节点。共享工具和适配器允许复用，不计入一对一业务文件。

入库保留 7 个节点：校验清单 → 解析 → 切块 → 编码 → 写入 → 验证 → 激活。问答保留 7 个节点：输入 → 检索（含问题编码）→ 融合 → 可选重排 → 证据 → 生成 → 引用校验。无需新增问题编码节点。

原 `D:/S/项目/实战项目/fastapi-rag/app/rag/ingest/index_service.py` 目前是占位。后续 T05 将它的职责拆到 write_index_service.py、validate_index_service.py、activate_index_service.py 三个独立业务文件；检查引用后移除旧占位，不保留第二套索引业务入口。本轮不操作该文件。

| 编号/任务 | 节点文件（已有占位） | 唯一对应业务文件 | 状态 |
|---|---|---|---|
| I01 / T04a 校验清单 | `D:/S/项目/实战项目/fastapi-rag/app/process/ingest/nodes/node_validate_manifest.py` | `D:/S/项目/实战项目/fastapi-rag/app/rag/ingest/manifest_service.py` | 已有占位待实现 |
| I02 / T04a 解析文档 | `D:/S/项目/实战项目/fastapi-rag/app/process/ingest/nodes/node_parse_documents.py` | `D:/S/项目/实战项目/fastapi-rag/app/rag/ingest/parse_service.py` | 已有占位待实现 |
| I03 / T04b 语义切块 | `D:/S/项目/实战项目/fastapi-rag/app/process/ingest/nodes/node_split_documents.py` | `D:/S/项目/实战项目/fastapi-rag/app/rag/ingest/split_service.py` | 已有占位待实现 |
| I04 / T05a 片段编码 | `D:/S/项目/实战项目/fastapi-rag/app/process/ingest/nodes/node_embed_chunks.py` | `D:/S/项目/实战项目/fastapi-rag/app/rag/ingest/embedding_service.py` | 已有占位待实现 |
| I05 / T05a 写入索引 | `D:/S/项目/实战项目/fastapi-rag/app/process/ingest/nodes/node_write_index.py` | `D:/S/项目/实战项目/fastapi-rag/app/rag/ingest/write_index_service.py` | 业务文件待新增 |
| I06 / T05b 验证索引 | `D:/S/项目/实战项目/fastapi-rag/app/process/ingest/nodes/node_validate_index.py` | `D:/S/项目/实战项目/fastapi-rag/app/rag/ingest/validate_index_service.py` | 业务文件待新增 |
| I07 / T05b 激活索引 | `D:/S/项目/实战项目/fastapi-rag/app/process/ingest/nodes/node_activate_index.py` | `D:/S/项目/实战项目/fastapi-rag/app/rag/ingest/activate_index_service.py` | 业务文件待新增 |
| Q01 / T07a 输入检查 | `D:/S/项目/实战项目/fastapi-rag/app/process/query/nodes/node_check_input.py` | `D:/S/项目/实战项目/fastapi-rag/app/rag/query/input_service.py` | 已有占位待实现 |
| Q02 / T06a 双路检索 | `D:/S/项目/实战项目/fastapi-rag/app/process/query/nodes/node_retrieve.py` | `D:/S/项目/实战项目/fastapi-rag/app/rag/query/retrieval_service.py` | 已有占位待实现 |
| Q03 / T06a 融合去重 | `D:/S/项目/实战项目/fastapi-rag/app/process/query/nodes/node_fuse.py` | `D:/S/项目/实战项目/fastapi-rag/app/rag/query/fusion_service.py` | 已有占位待实现 |
| Q04 / T06b 可选重排 | `D:/S/项目/实战项目/fastapi-rag/app/process/query/nodes/node_rerank.py` | `D:/S/项目/实战项目/fastapi-rag/app/rag/query/rerank_service.py` | 已有占位待实现 |
| Q05 / T07a 证据打包 | `D:/S/项目/实战项目/fastapi-rag/app/process/query/nodes/node_prepare_evidence.py` | `D:/S/项目/实战项目/fastapi-rag/app/rag/query/evidence_service.py` | 已有占位待实现 |
| Q06 / T07a 生成回答 | `D:/S/项目/实战项目/fastapi-rag/app/process/query/nodes/node_generate_answer.py` | `D:/S/项目/实战项目/fastapi-rag/app/rag/query/answer_service.py` | 已有占位待实现 |
| Q07 / T07a 校验引用 | `D:/S/项目/实战项目/fastapi-rag/app/process/query/nodes/node_validate_citations.py` | `D:/S/项目/实战项目/fastapi-rag/app/rag/query/citation_service.py` | 已有占位待实现 |

### 1.3.2 实际编码顺序

每一行可再按下文节点步骤独立实施、验收，不授权一次实现整组。保留 T01～T09 编号；I/Q 编号是节点工作单元，非运行完成记录。

| 顺序 | 工作单元 | 前置与交付门槛 |
|---|---|---|
| 1 | 核对已有 T03b-5、配置清理验收和 T01 资源余项 | 利用已有实测，不重复安装模型；Milvus 完整 schema/搜索验证仍待 T02d |
| 2 | T04 业务结构、入库状态、当前需要的工具/配置 | 先定输入输出，模块导入无副作用 |
| 3 | I01 → I02 → I03；T04c 前半图检查 | 每完成服务即实现配对节点；校验来源、稳定 ID 和失败传播 |
| 4 | T02d + T05 所需 Milvus schema/方法、I04 → I05 | 专用集合验证插入、dense/sparse 查询；编码和写入可核对 |
| 5 | I06 → I07 → T05c 完整图/CLI/活动就绪 | 验证通过才激活；全量构建、失败恢复、重启恢复 |
| 6 | T06 问答候选结构、状态及 query 编码门面；Q02 → Q03 → Q04 | 可先直接调用检索服务验证；调参前独立验收题冻结隔离 |
| 7 | T07 补输出结构、Q01 → Q05 → Q06 → Q07 | 三种业务状态、引用与技术错误清楚；不把检索分数当答案保证 |
| 8 | T07a/b 问答图、API、依赖与生命周期 | 整请求容量限制、线程推理、HTTP 错误映射完成 |
| 9 | T07c 开发评测 → T09 交付准备 | Q05/Q11/Q16 及 20 道开发题记录；正式独立评测仍在阶段 5 |
| 10 | T08 可选功能 | 仅 T07 通过且用户选择后实施；不隐含历史/归档 |

### 1.3.3 业务结构与状态文件

**业务结构：`D:/S/项目/实战项目/fastapi-rag/app/rag/schemas.py`（已有占位）**

1. T04 定义 ManifestEntry、ValidatedCorpus、SourceSpan、ParsedBlock、Chunk。来源包含 path、line_start/line_end、固定提交 URL、官方页面、版本；多文件/不连续选行用 source_spans 列表，不能伪装连续范围。
2. Chunk 定义 chunk_id/document_id/text/content_hash/heading_path/content_type/related_chunk_ids/source_commit/knowledge_version/parser_version/splitter_version；build_id 与稳定 ID 分离。
3. T05 定义 BuildMetadata、ValidationReport、ActiveIndex：构建/集合、清单及产物指纹、模型/分词/编码/schema 版本、计数、验证状态和前一活动版本。向量可复用 EncodedText；落盘时定义稀疏键的 JSON 序列化/恢复规则。
4. T06 定义 Candidate：片段及来源、build_id、召回通道、两路排名/分数、融合和重排分数、可追踪窗口。
5. T07 定义 EvidenceItem、AnswerDraft、Citation、QueryResult；业务状态限定 answered/clarify/insufficient_evidence，技术错误另行表达。用 Pydantic 校验边界数据和结构化生成，禁止未知字段/非法行号/空 answered 等不一致结果。
6. 分阶段验证序列化往返、字段约束和跨层映射，不把 SDK 对象或密钥塞进业务结构。

**入库状态：`D:/S/项目/实战项目/fastapi-rag/app/process/ingest/state.py`（已有占位）**

1. 定义 IngestState（TypedDict）：task_id、build_id、manifest_path、validated_manifest、source_commit、knowledge_version、manifest_digest、parsed_artifact、chunks_artifact、vectors_artifact、document_count、chunk_count、vector_count、collection_name、build_metadata、validation_report、previous_active_build_id、active_index、status、timings、error。
2. CLI 初始化构建 ID 与输入；I01～I07 分别更新上表输出字段，不原地修改共享嵌套对象，不使用全局可变状态。
3. 状态只保存产物引用、必要元数据和统计，不反复携带全库向量；客户端/执行器通过依赖注入提供。
4. 明确 created/validated/parsed/split/embedded/written/verified/activated/failed 阶段及每个节点的必要输入；技术异常记录受控错误后向入口传播。
5. T04c 验证前三节点衔接；T05c 验证完整状态转换、失败不激活以及重跑使用独立构建标识。

**问答状态：`D:/S/项目/实战项目/fastapi-rag/app/process/query/state.py`（已有占位）**

1. T06 先定义 request_id、question、context、target_version、knowledge_version、active_build_id、collection_name、retrieval_text、dense_candidates、sparse_candidates、fused_candidates、ranked_candidates。
2. T07 补 session_id（可选，不代表启用历史）、input_decision、evidence_items、citation_map、answer_draft、answer、citations、status、timings、usage、error。
3. 请求开始固定活动版本快照；各节点返回增量，列表默认覆盖而非无条件累加，防止重试造成重复候选。
4. clarify/insufficient_evidence 是正常业务终态，模型/存储/解析/预算异常独立；不在状态存密钥或 SDK 实例。
5. 验证请求之间不串状态、提前结束不调用模型、引用只来自本请求证据。

### 1.3.4 工具与配置文件（按需复用或补齐）

“工具类/配置类文件”指职责模块，不强制使用 Python class。继续 .env + os.getenv 与小型校验函数，不重新引入 Settings/BaseSettings/Config 对象。

| 完整路径 | 当前状态 | 需要的能力/步骤 |
|---|---|---|
| `D:/S/项目/实战项目/fastapi-rag/app/shared/utils/paths.py` | 已有 | 复用 resolve_within；校验源文件和产物真实路径边界。 |
| `D:/S/项目/实战项目/fastapi-rag/app/shared/utils/hashing.py` | 已有 | 复用 Git blob SHA-1 校验原件、SHA-256 生成内容/产物指纹。 |
| `D:/S/项目/实战项目/fastapi-rag/app/shared/utils/artifact_io.py` | 待新增 | T04 起按需实现 UTF-8 JSON/JSONL 读写、schema 校验、临时文件与同卷原子替换；失败不覆盖旧产物。仅做 I/O，不做激活业务判断。 |
| `D:/S/项目/实战项目/fastapi-rag/app/shared/utils/token_budget.py` | 待新增 | 接收已加载 tokenizer，计数单文本/成对输入；复用统一 Qwen 消息预算规则，禁止按字数替代 token；不自行加载模型。 |
| `D:/S/项目/实战项目/fastapi-rag/app/shared/runtime/tracing.py` | 已有 | node_log/step_log/trace_context 记录 build_id/request_id 和真实完成耗时；不吞异常。 |
| `D:/S/项目/实战项目/fastapi-rag/app/shared/runtime/logger.py` | 已有 | 入口初始化、正常关闭刷新；不记录密钥和完整模型消息。 |
| `D:/S/项目/实战项目/fastapi-rag/app/shared/runtime/load_prompt.py` | 已有 | 复用 string.Template 单次替换，缺模板/变量明确失败。 |
| `D:/S/项目/实战项目/fastapi-rag/app/shared/runtime/resources.py` | 已有待接入 | BoundedExecutor 运行同步 CPU/SDK 调用，满容量拒绝；取消等待不提前释放在途线程容量。 |
| `D:/S/项目/实战项目/fastapi-rag/app/shared/errors.py` | 已有待扩展 | 按节点定义受控的清单/解析/索引/生成/引用错误码；技术错误不转换为资料不足。 |
| `D:/S/项目/实战项目/fastapi-rag/app/shared/metrics.py` | 已有 | 复用统计结构；不要与真实持久费用台账重复预留/核销。 |
| `D:/S/项目/实战项目/fastapi-rag/app/shared/usage_store.py` | 已有 | 保留 SQLite 预算、预留、核销、未知费用阻止与对账规则。 |
| `D:/S/项目/实战项目/fastapi-rag/app/shared/config/settings.py` | 已有 | 只保留 PROJECT_ROOT 与显式 load_environment；模块导入不读 .env。 |
| `D:/S/项目/实战项目/fastapi-rag/app/shared/config/runtime_config.py` | 已有 | 复用布尔、正整数、日志级别检查；用于运行开关和容量参数。 |
| `D:/S/项目/实战项目/fastapi-rag/app/shared/config/model_config.py` | 已有 | 复用路径、地址、金额校验；既有 BGE/RERANK 长度、模型路径、Milvus、Qwen 和费用字段保留。 |
| `D:/S/项目/实战项目/fastapi-rag/app/shared/config/rag_config.py` | 待新增 | 提供切块、批量、候选数、RRF、证据数、问答容量的小型读取校验函数；不持有配置对象/导入缓存。 |
| `D:/S/项目/实战项目/fastapi-rag/.env.example` | 已有，后续实现时同步 | 拟新增 CHUNK_MAX_TOKENS、CHUNK_OVERLAP_TOKENS、INGEST_BATCH_SIZE、DENSE_TOP_K、SPARSE_TOP_K、FUSION_TOP_K、RRF_K、EVIDENCE_TOP_K、QUERY_MAX_CONCURRENCY；本次不修改。 |

拟配置的约束：overlap 非负且小于 chunk 长度；单文本长度不超过模型预算；批量不得超过适配器上限；候选数/证据数/RRF_K/并发数为正数，证据数不超过候选上限。dense/sparse 各 10、融合最多 10、证据 3～5 仅是初始建议，最终受实际输入预算约束；QUERY_MAX_CONCURRENCY 首版为 1。复用已有 RERANK_ENABLED，不另设冲突开关。RRF_K 和切块预算在实施时固定初值、说明依据并记录构建/评测元数据；运行参数变化不混用旧构建。

新增配置仅在实际消费该字段的任务中加入，届时同步 `D:/S/项目/实战项目/fastapi-rag/.env.example` 和 `D:/S/项目/实战项目/fastapi-rag/docs/environment.md`，不改真实密钥；本轮范围只有 plan.md。

### 1.3.5 节点编码任务卡

每张卡遵循“先业务结构/依赖 → 业务函数 → 配对节点 → 小样本及失败分支”的顺序。下文工具简称的完整路径见上一表，外部连接路径见下一节。节点共同使用 tracing.py；函数名/状态字段为设计，非现有可调用 API。

#### I01 / T04a 校验清单

- 节点：`D:/S/项目/实战项目/fastapi-rag/app/process/ingest/nodes/node_validate_manifest.py`。
- 唯一业务：`D:/S/项目/实战项目/fastapi-rag/app/rag/ingest/manifest_service.py`。
- 输入 → 输出：manifest_path → validated_manifest、manifest_digest、knowledge_version。
- 依赖：paths.py、hashing.py；settings.py。

1. 读取并校验 manifest 字段、固定提交、重复条目和 10 篇文档/64 个示例/许可证数量。
2. 用 paths.resolve_within 限定 corpus/raw 内路径，原始字节用 git_blob_sha1 校验，不先改变换行。
3. 核对来源 URL 与提交；许可证只校验不作为知识片段，evaluation 不进入输入。
4. 返回允许读取的文件描述及指纹；节点写入状态，缺文件/越界/哈希错误明确终止。

验收：篡改哈希、越界和缺文件均失败；清单之外的文件不会被解析。

#### I02 / T04a 解析文档

- 节点：`D:/S/项目/实战项目/fastapi-rag/app/process/ingest/nodes/node_parse_documents.py`。
- 唯一业务：`D:/S/项目/实战项目/fastapi-rag/app/rag/ingest/parse_service.py`。
- 输入 → 输出：validated_manifest → parsed_artifact、document_count。
- 依赖：paths.py、artifact_io.py；settings.py。

1. 按原始行号读取 Markdown，维护标题栈并识别段落、列表、围栏及 /// 提示块。
2. 解析示例包含指令，将目标映射到已校验清单，不能直接执行其中的 ../../ 路径。
3. 区分 ln 选行与 hl 高亮，检查范围；分别保留 Markdown 和 Python 的来源行号。
4. 输出 ParsedBlock 和正文/代码关联；图片只保留链接，未知重要指令明确报错，不能静默略过。

验收：抽查 Q05/Q11/Q16 材料及 ln[16:19] hl[17] 示例，选行与来源可回查。

#### I03 / T04b 语义切块

- 节点：`D:/S/项目/实战项目/fastapi-rag/app/process/ingest/nodes/node_split_documents.py`。
- 唯一业务：`D:/S/项目/实战项目/fastapi-rag/app/rag/ingest/split_service.py`。
- 输入 → 输出：parsed_artifact → chunks_artifact、chunk_count。
- 依赖：token_budget.py、hashing.py、artifact_io.py；rag_config.py、model_config.py。

1. 按标题、段落、提示块、代码边界组织片段，保留关键条件。
2. 通过模型适配器取得真实 tokenizer 计数，分别约束 embedding 与 reranker 成对输入预算。
3. 长代码按函数或行窗口切分，保存父片段、原始行范围和关联 ID，不静默截断。
4. 根据来源、处理版本和内容生成稳定 ID/指纹；build_id 独立保存，不参与稳定 ID。
5. 检查空正文、重复 ID 和关联完整性，按确定顺序写 chunks.jsonl。

验收：同输入同版本结果稳定；长代码可追溯；实际分词长度达标。

#### I04 / T05a 片段编码

- 节点：`D:/S/项目/实战项目/fastapi-rag/app/process/ingest/nodes/node_embed_chunks.py`。
- 唯一业务：`D:/S/项目/实战项目/fastapi-rag/app/rag/ingest/embedding_service.py`。
- 输入 → 输出：chunks_artifact → vectors_artifact、vector_count。
- 依赖：token_budget.py、artifact_io.py、resources.py；model_config.py、rag_config.py。

1. 按固定顺序建立 chunk_id 与文本对应关系，以小批量调用 llm_provider.embed_documents。
2. 读取 dense_vecs/lexical_weights，校验数量、1024 维、有限数值与稀疏键值。
3. 绑定 chunk_id 保存编码结果及模型/分词/归一化配置标识。
4. 分批输出构建专属产物；完整成功才更新完成状态，失败不能继续激活。

验收：输出与片段一一对应；批次失败不生成伪完整产物；无模型下载。

#### I05 / T05a 写入索引

- 节点：`D:/S/项目/实战项目/fastapi-rag/app/process/ingest/nodes/node_write_index.py`。
- 唯一业务：`D:/S/项目/实战项目/fastapi-rag/app/rag/ingest/write_index_service.py`。
- 输入 → 输出：片段和向量产物 → collection_name、build_metadata。
- 依赖：artifact_io.py；model_config.py、rag_config.py；milvus.py、milvus_schema.py。

1. 生成带项目前缀和 build_id 的新集合名，拒绝覆盖旧集合和培训集合。
2. 通过 MilvusStore 创建经 T02d 验证的 schema/索引；批量插入正文、来源和 dense/sparse。
3. 核对主键唯一、字段长度和返回数量，完成持久化、索引构建及加载。
4. 写 index-meta.json 和构建状态，保持待验证，不更新 active.json。

验收：失败不污染活动集合；字段和查询兼容有实测记录。

#### I06 / T05b 验证索引

- 节点：`D:/S/项目/实战项目/fastapi-rag/app/process/ingest/nodes/node_validate_index.py`。
- 唯一业务：`D:/S/项目/实战项目/fastapi-rag/app/rag/ingest/validate_index_service.py`。
- 输入 → 输出：build_metadata → validation_report。
- 依赖：artifact_io.py、hashing.py；model_config.py；milvus.py、milvus_schema.py。

1. 检查字段、维度、索引参数及模型/语料/处理版本一致性。
2. 对照片段、向量及实际存储数量和 ID；抽样回读正文和来源。
3. 分别执行 dense/sparse 查询，验证返回形状、ID 和来源。
4. 生成绑定 build_id 与元数据指纹的逐项报告，任何必需项失败都禁止激活。

验收：数量错误、来源错误、模型不符、查询失败均能阻止激活。

#### I07 / T05b 激活索引

- 节点：`D:/S/项目/实战项目/fastapi-rag/app/process/ingest/nodes/node_activate_index.py`。
- 唯一业务：`D:/S/项目/实战项目/fastapi-rag/app/rag/ingest/activate_index_service.py`。
- 输入 → 输出：validation_report、build_metadata → active_index、previous_active_build_id。
- 依赖：artifact_io.py、resources.py；settings.py；active_index.py、providers.py。

1. 验证报告通过且属于当前构建，确认集合仍可查询。
2. 读取旧活动记录，对切换加互斥；在同一文件系统写完整临时记录后原子替换 active.json。
3. 以原子替换为提交点：此前失败保留旧版本，此后重启以新记录恢复，报告实际结果。
4. 接入活动索引资源探测；每次问答固定版本快照，旧集合不自动删除。

验收：首次失败仍 not_ready；已有版本时失败旧版仍可查；切换后重启可恢复。

#### Q01 / T07a 输入检查

- 节点：`D:/S/项目/实战项目/fastapi-rag/app/process/query/nodes/node_check_input.py`。
- 唯一业务：`D:/S/项目/实战项目/fastapi-rag/app/rag/query/input_service.py`。
- 输入 → 输出：question/context/target_version、活动快照 → input_decision、retrieval_text。
- 依赖：token_budget.py；rag_config.py。

1. 校验非空和长度，保留原问题、代码缩进、错误文本和标识符。
2. 构造独立检索文本，读取活动知识版本。
3. 缺少必要条件时输出具体澄清项；明确超版本覆盖时说明范围，不保证兼容。
4. 返回 continue/clarify/insufficient_evidence 分支，技术错误独立抛出；不执行用户代码。

验收：普通问题继续；缺条件可追问；不机械要求所有问题提供版本。

#### Q02 / T06a 双路检索

- 节点：`D:/S/项目/实战项目/fastapi-rag/app/process/query/nodes/node_retrieve.py`。
- 唯一业务：`D:/S/项目/实战项目/fastapi-rag/app/rag/query/retrieval_service.py`。
- 输入 → 输出：retrieval_text、active_index → dense_candidates、sparse_candidates。
- 依赖：resources.py、token_budget.py；model_config.py、rag_config.py；providers.py、milvus.py。

1. 固定请求所用集合与 build_id，检查模型元数据。
2. 经门面 query 编码接口获取 dense/sparse；查询编码和建库编码兼容。
3. 通过 MilvusStore 分别检索两路，初始各 10 条，参数由配置读取。
4. 转换为 Candidate 并保留正文、来源、通道、排名和分数；空结果与服务故障分开。

验收：两路结果可单独查看；故障不转为空召回；不混用版本。

#### Q03 / T06a 融合去重

- 节点：`D:/S/项目/实战项目/fastapi-rag/app/process/query/nodes/node_fuse.py`。
- 唯一业务：`D:/S/项目/实战项目/fastapi-rag/app/rag/query/fusion_service.py`。
- 输入 → 输出：两路候选 → fused_candidates。
- 依赖：无需新增通用工具；rag_config.py。

1. 每路按 chunk_id 去重并确定从 1 开始的排名。
2. 按 Σ1/(rrf_k+rank) 累加两路排名分数，不直接相加原始相似度。
3. 合并通道和来源，稳定排序并按上限截取。
4. 返回融合结果；主图在空结果时结束为资料不足，不调用生成。

验收：重复候选仅一份；单路可用；同分顺序稳定。

#### Q04 / T06b 可选重排

- 节点：`D:/S/项目/实战项目/fastapi-rag/app/process/query/nodes/node_rerank.py`。
- 唯一业务：`D:/S/项目/实战项目/fastapi-rag/app/rag/query/rerank_service.py`。
- 输入 → 输出：问题、融合候选 → ranked_candidates。
- 依赖：token_budget.py、resources.py；model_config.py、rag_config.py；providers.py。

1. 关闭开关则原序返回，不能主动加载可选模型。
2. 开启时构造问题/片段文本对，真实 tokenizer 检查包含特殊符号的总长度。
3. 超长生成可追踪行窗口，保留父片段及实际来源范围；问题本身超限明确拒绝。
4. 通过门面调用受控 score，核对分数数量与有限性并排序，模型错误不静默降级。

验收：开关有效；窗口来源正确；与不重排比较覆盖率、延迟和内存。

#### Q05 / T07a 证据打包

- 节点：`D:/S/项目/实战项目/fastapi-rag/app/process/query/nodes/node_prepare_evidence.py`。
- 唯一业务：`D:/S/项目/实战项目/fastapi-rag/app/rag/query/evidence_service.py`。
- 输入 → 输出：ranked_candidates、问题 → evidence_items、citation_map。
- 依赖：token_budget.py、load_prompt.py；rag_config.py、model_config.py。

1. 挑选正文及关联代码，去重并保留完整关键条件，不机械保证 3～5 段都能放下。
2. 为实际证据/窗口分配 E1 等 ID，建立服务端来源映射。
3. 连同系统提示、JSON 格式、问题计算完整消息预算，超限则减少或缩小可追踪证据。
4. 校验最终证据与映射一致；因输入预算无法打包时返回受控限制错误，不伪装资料不足。

验收：当前 Qwen 使用 UTF-8 字节加每消息 256 余量检查，预算算法必须一致且包含完整消息。

#### Q06 / T07a 生成回答

- 节点：`D:/S/项目/实战项目/fastapi-rag/app/process/query/nodes/node_generate_answer.py`。
- 唯一业务：`D:/S/项目/实战项目/fastapi-rag/app/rag/query/answer_service.py`。
- 输入 → 输出：问题、证据包 → answer_draft、usage。
- 依赖：load_prompt.py、token_budget.py；model_config.py；qwen.py、usage_store.py。

1. 定义 AnswerDraft，完善 answer.prompt 的依据、边界、引用和语料指令隔离要求。
2. 创建 JsonOutputParser(pydantic_object=AnswerDraft)，将 get_format_instructions 放入 SystemMessage。
3. 以 HumanMessage 承载问题/证据，通过 llm_provider.chat(json_mode=True).invoke/ainvoke 调用。
4. 提取文本后 parse，再 model_validate；检查 finish_reason、非法 JSON、字段与状态。
5. 提取 token/费用/预留 ID，沿用既有预算回调；不重复记账、不自动付费重试。

验收：三种业务状态可解析；截断/超时/预算/解析错误独立；128 token 默认输出是否足够须样本验证，调整需同步预算。

#### Q07 / T07a 校验引用

- 节点：`D:/S/项目/实战项目/fastapi-rag/app/process/query/nodes/node_validate_citations.py`。
- 唯一业务：`D:/S/项目/实战项目/fastapi-rag/app/rag/query/citation_service.py`。
- 输入 → 输出：answer_draft、citation_map → answer、citations、status。
- 依赖：无需新增通用工具；settings.py（仅需要路径时）。

1. 校验状态与回答一致，answered 必须有正文及有效引用。
2. 每个引用 ID 必须来自实际送入模型的证据，拒绝虚构或跨构建 ID。
3. 去重并仅用服务端元数据组装固定链接、标题、版本、行号；窗口引用使用实际窗口范围。
4. 不删除非法引用后发布未经校验的答案；输出最终结果或明确校验错误。

验收：非法 ID、未发送证据和错版本被拒绝；ID 合法不等于语义支持，仍须人工评测。

### 1.3.6 需要补齐的连接文件

| 文件路径 | 状态/任务 | 具体实现步骤与验收 |
|---|---|---|
| `D:/S/项目/实战项目/fastapi-rag/app/infra/providers.py` | 已有待扩展，T05/T06/T07 | 补公共 query 编码和 rerank 入口，复用底层适配校验；提供受控 Milvus 业务入口/依赖注入，若沿用 call 则扩展操作白名单；接活动索引资源工厂。不得业务访问 _adapter 私有方法或重新加载模型。 |
| `D:/S/项目/实战项目/fastapi-rag/app/infra/models/embedding.py` | 已有，按需补 tokenizer 访问 | 复用 encode_queries/encode_documents，提供受控计数能力；检查维度、离线加载与超长拒绝。 |
| `D:/S/项目/实战项目/fastapi-rag/app/infra/models/reranker.py` | 已有，T06 接入 | 复用 score 与成对长度校验；门面保持开关、生命周期与资源限制。 |
| `D:/S/项目/实战项目/fastapi-rag/app/infra/models/qwen.py` | 已有，T07 接入 | 复用 ChatOpenAI 和费用回调；将消息预算规则与工具统一，避免两份不同算法；评估 128 默认输出和 512 配置上限是否满足 JSON 回答，调整前核对预算。 |
| `D:/S/项目/实战项目/fastapi-rag/app/infra/storage/milvus_schema.py` | 已有占位，T02d/T05 | 定义字段、1024 维 dense、sparse、索引/距离、字段长度和 schema 版本；专用集合实测兼容，不默认套培训参数。 |
| `D:/S/项目/实战项目/fastapi-rag/app/infra/storage/milvus.py` | 已有只读连接，T02d/T05/T06 扩展 | 补创建、批量插入、索引构建/加载、数量/回读、dense/sparse 搜索；专用 alias 和超时，SDK 返回转普通结构，禁止默认删除旧集合。 |
| `D:/S/项目/实战项目/fastapi-rag/app/infra/storage/active_index.py` | 待新增，T05 | 封装活动记录加载和集合/schema/模型一致性只读探测，提供不可变快照；激活业务仍在 activate_index_service，探针不执行切换或生成；重启恢复并接 Providers。 |
| `D:/S/项目/实战项目/fastapi-rag/app/process/ingest/main_graph.py` | 已有占位，T04c/T05c | 先验证前三节点，再连接七节点；失败终止，verified 才可激活。依赖注入服务，编译图；不要启动完整问答依赖来跑离线建库。 |
| `D:/S/项目/实战项目/fastapi-rag/scripts/build_index.py` | 已有占位，T05c | 显式加载配置/日志，生成 build_id、检查空间、只初始化建库所需模型和 Milvus，执行图、报告统计/失败退出码，finally 关闭资源；不依赖 Qwen/历史。 |
| `D:/S/项目/实战项目/fastapi-rag/app/process/query/main_graph.py` | 已有占位，T07a | 注入七个服务并编译；输入分支提前结束、空召回直接资料不足、重排关闭透传、生成后必须引用校验；技术失败由边界统一处理。 |
| `D:/S/项目/实战项目/fastapi-rag/app/api/schemas/query.py` | 已有占位，T07b | 定义 question/context/target_version 请求约束及 status/answer/citations/knowledge_version/request_id 返回模型；与业务结构显式映射，错误响应独立。 |
| `D:/S/项目/实战项目/fastapi-rag/app/api/dependencies.py` | 已有待扩展，T07b | 从 app.state 取已初始化 Providers、问答图和活动快照；未就绪明确返回错误，不在每次请求创建客户端。 |
| `D:/S/项目/实战项目/fastapi-rag/app/api/routes/query.py` | 已有占位，T07b | 实现 POST /query，生成 request_id，获取整请求容量、固定索引版本、调用图并映射结果；无效输入、未就绪/忙、上游/解析错误区分；finally 释放请求容量。 |
| `D:/S/项目/实战项目/fastapi-rag/app/main.py` | 已有待扩展，T07b | lifespan 创建并复用图及容量控制，注册 query router；CPU 调用交给 BoundedExecutor，异步模型调用也受整请求门槛约束；关闭拒绝新请求并等待在途任务后释放资源。 |
| `D:/S/项目/实战项目/fastapi-rag/app/api/routes/health.py` | 已有，T05 验证衔接 | 保持 /health 无外部副作用，/ready 仅读快照；全部必需能力和真实活动索引 ready 才返回 200。 |
| `D:/S/项目/实战项目/fastapi-rag/app/resources/prompts/answer.prompt` | 已有占位，T07a | 实现依据、版本、澄清/不足、JSON 格式和引用 ID 约束；与 EvidenceBundle/AnswerDraft 同步并记录提示词版本。 |

### 1.3.7 产物与验证安排

- 输入保持 `D:/S/项目/实战项目/fastapi-rag/corpus/manifest.json` 和 `D:/S/项目/实战项目/fastapi-rag/corpus/raw` 只读；禁止将 `D:/S/项目/实战项目/fastapi-rag/evaluation` 纳入建库。
- 拟产物：`D:/S/项目/实战项目/fastapi-rag/data/index/<build_id>/parsed.jsonl`、`D:/S/项目/实战项目/fastapi-rag/data/index/<build_id>/chunks.jsonl`、`D:/S/项目/实战项目/fastapi-rag/data/index/<build_id>/vectors.jsonl`、`D:/S/项目/实战项目/fastapi-rag/data/index/<build_id>/index-meta.json`、`D:/S/项目/实战项目/fastapi-rag/data/index/<build_id>/validation.json`；活动指针 `D:/S/项目/实战项目/fastapi-rag/data/index/active.json`。<build_id> 为运行占位符。向量缓存如保留须计量空间并定义保留数，不无限积累。
- 拟测试文件（均待新增）：`D:/S/项目/实战项目/fastapi-rag/tests/test_ingest_services.py` 覆盖清单/解析/切块；`D:/S/项目/实战项目/fastapi-rag/tests/test_index_lifecycle.py` 覆盖写入/验证/切换失败恢复；`D:/S/项目/实战项目/fastapi-rag/tests/test_query_services.py` 覆盖融合、窗口、预算、JSON 和引用；`D:/S/项目/实战项目/fastapi-rag/tests/test_rag_graphs.py` 覆盖状态分支；`D:/S/项目/实战项目/fastapi-rag/tests/test_query_api.py` 覆盖 HTTP/容量/技术错误。必要外部集成验证与假资源测试分开，不为本次 Markdown 修改新增测试。
- 先假资源检查状态与失败，再单节点实机、全量构建及开发评测；真实模型与数据库操作遵循资源/费用边界。独立 20 题调参前冻结隔离，正式仍是 16 道有据至少 13 道严格通过、4 道边界全部通过。
- 本节尚无可运行的新 CLI/API，不把拟入口写成已验证命令。每个工作单元交付时补实际命令、报告、用户验收状态；不得用本次计划更新标记 T04～T07 完成。

## 2. 任务清单

任务 ID 保留原 T01～T09。T01、T02a、T03 已部分推进，T04～T07 仅有文件骨架，T08 未启用，T09 尚未完成。下述验收条件是目标，不能当作已经通过的结果。

### T01 环境与资源核查

- 输入：架构第 2、3、9 节，现有模型路径、Windows 与虚拟机状态。
- 范围：只读核查 Python、模型文件、磁盘和内存，记录服务版本、挂载、端口、认证条件及项目专用命名。服务未启动时记录事实及用户启动步骤，不把“未连接”写成“兼容失败”。
- 产出：后续写入 docs/environment.md 与 data/reports/ 下的空间基线记录；列出 T02 所需条件。
- 用户验收：在 Windows 和虚拟机核对记录，区分实测值与旧截图；项目、共享缓存、模型及虚拟磁盘有基线，既有占用与新增占用分开。
- 通过标准：T02 的路径、服务访问条件和空间估算可核对；缺少凭据或未启动服务明确列出，不展示密钥。不改培训数据或其他服务。
- 失败处理：缺少的资料由用户补齐；需要启动共享服务时由用户操作或明确授权，不自动启动或修改。
- 独立验收题：在后续调参前安排用户准备并冻结 20 道独立题（16 有据、4 边界），记录冻结时间与内容指纹；题目及参考答案不进入开发调参上下文。尚未准备好不得声称已经冻结。

### T02 最小运行验证

前置：T02a 需要本机路径和安装空间条件；T02b～T02e 分别需要 T01 对应的模型、资源、网络或服务条件，以及可用的配置/日志基础。所需共享服务由用户启动或已明确授权。验证用集合使用项目专用前缀，不操作培训集合。按以下子任务分别推进：

| 子任务 | 输入与范围 | 产出 | 用户验收与通过标准 |
|---|---|---|---|
| T02a 独立环境 | Python 候选版本、必要依赖、空间基线；先估算，再在 D 盘建立环境 | 最小依赖声明、实际版本及安装记录 | 必要模块可导入，缓存位置可核对，无模型自动下载；记录新增字节数 |
| T02b BGE 编码 | 既有 BGE-M3、少量中文和代码片段 | 可重跑的验证入口与资源记录 | query/document 编码路径明确，dense 为 1024 维且数值有效，sparse 形状有效；记录模型文件标识、冷/热耗时、峰值内存 |
| T02c 重排与共存 | 既有 reranker、少量问题与候选 | 分数、输入长度与资源记录 | 单模型及两模型共存均有结果或明确失败证据；无持续换页、崩溃等阻碍演示的问题，用户确认可接受 |
| T02d Milvus | 已运行的 v2.4.11、候选 SDK、少量向量 | 独立验证集合及兼容性记录 | 插入、稠密查询、稀疏查询和融合可复现；记录实际 schema、索引参数、版本及资源占用 |
| T02e Qwen 小样本 | 用户配置的 API 凭据、账户地域、当前计价 | 少量生成结果、token 与费用记录 | 实际模型可调用，超时和错误有记录，输入输出上限与重试次数受控；先核对费用再安排批量评测 |

验证入口放本项目的 scripts/；模型/数据库适配逻辑放 app/infra/，验证入口调用适配器，避免复制两套客户端逻辑。验证报告集中到 data/reports/，不把单个验证脚本通过当作完整应用通过。

T02e 初始采样费用上限设为 1 元，计入当月 100 元总额；调用前按当前价格和最大输入输出估算，费用无法估计时不调用。不得依赖“可能有免费额度”。该小额限制是实施保护值，不是单次价格预测。

T02 总体通过标准：核心编码、Milvus、Qwen 可工作，依赖组合可锁定，并有模型共存与重排可用性结论。延迟目标根据此轮样本提出，由用户确认后记录；不预设响应秒数。若共存失败，先提交保留 CPU 路线的资源调整或关闭默认重排等具体方案供用户确认；必要时修订架构后再继续。不得把未完成验证标成通过。

### T03 应用基础

- 输入：T02a 的基础环境与 T01 已知路径；基础部分可先实施，外部服务相关部分以对应 T02 验证结果为依据。
- T03a 配置与运行入口：建立 app/api/、app/shared/ 所需最小文件，独立依赖锁定记录、.env.example、.gitignore；敏感值用占位符，模型路径缺失明确失败。
- T03a 收尾：保留已有入口，统一配置来源、优先级和字段；按 2026-11-18 用户最新决定使用固定根目录 .env + os.getenv，移除 Settings，由启动阶段显式加载环境，模块导入不加载。验收进程变量覆盖、跨工作目录读取、错误配置提示和 PyCharm 解释器绑定。
- T03b 拆为以下子任务，每次只选一个；T03a 收尾与 T03b-1 可作为一次边界明确的修复任务：

| 子任务 | 输入与产出 | 验收标准 |
|---|---|---|
| T03b-1 配置与日志统一 | 根目录 .env、os.getenv、logger.py → 明确配置字段及启动初始化入口 | 导入模块不自行初始化文件日志；启动无重复输出，级别/文件开关生效，日志轮转和保留可核对，不记录凭据 |
| T03b-2 节点与步骤追踪 | 统一 logger → tracing.py | 同步/异步函数均在真实完成后记录耗时，request_id/build_id 可追踪，异常记录后继续抛出 |
| T03b-3 提示词加载 | prompts 目录 → load_prompt.py | 文件缺失、必要变量缺失有清晰错误；限制模板路径，代码花括号和传入内容不会被重复当模板解析；答案提示词内容在 T07 完善 |
| T03b-4 公共工具与运行保护基础 | 配置/日志 → 路径、指纹、统一错误、用量记录与受限执行基础 | 路径越界拒绝，Git blob 与普通哈希口径明确；费用预留/核销和失败用量有检查；仅实现当前任务需要的通用能力 |
| T03b-5 外部能力接入与就绪 | T01 条件及上述基础 → infra/providers、模型/存储适配器、生命周期管理 | 分别结合 T02b～e 验证，不重复建客户端；必需与可选依赖分开，实际就绪检查替代固定 503；完整活动索引就绪在 T05 后验收 |

- 外部服务 SDK、异常及返回值转换集中在 infra；业务通过项目数据结构调用。全量历史、业务归档和页面/SSE 不隐含在本任务中。
- 产出：可启动的应用基础，实际启动命令与必要检查。
- 用户验收：/health 不加载或下载模型、不调用付费 API；索引尚未建立时 /ready 明确未就绪；必需与可选依赖状态分开；日志不含凭据。
- 通过标准：缺配置、模型路径错误、预算不足、API 超时均可解释；计费预留与核销覆盖失败/未知用量，重试有界。技术错误不伪装成资料不足。
- 失败处理：只修本任务范围，不绕过预算或就绪检查进入完整问答。

### T04 语料解析与切块

详细编码顺序、路径和节点任务卡见 1.3 节 I01～I03；先定义业务结构/入库状态，再逐个业务服务与配对节点实现。

- 输入：corpus/manifest.json、固定提交的 10 篇中文教程与 64 个示例、许可证。
- T04a 解析：校验清单、路径边界与内容哈希；解析标题、段落、提示块和代码包含指令，追踪代码选行与原始文件行号。
- T04b 切块：采用实际 tokenizer 检查长度，处理长代码与关联片段；生成稳定 ID、内容指纹、标题路径、版本和来源。
- T04c 入库状态与前半段节点：定义构建 ID、输入、产物引用和错误信息；实现清单校验、解析、切块节点，分别调用业务服务并返回状态更新。以小样本检查状态衔接和失败传播，不声称完整建库已完成。
- 产出：app/rag/ingest/ 对应模块、app/process/ingest/state.py 及前半段节点、data/index/ 下的片段与解析记录。
- 用户验收：抽查 Q05、Q11、Q16 对应材料及至少一段包含指令；片段可回到原始文件核对，选行无遗漏和越界。图片链接只保留为来源信息，不宣称已理解图片。
- 通过标准：相同输入与处理版本重复生成结果稳定；超长输入处理可追踪；缺文件或哈希错误明确失败；evaluation/ 不入库。
- 失败处理：定位原件、指令或切块规则，不通过静默跳过重要正文来完成导入。

### T05 编码与版本化建库

详细路径和任务卡见 1.3 节 I04～I07。写入、验证、激活分别使用 write_index_service.py、validate_index_service.py、activate_index_service.py；原 index_service.py 占位待实施时迁移移除，禁止三节点共用一个业务文件。

- 输入：T04 片段、T02 模型与 Milvus 兼容配置。
- T05a 构建：实现编码批处理与 Milvus 写入，新构建使用独立集合；保留 chunks.jsonl、index-meta.json 等审计产物。
- T05b 激活：验证数量、维度、来源和查询后切换活动版本；检查 schema 与模型元数据，保证失败后原活动版本仍可使用。
- T05c 完整入库图与 CLI：连接编码、写入、验证、激活节点，完成 main_graph.py 与 scripts/build_index.py；验收小样本全链路、完整固定语料构建及失败不激活。节点调用业务文件，业务通过 infra 访问模型和存储。
- 产出：app/infra/storage/ 与入库业务、完整入库状态/节点/图、可复现建库入口及活动版本记录。
- 用户验收：在专用测试构建中模拟中途失败；原活动索引仍可查，新索引验证通过后才激活；首次构建失败则保持未就绪。
- 通过标准：两次构建不会污染培训集合或产生无界重复数据，元数据足以重建；记录新增存储及构建耗时。
- 失败处理：保留故障记录和上个有效版本；旧集合清理由明确的保留规则管理，不直接批量删除共享数据。

### T06 混合检索与重排

详细路径和任务卡见 1.3 节 Q02～Q04；先补候选结构、问答状态基础字段和 query 编码门面。

- 输入：T05 活动索引、20 道开发诊断题；独立验收题已冻结且隔离。
- T06a 召回：实现 dense/sparse 检索、RRF 融合、去重及证据追踪，先验证结果与来源。
- T06b 重排与比较：加入开关和输入长度控制，对比稠密、混合、混合加重排；固定题集和索引版本，记录候选覆盖、最终证据覆盖、耗时及内存。
- 产出：app/rag/query/ 对应模块、开发检索报告及初始参数记录。
- 用户验收：逐步查看 Q05、Q11、Q16 的候选和最终证据；检查多证据问题是否覆盖必要条件，确认重排的收益和代价。
- 通过标准：代表问题的必要证据进入拟交给模型的上下文，20 道题有完整诊断记录；无召回与技术故障能区分。用户据报告确认默认重排开关与延迟目标。
- 失败处理：只用开发题定位解析、切块、召回或排序问题；不使用独立题调阈值，不将高相似度当作答案存在的保证。

### T07 LangGraph 问答与非流式 API

详细路径和任务卡见 1.3 节 Q01、Q05～Q07 及连接文件表；整图运行顺序仍为 Q01～Q07。

- 输入：T06 检索服务、Qwen 适配、业务边界和结构化返回约定。
- T07a 图与状态：连接输入/版本判断、检索、证据打包、生成、引用校验及结果分支；状态不含密钥。
- T07b API 与失败行为：实现 POST /query，提供 status、answer、citations、knowledge_version、request_id；限制并发，避免 CPU 同步推理阻塞异步事件循环。
- T07c 开发评测：20 道诊断题逐题评分；同一生成模型及可比参数比较直接回答和 RAG，记录正确性、证据命中、引用支持、边界、延迟与费用。
- 产出：app/process/、app/resources/prompts/、查询 API、开发评测记录和演示步骤。
- 用户验收：Q05、Q11、Q16 按既有评分说明严格通过；三道开发边界题行为符合预期；20 道题均有评分与失败分析，用户判断是否可进入交付准备。
- 通过标准：核心引用来自实际提供的证据，服务端生成来源信息；模拟非法引用、API 超时和 Milvus 故障可得到明确处理；有据回答、澄清、资料不足与技术失败可区分。
- 失败处理：保留问题、证据和评分，按模块定位修复；有据题存在核心错误时不能只靠前端演示掩盖。开发题结果不能替代阶段 5 的独立验收。
- “核心问答通过”指本任务的功能、代表题、开发边界和用户验收通过，不表示正式验收已通过。

### T08 可选页面与 SSE

前置：T07 已通过，用户选择实施；否则记录“未启用”，直接进入 T09。

- T08a 任务与事件：实现 POST /query/jobs 与 GET /query/jobs/{request_id}/events，任务有容量和有效期限制，支持存活期间重连回放；复用同一问答服务。
- T08b 页面：用 HTML 与 JavaScript 展示问题、进度、答案和引用；收到 done 后关闭连接。
- 产出：app/web/、任务生命周期与事件接口、可选演示说明。
- 用户验收：比较 /query 与 SSE 结果；模拟断连重连、任务过期、服务重启和生成失败，检查事件与实际 API 调用次数。
- 通过标准：重连不重复生成、不重复计费；失效任务明确提示；result 只发布校验后的答案；不把生成后分段显示称为实时 token 流。
- 失败处理：保留非流式核心能力；未通过的可选功能不标记完成，也不阻碍已约定的核心交付。
- 历史与业务归档不隐含在 T08 中；如选择启用，先明确各自输入、存储、失败行为、空间和验收任务。

### T09 交付准备

- 输入：已通过的核心任务，用户选定的可选功能状态，依赖版本与测量记录。
- 范围：整理环境配置、建库、启动、停止、重启、常见故障排查和演示步骤；核对待验证事项。
- 产出：更新 README.md，新增 docs/runbook.md，整理开发评测及资源费用报告；形成阶段 5 的执行清单。
- 用户验收：能找到真实入口、命令、环境变量与示例；已验证步骤和待验证步骤分开，功能启用状态与文档一致。
- 通过标准：依赖和索引版本可追溯，独立题已冻结且未用于调参，新增空间与费用有台账；用户确认可进入阶段 5。
- 失败处理：补足缺失的复现信息或回到对应任务修复；不把计划描述当作实测记录。

## 3. 阶段 5 交接与正式验收

以下是后续验收安排，本轮不运行：

1. 用户明确进入阶段 5 后，按 runbook 验证从配置、建库到问答的完整流程，检查重启加载和构建失败恢复。
2. 使用冻结的 20 道独立题：16 道有据题至少 13 道严格通过，4 道边界题全部通过；评分沿用 evaluation/sample-review.md。不把开发集的 17/3 分布当作正式集分布。
3. 固定实际模型、参数、语料、索引及提示词版本，比较直接回答与 RAG。直接回答的正确性与 RAG 的证据/引用指标分别记录，不凭空给直接回答计算检索命中。
4. 至少演示有据回答与澄清/资料不足；若启用页面/SSE，追加一致性、重连和任务失效验证。
5. 核对新增占用不超过 10 GB、当月服务器与模型 API 合计不超过 100 元。以字节记录并同时展示 GiB；虚拟机内部增长与宿主机虚拟磁盘增长不重复计数。
6. 记录最终通过、失败和限制。验收失败后可修复并复测，但一旦用失败题指导调参，应披露该题集已用于修复；再次声称独立验收需准备新的隔离题集。

## 4. 目录用途与后续产物

| 位置 | 用途 | 当前阶段 |
|---|---|---|
| README.md | 阅读入口与状态 | 已有，阶段 3 更新 |
| requirements.md | 业务范围、资源与质量标准 | 已有 |
| architecture.md | 技术、模块、流程与未验证事项 | 已有 |
| plan.md | 执行顺序、任务卡、验收与记录 | 阶段 3 新增 |
| AGENTS.md | PyCharm Codex 的协作与操作规则 | 阶段 3 新增 |
| corpus/ | 固定语料、配套示例、清单和许可证 | 已有，不能作为运行产物目录 |
| evaluation/ | 开发诊断题、评分及后续独立验收材料 | 已有，禁止入库 |
| docs/ | 调研及后续环境、复现说明 | 已有 |
| app/ | API、编排、RAG、基础设施及可选页面 | 骨架已建；仅配置、日志、应用入口和健康接口有部分实现 |
| scripts/ | 可重跑的验证及辅助入口 | run_api 已有；check_environment 和 build_index 为占位 |
| tests/ | 有实际验证价值的模块与集成测试 | 本轮新增 test_config_logging.py；其他模块/业务测试仍待对应任务 |
| data/index/ | 片段、构建元数据与活动版本清单 | 阶段 4 创建 |
| data/reports/ | 资源、费用、性能和运行报告 | 阶段 4 创建 |
| logs/ | 限量保留的运行日志 | 阶段 4 创建 |

模型继续引用已有 D 盘路径，不复制到项目。基础骨架已经存在，后续直接补齐对应文件，避免重复创建；空间、缓存及临时产物继续在 T01/T02 记录。

## 5. 完成记录

### 2026-11-17 原始记录（保留）

以下保留当时记录，不代表最新状态；其中“Git 未提交”由后续追加记录更新。

阶段 4 已完成基础搭建。T01 的本机环境核查、T02a 的基础依赖以及 T03a 的配置和最小入口已做初步检查，待用户在 PyCharm 验收。模型及服务兼容性、完整资源台账和后续任务仍待执行。T08 未启用。

2026-11-17：复用 Python 3.12.7，uv 锁文件检查通过。验证了配置覆盖、最小 LangGraph、/health 与 /ready。详见 [环境说明](docs/environment.md)。Git 未提交。

每完成一个子任务，在本节追加以下记录，记录前确认真实结果：

- 任务 ID 与日期：
- 本次输入、范围及修改文件：
- 实际运行命令与环境：
- 自动检查结果：
- 用户在 PyCharm 的检查结果：
- 耗时、内存、新增空间与费用（适用时）：
- 未验证事项与后续处理：
- 用户确认状态：
- Git 提交状态与提交 ID（未提交写明，不自动提交）：
- 下一任务是否得到用户确认：

历史下一步安排：先在 PyCharm 验收基础骨架，再继续 T01 尚缺的虚拟机资源及服务连接条件核查。

### 2026-11-18 只读核对与计划更新

- 本轮授权：只更新 plan.md 的进度、执行顺序和任务拆分，保留历史；不安装依赖、不运行服务或模型、不修改代码。
- 文件事实：基础环境和六层骨架存在，配置和健康入口有实现；模型/存储、入库/问答图及业务文件主要是占位。
- 当前问题：logger.py 同时存在 configure_logging(settings) 和导入时调用的 init_logger()；须统一。load_prompt.py、tracing.py 等尚待实现。
- 历史验证：environment.md 记录过 Python 3.12.7、锁文件、配置覆盖、最小 LangGraph 和健康接口检查。本轮未复跑，当前 PyCharm 绑定与用户验收仍待记录。
- Git 事实：核对时已有提交 b0225e6，时间 2026-11-17 16:45:07 +08:00，说明“chore: 初始化项目基础骨架与文档”；本次编辑前工作树未显示未提交变更。提交存在不代表用户已验收。
- 当前进度：第 4 步骨架已建，第 5～6 步部分实现；第 1～3 步仍有核查/验收余项，第 7～9 步功能未实现，第 10 步贯穿全程。
- 用户确认状态：已授权本次计划更新；不据此标记任何运行任务验收通过。
- 下一开发任务：验收现有骨架后，实施 T03a 配置收尾和 T03b-1 日志统一；之后按第 1.2 节推进。
- 本次文档更新不自动提交 Git，待用户确认。

### 2026-11-18 T03a 配置收尾 + T03b-1 日志统一（首次实现，配置方案已被下方修订取代）

- 授权与范围：用户明确授权本次实现；仅配置、日志、启动衔接、测试及交接文档。不扩展提示词、模型、入库或问答业务。用户要求优先于旧文档中桌面端只做文档的默认分工。
- 实施前 Git：分支 main，HEAD `b0225e6`；仅 plan.md 已有未提交修改，本轮保留原有更新与历史记录。
- 修改文件：app/shared/config/settings.py、runtime_config.py；app/shared/runtime/logger.py；app/main.py；scripts/run_api.py；.env.example；tests/test_config_logging.py；docs/environment.md；plan.md。未改本地 .env、依赖声明或锁文件。
- 实现：Settings 统一读取进程环境与根目录 .env，RuntimeConfig 只定义字段。删除 logger 中重复的 dotenv/os.getenv、init_logger 导入初始化和 inspect.stack 修补；唯一应用初始化位置是 FastAPI lifespan，结束时关闭 sink。保留既有同步日志装饰器，不提前实施 T03b-2。
- 日志契约：统一 LOG_LEVEL；LOG_FILE_ENABLE 默认 false；文件为 logs/app.log；LOG_ROTATION_BYTES 默认 5000000、LOG_RETENTION_DAYS 默认 7，校验正整数和保留天数上限。轮转时按修改时间清理匹配文件；非定时清理、不自动删旧命名文件。Uvicorn 控制台使用同一级别；文件仅收集应用日志。
- 自动检查：使用项目现有 Python 3.12.7 / .venv，无安装。临时副本先通过 12 项测试；写回目标项目后执行 `.\.venv\Scripts\python.exe -B -m unittest discover -s tests -p test_config_logging.py -v`，目标项目 12 项全部通过。涵盖配置覆盖、跨工作目录、非法字段/值与隐藏输入、导入与工厂无文件副作用、五档级别、开关、重复初始化、中文/调用位置、异常不展开局部值、真实轮转/过期保留、生命周期释放句柄，以及真实 Uvicorn INFO/ERROR 启动和 HTTP 200/503。
- 敏感信息：仅核对本地 .env 字段名，未输出凭据或改写 .env；日志禁用诊断变量展开，但不声称可自动脱敏调用方主动记录的所有内容。
- PyCharm 检查：尚未由用户执行/确认；具体步骤见 docs/environment.md 的本轮验收节。模型路径有效性和外部服务就绪仍待其对应任务，不属于本轮已验证结果。
- 资源与费用：未安装依赖、下载模型或调用付费 API；API 费用 0 元。测试日志放独立临时目录并清理自身产物，未修改真实日志；本轮未做完整资源基线或峰值内存测量。
- 用户确认状态：实现和自动检查完成，待用户 PyCharm 验收；不标记整个 T03 或 T02a 已验收通过。
- Git 提交状态：未提交，未推送；HEAD 仍为 b0225e6。
- 下一任务：未获用户确认，不启动任何下一任务。

### 2026-11-18 用户指定修订：参考日志格式 + .env / os.getenv

- 用户最新决定：采用参考 logger 的展示与输出配置能力，不保留 Settings；明确要求更新计划、验收并交付可运行测试。取代上条记录的 Settings 方案，不视为开始 T03b-2。
- 修改文件：app/shared/config/settings.py、runtime_config.py、app/shared/runtime/logger.py、app/main.py、scripts/run_api.py、.env.example、tests/test_config_logging.py、docs/environment.md、plan.md；新增 scripts/check_logging.py。保留既有未提交修改，培训参考仓库只读。
- 配置：移除 Settings/get_settings/RuntimeConfig；settings.py 只定位/显式加载根 .env，override=False，入口和日志初始化使用 os.getenv 与小型校验函数。原模型/存储字段继续保留在 .env 示例，配置业务待对应任务；本次未改真实 .env、依赖声明或锁。
- 日志：唯一函数 init_logger()，HTTP 在 lifespan 调用，演示 CLI 在 main 调用；导入不初始化。独立控制台/文件开关与级别，彩色 stdout、UTF-8 日期日志、每日/大小任一触发轮转、按天保留、enqueue=True；正常退出 complete 后 remove。保留 LOG_LEVEL 和 LOG_RETENTION_DAYS 的兼容读取；新示例使用 LOG_FILE_RETENTION=7 days。
- 边界：不使用 inspect.stack 修补，不展开异常局部值；不实现异步节点装饰器。日期日志保留策略可能清理同模式历史日期文件，旧 app.log 模式不迁移；说明见环境文档。
- 验证：项目 Python 3.12.7；先在临时副本验证，再写回真实项目执行 `.\.venv\Scripts\python.exe -B -m unittest discover -s tests -p test_config_logging.py -v`，12 项全部通过。覆盖配置、输出、真实大小轮转/过期清理、模拟午夜、队列完整写入与句柄释放、演示代码和实际 HTTP 200/503；未修改系统时钟或真实日志。
- 可运行测试：`scripts.check_logging` 演示全部五档日志和预期异常，支持 PyCharm 模块运行；自动回归在 tests/test_config_logging.py。PyCharm 配置、.env 样例与验收步骤已更新至 docs/environment.md 最新节。
- 资源：未安装包、下载模型或连接外部服务，付费 API 调用 0；测试自身临时文件结束清理，完整资源基线与峰值内存仍未测量。
- 状态：代码与自动检查完成，等待用户 PyCharm 验收；未提交/推送 Git，HEAD 保持 b0225e6；未授权开始下一任务。

### 2026-11-18 用户验收确认与配置原则固化

- 用户明确回复“确认验收”，确认本次 T03a 配置收尾 + T03b-1 日志统一（.env + os.getenv 版本）通过；不扩大为 T01、T02 或整个 T03 已通过。此前“待验收”记录保留为当时状态，以本条及进度表为最新状态。
- 按用户要求在 AGENTS.md 提炼配置原则：采用 12-Factor App Config，将部署变化参数移出代码；区分本地 Dotenv 与生产环境注入，明确当前来源优先级、必要校验、敏感值保护及不重新引入 Settings 对象的项目取舍。命令行覆盖仅为将来可选层，不宣称已实现。
- 本次仅修改 AGENTS.md 与 plan.md；核对文档差异，未修改应用代码或重复运行测试。前轮 12 项自动检查通过的结果保留。
- Git 状态：尚未提交、未推送；本轮不执行 Git 提交。
- 下一任务：用户尚未确认开始，不进入 T03b-2 或其他任务。


### 2026-11-18 T03b-2 节点与步骤追踪

- 授权：本轮仅实现 T03b-2；已阅读六份约定文档并核对代码/Git。保留此前未提交配置、日志、文档与测试改动。培训参考仓库不写入。
- 输入与修改：基于已验收统一 logger；实现 app/shared/runtime/tracing.py，logger.py 保留兼容导出；新增 scripts/check_tracing.py、tests/test_tracing.py；更新 docs/environment.md 和本计划，另修正 tests/test_config_logging.py 中 HTTP 子进程的配置隔离，共 7 个文件。
- 实现：同步/async def 双路径、perf_counter 完成计时、request_id/build_id 解析与 ContextVar 继承恢复；异常及取消记录类型/耗时后原样抛出。不记录业务输入输出、异常文本或堆栈；不生成 ID，不自动为普通业务日志附加字段。生成器明确拒绝。
- 自动检查：使用目标项目现有 Python 3.12.7 / .venv，执行 `python -B -m unittest discover -s tests -p test_*.py -v`，追踪 8 项及配置日志 12 项共 20 项全部通过（含真实本地 HTTP 200/503）。`python -B -m scripts.check_tracing` 实际运行成功，结束码 0；验证时文件输出关闭。临时副本先行通过 8 项追踪测试。验收命令与演示见 docs/environment.md 的 T03b-2 节。
- 回归修正：首次真实项目运行 19/20 通过，原有 HTTP ERROR 级别测试受到真实 .env 分项控制台级别影响；为测试子进程显式设置 LOG_CONSOLE_ENABLE/LOG_CONSOLE_LEVEL，未修改生产日志配置或 .env。
- 用户 PyCharm 验收：待用户运行/确认，未标记通过。
- 范围与资源：未修改 .env、依赖与锁文件、提示词、模型、入库或问答业务；不安装依赖、不下载模型、不连接外部服务或调用付费 API。临时准备文件位于系统临时目录，未暂存到培训参考仓库；未测量完整空间基线/峰值内存。
- Git：实施前 HEAD b0225e6，已有 9 个已跟踪修改和 2 个未跟踪文件；本轮不提交、不推送。读取时使用单次 safe.directory 参数，没有改全局 Git 配置。
- 下一任务：T03b-3 及其他任务未获开始确认，不启动。

### 2026-11-19 GitHub 推送认证失败排查

- 状态：推送被 GitHub 认证拒绝，尚未修复或验证推送成功；不改变业务任务验收状态。
- 证据：origin 的 fetch/push 地址均为 https://github.com/Evi86266/fastapi-rag，当前分支 main，未配置上游；工作区仍有已修改及未跟踪文件，push 不会包含未提交内容。
- 第一次失败：Invalid username or token，表示提交的身份凭据无效。GitHub HTTPS Git 操作不接受账户密码；仅凭日志不能判断是使用了密码、token 过期/撤销、用户名不匹配还是其他凭据问题。
- 第二次失败：Authentication request was cancelled 后出现 No anonymous write access，说明认证流程取消后没有可用身份，匿名用户不能推送。
- 本机配置 credential.helper=manager；但 PyCharm 日志中的 -c credential.helper= 会在该次命令清空 helper 列表，因此不能假定本机 Git Credential Manager 已缓存的登录会被此次 IDE 推送使用。需要检查 IDE 自己提供的认证。
- 恢复步骤：在 PyCharm 的 GitHub 账户设置中重新登录有该仓库写权限的账号，完成浏览器授权且不要取消；如使用 token，需有效且授权目标仓库，细粒度 token 的 Contents 权限应为 Read and write。不要输入 GitHub 账户密码，不将 token 写入远程 URL 或文档。
- 可选排查路径：在用户自己的终端进入本仓库，运行 git push -u origin main（不添加 -c credential.helper=），完成 Git Credential Manager 登录。执行前核对准备推送的提交；若终端成功而 IDE 失败，继续检查 IDE 认证配置。
- 验收：认证完成后推送成功，git branch -vv 显示 main 跟踪 origin/main，并在 GitHub 核对提交。未提交文件需另行审阅和提交，不会随本次 push 上传。
- 本轮仅检查和更新计划，未读取 token、修改凭据、提交或推送。检查进程曾遇到仓库所有权保护，使用单次 safe.directory 参数进行只读核查，没有修改全局配置；此问题与用户日志中的远程认证失败不同。
- 官方参考：https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens
### 2026-11-19 T03b-3 提示词加载

- 用户确认：T03b-2 已验收；本轮仅授权 T03b-3。历史待验收状态由本条更新。
- 当前代码：load_prompt.py 原为占位，answer.prompt 留待 T07；本次实现纯本地加载，不接入模型、入库或问答业务。
- 修改 6 文件：app/shared/runtime/load_prompt.py；新增 app/resources/prompts/loading_demo.prompt、scripts/check_prompts.py、tests/test_load_prompt.py；更新 docs/environment.md 和 plan.md。保留既有未提交改动。
- 契约：固定 prompts 根目录，受限相对 .prompt 名称，resolve 后检查边界；UTF-8 读取；string.Template 严格校验变量和语法，单次替换；不缓存、不读取 .env、不初始化日志。模板中的普通花括号原样保留，字面美元符写 $$；变量值中的美元符与花括号不用转义。
- 自动检查：使用项目现有 .venv 执行 `python -B -m unittest discover -s tests -p test_*.py -v`，配置/日志 12 项、追踪 8 项、提示词 8 项，共 28 项全部通过；`python -B -m scripts.check_prompts` 演示通过，退出码 0。链接越界通过模拟 resolve 结果验证，未创建真实 Windows 符号链接。PyCharm 步骤见 docs/environment.md 的 T03b-3 节。
- 用户 PyCharm 验收：待运行/确认，未标记通过。答案提示词完善仍在 T07。
- Git 基线：main 跟踪 origin/main，HEAD f4397a7；已有 AGENTS.md、docs/environment.md、plan.md 修改及 4 个未跟踪的日志/追踪脚本和测试。本轮不提交、不推送，不改变全局 safe.directory。
- 资源：不安装依赖、不下载模型、不连接外部服务，API 调用费用 0；测试临时文件在项目 .cache/tmp 内隔离并清理；实现准备文件暂放系统临时目录，未写入培训参考仓库。未做完整空间基线或峰值内存测量。
- 下一任务：未授权，不启动。
### 2026-11-19 T03b-4 公共工具与运行保护基础

- 用户确认：T03b-3 已验收；本轮明确授权实施 T03b-4。仅补公共基础，不扩展模型、入库或问答业务，不启动下一任务。
- 阅读与基线：已阅读 AGENTS.md、README.md、requirements.md、architecture.md、plan.md、docs/environment.md 并核对代码。核对期间用户提交使 HEAD 从 f4397a7 更新为 bb154c4（加载提示词），main 跟踪 origin/main；以 bb154c4 为实施基线。既有 AGENTS.md、环境文档、计划与未跟踪的演示/测试文件均保留。
- 修改 9 文件：app/shared/utils/paths.py、hashing.py；app/shared/errors.py、metrics.py；app/shared/runtime/resources.py；新增 scripts/check_runtime_foundation.py、tests/test_runtime_foundation.py；更新 docs/environment.md 与 plan.md。
- 实现：受限相对路径及解析后边界、原始字节 SHA-256/Git blob SHA-1、稳定技术错误码、线程安全 Decimal 内存预算预留/核销/未知费用对账、受限同步线程执行及 ContextVar 传递。满容量立即拒绝；取消或超时不提前释放仍在运行的线程容量；显式关闭等待在途任务。
- 边界：台账不持久化、不自动按月滚动，不代表真实月费保护已上线；未来付费接入必须完成恢复与对账。线程不能被取消强杀，无自动重试；不新增未被启动层消费的环境变量。路径检查不防御本地并发替换链接，测试模拟链接解析越界。保留既有提示词、配置和 API 契约。
- 自动验证：项目现有 .venv / Python 3.12；临时副本运行 `python -B -m unittest discover -s tests -p 'test_*.py' -v`，44 项全部通过（已有 28 + 本轮 16，含实际本地 HTTP 200/503）；`python -B -m scripts.check_runtime_foundation` 退出码 0。Git blob 使用真实 git hash-object --stdin 对照。实际项目写回后的检查以追加结果为准。
- 资源与费用：无安装、模型下载、数据库连接或收费 API 调用，API 费用 0。临时副本在系统临时目录准备，未写培训参考仓库；未测完整项目空间与峰值内存，不把本轮结果当作 T01 验收。
- PyCharm 步骤：见 docs/environment.md 的 T03b-4 节，专项 16 项、演示脚本、完整回归 44 项。
- 用户确认状态：实现和自动检查完成，待用户 PyCharm 验收，不标记 T03b-4 验收通过。
- Git：本轮未提交、未推送；下一任务未授权，不启动。

- 写回后实测：实际项目现有 .venv 中完整 44 项测试全部通过，演示脚本退出码 0；仍待用户 PyCharm 验收，未提交 Git。


### 2026-11-19 T03b-5 第一部分：生命周期与分项就绪（外部配置待用户回复）

- 用户确认：T03b-4 已验收且已提交 Git。已核对 HEAD `331c6cc 公共工具与运行保护基础`，main 跟踪 origin/main；这不代表未跟踪的历史测试/脚本已被提交。
- 本次授权：只做 T03b-5；用户后续指示“先修改其他，保留需要回复的部分，等我操作后再修改模型和数据库的部分”。因此真实模型、数据库、API 配置及适配器继续暂缓，不将本部分等同整项完成。
- 阅读与基线：已阅读 AGENTS.md、README.md、requirements.md、architecture.md、本计划和 docs/environment.md，并核对代码、依赖、现有模型目录及 Git。已有 AGENTS.md、环境文档和计划的修改，以及历史演示/测试未跟踪文件均保留。培训仓库只读。
- 修改 8 文件：app/infra/providers.py、app/api/dependencies.py、app/api/routes/health.py、app/main.py；新增 scripts/check_readiness.py、tests/test_providers.py；更新 docs/environment.md、本计划。
- 实现：可注入的同步资源生命周期契约，单应用资源拥有者、后台受限初始化、只读探测与安全状态快照，部分失败和取消后清理。/health 保持无外部副作用；/ready 按必需依赖状态选择 200/503，默认明确等待外部配置和 T05 活动索引，关闭的可选依赖不阻塞。
- 暂缓：未改 .env/.env.example、模型/数据库配置或适配器、费用模块、依赖及锁文件。未安装 SDK、下载/加载模型、连接虚拟机服务或调用 Qwen，费用 0。真实适配、费用持久化/未知账单恢复及 T02b～e 验证尚未完成；完整活动索引仍在 T05 后验收。
- 自动检查：使用项目现有 Python 3.12.7 / .venv，在临时副本运行 `python -B -m unittest discover -s tests -p 'test_*.py' -v`，56 项全部通过（已有 44 + 新增 12）；`python -B -m scripts.check_readiness` 输出默认 pending/disabled 分项并退出 0。模拟测试不证明真实 BGE/Milvus/Qwen 可用；实际项目写回后结果追加于本节。
- 资源：本次没有新增模型/依赖，准备文件位于系统临时目录，未在培训仓库暂存；本轮未测量完整资源基线或模型峰值内存，不标记 T01 完成。
- PyCharm 验收：见 docs/environment.md 的 T03b-5 第一部分，专项 12 项、完整 56 项、就绪演示与 HTTP 分项检查。
- 用户确认状态：本部分实现及隔离自动检查完成，等待用户 PyCharm 验收；T03b-5 仍进行中，等待外部配置。待回复清单集中在 docs/environment.md 本节末尾。
- Git：本轮未提交、未推送；不开始入库、问答或下一任务。用户操作并回复后继续同一 T03b-5 的外部接入。

- 写回后实测：在实际项目现有 .venv 运行完整 56 项测试全部通过；scripts.check_readiness 输出等待配置/活动索引及可选依赖关闭状态，退出码 0。本部分待用户 PyCharm 验收，外部接入仍待用户回复；未提交 Git。


### 2026-11-20 T03b-5 配置核对、字段修正与免费前置检查

- 用户已填写 Milvus/Qwen，授权检查其余设置并申请执行修改；另确认本月已有服务器/API 支出为 0。继续 T03b-5，不开始下一任务，不提交 Git。
- 核对实际 `.env`，发现生成字段采用 LLM_DEFAULT_MODEL、OPENAI_BASE_URL、OPENAI_API_KE；修正为 QWEN_MODEL、QWEN_BASE_URL、QWEN_API_KEY，保留原始值。模型路径存在，CPU/float32、重排关闭、历史和业务归档关闭符合设计。
- 补齐北京 qwen-flash 已核对的标准输入/输出单价、月预算 100 元、期初支出 0 元、采样预算 1 元、输入/输出上限 4096/128、超时 30 秒和零重试。参数由前置检查脚本消费；尚无真实生成适配器或持久费用保护，不据此发起付费请求。
- 修改：本地 .env、.env.example、scripts/check_external_config.py（新增）、scripts/check_readiness.py、app/infra/providers.py、tests/test_providers.py、docs/environment.md、plan.md。真实模型/数据库适配仍未实现；就绪原因改为 adapter_not_implemented，避免继续错误归因于等待用户配置。
- 准备验证：配置正常路径及缺 Key、带认证 URL、NaN 预算、重试越界、非法设备、过期账期六类失败场景均通过，错误输出不包含敏感输入。写回后的配置、免费传输检查和回归结果追加在下方。
- 状态：配置修正不代表 T03b-5 整项完成或用户已验收。后续仍需 SDK 兼容/资源安装核查、适配器接入、持久费用台账、T02b～e 实测；活动索引仍在 T05 后验收。用户历史支出已确认，不再以此为待回复事项。

- 写回实测：配置/传输检查结果 {"configuration": "valid", "invalid_fields": [], "models": {"BGE_M3_PATH": "files_present_not_loaded", "BGE_RERANKER_LARGE": "files_present_not_loaded"}, "estimated_single_call_max_cny": "0.0008064", "paid_call_performed": false, "readiness": "adapters_not_implemented", "transport": {"MILVUS_URL": "tcp_reachable", "QWEN_BASE_URL": "tls_reachable"}}；完整回归退出码 0（成功时为 56 项 OK）。未调用付费 API，未安装 SDK，未提交 Git。


### 2026-11-20 T03b-5 真实外部适配与就绪交付

- 授权：用户明确“继续完成 T03b-5”，沿用已确认本地模型、Milvus/Qwen 配置和本月期初支出 0；本轮不进入入库、检索或问答业务，不提交/推送 Git。
- 实现：BGE-M3 query/document 稠密/稀疏编码、本地可选重排、Milvus 独立 alias 连接与版本 RPC、Qwen 免费模型列表鉴权和有预算保护的非流式生成；Providers 统一后台初始化、受限执行、快照/故障状态和收尾。配置/SDK/供应商错误以受控 code 返回；API 请求不额外触发加载或生成。
- 费用：新增 SQLite 持久台账，跨线程/进程事务预留，成功按实际 token 和标准价格估算核销，失败/未知及崩溃 pending 保留并阻止新付费请求，重启不重置。月预算 100 元、采样累计 1 元，无自动重试；账期/预算策略变化须先对账，不自动迁移。
- 依赖：安装 CPU torch 2.6.0+cpu、FlagEmbedding 1.3.5、transformers 4.51.3、peft 0.15.2、sentence-transformers 3.4.1、PyMilvus 2.4.15；setuptools 80.9.0 修复 SDK 的 pkg_resources 导入兼容性。安装及缓存位于 D 盘项目，未下载/复制模型，未升级共享服务。pyproject 与 uv.lock 同步。
- 主要修改：app/infra/models/{embedding,reranker,qwen}.py、app/infra/storage/milvus.py、app/infra/providers.py；app/shared/config/model_config.py、errors.py、新增 usage_store.py；新增 scripts/check_external.py、tests/test_external_adapters.py；调整既有配置/Providers 测试隔离和检查脚本；.env.example、依赖文件、README、环境说明、本计划。保留既有用户未提交改动；真实密钥未写入代码/文档/日志。
- 实机 Milvus：实际版本 v2.4.11，独立连接、RPC 和关闭成功，无数据写入。Qwen 模型列表鉴权通过；唯一一次生成返回“连接成功”，14 输入/2 输出 token，标准价估算 0.0000051 元，预留上限 0.0008064 元，台账剩余 0.9999949 元、未决 0。最终供应商账单未人工对账，不能把估算当作账单实付。
- 模型：单独 BGE 启动 42.193s，query/document 都为 1024 维，稀疏词项数 8/14，小样本两次编码合计 2.128s。单独重排启动 38.863s，分数约 0.99484/0.0000763；该样本不代表检索效果验收。
- 共存：两模型同时加载并完成编码/重排，启动 43.292s，采样 RSS 峰值 3,406,176,256 字节（约 3.172 GiB），总计 48.929s，正常释放。此为 50ms 采样进程 RSS，非系统总内存/完整换页监控；PyCharm 交互体验仍由用户验收，默认重排保持关闭。
- 默认就绪：真实 embedding/milvus/qwen ready；reranker/history/archive disabled；active_index pending_t05_active_index，整体 not_ready 符合约定。停止后资源释放无错误。实机报告保存在 data/reports/external-*.json（被 Git 忽略）。
- 范围限制：Milvus 字段、索引和稠密/稀疏/融合查询的 T02d 完整兼容性、活动索引与业务入库在后续对应任务中验收。T03b-5 的连接/生命周期完成不代表 T01/T02/T03 全部任务通过。
- 验收交接：docs/environment.md 最新节提供 68 项回归、各组件/共存、可选一次付费和 HTTP 验收步骤。T03b-5 实现完成，自动/实机检查结果见本节及下方最终记录；用户尚未验收，未经确认不提交 Git、不开始下一任务。

- 最终写回验证：实际项目 68 项自动回归全部通过；真实资源生命周期的 ASGI HTTP 检查 /health=200、/ready=503，外部三项 ready、活动索引 pending，关闭成功。新增付费调用仍为 1 次。空间逻辑统计：{"project_logical_bytes": 3370529834, "project_gib": 3.1390505228191614, "baseline_bytes": 87550630, "growth_bytes": 3282979204, "growth_gib": 3.0575126446783543, "temporary_preparation_bytes": 334597, "shared_service_data_written": false}。文件逻辑大小可能重复计算硬链接，作为保守口径；未写数据库数据，既有模型/虚拟机基础占用单列。用户验收待确认，未提交 Git。


### 2026-11-20 T03b-5 模型门面与 ChatOpenAI 重构（待用户验收）

- 按用户示例提供 `LLMProvider.chat(model=None, json_mode=False)`、`embedding_model()`、`reranker_model()`、`embed_documents(texts)`，文件末尾为模块级 `llm_provider = LLMProvider()`；同步调用无需绑定其他对象，导入不加载配置/模型。
- 模型业务入口集中于 providers.py，三种适配器按需创建并与默认生命周期共享。BGE 的原编码/重排逻辑保留，仅增加模型获取与并发加载保护；文档向量输出为 dense_vecs/lexical_weights 字典。
- Qwen 生成改为真实 ChatOpenAI 客户端，普通/JSON 选项缓存并共享连接；既有 generate 检查入口委托到同一客户端。原持久费用台账复用，通过回调覆盖 invoke/ainvoke 的预留、核销与未知费用阻止，模型/输出上限仍受已核价配置约束。非流式范围不变。
- 修改范围：providers.py、models/{embedding,reranker,qwen}.py、两个相关测试文件、依赖及锁文件；环境说明与本计划同步。保留其他已有改动，不修改 .env、数据库或入库/问答代码。
- 依赖：已安装并锁定 langchain-openai 1.8.3（关联 langchain-core 1.8.4、openai 3.57.0），未下载模型。本轮未发起真实生成请求，未增加 API 费用。
- 验证：临时副本 76 项自动回归全部通过，新增覆盖普通/JSON 客户端复用、直接调用费用保护、异步成功/超时、关闭失效、模型单例及异步资源释放。使用假 HTTP/模型，不将隔离测试等同本次新 SDK 的实机生成验收。
- PyCharm：项目 .venv 解释器、项目根工作目录，运行 `python -B -m unittest discover -s tests -p 'test_*.py' -v`；预期 76 项 OK。模型门面构造与使用示例见 docs/environment.md 最新节。
- 状态：等待用户 PyCharm 验收；未提交/推送 Git，不开始下一任务。写回后验证结果追加如下。

- 写回后验证：实际项目 76 项自动回归全部通过；uv pip check 无依赖冲突；独立进程确认导入门面不创建适配器、不导入模型 SDK。项目逻辑大小 3485102406 字节（约 3.2458 GiB，含既有文件，硬链接可能重复计数），本次新增付费调用 0。待用户验收，未提交 Git。


## 2026-11-23 配置层清理（待用户验收）

- 删除无应用引用的 bailian_mcp_config、embedding_config、lm_config、milvus_config、mineru_config、minio_config、reranker_config 及其专用 common；删除无引用的 storage_config 空占位。删除的是应用配置代码，不涉及共享 MinIO 服务或数据。
- settings.py 删除旧 AppSettings、全局 settings 及导入时 load_dotenv；仅保留 PROJECT_ROOT 和显式 load_environment，固定根 .env、override=False、interpolate=False。
- model_config.py、runtime_config.py 已检查，保留实际调用的字段、URL、金额、模型路径、布尔、整数和日志级别校验，不引入配置对象或重复封装。
- 未变更环境字段、默认值、真实 .env 或 .env.example；未修改入库或问答业务，未连接真实模型/数据库或调用付费 API。
- 验证：完整自动回归通过（退出码 0）。PyCharm 使用项目 .venv，在项目根执行 `python -B -m unittest discover -s tests -p 'test_*.py' -v` 复核；重点检查导入无副作用、显式加载、进程变量优先及适配器回归。
- 用户尚未验收；不提交、不推送 Git，不开始下一任务。原有暂存区保持不动，已暂存的旧配置文件在工作区删除，待用户确认后统一处理提交。

## 2026-11-23 搭建顺序与节点计划细化（仅文档）

- 用户授权：只修改 plan.md，明确入库链/问答链一节点一业务文件，补工具、配置、结构、状态及连接文件路径与实现步骤。
- 调整：新增 1.3 节和 14 张节点任务卡；拆分原 index_service 的目标职责为三个独立业务文件；更新当前下一步及 T04～T07 交叉指引，保留历史记录和验收标准。
- 新增文件均仅为计划，未创建/删除/重命名代码；未修改 .env、其他文档、数据库、模型或 Git 暂存区；未提交/推送。
- 文档检查：核对七对入库/七对问答一一对应、完整路径、前置顺序、错误分支及状态与连接交付；保留既有完成记录。未运行应用测试或外部请求，不把计划交付当作业务验收。
- 文档冲突说明：requirements.md 末尾“尚未进入阶段 4”、architecture.md 配置节“尚未创建 .env”等为旧描述；实际状态按最新记录。本轮遵守只改 plan.md，不同步其他文件。

## 2026-11-23 T04 入库业务结构与状态（待用户验收）

- 用户本轮确认 T03b-5 模型门面与 ChatOpenAI 重构已验收并提交。只读 Git 实际 HEAD 为 7b46a1a，仍有模型门面、配置、文档等已跟踪修改、AD 暂存项和未跟踪文件；不将其描述为干净工作区，不代为提交或调整暂存区。历史“待验收”以本轮明确确认更新，配置清理未扩大确认。
- 本轮仅实现 app/rag/schemas.py、app/process/ingest/state.py，新增 tests/test_ingest_structures.py，并更新本计划；I01～I07 节点、服务、图、CLI 与问答仍未实现。此前 1.2/1.3 节“只改计划”为历史范围，本轮授权由此记录更新。
- schemas.py 提供 ManifestEntry、ValidatedCorpus、SourceSpan、ParsedBlock、Chunk；Pydantic 拒绝未知字段，检查非空正文、哈希格式、正整数且非反向行号、来源版本一致；多文件/不连续来源保存独立 source_spans，保留代码原文。真实文件边界、哈希真实性、来源 URL、稳定 ID 生成、关联完整性由后续服务验证，模型构造不代表语料已经通过这些检查。
- IngestState 使用 TypedDict(total=False)，支持节点返回增量和 state["task_id"] / state.get("chunks_artifact") 字典访问。create_ingest_state(**overrides) 每次创建新字典，深拷贝覆盖对象，拒绝未知字段；TypedDict 不做运行时值校验。CLI 后续提供唯一 build_id，默认 None 不伪造构建成功。
- 对齐差异：原状态字段表遗漏 validated_manifest，已补齐以连接 I01/I02；遵守产物引用设计，不把全量 chunks/向量塞入状态。保留七节点全部计划字段；T05 的 build_metadata/validation_report/active_index 暂用 JSON 对象类型，具体强类型结构和激活规则仍留 T05。timings 单位毫秒，error 只记录受控节点/错误码/说明。
- 自动检查：临时副本使用项目 .venv 运行专项测试，7 项通过。写回目标项目的结果另行追加。未安装依赖、读取 .env、加载模型、写数据库或调用 API。
- PyCharm 验收：打开 D:/S/项目/实战项目/fastapi-rag，解释器选 .venv/Scripts/python.exe，工作目录选项目根。在 Terminal 执行 `.\.venv\Scripts\python.exe -B -m unittest discover -s tests -p test_ingest_structures.py -v`，预期 7 项 OK；不需要启动 API 或虚拟机服务。
- 调试验收：在 test_overrides_deeply_isolated 中修改 first 后设置断点，观察 first、second、metadata、corpus、timings；只有 first 改变。在 test_json_round_trip_preserves_disjoint_spans 中检查来源范围 1～3、8～9 分开保存。非法字段/来源约束测试中的 ValidationError 是预期且被断言捕获。
- 用户尚未验收本轮；T04 整体未完成，不提交/推送 Git，不开始下一任务。
- 写回验证：目标项目专项测试 7 项全部通过（退出码 0）；本轮未运行外部服务或付费请求。未提交，等待用户验收。


### 2026-11-23 T04 测试精简（最新验收入口）

- 按用户要求，tests/test_ingest_structures.py 从 7 项精简为 1 项 test_ingest_structures_smoke，约 50 行。使用内置文本“FastAPI 支持路径参数。”；虚构路径、URL、哈希仅作结构样例，不要求准备文件或访问网络。
- 保留五种业务结构创建、片段 JSON 往返、默认状态、覆盖值及嵌套对象隔离检查；去掉本轮异常参数矩阵和重复测试。此结果不代表解析、建库或整个 T04 已完成。
- 仅修改本轮测试、AGENTS.md 与 plan.md；业务代码、依赖、构建配置及其他测试未改动。AGENTS.md 已保存后续“最小必要测试”标准，关键数据/费用失败保护仍按需检查。
- PyCharm：项目 .venv 解释器，项目根工作目录；执行 `.\.venv\Scripts\python.exe -B -m unittest discover -s tests -p test_ingest_structures.py -v`，预期 1 test / OK。前文 7 项及旧测试函数名属于历史记录，以本节为准。
- 本轮完整自动回归退出码：0；详细终端结果由本轮交付说明记录。未运行真实模型或付费 API；待用户验收，未提交 Git、不开始下一任务。
