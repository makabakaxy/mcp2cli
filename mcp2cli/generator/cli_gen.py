"""AI-powered CLI command tree generation."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import click
import yaml

from mcp2cli.cli.mapping import cli_path, extract_tools_from_yaml, print_command_tree
from mcp2cli.config.tool_store import load_tools, tools_path
from mcp2cli.constants import CLI_DIR, TEMPLATES_DIR
from mcp2cli.generator.llm_backend import ClaudeCLIBackend, get_backend
from mcp2cli.generator.validator import validate_cli_yaml

MAX_RETRIES = 2


def generate_cli(server_name: str, merge: bool = False) -> bool:
    """Generate CLI command tree YAML via LLM.

    Returns True on success.
    """
    tools_json = load_tools(server_name)
    if tools_json is None:
        click.echo(
            f"Error: tools/{server_name}.json not found.\n"
            f"Run `mcp2cli scan {server_name}` first.",
            err=True,
        )
        return False

    click.echo(f"Generating CLI command tree for {server_name} ({len(tools_json.tools)} tools)...")

    backend = get_backend()
    command_name = "generate cli"

    # Check for unfinished session
    existing_session = backend.find_session(command_name, server_name)
    if existing_session:
        if click.confirm("Found unfinished session. Resume?", default=True):
            click.echo(f"Resuming session {existing_session[:12]}...")
            result = backend.resume(
                existing_session,
                _build_resume_prompt(server_name),
                show_progress=True,
                progress_message="Resuming generation...",
            )
            if not result.is_error:
                return _post_validate(server_name, backend, result.session_id, command_name)
        existing_session = None

    # Build and send prompt
    prompt = _build_prompt(server_name, tools_json.version, merge)
    result = backend.invoke(
        prompt,
        command_name=command_name,
        server_name=server_name,
        show_progress=True,
        progress_message=f"Generating CLI tree for {server_name}...",
    )

    if result.is_error:
        click.echo(f"LLM error: {result.result}", err=True)
        return False

    return _post_validate(server_name, backend, result.session_id, command_name)


def _post_validate(
    server_name: str,
    backend: ClaudeCLIBackend,
    session_id: str | None,
    command_name: str,
) -> bool:
    """Run program-side validation with retry."""
    for attempt in range(1, MAX_RETRIES + 1):
        errors = validate_cli_yaml(server_name)
        if not errors:
            click.echo("Program validation passed ✓")
            # Print tree preview
            data = yaml.safe_load(cli_path(server_name).read_text(encoding="utf-8"))
            if data:
                yaml_tools = extract_tools_from_yaml(data)
                click.echo(f"  Coverage: {len(yaml_tools)} tools mapped")
                print_command_tree(data, server_name)
            click.echo(f"Written to {cli_path(server_name)}")
            backend.clear_session(command_name, server_name)
            return True

        click.echo(f"Program validation failed (attempt {attempt}/{MAX_RETRIES}):")
        for e in errors:
            click.echo(f"  - {e}")

        if attempt >= MAX_RETRIES or session_id is None:
            click.echo("Validation failed. Please fix manually or re-run.", err=True)
            return False

        click.echo("Retrying with error context...")
        error_prompt = _build_retry_prompt(server_name, errors)
        result = backend.resume(session_id, error_prompt, show_progress=True, progress_message="Fixing validation errors...")
        if result.is_error:
            click.echo(f"LLM retry error: {result.result}", err=True)
            return False

    return False


def _build_prompt(server_name: str, version: str | None, merge: bool) -> str:
    skill_path = TEMPLATES_DIR / "cli_gen_skill.md"
    example_path = TEMPLATES_DIR / "cli_gen_example.md"
    tools_file = tools_path(server_name)
    output_path = cli_path(server_name)

    CLI_DIR.mkdir(parents=True, exist_ok=True)

    if merge:
        existing_cli = cli_path(server_name)
        return (
            f"你是 mcp2cli 的 CLI 命令树生成器。你的任务是为 MCP server 新增的 tool 扩展已有的命令树。\n\n"
            f"请按以下步骤执行：\n\n"
            f"第一步：阅读生成规则\n"
            f"读取文件 {skill_path} ，理解命令树的分层原则、命名规范和格式要求。\n\n"
            f"第二步：阅读输出示例\n"
            f"读取文件 {example_path} ，理解期望的 YAML 输出格式和风格。\n\n"
            f"第三步：获取 tool 列表\n"
            f"读取文件 {tools_file} ，这是 MCP server \"{server_name}\" 的所有 tool 定义。\n\n"
            f"第四步：读取已有命令树\n"
            f"读取文件 {existing_cli} ，这是当前已有的命令映射文件。\n\n"
            f"第五步：差异分析\n"
            f"对比 tool 列表和已有命令树：\n"
            f"- 找出已有命令树中已映射的 tool（保持不变）\n"
            f"- 找出 tool 列表中新增的、尚未映射的 tool\n"
            f"- 找出已有命令树中引用了但 tool 列表中已不存在的 tool（需删除）\n\n"
            f"第六步：增量生成\n"
            f"将新增 tool 合并到已有命令树中：\n"
            f"- 保留已有结构、描述、别名、示例不变\n"
            f"- 仅新增 tool 的映射节点\n"
            f"- 将 generated_by 改为 \"ai-merge\"\n"
            f"- 更新 generated_at 时间戳\n"
            f"- 如有已不存在的 tool，直接删除对应的叶子节点\n\n"
            f"第七步：写入文件\n"
            f"将合并后的完整 YAML 写入 {output_path} 。\n\n"
            f"第八步：自验\n"
            f"执行命令 mcp2cli validate {server_name} ，检查合并后的 YAML 是否符合所有规则。\n"
            f"如果校验报错，根据输出信息修复 YAML 后重新写入 {output_path}，再次执行 mcp2cli validate {server_name} 直到校验通过。\n\n"
            f"重要约束：\n"
            f"- 已有结构必须完整保留，不可重组、不可修改描述\n"
            f"- 仅新增节点遵循 cli_gen_skill.md 的规则\n"
            f"- 完成后输出摘要：\"Merged: X new tools added, Y existing preserved, Z removed\"\n"
        )

    return (
        f"你是 mcp2cli 的 CLI 命令树生成器。你的任务是将 MCP server 的扁平 tool 列表组织为层级式命令树，输出一个 YAML 映射文件。\n\n"
        f"请按以下步骤执行：\n\n"
        f"第一步：阅读生成规则\n"
        f"读取文件 {skill_path} ，理解命令树的分层原则、命名规范和格式要求。\n\n"
        f"第二步：阅读输出示例\n"
        f"读取文件 {example_path} ，理解期望的 YAML 输出格式和风格。\n\n"
        f"第三步：获取 tool 列表\n"
        f"读取文件 {tools_file} ，这是 MCP server \"{server_name}\" 的所有 tool 定义，包含 tool 名称、描述和 input_schema。\n\n"
        f"第四步：生成命令树\n"
        f"根据规则和示例，将所有 tool 组织为层级命令树。确保：\n"
        f"- 每个 tool 都被映射到命令树中（覆盖率 100%）\n"
        f"- 遵循 cli_gen_skill.md 中的所有规则\n"
        f"- YAML 格式与 cli_gen_example.md 保持一致\n\n"
        f"第五步：写入文件\n"
        f"将生成的完整 YAML 内容写入 {output_path} 。\n\n"
        f"第六步：自验\n"
        f"执行命令 mcp2cli validate {server_name} ，检查生成的 YAML 是否符合所有规则。\n"
        f"如果校验报错，根据输出信息修复 YAML 后重新写入 {output_path}，再次执行 mcp2cli validate {server_name} 直到校验通过。\n\n"
        f"重要约束：\n"
        f"- 不要输出解释说明，直接执行上述步骤\n"
        f"- 写入的文件必须是合法的 YAML\n"
        f"- 所有 tool 必须被覆盖，不能遗漏\n"
        f"- 完成后输出一行摘要：\"Generated: X tools mapped to Y commands\"\n"
    )


def _build_retry_prompt(server_name: str, errors: list[str]) -> str:
    output_path = cli_path(server_name)
    error_text = "\n".join(f"- {e}" for e in errors)
    return (
        f"你上一次生成并写入 {output_path} 的 YAML 存在以下问题：\n\n"
        f"{error_text}\n\n"
        f"请修复以上问题后重新写入 {output_path} 。\n"
        f"注意：\n"
        f"- 你已经读取过 skill/example/tools 文件，不需要重新读取\n"
        f"- 保持其他正确部分不变，只修复列出的问题\n"
        f"- 修复后执行 mcp2cli validate {server_name} 验证\n"
        f"- 修复后输出摘要：\"Fixed: <修复内容简述>\"\n"
    )


def _build_resume_prompt(server_name: str) -> str:
    return (
        f"请继续上次未完成的 CLI 命令树生成任务。\n"
        f"目标 server: {server_name}\n"
        f"如果 YAML 文件已经生成，请执行 mcp2cli validate {server_name} 验证。\n"
        f"如果未生成，请从上次中断的地方继续。\n"
    )
