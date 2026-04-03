# mcp-atlassian Workflow Examples

> Multi-step workflow examples. For single-command usage, refer to the Example column in SKILL.md.
> This file is never overwritten by mcp2cli generate/update — feel free to edit and add your own workflows.

## Create a bug and assign it

```bash
mcp2cli jira issue create \
  --project-key INFRA \
  --summary "Login page returns 500" \
  --issue-type Bug \
  --assignee "jane@example.com" \
  --additional-fields '{"priority":{"name":"High"},"labels":["production"]}'
```

## Search and transition issues

```bash
# Find open bugs assigned to me
mcp2cli jira issue search --jql "assignee = currentUser() AND issuetype = Bug AND status = Open"

# Get available transitions
mcp2cli jira issue transitions --issue-key INFRA-456

# Move to "In Progress"
mcp2cli jira issue transition --issue-key INFRA-456 --transition-id 21 --comment "Starting work"
```

## Sprint management workflow

```bash
# List boards
mcp2cli jira board list --project-key INFRA

# List active sprints
mcp2cli jira sprint list --board-id 42 --state active

# Create a new sprint
mcp2cli jira sprint create --board-id 42 --name "Sprint 15" \
  --start-date "2026-04-07T00:00:00Z" --end-date "2026-04-21T00:00:00Z" \
  --goal "Complete auth refactor"

# Add issues to sprint
mcp2cli jira sprint add-issues --sprint-id 150 --issue-keys "INFRA-100,INFRA-101,INFRA-102"
```

## Confluence page workflow

```bash
# Create a page
mcp2cli confluence page create --space-key TEAM --title "Sprint 15 Retrospective" \
  --content "# Sprint 15 Retro\n\n## What went well\n\n## What to improve"

# Search for pages
mcp2cli confluence search --query "Sprint Retrospective" --spaces-filter TEAM

# Get page and update it
mcp2cli confluence page get --page-id 12345
mcp2cli confluence page update --page-id 12345 --title "Sprint 15 Retrospective" \
  --content "# Updated content" --version-comment "Added action items"
```

## Link issues and log work

```bash
# Link issue to epic
mcp2cli jira link epic --issue-key INFRA-456 --epic-key INFRA-100

# Create a "blocks" relationship
mcp2cli jira link create --link-type Blocks --inward-issue-key INFRA-456 --outward-issue-key INFRA-789

# Log 2 hours of work
mcp2cli jira worklog add --issue-key INFRA-456 --time-spent "2h" --comment "Implemented auth flow"
```
