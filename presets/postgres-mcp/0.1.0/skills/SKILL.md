---
name: "postgres-mcp"
description: Run read-only SQL queries against a PostgreSQL database via CLI. Use when user needs to query, inspect, or retrieve data from a Postgres database.
source_version: "0.1.0"
source_cli_hash: "04fa3686"
generated_at: "2026-04-06T09:14:02.467594+00:00"
---

# postgres-mcp (via mcp2cli)

Run read-only SQL queries against a PostgreSQL database.

## Shortcuts

- `mcp2cli postgres <cmd>` (alias for `mcp2cli postgres-mcp`)

## Commands

### Query
| Command | Description | Example | Ref |
|---|---|---|---|
| `mcp2cli postgres query` | Run a read-only SQL query | `mcp2cli postgres query --sql 'SELECT * FROM users LIMIT 10'`<br>`mcp2cli postgres query --sql 'SELECT table_name FROM information_schema.tables WHERE table_schema='"'"'public'"'"''` | [ref](reference/query.md) |

## Discover Parameters

Append `--help` to any command for full parameter list:

    mcp2cli postgres query --help

> **Note**: Use Ref links in the Commands table above to view detailed parameter reference and more examples.

## User Notes

> **MUST READ** [users/skill.md](users/skill.md) for custom workflows and tips.
> **Config**: MCP server settings live in `~/.agents/mcp2cli/servers.yaml` - edit there to take effect.
