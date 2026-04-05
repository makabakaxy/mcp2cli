# Pipeline & CI Commands

## pipeline list — List pipelines

```bash
mcp2cli gitlab pipeline list --project-id my-group/my-repo
mcp2cli gitlab pipeline list --project-id my-group/my-repo --status failed --ref main
```

Also supports: `--scope` (running|pending|finished|branches|tags), `--status`, `--ref`, `--sha`, `--yaml-errors`, `--username`, `--updated-after`, `--updated-before`, `--page`, `--per-page`

## pipeline get — Get pipeline details

```bash
mcp2cli gitlab pipeline get --project-id my-group/my-repo --pipeline-id 1234
```

## pipeline create — Trigger a new pipeline

```bash
mcp2cli gitlab pipeline create --project-id my-group/my-repo --ref main
mcp2cli gitlab pipeline create --project-id my-group/my-repo --ref feature/branch
```

Also supports: `--variables`

## pipeline retry — Retry a failed pipeline

```bash
mcp2cli gitlab pipeline retry --project-id my-group/my-repo --pipeline-id 1234
```

## pipeline cancel — Cancel a running pipeline

```bash
mcp2cli gitlab pipeline cancel --project-id my-group/my-repo --pipeline-id 1234
```

## pipeline job list — List all jobs in a pipeline

```bash
mcp2cli gitlab pipeline job list --project-id my-group/my-repo --pipeline-id 1234
```

## pipeline job get — Get job details

```bash
mcp2cli gitlab pipeline job get --project-id my-group/my-repo --job-id 5678
```

## pipeline job output — Get job log output

```bash
mcp2cli gitlab pipeline job output --project-id my-group/my-repo --job-id 5678
```

## pipeline job play — Trigger a manual job

```bash
mcp2cli gitlab pipeline job play --project-id my-group/my-repo --job-id 5678
```

## pipeline job retry — Retry a failed job

```bash
mcp2cli gitlab pipeline job retry --project-id my-group/my-repo --job-id 5678
```

## pipeline job cancel — Cancel a running job

```bash
mcp2cli gitlab pipeline job cancel --project-id my-group/my-repo --job-id 5678
```

## pipeline artifact list — List job artifacts

```bash
mcp2cli gitlab pipeline artifact list --project-id my-group/my-repo --job-id 5678
```

## pipeline artifact download — Download artifact archive

```bash
mcp2cli gitlab pipeline artifact download --project-id my-group/my-repo --job-id 5678
```

## pipeline artifact get-file — Get a specific artifact file

```bash
mcp2cli gitlab pipeline artifact get-file --project-id my-group/my-repo --job-id 5678 --artifact-path dist/app.zip
```

Use `mcp2cli gitlab pipeline <action> --help` for full parameter details.
