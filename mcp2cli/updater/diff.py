"""Tool list diff computation between old and new scans."""

from __future__ import annotations

import json
from dataclasses import dataclass, field

from mcp2cli.config.models import ToolsJSON


@dataclass
class ToolsDiff:
    """Diff result between two tool snapshots."""

    version_changed: bool
    old_version: str | None
    new_version: str | None
    added_tools: list[str] = field(default_factory=list)
    removed_tools: list[str] = field(default_factory=list)
    schema_changed_tools: list[str] = field(default_factory=list)

    @property
    def has_any_change(self) -> bool:
        return (
            self.version_changed
            or bool(self.added_tools)
            or bool(self.removed_tools)
            or bool(self.schema_changed_tools)
        )

    @property
    def needs_cli_regen(self) -> bool:
        """Tool additions or removals require CLI tree regeneration."""
        return bool(self.added_tools or self.removed_tools)

    def summary_lines(self) -> list[str]:
        lines: list[str] = []
        if self.version_changed:
            lines.append(f"version: {self.old_version} -> {self.new_version}")

        old_count = (
            len(set(self.removed_tools))
            + len(set(self.schema_changed_tools))
            + (len(set()) if not self.added_tools else 0)
        )
        if self.added_tools or self.removed_tools:
            lines.append(f"tools: +{len(self.added_tools)} -{len(self.removed_tools)}")
            for t in self.added_tools:
                lines.append(f"  + {t}")
            for t in self.removed_tools:
                lines.append(f"  - {t}")

        if self.schema_changed_tools:
            lines.append(f"schema changes: {', '.join(self.schema_changed_tools)}")

        return lines


def compute_diff(old: ToolsJSON, new: ToolsJSON) -> ToolsDiff:
    """Compare two ToolsJSON snapshots and return a ToolsDiff."""
    old_names = old.tool_names()
    new_names = new.tool_names()

    added = sorted(new_names - old_names)
    removed = sorted(old_names - new_names)

    # Schema comparison for tools present in both
    common = old_names & new_names
    old_schemas = {t.name: t.input_schema for t in old.tools}
    new_schemas = {t.name: t.input_schema for t in new.tools}

    schema_changed = []
    for name in sorted(common):
        old_s = json.dumps(old_schemas.get(name, {}), sort_keys=True)
        new_s = json.dumps(new_schemas.get(name, {}), sort_keys=True)
        if old_s != new_s:
            schema_changed.append(name)

    return ToolsDiff(
        version_changed=old.version != new.version,
        old_version=old.version,
        new_version=new.version,
        added_tools=added,
        removed_tools=removed,
        schema_changed_tools=schema_changed,
    )
