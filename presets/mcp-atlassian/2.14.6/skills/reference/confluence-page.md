# Confluence Page Commands

## get — Get page content by ID or title

```bash
mcp2cli confluence page get --page-id 123456789
mcp2cli confluence page get --title "Meeting Notes" --space-key TEAM
```

Also supports: `--page-id`, `--title`, `--space-key`, `--include-metadata`, `--convert-to-markdown`

## create — Create a new page

```bash
mcp2cli confluence page create --space-key TEAM --title "Meeting Notes" --content "# Notes\n..."
mcp2cli confluence page create --space-key DEV --title "API Design" --content "# API" --parent-id 123456789
```

Also supports: `--parent-id`, `--content-format`, `--enable-heading-anchors`, `--emoji`

## update — Update page content

```bash
mcp2cli confluence page update --page-id 123456789 --title "Updated Notes" --content "# Updated\n..."
```

Also supports: `--is-minor-edit`, `--version-comment`, `--parent-id`, `--content-format`, `--enable-heading-anchors`, `--emoji`

## delete — Delete a page

```bash
mcp2cli confluence page delete --page-id 123456789
```

## move — Move a page to a new parent or space

```bash
mcp2cli confluence page move --page-id 123456789 --target-parent-id 987654321
mcp2cli confluence page move --page-id 123456789 --target-space-key NEWSPACE
```

Also supports: `--target-parent-id`, `--target-space-key`, `--position`

## children — Get child pages

```bash
mcp2cli confluence page children --parent-id 123456789
mcp2cli confluence page children --parent-id 123456789 --limit 25 --include-content
```

Also supports: `--expand`, `--limit`, `--include-content`, `--convert-to-markdown`, `--start`, `--include-folders`

## history — Get a historical version of a page

```bash
mcp2cli confluence page history --page-id 123456789 --version 3
```

Also supports: `--convert-to-markdown`

## diff — Get diff between two versions

```bash
mcp2cli confluence page diff --page-id 123456789 --from-version 1 --to-version 3
```

## views — Get page view statistics

```bash
mcp2cli confluence page views --page-id 123456789
```

Also supports: `--include-title`

## images — Get all images from a page

```bash
mcp2cli confluence page images --content-id 123456789
```

Use `mcp2cli confluence page <action> --help` for full parameter details.
