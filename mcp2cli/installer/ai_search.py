"""AI-powered search for MCP server installation info."""

from __future__ import annotations

import json

import click

from mcp2cli.config.models import AISearchResult
from mcp2cli.generator.llm_backend import get_backend

INSTALL_PROMPT_TEMPLATE = """你是 MCP server 安装助手。用户需要安装名为 "{server_name}" 的 MCP server。

请通过搜索互联网，找到该 MCP server 的安装和配置信息，然后输出一个 JSON 对象。

搜索策略：
1. 搜索 "{server_name} MCP server" 或 "{server_name} model context protocol"
2. 查看 GitHub 仓库的 README，找到 MCP 配置示例
3. 查看 npm / PyPI 包页面，确认包名和安装方式

输出格式（严格 JSON）：

```json
{{
  "found": true,
  "server_name": "{server_name}",
  "package_name": "package-name",
  "package_registry": "pypi",
  "command": "uvx",
  "args": ["{server_name}"],
  "env": {{
    "ENV_VAR_NAME": {{
      "description": "Description of this env var",
      "example": "https://example.com",
      "required": true,
      "sensitive": false
    }}
  }},
  "source_url": "https://github.com/..."
}}
```

字段说明：
- `found`: 是否找到该 MCP server
- `command`: 启动命令（常见: uvx, npx, node, python）
- `args`: 命令参数数组
- `env`: 环境变量定义
  - `required`: 是否必须提供
  - `sensitive`: 是否为敏感信息（如 API Token），用于决定是否在确认界面隐藏显示
- `source_url`: 信息来源 URL，供用户查验

如果找不到该 MCP server，返回：
```json
{{
  "found": false,
  "error": "未找到名为 {server_name} 的 MCP server",
  "suggestions": ["类似名称的 server 列表"]
}}
```

注意：
- 只输出 JSON，不要输出任何其他内容
- 优先使用官方文档中的配置格式
- command 优先使用 uvx (Python) 或 npx (Node.js) 等免安装运行器"""


def ai_search_server(server_name: str) -> AISearchResult | None:
    """Use AI to search for MCP server installation info.

    Returns AISearchResult or None on failure.
    """
    click.echo(f"🔍 Searching for {server_name} installation info...")

    backend = get_backend()
    prompt = INSTALL_PROMPT_TEMPLATE.format(server_name=server_name)

    result = backend.invoke(
        prompt,
        command_name="install search",
        server_name=server_name,
        show_progress=True,
        progress_message=f"Searching for {server_name}...",
    )

    if result.is_error:
        click.echo(f"AI search failed: {result.result}", err=True)
        return None

    # Parse the JSON from LLM result
    text = result.result.strip()
    parsed = _extract_json(text)
    if parsed is None:
        # Retry once with session
        if result.session_id:
            click.echo("  Retrying AI search (invalid JSON)...")
            retry_result = backend.resume(
                result.session_id,
                "你的上一次输出不是合法的 JSON。请只输出 JSON 对象，不要输出任何其他文字。",
            )
            if not retry_result.is_error:
                parsed = _extract_json(retry_result.result.strip())

    if parsed is None:
        click.echo("Error: Could not parse AI search result as JSON.", err=True)
        return None

    search_result = AISearchResult.from_dict(parsed)

    if search_result.found:
        click.echo(f"  Found: {search_result.server_name} ({search_result.package_registry})")
        if search_result.source_url:
            click.echo(f"  Source: {search_result.source_url}")
    else:
        click.echo(f"  ✗ Could not find MCP server \"{server_name}\"")
        if search_result.error:
            click.echo(f"  {search_result.error}")
        if search_result.suggestions:
            click.echo(f"  Did you mean: {', '.join(search_result.suggestions)}")

    backend.clear_session("install search", server_name)
    return search_result


def _extract_json(text: str) -> dict | None:
    """Try to extract JSON from text that may contain markdown fences."""
    # Direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try extracting from ```json ... ```
    import re
    match = re.search(r"```(?:json)?\s*\n(.*?)```", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            pass

    # Try finding { ... } block
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end > start:
        try:
            return json.loads(text[start:end + 1])
        except json.JSONDecodeError:
            pass

    return None
