"""Remote preset index fetching with local cache."""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError

import click
import yaml

from mcp2cli.constants import CONFIG_YAML, DATA_DIR
from mcp2cli.preset.models import PresetEntry, PresetIndex

PRESET_CACHE_DIR = DATA_DIR / ".preset-cache"
INDEX_CACHE = PRESET_CACHE_DIR / "index.json"
INDEX_META = PRESET_CACHE_DIR / "index.meta.json"

DEFAULT_REPO_URL = "https://raw.githubusercontent.com/mcp2cli/mcp2cli-presets/main"
DEFAULT_CACHE_TTL_HOURS = 24
INDEX_TIMEOUT = 5


def _get_config() -> dict:
    """Read preset config from config.yaml."""
    if not CONFIG_YAML.exists():
        return {}
    try:
        data = yaml.safe_load(CONFIG_YAML.read_text(encoding="utf-8"))
        return data.get("preset", {}) if isinstance(data, dict) else {}
    except Exception:
        return {}


def _repo_url() -> str:
    return _get_config().get("repo_url", DEFAULT_REPO_URL)


def _cache_ttl_hours() -> int:
    return _get_config().get("cache_ttl_hours", DEFAULT_CACHE_TTL_HOURS)


def _is_auto_check_enabled() -> bool:
    return _get_config().get("auto_check", True)


def fetch_index(force_refresh: bool = False) -> PresetIndex | None:
    """Fetch the remote index.json with local caching.

    Returns PresetIndex or None if unavailable.
    """
    PRESET_CACHE_DIR.mkdir(parents=True, exist_ok=True)

    # Check cache
    if not force_refresh and INDEX_CACHE.exists() and INDEX_META.exists():
        try:
            meta = json.loads(INDEX_META.read_text(encoding="utf-8"))
            cached_at = datetime.fromisoformat(meta["cached_at"])
            age_hours = (datetime.now(timezone.utc) - cached_at).total_seconds() / 3600
            if age_hours < _cache_ttl_hours():
                data = json.loads(INDEX_CACHE.read_text(encoding="utf-8"))
                return PresetIndex.from_dict(data)
        except Exception:
            pass

    # Fetch from remote
    url = f"{_repo_url()}/index.json"
    etag = None
    if INDEX_META.exists():
        try:
            meta = json.loads(INDEX_META.read_text(encoding="utf-8"))
            etag = meta.get("etag")
        except Exception:
            pass

    try:
        req = Request(url, method="GET")
        if etag:
            req.add_header("If-None-Match", etag)

        with urlopen(req, timeout=INDEX_TIMEOUT) as resp:
            if resp.status == 304:
                # Cache still valid
                _update_cache_timestamp(etag)
                data = json.loads(INDEX_CACHE.read_text(encoding="utf-8"))
                return PresetIndex.from_dict(data)

            body = resp.read().decode("utf-8")
            new_etag = resp.headers.get("ETag")

            # Update cache
            INDEX_CACHE.write_text(body, encoding="utf-8")
            _save_meta(new_etag)

            data = json.loads(body)
            return PresetIndex.from_dict(data)

    except URLError:
        # Network failure — use stale cache if available
        if INDEX_CACHE.exists():
            try:
                data = json.loads(INDEX_CACHE.read_text(encoding="utf-8"))
                return PresetIndex.from_dict(data)
            except Exception:
                pass
        return None
    except Exception:
        return None


def find_preset(server_name: str) -> PresetEntry | None:
    """Find a preset for the given server name."""
    index = fetch_index()
    if index is None:
        return None
    return index.find(server_name)


def _save_meta(etag: str | None) -> None:
    meta = {
        "etag": etag,
        "cached_at": datetime.now(timezone.utc).isoformat(),
    }
    INDEX_META.write_text(json.dumps(meta, indent=2), encoding="utf-8")


def _update_cache_timestamp(etag: str | None) -> None:
    _save_meta(etag)
