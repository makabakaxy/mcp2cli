"""Bundled presets — pre-generated skill files shipped with the package.

These presets are available immediately after installation without needing
to fetch from the remote preset repository or run AI generation.

Usage:
    from mcp2cli.bundled_presets import list_bundled, get_bundled_path

    for name in list_bundled():
        print(name)
"""

from __future__ import annotations

import json
from pathlib import Path

BUNDLED_DIR = Path(__file__).parent


def list_bundled() -> list[str]:
    """Return names of all bundled presets."""
    return sorted(
        d.name
        for d in BUNDLED_DIR.iterdir()
        if d.is_dir() and (d / "manifest.json").exists()
    )


def get_bundled_path(server_name: str) -> Path | None:
    """Return the path to a bundled preset directory, or None if not found."""
    preset_dir = BUNDLED_DIR / server_name
    if preset_dir.is_dir() and (preset_dir / "manifest.json").exists():
        return preset_dir
    return None


def load_manifest(server_name: str) -> dict | None:
    """Load the manifest.json for a bundled preset."""
    preset_dir = get_bundled_path(server_name)
    if preset_dir is None:
        return None
    with open(preset_dir / "manifest.json") as f:
        return json.load(f)
