"""Read MCP server configurations from Claude/Cursor/Codex config files."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterator

import click

from mcp2cli.config.models import ConfigSource, ServerConfig
from mcp2cli.constants import CLIENT_CONFIGS, SERVERS_YAML


def _read_json_config(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _read_servers_yaml() -> dict:
    if not SERVERS_YAML.exists():
        return {}
    try:
        import yaml
        return yaml.safe_load(SERVERS_YAML.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}


def iter_client_servers(
    client: str | None = None,
) -> Iterator[tuple[str, ServerConfig, ConfigSource]]:
    """Yield (server_name, ServerConfig, ConfigSource) for each server in client configs."""
    clients = [client] if client else list(CLIENT_CONFIGS.keys())

    for c in clients:
        info = CLIENT_CONFIGS.get(c)
        if not info:
            continue

        config_path = info["config_path"]
        fmt = info["format"]
        server_key = info["server_key"]

        if fmt.endswith("_json"):
            data = _read_json_config(config_path)
            if not data:
                continue
            servers = data.get(server_key, {})
            for name, cfg in servers.items():
                if not isinstance(cfg, dict):
                    continue
                yield name, ServerConfig(
                    name=name,
                    command=cfg.get("command", ""),
                    args=cfg.get("args", []),
                    env=cfg.get("env", {}),
                ), ConfigSource(
                    client=c,
                    config_path=config_path,
                    config_format=fmt,
                )
        elif fmt == "codex_toml":
            if not config_path.exists():
                continue
            try:
                import tomllib
                data = tomllib.loads(config_path.read_text(encoding="utf-8"))
            except Exception:
                continue
            servers = data.get("mcp_servers", {})
            for name, cfg in servers.items():
                if not isinstance(cfg, dict):
                    continue
                yield name, ServerConfig(
                    name=name,
                    command=cfg.get("command", ""),
                    args=cfg.get("args", []),
                    env=cfg.get("env", {}),
                ), ConfigSource(
                    client=c,
                    config_path=config_path,
                    config_format=fmt,
                )


def iter_servers_yaml() -> Iterator[tuple[str, ServerConfig]]:
    """Yield (server_name, ServerConfig) from servers.yaml."""
    data = _read_servers_yaml()
    for name, cfg in data.get("servers", {}).items():
        if not isinstance(cfg, dict):
            continue
        yield name, ServerConfig(
            name=name,
            command=cfg.get("command", ""),
            args=cfg.get("args", []),
            env=cfg.get("env", {}),
        )


def find_server_config(server_name: str) -> ServerConfig | None:
    """Find server config from servers.yaml first, then client configs."""
    for name, cfg in iter_servers_yaml():
        if name == server_name:
            return cfg

    for name, cfg, _ in iter_client_servers():
        if name == server_name:
            return cfg

    return None


def list_all_servers() -> list[dict]:
    """List all known servers across all sources."""
    seen: dict[str, dict] = {}

    for name, cfg in iter_servers_yaml():
        if name not in seen:
            seen[name] = {"name": name, "source": "servers.yaml", "config": cfg}

    for name, cfg, source in iter_client_servers():
        if name not in seen:
            seen[name] = {"name": name, "source": f"{source.client}", "config": cfg}
        else:
            seen[name]["source"] += f", {source.client}"

    return list(seen.values())
