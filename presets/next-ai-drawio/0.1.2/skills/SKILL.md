---
name: "next-ai-drawio"
description: Create, edit, and export draw.io diagrams via CLI with real-time browser preview. Use when user needs to create flowcharts, diagrams, or edit mxGraphModel XML diagrams.
source_version: "0.1.2"
source_cli_hash: "43de5f35"
generated_at: "2026-04-06T08:44:27.228580+00:00"
---

# next-ai-drawio (via mcp2cli)

Create and manage draw.io diagrams via CLI with live browser preview.

## Shortcuts

- `mcp2cli drawio <cmd>` (alias for `next-ai-drawio`)

## Commands

### Session
| Command | Description | Example | Ref |
|---|---|---|---|
| `mcp2cli drawio session start` | Start diagram session and open browser for live preview | `mcp2cli drawio session start` | [ref](reference/session.md) |

### Diagram
| Command | Description | Example | Ref |
|---|---|---|---|
| `mcp2cli drawio diagram create` | Create a new diagram from mxGraphModel XML | `mcp2cli drawio diagram create --xml '<mxGraphModel>...</mxGraphModel>'` | [ref](reference/diagram.md) |
| `mcp2cli drawio diagram get` | Get the current diagram XML from browser | `mcp2cli drawio diagram get` | [ref](reference/diagram.md) |
| `mcp2cli drawio diagram edit` | Edit diagram by ID-based cell operations (add/update/delete) | | [ref](reference/diagram.md) |
| `mcp2cli drawio diagram export` | Export diagram to file (.drawio/.png/.svg) | `mcp2cli drawio diagram export --path ./diagram.png` | [ref](reference/diagram.md) |

## Discover Parameters

Append `--help` to any command for full parameter list:

    mcp2cli drawio diagram create --help

> **Note**: Use Ref links in the Commands table above to view detailed parameter reference and more examples.

## User Notes

> **MUST READ** [users/skill.md](users/skill.md) for custom workflows and tips.
> **Config**: MCP server settings live in `~/.agents/mcp2cli/servers.yaml` - edit there to take effect.
