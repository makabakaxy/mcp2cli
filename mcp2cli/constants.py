"""Path constants and configuration defaults."""

from pathlib import Path

DATA_DIR = Path.home() / ".agents" / "mcp2cli"
SESSIONS_DIR = DATA_DIR / ".sessions"
TOOLS_DIR = DATA_DIR / "tools"
CLI_DIR = DATA_DIR / "cli"
SKILLS_DIR = DATA_DIR / "skills"
SERVERS_YAML = DATA_DIR / "servers.yaml"
CONFIG_YAML = DATA_DIR / "config.yaml"
DAEMON_PID = DATA_DIR / "daemon.pid"
DAEMON_SOCK = DATA_DIR / "daemon.sock"
DAEMON_LOG = DATA_DIR / "daemon.log"

SHARED_SKILLS_DIR = Path.home() / ".agents" / "skills"

CLIENT_CONFIGS = {
    "claude": {
        "config_path": Path.home() / ".claude.json",
        "skill_dir": Path.home() / ".claude" / "skills",
        "format": "claude_json",
        "server_key": "mcpServers",
    },
    "cursor": {
        "config_path": Path.home() / ".cursor" / "mcp.json",
        "skill_dir": Path.home() / ".cursor" / "skills",
        "format": "cursor_json",
        "server_key": "mcpServers",
    },
    "codex": {
        "config_path": Path.home() / ".codex" / "config.toml",
        "skill_dir": Path.home() / ".codex" / "skills",
        "format": "codex_toml",
        "server_key": "mcp_servers",
    },
}

TEMPLATES_DIR = Path(__file__).parent / "generator" / "templates"
PRESETS_DIR = Path(__file__).parent / "presets"

SESSION_EXPIRY_HOURS = 24

RESERVED_COMMANDS = frozenset({
    "list", "scan", "generate", "validate", "daemon",
    "tools", "call", "convert", "install", "remove",
    "uninstall", "update", "mcp", "skill", "preset",
})
