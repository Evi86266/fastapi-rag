"""内容指纹与 Git blob 校验；不修改输入，不规范化换行或编码。

流程：调用方提供原始 bytes → 普通指纹用 SHA-256 →
Git blob 用 SHA-1(blob + 空格 + 字节长度 + NUL + 原始内容)。
Git blob SHA-1 仅用于匹配既定 Git 对象，不用于安全签名。
"""

import hashlib


def content_sha256(content: bytes) -> str:
    """计算原始字节的 SHA-256；文本调用方应明确选择 UTF-8 等编码。"""
    if not isinstance(content, bytes):
        raise TypeError("content 必须是 bytes")
    return hashlib.sha256(content).hexdigest()


def git_blob_sha1(content: bytes) -> str:
    """计算 Git SHA-1 仓库的 blob ID；长度按字节计，区别于裸 SHA-1。"""
    if not isinstance(content, bytes):
        raise TypeError("content 必须是 bytes")
    header = f"blob {len(content)}\0".encode("ascii")
    return hashlib.sha1(header + content, usedforsecurity=False).hexdigest()
