"""Shared file operation utilities."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import yaml


# ---------------------------------------------------------------------------
# Atomic file writes
# ---------------------------------------------------------------------------

def atomic_write_text(path: Path, content: str) -> None:
    """Write text to *path* atomically via a temp file."""
    fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with open(fd, "w", encoding="utf-8") as f:
            f.write(content)
        Path(tmp).replace(path)
    except Exception:
        Path(tmp).unlink(missing_ok=True)
        raise


def atomic_write_json(path: Path, data: dict) -> None:
    """Write *data* as indented JSON to *path* atomically."""
    content = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    atomic_write_text(path, content)


# ---------------------------------------------------------------------------
# YAML frontmatter helpers
# ---------------------------------------------------------------------------

def parse_frontmatter(text: str) -> dict | None:
    """Parse YAML frontmatter from markdown text.

    Returns the parsed dict, or None if no valid frontmatter is present.
    """
    if not text.startswith("---"):
        return None
    end = text.find("---", 3)
    if end == -1:
        return None
    try:
        result = yaml.safe_load(text[3:end])
        return result if isinstance(result, dict) else None
    except yaml.YAMLError:
        return None


def strip_frontmatter(text: str) -> str:
    """Return the body of a markdown file with frontmatter removed."""
    if not text.startswith("---"):
        return text
    end = text.find("---", 3)
    if end == -1:
        return text
    return text[end + 3:].strip()


# ---------------------------------------------------------------------------
# Skill directory helpers
# ---------------------------------------------------------------------------

def ensure_users_dir(skill_dir: Path) -> None:
    """Create the users/ subdirectory with placeholder files if absent.

    Idempotent — safe to call even when the directory already exists.
    """
    users_dir = skill_dir / "users"
    if users_dir.exists():
        return

    users_dir.mkdir(parents=True, exist_ok=True)
    (users_dir / ".gitkeep").touch()

    users_skill = users_dir / "skill.md"
    if not users_skill.exists():
        users_skill.write_text(
            "# User Notes\n\nAdd your custom workflows and tips here.\n"
            "This file is never overwritten by mcp2cli generate/update.\n",
            encoding="utf-8",
        )
