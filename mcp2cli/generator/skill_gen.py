"""AI-powered Skill file generation."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import click
import yaml

from mcp2cli.cli.mapping import cli_path, cli_yaml_hash
from mcp2cli.config.tool_store import load_tools, tools_path
from mcp2cli.constants import SKILLS_DIR, TEMPLATES_DIR
from mcp2cli.generator.llm_backend import get_backend
from mcp2cli.generator.validator import validate_skill

MAX_RETRIES = 1


def generate_skill(
    server_name: str,
    output_dir: Path | None = None,
    full: bool = False,
) -> bool:
    """Generate Skill files (SKILL.md + reference/ + users/workflows.md) via LLM.

    Returns True on success.
    """
    cli_yaml = cli_path(server_name)
    if not cli_yaml.exists():
        click.echo(
            f"Error: cli/{server_name}.yaml not found.\n"
            f"Run `mcp2cli generate cli {server_name}` first.",
            err=True,
        )
        return False

    tools_json = load_tools(server_name)
    if tools_json is None:
        click.echo(
            f"Error: tools/{server_name}.json not found.\n"
            f"Run `mcp2cli scan {server_name}` first.",
            err=True,
        )
        return False

    out_dir = output_dir or (SKILLS_DIR / server_name)
    skill_md = out_dir / "SKILL.md"

    # Compute source_cli_hash
    source_hash = cli_yaml_hash(server_name)

    # Mode detection
    if skill_md.exists() and not full:
        existing_hash = _read_existing_hash(skill_md)
        if existing_hash and existing_hash == source_hash:
            click.echo(f"Skill files are up-to-date (source_cli_hash matches). Nothing to do.")
            return True
        incremental = True
        click.echo(f"Updating skill files (incremental)...")
    else:
        incremental = False
        click.echo(f"Generating skill files for {server_name}...")

    # Read CLI YAML for version
    cli_data = yaml.safe_load(cli_yaml.read_text(encoding="utf-8"))
    source_version = cli_data.get("version") or "null"

    backend = get_backend()
    command_name = "generate skill"

    # Check for unfinished session
    existing_session = backend.find_session(command_name, server_name)
    if existing_session:
        if click.confirm("Found unfinished session. Resume?", default=True):
            result = backend.resume(
                existing_session,
                _build_resume_prompt(server_name, out_dir),
                show_progress=True,
                progress_message="Resuming skill generation...",
            )
            if not result.is_error:
                return _post_validate(server_name, out_dir, backend, result.session_id, command_name)

    # Build and send prompt
    generated_at = datetime.now(timezone.utc).isoformat()
    prompt = _build_prompt(
        server_name=server_name,
        source_version=source_version,
        source_cli_hash=source_hash or "",
        generated_at=generated_at,
        output_dir=out_dir,
        incremental=incremental,
    )

    result = backend.invoke(
        prompt,
        command_name=command_name,
        server_name=server_name,
        show_progress=True,
        progress_message=f"Generating skill files for {server_name}...",
    )

    if result.is_error:
        click.echo(f"LLM error: {result.result}", err=True)
        return False

    return _post_validate(server_name, out_dir, backend, result.session_id, command_name)


def _post_validate(
    server_name: str,
    output_dir: Path,
    backend,
    session_id: str | None,
    command_name: str,
) -> bool:
    """Run program-side validation with retry."""
    for attempt in range(1, MAX_RETRIES + 2):
        errors = validate_skill(server_name, output_dir)

        # Filter warnings from blocking errors
        hard_errors = [e for e in errors if not e.startswith("Warning:")]

        if not hard_errors:
            if errors:
                for w in errors:
                    click.echo(f"  {w}")
            _print_summary(server_name, output_dir)
            backend.clear_session(command_name, server_name)
            return True

        click.echo(f"Skill validation issues (attempt {attempt}/{MAX_RETRIES + 1}):")
        for e in errors:
            click.echo(f"  - {e}")

        if attempt > MAX_RETRIES or session_id is None:
            click.echo("Validation failed. Please fix manually or re-run with --full.", err=True)
            return False

        click.echo("Retrying with error context...")
        error_prompt = _build_retry_prompt(server_name, output_dir, errors)
        result = backend.resume(session_id, error_prompt, show_progress=True, progress_message="Fixing skill validation errors...")
        if result.is_error:
            click.echo(f"LLM retry error: {result.result}", err=True)
            return False

    return False


def _print_summary(server_name: str, output_dir: Path) -> None:
    skill_md = output_dir / "SKILL.md"
    if skill_md.exists():
        body = skill_md.read_text(encoding="utf-8")
        tokens = len(body) // 4
        click.echo(f"  SKILL.md → ~{tokens} tokens")

    ref_dir = output_dir / "reference"
    if ref_dir.exists():
        ref_files = list(ref_dir.glob("*.md"))
        click.echo(f"  reference/ → {len(ref_files)} files")

    workflows = output_dir / "users" / "workflows.md"
    if workflows.exists():
        click.echo(f"  users/workflows.md → generated")

    click.echo(f"Written to {output_dir}")


def _build_prompt(
    server_name: str,
    source_version: str,
    source_cli_hash: str,
    generated_at: str,
    output_dir: Path,
    incremental: bool,
) -> str:
    skill_rule_path = TEMPLATES_DIR / "skill_gen_skill.md"
    skill_example_path = TEMPLATES_DIR / "skill_gen_example.md"
    cli_yaml_path = cli_path(server_name)
    tools_file = tools_path(server_name)

    output_dir.mkdir(parents=True, exist_ok=True)

    if incremental:
        return (
            f"你是 mcp2cli 的 Skill 文件生成器。你的任务是更新已有的 Skill 文件，使其与最新的 CLI 命令树保持一致。\n\n"
            f"请按以下步骤执行：\n\n"
            f"第一步：阅读生成规则\n"
            f"读取文件 {skill_rule_path}，理解 Skill 文件的结构要求和精简原则。\n\n"
            f"第二步：获取当前命令树\n"
            f"读取文件 {cli_yaml_path}，这是 MCP server \"{server_name}\" 的最新层级命令映射文件。\n\n"
            f"第三步：获取 tool schema\n"
            f"读取文件 {tools_file}，获取所有 tool 的 inputSchema（参数定义）。\n\n"
            f"第四步：读取已有 Skill 文件\n"
            f"读取以下已有文件：\n"
            f"- {output_dir}/SKILL.md\n"
            f"- {output_dir}/reference/ 下的所有 .md 文件\n\n"
            f"第五步：差异分析\n"
            f"对比当前 CLI YAML 命令树与已有 Skill 文件中的命令列表：\n"
            f"- 找出新增的命令（CLI 中有，但 SKILL.md 的 Commands 表中没有）\n"
            f"- 找出已删除的命令（SKILL.md 中有，但 CLI 中已不存在）\n"
            f"- 找出描述发生变化的命令\n"
            f"- 检查 reference/ 文件中是否有引用了已删除命令的段落\n\n"
            f"第六步：增量修改\n"
            f"仅修改受差异影响的部分，保留其他内容不变：\n"
            f"- SKILL.md：在 Commands 表中增删命令行，保持已有命令的 Example 和格式不变\n"
            f"- reference/：为新增命令添加段落（含示例和参数），删除已移除命令的段落\n"
            f"- frontmatter：更新 source_cli_hash 为 \"{source_cli_hash}\"，source_version 为 \"{source_version}\"，generated_at 为 \"{generated_at}\"\n\n"
            f"第七步：写入文件\n"
            f"将修改后的文件写入 {output_dir}。未修改的文件不需要重写。\n\n"
            f"重要约束：\n"
            f"- 已有的命令描述、示例、格式不可随意修改——只改差异部分\n"
            f"- 新增命令的示例和参数需从 tools JSON 的 inputSchema 提取\n"
            f"- SKILL.md 总 token 数仍需 ≤ 800\n"
            f"- frontmatter 中的 source_cli_hash 必须使用上面给定的值 \"{source_cli_hash}\"\n"
            f"- 不要输出解释说明，直接执行上述步骤\n"
            f"- users/ 目录下的文件不要触碰\n"
            f"- 完成后输出摘要：\"Updated: X new commands added, Y removed, Z preserved\"\n"
        )

    return (
        f"你是 mcp2cli 的 Skill 文件生成器。你的任务是为 MCP server 生成 agent 可用的 Skill 文件集合（SKILL.md + reference + examples）。\n\n"
        f"请按以下步骤执行：\n\n"
        f"第一步：阅读生成规则\n"
        f"读取文件 {skill_rule_path}，理解 Skill 文件的结构要求、精简原则和参数提取方法。\n\n"
        f"第二步：阅读输出示例\n"
        f"读取文件 {skill_example_path}，理解 SKILL.md、reference 和 examples 的期望输出格式。\n\n"
        f"第三步：获取命令树\n"
        f"读取文件 {cli_yaml_path}，这是 MCP server \"{server_name}\" 的层级命令映射文件，包含：\n"
        f"- commands 树结构（_tool 指向 MCP tool 原始名称）\n"
        f"- server_aliases（server 名称别名）\n"
        f"- command_shortcuts（命令快捷方式）\n\n"
        f"第四步：获取 tool schema\n"
        f"读取文件 {tools_file}，获取所有 tool 的名称、描述和 inputSchema（参数定义）。\n\n"
        f"第五步：生成文件\n"
        f"在 {output_dir} 下生成以下文件：\n\n"
        f"a) SKILL.md — 主文件（≤ 800 tokens）\n"
        f"   - frontmatter 必须包含以下字段：\n"
        f"     - name: \"{server_name}\"\n"
        f"     - description: 英文一句话概述，含核心能力关键词\n"
        f"     - source_version: \"{source_version}\"\n"
        f"     - source_cli_hash: \"{source_cli_hash}\"\n"
        f"     - generated_at: \"{generated_at}\"\n"
        f"   - Shortcuts 表：列出所有 command_shortcuts 和 server_aliases\n"
        f"   - Commands 表：按 group 分段，每段最多 8 个高频命令\n"
        f"   - 命令路径优先使用 command_shortcuts 的最短形式\n"
        f"   - Discover Parameters 段落：提示 --help 和 reference/\n"
        f"   - User Notes 段落：固定 MUST READ 链接指向 users/SKILL.md\n\n"
        f"b) reference/<group>.md 或 reference/<group>-<resource>.md\n"
        f"   - 每个命令给 1-3 个简单使用示例（展示 required 参数）\n"
        f"   - \"Also supports\" 行列出 optional 参数名（从 inputSchema 提取，kebab-case）\n"
        f"   - 末尾提示 --help\n"
        f"   - 单文件 ≤ 200 行\n\n"
        f"c) users/workflows.md — 仅在首次生成时创建（若文件已存在则跳过）\n"
        f"   - 5-10 个常见使用场景\n"
        f"   - 包含多步骤工作流\n"
        f"   - 使用最短命令形式\n\n"
        f"第六步：写入文件\n"
        f"将所有文件写入 {output_dir}。确保目录结构正确。\n"
        f"注意创建 users/ 目录和 users/.gitkeep 和 users/SKILL.md （内容为空模板）。\n"
        f"如果 {output_dir}/users/workflows.md 已存在，不要覆盖它。\n\n"
        f"重要约束：\n"
        f"- SKILL.md 必须精简，≤ 800 tokens\n"
        f"- frontmatter 中的 source_cli_hash 必须使用上面给定的值 \"{source_cli_hash}\"，不要自行计算\n"
        f"- 命令表优先使用 command_shortcuts 的最短形式\n"
        f"- reference 中的参数名从 inputSchema 提取，使用 kebab-case（如 project_key → --project-key）\n"
        f"- 不要输出解释说明，直接执行上述步骤\n"
        f"- 完成后输出一行摘要：\"Generated: SKILL.md (N tokens) + M reference files + users/workflows.md\"\n"
    )


def _build_retry_prompt(server_name: str, output_dir: Path, errors: list[str]) -> str:
    error_text = "\n".join(f"- {e}" for e in errors)
    return (
        f"你上一次生成的 Skill 文件存在以下问题：\n\n"
        f"{error_text}\n\n"
        f"请修复以上问题后重新写入 {output_dir}。\n"
        f"注意：\n"
        f"- 你已经读取过规则/示例/YAML/tools 文件，不需要重新读取\n"
        f"- 保持其他正确部分不变，只修复列出的问题\n"
        f"- 修复后输出摘要：\"Fixed: <修复内容简述>\"\n"
    )


def _build_resume_prompt(server_name: str, output_dir: Path) -> str:
    return (
        f"请继续上次未完成的 Skill 文件生成任务。\n"
        f"目标 server: {server_name}\n"
        f"输出目录: {output_dir}\n"
        f"如果文件已经生成，请检查是否完整。如果未生成，请从上次中断的地方继续。\n"
    )


def _read_existing_hash(skill_md: Path) -> str | None:
    """Read source_cli_hash from SKILL.md frontmatter."""
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None
    end = text.find("---", 3)
    if end == -1:
        return None
    try:
        fm = yaml.safe_load(text[3:end])
        return fm.get("source_cli_hash") if isinstance(fm, dict) else None
    except yaml.YAMLError:
        return None
