"""I01 清单校验：先检查元数据和路径，再逐个核对原始字节哈希。

只读取清单列出的固定版本文件；许可证参与校验但不输出为知识输入。
不加载环境、模型或数据库，不解析正文，也不写入产物。
"""

from collections import Counter
import json
from pathlib import Path

from pydantic import ValidationError

from app.rag.schemas import ManifestEntry, ValidatedCorpus
from app.shared.config.settings import PROJECT_ROOT
from app.shared.errors import AppError, PathBoundaryError
from app.shared.runtime.tracing import step_log
from app.shared.utils.hashing import content_sha256, git_blob_sha1
from app.shared.utils.paths import resolve_within

# 已确认的语料业务版本，不属于部署环境配置。
SOURCE_COMMIT = "ca5f60ee72f35fb2134d8b5d26bbb75965bcff66"
KNOWLEDGE_VERSION = "0.135.1"
COUNTS = {"documents": 10, "examples": 64, "licenses": 1}


class ManifestValidationError(AppError):
    """清单失败携带稳定错误码；不泄露原始 JSON 或系统异常内容。"""

    def __init__(self, code: str):
        self.code = code
        super().__init__(f"清单校验失败：{code}")


def _unique_object(pairs):
    """拒绝 JSON 重复键，避免解析器静默覆盖校验字段。"""
    result = {}
    for key, value in pairs:
        if key in result:
            raise ManifestValidationError("manifest_duplicate_key")
        result[key] = value
    return result


def _read(path: Path) -> bytes:
    """按原始字节读取；缺文件与其他读取故障分别报告。"""
    try:
        return path.read_bytes()
    except FileNotFoundError:
        raise ManifestValidationError("manifest_file_missing") from None
    except OSError:
        raise ManifestValidationError("manifest_read_error") from None


@step_log("validate_manifest")
def validate_manifest(manifest_path: str, *, project_root: Path = PROJECT_ROOT) -> ValidatedCorpus:
    """校验相对项目根的清单，返回文档和示例白名单及清单 SHA-256。

    project_root 用于显式依赖注入和隔离测试；必须是绝对目录。
    调用期间原件应保持不变；不保证防御本地进程并发替换文件。
    """
    try:
        return _validate(manifest_path, Path(project_root))
    except PathBoundaryError:
        raise ManifestValidationError("manifest_invalid_path") from None
    except (ValidationError, json.JSONDecodeError, UnicodeError):
        raise ManifestValidationError("manifest_invalid_schema") from None
    except (OSError, RuntimeError):
        raise ManifestValidationError("manifest_read_error") from None


def _validate(manifest_path: str, root: Path) -> ValidatedCorpus:
    """先完成所有条目的路径/来源检查，随后才读取被允许的原件。"""
    manifest_file = resolve_within(root, manifest_path)
    raw = _read(manifest_file)
    data = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_object)
    if not isinstance(data, dict):
        raise ManifestValidationError("manifest_invalid_schema")
    if (data.get("repository") != "fastapi/fastapi"
            or data.get("commit_sha") != SOURCE_COMMIT
            or data.get("release_tag") != KNOWLEDGE_VERSION
            or data.get("document_language") != "zh"):
        raise ManifestValidationError("manifest_version_mismatch")
    counts = data.get("counts")
    if (not isinstance(counts, dict) or counts != COUNTS
            or any(type(value) is not int for value in counts.values())):
        raise ManifestValidationError("manifest_count_mismatch")
    files = data.get("files")
    if not isinstance(files, list):
        raise ManifestValidationError("manifest_invalid_schema")
    entries = [ManifestEntry.model_validate(item) for item in files]
    if Counter(entry.kind for entry in entries) != {"document": 10, "example": 64, "license": 1}:
        raise ManifestValidationError("manifest_count_mismatch")

    raw_root = resolve_within(root, "corpus/raw")
    seen_paths, seen_targets = set(), set()
    checked = []
    for entry in entries:
        # 使用规范的上游 POSIX 路径；本地地址必须与之逐字对应。
        if "\\" in entry.path or entry.local_path != f"corpus/raw/{entry.path}":
            raise ManifestValidationError("manifest_invalid_path")
        target = resolve_within(raw_root, entry.path)
        # 防止 corpus/raw 本身或其内部链接指向 evaluation 等其他项目目录。
        expected_root = root.resolve() / "corpus" / "raw"
        if raw_root != expected_root or target != expected_root.joinpath(*entry.path.split("/")):
            raise ManifestValidationError("manifest_invalid_path")
        if entry.path.casefold() in seen_paths or target in seen_targets:
            raise ManifestValidationError("manifest_duplicate_entry")
        seen_paths.add(entry.path.casefold())
        seen_targets.add(target)
        if entry.kind == "document":
            allowed = entry.path.startswith("docs/zh/docs/tutorial/") and entry.path.endswith(".md") and entry.language == "zh"
        elif entry.kind == "example":
            allowed = entry.path.startswith("docs_src/") and entry.path.endswith(".py")
        else:
            allowed = entry.path == "LICENSE"
        if not allowed:
            raise ManifestValidationError("manifest_invalid_source")
        if entry.source_url != f"https://github.com/fastapi/fastapi/blob/{SOURCE_COMMIT}/{entry.path}":
            raise ManifestValidationError("manifest_source_url_mismatch")
        checked.append((entry, target))

    for entry, target in checked:
        if git_blob_sha1(_read(target)) != entry.git_blob_sha:
            raise ManifestValidationError("manifest_hash_mismatch")
    return ValidatedCorpus(
        manifest_path=manifest_file.relative_to(root.resolve()).as_posix(),
        manifest_digest=content_sha256(raw), source_commit=SOURCE_COMMIT,
        knowledge_version=KNOWLEDGE_VERSION,
        files=[entry for entry in entries if entry.kind != "license"],
    )
