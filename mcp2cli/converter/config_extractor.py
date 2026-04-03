"""Extract MCP server config from client configuration files."""

from __future__ import annotations

import click

from mcp2cli.config.models import ConfigSource, ServerConfig
from mcp2cli.config.reader import iter_client_servers


class ServerNotFoundError(Exception):
    pass


def extract_server_config(
    server_name: str,
    source: str = "auto",
) -> tuple[ServerConfig, list[ConfigSource]]:
    """Extract server config from client configs.

    Args:
        server_name: MCP server name
        source: Config source filter ("auto", "claude", "cursor", "codex")

    Returns:
        (ServerConfig, list of ConfigSource where it was found)

    Raises:
        ServerNotFoundError: Server not found in any config
    """
    config: ServerConfig | None = None
    sources: list[ConfigSource] = []

    client_filter = None if source == "auto" else source

    for name, cfg, src in iter_client_servers(client_filter):
        if name == server_name:
            if config is None:
                config = cfg
            sources.append(src)

    if config is None:
        available = set()
        for name, _, _ in iter_client_servers():
            available.add(name)
        raise ServerNotFoundError(
            f'Server "{server_name}" not found in any config source.\n'
            f"Available: {', '.join(sorted(available)) if available else '(none)'}\n"
            f"Use `mcp2cli list` to see all configured servers.\n"
            f"Use `mcp2cli install {server_name}` to install a new server."
        )

    return config, sources
