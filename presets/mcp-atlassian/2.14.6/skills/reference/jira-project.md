# JIRA Project Commands

## list — List all accessible projects

```bash
mcp2cli jira project list
mcp2cli jira project list --include-archived
```

Also supports: `--include-archived`

## issues — Get all issues in a project

```bash
mcp2cli jira project issues --project-key INFRA
mcp2cli jira project issues --project-key INFRA --limit 20
```

Also supports: `--limit`, `--start-at`

## components — Get project components

```bash
mcp2cli jira project components --project-key INFRA
```

## versions — Get project fix versions

```bash
mcp2cli jira project versions --project-key INFRA
```

Use `mcp2cli jira project <action> --help` for full parameter details.
