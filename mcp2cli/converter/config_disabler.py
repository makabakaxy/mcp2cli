"""Disable MCP servers in client configuration files."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import click

from mcp2cli.config.models import ConfigSource


def disable_server(
    server_name: str,
    config_path: Path,
    config_format: str,
) -> bool:
    """Set disabled=true for a server in a client config file.

    Returns True if successful, False on failure.
    """
    if not config_path.exists():
        return False

    try:
        if config_format in ("claude_json", "cursor_json"):
            return _disable_json(server_name, config_path)
        elif config_format == "codex_toml":
            return _disable_toml(server_name, config_path)
        return False
    except Exception as e:
        click.echo(f"  Warning: Failed to disable {server_name} in {config_path}: {e}", err=True)
        return False


def _disable_json(server_name: str, config_path: Path) -> bool:
    text = config_path.read_text(encoding="utf-8")
    data = json.loads(text)

    servers = data.get("mcpServers", {})
    if server_name not in servers:
        return False

    if servers[server_name].get("disabled"):
        click.echo(f"  Already disabled in {config_path}")
        return True

    servers[server_name]["disabled"] = True

    _atomic_write_json(config_path, data)
    return True


def _disable_toml(server_name: str, config_path: Path) -> bool:
    try:
        import tomlkit
    except ImportError:
        click.echo("  Warning: tomlkit not installed, cannot modify TOML config", err=True)
        return False

    text = config_path.read_text(encoding="utf-8")
    data = tomlkit.loads(text)

    servers = data.get("mcp_servers", {})
    if server_name not in servers:
        return False

    if servers[server_name].get("disabled"):
        click.echo(f"  Already disabled in {config_path}")
        return True

    servers[server_name]["disabled"] = True

    _atomic_write_text(config_path, tomlkit.dumps(data))
    return True


def disable_in_all_sources(
    server_name: str,
    sources: list[ConfigSource],
) -> bool:
    """Disable server in all config sources. Returns True if all succeed."""
    all_ok = True
    for src in sources:
        ok = disable_server(server_name, src.config_path, src.config_format)
        if ok:
            click.echo(f"  {src.config_path}: {server_name} disabled ✓")
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
