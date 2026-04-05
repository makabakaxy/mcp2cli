from pathlib import Path


def safe_filename(name: str) -> str:
    """Replace characters unsafe for filenames (e.g. '/') with '-'."""
    return name.replace("/", "-")


def skills_path(server_name: str) -> Path:
    """Return the local skills directory for a server."""
    from mcp2cli.constants import SKILLS_DIR
    return SKILLS_DIR / safe_filename(server_name)


def shared_skills_path(server_name: str) -> Path:
    """Return the shared skills directory for a server."""
    from mcp2cli.constants import SHARED_SKILLS_DIR
    return SHARED_SKILLS_DIR / safe_filename(server_name)