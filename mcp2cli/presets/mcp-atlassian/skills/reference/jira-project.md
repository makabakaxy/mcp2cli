# JIRA Project Reference

## mcp2cli jira project list

List all accessible projects.

| Parameter | Required | Description |
|---|---|---|
| `--include-archived` | no | Include archived projects |

## mcp2cli jira project issues

Get all issues for a project.

| Parameter | Required | Description |
|---|---|---|
| `--project-key` | yes | Project key (e.g., "INFRA") |
| `--limit` | no | Max results (1-50) |
| `--start-at` | no | Pagination offset |

## mcp2cli jira project components

| Parameter | Required | Description |
|---|---|---|
| `--project-key` | yes | Project key |

## mcp2cli jira project versions

| Parameter | Required | Description |
|---|---|---|
| `--project-key` | yes | Project key |
