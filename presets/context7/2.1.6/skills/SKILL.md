---
name: context7
description: Fetch up-to-date library documentation and code examples via Context7. Use when user needs to resolve library IDs or query docs for any programming library or framework.
source_version: "2.1.6"
source_cli_hash: "33f99894"
generated_at: "2026-04-06T08:07:46.791875+00:00"
---

# context7 (via mcp2cli)

Resolve library IDs and query up-to-date documentation and code examples from Context7.

## Shortcuts

No shortcuts configured. Use full command form: `mcp2cli context7 <cmd>`

## Commands

### Library
| Command | Description | Example | Ref |
|---|---|---|---|
| `mcp2cli context7 library resolve` | Resolve a library name to a Context7-compatible library ID | `mcp2cli context7 library resolve --library-name react --query 'hooks usage'`<br>`mcp2cli context7 library resolve --library-name 'next.js' --query 'server side rendering'` | [ref](reference/library.md) |
| `mcp2cli context7 library search` | Query up-to-date docs and code examples for a library | `mcp2cli context7 library search --library-id '/vercel/next.js' --query 'How to set up authentication with JWT'` | [ref](reference/library.md) |

## Discover Parameters

Append `--help` to any command for full parameter list:

    mcp2cli context7 library resolve --help

> **Note**: Use Ref links in the Commands table above to view detailed parameter reference and more examples.

## User Notes

> **MUST READ** [users/skill.md](users/skill.md) for custom workflows and tips.
> **Config**: MCP server settings live in `~/.agents/mcp2cli/servers.yaml` - edit there to take effect.
