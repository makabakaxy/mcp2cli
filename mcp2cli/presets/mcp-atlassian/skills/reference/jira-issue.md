# JIRA Issue Reference

## mcp2cli jira issue create

Create a new JIRA issue.

| Parameter | Required | Description |
|---|---|---|
| `--project-key` | yes | Project key (e.g., "INFRA") |
| `--summary` | yes | Issue summary/title |
| `--issue-type` | yes | Type: Task, Bug, Story, Epic, Subtask |
| `--description` | no | Markdown description |
| `--assignee` | no | Email, display name, or account ID |
| `--components` | no | Comma-separated component names |
| `--additional-fields` | no | JSON string for custom fields |

**Examples:**
```bash
mcp2cli jira issue create --project-key INFRA --summary "Fix memory leak" --issue-type Bug
mcp2cli jira issue create --project-key INFRA --summary "Add login" --issue-type Story --assignee "user@example.com"
mcp2cli jira issue create --project-key INFRA --summary "Epic" --issue-type Epic --additional-fields '{"priority":{"name":"High"}}'
```

## mcp2cli jira issue get

Get issue details by key.

| Parameter | Required | Description |
|---|---|---|
| `--issue-key` | yes | Issue key (e.g., "PROJ-123") |
| `--fields` | no | Comma-separated fields or `*all` |
| `--expand` | no | renderedFields, transitions, changelog |
| `--comment-limit` | no | Max comments to include (default 10) |

## mcp2cli jira issue search

Search issues using JQL.

| Parameter | Required | Description |
|---|---|---|
| `--jql` | yes | JQL query string |
| `--fields` | no | Fields to return |
| `--limit` | no | Max results (1-50, default 10) |
| `--start-at` | no | Pagination offset |

**JQL examples:**
```
"project = INFRA AND status = Open"
"assignee = currentUser() AND updated >= -7d"
"issuetype = Epic AND project = INFRA"
"labels = frontend AND priority = High"
```

## mcp2cli jira issue update

| Parameter | Required | Description |
|---|---|---|
| `--issue-key` | yes | Issue key |
| `--fields` | yes | JSON string of fields to update |
| `--additional-fields` | no | JSON for custom/epic fields |
| `--components` | no | Comma-separated component names |

## mcp2cli jira issue delete

| Parameter | Required | Description |
|---|---|---|
| `--issue-key` | yes | Issue key |

## mcp2cli jira issue transition

| Parameter | Required | Description |
|---|---|---|
| `--issue-key` | yes | Issue key |
| `--transition-id` | yes | Transition ID (use `transitions` to get IDs) |
| `--comment` | no | Comment for the transition |

## mcp2cli jira comment add

| Parameter | Required | Description |
|---|---|---|
| `--issue-key` | yes | Issue key |
| `--body` | yes | Comment text in Markdown |

## mcp2cli jira link create

| Parameter | Required | Description |
|---|---|---|
| `--link-type` | yes | e.g., "Blocks", "Relates to" |
| `--inward-issue-key` | yes | Source issue key |
| `--outward-issue-key` | yes | Target issue key |

## mcp2cli jira link epic

| Parameter | Required | Description |
|---|---|---|
| `--issue-key` | yes | Issue to link |
| `--epic-key` | yes | Epic to link to |

## mcp2cli jira worklog add

| Parameter | Required | Description |
|---|---|---|
| `--issue-key` | yes | Issue key |
| `--time-spent` | yes | e.g., "1h 30m", "1d", "30m" |
| `--comment` | no | Worklog comment |

## mcp2cli jira dev get

| Parameter | Required | Description |
|---|---|---|
| `--issue-key` | yes | Issue key |

Returns linked pull requests, branches, and commits.
