"""受限路径工具，不创建目录、不读取配置。

流程：校验显式绝对根目录 → 拒绝危险相对路径 → resolve 链接 →
核对实际目标仍在根目录内 → 返回 Path。用于受信目录中的应用文件。
"""

from pathlib import Path, PureWindowsPath

from app.shared.errors import PathBoundaryError

_RESERVED = {"CON", "PRN", "AUX", "NUL", "CONIN$", "CONOUT$"} | {
    f"{prefix}{number}" for prefix in ("COM", "LPT") for number in "123456789¹²³"
}


def resolve_within(root: Path, relative: str) -> Path:
    """返回根目录内路径；允许中文和空格，拒绝 Windows 特殊路径及父级段。

    根目录由调用方显式传入绝对路径，避免受工作目录影响。目标可尚不存在。
    resolve 能检查已有链接，但无法防御本地进程并发替换目录（TOCTOU）。
    """
    root = Path(root)
    if not root.is_absolute():
        raise PathBoundaryError("根目录必须是绝对路径")
    if not isinstance(relative, str) or not relative:
        raise PathBoundaryError("必须提供非空相对路径")
    normalized = relative.replace("\\", "/")
    parts = normalized.split("/")
    if PureWindowsPath(relative).drive or normalized.startswith("/"):
        raise PathBoundaryError("不允许绝对路径或盘符")
    for part in parts:
        if (part in {"", ".", ".."} or part.endswith((" ", "."))
                or any(ord(char) < 32 or char in '<>:"|?*' for char in part)
                or part.split(".")[0].upper() in _RESERVED):
            raise PathBoundaryError("相对路径包含非法目录段")
    resolved_root = root.resolve()
    target = resolved_root.joinpath(*parts).resolve()
    if not target.is_relative_to(resolved_root):
        raise PathBoundaryError("路径越出指定目录")
    return target
