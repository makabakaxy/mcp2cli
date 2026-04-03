"""Manage tools/<server>.json files."""

from __future__ import annotations

import json
from pathlib import Path

from mcp2cli.config.models import ToolsJSON
from mcp2cli.constants import TOOLS_DIR


def tools_path(server_name: str) -> Path:
    return TOOLS_DIR / f"{server_name}.json"


def load_tools(server_name: str) -> ToolsJSON | None:
    path = tools_path(server_name)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return ToolsJSON.from_dict(data)
    except (json.JSONDecodeError, KeyError):
        return None


def save_tools(tools_json: ToolsJSON) -> Path:
    TOOLS_DIR.mkdir(parents=True, exist_ok=True)
    path = tools_path(tools_json.server)
    path.write_text(json.dumps(tools_json.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return path
