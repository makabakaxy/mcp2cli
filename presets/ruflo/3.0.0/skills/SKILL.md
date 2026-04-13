---
name: ruflo
description: Manage multi-agent swarms, memory, tasks, hooks, workflows, and browser automation via CLI. Use when spawning agents, storing/searching memory, orchestrating workflows, coordinating hive-minds, or automating browser interactions.
source_version: "3.0.0"
source_cli_hash: "d3fd1093"
generated_at: "2026-04-06T08:38:53.305460+00:00"
---

# ruflo (via mcp2cli)

Multi-agent orchestration, vector memory, task management, and browser automation.

## Shortcuts

No shortcuts configured. Use full form: `mcp2cli ruflo <group> <cmd>`

## Commands

### Agent
| Command | Description | Example | Ref |
|---|---|---|---|
| `mcp2cli ruflo agent spawn` | Spawn a new agent | `mcp2cli ruflo agent spawn --agent-type worker --model sonnet` | [ref](reference/agent.md) |
| `mcp2cli ruflo agent list` | List all agents | `mcp2cli ruflo agent list` | [ref](reference/agent.md) |
| `mcp2cli ruflo agent status` | Get agent status | `mcp2cli ruflo agent status --agent-id agent-1` | [ref](reference/agent.md) |
| `mcp2cli ruflo agent update` | Update agent config | | [ref](reference/agent.md) |
| `mcp2cli ruflo agent terminate` | Terminate an agent | `mcp2cli ruflo agent terminate --agent-id agent-1` | [ref](reference/agent.md) |
| `mcp2cli ruflo agent health` | Check agent health | | [ref](reference/agent.md) |

### Memory
| Command | Description | Example | Ref |
|---|---|---|---|
| `mcp2cli ruflo memory store` | Store value with vector embedding | `mcp2cli ruflo memory store --key mykey --value "data"` | [ref](reference/memory.md) |
| `mcp2cli ruflo memory get` | Retrieve value by key | `mcp2cli ruflo memory get --key mykey` | [ref](reference/memory.md) |
| `mcp2cli ruflo memory search` | Semantic vector search | `mcp2cli ruflo memory search --query "auth patterns"` | [ref](reference/memory.md) |
| `mcp2cli ruflo memory list` | List memory entries | | [ref](reference/memory.md) |
| `mcp2cli ruflo memory delete` | Delete memory entry | `mcp2cli ruflo memory delete --key mykey` | [ref](reference/memory.md) |
| `mcp2cli ruflo memory stats` | Get memory statistics | | [ref](reference/memory.md) |

### Task
| Command | Description | Example | Ref |
|---|---|---|---|
| `mcp2cli ruflo task create` | Create a new task | `mcp2cli ruflo task create --type feature --description "Add login"` | [ref](reference/task.md) |
| `mcp2cli ruflo task list` | List all tasks | `mcp2cli ruflo task list --status pending` | [ref](reference/task.md) |
| `mcp2cli ruflo task status` | Get task status | `mcp2cli ruflo task status --task-id t1` | [ref](reference/task.md) |
| `mcp2cli ruflo task update` | Update task progress | | [ref](reference/task.md) |
| `mcp2cli ruflo task complete` | Mark task complete | `mcp2cli ruflo task complete --task-id t1` | [ref](reference/task.md) |
| `mcp2cli ruflo task assign` | Assign task to agents | | [ref](reference/task.md) |
| `mcp2cli ruflo task cancel` | Cancel a task | | [ref](reference/task.md) |

### Hooks
| Command | Description | Example | Ref |
|---|---|---|---|
| `mcp2cli ruflo hooks pre-task` | Record task start, get agent suggestions | `mcp2cli ruflo hooks pre-task --task-id t1 --description "Fix bug"` | [ref](reference/hooks.md) |
| `mcp2cli ruflo hooks post-task` | Record task completion | `mcp2cli ruflo hooks post-task --task-id t1 --success true` | [ref](reference/hooks.md) |
| `mcp2cli ruflo hooks route` | Route task to optimal agent | `mcp2cli ruflo hooks route --task "implement OAuth"` | [ref](reference/hooks.md) |
| `mcp2cli ruflo hooks pre-edit` | Get context before editing file | `mcp2cli ruflo hooks pre-edit --file-path src/auth.ts` | [ref](reference/hooks.md) |
| `mcp2cli ruflo hooks init` | Initialize hooks in project | `mcp2cli ruflo hooks init --template standard` | [ref](reference/hooks.md) |
| `mcp2cli ruflo hooks metrics` | View learning metrics | | [ref](reference/hooks.md) |

### Hive-Mind
| Command | Description | Example | Ref |
|---|---|---|---|
| `mcp2cli ruflo hive-mind spawn` | Spawn workers and join hive | `mcp2cli ruflo hive-mind spawn --count 3 --role worker` | [ref](reference/hive-mind.md) |
| `mcp2cli ruflo hive-mind init` | Initialize hive-mind collective | `mcp2cli ruflo hive-mind init --topology mesh` | [ref](reference/hive-mind.md) |
| `mcp2cli ruflo hive-mind status` | Get hive-mind status | | [ref](reference/hive-mind.md) |
| `mcp2cli ruflo hive-mind consensus` | Propose or vote on consensus | `mcp2cli ruflo hive-mind consensus --action propose --type config` | [ref](reference/hive-mind.md) |
| `mcp2cli ruflo hive-mind broadcast` | Broadcast to all workers | `mcp2cli ruflo hive-mind broadcast --message "Start phase 2"` | [ref](reference/hive-mind.md) |

### Workflow
| Command | Description | Example | Ref |
|---|---|---|---|
| `mcp2cli ruflo workflow run` | Run workflow from template | `mcp2cli ruflo workflow run --template ci-pipeline` | [ref](reference/workflow.md) |
| `mcp2cli ruflo workflow create` | Create a new workflow | `mcp2cli ruflo workflow create --name my-flow` | [ref](reference/workflow.md) |
| `mcp2cli ruflo workflow list` | List all workflows | | [ref](reference/workflow.md) |
| `mcp2cli ruflo workflow status` | Get workflow status | `mcp2cli ruflo workflow status --workflow-id wf1` | [ref](reference/workflow.md) |
| `mcp2cli ruflo workflow execute` | Execute a workflow | `mcp2cli ruflo workflow execute --workflow-id wf1` | [ref](reference/workflow.md) |

### Claims
| Command | Description | Example | Ref |
|---|---|---|---|
| `mcp2cli ruflo claims claim` | Claim an issue for work | `mcp2cli ruflo claims claim --issue-id 123 --claimant "agent:coder-1:coder"` | [ref](reference/claims.md) |
| `mcp2cli ruflo claims list` | List all claims | | [ref](reference/claims.md) |
| `mcp2cli ruflo claims release` | Release a claim | `mcp2cli ruflo claims release --issue-id 123 --claimant "agent:coder-1:coder"` | [ref](reference/claims.md) |
| `mcp2cli ruflo claims handoff` | Handoff issue to another agent | | [ref](reference/claims.md) |
| `mcp2cli ruflo claims load` | Get agent load info | | [ref](reference/claims.md) |

### Browser
| Command | Description | Example | Ref |
|---|---|---|---|
| `mcp2cli ruflo browser open` | Navigate to URL | `mcp2cli ruflo browser open --url https://example.com` | [ref](reference/browser.md) |
| `mcp2cli ruflo browser snapshot` | Get accessibility tree | | [ref](reference/browser.md) |
| `mcp2cli ruflo browser screenshot` | Capture screenshot | | [ref](reference/browser.md) |
| `mcp2cli ruflo browser click` | Click an element | `mcp2cli ruflo browser click --ref elem-1` | [ref](reference/browser.md) |
| `mcp2cli ruflo browser fill` | Fill an input field | `mcp2cli ruflo browser fill --ref input-1 --value "text"` | [ref](reference/browser.md) |

### Swarm
| Command | Description | Example | Ref |
|---|---|---|---|
| `mcp2cli ruflo swarm init` | Initialize a swarm | `mcp2cli ruflo swarm init --topology hierarchical` | [ref](reference/swarm.md) |
| `mcp2cli ruflo swarm status` | Get swarm status | | [ref](reference/swarm.md) |
| `mcp2cli ruflo swarm health` | Check swarm health | | [ref](reference/swarm.md) |
| `mcp2cli ruflo swarm shutdown` | Shutdown a swarm | | [ref](reference/swarm.md) |

## Discover Parameters

Append `--help` to any command for full parameter list:

    mcp2cli ruflo agent spawn --help

> **Note**: Use Ref links above to view detailed parameter reference and more examples.

## User Notes

> **MUST READ** [users/skill.md](users/skill.md) for custom workflows and tips.
> **Config**: MCP server settings live in `~/.agents/mcp2cli/servers.yaml` - edit there to take effect.
