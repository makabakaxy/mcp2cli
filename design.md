一、项目定位
mcp2cli 是一个将 MCP (Model Context Protocol) 工具转化为层级式 CLI 命令的桥接工具。它从已有的 Claude/Cursor/Codex 配置中读取 MCP server 定义，通过 AI 分析工具列表生成符合人类直觉的层级命令树，并通过常驻代理进程（Daemon）解决每次调用的性能问题。

核心价值：

将 MCP 工具的 schema（通常 4000-6000 tokens）压缩为 Skill 文件（约 400 tokens），节省 90%+ 上下文
通过层级式 CLI 实现渐进式披露，agent 按需探索命令树
兼容已有的大量 MCP 工具生态，无需改造 MCP server
二、总体架构
┌──────────────── 配置源 ─────────────────┐
│  ~/.claude.json                         │
│  ~/.cursor/mcp.json                     │
│  ~/.codex/config.toml                   │
│  ~/.agents/mcp2cli/servers.yaml (自定义补充)    │
└──────────────────┬──────────────────────┘
                   │ mcp2cli scan
                   ▼
┌──────────────────────────────────────────┐
│       ~/.agents/mcp2cli/registry.json           │
│  (server 配置 + tool schema 物化视图)     │
└──────────────────┬───────────────────────┘
                   │ mcp2cli generate cli (AI 分析)
                   ▼
┌──────────────────────────────────────────┐
│    ~/.agents/mcp2cli/cli/<server>.yaml          │
│  (层级命令树 → tool 映射文件)             │
└───────┬──────────────┬───────────────────┘
        │              │ mcp2cli generate skill
        ▼              ▼
  层级式 CLI        SKILL.md
  (用户/agent       (agent 阅读,
   直接调用)        渐进式披露)
        │
        ▼
┌──────────────────────────────────────────┐
│          MCP Proxy Daemon                │
│  (Unix Socket, 连接池, 两层空闲回收)      │
└──────────────────────────────────────────┘
三、CLI 命令体系
3.1 三层命令设计
┌─────────────────────────────────────────────────────────────┐
│                      mcp2cli 命令体系                        │
├──────────────┬──────────────────────────────────────────────┤
│  第一层       │  管理命令                                     │
│  (管理)       │  mcp2cli list / scan / generate / daemon     │
├──────────────┼──────────────────────────────────────────────┤
│  第二层       │  底层直通命令                                  │
│  (直通)       │  mcp2cli tools <server> [tool]               │
│              │  mcp2cli call <server> <tool> [--args]        │
├──────────────┼──────────────────────────────────────────────┤
│  第三层       │  层级式命令 (AI 生成, 渐进式披露)               │
│  (层级)       │  mcp2cli <server> <group> <sub> <action>     │
└──────────────┴──────────────────────────────────────────────┘
3.2 管理命令
# 列出所有配置源中的 MCP server
mcp2cli list
# 扫描 server 的 tool 列表，写入 registry.json
mcp2cli scan mcp-atlassian
mcp2cli scan --all
# AI 生成层级命令映射文件
mcp2cli generate cli mcp-atlassian
# 生成 SKILL.md（基于层级命令树）
mcp2cli generate skill mcp-atlassian --output ~/.cursor/skills/mcp-atlassian/SKILL.md
# Daemon 管理
mcp2cli daemon status
mcp2cli daemon stop
3.3 底层直通命令
直接使用 MCP tool 原始名称，不经过层级映射。始终可用，不依赖 generate cli：

# 列出所有 tool
mcp2cli tools mcp-atlassian
# 查看某个 tool 的参数
mcp2cli tools mcp-atlassian jira_create_issue
# 直接调用（使用 MCP tool 原始名称）
mcp2cli call mcp-atlassian jira_create_issue --project INFRA --summary "Fix bug"
3.4 层级式命令（核心创新）
经过 mcp2cli generate cli 后可用。渐进式披露——每层 --help 只暴露下一层的信息：

# 第 0 层：查看有哪些 server 可用
mcp2cli --help
#  Commands:
#    mcp-atlassian   Confluence & JIRA operations
#    playwright      Browser automation
#    list            List all MCP servers
#    scan            Scan server tools
#    ...
# 第 1 层：查看 server 下有哪些分组
mcp2cli mcp-atlassian --help
#  Usage: mcp2cli mcp-atlassian <group> ...
#
#  Groups:
#    jira          JIRA project management
#    confluence    Confluence wiki operations
# 第 2 层：查看分组下有哪些资源
mcp2cli mcp-atlassian jira --help
#  Usage: mcp2cli mcp-atlassian jira <resource> ...
#
#  Resources:
#    issue     Issue operations
#    sprint    Sprint operations
#    board     Board operations
# 第 3 层：查看资源的可用操作
mcp2cli mcp-atlassian jira issue --help
#  Usage: mcp2cli mcp-atlassian jira issue <action> [OPTIONS]
#
#  Actions:
#    create    Create a new issue
#    get       Get issue details by key
#    search    Search issues using JQL
#    update    Update an existing issue
# 第 4 层：查看具体操作的参数
mcp2cli mcp-atlassian jira issue create --help
#  Usage: mcp2cli mcp-atlassian jira issue create [OPTIONS]
#
#  Create a new JIRA issue
#
#  Options:
#    --project      (required)  Project key, e.g. "INFRA"
#    --summary      (required)  Issue summary
#    --issue-type               Issue type (default: "Task")
#    --description              Detailed description
#    --assignee                 Assignee username
# 实际调用
mcp2cli mcp-atlassian jira issue create --project INFRA --summary "Fix memory leak"
mcp2cli mcp-atlassian confluence page get --page-id 12345
mcp2cli mcp-atlassian jira sprint create --board-id 42 --name "Sprint 10"
对比改进前后：

改进前（扁平）	改进后（层级）
mcp2cli call mcp-atlassian jira_create_issue	mcp2cli mcp-atlassian jira issue create
mcp2cli call mcp-atlassian confluence_get_page	mcp2cli mcp-atlassian confluence page get
一次性暴露 12 个 tool 名	逐层展开：2 → 3 → 4 → 参数
四、CLI 映射文件设计
mcp2cli generate cli 的产物，存储在 ~/.agents/mcp2cli/cli/<server>.yaml。

4.1 文件格式
# ~/.agents/mcp2cli/cli/mcp-atlassian.yaml
server: mcp-atlassian
generated_at: "2026-04-02T10:00:00Z"
generated_by: ai          # "ai" 或 "manual"

# server 名称别名：替代第一个 子命令
server_aliases:
  - atlassian              # mcp2cli atlassian jira issue → mcp2cli mcp-atlassian jira issue

# 命令快捷方式：跳过 server token，直接匹配子命令
command_shortcuts:
  - jira                   # mcp2cli jira issue create → mcp2cli mcp-atlassian jira issue create
  - confluence             # mcp2cli confluence page get → mcp2cli mcp-atlassian confluence page get

commands:
  jira:
    _description: "JIRA project management"
    issue:
      _description: "Issue operations"
      create:
        _tool: jira_create_issue
        _description: "Create a new JIRA issue"
        _examples:
          - "mcp2cli mcp-atlassian jira issue create --project INFRA --summary 'Fix bug'"
        _param_aliases:             # 可选：参数缩写别名
          type: issue-type          # --type 自动展开为 --issue-type
      get:
        _tool: jira_get_issue
        _description: "Get issue details by key"
      search:
        _tool: jira_search
        _description: "Search issues using JQL"
      update:
        _tool: jira_update_issue
        _description: "Update an existing issue"
    sprint:
      _description: "Sprint operations"
      create:
        _tool: jira_create_sprint
        _description: "Create a new sprint"
      list:
        _tool: jira_list_sprints
        _description: "List sprints for a board"
  confluence:
    _description: "Confluence wiki operations"
    page:
      _description: "Page operations"
      get:
        _tool: confluence_get_page
        _description: "Get page content"
      create:
        _tool: confluence_create_page
        _description: "Create a new page"
      update:
        _tool: confluence_update_page
        _description: "Update page content"
    search:
      _tool: confluence_search
      _description: "Search Confluence content"
设计说明：

_ 前缀字段为元数据，非 _ 前缀为子命令节点
叶子节点包含 _tool 字段，指向 MCP tool 原始名称
中间节点只有 _description，用于 --help 展示
_param_aliases 提供参数缩写别名（如 --type 展开为 --issue-type）
_examples 在 --help 和 SKILL.md 中展示
server_aliases 定义 server 名称的简短别名
command_shortcuts 定义可跳过 server 直接使用的顶层命令
文件可由 AI 生成后人工微调
4.2 命令解析流程
输入: mcp2cli mcp-atlassian jira issue create --project INFRA
解析过程:
  1. "mcp-atlassian" → 在已生成的 cli/*.yaml 中查找
     → 找到 ~/.agents/mcp2cli/cli/mcp-atlassian.yaml
  2. "jira" → commands.jira (中间节点, 继续)
  3. "issue" → commands.jira.issue (中间节点, 继续)
  4. "create" → commands.jira.issue.create
     → 发现 _tool 字段 → 叶子节点, 停止路径解析
  5. 剩余参数 "--project INFRA" → 转为 tool 参数
     → 查 _param_aliases: 无匹配别名
     → 查 registry.json 中 jira_create_issue 的 input_schema 校验参数合法性
  6. 转发到 daemon:
     → {"server": "mcp-atlassian", "tool": "jira_create_issue",
        "params": {"project": "INFRA"}}
4.3 找不到映射时的 Fallback
输入: mcp2cli mcp-atlassian some_unknown_tool --arg val
解析:
  1. "mcp-atlassian" → 找到 yaml
  2. "some_unknown_tool" → commands 中不存在
  3. Fallback: 当作 MCP tool 原始名称，等价于
     mcp2cli call mcp-atlassian some_unknown_tool --arg val
  4. 在 registry.json 中查找 tool 是否存在
  5. 存在则直接调用，不存在则报错
这保证层级命令和直通命令在同一入口下兼容。

4.4 别名与快捷路由
为了减少输入长度、提升使用效率，支持两种快捷路由方式：
┌──────────────────────────────────────────────────────────────────────────┐
│  类型              │  配置字段            │  效果                          │
├──────────────────────────────────────────────────────────────────────────┤
│  Server 别名       │  server_aliases      │  替换第一个 token               │
│                    │                      │  mcp2cli atlassian jira issue  │
│                    │                      │  → mcp2cli mcp-atlassian ...   │
├──────────────────────────────────────────────────────────────────────────┤
│  命令快捷方式       │  command_shortcuts   │  跳过 server token              │
│                    │                      │  mcp2cli jira issue            │
│                    │                      │  → mcp2cli mcp-atlassian jira  │
└──────────────────────────────────────────────────────────────────────────┘

server_aliases：值为字符串列表，每个元素是 server 名的简短替代。
command_shortcuts：值为字符串列表，每个元素必须是 commands 下的顶层 key。

详细设计见 [4.4-alias-routing.md](4.4-alias-routing.md)（索引构建、解析算法、优先级规则、冲突检测、AI 生成规则、--help 展示、SKILL.md 别名展示）。

五、AI 生成流程 (mcp2cli generate cli)
5.1 流程
mcp2cli generate cli mcp-atlassian
            │
            ▼
  ┌─ 1. 读取 registry.json ──────────────────────┐
  │  获取 mcp-atlassian 的所有 tool:              │
  │    - jira_create_issue                        │
  │    - jira_get_issue                           │
  │    - jira_search                              │
  │    - jira_create_sprint                       │
  │    - confluence_get_page                      │
  │    - confluence_search                        │
  │    - confluence_create_page                   │
  │    - ...                                      │
  └───────────────────┬──────────────────────────┘
                      │
                      ▼
  ┌─ 2. 构造 Prompt 发给 LLM ───────────────────┐
  │  "请将以下 MCP tool 分组为层级命令树：          │
  │   规则：                                      │
  │   - 按产品/领域分第一层 (jira, confluence)     │
  │   - 按资源类型分第二层 (issue, page, sprint)   │
  │   - 按操作分第三层 (create, get, list, ...)   │
  │   - 最深不超过 4 层                           │
  │   - 动词使用: create/get/list/search/         │
  │     update/delete                             │
  │   - 输出 YAML 格式"                           │
  └───────────────────┬──────────────────────────┘
                      │
                      ▼
  ┌─ 3. LLM 返回命令树 YAML ────────────────────┐
  │  commands:                                   │
  │    jira:                                     │
  │      issue:                                  │
  │        create: { _tool: jira_create_issue }  │
  │        get:    { _tool: jira_get_issue }     │
  │        ...                                   │
  └───────────────────┬──────────────────────────┘
                      │
                      ▼
  ┌─ 4. 校验 + 写入 ────────────────────────────┐
  │  - 检查所有 _tool 值在 registry 中都存在      │
  │  - 检查所有 tool 都被覆盖（无遗漏）           │
  │  - 写入 ~/.agents/mcp2cli/cli/mcp-atlassian.yaml   │
  │  - 打印命令树预览，供用户确认                  │
  └──────────────────────────────────────────────┘
5.2 生成后预览
$ mcp2cli generate cli mcp-atlassian
Analyzing 12 tools from mcp-atlassian...
Generated command tree:
mcp-atlassian
├── jira
│   ├── issue
│   │   ├── create     → jira_create_issue
│   │   ├── get        → jira_get_issue
│   │   ├── search     → jira_search
│   │   └── update     → jira_update_issue
│   ├── sprint
│   │   ├── create     → jira_create_sprint
│   │   └── list       → jira_list_sprints
│   └── board
│       └── list       → jira_list_boards
└── confluence
    ├── page
    │   ├── get        → confluence_get_page
    │   ├── create     → confluence_create_page
    │   └── update     → confluence_update_page
    └── search         → confluence_search
Coverage: 12/12 tools mapped ✓
Written to ~/.agents/mcp2cli/cli/mcp-atlassian.yaml
You can edit this file to adjust grouping.
Next: run 'mcp2cli generate skill mcp-atlassian' to create a SKILL.md
5.3 AI 生成 vs 手动编辑
场景	方式
首次转换	mcp2cli generate cli 让 AI 生成初始版本
微调分组	直接编辑 YAML 文件（改层级、改描述、加别名）
MCP server 新增 tool	mcp2cli generate cli --merge：AI 只处理新增的，保留已有调整
完全自定义	手写 YAML，generated_by: manual
六、Skill 生成（基于层级命令树）
mcp2cli generate skill 读取映射文件，生成层级式的 SKILL.md：

# mcp-atlassian (via mcp2cli)
Manage JIRA and Confluence via CLI.
## Command Structure
mcp2cli mcp-atlassian <group> <resource> <action> [OPTIONS]
### JIRA
| Command | Description |
|---------|-------------|
| `mcp2cli mcp-atlassian jira issue create` | Create a new issue |
| `mcp2cli mcp-atlassian jira issue get` | Get issue details |
| `mcp2cli mcp-atlassian jira issue search` | Search issues |
| `mcp2cli mcp-atlassian jira sprint create` | Create a sprint |
| `mcp2cli mcp-atlassian jira sprint list` | List sprints |
### Confluence
| Command | Description |
|---------|-------------|
| `mcp2cli mcp-atlassian confluence page get` | Get page content |
| `mcp2cli mcp-atlassian confluence page create` | Create a new page |
| `mcp2cli mcp-atlassian confluence search` | Search Confluence |
## Discover Parameters
For any command's full parameter list, append `--help`:
    mcp2cli mcp-atlassian jira issue create --help
## Examples
    # Create a JIRA issue
    mcp2cli mcp-atlassian jira issue create --project INFRA --summary "Fix memory leak"
    # Search JIRA
    mcp2cli mcp-atlassian jira issue search --jql "project=INFRA AND status=Open"
    # Get a Confluence page
    mcp2cli mcp-atlassian confluence page get --page-id 12345
Agent 使用模式对比：

传统 MCP 方式（agent 上下文中加载全部 tool schema）:
  → 12 个 tool 的完整 schema ≈ 5000 tokens
  → 每轮对话都带着
mcp2cli + Skill 方式:
  → SKILL.md ≈ 400 tokens（只有命令表 + 示例）
  → agent 需要参数详情时: mcp2cli ... --help ≈ 200 tokens（按需）
  → 总计: 400 + 200 × 使用次数
  → 一般一次对话调用 2-3 个 tool ≈ 1000 tokens，节省 80%
七、Daemon 设计
7.1 架构
┌─────────────────────────────────────────────────┐
│                MCP Proxy Daemon                 │
│                                                 │
│  监听: ~/.agents/mcp2cli/daemon.sock (Unix Socket)      │
│  PID:  ~/.agents/mcp2cli/daemon.pid                    │
│                                                 │
│  ┌─ 连接池 ───────────────────────────────────┐ │
│  │                                            │ │
│  │  mcp-atlassian  [alive]  last: 10:05       │ │
│  │  playwright     [idle]   last: 09:30       │ │
│  │                                            │ │
│  └────────────────────────────────────────────┘ │
│                                                 │
│  看门狗: 每 30s 检查一次                          │
└─────────────────────────────────────────────────┘
7.2 两层空闲回收
┌──────────── 第一层：Server 连接回收 ──────────────┐
│                                                  │
│  每个 MCP server 连接独立跟踪 last_used 时间戳     │
│                                                  │
│  某个 server 空闲 > SERVER_IDLE (默认 10 min)      │
│  → 关闭该 server 的子进程                          │
│  → 释放该连接的内存                                │
│  → 其他 server 连接不受影响                        │
│                                                  │
│  例：playwright 用了一次后 10min 没用               │
│  → 关闭 playwright 进程                           │
│  → mcp-atlassian 连接保持                         │
│                                                  │
└──────────────────────────────────────────────────┘
                      │
                      ▼
┌──────────── 第二层：Daemon 自身回收 ──────────────┐
│                                                  │
│  条件：所有 server 连接已关闭                       │
│       AND 无新请求 > DAEMON_IDLE (默认 5 min)      │
│  → Daemon 进程退出                                │
│  → 清理 PID 文件和 Socket 文件                     │
│                                                  │
│  绝对兜底：                                       │
│  Daemon 运行时间 > MAX_LIFETIME (默认 24h)         │
│  → 无条件退出（防止僵尸进程）                       │
│                                                  │
└──────────────────────────────────────────────────┘
7.3 生命周期管理
首次 CLI 调用:
  main.py → 检查 daemon.pid → 不存在/进程已死
  → fork daemon 子进程 (detach, start_new_session)
  → daemon 创建 Unix Socket, 写 PID 文件
  → main.py 等待 socket 文件出现 (最多 5s)
  → 连接 socket, 发送请求
后续调用:
  main.py → 检查 daemon.pid → 进程存活
  → 直接连接 socket, 发送请求 (~50ms)
崩溃恢复:
  main.py → 检查 daemon.pid → 文件存在但进程已死
  → 清理 stale PID 文件和 socket 文件
  → 重新启动 daemon
八、文件布局
~/.agents/mcp2cli/                          # 运行时数据目录
├── registry.json                    # tool schema 物化视图
├── daemon.pid                       # daemon PID 文件
├── daemon.sock                      # Unix Domain Socket
├── daemon.log                       # daemon 日志
├── servers.yaml                     # 用户自定义 MCP server（可选）
├── cli/                             # AI 生成的命令映射文件
│   ├── mcp-atlassian.yaml
│   └── playwright.yaml
└── cache/                           # schema 缓存
    └── schemas/
        ├── mcp-atlassian.json
        └── playwright.json
mcp2cli/                             # 项目源码
├── pyproject.toml
├── README.md
├── mcp2cli/
│   ├── __init__.py
│   ├── main.py                      # CLI 入口 (click/typer)
│   ├── config/
│   │   ├── reader.py                # 读取 Claude/Cursor/Codex 配置
│   │   ├── registry.py              # registry.json 管理
│   │   └── models.py                # 数据模型 (dataclass)
│   ├── cli/
│   │   ├── resolver.py              # 层级命令解析器
│   │   └── mapping.py               # 读写 cli/*.yaml 映射文件
│   ├── daemon/
│   │   ├── server.py                # Daemon 主进程 (asyncio)
│   │   ├── client.py                # IPC 客户端
│   │   ├── lifecycle.py             # 启停/PID/健康检查
│   │   └── pool.py                  # 连接池 + 空闲回收
│   ├── scanner.py                   # 连接 MCP server → list_tools
│   └── generator/
│       ├── cli_gen.py               # AI 生成命令映射
│       ├── skill_gen.py             # 生成 SKILL.md
│       └── templates/
│           └── skill.md.j2          # Jinja2 模板
└── tests/
九、端到端使用流程
# ① 查看有哪些 MCP server 可用
$ mcp2cli list
  NAME             SOURCE           STATUS
  mcp-atlassian    claude:global    not scanned
  playwright       claude:project   not scanned
# ② 扫描某个 server 的工具列表
$ mcp2cli scan mcp-atlassian
  Connecting to mcp-atlassian...
  Found 12 tools. Saved to registry.
# ③ AI 生成层级命令映射
$ mcp2cli generate cli mcp-atlassian
  Analyzing 12 tools...
  Generated command tree:
  mcp-atlassian
  ├── jira
  │   ├── issue (create, get, search, update)
  │   ├── sprint (create, list)
  │   └── board (list)
  └── confluence
      ├── page (get, create, update)
      └── search
  Coverage: 12/12 ✓
  Written to ~/.agents/mcp2cli/cli/mcp-atlassian.yaml
# ④ 生成 Skill 文件供 agent 使用
$ mcp2cli generate skill mcp-atlassian -o ~/.cursor/skills/mcp-atlassian/SKILL.md
  Skill file generated.
# ⑤ 直接使用层级式 CLI
$ mcp2cli mcp-atlassian jira issue create --project INFRA --summary "Fix leak"
  { "key": "INFRA-5678", "self": "https://jira.shopee.io/rest/..." }
# ⑥ Agent 使用模式（在 Cursor/Codex 中）
# Agent 读取 SKILL.md → 知道有 mcp2cli mcp-atlassian 可用
# Agent 需要查参数 → mcp2cli mcp-atlassian jira issue create --help
# Agent 调用 → mcp2cli mcp-atlassian jira issue create --project INFRA ...
十、关键设计决策
决策点	选择	理由
层级命令 vs 扁平命令	两者共存，层级命令优先，扁平 fallback	层级对 agent 更友好，但不能丢失直通能力
映射文件格式	YAML，_ 前缀元数据	人类可读可编辑，AI 易生成，_ 前缀区分元数据和子命令
映射文件位置	~/.agents/mcp2cli/cli/<server>.yaml	每个 server 独立文件，互不干扰
AI 生成 vs 手写	AI 初始化 + 人工微调	AI 处理 80% 的分组逻辑，人工处理边缘情况
新增 tool 处理	generate cli --merge	保留已有调整，只处理新增
参数命名风格	_param_aliases 仅用于自定义缩写别名	按需配置，不做强制格式转换
Daemon 退出	两层空闲回收 + 24h 兜底	精细控制资源释放，防僵尸
配置优先级	自定义 > Claude > Cursor > Codex	用户自定义覆盖一切
十一、扩展能力
已规划但不在 MVP 中的功能：

mcp2cli install：将 mcp2cli mcp-atlassian 安装为独立命令 mcp-atlassian（通过 symlink 或 shell alias）
交互模式：mcp2cli mcp-atlassian -i 进入交互式 REPL，自动补全命令路径
管道支持：echo '{"jql":"project=INFRA"}' | mcp2cli mcp-atlassian jira issue search --json
多 server 编排：mcp2cli pipe mcp-atlassian:jira:issue:get | mcp-atlassian