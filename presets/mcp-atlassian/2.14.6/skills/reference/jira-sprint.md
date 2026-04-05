# JIRA Sprint Commands

## create — Create a new sprint

```bash
mcp2cli jira sprint create --board-id 42 --name "Sprint 1" --start-date 2026-04-01 --end-date 2026-04-14
mcp2cli jira sprint create --board-id 42 --name "Sprint 2" --start-date 2026-04-15 --end-date 2026-04-28 --goal "Finish auth module"
```

Also supports: `--goal`

## update — Update sprint details

```bash
mcp2cli jira sprint update --sprint-id 100 --name "Sprint 1 (Updated)"
mcp2cli jira sprint update --sprint-id 100 --state closed
```

Also supports: `--name`, `--state`, `--start-date`, `--end-date`, `--goal`

## list — List sprints for a board

```bash
mcp2cli jira sprint list --board-id 42
mcp2cli jira sprint list --board-id 42 --state active
```

Also supports: `--state`, `--start-at`, `--limit`

## issues — Get issues in a sprint

```bash
mcp2cli jira sprint issues --sprint-id 100
mcp2cli jira sprint issues --sprint-id 100 --limit 20
```

Also supports: `--fields`, `--limit`, `--start-at`

## add-issues — Add issues to a sprint

```bash
mcp2cli jira sprint add-issues --sprint-id 100 --issue-keys "INFRA-1,INFRA-2,INFRA-3"
```

Use `mcp2cli jira sprint <action> --help` for full parameter details.
