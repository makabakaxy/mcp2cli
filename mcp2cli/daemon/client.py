"""IPC client for communicating with the MCP Proxy Daemon."""

from __future__ import annotations

import json
import socket
import struct
import uuid

from mcp2cli.constants import DAEMON_SOCK

DEFAULT_TIMEOUT = 60
PING_TIMEOUT = 3


def _send_request(request: dict, timeout: float = DEFAULT_TIMEOUT) -> dict:
    """Send a request to the daemon and return the response."""
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        sock.connect(str(DAEMON_SOCK))
        data = json.dumps(request, ensure_ascii=False).encode("utf-8")
        frame = struct.pack(">I", len(data)) + data
        sock.sendall(frame)

        # Read response
        header = _recv_exact(sock, 4)
        length = struct.unpack(">I", header)[0]
        body = _recv_exact(sock, length)
        return json.loads(body.decode("utf-8"))
    finally:
        sock.close()


def _recv_exact(sock: socket.socket, n: int) -> bytes:
    """Receive exactly n bytes from socket."""
    buf = b""
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise ConnectionError("Daemon connection closed unexpectedly")
        buf += chunk
    return buf


def call_tool(
    server: str,
    tool: str,
    params: dict | None = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> dict:
    """Call an MCP tool through the daemon.

    Returns the full response dict: {"id": ..., "ok": bool, "result": ..., "error": ...}
    """
    request = {
        "id": str(uuid.uuid4()),
        "method": "call_tool",
        "server": server,
        "tool": tool,
        "params": params or {},
    }
    return _send_request(request, timeout=timeout)


def ping() -> bool:
    """Check if daemon is alive. Returns True if responding."""
    try:
        resp = _send_request(
            {"id": str(uuid.uuid4()), "method": "ping"},
            timeout=PING_TIMEOUT,
        )
        return resp.get("ok", False)
    except (OSError, ConnectionError, TimeoutError):
        return False


def daemon_status() -> dict | None:
    """Query daemon status. Returns response dict or None if not running."""
    try:
        return _send_request(
            {"id": str(uuid.uuid4()), "method": "status"},
            timeout=PING_TIMEOUT,
        )
    except (OSError, ConnectionError, TimeoutError):
        return None


def daemon_disconnect(server_name: str) -> bool:
    """Ask the daemon to disconnect a server. Returns True on success."""
    try:
        resp = _send_request(
            {"id": str(uuid.uuid4()), "method": "disconnect", "server": server_name},
            timeout=PING_TIMEOUT,
        )
        return resp.get("ok", False)
    except (OSError, ConnectionError, TimeoutError):
        return False
