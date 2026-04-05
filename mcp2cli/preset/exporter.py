"""Export preset bundle to a local directory."""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import click

from mcp2cli.preset.models import Manifest
from mcp2cli.preset.pusher import prepare_preset
from mcp2cli.utils import safe_filename
from mcp2cli.utils.file_ops import ensure_users_dir


def rebuild_index(output_dir: str) -> None:
    """Scan all preset subdirectories and write index.json.

    Looks for ``<server>/<version>/manifest.json`` under *output_dir*,
    aggregates them into a single ``index.json`` at the root.
    """
    root = Path(output_dir)
    entries: dict[str, dict] = {}  # server -> entry dict

    for manifest_path in sorted(root.glob("*/*/manifest.json")):
        try:
            manifest = Manifest.from_dict(
                json.loads(manifest_path.read_text(encoding="utf-8"))
            )
        except Exception:
            continue

        version = manifest_path.parent.name
        server = manifest.server

        if server not in entries:
            entries[server] = {
                "server": server,
                "latest": version,
                "versions": [],
                "description": "",
                "updated_at": manifest.generated_at,
                "tool_count": manifest.tool_count,
            }

        entry = entries[server]
        if version not in entry["versions"]:
            entry["versions"].append(version)

        # Use the most recently generated manifest as latest
        if manifest.generated_at > entry.get("updated_at", ""):
            entry["latest"] = version
            entry["updated_at"] = manifest.generated_at
            entry["tool_count"] = manifest.tool_count

    index = {
        "version": 2,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "presets": list(entries.values()),
    }

    index_path = root / "index.json"
    index_path.write_text(
        json.dumps(index, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    click.echo(f"  ✓ index.json ({len(entries)} preset(s))")


def export_preset(
    server_name: str,
    version: str | None = None,
    output_dir: str = ".",
    yes: bool = False,
) -> bool:
    """Validate and write a preset bundle to a local directory.

    Output structure: <output_dir>/<server_name>/<version>/
    containing tools.json, cli.yaml, skills/, and manifest.json.

    Returns True on success.
    """
    result = prepare_preset(server_name, version)
    if result is None:
        return False
    preset_version, file_pairs, manifest, _tools_json = result

    target_dir = Path(output_dir) / safe_filename(server_name) / preset_version

    # Confirm
    click.echo(f"\nExport to: {target_dir}/")
    click.echo(f"Files ({len(file_pairs)} + manifest.json):")
    for rel, _ in file_pairs:
        click.echo(f"  {rel}")
    click.echo("  manifest.json")

    if target_dir.exists():
        if not yes:
            if not click.confirm(f"\n{target_dir} already exists. Overwrite?", default=True):
                click.echo("Aborted.")
                return False
        shutil.rmtree(target_dir)

    if not yes:
        if not click.confirm("\nProceed?", default=True):
            click.echo("Aborted.")
            return False

    # Write files
    target_dir.mkdir(parents=True, exist_ok=True)

    for rel_path, local_path in file_pairs:
        dest = target_dir / rel_path
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(local_path, dest)
        click.echo(f"  ✓ {rel_path}")

    # Write manifest
    manifest_path = target_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest.to_dict(), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    click.echo("  ✓ manifest.json")

    # Create users/ directory with placeholder SKILL.md
    skills_dir = target_dir / "skills"
    if skills_dir.exists():
        ensure_users_dir(skills_dir)

    # Rebuild index.json for the output directory
    rebuild_index(output_dir)

    click.echo(f"\n✅ Exported to {target_dir}/")
    return True
