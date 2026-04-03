"""Re-enable MCP servers in client configs (undo convert's disable)."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import click

from mcp2cli.config.models import ConfigSource


def re_enable_server(
    server_name: str,
    config_path: Path,
    config_format: str,
) -> bool:
    """Remove the 'disabled' field from a server entry in a client config.

    Returns True if successful or already enabled.
    """
    if not config_path.exists():
        return True

    try:
        if config_format in ("claude_json", "cursor_json"):
            return _re_enable_json(server_name, config_path)
        elif config_format == "codex_toml":
            return _re_enable_toml(server_name, config_path)
        return True
    except Exception as e:
        click.echo(
            f"  Warning: failed to re-enable {server_name} in {config_path}: {e}",
            err=True,
        )
        return False


def _re_enable_json(server_name: str, config_path: Path) -> bool:
    text = config_path.read_text(encoding="utf-8")
    data = json.loads(text)

    servers = data.get("mcpServers", {})
    if server_name not in servers:
        return True

    entry = servers[server_name]
    if "disabled" not in entry:
        return True

    del entry["disabled"]
    _atomic_write_json(config_path, data)
    return True


def _re_enable_toml(server_name: str, config_path: Path) -> bool:
    try:
        import tomlkit
    except ImportError:
        click.echo("  Warning: tomlkit not installed, cannot modify TOML config", err=True)
        return False

    text = config_path.read_text(encoding="utf-8")
    data = tomlkit.loads(text)

    servers = data.get("mcp_servers", {})
    if server_name not in servers:
        return True

    entry = servers[server_name]
    if "disabled" not in entry:
        return True

    del entry["disabled"]
    _atomic_write_text(config_path, tomlkit.dumps(data))
    return True


def re_enable_in_clients(
    server_name: str,
    sources: list[ConfigSource],
) -> bool:
    """Re-enable server in all disabled config sources."""
    all_ok = True
    for src in sources:
        ok = re_enable_server(server_name, src.config_path, src.config_format)
        if ok:
            click.echo(f"  ✓ {src.config_path}: {server_name} re-enabled")
        else:
            all_ok = False
    return all_ok


def _atomic_write_json(path: Path, data: dict) -> None:
    content = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    _atomic_write_text(path, content)


def _atomic_write_text(path: Path, content: str) -> None:
    fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with open(fd, "w", encoding="utf-8") as f:
            f.write(content)
        Path(tmp).replace(path)
    except Exception:
        Path(tmp).unlink(missing_ok=True)
        raise
