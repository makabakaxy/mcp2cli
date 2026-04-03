"""Interactive environment variable input."""

from __future__ import annotations

import getpass

import click


def collect_env_values(
    env_defs: dict[str, dict],
    preset_envs: dict[str, str] | None = None,
) -> dict[str, str]:
    """Interactively collect env values from user.

    Args:
        env_defs: Env variable definitions from AI search result.
                  Each value is a dict with 'description', 'example', 'required', 'sensitive'.
        preset_envs: Pre-set env values from --env flags.

    Returns:
        Dict of env_name -> env_value.
    """
    preset_envs = preset_envs or {}
    result: dict[str, str] = {}

    click.echo("\n📋 Environment variables:")

    for name, info in env_defs.items():
        description = info.get("description", "")
        example = info.get("example", "")
        required = info.get("required", False)
        sensitive = info.get("sensitive", False)

        # Use preset value if available
        if name in preset_envs:
            result[name] = preset_envs[name]
            display = "****" if sensitive else preset_envs[name]
            click.echo(f"  {name}: {display} (from --env)")
            continue

        # Build prompt
        req_str = ", required" if required else ", optional"
        sens_str = ", sensitive" if sensitive else ""
        prompt_text = f"  {name} ({description}{req_str}{sens_str})"
        if example:
            prompt_text += f"\n    example: {example}"

        click.echo(prompt_text)

        skip_hint = ", Enter to skip" if not required else ""
        if sensitive:
            value = getpass.getpass(f"  > {'(required) ' if required else f'(optional{skip_hint}) '}")
        else:
            prompt_label = "  > (required)" if required else f"  > (optional{skip_hint})"
            value = click.prompt(prompt_label, default="" if not required else None, show_default=False)

        if value:
            result[name] = value
        elif required:
            click.echo("    ⚠ Required but empty — server may not work correctly")
        else:
            click.echo("    (skipped)")

    return result
