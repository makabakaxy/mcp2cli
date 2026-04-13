---
name: filesystem-mcp
description: Read, write, edit, move, and search files and directories via CLI. Use when user needs to access file contents, manage directory structures, or search for files by pattern.
source_version: "0.2.0"
source_cli_hash: "6687ec79"
generated_at: "2026-04-06T09:00:48.172488+00:00"
---

# filesystem-mcp (via mcp2cli)

Read, write, edit, move, and search files and directories via CLI.

## Shortcuts

- `mcp2cli filesystem <cmd>` (alias for `mcp2cli filesystem-mcp`)

## Commands

### File
| Command | Description | Example | Ref |
|---|---|---|---|
| `mcp2cli filesystem file get` | Read text file contents | `mcp2cli filesystem file get --path /path/to/file.txt`<br>`mcp2cli filesystem file get --path /path/to/file.txt --head 50` | [ref](reference/file.md) |
| `mcp2cli filesystem file write` | Create or overwrite a file | `mcp2cli filesystem file write --path /path/to/file.txt --content 'Hello World'` | [ref](reference/file.md) |
| `mcp2cli filesystem file edit` | Make line-based edits to a file | `mcp2cli filesystem file edit --path /path/to/file.txt --edits '[{"oldText":"foo","newText":"bar"}]'` | [ref](reference/file.md) |
| `mcp2cli filesystem file search` | Search files by glob pattern | `mcp2cli filesystem file search --path /project --pattern '**/*.py'` | [ref](reference/file.md) |
| `mcp2cli filesystem file get-multiple` | Read multiple files at once | `mcp2cli filesystem file get-multiple --paths '["file1.txt","file2.txt"]'` | [ref](reference/file.md) |
| `mcp2cli filesystem file get-media` | Read image/audio as base64 | `mcp2cli filesystem file get-media --path /path/to/image.png` | [ref](reference/file.md) |
| `mcp2cli filesystem file move` | Move or rename a file | `mcp2cli filesystem file move --source /old/path --destination /new/path` | [ref](reference/file.md) |
| `mcp2cli filesystem file info` | Get file metadata | `mcp2cli filesystem file info --path /path/to/file.txt` | [ref](reference/file.md) |

### Directory
| Command | Description | Example | Ref |
|---|---|---|---|
| `mcp2cli filesystem directory create` | Create a directory | `mcp2cli filesystem directory create --path /new/dir` | [ref](reference/directory.md) |
| `mcp2cli filesystem directory list` | List directory contents | `mcp2cli filesystem directory list --path /project` | [ref](reference/directory.md) |
| `mcp2cli filesystem directory tree` | Get recursive directory tree | `mcp2cli filesystem directory tree --path /project` | [ref](reference/directory.md) |
| `mcp2cli filesystem directory list-sizes` | List with size information | `mcp2cli filesystem directory list-sizes --path /project` | [ref](reference/directory.md) |
| `mcp2cli filesystem directory list-allowed` | List accessible directories | `mcp2cli filesystem directory list-allowed` | [ref](reference/directory.md) |

## Discover Parameters

Append `--help` to any command for full parameter list:

    mcp2cli filesystem file get --help

> **Note**: Use Ref links in the Commands table above to view detailed parameter reference and more examples.

## User Notes

> **MUST READ** [users/skill.md](users/skill.md) for custom workflows and tips.
> **Config**: MCP server settings live in `~/.agents/mcp2cli/servers.yaml` - edit there to take effect.
