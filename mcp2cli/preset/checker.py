"""Pipeline integration entry point for preset checking."""

from __future__ import annotations

import click

from mcp2cli.preset.downloader import pull_preset
from mcp2cli.preset.models import PresetEntry
from mcp2cli.preset.registry import _is_auto_check_enabled, fetch_index


def probe_preset(
    server_name: str,
    version: str | None = None,
    no_preset: bool = False,
) -> PresetEntry | None:
    """Probe for an available preset without pulling it.

    Returns the PresetEntry if found and valid, None otherwise.
    """
    if no_preset:
        return None

    if not _is_auto_check_enabled():
        return None

    index = fetch_index()
    if index is None:
        return None

    entry = index.find(server_name)
    if entry is None:
        return None

    if version is not None and version not in entry.versions:
        return None

    return entry


def check_and_pull_preset(
    server_name: str,
    version: str | None = None,
    no_preset: bool = False,
    force: bool = False,
) -> bool:
    """Pull a preset (no confirmation — caller is responsible for confirming).

    Used as a pipeline step in install/convert flows.

    Returns:
        True if preset was successfully pulled (downstream steps can be skipped).
        False if no preset used (continue normal flow).
    """
    entry = probe_preset(server_name, version=version, no_preset=no_preset)
    if entry is None:
        return False

    click.echo("Pulling preset...")
    ok = pull_preset(server_name, version=version, force=force)

    if ok:
        click.echo("  Skipping: scan, generate cli, generate skill (using preset)")
    else:
        click.echo("  Preset download failed. Proceeding with AI generation.")

    return ok
