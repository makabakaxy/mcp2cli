---
name: "agentops-mcp"
description: Monitor AI agent traces and spans via CLI. Use when user needs to authorize with AgentOps, retrieve trace information, or inspect span metrics.
source_version: "0.3.0"
source_cli_hash: "e025631a"
generated_at: "2026-04-06T09:03:03.084973+00:00"
---

# agentops-mcp (via mcp2cli)

Monitor AI agent observability data via AgentOps — traces, spans, and metrics.

## Shortcuts

- `mcp2cli agentops <cmd>` (alias for `mcp2cli agentops-mcp`)

## Commands

### Auth
| Command | Description | Example | Ref |
|---|---|---|---|
| `mcp2cli agentops auth` | Authorize with AgentOps API key | `mcp2cli agentops auth --api-key YOUR_KEY` | [ref](reference/auth.md) |

### Trace
| Command | Description | Example | Ref |
|---|---|---|---|
| `mcp2cli agentops trace get` | Get trace info and metrics by ID | `mcp2cli agentops trace get --trace-id abc123` | [ref](reference/trace.md) |
| `mcp2cli agentops trace get-complete` | Get complete trace with all data | `mcp2cli agentops trace get-complete --trace-id abc123` | [ref](reference/trace.md) |

### Span
| Command | Description | Example | Ref |
|---|---|---|---|
| `mcp2cli agentops span get` | Get span info and metrics by ID | `mcp2cli agentops span get --span-id xyz456` | [ref](reference/span.md) |

## Discover Parameters

Append `--help` to any command for full parameter list:

    mcp2cli agentops trace get --help

> **Note**: Use Ref links in the Commands table above to view detailed parameter reference and more examples.

## User Notes

> **MUST READ** [users/skill.md](users/skill.md) for custom workflows and tips.
> **Config**: MCP server settings live in `~/.agents/mcp2cli/servers.yaml` - edit there to take effect.
