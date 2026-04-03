"""Preset spec parsing — 'server@version' syntax."""

from __future__ import annotations


def parse_preset_spec(spec: str) -> tuple[str, str | None]:
    """Parse a preset specifier into (server_name, version).

    Supported formats:
        'mcp-atlassian'        → ('mcp-atlassian', None)
        'mcp-atlassian@1.2.3'  → ('mcp-atlassian', '1.2.3')
        'mcp-atlassian@latest' → ('mcp-atlassian', None)

    Returns:
        (server_name, version_or_none)

    Raises:
        ValueError: If the spec is empty or has an empty server/version part.
    """
    if not spec or not spec.strip():
        raise ValueError("Preset spec cannot be empty.")

    spec = spec.strip()

    if "@" not in spec:
        return spec, None

    parts = spec.split("@", 1)
    server_name = parts[0]
    version = parts[1]

    if not server_name:
        raise ValueError(f"Invalid preset spec '{spec}': server name is empty.")

    if not version:
        raise ValueError(f"Invalid preset spec '{spec}': version is empty after '@'.")

    if version == "latest":
        return server_name, None

    return server_name, version
