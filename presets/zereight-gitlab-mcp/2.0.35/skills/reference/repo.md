# Repository & File Commands

## repo search — Search for projects

```bash
mcp2cli gitlab repo search --search my-project
mcp2cli gitlab repo search --search "my team api" --per-page 50
```

Also supports: `--page`, `--per-page`

## repo list — List accessible projects

```bash
mcp2cli gitlab repo list
mcp2cli gitlab repo list --owned true --visibility private
```

Also supports: `--search`, `--search-namespaces`, `--owned`, `--membership`, `--simple`, `--archived`, `--visibility` (public|internal|private), `--order-by`, `--sort`, `--with-issues-enabled`, `--with-merge-requests-enabled`, `--min-access-level`, `--page`, `--per-page`

## repo get — Get project details

```bash
mcp2cli gitlab repo get --project-id my-group/my-repo
```

## repo create — Create a new project

```bash
mcp2cli gitlab repo create --name my-new-repo --visibility private
mcp2cli gitlab repo create --name my-new-repo --visibility public --initialize-with-readme true
```

Also supports: `--description`, `--visibility` (private|internal|public), `--initialize-with-readme`

## repo fork — Fork a project

```bash
mcp2cli gitlab repo fork --project-id my-group/my-repo
mcp2cli gitlab repo fork --project-id my-group/my-repo --namespace my-namespace
```

Also supports: `--namespace`

## repo tree — List files and directories

```bash
mcp2cli gitlab repo tree --project-id my-group/my-repo
mcp2cli gitlab repo tree --project-id my-group/my-repo --path src/ --ref main --recursive true
```

Also supports: `--path`, `--ref`, `--recursive`, `--per-page`, `--page-token`, `--pagination`

## repo file get — Get file contents

```bash
mcp2cli gitlab repo file get --project-id my-group/my-repo --file-path src/main.go
mcp2cli gitlab repo file get --project-id my-group/my-repo --file-path README.md --ref develop
```

Also supports: `--ref`

## repo file update — Create or update a single file

```bash
mcp2cli gitlab repo file update --project-id my-group/my-repo --file-path src/config.json --content '{"key":"value"}' --commit-message "Update config" --branch main
```

Also supports: `--project-id`, `--previous-path`, `--last-commit-id`, `--commit-id`

## repo file push — Push multiple files in one commit

```bash
mcp2cli gitlab repo file push --project-id my-group/my-repo --branch main --commit-message "Add files" --files '[{"file_path":"a.txt","content":"hello"},{"file_path":"b.txt","content":"world"}]'
```

## repo member list — List project members

```bash
mcp2cli gitlab repo member list --project-id my-group/my-repo
mcp2cli gitlab repo member list --project-id my-group/my-repo --query "john"
```

Also supports: `--query`, `--user-ids`, `--skip-users`, `--include-inheritance`, `--per-page`, `--page`

Use `mcp2cli gitlab repo <action> --help` for full parameter details.
