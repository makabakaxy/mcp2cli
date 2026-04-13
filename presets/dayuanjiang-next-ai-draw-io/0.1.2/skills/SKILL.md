---
name: "dayuanjiang/next-ai-draw-io"
description: Create, edit, and export draw.io diagrams via CLI with real-time browser preview. Use when user needs to create or modify diagrams, generate mxGraphModel XML, or export diagrams as PNG/SVG.
source_version: "0.1.2"
source_cli_hash: "7a303472"
generated_at: "2026-04-05T08:11:21.312972+00:00"
---

# dayuanjiang/next-ai-draw-io (via mcp2cli)

Create and edit draw.io diagrams with real-time browser preview.

## Shortcuts

- `mcp2cli diagram <cmd>`
- `mcp2cli session <cmd>`
- `mcp2cli next-ai-draw-io <cmd>`

## Commands

### Session
| Command | Description | Example | Ref |
|---|---|---|---|
| `mcp2cli session start` | Start session and open browser preview | `mcp2cli session start` | [ref](reference/session.md) |

### Diagram
| Command | Description | Example | Ref |
|---|---|---|---|
| `mcp2cli diagram create` | Create a new diagram from mxGraphModel XML | `mcp2cli diagram create --xml '<mxGraphModel>...</mxGraphModel>'` | [ref](reference/diagram.md) |
| `mcp2cli diagram get` | Get current diagram XML from browser | `mcp2cli diagram get` | [ref](reference/diagram.md) |
| `mcp2cli diagram edit` | Edit diagram using ID-based cell operations | `mcp2cli diagram edit --operations '[{"operation":"add","cell_id":"rect-1","new_xml":"..."}]'` | [ref](reference/diagram.md) |
| `mcp2cli diagram export` | Export diagram to file (.drawio/.png/.svg) | `mcp2cli diagram export --path ./diagram.png` | [ref](reference/diagram.md) |

## Discover Parameters

Append `--help` to any command for full parameter list:

    mcp2cli diagram create --help

> **Note**: Use Ref links above to view detailed parameter reference and examples.

## User Notes

> **MUST READ** [users/skill.md](users/skill.md) for custom workflows and tips.
> **Config**: MCP server settings live in `~/.agents/mcp2cli/servers.yaml` - edit there to take effect.
