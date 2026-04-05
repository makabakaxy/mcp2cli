# JIRA Issue Commands

## create — Create a new JIRA issue

```bash
mcp2cli jira issue create --project-key INFRA --summary "Fix memory leak" --issue-type Task
mcp2cli jira issue create --project-key DEV --summary "Add login" --issue-type Story --assignee john@example.com
mcp2cli jira issue create --project-key INFRA --summary "Bug fix" --issue-type Bug --components "Frontend,API" --additional-fields '{"priority": {"name": "High"}}'
```

Also supports: `--description`, `--components`, `--additional-fields`

## get — Get issue details by key

```bash
mcp2cli jira issue get --issue-key INFRA-1234
mcp2cli jira issue get --issue-key INFRA-1234 --fields "summary,status,assignee" --comment-limit 5
```

Also supports: `--fields`, `--expand`, `--comment-limit`, `--properties`, `--update-history`

## search — Search issues using JQL

```bash
mcp2cli jira issue search --jql "project=INFRA AND status=Open"
mcp2cli jira issue search --jql "assignee=currentUser() AND updated >= -7d" --limit 20
```

Also supports: `--fields`, `--limit`, `--start-at`, `--expand`, `--projects-filter`, `--page-token`

## update — Update an existing issue

```bash
mcp2cli jira issue update --issue-key INFRA-1234 --fields '{"summary": "New title", "assignee": "user@example.com"}'
```

Also supports: `--additional-fields`, `--components`, `--attachments`

## delete — Delete an issue

```bash
mcp2cli jira issue delete --issue-key INFRA-1234
```

## transition — Transition issue to new status

```bash
mcp2cli jira issue transition --issue-key INFRA-1234 --transition-id 31
mcp2cli jira issue transition --issue-key INFRA-1234 --transition-id 31 --comment "Moving to done"
```

Also supports: `--fields`, `--comment`

## transitions — List available transitions

```bash
mcp2cli jira issue transitions --issue-key INFRA-1234
```

## link — Link two issues

```bash
mcp2cli jira issue link --link-type "Blocks" --inward-issue-key INFRA-123 --outward-issue-key INFRA-456
```

Also supports: `--comment`, `--comment-visibility`

## unlink — Remove a link between issues

```bash
mcp2cli jira issue unlink --link-id 12345
```

## epic-link — Link issue to an epic

```bash
mcp2cli jira issue epic-link --issue-key INFRA-123 --epic-key INFRA-100
```

## remote-link — Create a remote web link

```bash
mcp2cli jira issue remote-link --issue-key INFRA-123 --url "https://docs.example.com" --title "Documentation"
```

Also supports: `--summary`, `--relationship`, `--icon-url`

## batch-create — Batch create multiple issues

```bash
mcp2cli jira issue batch-create --issues '[{"project_key":"INFRA","summary":"Task 1","issue_type":"Task"},{"project_key":"INFRA","summary":"Task 2","issue_type":"Bug"}]'
```

Also supports: `--validate-only`

## batch-changelogs — Get changelogs for multiple issues

```bash
mcp2cli jira issue batch-changelogs --issue-ids-or-keys "INFRA-1,INFRA-2"
```

Also supports: `--fields`, `--limit`

## dates — Get date and transition history

```bash
mcp2cli jira issue dates --issue-key INFRA-1234
```

Also supports: `--include-status-changes`, `--include-status-summary`

## sla — Calculate SLA metrics

```bash
mcp2cli jira issue sla --issue-key INFRA-1234
mcp2cli jira issue sla --issue-key INFRA-1234 --metrics "cycle_time,time_in_status"
```

Also supports: `--metrics`, `--working-hours-only`, `--include-raw-dates`

## dev-info — Get development info (PRs, commits, branches)

```bash
mcp2cli jira issue dev-info --issue-key INFRA-1234
```

Also supports: `--application-type`, `--data-type`

## comment add — Add a comment

```bash
mcp2cli jira issue comment add --issue-key INFRA-1234 --body "This is a comment"
```

Also supports: `--visibility`, `--public`

## comment edit — Edit a comment

```bash
mcp2cli jira issue comment edit --issue-key INFRA-1234 --comment-id 56789 --body "Updated comment"
```

Also supports: `--visibility`

## watcher list/add/remove — Manage watchers

```bash
mcp2cli jira issue watcher list --issue-key INFRA-1234
mcp2cli jira issue watcher add --issue-key INFRA-1234 --user-identifier user@example.com
mcp2cli jira issue watcher remove --issue-key INFRA-1234 --account-id abc123
```

## worklog list/add — Manage worklogs

```bash
mcp2cli jira issue worklog list --issue-key INFRA-1234
mcp2cli jira issue worklog add --issue-key INFRA-1234 --time-spent "2h 30m"
```

Also supports: `--comment`, `--started`, `--original-estimate`, `--remaining-estimate`

Use `mcp2cli jira issue <action> --help` for full parameter details.
