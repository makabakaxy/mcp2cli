"""Presets — pre-generated skill files shipped with the package.

These presets are available immediately after installation without needing
to fetch from the remote preset repository or run AI generation.

Usage:
    from mcp2cli.presets import list_presets, load_manifest

    for name in list_presets():
        print(name)

    manifest = load_manifest("mcp-atlassian")
"""

from __future__ import annotations

import json
from pathlib import Path

PRESETS_DIR = Path(__file__).parent


def list_presets() -> list[str]:
    """Return names of all bundled presets."""
    return sorted(
        d.name
        for d in PRESETS_DIR.iterdir()
        if d.is_dir() and (d / "manifest.json").exists()
    )


def get_preset_path(server_name: str) -> Path | None:
    """Return the path to a bundled preset directory, or None if not found."""
    preset_dir = PRESETS_DIR / server_name
    if preset_dir.is_dir() and (preset_dir / "manifest.json").exists():
        return preset_dir
    return None


def load_manifest(server_name: str) -> dict | None:
    """Load the manifest.json for a bundled preset."""
    preset_dir = get_preset_path(server_name)
    if preset_dir is None:
        return None
    with open(preset_dir / "manifest.json") as f:
        return json.load(f)
