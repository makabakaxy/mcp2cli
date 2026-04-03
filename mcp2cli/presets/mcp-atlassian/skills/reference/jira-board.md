# JIRA Board Reference

## mcp2cli jira board list

List agile boards.

| Parameter | Required | Description |
|---|---|---|
| `--board-name` | no | Fuzzy search by name |
| `--project-key` | no | Filter by project |
| `--board-type` | no | scrum or kanban |
| `--limit` | no | Max results (1-50) |

## mcp2cli jira board issues

Get issues from a board filtered by JQL.

| Parameter | Required | Description |
|---|---|---|
| `--board-id` | yes | Board ID |
| `--jql` | yes | JQL query string |
| `--fields` | no | Fields to return |
| `--limit` | no | Max results |
