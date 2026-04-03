"""Download preset files from remote repository."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from urllib.request import urlopen
from urllib.error import URLError

import click

from mcp2cli.constants import CLI_DIR, DATA_DIR, SKILLS_DIR, TOOLS_DIR
from mcp2cli.preset.models import Manifest
from mcp2cli.preset.registry import _repo_url, find_preset

FILE_TIMEOUT = 10


def pull_preset(
    server_name: str,
    version: str | None = None,
    force: bool = False,
) -> bool:
    """Download all preset files for a server.

    Args:
        server_name: MCP server name.
        version: Specific version to pull, or None for latest.
        force: Overwrite existing files without prompting.

    Returns True on success.
    """
    repo_url = _repo_url()

    # Resolve version from index if not specified
    entry = find_preset(server_name)
    if version is None and entry is not None:
        version = entry.resolve_version(None)
    elif version is not None and entry is not None:
        # Validate that the requested version exists
        version = entry.resolve_version(version)

    # Try versioned URL first, fall back to flat (old repo structure)
    manifest_data = None
    if version:
        versioned_url = f"{repo_url}/presets/{server_name}/{version}/manifest.json"
        manifest_data = _download_json(versioned_url)

    if manifest_data is None:
        # Fallback to flat structure (backward compat with old repos)
        flat_url = f"{repo_url}/presets/{server_name}/manifest.json"
        manifest_data = _download_json(flat_url)
        if manifest_data is None:
            click.echo(f"Error: could not download manifest for {server_name}.", err=True)
            return False
        # Using flat URL — set base_url accordingly
        base_url = f"{repo_url}/presets/{server_name}"
    else:
        base_url = f"{repo_url}/presets/{server_name}/{version}"

    manifest = Manifest.from_dict(manifest_data)
    ver_display = manifest.server_version or version or "unknown"
    click.echo(
        f"Downloading preset for {server_name}..."
    )
    click.echo(
        f"  Preset: v{ver_display}, "
        f"{manifest.tool_count} tools, "
        f"generated {manifest.generated_at[:10]}"
    )

    # Check existing files
    if not force:
        existing = _check_existing(server_name, manifest.files)
        if existing:
            click.echo(f"\n  Local files already exist for {server_name}:")
            for f in existing[:5]:
                click.echo(f"    {f}")
            if not click.confirm("  Overwrite with preset?", default=True):
                return False

    # Download each file
    downloaded: list[Path] = []

    for rel_path in manifest.files:
        url = f"{base_url}/{rel_path}"
        target = _map_target_path(server_name, rel_path)
        target.parent.mkdir(parents=True, exist_ok=True)

        ok = download_file(url, target)
        if not ok:
            click.echo(f"  Error: failed to download {rel_path}", err=True)
            # Clean up partial download
            for p in downloaded:
                p.unlink(missing_ok=True)
            return False

        downloaded.append(target)
        click.echo(f"  ✓ {rel_path}")

    # Create users/ directory
    users_dir = SKILLS_DIR / server_name / "users"
    if not users_dir.exists():
        users_dir.mkdir(parents=True, exist_ok=True)
        (users_dir / ".gitkeep").touch()
        users_skill = users_dir / "SKILL.md"
        if not users_skill.exists():
            users_skill.write_text(
                "# User Notes\n\nAdd your custom workflows and tips here.\n"
                "This file is never overwritten by mcp2cli generate/update.\n",
                encoding="utf-8",
            )

    click.echo(f"Done! Files written to {DATA_DIR}/")
    return True


def download_file(url: str, target_path: Path) -> bool:
    """Download a single file to target path (atomic write)."""
    try:
        with urlopen(url, timeout=FILE_TIMEOUT) as resp:
            if resp.status != 200:
                return False
            content = resp.read()
    except (URLError, OSError):
        return False

    # Atomic write
    target_path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=target_path.parent, suffix=".tmp")
    try:
        with open(fd, "wb") as f:
            f.write(content)
        Path(tmp).replace(target_path)
        return True
    except Exception:
        Path(tmp).unlink(missing_ok=True)
        return False


def _download_json(url: str) -> dict | None:
    try:
        with urlopen(url, timeout=FILE_TIMEOUT) as resp:
            if resp.status != 200:
                return None
            return json.loads(resp.read().decode("utf-8"))
    except (URLError, OSError, json.JSONDecodeError):
        return None


def _map_target_path(server_name: str, rel_path: str) -> Path:
    """Map a manifest relative path to the local target path."""
    if rel_path == "tools.json":
        return TOOLS_DIR / f"{server_name}.json"
    if rel_path == "cli.yaml":
        return CLI_DIR / f"{server_name}.yaml"
    if rel_path.startswith("skills/"):
        return SKILLS_DIR / server_name / rel_path[len("skills/"):]
    return DATA_DIR / server_name / rel_path


def _check_existing(server_name: str, files: list[str]) -> list[Path]:
    """Check which preset files already exist locally."""
    existing: list[Path] = []
    for rel_path in files:
        target = _map_target_path(server_name, rel_path)
        if target.exists():
            existing.append(target)
    return existing
