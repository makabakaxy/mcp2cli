# mcp2cli convert 设计文档

本文档是 [0.0-design-overview.md](0.0-design-overview.md) 第十一章 `mcp2cli convert` 的展开设计。

## 一、功能概述

`mcp2cli convert` 将**已配置在 Claude/Cursor/Codex 中的 MCP server** 转换为 skill，并在原客户端配置中关闭该 MCP server。转换后，agent 通过 skill + CLI 调用 MCP server（由 mcp2cli daemon 管理），而非直接通过 MCP 协议通信。

**核心收益**：将 agent 每轮对话中 MCP tool schema 的 token 消耗从 ~5000 降至 ~600（节省 75%+）。

**与 `install` 的区别**：

| 维度 | `mcp2cli install` | `mcp2cli convert` |
|------|-------------------|-------------------|
| 适用场景 | 系统中尚未配置的新 server | 已在 Claude/Cursor/Codex 中配置好的 server |
| 配置来源 | AI 搜索互联网 | 读取已有客户端配置文件 |
| 环境变量 | 交互式提示用户输入 | 从已有配置中提取（无需交互） |
| AI 依赖 | 第一步需要 AI（claude -p） | 第一步无需 AI（纯配置解析） |
| 写 servers.yaml | 是 | 是（复用同一代码） |
| Pipeline | scan → cli → skill → sync | 相同（复用同一 runner） |
| 关闭原配置 | 无（没有原配置） | 在客户端配置中设置 disabled |

## 二、命令接口

```bash
mcp2cli convert <server-name> [OPTIONS]

Arguments:
  server-name          已配置在 Claude/Cursor/Codex 中的 MCP server 名称

Options:
  --source SOURCE      指定从哪个配置读取 (claude, cursor, codex, auto)
                       默认 auto：按 claude → cursor → codex 顺序搜索
  --skip-disable       不关闭原始客户端配置中的 server
  --skill-targets      skill sync 目标客户端 (默认: claude,cursor,codex)
                       可选值: claude, cursor, codex, all
  --dry-run            只展示操作预览，不实际修改
  --yes                跳过确认提示
  --force              servers.yaml 中已存在时覆盖
```

## 三、完整流程

```
mcp2cli convert mcp-atlassian
        │
        ▼
┌─ Step 0: 定位并提取配置 ──────────────────────────┐
│  1. 搜索配置源（顺序: claude → cursor → codex）    │
│  2. 提取 command, args, env                       │
│  3. 记录在哪些配置文件中找到了该 server             │
│  4. 若已在 servers.yaml → 提示（--force 可覆盖）   │
└───────────────────┬───────────────────────────────┘
                    │
                    ▼
┌─ Step 1: 写入 servers.yaml ──────────────────────┐
│  复用 installer/servers_writer.py                 │
│  将提取的配置写入 ~/.agents/mcp2cli/servers.yaml   │
└───────────────────┬───────────────────────────────┘
                    │
                    ▼
┌─ Step 2-5: Pipeline（复用已有模块）───────────────┐
│  Step 2: scan        → scanner.py                │
│  Step 3: generate cli → generator/cli_gen.py     │
│  Step 4: generate skill → generator/skill_gen.py │
│  Step 5: skill sync  → installer/skill_sync.py   │
└───────────────────┬───────────────────────────────┘
                    │
                    ▼
┌─ Step 6: 关闭原始配置 ───────────────────────────┐
│  在所有包含该 server 的客户端配置中设置 disabled   │
│  仅在前面所有步骤成功后才执行                      │
│  Claude JSON:  "disabled": true                  │
│  Cursor JSON:  "disabled": true                  │
│  Codex TOML:   disabled = true                   │
└──────────────────────────────────────────────────┘
```

### 3.1 Step 0 配置提取

```
mcp2cli convert mcp-atlassian --source auto
        │
        ▼
┌─ 1. 枚举配置源 ──────────────────────────────────┐
│  调用 config/reader.py 读取所有配置文件：          │
│  - ~/.claude.json                                │
│  - claude_desktop_config.json（多个搜索路径）     │
│  - ~/.cursor/mcp.json                            │
│  - ~/.codex/config.toml                          │
│  - ~/.agents/mcp2cli/servers.yaml                │
└───────────────────┬──────────────────────────────┘
                    │
                    ▼
┌─ 2. 查找目标 server ─────────────────────────────┐
│  在各配置的 mcpServers / mcp_servers 中           │
│  查找 key == server_name 的条目                   │
│                                                  │
│  --source auto: 按优先级匹配第一个                │
│  --source claude: 只搜索 Claude 配置              │
│                                                  │
│  找不到 → 报错 + 列出可用 server + 提示 list      │
└───────────────────┬──────────────────────────────┘
                    │
                    ▼
┌─ 3. 提取配置 ────────────────────────────────────┐
│  从匹配的配置条目中提取：                          │
│  - command: str (如 "uvx", "npx")                │
│  - args: list[str] (如 ["mcp-atlassian"])        │
│  - env: dict[str, str] (环境变量键值对)           │
│                                                  │
│  同时记录所有包含该 server 的配置文件路径           │
│  （用于后续 disable 步骤）                        │
└───────────────────┬──────────────────────────────┘
                    │
                    ▼
┌─ 4. 检查 servers.yaml ──────────────────────────┐
│  该 server 是否已存在于 servers.yaml ？            │
│                                                  │
│  已存在 且 未指定 --force:                        │
│    → 打印提示 "mcp-atlassian already exists in    │
│      servers.yaml, skipping write"               │
│    → 跳过 Step 1，继续 pipeline                  │
│                                                  │
│  已存在 且 指定 --force:                          │
│    → 覆盖写入                                    │
│                                                  │
│  不存在:                                         │
│    → 正常写入                                    │
└──────────────────────────────────────────────────┘
```

### 3.2 Step 6 关闭原始配置

**策略：disable 而非 remove**。安全可逆，用户可随时手动恢复。

```
disable_in_all_sources(server_name, found_sources)
        │
        ├── 遍历 found_sources
        │
        ├── ~/.claude.json (format: claude_json)
        │   → 读取 JSON
        │   → mcpServers.mcp-atlassian.disabled = true
        │   → 写回（原子写入）
        │
        ├── ~/.cursor/mcp.json (format: cursor_json)
        │   → 读取 JSON
        │   → mcpServers.mcp-atlassian.disabled = true
        │   → 写回（原子写入）
        │
        └── ~/.codex/config.toml (format: codex_toml)
            → 读取 TOML (tomlkit，保留注释)
            → mcp_servers.mcp-atlassian.disabled = true
            → 写回（原子写入）
```

**各客户端 disable 格式：**

Claude (`~/.claude.json`)：

```json
{
  "mcpServers": {
    "mcp-atlassian": {
      "command": "uvx",
      "args": ["mcp-atlassian"],
      "env": { "JIRA_URL": "..." },
      "disabled": true
    }
  }
}
```

Cursor (`~/.cursor/mcp.json`)：

```json
{
  "mcpServers": {
    "mcp-atlassian": {
      "command": "uvx",
      "args": ["mcp-atlassian"],
      "disabled": true
    }
  }
}
```

Codex (`~/.codex/config.toml`)：

```toml
[mcp_servers.mcp-atlassian]
command = "uvx"
args = ["mcp-atlassian"]
disabled = true
```

**写入安全措施：**

- 读取整个文件 → 仅修改目标 server 条目 → 原子写入（写临时文件 + `os.rename`）
- TOML 使用 `tomlkit`（保留注释和格式）
- JSON 使用 `json.dump(indent=2)` 保持格式
- 写入前备份原文件内容（在内存中），写入失败时可恢复

## 四、Pipeline 定义

复用 `installer/pipeline.py` 的 Step dataclass 和 runner。

```python
pipeline: list[Step] = [
    Step(
        name="extract-config",
        run=lambda: extract_and_write(server_name, source, force),
        retry_cmd=f"mcp2cli convert {server_name}",
    ),
    Step(
        name="scan",
        run=lambda: run_scan(server_name),
        retry_cmd=f"mcp2cli scan {server_name}",
        depends_on=["extract-config"],
    ),
    Step(
        name="generate-cli",
        run=lambda: run_generate_cli(server_name),
        retry_cmd=f"mcp2cli generate cli {server_name}",
        depends_on=["scan"],
    ),
    Step(
        name="generate-skill",
        run=lambda: run_generate_skill(server_name),
        retry_cmd=f"mcp2cli generate skill {server_name}",
        depends_on=["generate-cli"],
    ),
    Step(
        name="skill-sync",
        run=lambda: run_skill_sync(server_name),
        retry_cmd=f"mcp2cli skill sync {server_name}",
        depends_on=["generate-skill"],
    ),
    Step(
        name="disable-in-clients",
        run=lambda: disable_in_all_sources(server_name, found_sources),
        retry_cmd='(手动在配置文件中添加 "disabled": true)',
        depends_on=["skill-sync"],  # 仅在全部成功后才关闭
    ),
]
```

**设计说明**：

- `disable-in-clients` 依赖 `skill-sync`，确保只有在 skill 完全就绪后才关闭原配置
- 使用 `--skip-disable` 时不添加最后一个 Step
- 每步失败只打警告，不中止 pipeline（除非后续步骤有依赖）

## 五、代码结构

```
mcp2cli/
├── main.py                          # 新增 convert 子命令
├── converter/                       # 新增包
│   ├── __init__.py
│   ├── config_extractor.py          # 从客户端配置中提取 server 配置
│   ├── config_disabler.py           # 在客户端配置中设置 disabled
│   └── pipeline.py                  # convert 专属 pipeline 组装
├── installer/                       # 已有，复用
│   ├── pipeline.py                  # Step dataclass + runner（共享）
│   ├── servers_writer.py            # 写入 servers.yaml（共享）
│   └── skill_sync.py               # skill 软链接（共享）
├── config/
│   └── reader.py                    # 已有，读取所有配置源
```

### 模块职责

**`converter/config_extractor.py`**：

```python
def extract_server_config(
    server_name: str,
    source: str = "auto",
) -> tuple[ServerConfig, list[ConfigSource]]:
    """
    从客户端配置文件中提取 MCP server 配置。

    Args:
        server_name: MCP server 名称
        source: 配置来源 ("auto", "claude", "cursor", "codex")

    Returns:
        (ServerConfig, [ConfigSource, ...])
        ServerConfig 包含 command, args, env
        ConfigSource 列表记录所有包含该 server 的配置文件路径和格式

    Raises:
        ServerNotFoundError: 在任何配置中都找不到该 server
    """
```

**`converter/config_disabler.py`**：

```python
def disable_server(
    server_name: str,
    config_path: Path,
    config_format: str,  # "claude_json" | "cursor_json" | "codex_toml"
) -> bool:
    """
    在客户端配置文件中设置 server 为 disabled。

    Returns:
        True 如果成功 disable，False 如果失败（权限等问题）
    """

def disable_in_all_sources(
    server_name: str,
    sources: list[ConfigSource],
) -> bool:
    """
    在所有包含该 server 的配置文件中设置 disabled。

    Returns:
        True 如果全部成功
    """
```

**`converter/pipeline.py`**：

```python
def build_convert_pipeline(
    server_name: str,
    source: str,
    force: bool,
    skip_disable: bool,
    found_sources: list[ConfigSource],
) -> list[Step]:
    """组装 convert 专属 pipeline。"""
```

## 六、错误处理

| 场景 | 处理方式 |
|------|---------|
| server 在任何配置中都找不到 | 报错，列出可用 server，提示用 `mcp2cli list` 查看 |
| server 在多个配置中都有 | 用第一个匹配的提取配置，disable 时关闭**所有**包含它的配置 |
| server 已在 servers.yaml 中 | 提示已存在，无 `--force` 则跳过写入，继续 pipeline |
| 配置文件无写入权限 | disable 步骤报警告，不阻断整体流程，提示手动添加 disabled |
| pipeline 中途失败 | 不执行 disable 步骤（避免关闭原配置却没有可用 skill） |
| server 已被 disabled | 跳过该配置的 disable，打印提示 "Already disabled in [path]" |
| 客户端配置文件不存在 | 跳过该客户端，不报错 |
| `--dry-run` 模式 | 展示所有计划操作，不修改任何文件 |

## 七、端到端示例

### 7.1 标准转换流程

```
$ mcp2cli convert mcp-atlassian

🔍 Finding mcp-atlassian in config sources...
   Found in: ~/.claude.json (claude:global)
   Found in: ~/.cursor/mcp.json (cursor)

📋 Extracted config from ~/.claude.json:
   command: uvx
   args: [mcp-atlassian]
   env: JIRA_URL, JIRA_API_TOKEN (2 vars)

📝 Will write to ~/.agents/mcp2cli/servers.yaml:
   mcp-atlassian:
     command: uvx
     args: [mcp-atlassian]
     env: JIRA_URL, JIRA_API_TOKEN

   Proceed? [Y/n] y

✓ servers.yaml: mcp-atlassian added

🔧 Scanning mcp-atlassian... 65 tools found
🤖 Generating CLI command tree... 65/65 tools ✓
🧩 Generating skill definitions... ✓
🔗 Syncing skill...
   ~/.claude/skills/mcp-atlassian  ✓
   ~/.cursor/skills/mcp-atlassian  ✓
   ~/.codex/skills/mcp-atlassian   ✓

🔒 Disabling MCP server in original configs...
   ~/.claude.json: mcp-atlassian disabled ✓
   ~/.cursor/mcp.json: mcp-atlassian disabled ✓

✅ Convert complete!
   MCP server now managed by mcp2cli daemon
   Skills synced to Claude Code, Cursor, Codex
   Original MCP config disabled (can re-enable manually)
```

### 7.2 找不到 server

```
$ mcp2cli convert mcp-jiraa

🔍 Finding mcp-jiraa in config sources...
   ✗ Server "mcp-jiraa" not found in any config source.

   Available MCP servers:
     mcp-atlassian    (claude:global, cursor)
     playwright       (claude:project)

   Use `mcp2cli list` to see all configured servers.
   Use `mcp2cli install mcp-jiraa` to install a new server.
```

### 7.3 servers.yaml 已存在

```
$ mcp2cli convert mcp-atlassian

🔍 Finding mcp-atlassian in config sources...
   Found in: ~/.claude.json (claude:global)

⚠ mcp-atlassian already exists in servers.yaml, skipping write.
   Use --force to overwrite.

🔧 Scanning mcp-atlassian... 65 tools found
🤖 Generating CLI command tree... 65/65 tools ✓
🧩 Generating skill definitions... ✓
🔗 Syncing skill... ✓

🔒 Disabling MCP server in original configs...
   ~/.claude.json: mcp-atlassian disabled ✓

✅ Convert complete!
```

### 7.4 Dry-run 模式

```
$ mcp2cli convert mcp-atlassian --dry-run

🔍 Finding mcp-atlassian in config sources...
   Found in: ~/.claude.json (claude:global)
   Found in: ~/.cursor/mcp.json (cursor)

📋 Extracted config from ~/.claude.json:
   command: uvx
   args: [mcp-atlassian]
   env: JIRA_URL, JIRA_API_TOKEN (2 vars)

[DRY RUN] Would write to ~/.agents/mcp2cli/servers.yaml:
   mcp-atlassian:
     command: uvx
     args: [mcp-atlassian]
     env: JIRA_URL, JIRA_API_TOKEN

[DRY RUN] Would execute pipeline:
   1. scan mcp-atlassian
   2. generate cli mcp-atlassian
   3. generate skill mcp-atlassian
   4. skill sync mcp-atlassian

[DRY RUN] Would disable in:
   ~/.claude.json: set mcp-atlassian.disabled = true
   ~/.cursor/mcp.json: set mcp-atlassian.disabled = true

No files were modified.
```

### 7.5 跳过 disable

```
$ mcp2cli convert mcp-atlassian --skip-disable --yes

✓ servers.yaml: mcp-atlassian added
🔧 Scanning mcp-atlassian... 65 tools found
🤖 Generating CLI command tree... 65/65 tools ✓
🧩 Generating skill definitions... ✓
🔗 Syncing skill... claude ✓  cursor ✓  codex ✓

✅ Convert complete!
   Original MCP config was NOT disabled (--skip-disable).
```

## 八、与现有模块的关系

```
mcp2cli convert <server>
    │
    ├── converter/config_extractor.py
    │     调用 config/reader.py 枚举配置
    │     提取 server 配置 + 记录来源
    │
    ├── installer/servers_writer.py    ← 复用
    │     写入 servers.yaml
    │
    ├── installer/pipeline.py          ← 复用 Step + runner
    │
    ├── scanner.py                     ← 复用
    ├── generator/cli_gen.py           ← 复用
    ├── generator/skill_gen.py         ← 复用
    ├── installer/skill_sync.py        ← 复用
    │
    └── converter/config_disabler.py
          在客户端配置中设置 disabled
```
