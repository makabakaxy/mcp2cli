"""Convert pipeline assembly."""

from __future__ import annotations

from mcp2cli.config.models import ConfigSource, ServerConfig
from mcp2cli.installer.pipeline import Step


def build_convert_pipeline(
    server_name: str,
    config: ServerConfig,
    found_sources: list[ConfigSource],
    skip_disable: bool = False,
    force: bool = False,
    no_preset: bool = False,
    preset_version: str | None = None,
) -> list[Step]:
    """Build the convert-specific pipeline."""
    from mcp2cli.generator.cli_gen import generate_cli
    from mcp2cli.generator.skill_gen import generate_skill
    from mcp2cli.installer.servers_writer import write_server
    from mcp2cli.installer.skill_sync import skill_sync
    from mcp2cli.preset.checker import check_and_pull_preset
    from mcp2cli.scanner import scan_server

    return [
        Step(
            name="write-config",
            run=lambda: write_server(config, force=force),
            retry_cmd=f"mcp2cli convert {server_name}",
        ),
        Step(
            name="preset-check",
            run=lambda: check_and_pull_preset(
                server_name, version=preset_version, no_preset=no_preset,
            ),
            retry_cmd=f"mcp2cli preset pull {server_name}",
            depends_on=["write-config"],
            fatal=False,
        ),
        Step(
            name="scan",
            run=lambda: scan_server(server_name) is not None,
            retry_cmd=f"mcp2cli scan {server_name}",
            depends_on=["write-config"],
            skip_if=["preset-check"],
        ),
        Step(
            name="generate-cli",
            run=lambda: generate_cli(server_name),
            retry_cmd=f"mcp2cli generate cli {server_name}",
            depends_on=["scan"],
            skip_if=["preset-check"],
        ),
        Step(
            name="generate-skill",
            run=lambda: generate_skill(server_name),
            retry_cmd=f"mcp2cli generate skill {server_name}",
            depends_on=["generate-cli"],
            skip_if=["preset-check"],
        ),
        Step(
            name="skill-sync",
            run=lambda: skill_sync(server_name, skip_disable=skip_disable),
            retry_cmd=f"mcp2cli skill sync {server_name}",
            depends_on=["generate-skill"],
        ),
    ]
