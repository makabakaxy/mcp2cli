<!-- Keywords: mcp2cli mcp2skill mcp-to-skill mcp-to-cli mcpcli mcp to skill mcp to cli mcp 2 cli mcp 2 skill -->

# mcp2cli

> Also known as: **mcp2skill** · **mcp-to-cli** · **mcp-to-skill** · **mcpcli**

Convert MCP servers into CLI commands and compact AI agent skills.

## Why

For example, install [zereight/gitlab-mcp](https://github.com/zereight/gitlab-mcp) — it exposes **122 tools** across 14 categories (merge requests, issues, pipelines, wikis, etc.). Every tool schema gets injected into your AI conversation context on every request. We measured this directly against the Claude API:

| Per-request input tokens | Before (raw MCP) | After (mcp2cli) |
|---|---|---|
| Your message | 20 | 20 |
| Tool definitions (122 tools) | 27,969 | — |
| Skill file (1 file) | — | ~800 |
| **Total** | **27,989** | **~820** |
| **Reduction** | | **~97%** |

After `mcp2cli convert`, your AI agent stops seeing 122 tool definitions. Instead, it reads one small skill file, and calls CLI commands like `mcp2cli gitlab mr create --project-id 123 --title "Fix bug"` to get the job done.

Beyond token savings, some projects maintain both a CLI and an MCP server in parallel (e.g. the GitLab MCP server vs. the `glab` CLI). Keeping two interfaces in sync is a maintenance burden and inevitably leads to feature drift. mcp2cli eliminates the need — one MCP server, one generated CLI, always consistent.

## Quick Start

```bash
pip install mcp-to-cli
```

If you already have an MCP server configured in Claude, Cursor, or Codex:

```bash
mcp2cli list              # See which MCP servers are available
mcp2cli convert gitlab-mcp
```

That's it. Your MCP server is now a CLI, and the compressed skill files are synced to your AI clients.

## How It Works

`mcp2cli convert gitlab-mcp` runs a 3-phase pipeline:

```
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│  1. Extract  │─────>│  2. Generate │─────>│   3. Sync    │
│              │      │              │      │              │
│  Read config │      │ AI-generate  │      │ Copy skills, │
│  from Claude,│      │ CLI + skill  │      │ disable MCP  │
│  Cursor,Codex│      │              │      │              │
└──────┬───────┘      └──────┬───────┘      └──────┬───────┘
       v                     v                     v
 mcp_servers.json    cli.yaml + SKILL.md    ~/.claude/skills/
```

1. **Extract** — Reads your MCP server config from Claude (`~/.claude.json`) / Cursor (`~/.cursor/mcp.json`) / Codex (`~/.codex/config.toml`)
2. **Generate** — Connects to the MCP server, discovers all tools, and uses AI to generate a CLI command tree (`cli.yaml`) and a compressed skill file (`SKILL.md`)
3. **Sync** — Copies skill files to your AI clients and disables the raw MCP server

Each skill directory contains a `users/` subdirectory where you can add your own notes and workflows. This directory is never overwritten by `mcp2cli`.

At runtime, the generated CLI resolves commands to MCP tool calls through a lightweight daemon:

```
mcp2cli gitlab mr list --project-id 123
        │
        │  resolve via cli.yaml
        v
  tool: gitlab_list_merge_requests(project_id=123)
        │
        v
  ┌─────────┐     MCP protocol     ┌────────────┐
  │ mcp2cli │ ──────────────────>  │ MCP Server │
  │ daemon  │ <──────────────────  │ (gitlab)   │
  └─────────┘     JSON result      └────────────┘
```

The daemon starts automatically on first use and stops when idle.

## Presets — Pre-built Skills, Download in Seconds

Don't want to wait for AI generation (~2-3 min)? Use **presets** — pre-built CLI mappings + skill files shared by the community. Downloads in ~10 seconds.

```bash
mcp2cli preset list                       # Browse available presets
mcp2cli preset pull mcp-atlassian         # Download + sync to AI clients
mcp2cli preset pull mcp-atlassian@1.2.3   # Pin a specific version
mcp2cli preset push gitlab-mcp            # Share your result with others
```

During `convert` and `install`, presets are checked automatically — if one exists, you can skip AI generation entirely:

```
mcp2cli convert/install
        |
   preset-check ─── found? ─── yes ──→ download preset (~10s)
        |                                      |
        no                                     |
        |                                      |
   scan → generate cli → generate skill        |
        (~2-3 min)                             |
        |                                      |
        └──────────────→ skill sync ←──────────┘
```

Custom registry for private/team use:

```bash
mcp2cli preset registry set https://github.com/your-org/mcp2cli-presets
```

## Install — Add New MCP Servers

`convert` works with servers already configured in your AI clients. For MCP servers you haven't set up yet, use `install` — it searches the internet for installation info, prompts for env vars, then runs the full conversion pipeline:

```bash
mcp2cli install mcp-atlassian
```

## Usage Examples

```bash
# List all configured local MCP servers
mcp2cli list

# Convert a server (auto-detects config from all clients)
mcp2cli convert gitlab-mcp

# Use the generated CLI
mcp2cli gitlab mr list --project-id 123
mcp2cli gitlab issue create --title "Fix login bug" --project-id 123

# Update when the MCP server adds new tools
mcp2cli update gitlab-mcp

# Remove everything (CLI, skills, config)
mcp2cli remove gitlab-mcp
```

## Commands

| Command | Description |
|---------|-------------|
| `convert <server>` | Convert an MCP server to skill-based usage |
| `install <server>` | Install a new MCP server and generate skills |
| `update <server>` | Update tools and regenerate CLI + skills |
| `remove <server>` | Remove a server and all generated artifacts |
| `list` | List all configured MCP servers |
| `scan <server>` | Discover all tools from an MCP server |
| `tools <server>` | List tools or show tool details |
| `call <server> <tool>` | Call an MCP tool directly |
| `generate cli <server>` | (Re)generate the CLI command tree |
| `generate skill <server>` | (Re)generate skill files |
| `skill sync <server>` | Sync skill files to AI clients |
| `skill unsync <server>` | Remove synced skills and re-enable MCP server |
| `preset list [server]` | Browse available presets (local + remote) |
| `preset pull <name[@ver]>` | Download a preset, skip AI generation |
| `preset export <server>` | Export a preset bundle to a local directory |
| `preset push <server>` | Push local preset to community registry |
| `validate <server>` | Validate CLI mapping and skill files |

## License

MIT
