# Confluence Page Reference

## mcp2cli confluence page get

Get page content by ID or by title + space key.

| Parameter | Required | Description |
|---|---|---|
| `--page-id` | no* | Page ID |
| `--title` | no* | Exact page title (requires --space-key) |
| `--space-key` | no* | Space key (requires --title) |
| `--include-metadata` | no | Include metadata (default true) |
| `--convert-to-markdown` | no | Convert to markdown (default true) |

*Provide either `--page-id` OR both `--title` and `--space-key`.

## mcp2cli confluence page create

| Parameter | Required | Description |
|---|---|---|
| `--space-key` | yes | Space key (e.g., "TEAM") |
| `--title` | yes | Page title |
| `--content` | yes | Page content (markdown by default) |
| `--parent-id` | no | Parent page ID |
| `--content-format` | no | markdown, wiki, or storage |

**Examples:**
```bash
mcp2cli confluence page create --space-key TEAM --title "Meeting Notes" --content "# Notes\n\n- Item 1"
mcp2cli confluence page create --space-key DEV --title "API Docs" --content "..." --parent-id 12345
```

## mcp2cli confluence page update

| Parameter | Required | Description |
|---|---|---|
| `--page-id` | yes | Page ID |
| `--title` | yes | Page title |
| `--content` | yes | New content |
| `--is-minor-edit` | no | Minor edit flag |
| `--version-comment` | no | Version comment |

## mcp2cli confluence page delete

| Parameter | Required | Description |
|---|---|---|
| `--page-id` | yes | Page ID |

## mcp2cli confluence page children

| Parameter | Required | Description |
|---|---|---|
| `--parent-id` | yes | Parent page ID |
| `--limit` | no | Max results (1-50) |
| `--include-content` | no | Include page content |

## mcp2cli confluence page move

| Parameter | Required | Description |
|---|---|---|
| `--page-id` | yes | Page ID to move |
| `--target-parent-id` | no | New parent page ID |
| `--target-space-key` | no | Target space for cross-space moves |
| `--position` | no | append, above, or below |

## mcp2cli confluence comment add

| Parameter | Required | Description |
|---|---|---|
| `--page-id` | yes | Page ID |
| `--body` | yes | Comment in Markdown |

## mcp2cli confluence attachment upload

| Parameter | Required | Description |
|---|---|---|
| `--content-id` | yes | Page ID |
| `--file-path` | yes | Path to file |
| `--comment` | no | Attachment comment |
