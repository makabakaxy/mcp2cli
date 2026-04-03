"""Connect to MCP server and scan its tool list."""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone

import click

from mcp2cli.config.models import ServerConfig, ToolInfo, ToolsJSON
from mcp2cli.config.reader import find_server_config
from mcp2cli.config.tool_store import save_tools


async def _scan_server(config: ServerConfig) -> ToolsJSON:
    """Connect to MCP server via stdio and list tools."""
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    params = StdioServerParameters(
        command=config.command,
        args=config.args,
        env={**config.env} if config.env else None,
    )

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            server_version = None
            if hasattr(session, '_server_info') and session._server_info:
                server_version = getattr(session._server_info, 'version', None)

            result = await session.list_tools()

            tools = []
            for tool in result.tools:
                tools.append(ToolInfo(
                    name=tool.name,
                    description=tool.description or "",
                    input_schema=tool.inputSchema if hasattr(tool, 'inputSchema') else {},
                ))

            return ToolsJSON(
                server=config.name,
                version=server_version,
                scanned_at=datetime.now(timezone.utc).isoformat(),
                tools=tools,
            )


def scan_server(server_name: str) -> ToolsJSON | None:
    """Scan an MCP server and save tools JSON. Returns ToolsJSON or None on failure."""
    config = find_server_config(server_name)
    if config is None:
        click.echo(f"Error: Server '{server_name}' not found in any config.", err=True)
        click.echo("Use `mcp2cli list` to see available servers.", err=True)
        return None

    click.echo(f"Scanning {server_name}...")
    try:
        tools_json = asyncio.run(_scan_server(config))
    except Exception as e:
        click.echo(f"Error scanning {server_name}: {e}", err=True)
        return None

    path = save_tools(tools_json)
    click.echo(f"  Found {len(tools_json.tools)} tools. Written to {path}")
    return tools_json
