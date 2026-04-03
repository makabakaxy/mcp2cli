"""Hierarchical command resolution with alias routing and JSON input support."""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import click
import yaml

from mcp2cli.cli.mapping import cli_path, extract_tools_from_yaml, load_cli_yaml
from mcp2cli.config.tool_store import load_tools
from mcp2cli.constants import CLI_DIR, RESERVED_COMMANDS


@dataclass
class AliasEntry:
    """A single entry in the global alias index."""

    server: str
    yaml_path: Path
    command_prefix: list[str]
    alias_type: str  # "canonical" | "server_alias" | "shortcut"


@dataclass
class ResolveResult:
    """Result of command resolution."""

    server: str
    tool: str
    params: dict
    cli_yaml_path: Path


def build_alias_index() -> dict[str, AliasEntry]:
    """Load all cli/*.yaml and build a global alias index.

    Priority (highest first):
      1. canonical server name (filename stem)
      2. server_aliases
      3. command_shortcuts
    """
    index: dict[str, AliasEntry] = {}

    if not CLI_DIR.exists():
        return index

    yaml_files = sorted(CLI_DIR.glob("*.yaml"))
    for yf in yaml_files:
        try:
            data = yaml.safe_load(yf.read_text(encoding="utf-8"))
        except (yaml.YAMLError, OSError):
            continue
        if not isinstance(data, dict):
            continue

        server = data.get("server", yf.stem)

        # Canonical
        if server not in RESERVED_COMMANDS:
            _try_register(index, server, AliasEntry(
                server=server, yaml_path=yf,
                command_prefix=[], alias_type="canonical",
            ))

        # Server aliases
        for alias in data.get("server_aliases", []):
            if alias in RESERVED_COMMANDS:
                continue
            _try_register(index, alias, AliasEntry(
                server=server, yaml_path=yf,
                command_prefix=[], alias_type="server_alias",
            ))

        # Command shortcuts
        for shortcut in data.get("command_shortcuts", []):
            if shortcut in RESERVED_COMMANDS:
                continue
            _try_register(index, shortcut, AliasEntry(
                server=server, yaml_path=yf,
                command_prefix=[shortcut], alias_type="shortcut",
            ))

    return index


def _try_register(
    index: dict[str, AliasEntry],
    token: str,
    entry: AliasEntry,
) -> None:
    """Register an alias entry, respecting priority."""
    priority = {"canonical": 0, "server_alias": 1, "shortcut": 2}
    if token in index:
        existing = index[token]
        if priority.get(entry.alias_type, 9) >= priority.get(existing.alias_type, 9):
            click.echo(
                f"Warning: alias '{token}' for {entry.server} conflicts with "
                f"{existing.server} ({existing.alias_type}), ignored.",
                err=True,
            )
            return
    index[token] = entry


def resolve_command(tokens: list[str]) -> ResolveResult | None:
    """Resolve a token sequence into a tool call.

    Returns ResolveResult or None if resolution fails.
    """
    if not tokens:
        return None

    first = tokens[0]
    index = build_alias_index()

    entry = index.get(first)
    if entry is None:
        click.echo(f"Error: unknown command '{first}'.", err=True)
        click.echo("Use `mcp2cli --help` to see available commands.", err=True)
        return None

    data = load_cli_yaml(entry.server)
    if data is None:
        click.echo(f"Error: could not load CLI mapping for '{entry.server}'.", err=True)
        return None

    commands = data.get("commands", {})
    remaining_tokens = entry.command_prefix + tokens[1:]

    # Walk the command tree
    node = commands
    path: list[str] = []
    consumed = 0

    for i, tok in enumerate(remaining_tokens):
        if tok.startswith("-"):
            break
        if tok.startswith("{"):
            break

        children = {k: v for k, v in node.items()
                    if not k.startswith("_") and isinstance(v, dict)}

        if tok in children:
            node = children[tok]
            path.append(tok)
            consumed = i + 1
        else:
            # Fallback: treat remaining tokens as MCP tool name
            potential_tool = tok
            tools_json = load_tools(entry.server)
            if tools_json and potential_tool in tools_json.tool_names():
                remaining_args = remaining_tokens[i + 1:]
                params = _parse_args(remaining_args, entry.server, potential_tool)
                return ResolveResult(
                    server=entry.server,
                    tool=potential_tool,
                    params=params,
                    cli_yaml_path=entry.yaml_path,
                )
            click.echo(f"Error: unknown sub-command '{tok}' under {'/'.join(path) or entry.server}.", err=True)
            _show_help(node, entry.server, path)
            return None

    # Check if we landed on a leaf (has _tool)
    tool = node.get("_tool")
    if tool:
        remaining_args = remaining_tokens[consumed:]
        params = _parse_args(remaining_args, entry.server, tool)
        return ResolveResult(
            server=entry.server,
            tool=tool,
            params=params,
            cli_yaml_path=entry.yaml_path,
        )

    # Intermediate node — show help
    _show_help(node, entry.server, path)
    return None


def _parse_args(
    tokens: list[str],
    server_name: str,
    tool_name: str,
) -> dict:
    """Parse remaining tokens into tool parameters.

    Supports --flag-name value and JSON positional argument.
    """
    json_params: dict = {}
    flag_params: dict = {}
    i = 0

    # Load input schema for type-aware parsing
    tools_json = load_tools(server_name)
    schema_props: dict = {}
    if tools_json:
        for t in tools_json.tools:
            if t.name == tool_name:
                schema_props = t.input_schema.get("properties", {})
                break

    while i < len(tokens):
        tok = tokens[i]

        if tok.startswith("{"):
            if json_params:
                click.echo("Error: only one JSON argument allowed.", err=True)
                raise SystemExit(1)
            try:
                json_params = json.loads(tok)
            except json.JSONDecodeError as e:
                click.echo(f"Error: invalid JSON argument: {e}", err=True)
                raise SystemExit(1)
            i += 1

        elif tok == "--help" or tok == "-h":
            _show_tool_help(server_name, tool_name)
            raise SystemExit(0)

        elif tok.startswith("--"):
            key = tok.lstrip("-")
            param_name = key.replace("-", "_")

            if i + 1 < len(tokens) and not tokens[i + 1].startswith("--"):
                raw_value = tokens[i + 1]
                i += 2
            else:
                raw_value = "true"
                i += 1

            # Auto-parse JSON for object/array schema types
            prop_schema = schema_props.get(param_name, {})
            prop_type = prop_schema.get("type", "string")
            if prop_type in ("object", "array") and raw_value not in ("true", "false"):
                try:
                    flag_params[param_name] = json.loads(raw_value)
                    continue
                except json.JSONDecodeError:
                    pass

            flag_params[param_name] = raw_value

        else:
            click.echo(f"Error: unexpected argument: {tok}", err=True)
            raise SystemExit(1)

    # Merge: flags override JSON
    return {**json_params, **flag_params}


def _show_help(node: dict, server_name: str, path: list[str]) -> None:
    """Show help for an intermediate command node."""
    if path:
        cmd_path = f"mcp2cli {server_name} {' '.join(path)}"
    else:
        cmd_path = f"mcp2cli {server_name}"

    desc = node.get("_description", "")
    click.echo(f"Usage: {cmd_path} <command> [OPTIONS]")
    if desc:
        click.echo(f"\n  {desc}")

    children = {k: v for k, v in node.items()
                if not k.startswith("_") and isinstance(v, dict)}
    if children:
        click.echo("\nCommands:")
        for name, child in children.items():
            child_desc = child.get("_description", "")
            tool = child.get("_tool", "")
            suffix = f"  → {tool}" if tool else ""
            click.echo(f"  {name:<20} {child_desc}{suffix}")

    click.echo(f"\nRun '{cmd_path} <command> --help' for more information.")


def _show_tool_help(server_name: str, tool_name: str) -> None:
    """Show help for a leaf command (tool)."""
    tools_json = load_tools(server_name)
    if not tools_json:
        click.echo(f"No tool information available for {server_name}.")
        return

    tool = None
    for t in tools_json.tools:
        if t.name == tool_name:
            tool = t
            break

    if not tool:
        click.echo(f"Tool '{tool_name}' not found.")
        return

    click.echo(f"  {tool.description or tool_name}\n")

    props = tool.input_schema.get("properties", {})
    required = set(tool.input_schema.get("required", []))

    if props:
        click.echo("Options:")
        for pname, pschema in props.items():
            flag_name = pname.replace("_", "-")
            ptype = pschema.get("type", "")
            pdesc = pschema.get("description", "")
            req_str = "(required)" if pname in required else ""
            default = pschema.get("default")
            def_str = f" (default: {default})" if default is not None else ""
            click.echo(f"  --{flag_name:<25} {req_str:<12} {pdesc}{def_str}")

    click.echo(
        f"\nJSON Input:\n"
        f"  mcp2cli ... '{{\"{list(props.keys())[0] if props else 'key'}\":\"value\"}}'\n"
        f"  Flags override JSON keys."
    )


def list_dynamic_commands() -> list[tuple[str, str]]:
    """Return (name, description) pairs for all registered servers."""
    if not CLI_DIR.exists():
        return []
    result = []
    for yf in sorted(CLI_DIR.glob("*.yaml")):
        try:
            data = yaml.safe_load(yf.read_text(encoding="utf-8"))
        except (yaml.YAMLError, OSError):
            continue
        if not isinstance(data, dict):
            continue
        server = data.get("server", yf.stem)
        commands = data.get("commands", {})
        groups = [k for k in commands if not k.startswith("_")]
        desc = ", ".join(groups[:3])
        if len(groups) > 3:
            desc += f", ... ({len(groups)} groups)"
        result.append((server, desc))
    return result
