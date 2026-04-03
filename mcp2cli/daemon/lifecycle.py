"""Daemon lifecycle management — start, stop, health check."""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import time

import click

from mcp2cli.constants import DAEMON_LOG, DAEMON_PID, DAEMON_SOCK
from mcp2cli.daemon.client import ping


def is_daemon_running() -> bool:
    """Check if daemon is running via PID file + process existence."""
    if not DAEMON_PID.exists():
        return False
    try:
        pid = int(DAEMON_PID.read_text().strip())
        os.kill(pid, 0)
        return True
    except (ValueError, ProcessLookupError, PermissionError):
        # Stale PID file
        _cleanup_stale()
        return False


def ensure_daemon() -> bool:
    """Ensure daemon is running, starting it if needed.

    Returns True if daemon is available.
    """
    if is_daemon_running() and ping():
        return True

    _cleanup_stale()
    return _start_daemon()


def _start_daemon() -> bool:
    """Fork a daemon subprocess."""
    DAEMON_SOCK.parent.mkdir(parents=True, exist_ok=True)

    proc = subprocess.Popen(
        [sys.executable, "-m", "mcp2cli.daemon.server"],
        start_new_session=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # Wait for socket to appear
    for _ in range(50):  # 5 seconds max
        time.sleep(0.1)
        if DAEMON_SOCK.exists() and ping():
            return True

    click.echo("Warning: daemon did not start within 5 seconds.", err=True)
    return False


def stop_daemon() -> bool:
    """Stop the running daemon. Returns True if stopped."""
    if not DAEMON_PID.exists():
        return False

    try:
        pid = int(DAEMON_PID.read_text().strip())
        os.kill(pid, signal.SIGTERM)

        # Wait for process to exit
        for _ in range(30):
            time.sleep(0.1)
            try:
                os.kill(pid, 0)
            except ProcessLookupError:
                _cleanup_stale()
                return True

        # Force kill
        os.kill(pid, signal.SIGKILL)
        _cleanup_stale()
        return True
    except (ValueError, ProcessLookupError, PermissionError):
        _cleanup_stale()
        return True


def _cleanup_stale() -> None:
    """Remove stale PID and socket files."""
    DAEMON_PID.unlink(missing_ok=True)
    DAEMON_SOCK.unlink(missing_ok=True)


def get_daemon_info() -> dict | None:
    """Return daemon info dict or None if not running."""
    if not is_daemon_running():
        return None

    try:
        pid = int(DAEMON_PID.read_text().strip())
    except (ValueError, FileNotFoundError):
        return None

    from mcp2cli.daemon.client import daemon_status
    status = daemon_status()
    return {
        "pid": pid,
        "socket": str(DAEMON_SOCK),
        "servers": status.get("result", {}).get("servers", []) if status else [],
    }
