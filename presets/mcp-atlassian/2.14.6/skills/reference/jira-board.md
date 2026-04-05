# JIRA Board Commands

## list — List agile boards

```bash
mcp2cli jira board list
mcp2cli jira board list --project-key INFRA
mcp2cli jira board list --board-type scrum --project-key DEV
```

Also supports: `--board-name`, `--project-key`, `--board-type`, `--start-at`, `--limit`

## issues — Get issues from a board

```bash
mcp2cli jira board issues --board-id 42 --jql "status=Open"
mcp2cli jira board issues --board-id 42 --jql "issuetype=Bug AND priority=High" --limit 20
```

Also supports: `--fields`, `--start-at`, `--limit`, `--expand`

Use `mcp2cli jira board <action> --help` for full parameter details.
