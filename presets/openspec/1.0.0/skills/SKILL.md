---
name: openspec
description: Manage OpenSpec change lifecycle and project specs via CLI. Use when user needs to create/archive changes, check artifact status, validate proposals, or browse specs.
source_version: "1.0.0"
source_cli_hash: "9c6172a4"
generated_at: "2026-04-06T08:22:31.209231+00:00"
---

# openspec (via mcp2cli)

Manage OpenSpec change lifecycle — create, track, validate, and archive spec changes.

## Shortcuts

No shortcuts configured. Use: `mcp2cli openspec <group> <cmd>`

## Commands

### project
| Command | Description | Example | Ref |
|---|---|---|---|
| `mcp2cli openspec project init` | Initialize OpenSpec in your project | `mcp2cli openspec project init` | [ref](reference/project.md) |
| `mcp2cli openspec project update` | Update OpenSpec instruction files | `mcp2cli openspec project update` | [ref](reference/project.md) |
| `mcp2cli openspec project refresh-cache` | Force refresh the cached directory listing | `mcp2cli openspec project refresh-cache` | [ref](reference/project.md) |

### change
| Command | Description | Example | Ref |
|---|---|---|---|
| `mcp2cli openspec change create` | Create a new change directory | `mcp2cli openspec change create --name add-dark-mode --description "Add dark mode support"` | [ref](reference/change.md) |
| `mcp2cli openspec change status` | Display artifact completion status | `mcp2cli openspec change status --change-name add-dark-mode` | [ref](reference/change.md) |
| `mcp2cli openspec change instructions` | Output enriched instructions for an artifact | `mcp2cli openspec change instructions --artifact design.md --change-name add-dark-mode` | [ref](reference/change.md) |
| `mcp2cli openspec change archive` | Archive a completed change and update main specs | `mcp2cli openspec change archive --change-name add-dark-mode` | [ref](reference/change.md) |

### content
| Command | Description | Example | Ref |
|---|---|---|---|
| `mcp2cli openspec content list` | List changes or specs | `mcp2cli openspec content list`<br>`mcp2cli openspec content list --specs` | [ref](reference/content.md) |
| `mcp2cli openspec content show` | Show details of a change or spec | `mcp2cli openspec content show --item-name add-dark-mode` | [ref](reference/content.md) |
| `mcp2cli openspec content read-file` | Read any OpenSpec artifact file directly | `mcp2cli openspec content read-file --name add-dark-mode --file-type design.md` | [ref](reference/content.md) |
| `mcp2cli openspec content validate` | Validate a change proposal or spec | `mcp2cli openspec content validate --item-name add-dark-mode` | [ref](reference/content.md) |

## Discover Parameters

Append `--help` to any command for full parameter list:

    mcp2cli openspec change create --help

> **Note**: Use Ref links in the Commands table above to view detailed parameter reference and more examples.

## User Notes

> **MUST READ** [users/skill.md](users/skill.md) for custom workflows and tips.
> **Config**: MCP server settings live in `~/.agents/mcp2cli/servers.yaml` - edit there to take effect.
