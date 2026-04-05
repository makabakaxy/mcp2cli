"""Remove pipeline assembly."""

from __future__ import annotations

from mcp2cli.installer.pipeline import Step
from mcp2cli.remover.scanner import RemovalPlan


def build_remove_pipeline(
    plan: RemovalPlan,
    keep_config: bool = False,
    skip_re_enable: bool = False,
    purge_package: bool = False,
) -> list[Step]:
    """Build the remove-specific pipeline (reverse order of install/convert)."""
    from mcp2cli.installer.servers_writer import remove_server
    from mcp2cli.remover.cleaner import delete_dir, delete_file, unsync_skills
    from mcp2cli.remover.config_re_enabler import re_enable_in_clients
    from mcp2cli.remover.package_purger import purge_package as purge_fn

    steps: list[Step] = []

    # Step 1: remove skill copy directories
    if plan.skill_copies or plan.agents_skill_dir:
        steps.append(Step(
            name="skill-unsync",
            run=lambda: unsync_skills(plan.server_name, plan.skill_copies, plan.agents_skill_dir),
            retry_cmd=f"mcp2cli skill unsync {plan.server_name}",
        ))

    # Step 2: delete skill source directory
    if plan.skills_dir:
        steps.append(Step(
            name="delete-skills",
            run=lambda: delete_dir(plan.skills_dir, keep_users=plan.keep_users),
            retry_cmd=f"rm -rf {plan.skills_dir}",
        ))

    # Step 3: delete CLI mapping
    if plan.cli_yaml:
        steps.append(Step(
            name="delete-cli",
            run=lambda: delete_file(plan.cli_yaml),
            retry_cmd=f"rm {plan.cli_yaml}",
        ))

    # Step 4: delete tools cache
    if plan.tools_json:
        steps.append(Step(
            name="delete-tools",
            run=lambda: delete_file(plan.tools_json),
            retry_cmd=f"rm {plan.tools_json}",
        ))

    # Step 5: remove servers.yaml entry
    if plan.servers_yaml_entry and not keep_config:
        steps.append(Step(
            name="remove-config",
            run=lambda: remove_server(plan.server_name),
            retry_cmd=f"mcp2cli mcp remove {plan.server_name}",
        ))

    # Step 6: re-enable client configs
    if plan.disabled_sources and not skip_re_enable:
        steps.append(Step(
            name="re-enable-clients",
            run=lambda: re_enable_in_clients(plan.server_name, plan.disabled_sources),
            retry_cmd='(manually remove "disabled": true from client configs)',
        ))

    # Step 7: purge package (optional)
    if purge_package and plan.package_info:
        steps.append(Step(
            name="purge-package",
            run=lambda: purge_fn(plan.package_info),
            retry_cmd=f"(manual: {plan.package_info.uninstall_cmd})",
        ))

    # Step 8: daemon disconnect
    steps.append(Step(
        name="daemon-disconnect",
        run=lambda: _daemon_disconnect(plan.server_name),
        retry_cmd="(daemon auto-reclaims idle connections)",
    ))

    return steps


def _daemon_disconnect(server_name: str) -> bool:
    """Notify daemon to disconnect the server. Non-blocking."""
    from mcp2cli.daemon.client import daemon_disconnect
    from mcp2cli.daemon.lifecycle import is_daemon_running

    if not is_daemon_running():
        return True
    return daemon_disconnect(server_name)
