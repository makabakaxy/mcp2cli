# Wiki Commands

## wiki list — List wiki pages in a project

```bash
mcp2cli gitlab wiki list --project-id my-group/my-repo
mcp2cli gitlab wiki list --project-id my-group/my-repo --with-content true
```

Also supports: `--with-content`, `--page`, `--per-page`

## wiki get — Get a wiki page

```bash
mcp2cli gitlab wiki get --project-id my-group/my-repo --slug my-page-slug
```

## wiki create — Create a new wiki page

```bash
mcp2cli gitlab wiki create --project-id my-group/my-repo --title "Getting Started" --content "# Getting Started\n..."
mcp2cli gitlab wiki create --project-id my-group/my-repo --title "API Docs" --content "# API\n..." --format markdown
```

Also supports: `--format`

## wiki update — Update an existing wiki page

```bash
mcp2cli gitlab wiki update --project-id my-group/my-repo --slug getting-started --content "# Updated Content\n..."
```

Also supports: `--title`, `--format`

## wiki delete — Delete a wiki page

```bash
mcp2cli gitlab wiki delete --project-id my-group/my-repo --slug getting-started
```

## wiki group list — List group wiki pages

```bash
mcp2cli gitlab wiki group list --group-id my-group
```

Also supports: `--with-content`, `--page`, `--per-page`

## wiki group get — Get a group wiki page

```bash
mcp2cli gitlab wiki group get --group-id my-group --slug my-page-slug
```

## wiki group create — Create a group wiki page

```bash
mcp2cli gitlab wiki group create --group-id my-group --title "Team Guidelines" --content "# Guidelines\n..."
```

Also supports: `--format`

## wiki group update — Update a group wiki page

```bash
mcp2cli gitlab wiki group update --group-id my-group --slug team-guidelines --content "# Updated\n..."
```

## wiki group delete — Delete a group wiki page

```bash
mcp2cli gitlab wiki group delete --group-id my-group --slug team-guidelines
```

Use `mcp2cli gitlab wiki <action> --help` for full parameter details.
