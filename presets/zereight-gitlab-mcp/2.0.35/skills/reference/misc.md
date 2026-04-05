# Miscellaneous Commands

## branch create — Create a new branch

```bash
mcp2cli gitlab branch create --project-id my-group/my-repo --branch feature/my-feature --ref main
```

Also supports: `--project-id`, `--ref`

## branch diffs — Get diffs between two branches/commits

```bash
mcp2cli gitlab branch diffs --project-id my-group/my-repo --from main --to feature/branch
mcp2cli gitlab branch diffs --project-id my-group/my-repo --from main --to feature/branch --excluded-file-patterns '["^vendor/"]'
```

Also supports: `--straight`, `--excluded-file-patterns`

## deployment list — List deployments

```bash
mcp2cli gitlab deployment list --project-id my-group/my-repo
```

## deployment get — Get a specific deployment

```bash
mcp2cli gitlab deployment get --project-id my-group/my-repo --deployment-id 123
```

## environment list — List environments

```bash
mcp2cli gitlab environment list --project-id my-group/my-repo
```

## environment get — Get a specific environment

```bash
mcp2cli gitlab environment get --project-id my-group/my-repo --environment-id 5
```

## milestone create — Create a milestone

```bash
mcp2cli gitlab milestone create --project-id my-group/my-repo --title "v2.0 Release"
mcp2cli gitlab milestone create --project-id my-group/my-repo --title "Sprint 5" --due-date 2026-04-30
```

Also supports: `--description`, `--due-date`, `--start-date`

## milestone list — List milestones

```bash
mcp2cli gitlab milestone list --project-id my-group/my-repo
```

Also supports: `--state`, `--search`

## milestone get — Get a specific milestone

```bash
mcp2cli gitlab milestone get --project-id my-group/my-repo --milestone-id 10
```

## milestone update — Edit a milestone

```bash
mcp2cli gitlab milestone update --project-id my-group/my-repo --milestone-id 10 --title "Updated title" --state-event close
```

## milestone delete — Delete a milestone

```bash
mcp2cli gitlab milestone delete --project-id my-group/my-repo --milestone-id 10
```

## milestone issues — Get milestone issues

```bash
mcp2cli gitlab milestone issues --project-id my-group/my-repo --milestone-id 10
```

## label list — List project labels

```bash
mcp2cli gitlab label list --project-id my-group/my-repo
```

Also supports: `--with-counts`, `--search`

## label create — Create a label

```bash
mcp2cli gitlab label create --project-id my-group/my-repo --name bug --color "#ff0000"
```

Also supports: `--description`, `--priority`

## label delete — Delete a label

```bash
mcp2cli gitlab label delete --project-id my-group/my-repo --label-id bug
```

## commit list — List commits

```bash
mcp2cli gitlab commit list --project-id my-group/my-repo
```

## commit get — Get commit details

```bash
mcp2cli gitlab commit get --project-id my-group/my-repo --sha abc1234
```

## commit diff — Get commit diff

```bash
mcp2cli gitlab commit diff --project-id my-group/my-repo --sha abc1234
```

## namespace list — List namespaces

```bash
mcp2cli gitlab namespace list
mcp2cli gitlab namespace list --search my-ns
```

Also supports: `--owned`, `--page`, `--per-page`

## namespace verify — Verify if a namespace path exists

```bash
mcp2cli gitlab namespace verify --path my-namespace
```

## group projects — List projects in a group

```bash
mcp2cli gitlab group projects --group-id my-group
mcp2cli gitlab group projects --group-id my-group --include-subgroups true
```

Also supports: `--search`, `--order-by`, `--sort`, `--archived`, `--visibility`, `--page`, `--per-page`

## user get — Get user details by usernames

```bash
mcp2cli gitlab user get --usernames '["john_doe"]'
```

## event list — List events for current user

```bash
mcp2cli gitlab event list
```

## event project-list — List events for a project

```bash
mcp2cli gitlab event project-list --project-id my-group/my-repo
```

## misc note — Add a note to an issue or MR

```bash
mcp2cli gitlab misc note --noteable-type issue --body "Comment text" --project-id my-group/my-repo --noteable-iid 42
```

## misc upload-markdown — Upload file for markdown use

```bash
mcp2cli gitlab misc upload-markdown --project-id my-group/my-repo --file-path /path/to/image.png
```

## misc download-attachment — Download an uploaded file

```bash
mcp2cli gitlab misc download-attachment --project-id my-group/my-repo --secret abc123 --filename image.png
```

Use `mcp2cli gitlab <group> <action> --help` for full parameter details.
