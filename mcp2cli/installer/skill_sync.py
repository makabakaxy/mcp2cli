"""Sync skill files to AI client directories and disable MCP configs."""

from __future__ import annotations

import shutil
from pathlib import Path

import click

from mcp2cli.constants import CLIENT_CONFIGS
from mcp2cli.utils import safe_filename, shared_skills_path, skills_path
from mcp2cli.converter.config_disabler import disable_server


def skill_sync(
    server_name: str,
    targets: list[str] | None = None,
    skip_disable: bool = False,
) -> bool:
    """Copy skill files to client directories and optionally disable MCP.

    Returns True on success.
    """
    source_dir = skills_path(server_name)
    if not source_dir.exists() or not (source_dir / "SKILL.md").exists():
        click.echo(
            f"Error: Skill files not found at {source_dir}\n"
            f"Run `mcp2cli generate skill {server_name}` first.",
            err=True,
        )
        return False

    target_clients = targets or list(CLIENT_CONFIGS.keys())
    click.echo(f"🔗 Syncing skill for {server_name}...")

    # Copy to shared skills directory
    shared = shared_skills_path(server_name)
    _copy_skill(source_dir, shared)
    click.echo(f"  {shared} ✓")

    # Copy to each client skill directory
    for client in target_clients:
        info = CLIENT_CONFIGS.get(client)
        if not info:
            continue

        target = info["skill_dir"] / safe_filename(server_name)
        _copy_skill(source_dir, target)
        click.echo(f"  {target} ✓")

        # Disable MCP in client config
        if not skip_disable:
            config_path = info["config_path"]
            config_format = info["format"]
            if config_path.exists():
                ok = disable_server(server_name, config_path, config_format)
                if ok:
                    click.echo(f"  MCP disabled in {config_path}")

    if skip_disable:
        click.echo("  MCP config not modified (--skip-disable)")

    return True


def _copy_skill(source: Path, target: Path) -> None:
    """Copy skill directory, skipping users/ from source, preserving users/ at target."""
    target.mkdir(parents=True, exist_ok=True)

    # Remove non-users content at target
    for item in target.iterdir():
        if item.name == "users":
            continue
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()

    # Copy from source, skipping users/
    for item in source.iterdir():
        if item.name == "users":
            continue
        dest = target / item.name
        if item.is_dir():
            shutil.copytree(item, dest, dirs_exist_ok=True)
        else:
            shutil.copy2(item, dest)
