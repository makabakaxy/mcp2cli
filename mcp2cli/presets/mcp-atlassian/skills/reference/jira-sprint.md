# JIRA Sprint Reference

## mcp2cli jira sprint list

List sprints for a board.

| Parameter | Required | Description |
|---|---|---|
| `--board-id` | yes | Board ID |
| `--state` | no | active, future, or closed |
| `--limit` | no | Max results (1-50) |

## mcp2cli jira sprint create

| Parameter | Required | Description |
|---|---|---|
| `--board-id` | yes | Board ID |
| `--name` | yes | Sprint name |
| `--start-date` | yes | ISO 8601 format |
| `--end-date` | yes | ISO 8601 format |
| `--goal` | no | Sprint goal |

## mcp2cli jira sprint update

| Parameter | Required | Description |
|---|---|---|
| `--sprint-id` | yes | Sprint ID |
| `--name` | no | New name |
| `--state` | no | future, active, closed |
| `--goal` | no | New goal |

## mcp2cli jira sprint issues

| Parameter | Required | Description |
|---|---|---|
| `--sprint-id` | yes | Sprint ID |
| `--fields` | no | Fields to return |
| `--limit` | no | Max results |

## mcp2cli jira sprint add-issues

| Parameter | Required | Description |
|---|---|---|
| `--sprint-id` | yes | Sprint ID |
| `--issue-keys` | yes | Comma-separated issue keys |
