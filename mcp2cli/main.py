"""mcp2cli CLI entry point."""

from __future__ import annotations

from pathlib import Path

import click


class DynamicRootGroup(click.Group):
    """Fall back to dynamic command resolution for unknown top-level tokens."""

    def invoke(self, ctx):
        if not ctx.protected_args:
            return super().invoke(ctx)

        args = [*ctx.protected_args, *ctx.args]
        cmd_name = click.utils.make_str(args[0])
        cmd = self.get_command(ctx, cmd_name)

        if cmd is None and ctx.token_normalize_func is not None:
            cmd_name = ctx.token_normalize_func(cmd_name)
            cmd = self.get_command(ctx, cmd_name)

        if cmd is None and not args[0].startswith("-"):
            ctx._protected_args = []
            ctx.args = args
            ctx.invoked_subcommand = None
            with ctx:
                return click.Command.invoke(self, ctx)

        return super().invoke(ctx)


@click.group(cls=DynamicRootGroup, invoke_without_command=True)
@click.version_option()
@click.pass_context
def cli(ctx):
    """mcp2cli - Convert MCP servers into hierarchical CLI commands and agent Skills."""
    if ctx.invoked_subcommand is None:
        # Unknown top-level commands are handled dynamically by DynamicRootGroup.
        args = list(ctx.args)
        if args and not args[0].startswith("-"):
            _handle_dynamic_command(args)
        else:
            click.echo(ctx.get_help())


def _handle_dynamic_command(args: list[str]) -> None:
    """Handle dynamic hierarchical commands (e.g. mcp2cli mcp-atlassian jira issue create)."""
    from mcp2cli.cli.resolver import resolve_command
    from mcp2cli.daemon.client import call_tool
    from mcp2cli.daemon.lifecycle import ensure_daemon

    result = resolve_command(args)
    if result is None:
        raise SystemExit(1)

    if not ensure_daemon():
        click.echo("Error: could not start daemon.", err=True)
        raise SystemExit(1)

    response = call_tool(result.server, result.tool, result.params)

    if response.get("ok"):
        output = response.get("result", "")
        click.echo(output)
    else:
        error = response.get("error", {})
        click.echo(
            f"Error [{error.get('code', 'UNKNOWN')}]: {error.get('message', 'Unknown error')}",
            err=True,
        )
        raise SystemExit(1)


def _preset_status(local_ver: str | None, remote_entry) -> str:
    """Return a human-readable status string for a preset."""
    if local_ver and remote_entry:
        return "synced"
    if local_ver:
        return "local"
    return "remote"


def _display_preset_info(entry, version: str | None) -> None:
    """Print preset availability info to stdout."""
    display_ver = version or entry.latest
    click.echo("\nPre-generated skill files available:")
    click.echo(
        f"  Version: {display_ver} | "
        f"Tools: {entry.tool_count} | "
        f"Updated: {entry.updated_at[:10]}"
    )
    if entry.versions and len(entry.versions) > 1:
        click.echo(f"  Available versions: {', '.join(entry.versions)}")


# ---------------------------------------------------------------------------
# list
# ---------------------------------------------------------------------------

@cli.command("list")
def list_servers():
    """List all MCP servers from all config sources."""
    from mcp2cli.config.reader import list_all_servers

    servers = list_all_servers()
    if not servers:
        click.echo("No MCP servers found.")
        click.echo("Check ~/.claude.json, ~/.cursor/mcp.json, or ~/.agents/mcp2cli/servers.yaml")
        return

    click.echo(f"{'NAME':<25} {'SOURCE':<30}")
    click.echo("-" * 55)
    for s in servers:
        click.echo(f"{s['name']:<25} {s['source']:<30}")


# ---------------------------------------------------------------------------
# scan
# ---------------------------------------------------------------------------

@cli.command()
@click.argument("server_name")
def scan(server_name: str):
    """Scan an MCP server's tool list."""
    from mcp2cli.scanner import scan_server

    result = scan_server(server_name)
    if result is None:
        raise SystemExit(1)


# ---------------------------------------------------------------------------
# validate
# ---------------------------------------------------------------------------

@cli.command()
@click.argument("server_name")
def validate(server_name: str):
    """Validate CLI mapping and/or skill files for a server."""
    from mcp2cli.cli.mapping import cli_path
    from mcp2cli.generator.validator import validate_cli_yaml, validate_skill
    from mcp2cli.utils import skills_path

    has_errors = False

    cp = cli_path(server_name)
    if cp.exists():
        click.echo(f"Validating {cp}...")
        errors = validate_cli_yaml(server_name)
        if errors:
            for e in errors:
                click.echo(f"  ✗ {e}")
            has_errors = True
        else:
            click.echo("  All CLI checks passed ✓")

    sd = skills_path(server_name)
    if sd.exists():
        click.echo(f"Validating {sd}...")
        errors = validate_skill(server_name)
        if errors:
            for e in errors:
                click.echo(f"  ✗ {e}")
            has_errors = True
        else:
            click.echo("  All skill checks passed ✓")

    if not cp.exists() and not sd.exists():
        click.echo(f"No CLI or skill files found for '{server_name}'.")
        has_errors = True

    if has_errors:
        raise SystemExit(1)


# ---------------------------------------------------------------------------
# generate
# ---------------------------------------------------------------------------

@cli.group()
def generate():
    """Generate CLI command tree or skill files."""
    pass


@generate.command("cli")
@click.argument("server_name")
@click.option("--merge", is_flag=True, help="Incremental merge for new tools only")
def generate_cli_cmd(server_name: str, merge: bool):
    """Generate CLI command tree YAML via AI."""
    from mcp2cli.generator.cli_gen import generate_cli

    ok = generate_cli(server_name, merge=merge)
    if not ok:
        raise SystemExit(1)
    click.echo(f"Next: run 'mcp2cli generate skill {server_name}' to create a SKILL.md")


@generate.command("skill")
@click.argument("server_name")
@click.option("-o", "--output", type=click.Path(), help="Output directory")
@click.option("--full", is_flag=True, help="Force full regeneration")
def generate_skill_cmd(server_name: str, output: str | None, full: bool):
    """Generate Skill files (SKILL.md + reference + examples) via AI."""
    from mcp2cli.generator.skill_gen import generate_skill

    output_dir = Path(output) if output else None
    ok = generate_skill(server_name, output_dir=output_dir, full=full)
    if not ok:
        raise SystemExit(1)


# ---------------------------------------------------------------------------
# mcp (subgroup for server registration)
# ---------------------------------------------------------------------------

@cli.group("mcp")
def mcp_group():
    """Manage MCP server registrations in servers.yaml."""
    pass


@mcp_group.command("add")
@click.argument("server_name")
@click.option("--env", "env_pairs", multiple=True, help="Env values (KEY=VALUE)")
@click.option("--skip-install", is_flag=True, help="Skip package installation")
@click.option("--yes", is_flag=True, help="Skip confirmation")
def mcp_add(server_name: str, env_pairs: tuple, skip_install: bool, yes: bool):
    """Register an MCP server to servers.yaml via AI search."""
    from mcp2cli.config.models import ServerConfig
    from mcp2cli.installer.ai_search import ai_search_server
    from mcp2cli.installer.interactive import collect_env_values
    from mcp2cli.installer.servers_writer import write_server

    preset_envs: dict[str, str] = {}
    for pair in env_pairs:
        if "=" in pair:
            k, v = pair.split("=", 1)
            preset_envs[k] = v

    search_result = ai_search_server(server_name)
    if search_result is None or not search_result.found:
        raise SystemExit(1)

    env_values = collect_env_values(search_result.env, preset_envs)

    config = ServerConfig(
        name=server_name,
        command=search_result.command,
        args=search_result.args,
        env=env_values,
    )

    if not yes:
        click.echo(f"\nWill write to servers.yaml:")
        click.echo(f"  {server_name}:")
        click.echo(f"    command: {config.command} {' '.join(config.args)}")
        if env_values:
            click.echo(f"    env: {', '.join(env_values.keys())} ({len(env_values)} values set)")
        if search_result.source_url:
            click.echo(f"  Source: {search_result.source_url}")
        if not click.confirm("\nProceed?", default=True):
            click.echo("Aborted.")
            return

    write_server(config)


@mcp_group.command("remove")
@click.argument("server_name")
def mcp_remove(server_name: str):
    """Remove an MCP server from servers.yaml."""
    from mcp2cli.installer.servers_writer import remove_server

    if not remove_server(server_name):
        raise SystemExit(1)


# ---------------------------------------------------------------------------
# skill
# ---------------------------------------------------------------------------

@cli.group("skill")
def skill_group():
    """Manage skill files."""
    pass


@skill_group.command("sync")
@click.argument("server_name", required=False)
@click.option("--targets", help="Target clients (comma-separated: claude,cursor,codex)")
@click.option("--skip-disable", is_flag=True, help="Don't disable MCP in client configs")
def skill_sync_cmd(server_name: str | None, targets: str | None, skip_disable: bool):
    """Sync skill files to AI client directories."""
    from mcp2cli.constants import SKILLS_DIR
    from mcp2cli.installer.skill_sync import skill_sync

    target_list = targets.split(",") if targets else None

    if server_name:
        ok = skill_sync(server_name, targets=target_list, skip_disable=skip_disable)
        if not ok:
            raise SystemExit(1)
    else:
        if not SKILLS_DIR.exists():
            click.echo("No skill files found.")
            return
        for d in SKILLS_DIR.iterdir():
            if d.is_dir() and (d / "SKILL.md").exists():
                skill_sync(d.name, targets=target_list, skip_disable=skip_disable)


@skill_group.command("unsync")
@click.argument("server_name", required=False)
@click.option("--targets", help="Target clients (comma-separated: claude,cursor,codex)")
@click.option("--skip-re-enable", is_flag=True, help="Don't re-enable MCP in client configs")
def skill_unsync_cmd(server_name: str | None, targets: str | None, skip_re_enable: bool):
    """Remove skill files from AI client directories and re-enable MCP."""
    from mcp2cli.constants import CLIENT_CONFIGS
    from mcp2cli.remover.cleaner import unsync_skills
    from mcp2cli.remover.config_re_enabler import re_enable_server
    from mcp2cli.utils import safe_filename, shared_skills_path

    target_clients = targets.split(",") if targets else list(CLIENT_CONFIGS.keys())

    def _unsync_one(sname: str) -> None:
        copies: list[Path] = []
        for client in target_clients:
            info = CLIENT_CONFIGS.get(client)
            if not info:
                continue
            skill_dir = info["skill_dir"] / safe_filename(sname)
            if skill_dir.exists():
                copies.append(skill_dir)

        agents = shared_skills_path(sname)
        agents_dir = agents if agents.exists() else None

        unsync_skills(sname, copies, agents_dir)

        if not skip_re_enable:
            for client in target_clients:
                info = CLIENT_CONFIGS.get(client)
                if not info:
                    continue
                re_enable_server(sname, info["config_path"], info["format"])

    if server_name:
        _unsync_one(server_name)
    else:
        from mcp2cli.constants import SKILLS_DIR
        if SKILLS_DIR.exists():
            for d in SKILLS_DIR.iterdir():
                if d.is_dir():
                    _unsync_one(d.name)


# ---------------------------------------------------------------------------
# install
# ---------------------------------------------------------------------------

@cli.command()
@click.argument("server_name")
@click.option("--env", "env_pairs", multiple=True, help="Env values (KEY=VALUE)")
@click.option("--skill-targets", help="Skill sync targets (comma-separated)")
@click.option("--no-preset", is_flag=True, help="Skip preset check")
@click.option("--preset-version", default=None, help="Use a specific preset version (e.g. 1.2.3)")
@click.option("--yes", is_flag=True, help="Skip confirmation")
def install(
    server_name: str,
    env_pairs: tuple,
    skill_targets: str | None,
    no_preset: bool,
    preset_version: str | None,
    yes: bool,
):
    """Install a new MCP server and generate skill files."""
    from mcp2cli.config.models import ServerConfig
    from mcp2cli.installer.ai_search import ai_search_server
    from mcp2cli.installer.interactive import collect_env_values
    from mcp2cli.installer.pipeline import build_pipeline, run_pipeline
    from mcp2cli.installer.servers_writer import write_server

    preset_envs: dict[str, str] = {}
    for pair in env_pairs:
        if "=" in pair:
            k, v = pair.split("=", 1)
            preset_envs[k] = v

    search_result = ai_search_server(server_name)
    if search_result is None or not search_result.found:
        raise SystemExit(1)

    env_values = collect_env_values(search_result.env, preset_envs)

    config = ServerConfig(
        name=server_name,
        command=search_result.command,
        args=search_result.args,
        env=env_values,
    )

    if not yes:
        click.echo(f"\nWill write to servers.yaml:")
        click.echo(f"  {server_name}:")
        click.echo(f"    command: {config.command} {' '.join(config.args)}")
        if env_values:
            click.echo(f"    env: {', '.join(env_values.keys())} ({len(env_values)} values set)")
        if search_result.source_url:
            click.echo(f"  Source: {search_result.source_url}")

        # Probe for preset before confirmation
        from mcp2cli.preset.checker import probe_preset

        preset_entry = probe_preset(server_name, version=preset_version, no_preset=no_preset)
        if preset_entry is not None:
            _display_preset_info(preset_entry, preset_version)

            if not click.confirm("\nProceed?", default=True):
                click.echo("Aborted.")
                return

    pipeline = build_pipeline(
        server_name, config,
        write_step_name="mcp-add",
        no_preset=no_preset,
        preset_version=preset_version,
    )
    results = run_pipeline(pipeline)

    if results.all_ok:
        click.echo("\n✅ Installation complete!")
        click.echo(f"  Use CLI: mcp2cli {server_name} --help")
        click.echo(f"  Skill is now available in Claude Code, Cursor, and Codex")
    else:
        failed = results.failed_fatal
        click.echo(f"\n⚠ Installation partially complete. Failed steps: {', '.join(failed)}")


# ---------------------------------------------------------------------------
# convert
# ---------------------------------------------------------------------------

@cli.command()
@click.argument("server_name")
@click.option("--source", default="auto", help="Config source (auto/claude/cursor/codex)")
@click.option("--skip-disable", is_flag=True, help="Don't disable original MCP config")
@click.option("--no-preset", is_flag=True, help="Skip preset check")
@click.option("--preset-version", default=None, help="Use a specific preset version (e.g. 1.2.3)")
@click.option("--yes", is_flag=True, help="Skip confirmation")
@click.option("--force", is_flag=True, help="Overwrite servers.yaml entry")
def convert(
    server_name: str,
    source: str,
    skip_disable: bool,
    no_preset: bool,
    preset_version: str | None,
    yes: bool,
    force: bool,
):
    """Convert an already-configured MCP server to skill-based usage."""
    from mcp2cli.converter.config_extractor import ServerNotFoundError, extract_server_config
    from mcp2cli.installer.pipeline import build_pipeline, run_pipeline

    click.echo(f"Finding {server_name} in config sources...")

    try:
        config, sources = extract_server_config(server_name, source)
    except ServerNotFoundError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)

    for src in sources:
        click.echo(f"  Found in: {src.config_path} ({src.client})")

    click.echo(f"\nExtracted config:")
    click.echo(f"  command: {config.command}")
    click.echo(f"  args: {config.args}")
    if config.env:
        click.echo(f"  env: {', '.join(config.env.keys())} ({len(config.env)} vars)")

    # Probe for preset before confirmation
    from mcp2cli.preset.checker import probe_preset

    preset_entry = probe_preset(server_name, version=preset_version, no_preset=no_preset)

    if preset_entry is not None:
        _display_preset_info(preset_entry, preset_version)

        if not yes:
            if not click.confirm("\nProceed?", default=True):
                click.echo("Aborted.")
                return

    pipeline = build_pipeline(
        server_name=server_name,
        config=config,
        force_write=force,
        skip_disable=skip_disable,
        no_preset=no_preset,
        preset_version=preset_version,
    )
    results = run_pipeline(pipeline)

    if results.all_ok:
        click.echo("\n✅ Convert complete!")
        if not skip_disable:
            click.echo("  Original MCP config disabled (can re-enable manually)")
        else:
            click.echo("  Original MCP config was NOT disabled (--skip-disable)")
    else:
        failed = results.failed_fatal
        click.echo(f"\n⚠ Convert partially complete. Failed steps: {', '.join(failed)}")


# ---------------------------------------------------------------------------
# remove / uninstall
# ---------------------------------------------------------------------------

@cli.command()
@click.argument("server_name")
@click.option("--keep-config", is_flag=True, help="Keep servers.yaml config, only remove generated files")
@click.option("--skip-re-enable", is_flag=True, help="Don't re-enable MCP in client configs")
@click.option("--purge-package", is_flag=True, help="Also uninstall the underlying package")
@click.option("--force", "-f", is_flag=True, help="Skip confirmation prompt")
@click.option("--dry-run", is_flag=True, help="Preview actions without modifying files")
def remove(
    server_name: str,
    keep_config: bool,
    skip_re_enable: bool,
    purge_package: bool,
    force: bool,
    dry_run: bool,
):
    """Remove a server and all its generated artifacts."""
    from mcp2cli.installer.pipeline import run_pipeline
    from mcp2cli.remover.pipeline import build_remove_pipeline
    from mcp2cli.remover.scanner import scan_removal_targets

    click.echo(f"Scanning {server_name} artifacts...")

    plan = scan_removal_targets(server_name)

    if plan.is_empty():
        click.echo(f"\nServer \"{server_name}\" not found.")
        click.echo("  Use `mcp2cli list` to see all configured servers.")
        raise SystemExit(1)

    # Show plan
    lines = plan.summary_lines()
    click.echo(f"\nThe following will be removed:")
    for line in lines:
        click.echo(f"  {line}")

    if keep_config:
        click.echo(f"\n  Config: servers.yaml KEPT (--keep-config)")

    if plan.users_has_content and not force:
        click.echo(
            f"\n  Warning: users/ directory has custom content. "
            f"Use --force to proceed.",
            err=True,
        )
        raise SystemExit(1)

    if dry_run:
        click.echo("\n[DRY RUN] No files were modified.")
        return

    if not force:
        if not click.confirm("\nProceed?", default=True):
            click.echo("Aborted.")
            return

    pipeline = build_remove_pipeline(
        plan,
        keep_config=keep_config,
        skip_re_enable=skip_re_enable,
        purge_package=purge_package,
    )
    results = run_pipeline(pipeline)

    if results.all_ok:
        click.echo(f"\n✅ {server_name} removed successfully!")
    else:
        failed = results.failed_fatal
        click.echo(f"\n⚠ Removal partially complete. Failed steps: {', '.join(failed)}")


# Alias: uninstall = remove
cli.add_command(remove, "uninstall")


# ---------------------------------------------------------------------------
# update
# ---------------------------------------------------------------------------

@cli.command()
@click.argument("server_name", required=False)
@click.option("--all", "update_all_flag", is_flag=True, help="Update all registered servers")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation")
@click.option("--dry-run", is_flag=True, help="Preview changes without writing files")
def update(server_name: str | None, update_all_flag: bool, yes: bool, dry_run: bool):
    """Update server tools and regenerate CLI + skill files."""
    from mcp2cli.updater.pipeline import update_all, update_server

    if update_all_flag:
        ok = update_all(yes=yes, dry_run=dry_run)
    elif server_name:
        ok = update_server(server_name, yes=yes, dry_run=dry_run)
    else:
        click.echo("Error: provide a server name or use --all.", err=True)
        raise SystemExit(1)

    if not ok:
        raise SystemExit(1)


# ---------------------------------------------------------------------------
# tools (list tools for a server)
# ---------------------------------------------------------------------------

@cli.command("tools")
@click.argument("server_name")
@click.argument("tool_name", required=False)
def tools_cmd(server_name: str, tool_name: str | None):
    """List tools or show tool details for an MCP server."""
    from mcp2cli.config.tool_store import load_tools

    tools_json = load_tools(server_name)
    if tools_json is None:
        click.echo(f"No tools found for '{server_name}'. Run `mcp2cli scan {server_name}` first.")
        raise SystemExit(1)

    if tool_name:
        tool = next((t for t in tools_json.tools if t.name == tool_name), None)
        if not tool:
            click.echo(f"Tool '{tool_name}' not found in {server_name}.")
            click.echo(f"Available: {', '.join(t.name for t in tools_json.tools)}")
            raise SystemExit(1)

        click.echo(f"Tool: {tool.name}")
        click.echo(f"Description: {tool.description}")
        props = tool.input_schema.get("properties", {})
        required = set(tool.input_schema.get("required", []))
        if props:
            click.echo(f"\nParameters:")
            for pname, pschema in props.items():
                req = "(required)" if pname in required else "(optional)"
                ptype = pschema.get("type", "")
                pdesc = pschema.get("description", "")
                click.echo(f"  --{pname.replace('_', '-'):<25} {req:<12} {ptype:<8} {pdesc}")
    else:
        click.echo(f"Tools for {server_name} ({len(tools_json.tools)} tools):")
        click.echo(f"{'NAME':<40} {'DESCRIPTION'}")
        click.echo("-" * 80)
        for tool in tools_json.tools:
            desc = (tool.description[:55] + "...") if len(tool.description) > 58 else tool.description
            click.echo(f"{tool.name:<40} {desc}")


# ---------------------------------------------------------------------------
# call (direct tool call)
# ---------------------------------------------------------------------------

@cli.command("call")
@click.argument("server_name")
@click.argument("tool_name")
@click.argument("extra_args", nargs=-1, type=click.UNPROCESSED)
@click.option("--timeout", default=60, help="Request timeout in seconds")
def call_cmd(server_name: str, tool_name: str, extra_args: tuple, timeout: int):
    """Directly call an MCP tool by its raw name."""
    from mcp2cli.cli.resolver import _parse_args
    from mcp2cli.daemon.client import call_tool
    from mcp2cli.daemon.lifecycle import ensure_daemon

    params = _parse_args(list(extra_args), server_name, tool_name)

    if not ensure_daemon():
        click.echo("Error: could not start daemon.", err=True)
        raise SystemExit(1)

    response = call_tool(server_name, tool_name, params, timeout=timeout)

    if response.get("ok"):
        click.echo(response.get("result", ""))
    else:
        error = response.get("error", {})
        click.echo(
            f"Error [{error.get('code', 'UNKNOWN')}]: {error.get('message', '')}",
            err=True,
        )
        raise SystemExit(1)


# ---------------------------------------------------------------------------
# daemon
# ---------------------------------------------------------------------------

@cli.group("daemon")
def daemon_group():
    """Manage the MCP proxy daemon."""
    pass


@daemon_group.command("status")
def daemon_status_cmd():
    """Show daemon status."""
    from mcp2cli.daemon.lifecycle import get_daemon_info

    info = get_daemon_info()
    if info is None:
        click.echo("Daemon is not running.")
        return

    click.echo(f"Daemon is running:")
    click.echo(f"  PID: {info['pid']}")
    click.echo(f"  Socket: {info['socket']}")
    servers = info.get("servers", [])
    if servers:
        click.echo(f"  Active servers: {', '.join(servers)}")
    else:
        click.echo(f"  Active servers: (none)")


@daemon_group.command("stop")
def daemon_stop_cmd():
    """Stop the daemon."""
    from mcp2cli.daemon.lifecycle import stop_daemon

    if stop_daemon():
        click.echo("Daemon stopped.")
    else:
        click.echo("Daemon is not running.")


# ---------------------------------------------------------------------------
# preset
# ---------------------------------------------------------------------------

@cli.group("preset")
def preset_group():
    """Manage preset skill files from remote repository."""
    pass


@preset_group.command("list")
@click.argument("server_name", required=False)
@click.option("--local", "local_only", is_flag=True, help="Show only local presets")
def preset_list_cmd(server_name: str | None, local_only: bool):
    """List presets with local and remote status."""
    from mcp2cli.preset.local import scan_local_presets
    from mcp2cli.preset.registry import fetch_index

    local_map = scan_local_presets()
    index = None if local_only else fetch_index()

    # Detail view for a single server
    if server_name:
        local_ver = local_map.get(server_name)
        remote_entry = index.find(server_name) if index else None

        if not local_ver and not remote_entry:
            click.echo(f"No preset found for '{server_name}'.")
            raise SystemExit(1)

        click.echo(f"Preset: {server_name}")
        click.echo(f"  Local:       {local_ver or '-'}")
        if remote_entry:
            click.echo(f"  Remote:      {remote_entry.latest}")
            click.echo(f"  Versions:    {', '.join(remote_entry.versions)}")
            click.echo(f"  Updated:     {remote_entry.updated_at[:10] if remote_entry.updated_at else '-'}")
            if remote_entry.description:
                click.echo(f"  Description: {remote_entry.description}")
        else:
            click.echo(f"  Remote:      -")

        status = _preset_status(local_ver, remote_entry)
        click.echo(f"  Status:      {status}")
        return

    # Unified list view
    all_names: set[str] = set(local_map.keys())
    if index:
        for p in index.presets:
            all_names.add(p.server)

    if not all_names:
        click.echo("No presets found (local or remote).")
        return

    click.echo(f"  {'NAME':<25} {'LOCAL':<12} {'REMOTE':<12} {'STATUS'}")
    click.echo("  " + "-" * 65)
    for name in sorted(all_names):
        local_ver = local_map.get(name)
        remote_entry = index.find(name) if index else None
        remote_ver = remote_entry.latest if remote_entry else None
        status = _preset_status(local_ver, remote_entry)
        click.echo(
            f"  {name:<25} {local_ver or '-':<12} {remote_ver or '-':<12} {status}"
        )

    total = len(all_names)
    local_count = len(local_map)
    remote_count = len(index.presets) if index else 0
    click.echo(f"\n{total} presets ({local_count} local, {remote_count} remote).")


@preset_group.command("pull")
@click.argument("preset_spec")
@click.option(
    "--sync/--no-sync",
    "do_sync",
    default=True,
    help="Sync to AI clients after pull (default: enabled)",
)
@click.option("--force", is_flag=True, help="Overwrite existing local files")
@click.option("--dry-run", is_flag=True, help="Preview files without downloading")
def preset_pull_cmd(preset_spec: str, do_sync: bool, force: bool, dry_run: bool):
    """Pull preset files for a server from remote repository.

    Supports 'name@version' syntax (e.g. mcp-atlassian@1.2.3).
    Without a version, pulls the latest.
    """
    from mcp2cli.preset.downloader import pull_preset
    from mcp2cli.preset.version import parse_preset_spec

    server_name, version = parse_preset_spec(preset_spec)

    ok = pull_preset(server_name, version=version, force=force, dry_run=dry_run)
    if not ok:
        raise SystemExit(1)

    if dry_run:
        return

    if do_sync:
        from mcp2cli.installer.skill_sync import skill_sync
        click.echo("\nSyncing skill to AI clients...")
        skill_sync(server_name)
    else:
        click.echo(f"\nNext: run 'mcp2cli skill sync {server_name}' to copy to AI clients.")


@preset_group.command("export")
@click.argument("server_name")
@click.option("--version", "preset_version", default=None, help="Override version (default: from tools.json)")
@click.option("-o", "--output", "output_dir", default=".", help="Output directory (default: current directory)")
@click.option("--yes", is_flag=True, help="Skip confirmation")
def preset_export_cmd(server_name: str, preset_version: str | None, output_dir: str, yes: bool):
    """Export a preset bundle to a local directory.

    Validates local files and writes the preset bundle (tools.json, cli.yaml,
    skills/, manifest.json) to <output>/<server>/<version>/.
    """
    from mcp2cli.preset.exporter import export_preset

    ok = export_preset(server_name, version=preset_version, output_dir=output_dir, yes=yes)
    if not ok:
        raise SystemExit(1)


@preset_group.command("push")
@click.argument("server_name")
@click.option("--version", "preset_version", default=None, help="Override version (default: from tools.json)")
@click.option("--yes", is_flag=True, help="Skip confirmation")
def preset_push_cmd(server_name: str, preset_version: str | None, yes: bool):
    """Push local preset files to the remote repository via git SSH.

    Validates local files, assembles the preset bundle, pushes to a new
    branch, then prints a URL to open in your browser to create the PR.

    Requires git and an SSH key configured for the target repository.
    """
    from mcp2cli.preset.pusher import push_preset

    ok = push_preset(server_name, version=preset_version, yes=yes)
    if not ok:
        raise SystemExit(1)


# Alias: export = preset export
cli.add_command(preset_export_cmd, "export")


if __name__ == "__main__":
    cli()
