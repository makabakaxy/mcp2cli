"""MCP Proxy Daemon — asyncio-based Unix socket server."""

from __future__ import annotations

import asyncio
import json
import logging
import signal
import struct
import time
import uuid

from mcp2cli.constants import DAEMON_LOG, DAEMON_PID, DAEMON_SOCK
from mcp2cli.daemon.pool import ConnectionPool

logger = logging.getLogger("mcp2cli.daemon")

DAEMON_IDLE_SECONDS = 300  # 5 min — exit if all servers disconnected and no requests
MAX_LIFETIME_SECONDS = 86400  # 24h — unconditional exit


async def handle_request(pool: ConnectionPool, request: dict) -> dict:
    """Process a single IPC request and return a response dict."""
    req_id = request.get("id", str(uuid.uuid4()))
    method = request.get("method", "")

    if method == "ping":
        return {"id": req_id, "ok": True, "result": "pong"}

    if method == "call_tool":
        server = request.get("server", "")
        tool = request.get("tool", "")
        params = request.get("params", {})

        if not server:
            return _error(req_id, "SERVER_NOT_FOUND", "Missing 'server' field")
        if not tool:
            return _error(req_id, "TOOL_NOT_FOUND", "Missing 'tool' field")

        try:
            session = await pool.get_session(server)
        except ValueError as e:
            return _error(req_id, "SERVER_NOT_FOUND", str(e))
        except Exception as e:
            return _error(req_id, "SERVER_START_FAILED", str(e))

        try:
            result = await session.call_tool(tool, params)
            content_parts = []
            for item in result.content:
                if hasattr(item, "text"):
                    content_parts.append(item.text)
                else:
                    content_parts.append(str(item))
            return {"id": req_id, "ok": True, "result": "\n".join(content_parts)}
        except Exception as e:
            return _error(req_id, "TOOL_CALL_FAILED", str(e))

    if method == "disconnect":
        server = request.get("server", "")
        ok = await pool.disconnect(server)
        return {"id": req_id, "ok": True, "result": f"disconnected={ok}"}

    if method == "status":
        servers = pool.server_names()
        return {"id": req_id, "ok": True, "result": {"servers": servers}}

    return _error(req_id, "INTERNAL_ERROR", f"Unknown method: {method}")


def _error(req_id: str, code: str, message: str) -> dict:
    return {"id": req_id, "ok": False, "error": {"code": code, "message": message}}


async def _read_frame(reader: asyncio.StreamReader) -> bytes | None:
    """Read a length-prefixed frame. Returns None on EOF."""
    header = await reader.readexactly(4)
    length = struct.unpack(">I", header)[0]
    if length > 10 * 1024 * 1024:  # 10MB sanity limit
        return None
    return await reader.readexactly(length)


def _write_frame(data: bytes) -> bytes:
    """Create a length-prefixed frame."""
    return struct.pack(">I", len(data)) + data


async def _client_handler(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter,
    pool: ConnectionPool,
    activity_event: asyncio.Event,
) -> None:
    """Handle a single client connection."""
    try:
        raw = await _read_frame(reader)
        if raw is None:
            return
        request = json.loads(raw.decode("utf-8"))
        activity_event.set()
        response = await handle_request(pool, request)
        frame = _write_frame(json.dumps(response, ensure_ascii=False).encode("utf-8"))
        writer.write(frame)
        await writer.drain()
    except (asyncio.IncompleteReadError, ConnectionResetError):
        pass
    except Exception as e:
        logger.exception("Client handler error: %s", e)
    finally:
        writer.close()
        try:
            await writer.wait_closed()
        except Exception:
            pass


async def run_daemon() -> None:
    """Main daemon entry point — runs until idle or max lifetime."""
    logging.basicConfig(
        filename=str(DAEMON_LOG),
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    pool = ConnectionPool()
    await pool.start_watchdog()

    activity_event = asyncio.Event()
    start_time = time.monotonic()

    DAEMON_SOCK.parent.mkdir(parents=True, exist_ok=True)
    DAEMON_SOCK.unlink(missing_ok=True)

    server = await asyncio.start_unix_server(
        lambda r, w: _client_handler(r, w, pool, activity_event),
        path=str(DAEMON_SOCK),
    )

    import os as _os
    DAEMON_PID.write_text(str(_os.getpid()))
    logger.info("Daemon started, PID=%s, socket=%s", DAEMON_PID.read_text().strip(), DAEMON_SOCK)

    try:
        while True:
            activity_event.clear()
            try:
                await asyncio.wait_for(activity_event.wait(), timeout=DAEMON_IDLE_SECONDS)
            except asyncio.TimeoutError:
                if pool.is_empty():
                    logger.info("Daemon idle with no connections, shutting down.")
                    break

            elapsed = time.monotonic() - start_time
            if elapsed > MAX_LIFETIME_SECONDS:
                logger.info("Max lifetime reached (%.0fs), shutting down.", elapsed)
                break
    finally:
        server.close()
        await server.wait_closed()
        await pool.stop()
        DAEMON_SOCK.unlink(missing_ok=True)
        DAEMON_PID.unlink(missing_ok=True)
        logger.info("Daemon stopped.")


if __name__ == "__main__":
    asyncio.run(run_daemon())
