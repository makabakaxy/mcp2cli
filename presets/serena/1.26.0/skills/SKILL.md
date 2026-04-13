---
name: serena
description: Code editing and project management via Serena MCP. Use when user needs to read/write files, find/rename symbols, run shell commands, or manage project memory.
source_version: "1.26.0"
source_cli_hash: "bc6b949c"
generated_at: "2026-04-06T08:49:26.537103+00:00"
---

# serena (via mcp2cli)

Code-aware editing, symbol navigation, memory, and project management.

## Shortcuts

No shortcuts configured. Use `mcp2cli serena <group> <cmd>`.

## Commands

### File
| Command | Description | Example | Ref |
|---|---|---|---|
| `mcp2cli serena file create` | Create or overwrite a text file | `mcp2cli serena file create --relative-path src/new.py --content 'print("hi")'` | [ref](reference/file.md) |
| `mcp2cli serena file get` | Read a file or chunk | `mcp2cli serena file get --relative-path src/main.py`<br>`mcp2cli serena file get --relative-path src/main.py --start-line 10 --end-line 50` | [ref](reference/file.md) |
| `mcp2cli serena file search` | Search regex pattern across codebase | `mcp2cli serena file search --substring-pattern 'def my_func'` | [ref](reference/file.md) |
| `mcp2cli serena file list` | List files in a directory | `mcp2cli serena file list --relative-path . --recursive false` | [ref](reference/file.md) |
| `mcp2cli serena file find` | Find files by name mask | `mcp2cli serena file find --file-mask '*.py' --relative-path src` | [ref](reference/file.md) |
| `mcp2cli serena file replace` | Replace pattern occurrences in a file | | [ref](reference/file.md) |

### Symbol
| Command | Description | Example | Ref |
|---|---|---|---|
| `mcp2cli serena symbol find` | Find symbols by name path pattern | `mcp2cli serena symbol find --name-path-pattern MyClass/my_method` | [ref](reference/symbol.md) |
| `mcp2cli serena symbol overview` | Get high-level symbol overview of a file | `mcp2cli serena symbol overview --relative-path src/main.py` | [ref](reference/symbol.md) |
| `mcp2cli serena symbol replace` | Replace the body of a symbol | | [ref](reference/symbol.md) |
| `mcp2cli serena symbol insert-after` | Insert content after a symbol | | [ref](reference/symbol.md) |
| `mcp2cli serena symbol insert-before` | Insert content before a symbol | | [ref](reference/symbol.md) |
| `mcp2cli serena symbol rename` | Rename a symbol codebase-wide | | [ref](reference/symbol.md) |
| `mcp2cli serena symbol refs` | Find symbols referencing a symbol | | [ref](reference/symbol.md) |
| `mcp2cli serena symbol delete` | Delete a symbol if unreferenced | | [ref](reference/symbol.md) |

### Memory
| Command | Description | Example | Ref |
|---|---|---|---|
| `mcp2cli serena memory write` | Write project info to named memory | `mcp2cli serena memory write --memory-name 'auth/logic' --content 'Auth uses JWT'` | [ref](reference/memory.md) |
| `mcp2cli serena memory get` | Read a memory | `mcp2cli serena memory get --memory-name 'auth/logic'` | [ref](reference/memory.md) |
| `mcp2cli serena memory list` | List available memories | `mcp2cli serena memory list` | [ref](reference/memory.md) |
| `mcp2cli serena memory update` | Edit memory via pattern replacement | | [ref](reference/memory.md) |
| `mcp2cli serena memory rename` | Rename or move a memory | | [ref](reference/memory.md) |
| `mcp2cli serena memory delete` | Delete a memory | | [ref](reference/memory.md) |

### Shell / Project / Session
| Command | Description | Example | Ref |
|---|---|---|---|
| `mcp2cli serena shell` | Execute a shell command | `mcp2cli serena shell --command 'npm test'` | [ref](reference/shell.md) |
| `mcp2cli serena project activate` | Activate a project by name or path | `mcp2cli serena project activate --project my-project` | [ref](reference/project.md) |
| `mcp2cli serena project onboarding` | Perform project onboarding | | [ref](reference/project.md) |
| `mcp2cli serena session config` | Get current agent configuration | | [ref](reference/session.md) |
| `mcp2cli serena session modes` | Switch active agent modes | `mcp2cli serena session modes --modes '["editing","interactive"]'` | [ref](reference/session.md) |
| `mcp2cli serena session instructions` | Get Serena Instructions Manual | | [ref](reference/session.md) |

## Discover Parameters

Append `--help` to any command for full parameter list:

    mcp2cli serena file get --help

> **Note**: Use Ref links in the Commands table above to view detailed parameter reference and more examples.

## User Notes

> **MUST READ** [users/skill.md](users/skill.md) for custom workflows and tips.
> **Config**: MCP server settings live in `~/.agents/mcp2cli/servers.yaml` - edit there to take effect.
