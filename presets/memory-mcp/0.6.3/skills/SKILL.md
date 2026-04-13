---
name: memory-mcp
description: Manage a persistent knowledge graph with entities, relations, and observations via CLI. Use when user needs to store, retrieve, search, or update structured memory/knowledge.
source_version: "0.6.3"
source_cli_hash: "c015fc36"
generated_at: "2026-04-06T09:11:02.618250+00:00"
---

# memory-mcp (via mcp2cli)

Manage a persistent knowledge graph: entities, relations, observations.

## Shortcuts

- `mcp2cli memory <cmd>` (alias for `mcp2cli memory-mcp`)

## Commands

### Entity
| Command | Description | Example | Ref |
|---|---|---|---|
| `mcp2cli memory entity create` | Create entities in the knowledge graph | `mcp2cli memory entity create --entities '[{"name": "Alice", "entityType": "Person", "observations": ["Engineer"]}]'` | [ref](reference/entity.md) |
| `mcp2cli memory entity delete` | Delete entities and their relations | `mcp2cli memory entity delete --entity-names '["Alice"]'` | [ref](reference/entity.md) |

### Relation
| Command | Description | Example | Ref |
|---|---|---|---|
| `mcp2cli memory relation create` | Create relations between entities | `mcp2cli memory relation create --relations '[{"from": "Alice", "to": "Bob", "relationType": "knows"}]'` | [ref](reference/relation.md) |
| `mcp2cli memory relation delete` | Delete relations from the graph | | [ref](reference/relation.md) |

### Observation
| Command | Description | Example | Ref |
|---|---|---|---|
| `mcp2cli memory observation add` | Add observations to existing entities | `mcp2cli memory observation add --observations '[{"entityName": "Alice", "contents": ["Joined 2024"]}]'` | [ref](reference/observation.md) |
| `mcp2cli memory observation delete` | Delete observations from entities | | [ref](reference/observation.md) |

### Graph & Node
| Command | Description | Example | Ref |
|---|---|---|---|
| `mcp2cli memory graph get` | Read the entire knowledge graph | `mcp2cli memory graph get` | [ref](reference/graph.md) |
| `mcp2cli memory node search` | Search nodes by query | `mcp2cli memory node search --query "Alice"` | [ref](reference/node.md) |
| `mcp2cli memory node get` | Get specific nodes by name | `mcp2cli memory node get --names '["Alice", "Bob"]'` | [ref](reference/node.md) |

## Discover Parameters

Append `--help` to any command for full parameter list:

    mcp2cli memory entity create --help

> **Note**: Use Ref links in the Commands table above to view detailed parameter reference and more examples.

## User Notes

> **MUST READ** [users/skill.md](users/skill.md) for custom workflows and tips.
> **Config**: MCP server settings live in `~/.agents/mcp2cli/servers.yaml` - edit there to take effect.
