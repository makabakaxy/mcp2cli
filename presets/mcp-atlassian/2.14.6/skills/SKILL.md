---
name: mcp-atlassian
description: Manage JIRA issues, sprints, boards, and Confluence pages via CLI. Use when user needs to create/search/update JIRA tickets, manage sprints, or edit Confluence pages.
source_version: "null"
source_cli_hash: "7c573e11"
generated_at: "2026-04-03T10:56:14.617163+00:00"
---

# mcp-atlassian (via mcp2cli)

Manage JIRA and Confluence via CLI.

## Shortcuts

| Alias | Expands to |
|---|---|
| `mcp2cli jira` | `mcp2cli mcp-atlassian jira` |
| `mcp2cli confluence` | `mcp2cli mcp-atlassian confluence` |
| `mcp2cli atlassian` | `mcp2cli mcp-atlassian` |

## Commands

### JIRA
| Command | Description | Example | Ref |
|---|---|---|---|
| `mcp2cli jira issue create` | Create a new issue | `mcp2cli jira issue create --project-key INFRA --summary "Fix bug" --issue-type Task`<br>`mcp2cli jira issue create --project-key DEV --summary "Add login" --issue-type Story --assignee john@example.com` | [ref](reference/jira-issue.md) |
| `mcp2cli jira issue get` | Get issue details | `mcp2cli jira issue get --issue-key INFRA-1234` | [ref](reference/jira-issue.md) |
| `mcp2cli jira issue search` | Search issues via JQL | `mcp2cli jira issue search --jql "project=INFRA AND status=Open"` | [ref](reference/jira-issue.md) |
| `mcp2cli jira issue update` | Update an issue | `mcp2cli jira issue update --issue-key INFRA-1234 --fields '{"summary":"New title"}'` | [ref](reference/jira-issue.md) |
| `mcp2cli jira issue transition` | Change issue status | `mcp2cli jira issue transition --issue-key INFRA-1234 --transition-id 31` | [ref](reference/jira-issue.md) |
| `mcp2cli jira sprint create` | Create a sprint | `mcp2cli jira sprint create --board-id 42 --name "Sprint 1" --start-date 2026-04-01 --end-date 2026-04-14` | [ref](reference/jira-sprint.md) |
| `mcp2cli jira board list` | List agile boards | `mcp2cli jira board list --project-key INFRA` | [ref](reference/jira-board.md) |
| `mcp2cli jira project list` | List all projects | `mcp2cli jira project list` | [ref](reference/jira-project.md) |

### Confluence
| Command | Description | Example | Ref |
|---|---|---|---|
| `mcp2cli confluence page create` | Create a new page | `mcp2cli confluence page create --space-key TEAM --title "Notes" --content "# Notes"` | [ref](reference/confluence-page.md) |
| `mcp2cli confluence page get` | Get page by ID or title | `mcp2cli confluence page get --page-id 123456789`<br>`mcp2cli confluence page get --title "Meeting Notes" --space-key TEAM` | [ref](reference/confluence-page.md) |
| `mcp2cli confluence page update` | Update page content | | [ref](reference/confluence-page.md) |
| `mcp2cli confluence search` | Search content (CQL) | `mcp2cli confluence search --query "project documentation"` | [ref](reference/confluence.md) |
| `mcp2cli confluence page children` | Get child pages | `mcp2cli confluence page children --parent-id 123456789` | [ref](reference/confluence-page.md) |

## Discover Parameters

Append `--help` to any command for full parameter list:

    mcp2cli jira issue create --help

> Use Ref links above to view detailed parameter reference and more examples.

## User Notes

> **MUST READ** [users/skill.md](users/skill.md) for custom workflows and tips.
> **Config**: MCP server settings live in `~/.agents/mcp2cli/servers.yaml` - edit there to take effect.
