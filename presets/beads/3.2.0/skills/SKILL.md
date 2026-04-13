---
name: "beads"
description: Manage issues, track dependencies, and monitor workspace progress via CLI. Use when user needs to create/list/update issues, manage blockers, claim work, or get project stats.
source_version: "3.2.0"
source_cli_hash: "07387276"
generated_at: "2026-04-06T08:53:07.680832+00:00"
---

# beads (via mcp2cli)

Lightweight issue tracker with dependency management and workspace context.

## Shortcuts

No shortcuts defined. Base command: `mcp2cli beads <cmd>`

## Commands

### Issue
| Command | Description | Example | Ref |
|---|---|---|---|
| `mcp2cli beads issue create` | Create a new issue | `mcp2cli beads issue create --title "Fix memory leak" --issue-type bug`<br>`mcp2cli beads issue create --title "Add login" --issue-type feature --assignee alice` | [ref](reference/issue.md) |
| `mcp2cli beads issue get` | Get detailed issue info | `mcp2cli beads issue get --issue-id ISSUE-1` | [ref](reference/issue.md) |
| `mcp2cli beads issue list` | List issues with filters | `mcp2cli beads issue list --status open --assignee alice` | [ref](reference/issue.md) |
| `mcp2cli beads issue update` | Update issue fields | `mcp2cli beads issue update --issue-id ISSUE-1 --status in_progress` | [ref](reference/issue.md) |
| `mcp2cli beads issue close` | Close/complete an issue | `mcp2cli beads issue close --issue-id ISSUE-1` | [ref](reference/issue.md) |
| `mcp2cli beads issue claim` | Atomically claim an issue for work | `mcp2cli beads issue claim --issue-id ISSUE-1` | [ref](reference/issue.md) |
| `mcp2cli beads issue ready` | Find issues with no blockers | `mcp2cli beads issue ready`<br>`mcp2cli beads issue ready --assignee alice --limit 5` | [ref](reference/issue.md) |
| `mcp2cli beads issue blocked` | Get blocked issues | `mcp2cli beads issue blocked` | [ref](reference/issue.md) |

### Workspace
| Command | Description | Example | Ref |
|---|---|---|---|
| `mcp2cli beads dep` | Add dependency between issues | `mcp2cli beads dep --issue-id ISSUE-2 --depends-on-id ISSUE-1` | [ref](reference/workspace.md) |
| `mcp2cli beads stats` | Get issue statistics | `mcp2cli beads stats` | [ref](reference/workspace.md) |
| `mcp2cli beads context` | Manage workspace context | `mcp2cli beads context --action show` | [ref](reference/workspace.md) |
| `mcp2cli beads admin` | Admin/diagnostic operations | `mcp2cli beads admin --action validate` | [ref](reference/workspace.md) |
| `mcp2cli beads tool list` | List available tools | `mcp2cli beads tool list` | [ref](reference/workspace.md) |

## Discover Parameters

Append `--help` to any command for full parameter list:

    mcp2cli beads issue create --help

> **Note**: Use Ref links in the Commands table above to view detailed parameter reference and more examples.

## User Notes

> **MUST READ** [users/skill.md](users/skill.md) for custom workflows and tips.
> **Config**: MCP server settings live in `~/.agents/mcp2cli/servers.yaml` - edit there to take effect.
