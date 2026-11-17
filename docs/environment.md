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

默认访问 http://127.0.0.1:8000/health，应返回 HTTP 200；/ready 当前返回 HTTP 503，表明问答依赖尚未接入。

## 本次检查结果

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
