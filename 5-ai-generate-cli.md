# 5. AI 生成流程详细设计 (`mcp2cli generate cli`)

本文档是 [0-design-overview.md](0-design-overview.md) 第五章的展开设计，详细描述 `mcp2cli generate cli` 命令的 Prompt 构造、LLM 调用和校验流程。

## 5.1 总体流程

```
mcp2cli generate cli <server> [--merge]
            │
            ▼
  ┌─ 1. 扫描mcp server tools ─────────-────────────┐
  │  执行 mcp2cli scan <server>                    │
  │  → 确保 tools/<server>.json 是最新数据          │
  │  → 若 server 不可达则报错退出                   │
  └───────────────────┬────────────────────────────┘
                      │
                      ▼
  ┌─ 2. 定位模板文件 ─────────────────────────────┐
  │  cli_gen_skill.md   → 生成规则和约束           │
  │  cli_gen_example.md → 示例 YAML 输出           │
  │  路径: <install_path>/generator/templates/      │
  └───────────────────┬────────────────────────────┘
                      │
                      ▼
  ┌─ 3. 组装 Prompt ──────────────────────────────┐
  │  构建指令文本，指示 LLM：                       │
  │  a) 读取 cli_gen_skill.md  (学习生成规则)       │
  │  b) 读取 cli_gen_example.md (学习输出格式)      │
  │  c) 读取 tools/<server>.json (获取 tool 列表)   │
  │  d) [--merge] 读取已有 cli/<server>.yaml        │
  │  e) 生成 YAML 并写入目标路径                    │
  └───────────────────┬────────────────────────────┘
                      │
                      ▼
  ┌─ 4. 调用 LLM 后端 ───────────────────────────┐
  │  默认: claude -p --output-format json          │
  │  → 返回 JSON 含 session_id + result            │
  │  → 保留 session_id 用于后续重试                 │
  │  可选: Codex / Anthropic SDK / OpenAI 兼容接口  │
  │  配置: ~/.agents/mcp2cli/config.yaml           │
  │                                                │
  │  LLM 内部流程：                                 │
  │  a) 读取规则/示例/tools → 生成 YAML → 写入文件  │
  │  b) 执行 mcp2cli validate <server> 自验         │
  │  c) 若自验失败 → 自行修复 YAML → 重新写入并验证  │
  │  d) 自验通过 → 返回结果                         │
  └───────────────────┬────────────────────────────┘
                      │
                      ▼
  ┌─ 5. 程序侧校验（兜底）──────────────────────────┐
  │  - YAML 语法合法                               │
  │  - 所有 _tool 值在 tools/<server>.json 中存在   │
  │  - 所有 tool 都被映射（覆盖率 100%）            │
  │  - 命令路径无冲突                               │
  │  校验失败 → --resume session_id 继续对话重试    │
  │          （LLM 保留上次生成的完整上下文）        │
  │          （最多重试 2 次）                       │
  └───────────────────┬────────────────────────────┘
                      │
                      ▼
  ┌─ 6. 写入 + 预览 ─────────────────────────────┐
  │  写入 ~/.agents/mcp2cli/cli/<server>.yaml      │
  │  打印命令树预览                                │
  │  提示下一步: generate skill                    │
  └────────────────────────────────────────────────┘
```

## 5.2 Prompt 模板与会话管理

### 5.2.0 会话续接机制

`claude -p --output-format json` 返回结构化 JSON（含 `session_id`、`result`、`is_error` 等字段）。校验失败时，通过 `--resume <session_id>` 在同一会话中续接对话，LLM 保留完整上下文，只需传入错误信息即可针对性修复，无需重新读取规则/示例/tools 文件。重试的 Token 消耗约为首次的 10-20%。

### 5.2.1 首次生成 Prompt

以下是 `mcp2cli generate cli <server>` **首次生成**时，程序组装后发送给 LLM 的完整 Prompt：

```
你是 mcp2cli 的 CLI 命令树生成器。你的任务是将 MCP server 的扁平 tool 列表组织为层级式命令树，输出一个 YAML 映射文件。

请按以下步骤执行：

第一步：阅读生成规则
读取文件 {{SKILL_PATH}} ，理解命令树的分层原则、命名规范和格式要求。

第二步：阅读输出示例
读取文件 {{EXAMPLE_PATH}} ，理解期望的 YAML 输出格式和风格。

第三步：获取 tool 列表
读取文件 {{TOOLS_PATH}} ，这是 MCP server "{{SERVER_NAME}}" 的所有 tool 定义，包含 tool 名称、描述和 input_schema。

第四步：生成命令树
根据规则和示例，将所有 tool 组织为层级命令树。确保：
- 每个 tool 都被映射到命令树中（覆盖率 100%）
- 遵循 cli_gen_skill.md 中的所有规则
- YAML 格式与 cli_gen_example.md 保持一致

第五步：写入文件
将生成的完整 YAML 内容写入 {{OUTPUT_PATH}} 。

第六步：自验
执行命令 mcp2cli validate {{SERVER_NAME}} ，检查生成的 YAML 是否符合所有规则。
如果校验报错，根据输出信息修复 YAML 后重新写入 {{OUTPUT_PATH}}，再次执行 mcp2cli validate {{SERVER_NAME}} 直到校验通过。

重要约束：
- 不要输出解释说明，直接执行上述步骤
- 写入的文件必须是合法的 YAML
- 所有 tool 必须被覆盖，不能遗漏
- 完成后输出一行摘要："Generated: X tools mapped to Y commands"
```

**变量说明：**

| 变量 | 值 | 示例 |
|------|-----|------|
| `{{SKILL_PATH}}` | 安装路径下的 skill 模板 | `<pkg>/generator/templates/cli_gen_skill.md` |
| `{{EXAMPLE_PATH}}` | 安装路径下的 example 模板 | `<pkg>/generator/templates/cli_gen_example.md` |
| `{{TOOLS_PATH}}` | 运行时数据目录下的 tool 文件 | `~/.agents/mcp2cli/tools/mcp-atlassian.json` |
| `{{SERVER_NAME}}` | 目标 MCP server 名称 | `mcp-atlassian` |
| `{{OUTPUT_PATH}}` | YAML 输出路径 | `~/.agents/mcp2cli/cli/mcp-atlassian.yaml` |

### 5.2.2 --merge 模式 Prompt

当使用 `mcp2cli generate cli <server> --merge` 时，Prompt 增加一个步骤：

```
你是 mcp2cli 的 CLI 命令树生成器。你的任务是为 MCP server 新增的 tool 扩展已有的命令树。

请按以下步骤执行：

第一步：阅读生成规则
读取文件 {{SKILL_PATH}} ，理解命令树的分层原则、命名规范和格式要求。

第二步：阅读输出示例
读取文件 {{EXAMPLE_PATH}} ，理解期望的 YAML 输出格式和风格。

第三步：获取 tool 列表
读取文件 {{TOOLS_PATH}} ，这是 MCP server "{{SERVER_NAME}}" 的所有 tool 定义。

第四步：读取已有命令树
读取文件 {{EXISTING_CLI_PATH}} ，这是当前已有的命令映射文件。

第五步：差异分析
对比 tool 列表和已有命令树：
- 找出已有命令树中已映射的 tool（保持不变）
- 找出 tool 列表中新增的、尚未映射的 tool
- 找出已有命令树中引用了但 tool 列表中已不存在的 tool（标记为废弃）

第六步：增量生成
将新增 tool 合并到已有命令树中：
- 保留已有结构、描述、别名、示例不变
- 仅新增 tool 的映射节点
- 将 generated_by 改为 "ai-merge"
- 更新 generated_at 时间戳
- 如有废弃 tool，在该叶子节点添加 _deprecated: true

第七步：写入文件
将合并后的完整 YAML 写入 {{OUTPUT_PATH}} 。

第八步：自验
执行命令 mcp2cli validate {{SERVER_NAME}} ，检查合并后的 YAML 是否符合所有规则。
如果校验报错，根据输出信息修复 YAML 后重新写入 {{OUTPUT_PATH}}，再次执行 mcp2cli validate {{SERVER_NAME}} 直到校验通过。

重要约束：
- 已有结构必须完整保留，不可重组、不可修改描述
- 仅新增节点遵循 cli_gen_skill.md 的规则
- 完成后输出摘要："Merged: X new tools added, Y existing preserved, Z deprecated"
```

### 5.2.3 校验失败重试 Prompt（会话续接）

当程序侧校验发现问题时，通过 `--resume <session_id>` 在同一会话中追加发送：

```bash
# 程序侧调用
claude -p "<error_prompt>" --output-format json --resume <session_id>
```

重试 Prompt 内容：

```
你上一次生成并写入 {{OUTPUT_PATH}} 的 YAML 存在以下问题：

{{VALIDATION_ERRORS}}

请修复以上问题后重新写入 {{OUTPUT_PATH}} 。
注意：
- 你已经读取过 skill/example/tools 文件，不需要重新读取
- 保持其他正确部分不变，只修复列出的问题
- 修复后输出摘要："Fixed: <修复内容简述>"
```

由于在同一会话中，LLM 拥有之前所有步骤的上下文（读取过的规则、示例、tool 列表、生成过的 YAML），修复时无需重复读取文件，直接针对性修改即可。

## 5.3 cli_gen_skill.md 完整内容

存储位置：`mcp2cli/generator/templates/cli_gen_skill.md`

```markdown
# CLI 命令树生成规则

## 目标

将 MCP server 的扁平 tool 列表转化为层级式命令树，使命令路径符合人类直觉，支持渐进式披露。

## 分层原则

命令树最多 4 层，从上到下依次为：

| 层级 | 含义 | 示例 |
|------|------|------|
| 第 1 层 | 产品/领域 | jira, confluence, github |
| 第 2 层 | 资源类型 | issue, page, sprint, board |
| 第 3 层 | 操作动词 | create, get, list, search |
| 第 4 层 | 仅在必要时 | 子资源操作（极少使用） |

### 分层决策规则

1. **先看 tool 名称前缀**：tool 名中通常包含领域和资源信息
   - `jira_create_issue` → jira / issue / create
   - `confluence_get_page` → confluence / page / get
   - `jira_get_sprint_issues` → jira / sprint / issues（或展平为 jira / sprint / list）

2. **少于 5 个 tool 的 server**：不分第 1 层，直接从资源层开始
   - 例：只有 `run_query`, `list_tables` → query / run, table / list

3. **单个 tool 的 server**：不分层，直接作为叶子节点
   - 例：只有 `execute` → commands 下直接 execute

4. **无法自然分组的 tool**：放入 `misc` 或 `other` 分组

5. **tool 数量少于 3 个但属于同一领域**：可以不分资源层，直接 领域/操作
   - 例：只有 `confluence_search` → confluence / search（不需要中间层）

## 操作动词规范

叶子节点的命令名（操作动词）应统一为以下标准动词：

| 标准动词 | 适用场景 | 来源 tool 名中的常见词 |
|----------|----------|----------------------|
| `create` | 创建新资源 | create, add, new, insert |
| `get` | 获取单个资源详情 | get, fetch, read, show, view |
| `list` | 列出多个资源 | list, get_all, get_many, fetch_all |
| `search` | 按条件搜索 | search, query, find, filter |
| `update` | 修改现有资源 | update, edit, modify, set, change |
| `delete` | 删除资源 | delete, remove, destroy, drop |
| `move` | 移动/转移资源 | move, transfer, relocate |
| `download` | 下载/导出 | download, export, dump |
| `upload` | 上传/导入 | upload, import, attach |
| `link` | 建立关联 | link, connect, associate, add_to |
| `unlink` | 取消关联 | unlink, disconnect, remove_from |
| `transition` | 状态流转 | transition, change_status |

如果 tool 的操作不符合以上任何动词，保留其原始操作名（如 `batch-create`, `reply`）。

## YAML 格式规范

### 文件结构

```yaml
server: <server-name>
generated_at: "<ISO 8601 时间戳>"
generated_by: ai

server_aliases:
  - <别名>

command_shortcuts:
  - <快捷方式>

commands:
  <group>:
    _description: "<分组描述>"
    <resource>:
      _description: "<资源描述>"
      <action>:
        _tool: <MCP tool 原始名称>
        _description: "<操作描述>"
        _examples:
          - "<使用示例>"
```

### 元数据字段规范

| 字段 | 位置 | 必需 | 说明 |
|------|------|------|------|
| `_tool` | 叶子节点 | 是 | MCP tool 原始名称，必须与 tools/*.json 中的名称完全匹配 |
| `_description` | 所有节点 | 是 | 简短英文描述（一句话，首字母大写，无句号） |
| `_examples` | 叶子节点 | 可选 | 使用示例列表，每个示例是完整命令（含 mcp2cli 前缀） |
| `_param_aliases` | 叶子节点 | 可选 | 参数缩写映射 `{短名: 长名}` |

### 键名规则

- 子命令名（非 `_` 前缀）使用 **小写字母和连字符**：`issue`, `page`, `batch-create`
- 不使用下划线（`_` 前缀保留给元数据）
- 不使用驼峰命名

## server_aliases 自动生成规则

为 server 名称生成简短别名：

1. 去除 `mcp-` 前缀：`mcp-atlassian` → `atlassian`
2. 去除 `@scope/` 前缀：`@modelcontextprotocol/github` → `github`
3. 去除 `-mcp` 后缀：`atlassian-mcp` → `atlassian`
4. 若结果与管理命令同名（list, scan, generate, daemon, tools, call）→ 不生成
5. 若 server 名本身已经很短（无前后缀可去）→ 不生成别名

## command_shortcuts 自动生成规则

将 commands 下的顶层 key 注册为快捷方式：

1. 顶层命令名是**特定领域词**（jira, confluence, github, slack 等）→ 加入
2. 顶层命令名是**通用动词**（search, list, get, create, run 等）→ 不加入
3. 与管理命令同名 → 不加入
4. 只有一个顶层命令时 → 不生成（无快捷的必要）

## 描述撰写规范

- 语言：英文
- 中间节点 `_description`：描述该分组/资源是什么（名词短语）
  - 好：`"Issue operations"`, `"Sprint management"`
  - 差：`"Create and manage issues"`, `"Commands for sprints"`
- 叶子节点 `_description`：描述该操作做什么（动词开头的短语）
  - 好：`"Create a new issue"`, `"Search issues using JQL"`
  - 差：`"Issue creation"`, `"JQL search"`

## 示例选取规则

`_examples` 字段的值应为最常用、最具代表性的调用示例。规则：

1. 每个叶子节点 0-2 个示例
2. 只为**高频操作**（create, search）提供示例，低频操作可省略
3. 示例中使用 server 全名路径：`mcp2cli <server> <group> <resource> <action> --arg val`
4. 参数值使用真实感强的占位值：`--project INFRA`, `--summary "Fix memory leak"`
```

## 5.4 cli_gen_example.md 完整内容

存储位置：`mcp2cli/generator/templates/cli_gen_example.md`

```markdown
# CLI 映射文件示例

以下是一个完整的 `cli/<server>.yaml` 示例，展示了标准的输出格式。
请严格按照此格式生成。

## 示例：mcp-atlassian.yaml

```yaml
server: mcp-atlassian
generated_at: "2026-04-02T10:00:00Z"
generated_by: ai

server_aliases:
  - atlassian

command_shortcuts:
  - jira
  - confluence

commands:
  jira:
    _description: "JIRA project management"
    issue:
      _description: "Issue operations"
      create:
        _tool: jira_create_issue
        _description: "Create a new JIRA issue"
        _examples:
          - "mcp2cli mcp-atlassian jira issue create --project-key INFRA --summary 'Fix memory leak' --issue-type Task"
          - "mcp2cli mcp-atlassian jira issue create --project-key DEV --summary 'Add login' --issue-type Story --assignee john@example.com"
      get:
        _tool: jira_get_issue
        _description: "Get issue details by key"
        _examples:
          - "mcp2cli mcp-atlassian jira issue get --issue-key INFRA-1234"
      search:
        _tool: jira_search
        _description: "Search issues using JQL"
        _examples:
          - "mcp2cli mcp-atlassian jira issue search --jql 'project=INFRA AND status=Open'"
      update:
        _tool: jira_update_issue
        _description: "Update an existing issue"
      delete:
        _tool: jira_delete_issue
        _description: "Delete an existing issue"
      transition:
        _tool: jira_transition_issue
        _description: "Transition issue to a new status"
      link:
        _tool: jira_create_issue_link
        _description: "Create a link between two issues"
      comment:
        _description: "Issue comment operations"
        add:
          _tool: jira_add_comment
          _description: "Add a comment to an issue"
        edit:
          _tool: jira_edit_comment
          _description: "Edit an existing comment"
      watcher:
        _description: "Issue watcher operations"
        add:
          _tool: jira_add_watcher
          _description: "Add a watcher to an issue"
        remove:
          _tool: jira_remove_watcher
          _description: "Remove a watcher from an issue"
        list:
          _tool: jira_get_issue_watchers
          _description: "List watchers of an issue"
      worklog:
        _description: "Issue worklog operations"
        add:
          _tool: jira_add_worklog
          _description: "Add a worklog entry"
        list:
          _tool: jira_get_worklog
          _description: "Get worklog entries"
    sprint:
      _description: "Sprint operations"
      create:
        _tool: jira_create_sprint
        _description: "Create a new sprint"
      update:
        _tool: jira_update_sprint
        _description: "Update sprint details"
      list:
        _tool: jira_get_sprints_from_board
        _description: "List sprints for a board"
      issues:
        _tool: jira_get_sprint_issues
        _description: "Get issues in a sprint"
      add-issues:
        _tool: jira_add_issues_to_sprint
        _description: "Add issues to a sprint"
    board:
      _description: "Agile board operations"
      list:
        _tool: jira_get_agile_boards
        _description: "List agile boards"
      issues:
        _tool: jira_get_board_issues
        _description: "Get issues from a board"
    project:
      _description: "Project operations"
      list:
        _tool: jira_get_all_projects
        _description: "List all accessible projects"
      issues:
        _tool: jira_get_project_issues
        _description: "Get all issues in a project"
      components:
        _tool: jira_get_project_components
        _description: "Get project components"
      versions:
        _tool: jira_get_project_versions
        _description: "Get project fix versions"
    version:
      _description: "Version operations"
      create:
        _tool: jira_create_version
        _description: "Create a new fix version"
      batch-create:
        _tool: jira_batch_create_versions
        _description: "Batch create multiple versions"
    field:
      _description: "Field operations"
      search:
        _tool: jira_search_fields
        _description: "Search fields by keyword"
      options:
        _tool: jira_get_field_options
        _description: "Get allowed options for a field"
    link-type:
      _description: "Issue link type operations"
      list:
        _tool: jira_get_link_types
        _description: "List available link types"
  confluence:
    _description: "Confluence wiki operations"
    page:
      _description: "Page operations"
      get:
        _tool: confluence_get_page
        _description: "Get page content by ID or title"
        _examples:
          - "mcp2cli mcp-atlassian confluence page get --page-id 123456789"
          - "mcp2cli mcp-atlassian confluence page get --title 'Meeting Notes' --space-key TEAM"
      create:
        _tool: confluence_create_page
        _description: "Create a new page"
      update:
        _tool: confluence_update_page
        _description: "Update page content"
      delete:
        _tool: confluence_delete_page
        _description: "Delete a page"
      move:
        _tool: confluence_move_page
        _description: "Move a page to a new parent or space"
      children:
        _tool: confluence_get_page_children
        _description: "Get child pages of a page"
      history:
        _tool: confluence_get_page_history
        _description: "Get a historical version of a page"
      diff:
        _tool: confluence_get_page_diff
        _description: "Get diff between two page versions"
      views:
        _tool: confluence_get_page_views
        _description: "Get page view statistics"
      images:
        _tool: confluence_get_page_images
        _description: "Get all images from a page"
    search:
      _tool: confluence_search
      _description: "Search Confluence content"
      _examples:
        - "mcp2cli mcp-atlassian confluence search --query 'project documentation'"
    comment:
      _description: "Comment operations"
      list:
        _tool: confluence_get_comments
        _description: "Get comments for a page"
      add:
        _tool: confluence_add_comment
        _description: "Add a comment to a page"
      reply:
        _tool: confluence_reply_to_comment
        _description: "Reply to an existing comment"
    label:
      _description: "Label operations"
      list:
        _tool: confluence_get_labels
        _description: "Get labels for content"
      add:
        _tool: confluence_add_label
        _description: "Add a label to content"
    attachment:
      _description: "Attachment operations"
      list:
        _tool: confluence_get_attachments
        _description: "List attachments for content"
      upload:
        _tool: confluence_upload_attachment
        _description: "Upload an attachment"
      batch-upload:
        _tool: confluence_upload_attachments
        _description: "Upload multiple attachments"
      download:
        _tool: confluence_download_attachment
        _description: "Download an attachment"
      download-all:
        _tool: confluence_download_content_attachments
        _description: "Download all attachments for content"
      delete:
        _tool: confluence_delete_attachment
        _description: "Delete an attachment"
    user:
      _description: "User operations"
      search:
        _tool: confluence_search_user
        _description: "Search Confluence users"
```

## 格式要点

1. **顶层元数据**：`server`, `generated_at`, `generated_by`, `server_aliases`, `command_shortcuts`
2. **commands 树**：嵌套的 YAML 字典，`_` 前缀为元数据，其余为子命令
3. **叶子节点**：必有 `_tool` 和 `_description`，可选 `_examples` 和 `_param_aliases`
4. **中间节点**：只有 `_description`，其余键为子节点
5. **search 等单 tool 操作**：可直接挂在上层分组下，无需额外资源层
```

## 5.5 --merge 模式详细设计

### 5.5.1 触发场景

MCP server 新增了 tool（如升级版本后），用户希望保留已有的手动调整，只处理增量：

```bash
# server 升级后重新扫描
mcp2cli scan mcp-atlassian
# Found 15 tools (was 12)

# 增量更新命令树
mcp2cli generate cli mcp-atlassian --merge
# Merged: 3 new tools added, 12 existing preserved, 0 deprecated
```

### 5.5.2 差异处理策略

| 情况 | 处理 |
|------|------|
| tool 在 tools/*.json 中存在，在 cli/*.yaml 中已映射 | 保持不变（保留描述、示例、别名） |
| tool 在 tools/*.json 中存在，在 cli/*.yaml 中未映射 | 新增映射节点 |
| tool 在 cli/*.yaml 中映射，但 tools/*.json 中不存在 | 标记 `_deprecated: true` |
| server_aliases 和 command_shortcuts | 保持不变，不重新生成 |
| `generated_by` 字段 | 改为 `"ai-merge"` |

### 5.5.3 保护机制

- 已有的 `_description`、`_examples`、`_param_aliases` 不可被修改
- 已有的命令层级结构不可被重组
- 新增 tool 应尽量融入已有结构（如已有 jira/issue 分组，新增的 jira issue 相关 tool 放入该分组）

## 5.6 可配置 LLM 后端

### 5.6.1 配置文件

`~/.agents/mcp2cli/config.yaml`：

```yaml
llm:
  # 后端类型: claude-cli | codex | anthropic-sdk | openai-compatible
  backend: claude-cli

  # claude-cli 配置（默认）
  claude_cli:
    command: claude           # claude 可执行文件路径
    model: opus               # 模型选择: opus | sonnet | haiku

  # codex 配置
  codex:
    command: codex            # codex 可执行文件路径
    model: opus               # 模型选择

  # anthropic-sdk 配置
  anthropic_sdk:
    api_key_env: ANTHROPIC_API_KEY   # API key 环境变量名
    model: claude-sonnet-4-6-20250514
    max_tokens: 16384

  # openai-compatible 配置
  openai_compatible:
    base_url: https://api.openai.com/v1
    api_key_env: OPENAI_API_KEY
    model: gpt-4o
    max_tokens: 16384
```

### 5.6.2 各后端调用方式

**claude-cli（默认）：**

```bash
# 首次调用 — 返回 JSON 含 session_id
claude -p "<assembled_prompt>" \
  --output-format json \
  --model opus \
  --allowedTools "Read,Write,Bash"

# 校验失败时 — 在同一会话中续接
claude -p "<error_prompt>" \
  --output-format json \
  --resume <session_id>
```

使用 `--output-format json` 获取结构化响应，其中 `session_id` 用于后续重试的会话续接。
使用 `--allowedTools "Read,Write,Bash"` 限制 LLM 只能读写文件和执行命令。LLM 通过 Read 工具读取 skill/example/tools 文件，通过 Write 工具写入 cli/*.yaml，通过 Bash 工具执行 `mcp2cli validate` 进行自验。

**codex：**

```bash
# 首次调用 — 返回 JSON 含 session_id
codex exec --json "<assembled_prompt>"

# 返回 JSON:
# {
#   "session_id": "019d4d5e-71ac-7100-b2d1-6023471ff0dd",
#   "result": "Generated: 65 tools mapped to 52 cmds",
#   ...
# }
#
# → 程序提取 session_id，保存备用
# → 程序读取 cli/<server>.yaml，执行校验

# 校验失败时 — 在同一会话中续接
codex resume 019d4d5e-71ac-7100-b2d1-6023471ff0dd "<error_prompt>"
```

使用 `codex exec --json` 获取结构化响应，其中 `session_id` 用于后续通过 `codex resume` 续接会话。Codex 与 claude-cli 类似，LLM 具有文件系统访问权限，可自行读取文件和执行 `mcp2cli validate` 命令。

**anthropic-sdk：**

使用 Anthropic Python SDK 调用 API。需要将 skill/example/tools 文件内容作为 prompt 的一部分内联传入（SDK 模式下 LLM 无文件系统访问权限）。重试时通过 `messages` 数组追加对话历史实现会话续接。

**openai-compatible：**

使用 OpenAI 兼容接口。同样需要内联文件内容。重试时通过 `messages` 数组追加对话历史。

### 5.6.3 后端降级策略

| 后端 | Prompt 模式 | LLM 文件访问 | 文件内容 | 会话续接方式 |
|------|------------|-------------|---------|-------------|
| claude-cli | 文件引用模式 | 有（通过 Read/Write/Bash 工具） | LLM 自行读取 | `--resume <session_id>` |
| codex | 文件引用模式 | 有（通过工具） | LLM 自行读取 | `codex resume <session_id>` |
| anthropic-sdk | 内联模式 | 无 | 程序读取后内联到 prompt | messages 数组追加 |
| openai-compatible | 内联模式 | 无 | 程序读取后内联到 prompt | messages 数组追加 |

当使用 anthropic-sdk 或 openai-compatible 后端时，程序需要：
1. 预先读取 `cli_gen_skill.md`、`cli_gen_example.md`、`tools/<server>.json` 的内容
2. 将文件内容嵌入 prompt 中（替代"读取文件"指令）
3. 从 LLM 响应中提取 YAML 内容（而非由 LLM 写入文件）
4. 程序侧负责写入 `cli/<server>.yaml`

## 5.7 校验流程

### 5.7.1 校验项

LLM 生成 YAML 后，以下校验逻辑会在两处执行：
1. **LLM 自验**：LLM 通过 Bash 调用 `mcp2cli validate <server>` 命令，在 LLM 会话内自行检查并修复
2. **程序侧兜底**：LLM 返回后，程序再次调用同一校验逻辑做最终确认

`mcp2cli validate <server>` 命令执行以下校验：

```
┌─ 校验 1: YAML 语法 ─────────────────────────┐
│  尝试 yaml.safe_load()                       │
│  失败 → 报 YAML 语法错误 + 错误位置           │
└──────────────────────────────────────────────┘
                    │ 通过
                    ▼
┌─ 校验 2: 结构合法性 ────────────────────────┐
│  - 顶层必须有 server, commands 字段           │
│  - commands 不为空                           │
│  - 所有叶子节点必须有 _tool 字段              │
│  - 所有中间节点必须有 _description 字段       │
│  - 子命令名不以 _ 开头                       │
│  - 子命令名只含小写字母、数字、连字符         │
└──────────────────────────────────────────────┘
                    │ 通过
                    ▼
┌─ 校验 3: tool 映射完整性 ───────────────────┐
│  从 tools/<server>.json 获取所有 tool 名列表  │
│  从 YAML 中提取所有 _tool 值                  │
│                                              │
│  a) 未映射的 tool（在 JSON 中但不在 YAML 中） │
│     → 错误：Missing tools: [tool1, tool2]    │
│                                              │
│  b) 无效的 _tool（在 YAML 中但不在 JSON 中）  │
│     → 错误：Invalid tools: [tool3]           │
│                                              │
│  c) 重复映射（同一 tool 出现多次）             │
│     → 警告：Duplicate mappings: [tool4]      │
└──────────────────────────────────────────────┘
                    │ 通过
                    ▼
┌─ 校验 4: 命令路径合法性 ────────────────────┐
│  - 无重复的命令路径                           │
│  - 路径深度 ≤ 4                              │
│  - 快捷方式不与管理命令冲突                   │
└──────────────────────────────────────────────┘
```

### 5.7.2 重试策略（两层校验）

```
首次调用 claude -p (--output-format json, --allowedTools "Read,Write,Bash")
  │
  │  LLM 内部：
  │  ├─ 生成 YAML → 写入文件
  │  ├─ 调用 mcp2cli validate <server>
  │  ├─ 校验失败 → 自行修复 → 再次 validate（LLM 自主循环）
  │  └─ 校验通过 → 返回结果
  │
  │  ← 返回 session_id + result
  ▼
程序侧兜底校验（同一校验逻辑）
  │
  ├─ 通过 → 完成 ✓
  │
  └─ 失败 → claude -p "<errors>" --resume <session_id>
              │
              │  ← LLM 保留完整上下文，针对性修复 + 再次 validate
              ▼
           程序侧兜底校验
              │
              ├─ 通过 → 完成 ✓
              │
              └─ 失败 → 报错退出
                        提示用户手动修复
                        或切换 LLM 后端
```

由于 LLM 会话中已包含自验步骤，大部分校验问题会在 LLM 内部解决，程序侧重试的概率大幅降低。程序侧重试最多 1 次（对比原来的 2 次），因为自验已覆盖大部分场景。

### 5.7.3 校验报告输出

```
$ mcp2cli generate cli mcp-atlassian
Scanning mcp-atlassian... 65 tools found.
Generating command tree...
LLM self-validation passed ✓
Program validation passed ✓
  - 65/65 tools mapped
  - 5 groups, 18 resources, 65 actions
  - Depth: max 4 layers
  - Aliases: atlassian
  - Shortcuts: jira, confluence
Written to ~/.agents/mcp2cli/cli/mcp-atlassian.yaml

# LLM 自验通过但程序兜底发现问题时
$ mcp2cli generate cli some-server
Scanning some-server... 8 tools found.
Generating command tree...
LLM self-validation passed ✓
Program validation failed (attempt 1/2):
  - Missing tools: [some_tool_x]
Retrying with error context...
Program validation passed ✓ (attempt 2/2)
Written to ~/.agents/mcp2cli/cli/some-server.yaml

# 校验命令独立使用
$ mcp2cli validate mcp-atlassian
Validating ~/.agents/mcp2cli/cli/mcp-atlassian.yaml...
✓ YAML syntax valid
✓ Structure valid
✓ 65/65 tools mapped (100% coverage)
✓ No path conflicts (max depth: 4)
All checks passed ✓
```

## 5.8 文件布局变更

在项目源码中新增模板文件：

```
mcp2cli/
└── generator/
    ├── cli_gen.py                # AI 生成命令映射（组装 prompt、调用 LLM、校验）
    └── templates/
        ├── cli_gen_skill.md      # 生成规则和约束（5.3）
        ├── cli_gen_example.md    # 示例 YAML 输出（5.4）
        └── skill.md.j2           # Jinja2 模板（SKILL.md 生成用）
```
