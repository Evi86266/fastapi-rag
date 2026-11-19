"""提示词文件加载与单次变量替换，不负责模型调用或答案业务。

流程：校验相对模板名 → 解析并检查目录边界 → UTF-8 读取 →
校验模板及必要变量 → 单次替换返回。导入不读取模板、环境或初始化日志。
"""

from collections.abc import Mapping
from pathlib import Path
import re
from string import Template


PROMPTS_ROOT = Path(__file__).resolve().parents[2] / "resources" / "prompts"
_NAME = re.compile(r"(?:[A-Za-z0-9_-]+/)*[A-Za-z0-9_-]+\.prompt", re.ASCII)


def load_prompt(name: str, variables: Mapping[str, str] | None = None) -> str:
    """加载 prompts 内的模板；变量值须为字符串，空字符串允许，多余变量忽略。

    name 使用正斜杠相对路径，仅允许字母、数字、下划线、连字符及 .prompt
    后缀，拒绝绝对路径、上级目录和 Windows 特殊路径。模板使用 $name 或
    ${name}，字面美元符使用 $$；普通花括号无需转义。不执行表达式、不缓存。
    文件缺失抛 FileNotFoundError；非法路径、模板、缺变量抛 ValueError；
    参数类型错误抛 TypeError；读取失败保留 OSError，编码错误抛 UnicodeError。
    """
    if not isinstance(name, str) or _NAME.fullmatch(name) is None:
        raise ValueError("模板名必须是 prompts 内的相对 .prompt 路径，仅允许字母、数字、_、- 和目录分隔符 /")
    root = PROMPTS_ROOT.resolve()
    path = (root / name).resolve()
    # resolve 后再检查，防止目录链接或符号链接把合法文件名导向资源目录外。
    if not path.is_relative_to(root):
        raise ValueError("模板路径越出 prompts 目录")
    try:
        source = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise FileNotFoundError(f"提示词文件不存在：{name}") from None
    except UnicodeError:
        raise UnicodeError(f"提示词文件必须使用 UTF-8 编码：{name}") from None

    template = Template(source)
    if not template.is_valid():
        raise ValueError(f"提示词模板语法错误：{name}；使用 $name / ${{name}}，字面 $ 写为 $$")
    if variables is not None and not isinstance(variables, Mapping):
        raise TypeError("variables 必须是字符串键值映射或 None")
    values = {} if variables is None else dict(variables)
    required = template.get_identifiers()
    missing = [key for key in required if key not in values]
    if missing:
        raise ValueError(f"提示词 {name} 缺少必要变量：{', '.join(missing)}")
    for key in required:
        if not isinstance(values[key], str):
            raise TypeError(f"提示词变量 {key} 必须是字符串")
    # substitute 只扫描原模板；变量值中的占位符、花括号或代码不会被二次解析。
    return template.substitute({key: values[key] for key in required})
