# Confluence Search Reference

## mcp2cli confluence search

Search Confluence content using simple terms or CQL.

| Parameter | Required | Description |
|---|---|---|
| `--query` | yes | Search query (simple text or CQL) |
| `--limit` | no | Max results (1-50, default 10) |
| `--spaces-filter` | no | Comma-separated space keys |

**Query examples:**
```
"project documentation"
"type=page AND space=DEV"
"title~\"Meeting Notes\""
"label=documentation"
"lastModified > startOfMonth(\"-1M\")"
"contributor = currentUser() AND lastModified > startOfWeek()"
```

## mcp2cli confluence user search

| Parameter | Required | Description |
|---|---|---|
| `--query` | yes | CQL user search query |
| `--limit` | no | Max results (1-50) |

**Examples:**
```bash
mcp2cli confluence user search --query 'user.fullname ~ "John"'
```
