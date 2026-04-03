"""MCP server connection pool with idle reclamation."""

from __future__ import annotations

import asyncio
import logging
import os
import time
from dataclasses import dataclass, field

from mcp2cli.config.models import ServerConfig
from mcp2cli.config.reader import find_server_config

logger = logging.getLogger("mcp2cli.daemon")

SERVER_IDLE_SECONDS = 600  # 10 min
WATCHDOG_INTERVAL = 30


@dataclass
class ServerConnection:
    """A live connection to an MCP server subprocess."""

    server_name: str
    session: object  # mcp.ClientSession
    read_stream: object
    write_stream: object
    cm_stdio: object  # context manager for stdio_client
    cm_session: object  # context manager for ClientSession
    last_used: float = field(default_factory=time.monotonic)

    def touch(self) -> None:
        self.last_used = time.monotonic()

    def idle_seconds(self) -> float:
        return time.monotonic() - self.last_used


class ConnectionPool:
    """Manages MCP server connections with per-server idle reclamation."""

    def __init__(self) -> None:
        self._connections: dict[str, ServerConnection] = {}
        self._locks: dict[str, asyncio.Lock] = {}
        self._watchdog_task: asyncio.Task | None = None

    async def start_watchdog(self) -> None:
        self._watchdog_task = asyncio.create_task(self._watchdog_loop())

    async def stop(self) -> None:
        if self._watchdog_task:
            self._watchdog_task.cancel()
            try:
                await self._watchdog_task
            except asyncio.CancelledError:
                pass

        for name in list(self._connections.keys()):
            await self._close_server(name)

    async def get_session(self, server_name: str):
        """Get or create a session for the given server. Returns mcp.ClientSession."""
        if server_name not in self._locks:
            self._locks[server_name] = asyncio.Lock()

        async with self._locks[server_name]:
            conn = self._connections.get(server_name)
            if conn is not None:
                conn.touch()
                return conn.session

            return await self._connect(server_name)

    async def disconnect(self, server_name: str) -> bool:
        """Close a specific server connection. Returns True if it was connected."""
        if server_name in self._connections:
            await self._close_server(server_name)
            return True
        return False

    def is_empty(self) -> bool:
        return len(self._connections) == 0

    def server_names(self) -> list[str]:
        return list(self._connections.keys())

    async def _connect(self, server_name: str):
        """Establish a new connection to an MCP server."""
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client

        config = find_server_config(server_name)
        if config is None:
            raise ValueError(f"Server '{server_name}' is not configured")

        env = {**os.environ, **config.env} if config.env else None
        params = StdioServerParameters(
            command=config.command,
            args=config.args,
            env=env,
        )

        cm_stdio = stdio_client(params)
        read_stream, write_stream = await cm_stdio.__aenter__()

        cm_session = ClientSession(read_stream, write_stream)
        session = await cm_session.__aenter__()
        await session.initialize()

        conn = ServerConnection(
            server_name=server_name,
            session=session,
            read_stream=read_stream,
            write_stream=write_stream,
            cm_stdio=cm_stdio,
            cm_session=cm_session,
        )
        self._connections[server_name] = conn
        logger.info("Connected to %s", server_name)
        return session

    async def _close_server(self, server_name: str) -> None:
        conn = self._connections.pop(server_name, None)
        if conn is None:
            return
        try:
            await conn.cm_session.__aexit__(None, None, None)
        except Exception:
            pass
        try:
            await conn.cm_stdio.__aexit__(None, None, None)
        except Exception:
            pass
        logger.info("Disconnected from %s", server_name)

    async def _watchdog_loop(self) -> None:
        """Periodically check for idle server connections."""
        while True:
            await asyncio.sleep(WATCHDOG_INTERVAL)
            for name in list(self._connections.keys()):
                conn = self._connections.get(name)
                if conn and conn.idle_seconds() > SERVER_IDLE_SECONDS:
                    logger.info("Idle reclaim: %s (%.0fs idle)", name, conn.idle_seconds())
                    await self._close_server(name)
