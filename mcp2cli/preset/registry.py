"""Remote preset index fetching."""

from __future__ import annotations

import json
from urllib.request import Request, urlopen
from urllib.error import URLError

import yaml

from mcp2cli.constants import CONFIG_YAML
from mcp2cli.preset.models import PresetIndex

DEFAULT_REPO = "https://github.com/makabakaxy/mcp2cli"
INDEX_TIMEOUT = 5


# ---------------------------------------------------------------------------
# Config helpers
# ---------------------------------------------------------------------------

def _get_config() -> dict:
    """Read preset config from config.yaml."""
    if not CONFIG_YAML.exists():
        return {}
    try:
        data = yaml.safe_load(CONFIG_YAML.read_text(encoding="utf-8"))
        return data.get("preset", {}) if isinstance(data, dict) else {}
    except Exception:
        return {}


def _repo() -> str:
    return _get_config().get("repo", DEFAULT_REPO)


def _is_auto_check_enabled() -> bool:
    return _get_config().get("auto_check", True)


# ---------------------------------------------------------------------------
# URL derivation
# ---------------------------------------------------------------------------

def _parse_github_repo(repo_url: str) -> tuple[str, str]:
    """Parse a GitHub repo URL or SSH string into (owner, repo_name).

    Supports:
      https://github.com/owner/repo
      https://github.com/owner/repo.git
      git@github.com:owner/repo.git
    """
    url = repo_url.strip().rstrip("/")
    if url.startswith("git@github.com:"):
        path = url[len("git@github.com:"):]
    elif "github.com/" in url:
        path = url.split("github.com/", 1)[1]
    else:
        raise ValueError(f"Cannot parse GitHub repo URL: {repo_url!r}")

    path = path.removesuffix(".git")
    parts = path.split("/", 1)
    if len(parts) != 2 or not parts[0] or not parts[1]:
        raise ValueError(f"Cannot parse owner/repo from: {repo_url!r}")
    return parts[0], parts[1]


def _raw_base() -> str:
    """Raw-content base URL for the presets directory."""
    owner, name = _parse_github_repo(_repo())
    return f"https://raw.githubusercontent.com/{owner}/{name}/main/presets"


def _ssh_url() -> str:
    """SSH clone URL for the repo."""
    owner, name = _parse_github_repo(_repo())
    return f"git@github.com:{owner}/{name}.git"


def _pr_url(branch: str) -> str:
    """GitHub compare URL for creating a PR from *branch*."""
    owner, name = _parse_github_repo(_repo())
    return f"https://github.com/{owner}/{name}/compare/{branch}?expand=1"


# ---------------------------------------------------------------------------
# Index fetching
# ---------------------------------------------------------------------------

def fetch_index() -> PresetIndex | None:
    """Fetch the remote index.json.

    Returns PresetIndex or None if unavailable.
    """
    url = f"{_raw_base()}/index.json"

    try:
        req = Request(url, method="GET")
        with urlopen(req, timeout=INDEX_TIMEOUT) as resp:
            body = resp.read().decode("utf-8")
            data = json.loads(body)
            return PresetIndex.from_dict(data)
    except (URLError, Exception):
        return None


def find_preset(server_name: str) -> "PresetEntry | None":  # noqa: F821
    """Find a preset for the given server name."""
    index = fetch_index()
    if index is None:
        return None
    return index.find(server_name)
