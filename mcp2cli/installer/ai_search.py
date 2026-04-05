"""AI-powered search for MCP server installation info."""

from __future__ import annotations

import json

import click

from mcp2cli.config.models import AISearchCandidate, AISearchResult
from mcp2cli.generator.llm_backend import get_backend

INSTALL_PROMPT_TEMPLATE = """You are an MCP server installation assistant. The user wants to install an MCP server named "{server_name}".

Search the internet to find the most relevant MCP server (up to 3 candidates), ranked by recommendation, then output a JSON object.

Search strategy:
0. You MUST use the WebSearch tool; do not use browser tools
1. Search for "{server_name} MCP server" or "{server_name} model context protocol"
2. Check GitHub repos for star count, whether it is an official repo, and MCP config examples in the README
3. Check npm / PyPI package pages to confirm the package name and installation method
4. Prefer: official repo > high star count > actively maintained

Output format (strict JSON):

```json
{{
  "found": true,
  "candidates": [
    {{
      "server_name": "{server_name}",
      "package_name": "package-name",
      "package_registry": "npm",
      "command": "npx",
      "args": ["-y", "{server_name}"],
      "env": {{
        "ENV_VAR_NAME": {{
          "description": "Description of this env var",
          "example": "https://example.com",
          "required": true,
          "sensitive": false
        }}
      }},
      "source_url": "https://github.com/...",
      "github_stars": "8.2k",
      "is_official": true,
      "description": "One-line description of what this MCP server does"
    }}
  ]
}}
```

Field notes:
- `candidates`: list of candidates sorted by recommendation, up to 3; use an array even if only one is found
- `github_stars`: GitHub star count formatted as "8.2k" or "430"; use "" if not found
- `is_official`: whether the repo is published by the original author / official maintainer
- `description`: short one-sentence English description
- `command`: launch command (common values: uvx, npx, node, python)
- `env.required`: whether the env var must be provided
- `env.sensitive`: whether the value is sensitive (e.g. an API token)

If the MCP server cannot be found, return:
```json
{{
  "found": false,
  "error": "Could not find MCP server named {server_name}",
  "suggestions": ["similar-server-name-1", "similar-server-name-2"]
}}
```

Important:
- Output JSON only — no other text
- Prefer the configuration format shown in the official documentation
- For the command field, prefer zero-install runners such as uvx (Python) or npx (Node.js)"""


def ai_search_server(server_name: str) -> AISearchResult | None:
    """Use AI to search for MCP server installation info.

    Returns AISearchResult or None on failure.
    """
    click.echo(f"🔍 Searching for {server_name} installation info...")

    backend = get_backend()
    prompt = INSTALL_PROMPT_TEMPLATE.format(server_name=server_name)

    result = backend.invoke(
        prompt,
        command_name="install search",
        server_name=server_name,
        show_progress=True,
        progress_message=f"Searching for {server_name}...",
    )

    if result.is_error:
        click.echo(f"AI search failed: {result.result}", err=True)
        return None

    # Parse the JSON from LLM result
    text = result.result.strip()
    parsed = _extract_json(text)
    if parsed is None:
        # Retry once with session
        if result.session_id:
            click.echo("  Retrying AI search (invalid JSON)...")
            retry_result = backend.resume(
                result.session_id,
                "Your previous output was not valid JSON. Please output only a JSON object with no other text.",
            )
            if not retry_result.is_error:
                parsed = _extract_json(retry_result.result.strip())

    if parsed is None:
        click.echo("Error: Could not parse AI search result as JSON.", err=True)
        return None

    search_result = AISearchResult.from_dict(parsed)

    if not search_result.found:
        click.echo(f"  ✗ Could not find MCP server \"{server_name}\"")
        if search_result.error:
            click.echo(f"  {search_result.error}")
        if search_result.suggestions:
            click.echo(f"  Did you mean: {', '.join(search_result.suggestions)}")
        backend.clear_session("install search", server_name)
        return search_result

    # Select from candidates (or auto-select if only one)
    candidate = _select_candidate(server_name, search_result.candidates)
    if candidate is None:
        backend.clear_session("install search", server_name)
        return None

    # Populate top-level fields from the selected candidate
    search_result.server_name = candidate.server_name
    search_result.package_name = candidate.package_name
    search_result.package_registry = candidate.package_registry
    search_result.command = candidate.command
    search_result.args = candidate.args
    search_result.env = candidate.env
    search_result.source_url = candidate.source_url

    if search_result.source_url:
        click.echo(f"  Source: {search_result.source_url}")

    backend.clear_session("install search", server_name)
    return search_result


def _select_candidate(
    server_name: str,
    candidates: list[AISearchCandidate],
) -> AISearchCandidate | None:
    """Show candidate list and let user pick one. Returns selected candidate or None."""
    if not candidates:
        click.echo(f"  ✗ No candidates found for \"{server_name}\"", err=True)
        return None

    if len(candidates) == 1:
        c = candidates[0]
        click.echo(f"  Found: {c.server_name} ({c.package_registry})")
        return c

    # Multiple candidates — show selection table
    click.echo(f"\nFound {len(candidates)} MCP servers matching \"{server_name}\". Please select one:\n")

    col_name = max((len(c.package_name or c.server_name) for c in candidates), default=4)
    col_name = max(col_name, 4)

    rows = []
    for i, c in enumerate(candidates, start=1):
        name = c.package_name or c.server_name
        stars = f"★ {c.github_stars}" if c.github_stars else "—"
        status = "✓ Official" if c.is_official else "Community"
        desc = c.description or ""
        suffix = " (Recommended)" if i == 1 else ""
        rows.append((i, name, stars, status, desc + suffix, c.source_url or ""))

    header = f"  {'#':>2}  {'Name':<{col_name}}  {'Stars':<7}  {'Status':<10}  Description"
    click.echo(header)
    click.echo("  " + "─" * (len(header) - 2))

    for i, name, stars, status, desc, url in rows:
        click.echo(f"  {i:>2}  {name:<{col_name}}  {stars:<7}  {status:<10}  {desc}")
        if url:
            click.echo(f"      {'':>{col_name}}             {url}")

    click.echo("")
    raw = click.prompt(
        f"  Enter number [1-{len(candidates)}]",
        default="1",
        show_default=True,
    ).strip()

    try:
        choice = int(raw)
        if 1 <= choice <= len(candidates):
            selected = candidates[choice - 1]
            click.echo(f"  Selected: {selected.package_name or selected.server_name}")
            return selected
    except ValueError:
        pass

    click.echo("  Invalid selection, using first result.")
    return candidates[0]


def _extract_json(text: str) -> dict | None:
    """Try to extract JSON from text that may contain markdown fences."""
    # Direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try extracting from ```json ... ```
    import re
    match = re.search(r"```(?:json)?\s*\n(.*?)```", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            pass

    # Try finding { ... } block
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end > start:
        try:
            return json.loads(text[start:end + 1])
        except json.JSONDecodeError:
            pass

    return None
