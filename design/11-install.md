# mcp2cli install 设计文档

本文档是 [0.0-design-overview.md](0.0-design-overview.md) 第十一章 `mcp2cli install` 的展开设计。

## 一、功能概述

本章涉及三个命令：

- **`mcp2cli mcp install`**：安装 MCP server（AI 搜索配置 → 交互补全 → 写入 `~/.agents/mcp2cli/servers.yaml`）
- **`mcp2cli skill sync`**：将已生成的 skill 文件软链接到 Claude、Cursor、Codex 的 skill 目录，使 agent 能够发现并加载它
- **`mcp2cli install`**：一键全流程，内部依次执行 `mcp install` → scan → generate cli → generate skill → `skill sync`

**命令职责分工：**

| 命令 | 职责 |
|------|------|
| `mcp2cli mcp install` | 安装 MCP server package，写入 `~/.agents/mcp2cli/servers.yaml` |
| `mcp2cli skill sync` | 将 skill 软链接到各 AI 客户端目录，agent 就能用 |
| `mcp2cli install` | 完整流程：mcp install → scan → generate cli → generate skill → skill sync |

### mcp2cli mcp install 流程

```
mcp2cli mcp install mcp-atlassian
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
┌─ 3. 安装 MCP server package ──────────┐
│  根据 command 类型执行预安装：           │
│  uvx  → uvx install mcp-atlassian      │
│  npx  → npm install -g <package>       │
│  node → 检查路径/提示用户手动安装        │
│                                        │
│  失败处理：打印警告，继续写入配置         │
│  （daemon 启动时会自动安装）             │
└───────────────────┬─────────────────────┘
                    │
                    ▼
┌─ 4. 写入 servers.yaml ─────────────────┐
│  ~/.agents/mcp2cli/servers.yaml        │
│                                        │
│  servers:                              │
│    mcp-atlassian:        ✓ 写入        │
│      command: uvx                      │
│      args: [mcp-atlassian]             │
│      env:                              │
│        JIRA_URL: https://...           │
│        JIRA_API_TOKEN: ...             │
└────────────────────────────────────────┘
```

### mcp2cli skill sync 流程

```
mcp2cli skill sync mcp-atlassian
        │
        ▼
┌─ 1. 检查 skill 文件是否已生成 ──────────┐
│  ~/.agents/mcp2cli/skills/mcp-atlassian/│
│  ├── SKILL.md   ✓ 存在                 │
│  ├── reference/ ✓ 存在                 │
│  └── examples/  ✓ 存在                 │
└───────────────────┬─────────────────────┘
                    │
                    ▼
┌─ 2. 创建/更新软链接 ────────────────────┐
│  Claude Code:                          │
│    ~/.claude/skills/mcp-atlassian      │
│      → ~/.agents/mcp2cli/skills/       │
│         mcp-atlassian/                 │
│                                        │
│  Cursor:                               │
│    ~/.cursor/skills/mcp-atlassian      │
│      → ~/.agents/mcp2cli/skills/       │
│         mcp-atlassian/                 │
│                                        │
│  Codex:                                │
│    ~/.codex/skills/mcp-atlassian       │
│      → ~/.agents/mcp2cli/skills/       │
│         mcp-atlassian/                 │
└────────────────────────────────────────┘
```

### mcp2cli install 流程

```
mcp2cli install mcp-atlassian
        │
        ▼
┌─ Step Pipeline ────────────────────────┐
│                                        │
│  Step 0: mcp install                   │
│    mcp2cli mcp install mcp-atlassian   │
│    (AI 搜索 + 交互补全 + 安装 +        │
│     写 servers.yaml)                   │
│    失败 → 警告 + 跳过后续步骤           │
│         │ 成功                          │
│         ▼                              │
│  Step 1: scan                          │
│    mcp2cli scan mcp-atlassian          │
│    失败 → 警告 + 跳过后续步骤           │
│         │ 成功                          │
│         ▼                              │
│  Step 2: generate cli                  │
│    mcp2cli generate cli mcp-atlassian  │
│    失败 → 警告 + 跳过后续步骤           │
│         │ 成功                          │
│         ▼                              │
│  Step 3: generate skill                │
│    mcp2cli generate skill mcp-atlassian│
│    失败 → 警告 + 跳过后续步骤           │
│         │ 成功                          │
│         ▼                              │
│  Step 4: skill sync                    │
│    mcp2cli skill sync mcp-atlassian    │
│    失败 → 警告                          │
│                                        │
└────────────────────────────────────────┘
```

## 二、命令接口

### 2.1 mcp2cli mcp install（安装并注册 MCP server）

```bash
mcp2cli mcp install <server-name> [OPTIONS]

Arguments:
  server-name          MCP server 名称（如 mcp-atlassian, playwright）

Options:
  --env KEY=VALUE      预设 env 值，跳过交互式询问（可多次使用）
                       示例: --env JIRA_URL=https://xxx.atlassian.net
  --skip-install       跳过 package 安装步骤，只写 servers.yaml
  --dry-run            只展示将要执行的操作，不实际修改文件
  --yes                跳过确认提示，直接执行
```

写入目标：`~/.agents/mcp2cli/servers.yaml`（daemon 配置文件，格式见下文）。

### 2.2 mcp2cli skill sync（同步 skill 到各 AI 客户端）

```bash
mcp2cli skill sync [server-name] [OPTIONS]

Arguments:
  server-name          要同步的 server 名称（如 mcp-atlassian）
                       省略则同步所有已生成 skill 的 server

Options:
  --targets            同步到哪些客户端 (默认: claude,cursor,codex)
                       可选值: claude, cursor, codex, all
  --dry-run            只展示将要创建的软链接，不实际操作
  --force              覆盖已存在的软链接（默认跳过）
```

**各客户端 skill 目录：**

| 客户端 | Skill 目录 |
|--------|-----------|
| Claude Code | `~/.claude/skills/<server>/` |
| Cursor | `~/.cursor/skills/<server>/` |
| Codex | `~/.codex/skills/<server>/` |

所有软链接均指向 `~/.agents/mcp2cli/skills/<server>/`（实际存储位置）。

### 2.3 mcp2cli install（一键全流程）

```bash
mcp2cli install <server-name> [OPTIONS]

Arguments:
  server-name          MCP server 名称（如 mcp-atlassian, playwright）

Options:
  --env KEY=VALUE      同 mcp install，透传给 mcp install 阶段
  --skill-targets      skill sync 的目标客户端 (默认: claude,cursor,codex)
  --dry-run            只展示将要写入的内容，不实际修改文件（不执行 pipeline）
  --yes                跳过确认提示，直接执行
  --skip-generate      跳过 pipeline（等价于直接使用 mcp2cli mcp install）
```

### 2.4 servers.yaml 格式

`mcp2cli mcp install` 的写入目标，由 daemon 启动 MCP server 时读取：

```yaml
# ~/.agents/mcp2cli/servers.yaml
servers:
  mcp-atlassian:
    command: uvx
    args: [mcp-atlassian]
    env:
      JIRA_URL: https://your-company.atlassian.net
      JIRA_API_TOKEN: user_provided_token

  playwright:
    command: npx
    args: [playwright-mcp]
    env: {}
```

**写入逻辑：**
- server 已存在 → 跳过，打印提示（`--force` 可覆盖）
- server 不存在 → 追加到 `servers` 字典

## 三、AI 辅助安装（核心设计）

### 3.1 调用方式

使用 `claude -p` 搜索互联网，获取 MCP server 的安装配置信息：

```bash
claude -p "<install_prompt>" --output-format json
```

**关键设计：**

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

## 四、写入前确认

默认在执行前展示预览，要求用户确认：

```
The following will be written to ~/.agents/mcp2cli/servers.yaml:

  mcp-atlassian:
    command: uvx mcp-atlassian
    env:
      JIRA_URL = https://your-company.atlassian.net
      JIRA_API_TOKEN = ****  (sensitive)

  Source: https://github.com/sooperset/mcp-atlassian

Proceed? [Y/n]
```

使用 `--yes` 跳过此确认。使用 `--dry-run` 则只显示预览不执行。

## 五、Step Pipeline（install 专属）

`mcp2cli install` 通过统一的 Step Pipeline 依次执行 mcp install → scan → generate cli → generate skill → skill sync。

### 5.1 Step 数据结构

```python
@dataclass
class Step:
    name: str           # 步骤名，用于日志和错误信息
    run: Callable       # 执行函数，返回 bool（是否成功）
    retry_cmd: str      # 失败时提示用户的手动重试命令
    depends_on: list[str] = field(default_factory=list)
    # depends_on 列表中任意一步失败，本步自动跳过
```

### 5.2 Pipeline 定义与 Runner

```python
pipeline: list[Step] = [
    Step(
        name="mcp-install",
        run=lambda: run_mcp_install(server_name),
        retry_cmd=f"mcp2cli mcp install {server_name}",
    ),
    Step(
        name="scan",
        run=lambda: run_scan(server_name),
        retry_cmd=f"mcp2cli scan {server_name}",
        depends_on=["mcp-install"],   # mcp install 失败则跳过
    ),
    Step(
        name="generate-cli",
        run=lambda: run_generate_cli(server_name),
        retry_cmd=f"mcp2cli generate cli {server_name}",
        depends_on=["scan"],          # scan 失败则跳过
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
]

# Runner（无需 reduce/chain，for 循环 + 结构化 Step 即是最优平衡）
results: dict[str, bool] = {}
for step in pipeline:
    if any(not results.get(dep) for dep in step.depends_on):
        warn(f"Skipping {step.name}: dependency failed")
        results[step.name] = False
        continue

    ok = step.run()
    results[step.name] = ok
    if not ok:
        warn(f"{step.name} failed. Retry later: {step.retry_cmd}")
        # 不 break，让后续无依赖的步骤继续执行
```

**设计说明**：
- `depends_on` 让依赖关系声明在数据里而非散落在 if-else 中
- 每步失败只打警告，不中止 pipeline（除非后续步骤有依赖）
- Runner 不感知具体步骤内容，仅负责调度和错误收集

### 5.3 跳过 Pipeline

```bash
# 只安装 MCP server，等价于直接用 mcp2cli mcp install
mcp2cli install mcp-atlassian --skip-generate
```

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

📝 Will write to ~/.agents/mcp2cli/servers.yaml:
   mcp-atlassian:
     command: uvx mcp-atlassian
     env: JIRA_URL, JIRA_API_TOKEN (2 values set)

   Proceed? [Y/n] y

✓ servers.yaml: mcp-atlassian added

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

🧩 Generating skill definitions...
   Written to ~/.agents/mcp2cli/skills/mcp-atlassian/

🔗 Syncing skill to AI clients...
   ✓ ~/.claude/skills/mcp-atlassian  → ~/.agents/mcp2cli/skills/mcp-atlassian/
   ✓ ~/.cursor/skills/mcp-atlassian  → ~/.agents/mcp2cli/skills/mcp-atlassian/
   ✓ ~/.codex/skills/mcp-atlassian   → ~/.agents/mcp2cli/skills/mcp-atlassian/

✅ Installation complete!
   Next steps:
   - Use CLI: mcp2cli mcp-atlassian jira issue create --help
   - Skill is now available in Claude Code, Cursor, and Codex
```

### 6.2 已存在时跳过

```
$ mcp2cli install mcp-atlassian

🔍 Searching for mcp-atlassian installation info...
   Found: mcp-atlassian (PyPI)

📝 Will write to ~/.agents/mcp2cli/servers.yaml:
   ⊘ mcp-atlassian already exists, skipped

   Proceed with pipeline anyway? [Y/n] y

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
     mcp2cli mcp install mcp-jiraa --command uvx --args mcp-jiraa
```

### 6.4 预设 env 跳过交互

```
$ mcp2cli install mcp-atlassian \
    --env JIRA_URL=https://mycompany.atlassian.net \
    --env JIRA_API_TOKEN=my_token \
    --yes

🔍 Searching for mcp-atlassian installation info...
   Found: mcp-atlassian (PyPI)

✓ servers.yaml: mcp-atlassian added

🔧 Scanning mcp-atlassian... 65 tools found.
🤖 Generating CLI command tree... 65/65 tools ✓
🧩 Generating skill definitions... ✓
🔗 Syncing skill... claude ✓  cursor ✓  codex ✓

✅ Installation complete!
```

### 6.5 单独同步 skill

```
# 已有 skill，只想同步软链接到各客户端
$ mcp2cli skill sync mcp-atlassian

🔗 Syncing skill to AI clients...
   ✓ ~/.claude/skills/mcp-atlassian  → ~/.agents/mcp2cli/skills/mcp-atlassian/
   ✓ ~/.cursor/skills/mcp-atlassian  → ~/.agents/mcp2cli/skills/mcp-atlassian/
   ⊘ ~/.codex/skills/mcp-atlassian   already exists, skipped

# 同步所有已生成 skill 的 server
$ mcp2cli skill sync
   mcp-atlassian: claude ✓  cursor ✓  codex ✓
   playwright:    claude ✓  cursor ✓  codex ✓
```

### 6.6 Dry-run 模式

```
$ mcp2cli install mcp-atlassian --dry-run

🔍 Searching for mcp-atlassian installation info...
   Found: mcp-atlassian (PyPI)

📋 Environment variables required:
   JIRA_URL: > https://mycompany.atlassian.net
   JIRA_API_TOKEN: > ********

📝 [DRY RUN] Would write to ~/.agents/mcp2cli/servers.yaml:
   mcp-atlassian:
     command: uvx
     args: [mcp-atlassian]
     env:
       JIRA_URL: https://mycompany.atlassian.net
       JIRA_API_TOKEN: ...

   [DRY RUN] Would symlink:
   ~/.claude/skills/mcp-atlassian  → ~/.agents/mcp2cli/skills/mcp-atlassian/
   ~/.cursor/skills/mcp-atlassian  → ~/.agents/mcp2cli/skills/mcp-atlassian/
   ~/.codex/skills/mcp-atlassian   → ~/.agents/mcp2cli/skills/mcp-atlassian/

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
| skill sync：skill 文件不存在 | 报错，提示先运行 `mcp2cli generate skill <server>` |
| skill sync：客户端目录不存在 | 自动创建目录后再创建软链接 |

## 八、代码实现位置

```
mcp2cli/
├── main.py                    # 新增 mcp / skill / install 子命令
├── installer/
│   ├── __init__.py
│   ├── ai_search.py           # AI 搜索安装信息（claude -p 调用、prompt 构造、JSON 解析）
│   ├── servers_writer.py      # 写入 ~/.agents/mcp2cli/servers.yaml
│   ├── interactive.py         # 交互式 env 输入（密码模式、可选跳过）
│   ├── skill_sync.py          # skill sync：创建/更新各客户端 skill 目录的软链接
│   └── pipeline.py            # Step dataclass + pipeline runner
```

## 九、与现有模块的关系

```
mcp2cli mcp install <server>   mcp2cli skill sync [server]    mcp2cli install <server>
    │                               │                               │
    │                               │                               ├─ 调用 mcp install
    │                               │                               │
    ├── installer/ai_search.py      └── installer/skill_sync.py     └─ installer/pipeline.py
    │     调用 claude -p                  创建 symlink                    Step pipeline runner
    │
    ├── installer/servers_writer.py
    │     写入 servers.yaml
    │
    └── installer/interactive.py
          getpass / input

pipeline 内部调用（已有模块）：
    scan          → scanner.py
    generate cli  → generator/cli_gen.py
    generate skill → generator/skill_gen.py
    skill sync    → installer/skill_sync.py
```
