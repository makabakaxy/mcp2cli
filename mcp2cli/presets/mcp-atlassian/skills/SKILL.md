---
name: mcp-atlassian
description: Manage JIRA issues, sprints, boards, and Confluence pages via CLI. Use when user needs to create/search/update JIRA tickets, manage sprints, or edit Confluence pages.
source_version: "1.2.3"
source_cli_hash: "a3f8c2d1"
generated_at: "2026-04-01T00:00:00Z"
---

# mcp-atlassian (via mcp2cli)

Manage JIRA and Confluence via CLI.

## Shortcuts

- `mcp2cli jira <cmd>`
- `mcp2cli confluence <cmd>`
- `mcp2cli atlassian <cmd>`

## Commands

### JIRA

| Command | Description | Example | Ref |
|---|---|---|---|
| `mcp2cli jira issue create` | Create a new issue | `mcp2cli jira issue create --project-key INFRA --summary "Fix memory leak" --issue-type Task` | [ref](reference/jira-issue.md) |
| `mcp2cli jira issue get` | Get issue details | `mcp2cli jira issue get --issue-key PROJ-123` | [ref](reference/jira-issue.md) |
| `mcp2cli jira issue search` | Search issues using JQL | `mcp2cli jira issue search --jql "project=INFRA AND status=Open"` | [ref](reference/jira-issue.md) |
| `mcp2cli jira issue update` | Update an existing issue | | [ref](reference/jira-issue.md) |
| `mcp2cli jira issue delete` | Delete an issue | | [ref](reference/jira-issue.md) |
| `mcp2cli jira issue transition` | Transition to new status | | [ref](reference/jira-issue.md) |
| `mcp2cli jira comment add` | Add a comment | `mcp2cli jira comment add --issue-key PROJ-123 --body "Done"` | [ref](reference/jira-issue.md) |
| `mcp2cli jira sprint list` | List sprints for a board | | [ref](reference/jira-sprint.md) |
| `mcp2cli jira sprint create` | Create a sprint | | [ref](reference/jira-sprint.md) |
| `mcp2cli jira sprint issues` | Get sprint issues | | [ref](reference/jira-sprint.md) |
| `mcp2cli jira board list` | List agile boards | | [ref](reference/jira-board.md) |
| `mcp2cli jira project list` | List all projects | | [ref](reference/jira-project.md) |
| `mcp2cli jira project issues` | Get project issues | | [ref](reference/jira-project.md) |
| `mcp2cli jira link create` | Link two issues | | [ref](reference/jira-issue.md) |
| `mcp2cli jira link epic` | Link issue to epic | | [ref](reference/jira-issue.md) |
| `mcp2cli jira worklog add` | Log time on issue | | [ref](reference/jira-issue.md) |
| `mcp2cli jira dev get` | Get linked PRs/commits | | [ref](reference/jira-issue.md) |

### Confluence

| Command | Description | Example | Ref |
|---|---|---|---|
| `mcp2cli confluence page get` | Get page content | `mcp2cli confluence page get --page-id 12345` | [ref](reference/confluence-page.md) |
| `mcp2cli confluence page create` | Create a page | `mcp2cli confluence page create --space-key TEAM --title "Notes" --content "# Notes"` | [ref](reference/confluence-page.md) |
| `mcp2cli confluence page update` | Update page content | | [ref](reference/confluence-page.md) |
| `mcp2cli confluence page delete` | Delete a page | | [ref](reference/confluence-page.md) |
| `mcp2cli confluence page children` | Get child pages | | [ref](reference/confluence-page.md) |
| `mcp2cli confluence search` | Search content | `mcp2cli confluence search --query "project docs"` | [ref](reference/confluence-search.md) |
| `mcp2cli confluence comment add` | Add a comment | | [ref](reference/confluence-page.md) |
| `mcp2cli confluence attachment upload` | Upload file | | [ref](reference/confluence-page.md) |

## Discover Parameters

Append `--help` to any command for full parameter list:

    mcp2cli jira issue create --help

> **Note**: Use Ref links in the Commands table above to view detailed parameter reference and more examples.

## User Notes

> **MUST READ** [users/SKILL.md](users/SKILL.md) for custom workflows and tips.
> See [users/workflows.md](users/workflows.md) for multi-step workflow examples.
> Not overwritten by updates.
