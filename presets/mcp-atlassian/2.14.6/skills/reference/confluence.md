# Confluence Commands

## search — Search Confluence content

```bash
mcp2cli confluence search --query "project documentation"
mcp2cli confluence search --query "type=page AND space=DEV" --limit 20
mcp2cli confluence search --query "label=documentation" --spaces-filter "DEV,TEAM"
```

Also supports: `--limit`, `--spaces-filter`

## comment list — Get comments for a page

```bash
mcp2cli confluence comment list --page-id 123456789
```

## comment add — Add a comment to a page

```bash
mcp2cli confluence comment add --page-id 123456789 --body "This is a comment"
```

## comment reply — Reply to a comment

```bash
mcp2cli confluence comment reply --comment-id 456789 --body "Replying to this comment"
```

## label list — Get labels for content

```bash
mcp2cli confluence label list --page-id 123456789
```

## label add — Add a label to content

```bash
mcp2cli confluence label add --page-id 123456789 --name "documentation"
```

## user search — Search Confluence users

```bash
mcp2cli confluence user search --query 'user.fullname ~ "John Doe"'
mcp2cli confluence user search --query 'user.fullname ~ "John"' --limit 5
```

Also supports: `--limit`, `--group-name`

Use `mcp2cli confluence <cmd> --help` for full parameter details.
