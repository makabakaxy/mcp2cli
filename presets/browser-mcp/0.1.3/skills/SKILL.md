---
name: "browser-mcp"
description: Automate browser navigation, element interaction, and page capture via CLI. Use when user needs to navigate URLs, click/type/select page elements, take screenshots, or extract console logs.
source_version: "0.1.3"
source_cli_hash: "7e4a4a23"
generated_at: "2026-04-06T09:05:20.157997+00:00"
---

# browser-mcp (via mcp2cli)

Automate browser interactions via CLI.

## Shortcuts

- `mcp2cli browser <cmd>` (alias for `mcp2cli browser-mcp`)

## Commands

### Navigate
| Command | Description | Example | Ref |
|---|---|---|---|
| `mcp2cli browser navigate go` | Navigate to a URL | `mcp2cli browser navigate go --url https://example.com` | [ref](reference/navigate.md) |
| `mcp2cli browser navigate back` | Go back to the previous page | `mcp2cli browser navigate back` | [ref](reference/navigate.md) |
| `mcp2cli browser navigate forward` | Go forward to the next page | `mcp2cli browser navigate forward` | [ref](reference/navigate.md) |

### Interact
| Command | Description | Example | Ref |
|---|---|---|---|
| `mcp2cli browser interact click` | Click on a web page element | `mcp2cli browser interact click --element "Submit button" --ref e123` | [ref](reference/interact.md) |
| `mcp2cli browser interact type` | Type text into an editable element | `mcp2cli browser interact type --element "Search box" --ref e456 --text "hello" --submit true` | [ref](reference/interact.md) |
| `mcp2cli browser interact select-option` | Select an option in a dropdown | `mcp2cli browser interact select-option --element "Country" --ref e789 --values '["US"]'` | [ref](reference/interact.md) |
| `mcp2cli browser interact hover` | Hover over a page element | `mcp2cli browser interact hover --element "Menu" --ref e101` | [ref](reference/interact.md) |
| `mcp2cli browser interact press-key` | Press a key on the keyboard | `mcp2cli browser interact press-key --key "Enter"` | [ref](reference/interact.md) |

### Page
| Command | Description | Example | Ref |
|---|---|---|---|
| `mcp2cli browser page snapshot` | Capture accessibility snapshot of the current page | `mcp2cli browser page snapshot` | [ref](reference/page.md) |
| `mcp2cli browser page screenshot` | Take a screenshot of the current page | `mcp2cli browser page screenshot` | [ref](reference/page.md) |
| `mcp2cli browser page console-logs` | Get console logs from the browser | `mcp2cli browser page console-logs` | [ref](reference/page.md) |
| `mcp2cli browser page wait` | Wait for a specified time in seconds | `mcp2cli browser page wait --time 2` | [ref](reference/page.md) |

## Discover Parameters

Append `--help` to any command for full parameter list:

    mcp2cli browser interact click --help

> **Note**: Use Ref links in the Commands table above to view detailed parameter reference and more examples.

## User Notes

> **MUST READ** [users/skill.md](users/skill.md) for custom workflows and tips.
> **Config**: MCP server settings live in `~/.agents/mcp2cli/servers.yaml` - edit there to take effect.
