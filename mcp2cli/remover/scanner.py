"""Pre-removal scanning — collect all server artifacts into a RemovalPlan."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from mcp2cli.cli.mapping import cli_path
from mcp2cli.config.models import ConfigSource
from mcp2cli.config.reader import iter_client_servers
from mcp2cli.config.tool_store import tools_path
from mcp2cli.constants import CLIENT_CONFIGS
from mcp2cli.utils import safe_filename, shared_skills_path, skills_path
from mcp2cli.installer.servers_writer import server_exists
from mcp2cli.remover.package_purger import PackageInfo, detect_package_info


@dataclass
class RemovalPlan:
    """All artifacts that will be removed for a given server."""

    server_name: str

    # Generated files
    tools_json: Path | None = None
    cli_yaml: Path | None = None
    skills_dir: Path | None = None

    # User custom content
    users_has_content: bool = False
    keep_users: bool = False

    # Skill copy directories
    skill_copies: list[Path] = field(default_factory=list)
    agents_skill_dir: Path | None = None

    # Config
    servers_yaml_entry: bool = False
    disabled_sources: list[ConfigSource] = field(default_factory=list)

    # Package info
    package_info: PackageInfo | None = None

    def is_empty(self) -> bool:
        """No artifacts found anywhere."""
        return (
            self.tools_json is None
            and self.cli_yaml is None
            and self.skills_dir is None
            and not self.skill_copies
            and self.agents_skill_dir is None
            and not self.servers_yaml_entry
            and not self.disabled_sources
        )

    def summary_lines(self) -> list[str]:
        """Generate human-readable summary lines."""
        lines: list[str] = []

        if self.skill_copies or self.agents_skill_dir:
            lines.append("Skill copies:")
            for p in self.skill_copies:
                lines.append(f"  {p}")
            if self.agents_skill_dir:
                lines.append(f"  {self.agents_skill_dir}")

        gen_files: list[str] = []
        if self.skills_dir:
            gen_files.append(f"  {self.skills_dir}")
        if self.cli_yaml:
            gen_files.append(f"  {self.cli_yaml}")
        if self.tools_json:
            gen_files.append(f"  {self.tools_json}")
        if gen_files:
            lines.append("Generated files:")
            lines.extend(gen_files)

        if self.servers_yaml_entry:
            lines.append(f"Config: servers.yaml entry for {self.server_name}")

        if self.disabled_sources:
            lines.append("Re-enable (undo convert):")
            for src in self.disabled_sources:
                lines.append(f"  {src.config_path}: re-enable {self.server_name}")

        if self.users_has_content:
            lines.append(f"Warning: users/ directory has custom content in {self.skills_dir}")

        return lines


def scan_removal_targets(server_name: str) -> RemovalPlan:
    """Scan all possible artifacts for a server and build a RemovalPlan."""
    plan = RemovalPlan(server_name=server_name)

    # Generated files
    tp = tools_path(server_name)
    if tp.exists():
        plan.tools_json = tp

    cp = cli_path(server_name)
    if cp.exists():
        plan.cli_yaml = cp

    sd = skills_path(server_name)
    if sd.exists() and sd.is_dir():
        plan.skills_dir = sd
        users_dir = sd / "users"
        if users_dir.exists():
            user_files = [f for f in users_dir.iterdir() if f.name != ".gitkeep"]
            plan.users_has_content = bool(user_files)

    # Skill copy directories
    for client_name, info in CLIENT_CONFIGS.items():
        skill_copy = info["skill_dir"] / safe_filename(server_name)
        if skill_copy.exists():
            plan.skill_copies.append(skill_copy)

    shared = shared_skills_path(server_name)
    if shared.exists():
        plan.agents_skill_dir = shared

    # servers.yaml — try exact name, then fuzzy-match via safe_filename
    plan.servers_yaml_entry = server_exists(server_name)
    if not plan.servers_yaml_entry:
        from mcp2cli.installer.servers_writer import load_servers_yaml
        all_servers = load_servers_yaml().get("servers", {})
        for key in all_servers:
            if safe_filename(key) == safe_filename(server_name):
                plan.servers_yaml_entry = True
                plan.server_name = key
                break

    # Disabled sources in client configs
    for name, _, src in iter_client_servers():
        if name != server_name:
            continue
        try:
            import json as _json
            data = _json.loads(src.config_path.read_text(encoding="utf-8"))
            server_key = CLIENT_CONFIGS.get(src.client, {}).get("server_key", "mcpServers")
            servers = data.get(server_key, {})
            if server_name in servers and servers[server_name].get("disabled"):
                plan.disabled_sources.append(src)
        except Exception:
            pass

    # Package info
    if plan.servers_yaml_entry:
        from mcp2cli.installer.servers_writer import load_servers_yaml
        yaml_data = load_servers_yaml()
        entry = yaml_data.get("servers", {}).get(plan.server_name, {})
        plan.package_info = detect_package_info(plan.server_name, entry)

    return plan
