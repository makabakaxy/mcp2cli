"""Read and write CLI mapping YAML files."""

from __future__ import annotations

import hashlib
from pathlib import Path

import yaml

from mcp2cli.constants import CLI_DIR
from mcp2cli.utils import safe_filename


def cli_path(server_name: str) -> Path:
    return CLI_DIR / f"{safe_filename(server_name)}.yaml"


def load_cli_yaml(server_name: str) -> dict | None:
    path = cli_path(server_name)
    if not path.exists():
        return None
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError:
        return None


def save_cli_yaml(server_name: str, data: dict) -> Path:
    CLI_DIR.mkdir(parents=True, exist_ok=True)
    path = cli_path(server_name)
    path.write_text(yaml.dump(data, allow_unicode=True, default_flow_style=False, sort_keys=False), encoding="utf-8")
    return path


def cli_yaml_hash(server_name: str) -> str | None:
    """Compute SHA-256 first 8 hex chars of cli/<server>.yaml content."""
    path = cli_path(server_name)
    if not path.exists():
        return None
    content = path.read_bytes()
    return hashlib.sha256(content).hexdigest()[:8]


def extract_tools_from_yaml(data: dict) -> set[str]:
    """Extract all _tool values from a CLI YAML dict."""
    tools: set[str] = set()

    def _walk(node: dict) -> None:
        for key, value in node.items():
            if key.startswith("_"):
                if key == "_tool" and isinstance(value, str):
                    tools.add(value)
                continue
            if isinstance(value, dict):
                _walk(value)

    commands = data.get("commands", {})
    if isinstance(commands, dict):
        _walk(commands)
    return tools


def print_command_tree(data: dict, server_name: str) -> None:
    """Print a visual command tree."""
    commands = data.get("commands", {})

    def _print_node(node: dict, prefix: str = "", is_last: bool = True, parent_prefix: str = "") -> None:
        items = [(k, v) for k, v in node.items() if not k.startswith("_") and isinstance(v, dict)]
        for i, (key, value) in enumerate(items):
            last = i == len(items) - 1
            connector = "└── " if last else "├── "
            child_prefix = parent_prefix + ("    " if last else "│   ")

            tool = value.get("_tool")
            if tool:
                print(f"{parent_prefix}{connector}{key:<15} → {tool}")
            else:
                print(f"{parent_prefix}{connector}{key}")
                _print_node(value, prefix=key, is_last=last, parent_prefix=child_prefix)

    print(server_name)
    _print_node(commands)
