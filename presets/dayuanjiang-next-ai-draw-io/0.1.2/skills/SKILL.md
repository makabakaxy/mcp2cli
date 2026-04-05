---
name: "dayuanjiang/next-ai-draw-io"
description: Create, edit, and export draw.io diagrams via CLI with real-time browser preview. Use when user needs to create or modify diagrams, edit diagram elements, or export diagrams to PNG/SVG/drawio files.
source_version: "0.1.2"
source_cli_hash: "8bc1729d"
generated_at: "2026-04-05T07:02:59.842676+00:00"
---

# dayuanjiang/next-ai-draw-io (via mcp2cli)

Create and manage draw.io diagrams via CLI with real-time browser preview.

## Shortcuts

- `mcp2cli next-ai-draw-io <cmd>`

## Commands

### Session
| Command | Description | Example | Ref |
|---|---|---|---|
| `mcp2cli next-ai-draw-io session start` | Start a new diagram session and open browser for real-time preview | `mcp2cli next-ai-draw-io session start` | [ref](reference/session.md) |

### Diagram
| Command | Description | Example | Ref |
|---|---|---|---|
| `mcp2cli next-ai-draw-io diagram create` | Create a new diagram from mxGraphModel XML | `mcp2cli next-ai-draw-io diagram create --xml '<mxGraphModel>...</mxGraphModel>'` | [ref](reference/diagram.md) |
| `mcp2cli next-ai-draw-io diagram get` | Get the current diagram XML from browser | `mcp2cli next-ai-draw-io diagram get` | [ref](reference/diagram.md) |
| `mcp2cli next-ai-draw-io diagram edit` | Edit diagram by ID-based cell operations (add/update/delete) | `mcp2cli next-ai-draw-io diagram edit --operations '[{"operation":"add","cell_id":"r1","new_xml":"..."}]'` | [ref](reference/diagram.md) |
| `mcp2cli next-ai-draw-io diagram download` | Export the current diagram to a file | `mcp2cli next-ai-draw-io diagram download --path ./diagram.png`<br>`mcp2cli next-ai-draw-io diagram download --path ./diagram.svg --format svg` | [ref](reference/diagram.md) |

## Discover Parameters

Append `--help` to any command for full parameter list:

    mcp2cli next-ai-draw-io diagram create --help

> **Note**: Use Ref links in the Commands table above to view detailed parameter reference and more examples.

## User Notes

> **MUST READ** [users/SKILL.md](users/SKILL.md) for custom workflows and tips.
> See [users/workflows.md](users/workflows.md) for multi-step workflow examples.
> Not overwritten by updates.
