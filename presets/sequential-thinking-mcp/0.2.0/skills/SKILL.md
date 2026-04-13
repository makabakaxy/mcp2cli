---
name: "sequential-thinking-mcp"
description: Perform dynamic, reflective sequential reasoning for complex problem-solving. Use when user needs to break down problems step-by-step, plan with revision, or maintain multi-step reasoning context.
source_version: "0.2.0"
source_cli_hash: "a8b1ed57"
generated_at: "2026-04-06T09:09:09.667851+00:00"
---

# sequential-thinking-mcp (via mcp2cli)

Dynamic sequential reasoning through adaptive, revisable thought steps.

## Shortcuts

- `mcp2cli sequential-thinking <cmd>`

## Commands

### Think
| Command | Description | Example | Ref |
|---|---|---|---|
| `mcp2cli sequential-thinking think` | Execute a sequential thinking step | `mcp2cli sequential-thinking think --thought "Analyze the problem scope" --thought-number 1 --total-thoughts 5 --next-thought-needed true`<br>`mcp2cli sequential-thinking think --thought "Revise approach based on findings" --thought-number 3 --total-thoughts 5 --next-thought-needed false` | [ref](reference/think.md) |

## Discover Parameters

Append `--help` to any command for full parameter list:

    mcp2cli sequential-thinking think --help

> **Note**: Use Ref links in the Commands table above to view detailed parameter reference and more examples.

## User Notes

> **MUST READ** [users/skill.md](users/skill.md) for custom workflows and tips.
> **Config**: MCP server settings live in `~/.agents/mcp2cli/servers.yaml` - edit there to take effect.
