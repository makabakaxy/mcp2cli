---
name: "cloudflare-mcp"
description: Search Cloudflare documentation and get migration guides via CLI. Use when user needs to look up Workers, Pages, R2, D1, KV, Zero Trust, CDN, DNS, or any Cloudflare product/feature documentation.
source_version: "0.4.6"
source_cli_hash: "44e22a42"
generated_at: "2026-04-06T09:19:19.468070+00:00"
---

# cloudflare-mcp (via mcp2cli)

Search Cloudflare docs and get migration guides via CLI.

## Shortcuts

- `mcp2cli cloudflare <cmd>` (alias for `mcp2cli cloudflare-mcp`)

## Commands

### Docs
| Command | Description | Example | Ref |
|---|---|---|---|
| `mcp2cli cloudflare docs search` | Search Cloudflare documentation | `mcp2cli cloudflare docs search --query "Workers KV storage"`<br>`mcp2cli cloudflare docs search --query "Zero Trust Access policy"` | [ref](reference/docs.md) |
| `mcp2cli cloudflare docs migrate-guide` | Get Pages→Workers migration guide | `mcp2cli cloudflare docs migrate-guide` | [ref](reference/docs.md) |

## Discover Parameters

Append `--help` to any command for full parameter list:

    mcp2cli cloudflare docs search --help

> **Note**: Use Ref links in the Commands table above to view detailed parameter reference and more examples.

## User Notes

> **MUST READ** [users/skill.md](users/skill.md) for custom workflows and tips.
> **Config**: MCP server settings live in `~/.agents/mcp2cli/servers.yaml` - edit there to take effect.
