# Merge Request Commands

## create — Create a new merge request

```bash
mcp2cli gitlab mr create --title "Fix bug" --source-branch feature/fix --target-branch main
mcp2cli gitlab mr create --title "Add feature" --source-branch feature/add --target-branch main --project-id my-group/my-repo --description "Details here"
mcp2cli gitlab mr create --title "WIP feature" --source-branch feature/wip --target-branch main --draft true
```

Also supports: `--project-id`, `--description`, `--assignee-ids`, `--reviewer-ids`, `--labels`, `--draft`, `--remove-source-branch`, `--squash`, `--allow-collaboration`, `--target-project-id`

## get — Get MR details (by IID or source branch)

```bash
mcp2cli gitlab mr get --project-id my-group/my-repo --merge-request-iid 42
mcp2cli gitlab mr get --project-id my-group/my-repo --source-branch feature/fix
```

Also supports: `--source-branch`

## list — List merge requests

```bash
mcp2cli gitlab mr list --project-id my-group/my-repo
```

## update — Update a merge request

```bash
mcp2cli gitlab mr update --project-id my-group/my-repo --merge-request-iid 42 --title "Updated title"
mcp2cli gitlab mr update --project-id my-group/my-repo --merge-request-iid 42 --state-event close
```

Also supports: `--description`, `--target-branch`, `--assignee-ids`, `--reviewer-ids`, `--labels`, `--remove-source-branch`, `--squash`, `--draft`

## merge — Merge a merge request

```bash
mcp2cli gitlab mr merge --project-id my-group/my-repo --merge-request-iid 42
mcp2cli gitlab mr merge --project-id my-group/my-repo --merge-request-iid 42 --squash true --should-remove-source-branch true
```

Also supports: `--auto-merge`, `--merge-commit-message`, `--squash-commit-message`, `--merge-when-pipeline-succeeds`

## diff get — Get full diff of a merge request

```bash
mcp2cli gitlab mr diff get --project-id my-group/my-repo --merge-request-iid 42
```

Also supports: `--source-branch`, `--view` (inline|parallel), `--excluded-file-patterns`

## diff changed-files — List changed file paths (Step 1 of code review)

```bash
mcp2cli gitlab mr diff changed-files --project-id my-group/my-repo --merge-request-iid 42
```

Also supports: `--source-branch`, `--excluded-file-patterns`

## diff file — Get diffs for specific files (Step 2 of code review)

```bash
mcp2cli gitlab mr diff file --project-id my-group/my-repo --merge-request-iid 42 --file-paths '["src/api/users.ts","src/repo/user.go"]'
```

Also supports: `--source-branch`, `--unidiff`

## diff list — List diffs with pagination

```bash
mcp2cli gitlab mr diff list --project-id my-group/my-repo --merge-request-iid 42
```

Also supports: `--page`, `--per-page`, `--unidiff`

## approval get — Get approval state

```bash
mcp2cli gitlab mr approval get --project-id my-group/my-repo --merge-request-iid 42
```

## approval approve — Approve a merge request

```bash
mcp2cli gitlab mr approval approve --project-id my-group/my-repo --merge-request-iid 42
```

Also supports: `--sha`, `--approval-password`

## approval unapprove — Unapprove a merge request

```bash
mcp2cli gitlab mr approval unapprove --project-id my-group/my-repo --merge-request-iid 42
```

## conflict get — Get MR conflicts

```bash
mcp2cli gitlab mr conflict get --project-id my-group/my-repo --merge-request-iid 42
```

## thread create — Create a discussion thread on an MR

```bash
mcp2cli gitlab mr thread create --project-id my-group/my-repo --merge-request-iid 42 --body "This looks problematic"
```

## thread resolve — Resolve a discussion thread

```bash
mcp2cli gitlab mr thread resolve --project-id my-group/my-repo --merge-request-iid 42 --discussion-id abc123 --resolved true
```

## note create — Add a note to an MR

```bash
mcp2cli gitlab mr note create --project-id my-group/my-repo --merge-request-iid 42 --body "LGTM!"
```

Use `mcp2cli gitlab mr <action> --help` for full parameter details.
