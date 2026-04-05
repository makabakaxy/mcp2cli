# Confluence Attachment Commands

## list — List attachments for content

```bash
mcp2cli confluence attachment list --content-id 123456789
mcp2cli confluence attachment list --content-id 123456789 --filename "report.pdf"
```

Also supports: `--start`, `--limit`, `--filename`, `--media-type`

## upload — Upload an attachment

```bash
mcp2cli confluence attachment upload --content-id 123456789 --file-path ./diagram.png
mcp2cli confluence attachment upload --content-id 123456789 --file-path ./report.pdf --comment "Q4 report"
```

Also supports: `--comment`, `--minor-edit`

## batch-upload — Upload multiple attachments

```bash
mcp2cli confluence attachment batch-upload --content-id 123456789 --file-paths "./file1.pdf,./file2.png"
```

Also supports: `--comment`, `--minor-edit`

## download — Download an attachment

```bash
mcp2cli confluence attachment download --attachment-id att123456789
```

## download-all — Download all attachments for content

```bash
mcp2cli confluence attachment download-all --content-id 123456789
```

## delete — Delete an attachment

```bash
mcp2cli confluence attachment delete --attachment-id att123456789
```

Use `mcp2cli confluence attachment <action> --help` for full parameter details.
