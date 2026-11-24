# 本地开发环境

项目根目录为 D:\S\项目\实战项目\fastapi-rag。基础环境优先复用 D:\S\anaconda\python.exe（3.12），应用依赖装入项目的独立 .venv。PyCharm 中选择现有解释器 .venv\Scripts\python.exe。当前基础依赖覆盖 FastAPI、LangGraph、配置和日志。

## 在项目根目录同步依赖

PowerShell 中运行以下命令。缓存和临时文件集中在项目所在的 D 盘。

```powershell
New-Item -ItemType Directory -Force .cache\tmp | Out-Null
$env:UV_CACHE_DIR = Join-Path (Get-Location) '.cache\uv'
$env:TEMP = Join-Path (Get-Location) '.cache\tmp'
$env:TMP = $env:TEMP
uv sync --locked --python 'D:\S\anaconda\python.exe' --no-python-downloads
```

普通依赖使用 pyproject.toml 中的项目镜像。模型和 Milvus 等集成依赖在对应验证任务中加入，CPU PyTorch 的下载源届时单独配置。

## 本地配置与启动

用 .env.example 作为模板。运行环境变量优先于项目根目录 .env 中的值，路径按配置文件模块定位，不依赖 PyCharm 当前工作目录。Qwen 密钥仅填写在本地 .env 或进程环境中。健康检查不要求配置密钥或启动数据库。

PyCharm 运行配置选择模块名 scripts.run_api，并把工作目录设为项目根目录。也可在项目根目录运行：

```powershell
.\.venv\Scripts\python.exe -m scripts.run_api
```

默认访问 http://127.0.0.1:8000/health，应返回 HTTP 200；/ready 当前返回 HTTP 503，并列出尚待接入的必需依赖和活动索引；最新行为及验收见文末 T03b-5 节。

## 2026-11-17 基础环境检查结果

使用 D 盘 Python 3.12.7 建立 .venv，uv 安装 49 个包，锁文件一致性检查通过。以进程内 HTTP 测试验证 /health 返回 200、/ready 返回 503，并运行了一个最小 LangGraph，确认 .env 可跨工作目录读取、进程变量可覆盖配置。PyCharm 绑定与实机启动待用户验收。

按文件长度统计，.venv 为 29,693,736 字节，项目 .cache 为 41,373,298 字节，合计约 68 MiB。该数值是项目文件的逻辑大小，未去重统计硬链接，也不代表完整项目的最终占用。

## 代码分层

| 目录 | 职责 |
|---|---|
| app/api | HTTP 入口与数据结构 |
| app/process/ingest、app/process/query | 入库图、问答图及节点 |
| app/rag/ingest、app/rag/query | 节点调用的业务实现 |
| app/infra/models、app/infra/storage | 模型和数据库的适配入口 |
| app/shared | 配置、日志和项目公共工具 |
| app/resources/prompts | 后续问答提示词 |
| scripts | 可运行的入口 |
| tests | 后续验证代码 |

基础骨架中的业务包随相应开发任务补齐。原有语料和评测材料继续分别位于 corpus 与 evaluation。

## 2026-11-18 T03a / T03b-1 最新修订：.env + os.getenv

本节取代此前 Settings 版本的配置与验收说明。用户明确选择参考培训 logger 的展示和输出配置方式，并移除 Settings。范围仍限配置、日志与启动衔接，未开始下一任务。

### 配置读取

- `settings.py` 仅保留 `PROJECT_ROOT` 和 `load_environment()`，调用 `load_dotenv(项目根/.env, override=False, interpolate=False)`；不再定义 `Settings` 或 `get_settings`。
- 启动入口及日志初始化显式加载 `.env`，随后使用 `os.getenv()` 读取参数；优先级是进程变量 > 根目录 `.env` > 默认值。不依赖工作目录，不展开值中的变量引用。
- `runtime_config.py` 只提供布尔、正整数和日志级别的校验函数，不持有配置对象或缓存。没有 `RuntimeConfig` 类。错误文本指出字段和合法格式，不回显错误输入值。
- `load_dotenv` 会将值加入进程环境；由于 `override=False`，运行期间编辑 `.env` 不会替换已加载值，必须停止并重新启动。分项日志级别允许空值，其余空布尔/数值属于错误；未知变量不会统一报错，注意核对拼写。
- `.env` 中已有模型、存储、Qwen 字段保留；本次仅消费应用/日志字段，不提前实现这些业务，也不再由 Settings 在健康启动时统一校验它们。模型/存储分组文件仍占位，后续按各自任务验证配置。
- 本地 `.env` 未被自动改写，示例不含密钥。当前环境已安装 python-dotenv（现有依赖链提供），本次未安装包、未修改依赖锁。

| 变量 | 默认值 | 说明 |
|---|---|---|
| `APP_NAME` / `APP_HOST` / `APP_PORT` | `FastAPI RAG` / `127.0.0.1` / `8000` | 应用名与服务地址，端口为 1～65535 |
| `LOG_LEVEL` | `INFO` | 兼容已有配置，作为控制台/文件默认级别 |
| `LOG_CONSOLE_ENABLE` | `true` | 控制应用和标准启动脚本的 Uvicorn 控制台输出 |
| `LOG_CONSOLE_LEVEL` | 留空继承 LOG_LEVEL | DEBUG/INFO/WARNING/ERROR/CRITICAL，不区分大小写 |
| `LOG_FILE_ENABLE` | `false` | 文件日志开关，保持默认关闭 |
| `LOG_FILE_LEVEL` | 留空继承 LOG_LEVEL | 与控制台独立配置 |
| `LOG_ROTATION_BYTES` | `5000000` | 正整数；大小轮转阈值，默认 5 MB 十进制 |
| `LOG_FILE_RETENTION` | `7 days` | 支持 1～36500 days（也接受单数 day），明确限制为按天保留 |
| `LOG_RETENTION_DAYS` | `7` | 兼容前版；仅在 LOG_FILE_RETENTION 未设置时使用 |

布尔值支持 true/false、1/0、yes/no、on/off，不区分大小写。两个输出都关闭时应用日志不会输出；错误配置仍会导致启动失败。

### 日志行为与边界

- 唯一初始化函数为 `init_logger()`，HTTP 应用在 `app.main.lifespan` 中调用；演示 CLI 在自己的 main 中调用。导入模块不加载 `.env`、不初始化 sink；`create_app()` 会加载环境但不创建文件日志。
- 控制台采用参考文件的彩色时间、级别、模块/函数/行号格式，写 stdout；文件使用 UTF-8、无 ANSI 颜色，路径为项目根 `logs/app_YYYYMMDD.log`。普通调用由 Loguru 记录位置，不使用 `inspect.stack()` 修补。
- `enqueue=True` 将写入放到队列。正常退出时调用 `logger.complete()` 等待队列写完，再 remove 释放句柄；强制终止进程不保证刷新。HTTP lifespan 使用 await，独立脚本同步等待。
- 轮转条件为本地零点和文件大小阈值任一满足；实际在下一条日志写入时触发，没有后台计时器。单条超大日志不会截断，因此阈值不是严格文件大小上限。
- 轮转时按修改时间清理过期的 `app_*.log` 匹配文件，包括参考实现产生的同模式历史文件；旧 `app.log` 及 `app.*.log` 不自动迁移/删除。按天保留不是日志目录总容量硬上限。
- `diagnose=False` 禁止异常局部变量展开；不要主动把密钥、完整环境或敏感异常内容写入消息。本次不提供任意日志文本的自动脱敏。
- Uvicorn 服务/访问日志仍走标准 logging，仅在推荐的 `scripts.run_api` 启动时使用同一控制台开关与级别；不写入应用文件日志。直接使用 uvicorn CLI 时需自行传它的日志参数。
- T03b-1 当时仅保留同步装饰器；T03b-2 的新实现、接口与验收见文末，队列写入与函数异步执行是两个独立概念。

### PyCharm 验收和可运行测试

1. 打开 `D:\S\项目\实战项目\fastapi-rag`，解释器选择 `.venv\Scripts\python.exe`，工作目录选项目根。
2. 自动回归：在项目根的 PyCharm Terminal 运行：

   ```powershell
   .\.venv\Scripts\python.exe -B -m unittest discover -s tests -p test_config_logging.py -v
   ```

   预期 **12 tests / OK**。测试自身日志隔离到 `.cache/tmp/t03-*` 并清理自身目录，验证配置优先级、跨工作目录、错误参数、导入无副作用、独立级别/开关、中文/颜色/调用位置、重复初始化、大小轮转与保留、模拟跨日轮转、队列刷新与文件释放、演示代码，以及真实 Uvicorn 健康接口。不会连接模型、数据库或付费 API。

3. 日志演示：新增 Python 运行配置，模块名填 `scripts.check_logging`。也可执行：

   ```powershell
   .\.venv\Scripts\python.exe -B -m scripts.check_logging
   ```

   代码位于 `scripts/check_logging.py`，可直接修改演示消息后运行。它输出 DEBUG/INFO/WARNING/ERROR/CRITICAL 和一次预期 RuntimeError；这个异常是演示日志，不是程序失败。结束代码应为 0。

4. 在本地 `.env` 中按需添加或修改以下字段（保留其他已有配置和凭据；不要提交 `.env`），确认 PyCharm 运行配置没有同名变量覆盖它们：

   ```dotenv
   LOG_CONSOLE_ENABLE=true
   LOG_CONSOLE_LEVEL=INFO
   LOG_FILE_ENABLE=true
   LOG_FILE_LEVEL=DEBUG
   LOG_ROTATION_BYTES=5000000
   LOG_FILE_RETENTION=7 days
   ```

   重新运行演示。控制台无 DEBUG，今天的 `logs/app_YYYYMMDD.log` 包含 DEBUG；中文可读，控制台有颜色，文件没有颜色转义字符。来源应显示 `scripts.check_logging:main`。每次运行每条演示消息仅写一次，文件会追加，注意区分多次运行。
5. 验证开关：关闭控制台、文件保持开启，演示仅写文件；再开启控制台、关闭文件，确认文件不再追加。两者关闭则静默结束。每次修改均重启脚本。可以临时把大小阈值设为 512，多运行几次观察日期文件和带时间后缀的轮转文件。
6. 保留与跨日行为由回归测试模拟验证：保留设 2 天，3 天前测试文件被清理、1 天前文件保留；跨日测试调整测试日志记录时间，不改系统时钟。无需等待到午夜或等待 7 天。
7. HTTP：运行模块 `scripts.run_api`，访问 `http://127.0.0.1:8000/health` 应为 200，`/ready` 应为 503。正常启动/停止各一条应用 INFO 日志；关闭控制台后推荐启动脚本的 Uvicorn 日志也不显示。日志文件只包含应用日志。
8. 错误参数：临时把 LOG_FILE_LEVEL 设为 INVALID 或 LOG_ROTATION_BYTES 设为 0，演示应指出相应字段并失败。验收后恢复正常配置和默认大小，文件开关按需关闭。
9. 将实际结果反馈后记录用户验收；当前仅自动检查通过，尚未提交 Git，也未启动下一任务。


## 2026-11-18 T03b-2 节点与步骤追踪

实现位于 `app/shared/runtime/tracing.py`；推荐从这里导入 `node_log`、`step_log`、`trace_context`。旧的 `logger.node_log/step_log` 导入仍可用。导入追踪模块不加载环境或初始化 sink；日志配置、轮转、级别沿用 T03b-1。

- 装饰普通同步函数或 `async def`，保留函数元数据、签名、返回值和异常对象。异步函数直到实际 await 完成才记 success；使用 perf_counter 计时，包含等待时间。
- ID 优先级：函数显式命名的 request_id/build_id 参数（含默认值） > 名为 state 的 Mapping 中对应字段 > 父上下文。None 表示继承；缺失记为 None，文本显示 `-`。不生成 ID，不再使用 session_id/task_id 替代。原函数不接收 ID 参数时，不额外塞入参数，可在入口使用 `with trace_context(request_id="..."):`。
- 嵌套步骤继承两个 ID；退出时恢复父上下文。asyncio 子任务继承创建时的上下文，互不覆盖；原生新线程需入口显式传播上下文。追踪器不会修改业务 state。
- 每次调用记录 start 和 success/error；结构化 extra 含 trace_kind、trace_name、request_id、build_id、event、elapsed_ms、error_type。开始记录的耗时为 None；结束记录含毫秒数，文本展示三位小数。
- 异常（含异步取消）记录 ERROR 后原样向外抛出，不输出 success。只记录异常类型，不自动输出异常消息、堆栈、输入或返回值；ID 和装饰器名称应使用短且不含敏感信息的值。普通业务日志不会自动附加这些字段。
- 同步/异步生成器明确拒绝，避免把创建迭代器误报为完成。普通函数若只返回协程对象，其耗时只代表该同步函数本身；需将其改成 async def 并 await，才能追踪协程执行。此任务不接入 HTTP 中间件或实际业务图。

### PyCharm 验收

1. 打开项目 `D:\S\项目\实战项目\fastapi-rag`，选择项目 `.venv\Scripts\python.exe`，工作目录为项目根。
2. Terminal 运行追踪测试：

   ```powershell
   .\.venv\Scripts\python.exe -B -m unittest discover -s tests -p test_tracing.py -v
   ```

   预期 **8 tests / OK**：覆盖同步计时和返回值、异步真实完成、嵌套恢复、并发隔离、异常原样传播、取消、方法/默认参数及生成器拒绝。
3. 运行已有配置日志回归：

   ```powershell
   .\.venv\Scripts\python.exe -B -m unittest discover -s tests -p test_config_logging.py -v
   ```

   预期 **12 tests / OK**，包括真实本地 HTTP 200/503；测试日志仍隔离到项目 `.cache/tmp` 并清理。
4. 新建 Python 运行配置，模块名 `scripts.check_tracing`。运行配置环境变量设 `LOG_CONSOLE_ENABLE=true;LOG_CONSOLE_LEVEL=INFO;LOG_FILE_ENABLE=false`，不必改真实 .env。也可使用 `python -B -m scripts.check_tracing`（输出取决于当前日志配置）。
5. 检查同步节点和步骤都带 `build_id=demo-build`；两组并发异步节点和步骤分别带 `request_id=demo-A/demo-B`，不可串号。异步步骤结束耗时约 50ms 或更高，不能在等待前记录 success；这是演示等待，不是业务性能指标。
6. `demo-error` 节点应先 start 后 error，包含 RuntimeError 和耗时，无该节点的 success；随后出现调用方捕获提示，进程结束码为 0。需要调试时在 async_step 的 await 行和异常捕获处设置断点。
7. 如需验收文件输出，在运行配置设 `LOG_FILE_ENABLE=true;LOG_FILE_LEVEL=INFO`，确认当天 `logs/app_YYYYMMDD.log` 含相同 ID/事件，中文可读。停止后恢复临时运行配置。
8. 将结果反馈后记录用户验收；此任务不提交 Git、不启动 T03b-3。自动检查结果见 plan.md 最新记录。

## 2026-11-19 T03b-3 提示词加载

入口为 `app.shared.runtime.load_prompt.load_prompt(name, variables=None)`，返回字符串。
模板固定放在 `app/resources/prompts`；名称采用正斜杠相对路径，例如 `v1/example.prompt`，路径分段仅允许英文字母、数字、下划线、连字符，后缀必须为 `.prompt`。拒绝绝对路径、上级目录、反斜杠、盘符、UNC、备用数据流及解析后越界的链接。不提供自定义根目录入口。

模板使用标准库 string.Template 的 `$name` / `${name}`，变量名为 ASCII 标识符；字面 `$` 写 `$$`，普通 Python/JSON 花括号无需转义。模板出现的变量均必需；值必须为字符串，空字符串允许，多余键忽略。传入的文本不需要转义，也不做二次替换。该规则只保证文本替换，不代表能够防御模型提示词注入。

缺文件抛 FileNotFoundError；缺变量、非法路径或模板语法抛 ValueError；变量参数类型错误抛 TypeError；非法编码抛 UnicodeError；其他读取错误保留 OSError。错误不会输出变量值或模板全文。每次读取最新 UTF-8 文件，无缓存，不执行表达式。模板资源视为应用维护的文件，不用于接收用户上传文件；不保证防御并发修改资源目录的本地进程。

`answer.prompt` 保持 T07 占位。本次 `loading_demo.prompt` 只用于验证加载，未实现答案生成、模型、入库或问答调用。

### PyCharm 验收

1. 打开 `D:\S\项目\实战项目\fastapi-rag`，解释器选 `.venv\Scripts\python.exe`，工作目录选项目根。不需调整 .env 或启动外部服务。
2. Terminal 运行专项测试，预期 **8 tests / OK**：

   ```powershell
   .\.venv\Scripts\python.exe -B -m unittest discover -s tests -p test_load_prompt.p
   y -v
   ```

   覆盖中文和花括号、单次替换、缺文件、缺变量、非法模板、路径限制、模拟链接解析越界、跨工作目录、编码及无缓存。链接测试模拟 resolve 结果，不要求 Windows 创建符号链接权限。
3. 新建 Python 运行配置，选择“模块名” `scripts.check_prompts`，或在 Terminal 运行：

   ```powershell
   .\.venv\Scripts\python.exe -B -m scripts.check_prompts
   ```

   应显示中文演示，JSON/集合花括号完整，内容里的 `${not_provided}` 和字面 `${not_a_variable}` 保留；显示缺文件、缺变量、路径越界三条“预期错误”，最后“提示词加载验收演示通过”，退出码 0。
4. 可在 load_prompt 中 template.substitute 行打断点，检查原始 source、values 和返回值；无模型调用。可修改演示模板中的普通中文后重跑以观察即时生效，验收后恢复演示文件。
5. 完整回归预期 **28 tests / OK**，包括已有配置/日志 12 项、追踪 8 项、提示词 8 项：

   ```powershell
   .\.venv\Scripts\python.exe -B -m unittest discover -s tests -p 'test_*.py' -v
   ```

6. 将实际结果反馈后再记录用户验收。本次不提交 Git，不开始下一任务。自动检查实测结果见 plan.md 最新记录。
## 2026-11-19 T03b-4 公共工具与运行保护基础

本轮仅提供可复用基础，不接入模型、存储、入库或问答；健康接口仍为 /health 200、/ready 503。不新增依赖，不修改 .env 或启动配置。

- `app.shared.utils.paths.resolve_within(root, relative)`：root 必须为显式绝对路径；允许中文目录及斜杠/反斜杠，拒绝绝对路径、盘符、父级段、Windows 保留名、尾随点/空格及备用数据流。resolve 后检查链接边界，目标可不存在，不自动创建目录。目录必须由应用信任和维护；不防御本地进程并发替换链接。链接越界测试模拟 resolve，不宣称已测真实 Windows junction。
- `content_sha256(bytes)` 为原始内容 SHA-256；`git_blob_sha1(bytes)` 为 SHA-1 仓库的 Git blob ID，含 blob 类型与字节长度头；不转换换行和编码。文本须由调用方显式编码。测试通过真实 `git hash-object --stdin` 对照中文/混合换行内容。
- `AppError` 及子类具有稳定 code，区分路径、预算、用量状态、容量满和执行器关闭；尚未接入 HTTP 错误映射。错误消息不应放入原始供应商响应或凭据。
- `UsageLedger(limit, opening_spent=...)`：金额为人民币 Decimal，必须有限非负；每次调用及重试单独 reserve 最大费用，settle 记录 succeeded/failed 以及 token 数和实际费用。失败不等于免费，未知费用用 None，保持预留；只有确认无费用才填 Decimal("0")。reconcile 为已结束的未知账目补记实际费用。重复核销/对账拒绝，预算原子检查；实际费用超出预留仍如实登记，超预算后阻止新调用。token 的 None 表示未知，0 表示确认零用量。
- 台账是单进程内存对象，不持久化、不自动跨月结算、不自动估价；opening_spent 可带入已知历史支出，但不能恢复未决明细。未来付费接入前必须补齐持久化、未知账单恢复、当月服务器费用及 API 费用对账。演示额度不是生产预算或价格；本轮未启用付费调用。
- `BoundedExecutor(max_workers)`：显式容量，最多相同数量未完成工作，满时立即抛 ResourceBusyError，无等待队列或自动重试。run 接受同步函数，在线程中执行并复制 ContextVar，传播返回值和异常；不适合返回协程的同步包装函数。取消/asyncio.wait_for 超时只结束等待，无法终止底层线程，容量到线程真正结束才释放。close 同步等待，aclose 在线程中等待关闭，关闭后拒绝新调用。关闭须由拥有者调用，不从其工作函数内部关闭。
- 这些对象须由后续启动层显式创建、传入环境配置值并关闭；当前不建立全局实例、不增加未消费的环境字段，不改变已验收提示词异常契约。线程不能保证纯 Python CPU 任务并行加速，也不提供跨进程并发锁。

### PyCharm 验收

1. 打开 `D:\S\项目\实战项目\fastapi-rag`，解释器选项目 `.venv\Scripts\python.exe`，工作目录为项目根。不需修改 .env 或启动外部服务。
2. Terminal 运行专项检查，预期 **16 tests / OK**：

   ```powershell
   .\.venv\Scripts\python.exe -B -m unittest discover -s tests -p test_runtime_foundation.py -v
   ```

   覆盖非法路径与模拟链接越界、真实 Git 哈希对照、费用成功/失败/未知/超支、并发预留、线程上下文、异常原样抛出、容量满、取消/超时及关闭等待。
3. 新建 Python 运行配置，模块名为 `scripts.check_runtime_foundation`，运行后应显示路径错误 invalid_path、预算错误 budget_exceeded、未知失败余额 0.2、对账后余额 0.9、线程结果 6，最后“公共工具与运行保护基础演示通过”，退出码 0。控制台编码若不一致，可在运行配置设置 `PYTHONIOENCODING=utf-8`。
4. 调试可在 metrics.py 的 reserve/settle/reconcile、resources.py 的容量获取及 future 完成回调处设置断点；取消和关闭场景建议直接运行专项测试，避免断点暂停触发测试等待超时。
5. 完整回归预期 **44 tests / OK**：

   ```powershell
   .\.venv\Scripts\python.exe -B -m unittest discover -s tests -p 'test_*.py' -v
   ```

   包括既有 28 项回归和本轮 16 项，既有测试会启动短暂本地 HTTP 服务验证 200/503，日志与模板测试文件在 .cache/tmp 隔离并清理。
6. 反馈实际结果后再标记用户验收通过；本轮不提交 Git，不开始下一任务。


## 2026-11-19 T03b-5 第一部分：通用生命周期与分项就绪

用户本轮明确：先修改其他部分，模型、数据库及相关配置等用户操作并回复后再改。
因此本节仅交付可独立验收的通用基础，**不代表 T03b-5 整项完成**。
未改 `.env`、`.env.example`、模型/数据库适配器、配置分组、依赖声明或锁文件。
未安装 SDK、加载模型、连接数据库、调用生成 API；本次 API 费用为 0。

### 当前实现与边界

- `app/infra/providers.py` 定义 `ManagedDependency` 生命周期契约、依赖声明和安全状态快照。每个应用拥有一个 Providers，不使用跨应用全局客户端。默认声明尚未注册真实适配器。
- lifespan 创建资源拥有者，后台串行初始化已注册资源；阻塞工作复用 T03b-4 的单线程受限执行器。初始化阶段 HTTP 存活检查仍可用。未来适配器的网络操作必须自行设置超时；线程取消不能强杀底层调用，停止时等待真实工作完成。
- 已注册资源在启动后定期进行免费只读 `probe`；当前默认没有真实资源，因此不会联网。探测失败后下轮可恢复；初始化失败保留失败状态、重启后再尝试，避免重复部分加载。工厂必须自行清理未能返回的对象。
- 关闭时先停止后台任务、等待线程结束，再逆序释放全部实例；某个 close 失败不跳过其他实例。异常正文和凭据不进入就绪响应，关闭失败只记录数量。
- `/health` 保持 HTTP 200 / `{"status":"ok"}`。`/ready` 读取缓存状态，不执行模型推理、数据库操作或付费请求。仅当生命周期运行中、所有必需依赖真实为 ready 时返回 200，否则 503。
- 当前 `embedding/milvus/qwen` 为 `pending/awaiting_configuration`；`active_index` 为 `pending/pending_t05_active_index`。这是尚未接入的事实，不是连接失败诊断，也不通过配置存在来伪造 ready。
- `reranker/history/archive` 关闭时为 `disabled` 且不阻塞就绪。显式开启后成为本次运行的必需依赖；历史和归档尚未实现时明确报告 `feature_not_implemented`，本轮不会接入这两项业务。
- `checked_at` 为 UTC ISO 时间，表示实际探测时间；尚未执行真实探测的状态为 null。接口仅暴露固定依赖名、状态和受控原因，不暴露 URL、模型路径或密钥。
- 外部适配器真实接入、SDK 兼容锁定、Qwen 持久费用恢复和超时处理、T02b～e 实测均待后续在同一 T03b-5 内完成。T05 活动索引验收不提前实施。

### PyCharm 验收（本部分，无需外部配置）

1. 打开 `D:\S\项目\实战项目\fastapi-rag`，选择 `.venv\Scripts\python.exe`，工作目录为项目根。不需要启动虚拟机服务或填写密钥。
2. 在 Terminal 运行专项测试，预期 **12 tests / OK**：

   ```powershell
   .\.venv\Scripts\python.exe -B -m unittest discover -s tests -p test_providers.py -v
   ```

   验证必需/可选门槛、索引缺失、失败脱敏与恢复、部分初始化失败清理、关闭等待、单资源关闭失败不影响其他释放，以及真实 ASGI HTTP 200/503。
3. 运行完整回归，预期 **56 tests / OK**（既有 44 + 新增 12）：

   ```powershell
   .\.venv\Scripts\python.exe -B -m unittest discover -s tests -p 'test_*.py' -v
   ```

   测试仅使用假外部资源；已有日志测试会短暂启动本地 Uvicorn。不得将测试中的模拟 ready 当作真实服务接通。
4. 新建 Python 运行配置，模块名 `scripts.check_readiness`；或运行：

   ```powershell
   .\.venv\Scripts\python.exe -B -m scripts.check_readiness
   ```

   应输出 `not_ready`、`lifecycle=running`，上述必需能力 pending、关闭的可选能力 disabled，退出码 0。中文乱码时在运行配置添加 `PYTHONIOENCODING=utf-8`。
5. 运行模块 `scripts.run_api`，访问 `http://127.0.0.1:8000/health` 应为 200；访问 `/ready` 应为 503 且含 `dependencies` 分项。正常首轮初始化后检查 pending/disabled；刚启动时可能短暂为 not_started。反复刷新不会触发外部连接或付费调用。
6. 可在 PyCharm 运行配置临时设置 `RERANK_ENABLED=true`，重启后应看到 reranker 的 `required=true`、状态 pending；`HISTORY_ENABLED=true` 时 history 应为 `feature_not_implemented`。验收后删除临时覆盖，不修改真实 .env；进程变量优先于 .env。
7. 停止应用，确认资源收尾和“应用停止”日志正常。复杂关闭/故障行为由专项测试覆盖。反馈验收结果后再记录用户验收；不自动提交 Git。

### 待用户操作后统一回复的外部配置

仅记录待确认字段，不在本轮写入或修改它们的值：

| 项目 | 待回复内容 |
|---|---|
| Milvus | 实际 URL/IP 与端口、服务版本、是否已启动、认证方式；无认证请明确说明；有认证时填本地配置，不提交 Git |
| Qwen | 账户地域、API Base URL、模型名、API key 已填本地 .env 或待提供；密钥不写入文档或日志 |
| 费用 | 当月已有服务器/API 支出、当前输入/输出单价或授权按地域核对、是否沿用本轮 1 元采样预算 |
| 本地 BGE | 确认继续使用既有两套目录、CPU/float32、默认关闭重排 |

MongoDB 历史和 MinIO 业务归档本次保持关闭，不需要它们的凭据。
用户回复后才继续模型/数据库适配、配置写入、依赖安装及实机验证；不自动进入入库或问答。


## 2026-11-20 T03b-5 配置核对与修正

本节更新上节“等待用户配置”的状态。用户已配置 Milvus 和 Qwen，并授权自行核对修正；确认本月已有服务器/API 支出为 0 元。实际文件为项目根 `.env`，同级 `fastapi-rag.env` 不存在。

- 将用户填写的 `LLM_DEFAULT_MODEL`、`OPENAI_BASE_URL`、`OPENAI_API_KE` 分别改为项目约定的 `QWEN_MODEL`、`QWEN_BASE_URL`、`QWEN_API_KEY`，原值完整保留；不在文档、输出或暂存副本中保存密钥。
- 端点格式为北京地域业务空间专属 OpenAI 兼容接口，保留用户地址；格式识别不证明 API Key 有效。来源：[官方 Base URL](https://help.aliyun.com/zh/model-studio/base-url)。
- 保留已有两套本地 BGE 目录、CPU/float32；重排、历史和业务归档保持关闭。文件检查只证明必要文件存在，不证明权重完整或加载成功。
- 2026-11-20 核对 qwen-flash 北京标准价格，输入≤128k：输入 0.15、输出 1.5 元/百万 token，未依赖免费额度或优惠。[官方价格](https://help.aliyun.com/zh/model-studio/qwen-flash)。
- 配置本月预算 100 元、期初支出 0 元、初始采样上限 1 元；输入上限 4096、输出上限 128 token、超时 30 秒、自动重试 0 次。按上限估算单次 0.0008064 元。此处是前置检查参数，生成适配器和持久台账尚未接入，不能声称已实现运行时预算拦截。
- 新增 `scripts.check_external_config`，消费上述字段并校验模型文件、字段格式、金额、账期和保守费用估算。`.env.example` 同步变量及说明，地址/密钥留空，账期和历史支出要求操作者填写。
- 默认 `/ready` 的外部能力原因从 `awaiting_configuration` 更新为 `adapter_not_implemented`，明确配置补齐后仍缺适配器；活动索引继续等待 T05。真实 Milvus 服务版本/认证、BGE 加载、Qwen 鉴权/调用仍未验证，不改入库和问答业务。

### PyCharm 检查

项目解释器和工作目录沿用上一节，在 Terminal 执行：

```powershell
.\.venv\Scripts\python.exe -B -m scripts.check_external_config
.\.venv\Scripts\python.exe -B -m scripts.check_external_config --probe-network
.\.venv\Scripts\python.exe -B -m unittest discover -s tests -p 'test_*.py' -v
```

第一条应为 `configuration=valid`，金额估算 0.0008064；第二条在服务可达时分别显示 `tcp_reachable`、`tls_reachable`。网络检查每个目标一次，5 秒超时，不发送密钥，不调用生成或数据库业务；连通失败退出 1，不能据此断言认证或 SDK 不兼容。第三条预期 56 项通过。

启动 `scripts.run_api` 后 `/health` 仍为 200；`/ready` 仍为 503，已配置外部能力显示 `adapter_not_implemented`。当前未安装重型 SDK或运行模型，尚不能验收整项 T03b-5。


## 2026-11-20 T03b-5 真实适配与生命周期（最新行为）

本节取代前文“适配器尚未实现”和“只有配置前置检查”的状态。实现范围为本地编码/重排、Milvus 只读服务接入、Qwen 非流式调用、费用持久化和生命周期；入库、检索业务、问答图、活动索引仍按后续任务实施。

### 依赖与运行

- Python 3.12 / Windows；uv.lock 固定实际组合，CPU torch 2.6.0+cpu、FlagEmbedding 1.3.5、transformers 4.51.3、peft 0.15.2、sentence-transformers 3.4.1、PyMilvus 2.4.15。普通包沿用项目镜像，torch 单独使用官方 CPU 源；未装 CUDA、torchvision、torchaudio。
- setuptools 固定 80.9.0：PyMilvus 2.4.15 仍导入 pkg_resources，新版 setuptools 会导入失败。保留 SDK 弃用警告，不表示连接失败。未升级共享 Milvus 服务。
- `uv sync --locked --python .venv/Scripts/python.exe --no-python-downloads` 可复现；先按本文顶部设置 UV_CACHE_DIR/TEMP/TMP 到项目 D 盘。锁文件仅解析 Windows 应用环境，不宣称 Linux 应用安装验证通过。
- 配置继续 `.env` + `os.getenv()`，进程变量优先；修改配置后重启。`EXTERNAL_ENABLED` 默认 true；false 仅用于隔离测试/只检查健康接口，此时必需外部能力 pending，不能获得 ready。
- `MODEL_CPU_THREADS=2`、`BGE_MAX_LENGTH=512`、`RERANK_MAX_LENGTH=512`、`MILVUS_TIMEOUT_SECONDS=5` 为安全默认值；`MILVUS_TOKEN` 默认空，无认证当前已验证。有认证时显式配置 token 或 user:password。模型/服务地址和密钥没有真实代码默认值。

### 适配与就绪契约

- Providers 保留后台初始化、就绪探测和受限执行职责；默认模型实例与模块级 `llm_provider` 共用，不重复加载。模型业务入口统一为 `llm_provider`，原 `providers.call(...)` 保留供既有验证脚本使用。受限执行器仍满容量拒绝、关闭等待在途线程；直接取得 SDK 后的调用应由业务运行层安排线程与生命周期。
- BGE 本地离线、CPU/float32、批量 1；HF/Torch 缓存固定在项目 .cache，禁止 Hub 自动下载。模型缺失明确失败。query/document 分别有入口，沿用同一 BGE-M3 编码和归一化；输出转换成普通 dense list / sparse int-key dict。编码和文本对超长时拒绝，不静默截断代码；切块属于 T04。
- Milvus 使用独立连接 alias、有限 RPC 超时并读取真实服务版本，要求 2.4.x。只关闭自身连接，不创建/删除/写入集合。字段、索引、稠密/稀疏查询兼容性及活动集合验证留给后续 T02d/T05，不将版本 RPC 成功当作这些能力已验收。
- Qwen 生成统一使用 `langchain-openai==1.8.3` 的 `ChatOpenAI`，删除手写 HTTP 生成分支；普通/JSON 客户端缓存并共用连接和费用回调。`invoke/ainvoke` 均复用原 SQLite 预算预留与核销。免费模型列表探测使用同一 SDK；健康探针不生成。模型限已核价的北京 qwen-flash，非流式、关闭思考、无工具、零自动重试；`stream/astream` 回退到完整回复，不提供 token 流。更换价格/模型/地域仍须重新核价。
- `/health` 无外部请求副作用。启动后台会加载必需模型和连接服务；`/ready` 只读取状态快照。外部能力应依次 starting → ready 或明确错误，默认 reranker/history/archive disabled；active_index 保持 pending_t05_active_index，因此当前应用整体仍为 HTTP 503。不能通过关闭外部能力来伪造就绪。
- 模型探针只检查已加载实例，服务探针默认每 30 秒运行一次；检查时间为 UTC。推理占用唯一执行槽时跳过该轮探测。服务故障可在后续探测恢复，初始化失败需重启。快照表示最近一次检查，不保证两次检查之间永不故障。

### 费用与失败恢复

- `data/reports/qwen-usage.sqlite3` 保存预算策略、预留、状态和 token；不保存密钥、输入、输出。SQLite 事务原子预留，重启恢复，不自动清账或跨月重置；同一文件的预算/期初支出改动会拒绝，须先对账迁移。
- 按当月 100 元和小样本累计 1 元同时限制，期初 0 元由用户确认。按输入 4096/输出 128 token 和已核价单价，单次最大预留 0.0008064 元。输入使用 UTF-8 字节上界及每条消息 256 token 余量检查，再全额预留；接受纯文本消息，不接受多模态内容。
- 成功按返回 token 和标准价核销，金额是保守费用估算，优惠/缓存折扣及最终账单须另行核对。台账仅管理本项目，服务器/其他 API 新增支出不自动发现。
- 失败、超时、响应缺用量保留预留额，未知不当作免费；下次调用及重启后均阻止新付费请求。崩溃遗留 pending 同样阻止。仅在确认无仍在执行的请求后，根据供应商账单用 `PersistentUsage.reconcile` 对指定 reservation_id 补记；不能删除台账或虚构零费用绕过保护。
- 每次 HTTP 操作使用配置的 30 秒 HTTPX 超时（连接/读写等阶段），无自动重试；不是可强杀线程的全局墙钟期限。实际费用超预留仍如实记账，剩余额度不足会阻止新调用。

### PyCharm 验收

1. 解释器为项目 `.venv/Scripts/python.exe`，工作目录为项目根；停止其他模型检查进程，再逐条运行。可设置 PYTHONIOENCODING=utf-8，避免中文显示问题。
2. 自动回归（假资源，无真实外部请求）：

   ```powershell
   .\.venv\Scripts\python.exe -B -m unittest discover -s tests -p 'test_*.py' -v
   ```

   预期 76 项通过，覆盖持久费用、未知费用阻止、同步/异步 ChatOpenAI、JSON 参数、客户端复用与关闭、门面输出和原有生命周期回归；使用假 HTTP/模型，无真实付费请求。
3. 免费实机检查，分别运行以下模块参数（报告自动写入 data/reports/external-*.json）：

   ```powershell
  
   ```

   预期 passed=true、退出码 0；Milvus 返回 v2.4.11，Qwen 仅鉴权探测，编码 dense=1024 且 sparse 有效，重排返回两个有限分数；coexist 同时加载两个模型，不改变默认重排开关。报告内包含启动时间、小样本推理时间、50ms 采样 RSS 峰值、配置哈希和权重字节数；权重字节数不等于完整内容哈希。
4. 本次已完成一次 Qwen 采样，无需重复付费。如需自行重跑，显式添加 `--paid`；每次会新增一次调用和台账记录，仍受 1 元累计限制。
5. 运行 `scripts.run_api`：/health 应为 200。后台初始化完成后 /ready 中 embedding、milvus、qwen 应 ready，active_index pending，整体 503。关闭应用观察正常收尾；未接入 T05 前不期望整体 200。不要同时启动多个 worker 重复加载模型。
6. 故障检查可临时在运行配置覆盖 BGE_M3_PATH 为不存在目录，重启后应报告 model_path_missing；清空 QWEN_API_KEY 后应报告 missing_config；恢复并重启。超时和预算失败用隔离回归覆盖，避免为了验证失败而产生真实未知账单。
7. 反馈实机体验和验收结果；实现/自动检查通过不等于用户已验收，不自动提交 Git或开始下一任务。


### 2026-11-20 LLMProvider 统一调用验收

启动入口先调用 `load_environment()`，导入门面本身不读配置、不加载模型。

```python
from app.shared.config.settings import load_environment
from app.infra.providers import llm_provider
from langchain_openai import ChatOpenAI

load_environment()
chat = llm_provider.chat()  # 仅构造客户端，不生成、不收费
assert isinstance(chat, ChatOpenAI)
assert chat is llm_provider.chat()
json_chat = llm_provider.chat(json_mode=True)
# 本地模型按需加载；不要在异步事件循环内直接执行同步 CPU 推理。
# model = llm_provider.embedding_model()
# vectors = llm_provider.embed_documents(["FastAPI 查询参数示例"])
# reranker = llm_provider.reranker_model()  # 显式加载，即使默认重排开关关闭
```

`embed_documents` 返回 `dense_vecs` 与 `lexical_weights` 字典，复用既有编码与校验。
独立脚本使用后通过 `asyncio.run(llm_provider.aclose())` 释放资源；异步程序在原事件循环中 `await llm_provider.aclose()`。
应用内默认已启用模型由 Providers 生命周期关闭。显式获取未启用的可选模型时，调用方应同样执行门面收尾。
本次自动检查通过后仍待用户在 PyCharm 验收；不提交 Git，不开始入库或问答业务。


## 2026-11-23 配置层清理（待用户验收）

- 删除无应用引用的 bailian_mcp_config、embedding_config、lm_config、milvus_config、mineru_config、minio_config、reranker_config 及其专用 common；删除无引用的 storage_config 空占位。删除的是应用配置代码，不涉及共享 MinIO 服务或数据。
- settings.py 删除旧 AppSettings、全局 settings 及导入时 load_dotenv；仅保留 PROJECT_ROOT 和显式 load_environment，固定根 .env、override=False、interpolate=False。
- model_config.py、runtime_config.py 已检查，保留实际调用的字段、URL、金额、模型路径、布尔、整数和日志级别校验，不引入配置对象或重复封装。
- 未变更环境字段、默认值、真实 .env 或 .env.example；未修改入库或问答业务，未连接真实模型/数据库或调用付费 API。
- 验证：完整自动回归通过（退出码 0）。PyCharm 使用项目 .venv，在项目根执行 `python -B -m unittest discover -s tests -p 'test_*.py' -v` 复核；重点检查导入无副作用、显式加载、进程变量优先及适配器回归。
- 用户尚未验收；不提交、不推送 Git，不开始下一任务。原有暂存区保持不动，已暂存的旧配置文件在工作区删除，待用户确认后统一处理提交。
