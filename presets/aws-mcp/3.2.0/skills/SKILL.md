---
name: "aws-mcp"
description: Execute and suggest AWS CLI commands across all AWS services via natural language or direct CLI syntax. Use when user needs to manage EC2, S3, IAM, Lambda, RDS, or any other AWS resource.
source_version: "3.2.0"
source_cli_hash: "383d90d9"
generated_at: "2026-04-06T09:17:32.833960+00:00"
---

# aws-mcp (via mcp2cli)

Execute AWS CLI commands or get suggestions for AWS operations via natural language.

## Shortcuts

- `mcp2cli aws <cmd>` (alias for `mcp2cli aws-mcp <cmd>`)

## Commands

### AWS
| Command | Description | Example | Ref |
|---|---|---|---|
| `mcp2cli aws call` | Execute AWS CLI commands directly | `mcp2cli aws call --cli-command 'aws s3api list-buckets --region us-east-1'`<br>`mcp2cli aws call --cli-command 'aws ec2 describe-instances --region us-east-1'` | [ref](reference/aws.md) |
| `mcp2cli aws suggest` | Suggest AWS CLI commands from natural language | `mcp2cli aws suggest --query 'List all running EC2 instances in us-east-1'`<br>`mcp2cli aws suggest --query 'Create an S3 bucket with versioning enabled'` | [ref](reference/aws.md) |

## Discover Parameters

Append `--help` to any command for full parameter list:

    mcp2cli aws call --help

> **Note**: Use Ref links in the Commands table above to view detailed parameter reference and more examples.

## User Notes

> **MUST READ** [users/skill.md](users/skill.md) for custom workflows and tips.
> **Config**: MCP server settings live in `~/.agents/mcp2cli/servers.yaml` - edit there to take effect.
