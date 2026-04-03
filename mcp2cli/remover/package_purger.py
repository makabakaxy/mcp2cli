"""Infer and execute package uninstall commands."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass

import click


@dataclass
class PackageInfo:
    """Inferred package manager info for a server."""

    command: str
    package_name: str
    uninstall_cmd: str


def detect_package_info(server_name: str, servers_yaml_entry: dict) -> PackageInfo | None:
    """Infer uninstall command from servers.yaml entry.

    Returns PackageInfo or None if cannot determine.
    """
    command = servers_yaml_entry.get("command", "")
    args = servers_yaml_entry.get("args", [])
    if not args:
        return None

    package_name = args[0]

    uninstall_map = {
        "uvx": f"uv pip uninstall {package_name}",
        "npx": f"npm uninstall -g {package_name}",
        "pip": f"pip uninstall -y {package_name}",
        "python": f"pip uninstall -y {package_name}",
        "pipx": f"pipx uninstall {package_name}",
    }

    uninstall_cmd = uninstall_map.get(command)
    if not uninstall_cmd:
        return None

    return PackageInfo(
        command=command,
        package_name=package_name,
        uninstall_cmd=uninstall_cmd,
    )


def purge_package(info: PackageInfo) -> bool:
    """Execute the uninstall command. Returns True on success."""
    click.echo(f"  $ {info.uninstall_cmd}")
    try:
        result = subprocess.run(
            info.uninstall_cmd.split(),
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode == 0:
            click.echo(f"  ✓ {info.package_name} uninstalled")
            return True
        click.echo(f"  Warning: uninstall exited with code {result.returncode}", err=True)
        if result.stderr:
            click.echo(f"  {result.stderr.strip()}", err=True)
        return False
    except subprocess.TimeoutExpired:
        click.echo("  Warning: uninstall timed out", err=True)
        return False
    except FileNotFoundError:
        click.echo(f"  Warning: command not found: {info.uninstall_cmd.split()[0]}", err=True)
        return False
