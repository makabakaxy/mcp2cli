---
name: "zereight/gitlab-mcp"
description: Manage GitLab repos, MRs, issues, pipelines, deployments, and releases via CLI. Use when user needs to create/search repos, review/merge MRs, manage issues, or run pipelines.
source_version: "2.0.35"
source_cli_hash: "a0ad80a2"
generated_at: "2026-04-05T10:43:44.524105+00:00"
---

# zereight/gitlab-mcp (via mcp2cli)

Manage GitLab projects, merge requests, issues, pipelines, and releases via CLI.

## Shortcuts

- `mcp2cli gitlab <cmd>` (server alias)

## Commands

### Merge Requests
| Command | Description | Example | Ref |
|---|---|---|---|
| `mcp2cli gitlab mr create` | Create a new MR | `mcp2cli gitlab mr create --title "Fix bug" --source-branch feature/fix --target-branch main` | [ref](reference/mr.md) |
| `mcp2cli gitlab mr get` | Get MR details | `mcp2cli gitlab mr get --project-id my-group/my-repo --merge-request-iid 42` | [ref](reference/mr.md) |
| `mcp2cli gitlab mr list` | List merge requests | `mcp2cli gitlab mr list --project-id my-group/my-repo` | [ref](reference/mr.md) |
| `mcp2cli gitlab mr update` | Update a merge request | | [ref](reference/mr.md) |
| `mcp2cli gitlab mr merge` | Merge a merge request | `mcp2cli gitlab mr merge --project-id my-group/my-repo --merge-request-iid 42` | [ref](reference/mr.md) |
| `mcp2cli gitlab mr diff get` | Get MR full diff | | [ref](reference/mr.md) |
| `mcp2cli gitlab mr diff changed-files` | List changed file paths | `mcp2cli gitlab mr diff changed-files --project-id my-group/repo --merge-request-iid 42` | [ref](reference/mr.md) |
| `mcp2cli gitlab mr approval approve` | Approve a merge request | | [ref](reference/mr.md) |

### Issues
| Command | Description | Example | Ref |
|---|---|---|---|
| `mcp2cli gitlab issue create` | Create a new issue | `mcp2cli gitlab issue create --title "Fix memory leak" --project-id my-group/my-repo` | [ref](reference/issue.md) |
| `mcp2cli gitlab issue get` | Get issue details | `mcp2cli gitlab issue get --project-id my-group/my-repo --issue-iid 10` | [ref](reference/issue.md) |
| `mcp2cli gitlab issue list` | List issues | `mcp2cli gitlab issue list --project-id my-group/my-repo` | [ref](reference/issue.md) |
| `mcp2cli gitlab issue my` | List my assigned issues | `mcp2cli gitlab issue my` | [ref](reference/issue.md) |
| `mcp2cli gitlab issue update` | Update an issue | | [ref](reference/issue.md) |
| `mcp2cli gitlab issue delete` | Delete an issue | | [ref](reference/issue.md) |

### Repositories & Files
| Command | Description | Example | Ref |
|---|---|---|---|
| `mcp2cli gitlab repo search` | Search for projects | `mcp2cli gitlab repo search --search my-project` | [ref](reference/repo.md) |
| `mcp2cli gitlab repo get` | Get project details | `mcp2cli gitlab repo get --project-id my-group/my-repo` | [ref](reference/repo.md) |
| `mcp2cli gitlab repo create` | Create a new project | `mcp2cli gitlab repo create --name my-new-repo --visibility private` | [ref](reference/repo.md) |
| `mcp2cli gitlab repo file get` | Get file contents | `mcp2cli gitlab repo file get --project-id my-group/my-repo --file-path src/main.go` | [ref](reference/repo.md) |
| `mcp2cli gitlab repo file update` | Create or update a file | | [ref](reference/repo.md) |
| `mcp2cli gitlab repo tree` | List files/dirs in repo | | [ref](reference/repo.md) |

### Pipelines & CI
| Command | Description | Example | Ref |
|---|---|---|---|
| `mcp2cli gitlab pipeline list` | List pipelines | `mcp2cli gitlab pipeline list --project-id my-group/my-repo` | [ref](reference/pipeline.md) |
| `mcp2cli gitlab pipeline get` | Get pipeline details | | [ref](reference/pipeline.md) |
| `mcp2cli gitlab pipeline create` | Trigger a new pipeline | | [ref](reference/pipeline.md) |
| `mcp2cli gitlab pipeline retry` | Retry a pipeline | | [ref](reference/pipeline.md) |
| `mcp2cli gitlab pipeline job output` | Get job log output | | [ref](reference/pipeline.md) |
| `mcp2cli gitlab pipeline job list` | List pipeline jobs | | [ref](reference/pipeline.md) |

### Releases & Other
| Command | Description | Example | Ref |
|---|---|---|---|
| `mcp2cli gitlab release create` | Create a release | | [ref](reference/release.md) |
| `mcp2cli gitlab release list` | List releases | | [ref](reference/release.md) |
| `mcp2cli gitlab milestone create` | Create a milestone | | [ref](reference/misc.md) |
| `mcp2cli gitlab wiki create` | Create a wiki page | | [ref](reference/wiki.md) |
| `mcp2cli gitlab deployment list` | List deployments | | [ref](reference/misc.md) |
| `mcp2cli gitlab branch create` | Create a branch | | [ref](reference/misc.md) |

## Discover Parameters

Append `--help` to any command for full parameter list:

    mcp2cli gitlab mr create --help

> **Note**: Use Ref links in the Commands table above for detailed parameter reference and more examples.

## User Notes

> **MUST READ** [users/SKILL.md](users/SKILL.md) for custom workflows and tips.
> See [users/workflows.md](users/workflows.md) for multi-step workflow examples.
> Not overwritten by updates.
