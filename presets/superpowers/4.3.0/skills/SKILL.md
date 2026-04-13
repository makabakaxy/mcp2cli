---
name: "superpowers"
description: List and read Superpowers skills via CLI. Use when user needs to discover available skills or load skill instructions before performing a task.
source_version: "4.3.0"
source_cli_hash: "44dd1b4e"
generated_at: "2026-04-06T08:06:14.580512+00:00"
---

# superpowers (via mcp2cli)

Discover and read Superpowers skill instructions via CLI.

## Shortcuts

No shortcuts or server aliases configured.

## Commands

### Skill
| Command | Description | Example | Ref |
|---|---|---|---|
| `mcp2cli superpowers skill list` | List all available skills | `mcp2cli superpowers skill list` | [ref](reference/skill.md) |
| `mcp2cli superpowers skill get` | Read full content of a skill by name | `mcp2cli superpowers skill get --skill-name brainstorming`<br>`mcp2cli superpowers skill get --skill-name systematic-debugging` | [ref](reference/skill.md) |

## Discover Parameters

Append `--help` to any command for full parameter list:

    mcp2cli superpowers skill get --help

> **Note**: Use Ref links in the Commands table above to view detailed parameter reference and more examples.

## User Notes

> **MUST READ** [users/skill.md](users/skill.md) for custom workflows and tips.
> **Config**: MCP server settings live in `~/.agents/mcp2cli/servers.yaml` - edit there to take effect.
