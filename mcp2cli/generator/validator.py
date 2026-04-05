"""Validation logic for CLI YAML and Skill files."""

from __future__ import annotations

import re
from pathlib import Path

import yaml

from mcp2cli.cli.mapping import cli_path, cli_yaml_hash, extract_tools_from_yaml
from mcp2cli.config.tool_store import load_tools
from mcp2cli.constants import RESERVED_COMMANDS
from mcp2cli.utils import safe_filename, skills_path
from mcp2cli.utils.file_ops import ensure_users_dir, parse_frontmatter, strip_frontmatter


# ---------------------------------------------------------------------------
# CLI YAML Validation
# ---------------------------------------------------------------------------

def validate_cli_yaml(server_name: str) -> list[str]:
    """Validate cli/<server>.yaml. Returns list of error strings (empty = valid)."""
    errors: list[str] = []
    path = cli_path(server_name)

    if not path.exists():
        return [f"CLI file not found: {path}"]

    try:
        text = path.read_text(encoding="utf-8")
        data = yaml.safe_load(text)
    except yaml.YAMLError as e:
        return [f"YAML syntax error: {e}"]

    if not isinstance(data, dict):
        return ["YAML root must be a mapping"]

    # Structure checks
    if "server" not in data:
        errors.append("Missing top-level 'server' field")
    if "commands" not in data:
        errors.append("Missing top-level 'commands' field")
        return errors

    commands = data["commands"]
    if not isinstance(commands, dict) or not commands:
        errors.append("'commands' must be a non-empty mapping")
        return errors

    # Walk the tree
    _validate_tree(commands, [], errors)

    # Tool coverage
    tools_json = load_tools(server_name)
    if tools_json:
        yaml_tools = extract_tools_from_yaml(data)
        json_tools = tools_json.tool_names()

        missing = json_tools - yaml_tools
        invalid = yaml_tools - json_tools

        if missing:
            errors.append(f"Missing tools (in JSON but not YAML): {sorted(missing)}")
        if invalid:
            errors.append(f"Invalid tools (in YAML but not JSON): {sorted(invalid)}")

        # Duplicate check
        all_tool_refs = _collect_all_tools(commands)
        seen: dict[str, int] = {}
        for t in all_tool_refs:
            seen[t] = seen.get(t, 0) + 1
        dups = [t for t, c in seen.items() if c > 1]
        if dups:
            errors.append(f"Duplicate tool mappings: {dups}")

    # Command path checks
    paths = _collect_paths(commands, [])
    path_strs = ["/".join(p) for p in paths]
    if len(path_strs) != len(set(path_strs)):
        errors.append("Duplicate command paths detected")

    for p in paths:
        if len(p) > 4:
            errors.append(f"Path depth > 4: {'/'.join(p)}")

    # Shortcut conflict check
    shortcuts = data.get("command_shortcuts", [])
    if isinstance(shortcuts, list):
        for s in shortcuts:
            if s in RESERVED_COMMANDS:
                errors.append(f"Shortcut '{s}' conflicts with reserved command")

    return errors


def _validate_tree(node: dict, path: list[str], errors: list[str]) -> None:
    """Recursively validate command tree structure."""
    has_tool = "_tool" in node
    children = {k: v for k, v in node.items() if not k.startswith("_") and isinstance(v, dict)}

    if has_tool and children:
        errors.append(f"Node at {'/'.join(path)} has both _tool and children")

    if not has_tool and not children:
        if path:
            errors.append(f"Leaf node at {'/'.join(path)} missing _tool field")

    if not has_tool and "_description" not in node and path:
        errors.append(f"Intermediate node at {'/'.join(path)} missing _description")

    for key, value in node.items():
        if key.startswith("_"):
            continue
        if not re.match(r"^[a-z][a-z0-9-]*$", key):
            errors.append(f"Invalid command name '{key}' at {'/'.join(path)} (must be lowercase, a-z0-9-)")
        if isinstance(value, dict):
            _validate_tree(value, path + [key], errors)


def _collect_all_tools(node: dict) -> list[str]:
    tools: list[str] = []
    for key, value in node.items():
        if key == "_tool" and isinstance(value, str):
            tools.append(value)
        elif isinstance(value, dict) and not key.startswith("_"):
            tools.extend(_collect_all_tools(value))
    return tools


def _collect_paths(node: dict, prefix: list[str]) -> list[list[str]]:
    paths: list[list[str]] = []
    for key, value in node.items():
        if key.startswith("_"):
            continue
        if isinstance(value, dict):
            current = prefix + [key]
            if "_tool" in value:
                paths.append(current)
            else:
                paths.extend(_collect_paths(value, current))
    return paths


# ---------------------------------------------------------------------------
# Skill File Validation
# ---------------------------------------------------------------------------

def validate_skill(server_name: str, output_dir: Path | None = None) -> list[str]:
    """Validate skill files for a server. Returns list of error strings."""
    errors: list[str] = []
    skill_dir = output_dir or skills_path(server_name)

    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return [f"SKILL.md not found in {skill_dir}"]

    text = skill_md.read_text(encoding="utf-8")

    # Frontmatter check
    fm = parse_frontmatter(text)
    if fm is None:
        errors.append("SKILL.md missing YAML frontmatter")
    else:
        if "name" not in fm:
            errors.append("Frontmatter missing 'name'")
        elif safe_filename(fm["name"]) != safe_filename(server_name):
            errors.append(f"Frontmatter name '{fm['name']}' != server '{server_name}'")
        if not fm.get("description"):
            errors.append("Frontmatter missing or empty 'description'")
        if "source_cli_hash" not in fm:
            errors.append("Frontmatter missing 'source_cli_hash'")
        if "source_version" not in fm:
            errors.append("Frontmatter missing 'source_version'")

    # source_cli_hash freshness
    if fm and "source_cli_hash" in fm:
        current_hash = cli_yaml_hash(server_name)
        if current_hash and fm["source_cli_hash"] != current_hash:
            errors.append(
                f"source_cli_hash mismatch: skill has '{fm['source_cli_hash']}', "
                f"current CLI YAML hash is '{current_hash}'"
            )

    # Token estimate (rough: ~4 chars per token)
    body = strip_frontmatter(text)
    estimated_tokens = len(body) // 4
    if estimated_tokens > 1200:
        errors.append(f"SKILL.md estimated at {estimated_tokens} tokens (hard limit: 1200)")
    elif estimated_tokens > 800:
        errors.append(f"Warning: SKILL.md at ~{estimated_tokens} tokens (target: ≤800)")

    # Reference directory
    ref_dir = skill_dir / "reference"
    if not ref_dir.exists() or not list(ref_dir.glob("*.md")):
        errors.append("reference/ directory missing or empty")

    # Users directory (create if missing, not an error)
    ensure_users_dir(skill_dir)

    # Workflows placeholder (create if missing, not an error — LLM fills on first gen)
    workflows_md = skill_dir / "users" / "workflows.md"
    if not workflows_md.exists():
        workflows_md.write_text(
            "# Common Workflow Examples\n\n"
            "<!-- Multi-step workflow examples will be generated here on first run. -->\n"
            "<!-- This file is never overwritten by mcp2cli generate/update. -->\n",
            encoding="utf-8",
        )

    return errors
