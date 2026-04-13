---
name: chrome-devtools-mcp
description: Automate browser interactions via Chrome DevTools — control pages, interact with DOM elements, capture screenshots/snapshots, monitor console/network, evaluate JS, and run performance/Lighthouse audits. Use when user needs to navigate websites, fill forms, take screenshots, test web apps, or analyze page performance.
source_version: "0.21.0"
source_cli_hash: "41e39489"
generated_at: "2026-04-06T08:25:06.855684+00:00"
---

# chrome-devtools-mcp (via mcp2cli)

Automate browser interactions via Chrome DevTools.

## Shortcuts

- `mcp2cli chrome-devtools <cmd>` (alias for `mcp2cli chrome-devtools-mcp <cmd>`)

## Commands

### Page
| Command | Description | Example | Ref |
|---|---|---|---|
| `mcp2cli chrome-devtools page create` | Open new tab and load URL | `mcp2cli chrome-devtools page create --url https://example.com` | [ref](reference/page.md) |
| `mcp2cli chrome-devtools page list` | List all open pages | `mcp2cli chrome-devtools page list` | [ref](reference/page.md) |
| `mcp2cli chrome-devtools page navigate` | Navigate to URL or go back/forward/reload | `mcp2cli chrome-devtools page navigate --type url --url https://example.com` | [ref](reference/page.md) |
| `mcp2cli chrome-devtools page select` | Select page as active context | `mcp2cli chrome-devtools page select --page-id 1` | [ref](reference/page.md) |
| `mcp2cli chrome-devtools page close` | Close a page by ID | `mcp2cli chrome-devtools page close --page-id 2` | [ref](reference/page.md) |
| `mcp2cli chrome-devtools page wait` | Wait for text to appear | `mcp2cli chrome-devtools page wait --text '["Loaded"]'` | [ref](reference/page.md) |
| `mcp2cli chrome-devtools page emulate` | Emulate network/CPU/viewport | `mcp2cli chrome-devtools page emulate --network-conditions "Slow 3G"` | [ref](reference/page.md) |
| `mcp2cli chrome-devtools page resize` | Resize page window | `mcp2cli chrome-devtools page resize --width 1280 --height 720` | [ref](reference/page.md) |

### Element
| Command | Description | Example | Ref |
|---|---|---|---|
| `mcp2cli chrome-devtools element click` | Click on an element | `mcp2cli chrome-devtools element click --uid e12` | [ref](reference/element.md) |
| `mcp2cli chrome-devtools element fill` | Type text into input or select option | `mcp2cli chrome-devtools element fill --uid e5 --value "hello"` | [ref](reference/element.md) |
| `mcp2cli chrome-devtools element fill-form` | Fill multiple form elements at once | | [ref](reference/element.md) |
| `mcp2cli chrome-devtools element type` | Type text into focused input | `mcp2cli chrome-devtools element type --text "search query"` | [ref](reference/element.md) |
| `mcp2cli chrome-devtools element press-key` | Press key or key combination | `mcp2cli chrome-devtools element press-key --key "Enter"` | [ref](reference/element.md) |
| `mcp2cli chrome-devtools element hover` | Hover over an element | `mcp2cli chrome-devtools element hover --uid e8` | [ref](reference/element.md) |
| `mcp2cli chrome-devtools element drag` | Drag element onto another | | [ref](reference/element.md) |
| `mcp2cli chrome-devtools element upload` | Upload file through file input | | [ref](reference/element.md) |

### Capture
| Command | Description | Example | Ref |
|---|---|---|---|
| `mcp2cli chrome-devtools capture snapshot` | Take accessibility tree snapshot | `mcp2cli chrome-devtools capture snapshot` | [ref](reference/capture.md) |
| `mcp2cli chrome-devtools capture screenshot` | Take screenshot of page or element | `mcp2cli chrome-devtools capture screenshot --format png` | [ref](reference/capture.md) |

### Console & Network
| Command | Description | Example | Ref |
|---|---|---|---|
| `mcp2cli chrome-devtools console list` | List console messages | `mcp2cli chrome-devtools console list` | [ref](reference/console.md) |
| `mcp2cli chrome-devtools console get` | Get a console message by ID | `mcp2cli chrome-devtools console get --msgid 1` | [ref](reference/console.md) |
| `mcp2cli chrome-devtools network list` | List network requests | `mcp2cli chrome-devtools network list` | [ref](reference/network.md) |
| `mcp2cli chrome-devtools network get` | Get network request details | `mcp2cli chrome-devtools network get --reqid 5` | [ref](reference/network.md) |

### Script & Dialog
| Command | Description | Example | Ref |
|---|---|---|---|
| `mcp2cli chrome-devtools script evaluate` | Evaluate JavaScript in page | `mcp2cli chrome-devtools script evaluate --function '() => document.title'` | [ref](reference/script.md) |
| `mcp2cli chrome-devtools dialog handle` | Accept or dismiss browser dialog | `mcp2cli chrome-devtools dialog handle --action accept` | [ref](reference/dialog.md) |

### Performance
| Command | Description | Example | Ref |
|---|---|---|---|
| `mcp2cli chrome-devtools performance trace-start` | Start performance trace | `mcp2cli chrome-devtools performance trace-start` | [ref](reference/performance.md) |
| `mcp2cli chrome-devtools performance trace-stop` | Stop performance trace | `mcp2cli chrome-devtools performance trace-stop` | [ref](reference/performance.md) |
| `mcp2cli chrome-devtools performance analyze` | Analyze a performance insight | | [ref](reference/performance.md) |
| `mcp2cli chrome-devtools performance memory-snapshot` | Capture heap snapshot | `mcp2cli chrome-devtools performance memory-snapshot --file-path heap.heapsnapshot` | [ref](reference/performance.md) |
| `mcp2cli chrome-devtools performance lighthouse` | Run Lighthouse audit | `mcp2cli chrome-devtools performance lighthouse` | [ref](reference/performance.md) |

## Discover Parameters

Append `--help` to any command for full parameter list:

    mcp2cli chrome-devtools page navigate --help

> Use Ref links above to view detailed parameter reference and more examples.

## User Notes

> **MUST READ** [users/skill.md](users/skill.md) for custom workflows and tips.
> **Config**: MCP server settings live in `~/.agents/mcp2cli/servers.yaml` - edit there to take effect.
