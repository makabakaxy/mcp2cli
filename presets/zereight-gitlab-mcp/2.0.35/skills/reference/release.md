# Release Commands

## release list — List all releases

```bash
mcp2cli gitlab release list --project-id my-group/my-repo
```

## release get — Get a release by tag name

```bash
mcp2cli gitlab release get --project-id my-group/my-repo --tag-name v1.0.0
```

## release create — Create a new release

```bash
mcp2cli gitlab release create --project-id my-group/my-repo --tag-name v1.0.0 --name "v1.0.0 Release"
mcp2cli gitlab release create --project-id my-group/my-repo --tag-name v1.2.0 --name "Release v1.2.0" --description "## Changelog\n- Feature A\n- Bug fix B"
```

Also supports: `--description`, `--ref`, `--milestones`, `--released-at`, `--assets`

## release update — Update an existing release

```bash
mcp2cli gitlab release update --project-id my-group/my-repo --tag-name v1.0.0 --name "Updated Release"
```

Also supports: `--description`, `--milestones`, `--released-at`

## release delete — Delete a release

```bash
mcp2cli gitlab release delete --project-id my-group/my-repo --tag-name v1.0.0
```

## release evidence — Create release evidence

```bash
mcp2cli gitlab release evidence --project-id my-group/my-repo --tag-name v1.0.0
```

## release asset-download — Download a release asset

```bash
mcp2cli gitlab release asset-download --project-id my-group/my-repo --tag-name v1.0.0 --direct-asset-path /binaries/app.tar.gz
```

Use `mcp2cli gitlab release <action> --help` for full parameter details.
