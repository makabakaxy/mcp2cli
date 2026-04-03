"""Data models for preset index and manifest."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class PresetEntry:
    """A single entry from index.json."""

    server: str
    latest: str
    versions: list[str]
    description: str
    updated_at: str
    # Kept for backward compat with index v1
    server_version: str | None = None
    tool_count: int = 0

    def resolve_version(self, requested: str | None) -> str:
        """Resolve a requested version to an actual version string.

        Args:
            requested: Version string or None for latest.

        Returns:
            Resolved version string.

        Raises:
            ValueError: If the requested version is not available.
        """
        if requested is None:
            return self.latest

        if requested not in self.versions:
            raise ValueError(
                f"Version '{requested}' not available for {self.server}. "
                f"Available: {', '.join(self.versions)}"
            )
        return requested

    @classmethod
    def from_dict(cls, data: dict) -> PresetEntry:
        # Support both index v1 (server_version) and v2 (latest + versions)
        server = data["server"]
        server_version = data.get("server_version")

        if "latest" in data:
            # v2 format
            latest = data["latest"]
            versions = data.get("versions", [latest])
        elif server_version:
            # v1 format — synthesize v2 fields
            latest = server_version
            versions = [server_version]
        else:
            latest = ""
            versions = []

        return cls(
            server=server,
            latest=latest,
            versions=versions,
            description=data.get("description", ""),
            updated_at=data.get("updated_at", ""),
            server_version=server_version,
            tool_count=data.get("tool_count", 0),
        )


@dataclass
class PresetIndex:
    """Full index.json content."""

    version: int
    updated_at: str
    presets: list[PresetEntry] = field(default_factory=list)

    def find(self, server_name: str) -> PresetEntry | None:
        return next((p for p in self.presets if p.server == server_name), None)

    @classmethod
    def from_dict(cls, data: dict) -> PresetIndex:
        presets = [PresetEntry.from_dict(p) for p in data.get("presets", [])]
        return cls(
            version=data.get("version", 1),
            updated_at=data.get("updated_at", ""),
            presets=presets,
        )


@dataclass
class Manifest:
    """manifest.json for a single preset."""

    server: str
    server_version: str | None
    tool_count: int
    cli_hash: str
    generated_at: str
    generated_by: str
    files: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> Manifest:
        return cls(
            server=data["server"],
            server_version=data.get("server_version"),
            tool_count=data.get("tool_count", 0),
            cli_hash=data.get("cli_hash", ""),
            generated_at=data.get("generated_at", ""),
            generated_by=data.get("generated_by", "preset"),
            files=data.get("files", []),
        )
