# mcp2cli install 设计文档

本文档是 [0-design-overview.md](0-design-overview.md) 第十一章 `mcp2cli install` 的展开设计。

## 一、功能概述

`mcp2cli install` 是一个一键式安装命令，将 MCP server 的安装、配置和 CLI 生成合并为一步操作。

**核心流程：**

```
mcp2cli install mcp-atlassian
        │
        ▼
┌─ 1. AI 搜索安装信息 ────────────────────┐
│  调用 claude -p，搜索互联网获取：          │
│  - command (如 uvx, npx, node)          │
│  - args (如 ["mcp-atlassian"])          │
│  - env (如 JIRA_URL, JIRA_API_TOKEN)    │
│  - 哪些 env 需要用户填写                  │
└───────────────────┬─────────────────────┘
                    │
                    ▼
┌─ 2. 交互式补全 ────────────────────────┐
│  提示用户输入必需的 env 值：             │
│  JIRA_URL: https://xxx.atlassian.net   │
│  JIRA_API_TOKEN: ****                  │
└───────────────────┬─────────────────────┘
                    │
                    ▼
┌─ 3. 写入三个配置文件 ──────────────────┐
│  ~/.claude.json         ✓ 写入         │
│  ~/.cursor/mcp.json     ✓ 写入         │
│  ~/.codex/config.toml   ⊘ 已存在,跳过   │
└───────────────────┬─────────────────────┘
                    │
                    ▼
┌─ 4. 自动 scan + generate ─────────────┐
│  mcp2cli scan mcp-atlassian            │
│  mcp2cli generate cli mcp-atlassian    │
└────────────────────────────────────────┘
```

## 二、命令接口

### 2.1 基本用法

```bash
mcp2cli install <server-name>
```

### 2.2 完整参数

```bash
mcp2cli install <server-name> [OPTIONS]

Arguments:
  server-name          MCP server 名称（如 mcp-atlassian, playwright）

Options:
  --targets            写入哪些配置文件 (默认: claude,cursor,codex)
                       可选值: claude, cursor, codex, all
                       示例: --targets claude,cursor
  --skip-generate      跳过自动 scan + generate 步骤
  --env KEY=VALUE      预设 env 值，跳过交互式询问（可多次使用）
                       示例: --env JIRA_URL=https://xxx.atlassian.net
  --dry-run            只展示将要写入的内容，不实际修改文件
  --yes                跳过确认提示，直接执行
```

### 2.3 配置文件路径

| 目标 | 配置文件路径 | 格式 |
|------|-------------|------|
| Claude | `~/.claude.json` | JSON (`mcpServers` 字段) |
| Cursor | `~/.cursor/mcp.json` | JSON (`mcpServers` 字段) |
| Codex | `~/.codex/config.toml` | TOML (`[[mcp_servers]]` 表) |

## 三、AI 辅助安装（核心设计）

### 3.1 调用方式

使用 `claude -p` 搜索互联网，获取 MCP server 的安装配置信息：

```bash
claude -p "<install_prompt>" \
  --output-format json \
  --model sonnet \
  --max-turns 5 \
  --allowedTools "WebSearch,WebFetch"
```

**关键设计：**

- 使用 `--allowedTools "WebSearch,WebFetch"` 限制 AI 只能搜索和读取网页，不可执行任何写操作
- AI 通过搜索 GitHub README、npm/PyPI 页面、官方文档等获取安装信息
- 输出结构化 JSON，由程序侧解析和处理

### 3.2 Install Prompt 模板

```
你是 MCP server 安装助手。用户需要安装名为 "{{SERVER_NAME}}" 的 MCP server。

请通过搜索互联网，找到该 MCP server 的安装和配置信息，然后输出一个 JSON 对象。

搜索策略：
1. 搜索 "{{SERVER_NAME}} MCP server" 或 "{{SERVER_NAME}} model context protocol"
2. 查看 GitHub 仓库的 README，找到 MCP 配置示例
3. 查看 npm / PyPI 包页面，确认包名和安装方式

输出格式（严格 JSON）：

```json
{
  "found": true,
  "server_name": "mcp-atlassian",
  "package_name": "mcp-atlassian",
  "package_registry": "pypi",
  "command": "uvx",
  "args": ["mcp-atlassian"],
  "env": {
    "JIRA_URL": {
      "description": "Your Jira instance URL",
      "example": "https://your-company.atlassian.net",
      "required": true,
      "sensitive": false
    },
    "JIRA_API_TOKEN": {
      "description": "Jira API token for authentication",
      "example": "",
      "required": true,
      "sensitive": true
    }
  },
  "source_url": "https://github.com/..."
}
```

字段说明：
- `found`: 是否找到该 MCP server
- `command`: 启动命令（常见: uvx, npx, node, python）
- `args`: 命令参数数组
- `env`: 环境变量定义
  - `required`: 是否必须提供
  - `sensitive`: 是否为敏感信息（如 API Token），用于决定是否在确认界面隐藏显示
- `source_url`: 信息来源 URL，供用户查验

如果找不到该 MCP server，返回：
```json
{
  "found": false,
  "error": "未找到名为 xxx 的 MCP server",
  "suggestions": ["类似名称的 server 列表"]
}
```

注意：
- 只输出 JSON，不要输出任何其他内容
- 优先使用官方文档中的配置格式
- command 优先使用 uvx (Python) 或 npx (Node.js) 等免安装运行器
```

### 3.3 AI 返回结果处理

```
AI 返回 JSON
    │
    ├── found: false
    │   → 输出错误信息 + suggestions
    │   → 退出
    │
    └── found: true
        │
        ▼
    解析 env 定义
        │
        ├── 检查 --env 参数预设值，匹配的直接填入
        │
        └── 剩余 required=true 且未预设的 env
            → 交互式询问用户
            → sensitive=true 的字段使用密码输入模式（不回显）
```

### 3.4 会话续接（信息不全时）

如果 AI 首次搜索信息不完整（如只找到 command 但不确定 env），通过 `--resume` 续接：

```bash
# 首次调用返回 session_id
claude -p "<install_prompt>" --output-format json ...
# → session_id: "abc-123"

# 信息不完整时，追加上下文续接
claude -p "之前的搜索结果缺少 env 配置信息，请尝试搜索 {{SERVER_NAME}} 的环境变量配置要求" \
  --output-format json \
  --resume abc-123
```

最多重试 2 次，仍不完整则使用已获取的信息继续（env 部分可能为空），提示用户后续手动补充。

## 四、配置文件写入

### 4.1 写入流程

```
对每个目标配置文件 (claude, cursor, codex):
    │
    ├── 文件不存在 → 创建文件并写入 server 定义
    │
    ├── 文件存在，server 已定义 → 跳过，打印提示
    │   "⊘ ~/.claude.json: mcp-atlassian already exists, skipped"
    │
    └── 文件存在，server 未定义 → 追加 server 定义
        "✓ ~/.claude.json: mcp-atlassian added"
```

### 4.2 Claude 配置写入 (`~/.claude.json`)

```json
{
  "mcpServers": {
    "mcp-atlassian": {
      "command": "uvx",
      "args": ["mcp-atlassian"],
      "env": {
        "JIRA_URL": "https://your-company.atlassian.net",
        "JIRA_API_TOKEN": "user_provided_token"
      }
    }
  }
}
```

**写入逻辑：**

```python
# 伪代码
config = json.load(claude_json_path) if exists else {}
servers = config.setdefault("mcpServers", {})
if server_name in servers:
    print(f"⊘ {path}: {server_name} already exists, skipped")
    return
servers[server_name] = {
    "command": command,
    "args": args,
    "env": env_values  # 只写入有值的 env
}
json.dump(config, claude_json_path, indent=2)
print(f"✓ {path}: {server_name} added")
```

### 4.3 Cursor 配置写入 (`~/.cursor/mcp.json`)

格式与 Claude 完全相同：

```json
{
  "mcpServers": {
    "mcp-atlassian": {
      "command": "uvx",
      "args": ["mcp-atlassian"],
      "env": {
        "JIRA_URL": "https://your-company.atlassian.net",
        "JIRA_API_TOKEN": "user_provided_token"
      }
    }
  }
}
```

### 4.4 Codex 配置写入 (`~/.codex/config.toml`)

TOML 格式不同于 JSON：

```toml
[[mcp_servers]]
name = "mcp-atlassian"
command = "uvx"
args = ["mcp-atlassian"]

[mcp_servers.env]
JIRA_URL = "https://your-company.atlassian.net"
JIRA_API_TOKEN = "user_provided_token"
```

**写入逻辑：**

```python
# 伪代码
config = toml.load(codex_toml_path) if exists else {}
servers = config.setdefault("mcp_servers", [])
for s in servers:
    if s.get("name") == server_name:
        print(f"⊘ {path}: {server_name} already exists, skipped")
        return
servers.append({
    "name": server_name,
    "command": command,
    "args": args,
    "env": env_values
})
toml.dump(config, codex_toml_path)
print(f"✓ {path}: {server_name} added")
```

### 4.5 写入前确认

默认在写入前展示预览，要求用户确认：

```
The following configuration will be written:

  Server: mcp-atlassian
  Command: uvx mcp-atlassian
  Environment:
    JIRA_URL = https://your-company.atlassian.net
    JIRA_API_TOKEN = ****  (sensitive)

  Targets:
    ~/.claude.json          → will add
    ~/.cursor/mcp.json      → will add
    ~/.codex/config.toml    → already exists, skip

  Source: https://github.com/sooperset/mcp-atlassian

Proceed? [Y/n]
```

使用 `--yes` 跳过此确认。使用 `--dry-run` 则只显示预览不执行。

## 五、自动 scan + generate

### 5.1 流程

写入配置文件后，自动执行：

```
┌─ scan ──────────────────────────────────┐
│  mcp2cli scan mcp-atlassian             │
│  → 启动 MCP server 子进程               │
│  → 获取 tool 列表                       │
│  → 写入 ~/.agents/mcp2cli/tools/        │
│                                         │
│  失败处理：                              │
│  → 打印警告，不阻断后续步骤              │
│  → 提示: "Scan failed. You can retry    │
│     later with: mcp2cli scan ..."       │
└───────────────────┬─────────────────────┘
                    │ 成功
                    ▼
┌─ generate cli ──────────────────────────┐
│  mcp2cli generate cli mcp-atlassian     │
│  → AI 分析 tool 列表                    │
│  → 生成层级命令树 YAML                   │
│                                         │
│  失败处理：同上                           │
└─────────────────────────────────────────┘
```

### 5.2 跳过选项

```bash
# 只写配置文件，不自动 scan/generate
mcp2cli install mcp-atlassian --skip-generate
```

适用场景：用户只想注册 server 到配置中，后续手动控制 scan/generate 时机。

## 六、端到端示例

### 6.1 标准安装流程

```
$ mcp2cli install mcp-atlassian

🔍 Searching for mcp-atlassian installation info...
   Found: mcp-atlassian (PyPI)
   Source: https://github.com/sooperset/mcp-atlassian

📋 Environment variables required:
   JIRA_URL (Your Jira instance URL)
   > https://mycompany.atlassian.net

   JIRA_API_TOKEN (Jira API token, sensitive)
   > ********

   CONFLUENCE_URL (Your Confluence URL, optional)
   > (skip)

📝 Configuration preview:
   Server: mcp-atlassian
   Command: uvx mcp-atlassian
   Env: JIRA_URL, JIRA_API_TOKEN (2 values set)

   Targets:
     ~/.claude.json        → will add
     ~/.cursor/mcp.json    → will add
     ~/.codex/config.toml  → will add

   Proceed? [Y/n] y

✓ ~/.claude.json: mcp-atlassian added
✓ ~/.cursor/mcp.json: mcp-atlassian added
✓ ~/.codex/config.toml: mcp-atlassian added

🔧 Scanning mcp-atlassian...
   Found 65 tools. Written to ~/.agents/mcp2cli/tools/mcp-atlassian.json

🤖 Generating CLI command tree...
   mcp-atlassian
   ├── jira
   │   ├── issue (create, get, search, update, delete, transition)
   │   ├── sprint (create, update, list, issues)
   │   ├── board (list, issues)
   │   └── project (list, issues, components, versions)
   └── confluence
       ├── page (get, create, update, delete, move, children)
       ├── search
       ├── comment (list, add, reply)
       └── attachment (list, upload, download, delete)
   Coverage: 65/65 tools ✓
   Written to ~/.agents/mcp2cli/cli/mcp-atlassian.yaml

✅ Installation complete!
   Next steps:
   - Use: mcp2cli mcp-atlassian jira issue create --help
   - Generate skill: mcp2cli generate skill mcp-atlassian
```

### 6.2 已存在时跳过

```
$ mcp2cli install mcp-atlassian

🔍 Searching for mcp-atlassian installation info...
   Found: mcp-atlassian (PyPI)

📝 Configuration preview:
   Targets:
     ~/.claude.json        → already exists, skip
     ~/.cursor/mcp.json    → already exists, skip
     ~/.codex/config.toml  → will add

   Proceed? [Y/n] y

⊘ ~/.claude.json: mcp-atlassian already exists, skipped
⊘ ~/.cursor/mcp.json: mcp-atlassian already exists, skipped
✓ ~/.codex/config.toml: mcp-atlassian added

🔧 Scanning mcp-atlassian...
   ...
```

### 6.3 找不到 server

```
$ mcp2cli install mcp-jiraa

🔍 Searching for mcp-jiraa installation info...
   ✗ Could not find MCP server "mcp-jiraa"

   Did you mean:
     - mcp-atlassian (includes Jira + Confluence)

   You can also provide config manually:
     mcp2cli install mcp-jiraa --command uvx --args mcp-jiraa
```

### 6.4 预设 env 跳过交互

```
$ mcp2cli install mcp-atlassian \
    --env JIRA_URL=https://mycompany.atlassian.net \
    --env JIRA_API_TOKEN=my_token \
    --yes

🔍 Searching for mcp-atlassian installation info...
   Found: mcp-atlassian (PyPI)

✓ ~/.claude.json: mcp-atlassian added
✓ ~/.cursor/mcp.json: mcp-atlassian added
✓ ~/.codex/config.toml: mcp-atlassian added

🔧 Scanning mcp-atlassian... 65 tools found.
🤖 Generating CLI command tree... 65/65 tools ✓

✅ Installation complete!
```

### 6.5 Dry-run 模式

```
$ mcp2cli install mcp-atlassian --dry-run

🔍 Searching for mcp-atlassian installation info...
   Found: mcp-atlassian (PyPI)

📋 Environment variables required:
   JIRA_URL: > https://mycompany.atlassian.net
   JIRA_API_TOKEN: > ********

📝 [DRY RUN] Would write to:

   ~/.claude.json:
   {
     "mcpServers": {
       "mcp-atlassian": {
         "command": "uvx",
         "args": ["mcp-atlassian"],
         "env": { "JIRA_URL": "...", "JIRA_API_TOKEN": "..." }
       }
     }
   }

   ~/.cursor/mcp.json:
   (same as above)

   ~/.codex/config.toml:
   [[mcp_servers]]
   name = "mcp-atlassian"
   command = "uvx"
   args = ["mcp-atlassian"]
   ...

   No files were modified.
```

## 七、错误处理

| 场景 | 处理方式 |
|------|---------|
| AI 搜索无结果 | 展示 suggestions，提示用户手动指定 `--command` |
| AI 返回非法 JSON | 通过 `--resume` 重试 1 次，仍失败则报错退出 |
| 配置文件无写入权限 | 报错，提示用户检查文件权限 |
| scan 失败（server 无法启动） | 打印警告，提示手动重试，不阻断整体流程 |
| generate 失败 | 打印警告，提示手动重试 |
| 所有目标配置均已存在 | 提示全部跳过，询问是否要 `--force` 覆盖 |

## 八、代码实现位置

```
mcp2cli/
├── main.py                    # 新增 install 子命令
├── installer/
│   ├── __init__.py
│   ├── ai_search.py           # AI 搜索安装信息（claude -p 调用、prompt 构造、JSON 解析）
│   ├── config_writer.py       # 三配置文件写入（Claude/Cursor/Codex 各一个写入函数）
│   └── interactive.py         # 交互式 env 输入（密码模式、可选跳过）
```

## 九、与现有模块的关系

```
mcp2cli install <server>
    │
    ├── installer/ai_search.py     ← 新模块：AI 搜索
    │     调用 claude -p
    │
    ├── installer/config_writer.py ← 新模块：配置写入
    │     读写 ~/.claude.json 等
    │
    ├── installer/interactive.py   ← 新模块：交互输入
    │     getpass / input
    │
    ├── scanner.py                 ← 已有：scan 复用
    │     连接 MCP server → list_tools
    │
    └── generator/cli_gen.py       ← 已有：generate cli 复用
          AI 生成命令映射
```
