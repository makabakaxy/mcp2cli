# 6. Skill 文件生成详细设计 (`mcp2cli generate skill`)

本文档是 [design.md](design.md) 第六章的展开设计，详细描述 `mcp2cli generate skill` 命令的生成流程、Prompt 模板、文件格式和校验逻辑。

## 6.1 总体流程

```
mcp2cli generate skill <server> [-o <output_dir>]
            │
            ▼
  ┌─ 1. 读取输入文件 ──────────────────────────┐
  │  a) cli/<server>.yaml   (命令树+别名+快捷)  │
  │  b) tools/<server>.json (tool 详细 schema)  │
  │  若任一文件不存在 → 提示先执行对应步骤       │
  └───────────────────┬────────────────────────┘
                      │
                      ▼
  ┌─ 2. 定位模板文件 ──────────────────────────┐
  │  skill_gen_skill.md    → 生成规则和约束     │
  │  skill_gen_example.md  → 完整示例输出       │
  │  路径: <pkg>/generator/templates/           │
  └───────────────────┬────────────────────────┘
                      │
                      ▼
  ┌─ 3. 组装 Prompt 发给 LLM ─────────────────┐
  │  指示 LLM：                                │
  │  a) 读取生成规则 (skill_gen_skill.md)       │
  │  b) 读取示例 (skill_gen_example.md)         │
  │  c) 读取 cli/<server>.yaml                 │
  │  d) 读取 tools/<server>.json               │
  │  e) 生成 SKILL.md + reference/*.md +       │
  │     examples/examples.md                    │
  │  f) 写入目标目录                            │
  └───────────────────┬────────────────────────┘
                      │
                      ▼
  ┌─ 4. 调用 LLM 后端 ────────────────────────┐
  │  同 generate cli，支持：                    │
  │  claude-cli / codex / anthropic-sdk /       │
  │  openai-compatible                          │
  │                                             │
  │  LLM 生成文件 → 写入目标目录                 │
  │  含 --resume 重试机制（同 5-ai-generate-cli │
  │  的会话续接设计）                            │
  └───────────────────┬────────────────────────┘
                      │
                      ▼
  ┌─ 5. 程序侧校验（兜底）─────────────────────┐
  │  - SKILL.md 存在且 frontmatter 合法         │
  │  - SKILL.md token 数 ≤ 500（软上限警告）    │
  │  - command_shortcuts 在命令表中被使用        │
  │  - reference/ 目录存在且包含文件             │
  │  - examples/examples.md 存在                │
  │  校验失败 → --resume session_id 重试         │
  │          （最多重试 1 次）                   │
  └───────────────────┬────────────────────────┘
                      │
                      ▼
  ┌─ 6. 输出预览 ─────────────────────────────┐
  │  打印生成摘要：                             │
  │  - SKILL.md token 数                       │
  │  - reference 文件数量                       │
  │  - 覆盖的 command group 列表                │
  │  - 输出目录路径                             │
  └────────────────────────────────────────────┘
```

## 6.2 输出目录结构

默认输出到 `~/.agent/skills/<server>/`，可通过 `-o` 参数指定其他目录。

```
~/.agent/skills/<server>/
├── SKILL.md                        # 主文件（≤400 tokens），agent 每次对话自动加载
├── reference/                      # 详细参数 + 高频用法示例（agent 按需读取）
│   ├── jira-issue.md               # jira issue 子命令详细参数和示例
│   ├── jira-sprint.md              # jira sprint 子命令
│   ├── jira-board.md               # jira board 子命令
│   ├── jira-project.md             # jira project 子命令
│   ├── confluence-page.md          # confluence page 子命令
│   └── confluence-attachment.md    # confluence attachment 子命令
└── examples/                       # 多步骤复杂场景（agent 按需读取）
    └── examples.md
```

**拆分粒度规则**：
- 一个 group 下有 ≤5 个叶子命令 → 合并为 `<group>.md`（如 `jira-board.md`）
- 一个 group 下有 >5 个叶子命令且有明显的 resource 子分组 → 按 `<group>-<resource>.md` 拆分
- 总原则：单个 reference 文件 ≤ 200 行

## 6.3 SKILL.md 格式规范

### 6.3.1 Frontmatter

```yaml
---
name: <server-name>
description: <一句话概述，含核心能力关键词。用于 agent 判断何时触发此 skill。>
---
```

- `name`：与 server 名一致
- `description`：英文，一句话，包含可触发的关键词（如 "JIRA issues, sprints, Confluence pages"）

### 6.3.2 正文结构

```
# <server-name> (via mcp2cli)         ← 标题
<一行概述>                             ← 简介

## Shortcuts                           ← 快捷方式表（若有）
## Commands                            ← 命令总览表（按 group 分段）
## Discover Parameters                 ← --help 提示
## Quick Examples                      ← 2-3 个最常用示例
```

### 6.3.3 精简规则

1. **命令表优先使用 `command_shortcuts` 的最短形式**
   - 有 shortcut `jira` → 命令列为 `mcp2cli jira issue create`
   - 无 shortcut 但有 alias `atlassian` → 列为 `mcp2cli atlassian ...`
   - 都没有 → 使用全名 `mcp2cli <server> ...`

2. **每个 group 最多列 8 个高频命令**
   - 优先级：create > get > search > list > update > delete > 其他
   - 子资源操作（comment, watcher, worklog, label, attachment 等）不在主文件列出

3. **Quick Examples 只给 2-3 个最常用场景**

4. **总 token 数 ≤ 400**（约 300 词 / 60 行 markdown）

## 6.4 reference 文件格式规范

每个 reference 文件的结构：

```markdown
# <Group> <Resource> Commands

## <action> — <description>

```bash
# 示例描述
mcp2cli <shortcut> <resource> <action> --required-param value
```

Also supports: `--optional-param1`, `--optional-param2`, `--optional-param3`

## <next-action> — <description>
...

Use `mcp2cli <shortcut> <resource> <action> --help` for full parameter details.
```

**规则**：
- 每个命令列 1-3 个最常用的调用示例（使用最短命令形式）
- 示例中展示 required 参数的用法
- "Also supports" 行列出 optional 参数名（kebab-case），不需要示例
- 参数名从 `tools/<server>.json` 的 `inputSchema` 提取，转换为 kebab-case
- 文件末尾提示 `--help` 获取完整参数详情
- 每个 reference 文件 ≤ 200 行

**参数名转换规则**：
- inputSchema 中的 `project_key` → `--project-key`
- inputSchema 中的 `issueKey` → `--issue-key`
- 保持与 CLI YAML 中 `_param_aliases` 的一致性

## 6.5 examples/examples.md 格式规范

```markdown
# Common Usage Examples

## JIRA Workflow

### Create and assign an issue
```bash
mcp2cli jira issue create --project-key INFRA --summary "Fix memory leak" --issue-type Bug --assignee john@example.com
```

### Search and update issues
```bash
# Find open bugs
mcp2cli jira issue search --jql "project=INFRA AND issuetype=Bug AND status=Open"

# Update issue priority
mcp2cli jira issue update --issue-key INFRA-1234 --fields '{"priority": {"name": "High"}}'

# Transition to In Progress
mcp2cli jira issue transition --issue-key INFRA-1234 --transition-id 21
```

### Sprint management
```bash
# List boards
mcp2cli jira board list --project-key INFRA

# List sprints for a board
mcp2cli jira sprint list --board-id 42

# Add issues to sprint
mcp2cli jira sprint add-issues --sprint-id 100 --issue-keys "INFRA-1,INFRA-2"
```

## Confluence Workflow

### Create and manage pages
```bash
# Create a page
mcp2cli confluence page create --space-key TEAM --title "Meeting Notes" --content "# Today's Notes\n..."

# Get page content
mcp2cli confluence page get --page-id 123456789

# Search for pages
mcp2cli confluence search --query "project documentation" --limit 10
```
```

## 6.6 Prompt 模板

### 6.6.1 首次生成 Prompt

```
你是 mcp2cli 的 Skill 文件生成器。你的任务是为 MCP server 生成 agent 可用的 Skill 文件集合（SKILL.md + reference + examples）。

请按以下步骤执行：

第一步：阅读生成规则
读取文件 {{SKILL_RULE_PATH}}，理解 Skill 文件的结构要求、精简原则和参数提取方法。

第二步：阅读输出示例
读取文件 {{SKILL_EXAMPLE_PATH}}，理解 SKILL.md、reference 和 examples 的期望输出格式。

第三步：获取命令树
读取文件 {{CLI_YAML_PATH}}，这是 MCP server "{{SERVER_NAME}}" 的层级命令映射文件，包含：
- commands 树结构（_tool 指向 MCP tool 原始名称）
- server_aliases（server 名称别名）
- command_shortcuts（命令快捷方式）

第四步：获取 tool schema
读取文件 {{TOOLS_PATH}}，获取所有 tool 的名称、描述和 inputSchema（参数定义）。

第五步：生成文件
在 {{OUTPUT_DIR}} 下生成以下文件：

a) SKILL.md — 主文件（≤ 400 tokens）
   - frontmatter 包含 name 和 description（description 需包含核心能力关键词）
   - Shortcuts 表：列出所有 command_shortcuts 和 server_aliases
   - Commands 表：按 group 分段，每段最多 8 个高频命令
   - 命令路径优先使用 command_shortcuts 的最短形式
   - Discover Parameters 段落：提示 --help 和 reference/
   - Quick Examples：2-3 个最常用场景

b) reference/<group>.md 或 reference/<group>-<resource>.md
   - 每个命令给 1-3 个简单使用示例（展示 required 参数）
   - "Also supports" 行列出 optional 参数名（从 inputSchema 提取，kebab-case）
   - 末尾提示 --help
   - 单文件 ≤ 200 行

c) examples/examples.md
   - 5-10 个常见使用场景
   - 包含多步骤工作流
   - 使用最短命令形式

第六步：写入文件
将所有文件写入 {{OUTPUT_DIR}}。确保目录结构正确。

重要约束：
- SKILL.md 必须精简，≤ 400 tokens
- 命令表优先使用 command_shortcuts 的最短形式
- reference 中的参数名从 inputSchema 提取，使用 kebab-case（如 project_key → --project-key）
- 不要输出解释说明，直接执行上述步骤
- 完成后输出一行摘要："Generated: SKILL.md (N tokens) + M reference files + examples.md"
```

**变量说明：**

| 变量 | 值 | 示例 |
|------|-----|------|
| `{{SKILL_RULE_PATH}}` | 安装路径下的规则模板 | `<pkg>/generator/templates/skill_gen_skill.md` |
| `{{SKILL_EXAMPLE_PATH}}` | 安装路径下的示例模板 | `<pkg>/generator/templates/skill_gen_example.md` |
| `{{CLI_YAML_PATH}}` | 运行时 CLI YAML | `~/.agents/mcp2cli/cli/mcp-atlassian.yaml` |
| `{{TOOLS_PATH}}` | 运行时 tools JSON | `~/.agents/mcp2cli/tools/mcp-atlassian.json` |
| `{{SERVER_NAME}}` | 目标 server 名称 | `mcp-atlassian` |
| `{{OUTPUT_DIR}}` | 输出目录 | `~/.agent/skills/mcp-atlassian/` |

### 6.6.2 校验失败重试 Prompt（会话续接）

```
你上一次生成的 Skill 文件存在以下问题：

{{VALIDATION_ERRORS}}

请修复以上问题后重新写入 {{OUTPUT_DIR}}。
注意：
- 你已经读取过规则/示例/YAML/tools 文件，不需要重新读取
- 保持其他正确部分不变，只修复列出的问题
- 修复后输出摘要："Fixed: <修复内容简述>"
```

## 6.7 skill_gen_skill.md 完整内容

存储位置：`mcp2cli/generator/templates/skill_gen_skill.md`

```markdown
# Skill 文件生成规则

## 目标

从 CLI 映射文件 (`cli/<server>.yaml`) 和 tool schema (`tools/<server>.json`)
生成 agent 可用的 Skill 文件集合，使 agent 能够高效使用 mcp2cli 命令，
同时将上下文消耗从 ~5000 tokens（原始 MCP tool schema）降低到 ~400 tokens。

## 输出文件结构

### SKILL.md（主文件）

agent 每次对话自动加载，必须极度精简。

**硬性限制：≤ 400 tokens**

**正文结构（按此顺序）：**

1. Frontmatter（name + description）
2. `# <server> (via mcp2cli)` + 一行概述
3. `## Shortcuts` — 快捷方式表
4. `## Commands` — 命令总览表（按 group 分 ###）
5. `## Discover Parameters` — 提示 --help 和 reference/
6. `## Quick Examples` — 2-3 个示例

**命令形式优先级（最短形式优先）：**

1. 有 `command_shortcuts` → 使用快捷方式：`mcp2cli jira issue create`
2. 有 `server_aliases` → 使用别名：`mcp2cli atlassian jira issue create`
3. 都没有 → 使用全名：`mcp2cli mcp-atlassian jira issue create`

**命令筛选（每 group 最多 8 个）：**

优先级：create > get > search > list > update > delete > 其他
子资源操作（comment, watcher, worklog, label, attachment 等）不列入主文件。

### reference/<group>.md 或 reference/<group>-<resource>.md

**拆分规则：**
- group 下 ≤5 个叶子命令 → 合并为 `<group>.md`
- group 下 >5 个叶子命令 → 按 resource 拆分

**每个命令的内容：**
- 1-3 个使用示例（展示 required 参数）
- "Also supports" 行列出 optional 参数名
- 参数名从 inputSchema 提取，转换为 kebab-case

**参数名转换：**
- snake_case → kebab-case：`project_key` → `--project-key`
- camelCase → kebab-case：`issueKey` → `--issue-key`

**单文件限制：≤ 200 行**

### examples/examples.md

- 5-10 个常见使用场景
- 按工作流组织（如 "JIRA Workflow", "Confluence Workflow"）
- 包含多步骤操作
- 使用最短命令形式

## Frontmatter 规范

```yaml
---
name: <server-name>
description: <英文一句话，列出核心能力关键词>
---
```

description 示例：
- `Manage JIRA issues, sprints, boards, and Confluence pages via CLI. Use when user needs to create/search/update JIRA tickets, manage sprints, or edit Confluence pages.`
- `Automate GitHub operations via CLI. Use when user needs to manage repos, pull requests, issues, or releases.`

## 描述撰写规范

- 语言：英文
- 格式：`<做什么>. Use when <触发条件>.`
- 包含可触发的关键动词和名词
```

## 6.8 skill_gen_example.md 完整内容

存储位置：`mcp2cli/generator/templates/skill_gen_example.md`

本文件包含一个完整的 Skill 文件集合示例，展示三个文件的标准格式。

### SKILL.md 示例

```markdown
---
name: mcp-atlassian
description: Manage JIRA issues, sprints, boards, and Confluence pages via CLI. Use when user needs to create/search/update JIRA tickets, manage sprints, or edit Confluence pages.
---

# mcp-atlassian (via mcp2cli)

Manage JIRA and Confluence via CLI.

## Shortcuts

| Short form | Equivalent to |
|---|---|
| `mcp2cli jira <cmd>` | `mcp2cli mcp-atlassian jira <cmd>` |
| `mcp2cli confluence <cmd>` | `mcp2cli mcp-atlassian confluence <cmd>` |
| `mcp2cli atlassian <cmd>` | `mcp2cli mcp-atlassian <cmd>` |

## Commands

### JIRA
| Command | Description |
|---|---|
| `mcp2cli jira issue create` | Create a new issue |
| `mcp2cli jira issue get` | Get issue details |
| `mcp2cli jira issue search` | Search issues using JQL |
| `mcp2cli jira issue update` | Update an existing issue |
| `mcp2cli jira sprint create` | Create a sprint |
| `mcp2cli jira sprint list` | List sprints for a board |
| `mcp2cli jira board list` | List agile boards |
| `mcp2cli jira project list` | List all projects |

### Confluence
| Command | Description |
|---|---|
| `mcp2cli confluence page get` | Get page content |
| `mcp2cli confluence page create` | Create a new page |
| `mcp2cli confluence page update` | Update page content |
| `mcp2cli confluence search` | Search Confluence content |

## Discover Parameters

Append `--help` to any command for full parameter list:

    mcp2cli jira issue create --help

For detailed parameter reference, see `reference/` directory.

## Quick Examples

    # Create a JIRA issue
    mcp2cli jira issue create --project-key INFRA --summary "Fix memory leak" --issue-type Task

    # Search JIRA issues
    mcp2cli jira issue search --jql "project=INFRA AND status=Open"

    # Get a Confluence page
    mcp2cli confluence page get --page-id 12345

For more examples, see [examples.md](examples/examples.md).
```

### reference/jira-issue.md 示例

```markdown
# JIRA Issue Commands

## create — Create a new JIRA issue

```bash
# Create a task
mcp2cli jira issue create --project-key INFRA --summary "Fix memory leak" --issue-type Task

# Create with assignee
mcp2cli jira issue create --project-key DEV --summary "Add login" --issue-type Story --assignee john@example.com

# Create with additional fields
mcp2cli jira issue create --project-key INFRA --summary "Bug fix" --issue-type Bug --components "Frontend,API" --additional-fields '{"priority": {"name": "High"}}'
```

Also supports: `--description`, `--components`, `--additional-fields`

## get — Get issue details by key

```bash
mcp2cli jira issue get --issue-key INFRA-1234
```

Also supports: `--fields`, `--expand`, `--comment-limit`, `--properties`, `--update-history`

## search — Search issues using JQL

```bash
mcp2cli jira issue search --jql "project=INFRA AND status=Open"
mcp2cli jira issue search --jql "assignee=currentUser() AND updated >= -7d" --limit 20
```

Also supports: `--fields`, `--limit`, `--start-at`, `--expand`, `--projects-filter`

## update — Update an existing issue

```bash
mcp2cli jira issue update --issue-key INFRA-1234 --fields '{"summary": "New title", "assignee": "user@example.com"}'
```

Also supports: `--additional-fields`, `--components`, `--attachments`

## delete — Delete an issue

```bash
mcp2cli jira issue delete --issue-key INFRA-1234
```

## transition — Transition issue status

```bash
mcp2cli jira issue transition --issue-key INFRA-1234 --transition-id 31
```

Also supports: `--fields`, `--comment`

## link — Create a link between two issues

```bash
mcp2cli jira issue link --link-type "Blocks" --inward-issue-key INFRA-123 --outward-issue-key INFRA-456
```

Also supports: `--comment`, `--comment-visibility`

Use `mcp2cli jira issue <action> --help` for full parameter details.
```

### examples/examples.md 示例

```markdown
# Common Usage Examples

## JIRA Workflow

### Create and assign an issue
```bash
mcp2cli jira issue create --project-key INFRA --summary "Fix memory leak" --issue-type Bug --assignee john@example.com
```

### Search and update issues
```bash
# Find open bugs
mcp2cli jira issue search --jql "project=INFRA AND issuetype=Bug AND status=Open"

# Update priority
mcp2cli jira issue update --issue-key INFRA-1234 --fields '{"priority": {"name": "High"}}'

# Transition to In Progress
mcp2cli jira issue transition --issue-key INFRA-1234 --transition-id 21
```

### Sprint management
```bash
# List boards
mcp2cli jira board list --project-key INFRA

# List active sprints
mcp2cli jira sprint list --board-id 42 --state active

# Add issues to sprint
mcp2cli jira sprint add-issues --sprint-id 100 --issue-keys "INFRA-1,INFRA-2"
```

### Project overview
```bash
# List all projects
mcp2cli jira project list

# Get project issues
mcp2cli jira project issues --project-key INFRA --limit 20
```

## Confluence Workflow

### Create and manage pages
```bash
# Create a page
mcp2cli confluence page create --space-key TEAM --title "Meeting Notes" --content "# Notes\n..."

# Get page content
mcp2cli confluence page get --page-id 123456789

# Update a page
mcp2cli confluence page update --page-id 123456789 --title "Updated Notes" --content "# Updated\n..."
```

### Search and navigate
```bash
# Search pages
mcp2cli confluence search --query "project documentation" --limit 10

# Get child pages
mcp2cli confluence page children --parent-id 123456789

# Compare page versions
mcp2cli confluence page diff --page-id 123456789 --from-version 1 --to-version 3
```

### Attachment management
```bash
# List attachments
mcp2cli confluence attachment list --content-id 123456789

# Upload attachment
mcp2cli confluence attachment upload --content-id 123456789 --file-path ./diagram.png
```
```

## 6.9 校验流程

### 6.9.1 校验项

```
┌─ 校验 1: 文件存在性 ─────────────────────────┐
│  - SKILL.md 存在                              │
│  - reference/ 目录存在且至少有 1 个 .md 文件   │
│  - examples/examples.md 存在                  │
└──────────────────────────────────────────────┘
                    │ 通过
                    ▼
┌─ 校验 2: Frontmatter 合法性 ─────────────────┐
│  - SKILL.md 有 YAML frontmatter              │
│  - frontmatter 包含 name 和 description      │
│  - name 与 server 名一致                     │
│  - description 不为空                        │
└──────────────────────────────────────────────┘
                    │ 通过
                    ▼
┌─ 校验 3: Token 预算 ────────────────────────┐
│  估算 SKILL.md 的 token 数                   │
│  > 500 → 警告（软上限）                      │
│  > 800 → 错误（硬上限）                      │
└──────────────────────────────────────────────┘
                    │ 通过
                    ▼
┌─ 校验 4: 快捷方式覆盖 ──────────────────────┐
│  从 cli/<server>.yaml 读取 command_shortcuts │
│  检查 SKILL.md 的命令表是否使用了最短形式      │
│  未使用 → 警告                               │
└──────────────────────────────────────────────┘
```

### 6.9.2 重试策略

同 `generate cli` 的两层校验设计（见 5-ai-generate-cli.md 5.7.2）：
1. LLM 会话内自验（如果 LLM 后端支持 Bash 工具）
2. 程序侧兜底校验
3. 失败时通过 `--resume session_id` 在同一会话中重试（最多 1 次）

### 6.9.3 校验报告输出

```
$ mcp2cli generate skill mcp-atlassian
Reading cli/mcp-atlassian.yaml... 65 commands
Reading tools/mcp-atlassian.json... 65 tools
Generating skill files...
Generated:
  SKILL.md      → 380 tokens ✓
  reference/    → 6 files (jira-issue.md, jira-sprint.md, ...)
  examples/     → examples.md
Written to ~/.agent/skills/mcp-atlassian/
```

## 6.10 CLI 参数设计

```bash
mcp2cli generate skill <server> [OPTIONS]

Options:
  -o, --output <dir>    输出目录（默认：~/.agent/skills/<server>/）
  --force               覆盖已有文件
  --dry-run             只预览不写入
```

## 6.11 文件布局变更

在项目源码中新增模板文件：

```
mcp2cli/
└── generator/
    ├── cli_gen.py                    # 已有：CLI 生成逻辑
    ├── skill_gen.py                  # 新增：Skill 生成逻辑
    └── templates/
        ├── cli_gen_skill.md          # 已有：CLI 生成规则
        ├── cli_gen_example.md        # 已有：CLI 示例输出
        ├── skill_gen_skill.md        # 新增：Skill 生成规则（6.7）
        └── skill_gen_example.md      # 新增：Skill 示例输出（6.8）
```
