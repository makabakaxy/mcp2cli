"""Data models for mcp2cli configuration."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ServerConfig:
    """MCP server configuration extracted from client configs or servers.yaml."""

    name: str
    command: str
    args: list[str] = field(default_factory=list)
    env: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        d: dict = {"command": self.command, "args": self.args}
        if self.env:
            d["env"] = dict(self.env)
        return d


@dataclass
class ConfigSource:
    """Tracks where a server config was found."""

    client: str  # "claude", "cursor", "codex", "servers.yaml"
    config_path: Path
    config_format: str  # "claude_json", "cursor_json", "codex_toml", "servers_yaml"


@dataclass
class ToolInfo:
    """Single MCP tool definition."""

    name: str
    description: str
    input_schema: dict = field(default_factory=dict)


@dataclass
class ToolsJSON:
    """Materialized tools JSON file content."""

    server: str
    version: str | None
    scanned_at: str
    tools: list[ToolInfo] = field(default_factory=list)

    def tool_names(self) -> set[str]:
        return {t.name for t in self.tools}

    def to_dict(self) -> dict:
        return {
            "server": self.server,
            "version": self.version,
            "scanned_at": self.scanned_at,
            "tools": [
                {
                    "name": t.name,
                    "description": t.description,
                    "inputSchema": t.input_schema,
                }
                for t in self.tools
            ],
        }

    @classmethod
    def from_dict(cls, data: dict) -> ToolsJSON:
        tools = [
            ToolInfo(
                name=t["name"],
                description=t.get("description", ""),
                input_schema=t.get("inputSchema", {}),
            )
            for t in data.get("tools", [])
        ]
        return cls(
            server=data["server"],
            version=data.get("version"),
            scanned_at=data.get("scanned_at", ""),
            tools=tools,
        )


@dataclass
class AISearchResult:
    """Result from AI-based MCP server search."""

    found: bool
    server_name: str = ""
    package_name: str = ""
    package_registry: str = ""
    command: str = ""
    args: list[str] = field(default_factory=list)
    env: dict[str, dict] = field(default_factory=dict)
    source_url: str = ""
    error: str = ""
    suggestions: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> AISearchResult:
        return cls(
            found=data.get("found", False),
            server_name=data.get("server_name", ""),
            package_name=data.get("package_name", ""),
            package_registry=data.get("package_registry", ""),
            command=data.get("command", ""),
            args=data.get("args", []),
            env=data.get("env", {}),
            source_url=data.get("source_url", ""),
            error=data.get("error", ""),
            suggestions=data.get("suggestions", []),
        )
