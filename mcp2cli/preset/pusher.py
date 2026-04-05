"""Preset push/export: validate, assemble, and publish preset bundles."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import click

from mcp2cli.cli.mapping import cli_yaml_hash
from mcp2cli.config.tool_store import load_tools
from mcp2cli.constants import CLI_DIR, TOOLS_DIR
from mcp2cli.generator.validator import validate_cli_yaml, validate_skill
from mcp2cli.preset.models import Manifest
from mcp2cli.utils import safe_filename, skills_path


PrepareResult = tuple[str, list[tuple[str, Path]], Manifest, object]
"""(resolved_version, file_pairs, manifest, tools_json)"""


def prepare_preset(
    server_name: str,
    version: str | None = None,
) -> PrepareResult | None:
    """Load, validate, and collect files for a preset bundle.

    Returns (resolved_version, file_pairs, manifest, tools_json) on success,
    or None on failure.
    """
    # 1. Load tools.json
    tools_json = load_tools(server_name)
    if tools_json is None:
        click.echo(
            f"Error: tools/{server_name}.json not found. "
            f"Run 'mcp2cli scan {server_name}' first.",
            err=True,
        )
        return None

    # 2. Resolve version
    preset_version = version or tools_json.version or tools_json.scanned_at[:10]
    click.echo(f"Preparing preset: {server_name}@{preset_version}")

    # 3. Validate
    click.echo("Validating...")
    cli_errors = validate_cli_yaml(server_name)
    if cli_errors:
        click.echo("  CLI YAML validation failed:", err=True)
        for e in cli_errors:
            click.echo(f"    ✗ {e}", err=True)
        return None
    click.echo("  ✓ cli.yaml")

    skill_errors = validate_skill(server_name)
    hard_errors = [e for e in skill_errors if not e.startswith("Warning:")]
    if hard_errors:
        click.echo("  Skill validation failed:", err=True)
        for e in hard_errors:
            click.echo(f"    ✗ {e}", err=True)
        return None
    click.echo("  ✓ SKILL.md")

    # 4. Collect files
    file_pairs = _collect_files(server_name)  # [(preset_rel_path, local_Path)]

    # 5. Build manifest
    manifest = Manifest(
        server=server_name,
        server_version=preset_version,
        tool_count=len(tools_json.tools),
        cli_hash=cli_yaml_hash(server_name) or "",
        generated_at=datetime.now(timezone.utc).isoformat(),
        generated_by="mcp2cli-push",
        files=[rel for rel, _ in file_pairs],
    )

    return preset_version, file_pairs, manifest, tools_json


def push_preset(
    server_name: str,
    version: str | None = None,
    yes: bool = False,
) -> bool:
    """Validate local files, assemble a preset bundle, and push via git SSH.

    Returns True on success.
    """
    from mcp2cli.preset.github import push_branch
    from mcp2cli.preset.registry import _pr_url, _ssh_url, fetch_index

    result = prepare_preset(server_name, version)
    if result is None:
        return False
    preset_version, file_pairs, manifest, tools_json = result

    # 6. Build updated index.json
    index_data = _build_updated_index(server_name, preset_version, tools_json, fetch_index)

    # 7. Confirm
    version_dir = f"presets/{server_name}/{preset_version}"
    click.echo(f"\nFiles ({len(file_pairs)} + manifest.json + index.json):")
    for rel, _ in file_pairs:
        click.echo(f"  {version_dir}/{rel}")
    click.echo(f"  {version_dir}/manifest.json")
    click.echo(f"  presets/index.json")

    if not yes:
        if not click.confirm("\nProceed?", default=True):
            click.echo("Aborted.")
            return False

    # 8. Assemble git payloads: (repo_relative_path, bytes)
    payloads: list[tuple[str, bytes]] = []
    for rel_path, local_path in file_pairs:
        payloads.append((f"{version_dir}/{rel_path}", local_path.read_bytes()))
    payloads.append((
        f"{version_dir}/manifest.json",
        json.dumps(manifest.to_dict(), indent=2, ensure_ascii=False).encode(),
    ))
    payloads.append((
        "presets/index.json",
        json.dumps(index_data, indent=2, ensure_ascii=False).encode(),
    ))

    # 9. Push
    branch = f"preset/{server_name}-{preset_version}"
    commit_msg = f"preset: {server_name}@{preset_version} ({len(tools_json.tools)} tools)"
    click.echo("\nPushing to git...")
    ok = push_branch(
        ssh_url=_ssh_url(),
        branch=branch,
        files=payloads,
        commit_msg=commit_msg,
    )
    if not ok:
        return False

    # 10. Output PR URL
    url = _pr_url(branch)
    click.echo(f"\n✅ Done! Open this URL to create a PR:")
    click.echo(f"   {url}")
    return True


def _collect_files(server_name: str) -> list[tuple[str, Path]]:
    """Collect local preset files as (preset_relative_path, local_path) pairs.

    Includes:
      - tools/<server>.json   → tools.json
      - cli/<server>.yaml     → cli.yaml
      - skills/<server>/**    → skills/** (users/ directory excluded)
    """
    pairs: list[tuple[str, Path]] = []

    tools_file = TOOLS_DIR / f"{safe_filename(server_name)}.json"
    if tools_file.exists():
        pairs.append(("tools.json", tools_file))

    cli_file = CLI_DIR / f"{safe_filename(server_name)}.yaml"
    if cli_file.exists():
        pairs.append(("cli.yaml", cli_file))

    skill_dir = skills_path(server_name)
    if skill_dir.exists():
        for f in sorted(skill_dir.rglob("*")):
            if not f.is_file():
                continue
            rel = f.relative_to(skill_dir)
            if rel.parts[0] == "users":
                continue
            pairs.append((f"skills/{rel.as_posix()}", f))

    return pairs


def _build_updated_index(
    server_name: str,
    version: str,
    tools_json,
    fetch_index_fn,
) -> dict:
    """Return an updated index.json dict with the new preset entry added/updated."""
    now = datetime.now(timezone.utc).isoformat()
    index = fetch_index_fn()

    existing_versions: list[str] = []
    existing_description = ""
    index_format_version = 2

    if index is not None:
        index_format_version = index.version
        entry = index.find(server_name)
        if entry is not None:
            # Keep previous versions, excluding the one being pushed (avoid dupes)
            existing_versions = [v for v in entry.versions if v != version]
            existing_description = entry.description

        other_presets = [
            {
                "server": p.server,
                "latest": p.latest,
                "versions": p.versions,
                "description": p.description,
                "updated_at": p.updated_at,
                "tool_count": p.tool_count,
            }
            for p in index.presets
            if p.server != server_name
        ]
    else:
        other_presets = []

    updated_entry = {
        "server": server_name,
        "latest": version,
        "versions": [version] + existing_versions,
        "description": existing_description,
        "updated_at": now,
        "tool_count": len(tools_json.tools),
    }

    all_presets = other_presets + [updated_entry]
    all_presets.sort(key=lambda x: x["server"])

    return {
        "version": index_format_version,
        "updated_at": now,
        "presets": all_presets,
    }
