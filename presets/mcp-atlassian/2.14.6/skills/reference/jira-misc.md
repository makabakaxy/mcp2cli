# JIRA Misc Commands

## version create — Create a fix version

```bash
mcp2cli jira version create --project-key INFRA --name "v1.2.0"
mcp2cli jira version create --project-key INFRA --name "v1.3.0" --release-date 2026-06-01 --description "Summer release"
```

Also supports: `--start-date`, `--release-date`, `--description`

## version batch-create — Batch create versions

```bash
mcp2cli jira version batch-create --project-key INFRA --versions '[{"name":"v1.0"},{"name":"v2.0","releaseDate":"2026-12-01"}]'
```

## field search — Search fields by keyword

```bash
mcp2cli jira field search --keyword "priority"
mcp2cli jira field search --keyword "custom" --limit 20
```

Also supports: `--keyword`, `--limit`, `--refresh`

## field options — Get allowed options for a custom field

```bash
mcp2cli jira field options --field-id customfield_10001
mcp2cli jira field options --field-id customfield_10001 --values-only
```

Also supports: `--context-id`, `--project-key`, `--issue-type`, `--contains`, `--return-limit`, `--values-only`

## link-type list — List issue link types

```bash
mcp2cli jira link-type list
mcp2cli jira link-type list --name-filter "Blocks"
```

Also supports: `--name-filter`

## user get — Get user profile

```bash
mcp2cli jira user get --user-identifier user@example.com
mcp2cli jira user get --user-identifier "John Doe"
```

## service-desk get — Get service desk for a project

```bash
mcp2cli jira service-desk get --project-key SUP
```

## service-desk queues — Get service desk queues

```bash
mcp2cli jira service-desk queues --service-desk-id 4
```

Also supports: `--start-at`, `--limit`

## service-desk queue-issues — Get issues from a queue

```bash
mcp2cli jira service-desk queue-issues --service-desk-id 4 --queue-id 47
```

Also supports: `--start-at`, `--limit`

Use `mcp2cli jira <cmd> --help` for full parameter details.
