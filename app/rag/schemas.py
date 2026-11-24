"""T04 入库业务结构：清单、已校验语料、来源、解析块和片段。

流程：清单服务验证原件后生成 ValidatedCorpus；解析服务保留独立来源范围；
切块服务生成 Chunk。这里只做结构校验，不读取文件、计算 ID 或加载模型。
实际路径边界、原件哈希及链接与提交的一致性由后续清单服务验证。
"""

from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

NonEmpty = Annotated[str, StringConstraints(min_length=1, pattern=r"\S")]
Sha1 = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{40}$")]
Sha256 = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
PositiveLine = Annotated[int, Field(strict=True, ge=1)]


class IngestModel(BaseModel):
    """拒绝未知字段；赋值校验不能替代服务对列表修改和业务关系的检查。"""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class ManifestEntry(IngestModel):
    """对应现有 manifest.files 条目；path 是上游路径，local_path 相对项目根。"""

    path: NonEmpty
    local_path: NonEmpty
    kind: Literal["document", "example", "license"]
    language: NonEmpty | None = None
    git_blob_sha: Sha1
    source_url: NonEmpty


class ValidatedCorpus(IngestModel):
    """清单服务完成真实性校验后的输出；构造模型本身不证明原件已验证。"""

    manifest_path: NonEmpty
    manifest_digest: Sha256
    source_commit: Sha1
    knowledge_version: NonEmpty
    files: list[ManifestEntry] = Field(min_length=1)


class SourceSpan(IngestModel):
    """单文件连续且首尾包含的原始行范围；不连续选行必须拆成多个 span。"""

    path: NonEmpty
    line_start: PositiveLine
    line_end: PositiveLine
    source_url: NonEmpty
    official_url: NonEmpty | None = None
    source_commit: Sha1
    knowledge_version: NonEmpty

    @model_validator(mode="after")
    def check_lines(self) -> Self:
        """禁止反向范围，避免来源标记与原文失配。"""
        if self.line_end < self.line_start:
            raise ValueError("line_end must be >= line_start")
        return self


class ParsedBlock(IngestModel):
    """解析单元；正文和关联代码各保留自己的原始来源。"""

    block_id: NonEmpty
    document_id: NonEmpty
    text: NonEmpty
    heading_path: list[NonEmpty] = Field(default_factory=list)
    content_type: Literal["text", "code"]
    source_spans: list[SourceSpan] = Field(min_length=1)
    related_block_ids: list[NonEmpty] = Field(default_factory=list)
    source_commit: Sha1
    knowledge_version: NonEmpty
    parser_version: NonEmpty

    @model_validator(mode="after")
    def check_source_versions(self) -> Self:
        """混合来源可跨文件，但不得混用语料版本。"""
        if any(s.source_commit != self.source_commit or
               s.knowledge_version != self.knowledge_version for s in self.source_spans):
            raise ValueError("source_spans must match block version")
        return self


class Chunk(IngestModel):
    """可落盘片段；build_id 独立于稳定 ID，生成规则由切块服务实施。"""

    chunk_id: NonEmpty
    document_id: NonEmpty
    build_id: NonEmpty
    text: NonEmpty
    content_hash: Sha256
    heading_path: list[NonEmpty] = Field(default_factory=list)
    content_type: Literal["text", "code"]
    related_chunk_ids: list[NonEmpty] = Field(default_factory=list)
    source_spans: list[SourceSpan] = Field(min_length=1)
    source_commit: Sha1
    knowledge_version: NonEmpty
    parser_version: NonEmpty
    splitter_version: NonEmpty

    @model_validator(mode="after")
    def check_source_versions(self) -> Self:
        """片段版本与所有来源保持一致，不能把另一版本的代码并入正文。"""
        if any(s.source_commit != self.source_commit or
               s.knowledge_version != self.knowledge_version for s in self.source_spans):
            raise ValueError("source_spans must match chunk version")
        return self
