"""AI-powered Skill file generation."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import click
import yaml

from mcp2cli.cli.mapping import cli_path, cli_yaml_hash
from mcp2cli.config.tool_store import load_tools, tools_path
from mcp2cli.constants import TEMPLATES_DIR
from mcp2cli.generator.llm_backend import get_backend
from mcp2cli.generator.validator import validate_skill
from mcp2cli.utils import skills_path
from mcp2cli.utils.file_ops import parse_frontmatter

MAX_RETRIES = 1


def generate_skill(
    server_name: str,
    output_dir: Path | None = None,
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

    out_dir = output_dir or skills_path(server_name)
    skill_md = out_dir / "SKILL.md"

    # Compute source_cli_hash
    source_hash = cli_yaml_hash(server_name)

    # Up-to-date check
    if skill_md.exists():
        existing_hash = parse_frontmatter(skill_md.read_text(encoding="utf-8"))
        existing_hash = existing_hash.get("source_cli_hash") if existing_hash else None
        if existing_hash and existing_hash == source_hash:
            click.echo(f"Skill files are up-to-date (source_cli_hash matches). Nothing to do.")
            return True

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

    click.echo(f"  📦 Written to {output_dir}")


def _build_prompt(
    server_name: str,
    source_version: str,
    source_cli_hash: str,
    generated_at: str,
    output_dir: Path,
) -> str:
    skill_rule_path = TEMPLATES_DIR / "skill_gen_skill.md"
    skill_example_path = TEMPLATES_DIR / "skill_gen_example.md"
    cli_yaml_path = cli_path(server_name)
    tools_file = tools_path(server_name)

    output_dir.mkdir(parents=True, exist_ok=True)

    return (
        f"You are the Skill file generator for mcp2cli. Your task is to generate a set of agent-usable Skill files (SKILL.md + reference + examples) for an MCP server.\n\n"
        f"Follow these steps:\n\n"
        f"Step 1: Read the generation rules\n"
        f"Read file {skill_rule_path} to understand the Skill file structure requirements, conciseness principles, and parameter extraction methods.\n\n"
        f"Step 2: Read the output example\n"
        f"Read file {skill_example_path} to understand the expected output format for SKILL.md, reference, and examples.\n\n"
        f"Step 3: Get the command tree\n"
        f"Read file {cli_yaml_path}, the hierarchical command mapping file for MCP server \"{server_name}\", which contains:\n"
        f"- commands tree structure (_tool points to the original MCP tool name)\n"
        f"- server_aliases (server name aliases)\n"
        f"- command_shortcuts (command shortcuts)\n\n"
        f"Step 4: Get tool schemas\n"
        f"Read file {tools_file} to get the name, description, and inputSchema (parameter definitions) for all tools.\n\n"
        f"Step 5: Generate files\n"
        f"Generate the following files under {output_dir}:\n\n"
        f"a) SKILL.md — main file (≤ 800 tokens)\n"
        f"   - frontmatter must include the following fields:\n"
        f"     - name: \"{server_name}\"\n"
        f"     - description: one-sentence English summary with core capability keywords\n"
        f"     - source_version: \"{source_version}\"\n"
        f"     - source_cli_hash: \"{source_cli_hash}\"\n"
        f"     - generated_at: \"{generated_at}\"\n"
        f"   - Shortcuts table: list all command_shortcuts and server_aliases\n"
        f"   - Commands table: grouped by group, up to 8 high-frequency commands per group\n"
        f"   - Prefer the shortest form from command_shortcuts for command paths\n"
        f"   - Discover Parameters section: hint at --help and reference/\n"
        f"   - User Notes section: fixed MUST READ link to users/skill.md and ~/.agents/mcp2cli/servers.yaml\n\n"
        f"b) reference/<group>.md or reference/<group>-<resource>.md\n"
        f"   - 1-3 simple usage examples per command (demonstrating required parameters)\n"
        f"   - \"Also supports\" line listing optional parameter names (extracted from inputSchema, kebab-case)\n"
        f"   - Hint at --help at the end\n"
        f"   - Single file ≤ 200 lines\n\n"
        f"c) users/workflows.md — only create on first generation (skip if the file already exists)\n"
        f"   - 5-10 common usage scenarios\n"
        f"   - Include multi-step workflows\n"
        f"   - Use the shortest command forms\n\n"
        f"Step 6: Write files\n"
        f"Write all files to {output_dir}. Ensure the directory structure is correct.\n"
        f"Remember to create the users/ directory, users/.gitkeep, and users/skill.md (empty template).\n"
        f"If {output_dir}/users/workflows.md already exists, do not overwrite it.\n\n"
        f"Important constraints:\n"
        f"- SKILL.md must be concise, ≤ 800 tokens\n"
        f"- The source_cli_hash in the frontmatter must use the value given above: \"{source_cli_hash}\"; do not compute it yourself\n"
        f"- Prefer the shortest form from command_shortcuts in command tables\n"
        f"- Parameter names in reference must be extracted from inputSchema and use kebab-case (e.g. project_key → --project-key)\n"
        f"- Do not output explanations; execute the steps directly\n"
        f"- After completion, output a one-line summary: \"Generated: SKILL.md (N tokens) + M reference files + users/workflows.md\"\n"
    )


def _build_retry_prompt(server_name: str, output_dir: Path, errors: list[str]) -> str:
    error_text = "\n".join(f"- {e}" for e in errors)
    return (
        f"The Skill files you generated last time have the following issues:\n\n"
        f"{error_text}\n\n"
        f"Please fix the issues above and rewrite the files to {output_dir}.\n"
        f"Note:\n"
        f"- You have already read the rules/example/YAML/tools files; no need to re-read them\n"
        f"- Keep all correct parts unchanged; only fix the listed issues\n"
        f"- After fixing, output a summary: \"Fixed: <brief description of what was fixed>\"\n"
    )


def _build_resume_prompt(server_name: str, output_dir: Path) -> str:
    return (
        f"Please continue the unfinished Skill file generation task.\n"
        f"Target server: {server_name}\n"
        f"Output directory: {output_dir}\n"
        f"If the files have already been generated, check whether they are complete. If not, continue from where the task was interrupted.\n"
    )
