# Skill File Collection Example

This file contains a complete Skill file collection example, showing the standard format for the generated files.

## SKILL.md Example

```markdown
---
name: mcp-atlassian
description: Manage JIRA issues, sprints, boards, and Confluence pages via CLI. Use when user needs to create/search/update JIRA tickets, manage sprints, or edit Confluence pages.
source_version: "1.2.3"
source_cli_hash: "a3f8c2d1"
generated_at: "2026-04-02T10:00:00Z"
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
| `mcp2cli jira issue create` | Create a new issue | `mcp2cli jira issue create --project-key INFRA --summary "Fix memory leak" --issue-type Task`<br>`mcp2cli jira issue create --project-key DEV --summary "Add login" --issue-type Story --assignee john@example.com` | [ref](reference/jira-issue.md) |
| `mcp2cli jira issue get` | Get issue details | `mcp2cli jira issue get --issue-key INFRA-1234` | [ref](reference/jira-issue.md) |
| `mcp2cli jira issue search` | Search issues using JQL | `mcp2cli jira issue search --jql "project=INFRA AND status=Open"` | [ref](reference/jira-issue.md) |
| `mcp2cli jira issue update` | Update an existing issue | | [ref](reference/jira-issue.md) |
| `mcp2cli jira sprint create` | Create a sprint | | [ref](reference/jira-sprint.md) |
| `mcp2cli jira sprint list` | List sprints for a board | | [ref](reference/jira-sprint.md) |
| `mcp2cli jira board list` | List agile boards | | [ref](reference/jira-board.md) |
| `mcp2cli jira project list` | List all projects | | [ref](reference/jira-project.md) |

### Confluence
| Command | Description | Example | Ref |
|---|---|---|---|
| `mcp2cli confluence page get` | Get page content | `mcp2cli confluence page get --page-id 12345` | [ref](reference/confluence-page.md) |
| `mcp2cli confluence page create` | Create a new page | `mcp2cli confluence page create --space-key TEAM --title "Meeting Notes" --content "# Notes"` | [ref](reference/confluence-page.md) |
| `mcp2cli confluence page update` | Update page content | | [ref](reference/confluence-page.md) |
| `mcp2cli confluence search` | Search Confluence content | `mcp2cli confluence search --query "project documentation"` | [ref](reference/confluence.md) |

## Discover Parameters

Append `--help` to any command for full parameter list:

    mcp2cli jira issue create --help

> **Note**: Use Ref links in the Commands table above to view detailed parameter reference and more examples.

## User Notes

> **MUST READ** [users/skill.md](users/skill.md) for custom workflows and tips.
> **Config**: MCP server settings live in `~/.agents/mcp2cli/servers.yaml` - edit there to take effect.
```

## reference/jira-issue.md Example

```markdown
# JIRA Issue Commands

## create — Create a new JIRA issue

```bash
# Create a task
mcp2cli jira issue create --project-key INFRA --summary "Fix memory leak" --issue-type Task

# Create with assignee
mcp2cli jira issue create --project-key DEV --summary "Add login" --issue-type Story --assignee john@example.com

# Create with additional fields
mcp2cli jira issue create --project-key INFRA --summary "Bug fix" --issue-type Bug --components "Frontend,API" --additional-fields '{"priority": {"name": "High"}}'
```

Also supports: `--description`, `--components`, `--additional-fields`

## get — Get issue details by key

```bash
mcp2cli jira issue get --issue-key INFRA-1234
```

Also supports: `--fields`, `--expand`, `--comment-limit`, `--properties`, `--update-history`

## search — Search issues using JQL

```bash
mcp2cli jira issue search --jql "project=INFRA AND status=Open"
mcp2cli jira issue search --jql "assignee=currentUser() AND updated >= -7d" --limit 20
```

Also supports: `--fields`, `--limit`, `--start-at`, `--expand`, `--projects-filter`

## update — Update an existing issue

```bash
mcp2cli jira issue update --issue-key INFRA-1234 --fields '{"summary": "New title", "assignee": "user@example.com"}'
```

Also supports: `--additional-fields`, `--components`, `--attachments`

## delete — Delete an issue

```bash
mcp2cli jira issue delete --issue-key INFRA-1234
```

## transition — Transition issue status

```bash
mcp2cli jira issue transition --issue-key INFRA-1234 --transition-id 31
```

Also supports: `--fields`, `--comment`

## link — Create a link between two issues

```bash
mcp2cli jira issue link --link-type "Blocks" --inward-issue-key INFRA-123 --outward-issue-key INFRA-456
```

Also supports: `--comment`, `--comment-visibility`

Use `mcp2cli jira issue <action> --help` for full parameter details.
```

## users/workflows.md Example

Generated on first `generate skill` run, never overwritten afterwards.

```markdown
# Common Workflow Examples

> Multi-step workflow examples. For single-command usage, refer to the Example column in SKILL.md.
> This file is never overwritten by mcp2cli generate/update — feel free to edit and add your own workflows.

## JIRA Workflow

### Create and assign an issue
```bash
mcp2cli jira issue create --project-key INFRA --summary "Fix memory leak" --issue-type Bug --assignee john@example.com
```

### Search and update issues
```bash
# Find open bugs
mcp2cli jira issue search --jql "project=INFRA AND issuetype=Bug AND status=Open"

# Update priority
mcp2cli jira issue update --issue-key INFRA-1234 --fields '{"priority": {"name": "High"}}'

# Transition to In Progress
mcp2cli jira issue transition --issue-key INFRA-1234 --transition-id 21
```

### Sprint management
```bash
# List boards
mcp2cli jira board list --project-key INFRA

# List active sprints
mcp2cli jira sprint list --board-id 42 --state active

# Add issues to sprint
mcp2cli jira sprint add-issues --sprint-id 100 --issue-keys "INFRA-1,INFRA-2"
```

### Project overview
```bash
# List all projects
mcp2cli jira project list

# Get project issues
mcp2cli jira project issues --project-key INFRA --limit 20
```

## Confluence Workflow

### Create and manage pages
```bash
# Create a page
mcp2cli confluence page create --space-key TEAM --title "Meeting Notes" --content "# Notes\n..."

# Get page content
mcp2cli confluence page get --page-id 123456789

# Update a page
mcp2cli confluence page update --page-id 123456789 --title "Updated Notes" --content "# Updated\n..."
```

### Search and navigate
```bash
# Search pages
mcp2cli confluence search --query "project documentation" --limit 10

# Get child pages
mcp2cli confluence page children --parent-id 123456789

# Compare page versions
mcp2cli confluence page diff --page-id 123456789 --from-version 1 --to-version 3
```

### Attachment management
```bash
# List attachments
mcp2cli confluence attachment list --content-id 123456789

# Upload attachment
mcp2cli confluence attachment upload --content-id 123456789 --file-path ./diagram.png
```
```
