# 16. Preset Skills（远程预设仓库）

本文档是 [0.0-design-overview.md](0.0-design-overview.md) 第十三章的展开设计，描述预转换 skill 的远程托管、拉取和集成机制。

## 16.1 功能概述

mcp2cli 的 `convert` 和 `install` 流程中，`scan` + `generate cli` + `generate skill` 三步需要启动 MCP server 并调用 LLM，耗时约 2-3 分钟。对于常用的 MCP server（如 mcp-atlassian、playwright 等），这些生成结果是通用的、可复用的。

**Preset Skills** 将常用 MCP server 的全部转换产物（tools JSON、CLI YAML、SKILL.md + reference/ + users/workflows.md）预先生成并托管在远程 GitHub 仓库。用户在 `convert` 或 `install` 时，系统自动检查是否存在可用 preset：

- **有 preset**：提示用户拉取，跳过 scan + generate cli + generate skill，直接进入 skill sync
- **无 preset**：继续正常 AI 生成流程

**核心收益**：
- 新用户安装常用 server 从 ~3 分钟缩短到 ~10 秒（省去 AI 生成和 MCP server 启动时间）
- 无需本地配置 LLM 后端即可使用常用 server 的 skill
- 社区可贡献 preset，扩大覆盖范围

## 16.2 远程仓库结构

GitHub 仓库 `mcp2cli-presets`（公开仓库），结构如下（多版本）：

```
mcp2cli-presets/
├── index.json                    # 全局索引（所有可用 preset 及版本列表）
└── presets/
    ├── mcp-atlassian/
    │   ├── latest.json           # {"version": "1.3.0"} — 指向最新版本
    │   ├── 1.2.3/
    │   │   ├── manifest.json
    │   │   ├── tools.json
    │   │   ├── cli.yaml
    │   │   └── skills/
    │   │       ├── SKILL.md
    │   │       ├── reference/
    │   │       │   ├── jira-issue.md
    │   │       │   ├── jira-sprint.md
    │   │       │   └── confluence-page.md
    │   │       └── users/
    │   │           └── workflows.md
    │   └── 1.3.0/
    │       ├── manifest.json
    │       ├── tools.json
    │       ├── cli.yaml
    │       └── skills/...
    ├── playwright/
    │   ├── latest.json
    │   └── 0.5.0/
    │       ├── manifest.json
    │       └── ...
    └── mcp-github/
        └── ...
```

**与旧结构（v1，无版本子目录）的兼容**：客户端优先请求 `presets/{server}/{version}/manifest.json`，404 时回退到 `presets/{server}/manifest.json`（旧仓库扁平结构）。

### 16.2.1 index.json 格式

全局索引文件，列出所有可用 preset 的元数据摘要，客户端首次请求时下载并缓存：

```json
{
  "version": 2,
  "updated_at": "2026-04-03T00:00:00Z",
  "presets": [
    {
      "server": "mcp-atlassian",
      "latest": "1.3.0",
      "versions": ["1.3.0", "1.2.3"],
      "description": "JIRA + Confluence operations",
      "updated_at": "2026-04-03T00:00:00Z",
      "server_version": "1.3.0",
      "tool_count": 68
    },
    {
      "server": "playwright",
      "latest": "0.5.0",
      "versions": ["0.5.0"],
      "description": "Browser automation",
      "updated_at": "2026-03-28T00:00:00Z",
      "server_version": "0.5.0",
      "tool_count": 12
    },
    {
      "server": "mcp-github",
      "latest": "1.0.0",
      "versions": ["1.0.0"],
      "description": "GitHub repos, issues, PRs, and releases",
      "updated_at": "2026-03-25T00:00:00Z",
      "server_version": "1.0.0",
      "tool_count": 30
    }
  ]
}
```

| 字段 | 说明 |
|------|------|
| `version` | index 格式版本号，当前为 2（v1 兼容见下方说明） |
| `updated_at` | index 最后更新时间 |
| `presets[].server` | MCP server 名称（与 servers.yaml 中的 key 一致） |
| `presets[].latest` | 最新可用版本号 |
| `presets[].versions` | 所有可用版本列表（降序排列） |
| `presets[].description` | 一行描述 |
| `presets[].updated_at` | 该 preset 的最后更新时间 |
| `presets[].server_version` | （v1 兼容）等同于 `latest`，旧客户端使用此字段 |
| `presets[].tool_count` | （v1 兼容）最新版本的 tool 数量 |

**v1 → v2 向后兼容**：
- 新 index 保留 `server_version` 和 `tool_count` 字段，使旧客户端（不识别 `latest`/`versions`）仍可正常工作
- 新客户端读到 v1 index 时，将 `server_version` 映射为 `latest`，`versions` 设为 `[server_version]`

### 16.2.2 manifest.json 格式

每个 preset 目录下的详细元数据，客户端在 pull 时下载：

```json
{
  "server": "mcp-atlassian",
  "server_version": "1.2.3",
  "tool_count": 65,
  "cli_hash": "a3f8c2d1",
  "generated_at": "2026-04-01T00:00:00Z",
  "generated_by": "preset",
  "files": [
    "tools.json",
    "cli.yaml",
    "skills/SKILL.md",
    "skills/reference/jira-issue.md",
    "skills/reference/jira-sprint.md",
    "skills/reference/jira-board.md",
    "skills/reference/jira-project.md",
    "skills/reference/confluence-page.md",
    "skills/reference/confluence-attachment.md",
    "skills/users/workflows.md"
  ]
}
```

| 字段 | 说明 |
|------|------|
| `cli_hash` | CLI YAML 内容的 SHA-256 前 8 位（与 SKILL.md frontmatter 中的 `source_cli_hash` 一致） |
| `generated_by` | 固定为 `"preset"` |
| `files` | 需要下载的文件列表（相对于 preset 目录） |

## 16.3 命令接口

### 16.3.1 mcp2cli preset list

```bash
mcp2cli preset list [SERVER_NAME] [OPTIONS]

Arguments:
  server-name  (可选) 查看某个 preset 的所有可用版本

Options:
  --refresh    强制刷新远程索引（忽略本地缓存）
```

列出远程仓库中所有可用的 preset：

```
$ mcp2cli preset list
Available presets:
  NAME              LATEST    VERSIONS                UPDATED
  mcp-atlassian     1.3.0     1.3.0, 1.2.3            2026-04-03
  playwright        0.5.0     0.5.0                   2026-03-28
  mcp-github        1.0.0     1.0.0                   2026-03-25
  mcp-slack         0.8.2     0.8.2, 0.7.0            2026-03-20

4 presets available. Use 'mcp2cli preset pull <name>' to download.
```

查看某个 preset 的详细版本信息：

```
$ mcp2cli preset list mcp-atlassian
Preset: mcp-atlassian
  Latest:      1.3.0
  Versions:    1.3.0, 1.2.3
  Updated:     2026-04-03
  Description: JIRA + Confluence operations

Use 'mcp2cli preset pull mcp-atlassian@<version>' to download a specific version.
```

### 16.3.2 mcp2cli preset pull

```bash
mcp2cli preset pull <server-name[@version]> [OPTIONS]

Arguments:
  server-name[@version]   要拉取的 preset 名称，可选 @version 指定版本
                          不指定版本时拉取 latest

Options:
  --sync           拉取后自动执行 skill sync（复制到各客户端 + disable MCP）
  --force          已有本地文件时强制覆盖
  --dry-run        只展示将要下载的文件，不实际下载
```

拉取指定 server 的 preset 到本地运行时目录：

```
$ mcp2cli preset pull mcp-atlassian
⬇ Pulling mcp-atlassian preset (v1.3.0, latest)...
   ✓ tools/mcp-atlassian.json
   ✓ cli/mcp-atlassian.yaml
   ✓ skills/mcp-atlassian/SKILL.md
   ✓ skills/mcp-atlassian/reference/ (6 files)
   ✓ skills/mcp-atlassian/users/workflows.md
Done! Files written to ~/.agents/mcp2cli/

$ mcp2cli preset pull mcp-atlassian@1.2.3
⬇ Pulling mcp-atlassian preset (v1.2.3)...
   ✓ tools/mcp-atlassian.json
   ✓ cli/mcp-atlassian.yaml
   ✓ skills/mcp-atlassian/ (SKILL.md + reference + users/workflows.md)
Done! Files written to ~/.agents/mcp2cli/
```

带 `--sync`：

```
$ mcp2cli preset pull mcp-github --sync
⬇ Pulling mcp-github preset (v1.0.0)...
   ✓ tools, cli, skills downloaded

🔗 Syncing skill to AI clients...
   ✓ claude ✓ cursor ✓ codex
Done!
```

### 16.3.3 convert/install 的 preset 选项

```bash
mcp2cli convert mcp-atlassian --no-preset           # 跳过 preset 检查，强制走 AI 生成
mcp2cli install mcp-atlassian --no-preset           # 同上
mcp2cli install mcp-atlassian --preset-version=1.2.3 # 使用指定版本的 preset
```

## 16.4 Pipeline 集成

### 16.4.1 Step 扩展

在 `installer/pipeline.py` 的 Step dataclass 中新增 `skip_if` 字段：

```python
@dataclass
class Step:
    name: str
    run: Callable
    retry_cmd: str
    depends_on: list[str] = field(default_factory=list)
    skip_if: list[str] = field(default_factory=list)
    # skip_if 列表中任意一步成功，本步自动跳过（标记为 skipped 而非 failed）
```

### 16.4.2 Runner 扩展

```python
results: dict[str, bool] = {}
for step in pipeline:
    # 依赖失败 → 跳过
    if any(not results.get(dep) for dep in step.depends_on):
        warn(f"Skipping {step.name}: dependency failed")
        results[step.name] = False
        continue

    # 条件跳过（preset 成功时 scan/generate 无需执行）
    if any(results.get(s) for s in step.skip_if):
        info(f"Skipping {step.name}: preset used")
        results[step.name] = True   # 标记为成功，不阻塞后续依赖
        continue

    ok = step.run()
    results[step.name] = ok
    if not ok:
        warn(f"{step.name} failed. Retry later: {step.retry_cmd}")
```

**设计说明**：
- `skip_if` 与 `depends_on` 互不冲突：前者表示"某步成功时本步可跳过"，后者表示"某步失败时本步不可执行"
- 空 `skip_if` 列表等价于无跳过逻辑，不影响现有 pipeline 的行为

### 16.4.3 Install Pipeline（修改后）

```python
pipeline: list[Step] = [
    Step(
        name="mcp-install",
        run=lambda: run_mcp_install(server_name),
        retry_cmd=f"mcp2cli mcp install {server_name}",
    ),
    Step(
        name="preset-check",                          # ← 新增
        run=lambda: check_and_pull_preset(server_name),
        retry_cmd=f"mcp2cli preset pull {server_name}",
        depends_on=["mcp-install"],
    ),
    Step(
        name="scan",
        run=lambda: run_scan(server_name),
        retry_cmd=f"mcp2cli scan {server_name}",
        depends_on=["mcp-install"],
        skip_if=["preset-check"],                     # ← preset 成功时跳过
    ),
    Step(
        name="generate-cli",
        run=lambda: run_generate_cli(server_name),
        retry_cmd=f"mcp2cli generate cli {server_name}",
        depends_on=["scan"],
        skip_if=["preset-check"],                     # ← preset 成功时跳过
    ),
    Step(
        name="generate-skill",
        run=lambda: run_generate_skill(server_name),
        retry_cmd=f"mcp2cli generate skill {server_name}",
        depends_on=["generate-cli"],
        skip_if=["preset-check"],                     # ← preset 成功时跳过
    ),
    Step(
        name="skill-sync",
        run=lambda: run_skill_sync(server_name),
        retry_cmd=f"mcp2cli skill sync {server_name}",
        depends_on=["generate-skill"],
        # 注意：skill-sync 的 depends_on 中 generate-skill 被 skip_if 标记为
        # True（成功），因此 skill-sync 不会被阻塞
    ),
]
```

### 16.4.4 Convert Pipeline（修改后）

```python
pipeline: list[Step] = [
    Step(
        name="extract-config",
        run=lambda: extract_and_write(server_name, source, force),
        retry_cmd=f"mcp2cli convert {server_name}",
    ),
    Step(
        name="preset-check",                          # ← 新增
        run=lambda: check_and_pull_preset(server_name),
        retry_cmd=f"mcp2cli preset pull {server_name}",
        depends_on=["extract-config"],
    ),
    Step(
        name="scan",
        run=lambda: run_scan(server_name),
        retry_cmd=f"mcp2cli scan {server_name}",
        depends_on=["extract-config"],
        skip_if=["preset-check"],                     # ← preset 成功时跳过
    ),
    Step(
        name="generate-cli",
        run=lambda: run_generate_cli(server_name),
        retry_cmd=f"mcp2cli generate cli {server_name}",
        depends_on=["scan"],
        skip_if=["preset-check"],
    ),
    Step(
        name="generate-skill",
        run=lambda: run_generate_skill(server_name),
        retry_cmd=f"mcp2cli generate skill {server_name}",
        depends_on=["generate-cli"],
        skip_if=["preset-check"],
    ),
    Step(
        name="skill-sync",
        run=lambda: run_skill_sync(server_name, skip_disable=skip_disable),
        retry_cmd=f"mcp2cli skill sync {server_name}",
        depends_on=["generate-skill"],
    ),
]
```

### 16.4.5 preset-check 步骤内部流程

```
check_and_pull_preset(server_name)
        │
        ├── 1. 检查 --no-preset 标志 → 是 → return False（跳过 preset）
        │
        ├── 2. 拉取远程 index.json（带缓存）
        │   → 网络失败 → warn + return False（回退到正常流程）
        │
        ├── 3. 在 index 中查找 server_name
        │   → 不存在 → info("No preset found for <server>") + return False
        │
        ├── 4. 检查本地是否已有文件
        │   → 已有且非 --force → 提示 "Already exists. Overwrite? [Y/n]"
        │     → N → return False
        │
        ├── 5. 展示 preset 信息 + 确认
        │   "📦 Pre-generated skill files found for <server>:
        │      Version: 1.2.3 | Tools: 65 | Updated: 2026-04-01
        │      Pull and use preset? [Y/n]"
        │   → N → return False
        │   → --yes → 跳过确认
        │
        └── 6. 下载 preset 文件
            ├── 下载 manifest.json → 获取文件列表
            ├── 逐个下载 files 列表中的文件
            │   → tools.json → ~/.agents/mcp2cli/tools/<server>.json
            │   → cli.yaml   → ~/.agents/mcp2cli/cli/<server>.yaml
            │   → skills/    → ~/.agents/mcp2cli/skills/<server>/
            ├── 创建 users/ 目录 + .gitkeep（如不存在）
            └── return True（标记 preset 使用成功）
```

## 16.5 版本不匹配处理

preset 绑定特定 MCP server 版本。用户本地的 server 版本可能与 preset 不同。

| 场景 | 行为 |
|------|------|
| preset 版本 = 本地 server 版本 | 直接使用，无额外提示 |
| preset 版本 ≠ 本地版本（任一方更新） | 提示版本差异："Preset is for v1.2.3, your server may differ. Pull anyway? You can run `mcp2cli update` later to sync." |
| 本地 server 版本未知（尚未 scan） | 直接使用 preset，提示后续可 `mcp2cli update` |
| preset 版本为 null | 按 tool_count 提示，不做版本对比 |

**核心策略：先用后校验**——preset 提供命令树结构作为起点，如果用户的 server 版本有差异，通过 `mcp2cli update` 的增量更新机制自动处理（scan 新版本 → diff → generate cli --merge + generate skill）。

**版本差异示例：**

```
$ mcp2cli install mcp-atlassian
✓ servers.yaml: mcp-atlassian added

📦 Pre-generated skill files found for mcp-atlassian:
   Version: 1.2.3 | Tools: 65 | Updated: 2026-04-01
   ⚠ Note: Preset version may differ from your installed server.
     Run 'mcp2cli update mcp-atlassian' after install to sync.
   Pull and use preset? [Y/n] y

⬇ Pulling preset... ✓
...
```

## 16.6 下载机制

### 16.6.1 HTTP 直接下载

通过 GitHub raw URL 下载文件，不依赖 git/gh CLI：

```python
# 默认仓库地址
PRESET_REPO_URL = "https://raw.githubusercontent.com/<org>/mcp2cli-presets/main"

# 可通过 config.yaml 覆盖
# ~/.agents/mcp2cli/config.yaml
# preset:
#   repo_url: "https://raw.githubusercontent.com/myorg/mcp2cli-presets/main"
```

**URL 构造规则（多版本）：**

```
index.json    → {PRESET_REPO_URL}/index.json
manifest.json → {PRESET_REPO_URL}/presets/{server}/{version}/manifest.json
tools.json    → {PRESET_REPO_URL}/presets/{server}/{version}/tools.json
cli.yaml      → {PRESET_REPO_URL}/presets/{server}/{version}/cli.yaml
skills/...    → {PRESET_REPO_URL}/presets/{server}/{version}/skills/...
```

**回退（旧仓库兼容）**：若 `{server}/{version}/manifest.json` 返回 404，回退到 `{server}/manifest.json`（扁平结构）。

### 16.6.2 本地缓存策略

**仅缓存 index.json**：

```
~/.agents/mcp2cli/.preset-cache/
├── index.json       # 远程 index 的本地缓存
└── index.meta.json  # 缓存元数据（ETag、缓存时间）
```

```json
// index.meta.json
{
  "etag": "\"abc123\"",
  "cached_at": "2026-04-03T10:00:00Z"
}
```

- TTL 默认 24 小时，可通过 `config.yaml` 的 `preset.cache_ttl_hours` 配置
- 请求时发送 `If-None-Match` 头（ETag 条件请求），304 时使用缓存
- `mcp2cli preset list --refresh` 强制刷新

**Preset 文件不缓存**：直接写入最终目标位置（`tools/`、`cli/`、`skills/`），不做中间缓存。重复 pull 直接覆盖。

### 16.6.3 网络容错

| 场景 | 行为 |
|------|------|
| 无网络（DNS/连接超时） | 跳过 preset-check，打印 `⚠ Could not reach preset repository. Proceeding with AI generation.` |
| index.json 下载成功但某文件失败 | 中止 pull，回退到正常流程，打印 `⚠ Preset download failed. Proceeding with AI generation.` |
| HTTP 非 200 响应 | 同上 |

**超时设置**：index.json 请求超时 5 秒，单个文件下载超时 10 秒。

## 16.7 CLI YAML 标记

preset 拉取的 CLI YAML 中 `generated_by` 字段设为 `preset`（区别于 `ai` 和 `manual`）：

```yaml
# ~/.agents/mcp2cli/cli/mcp-atlassian.yaml
server: mcp-atlassian
version: "1.2.3"
generated_at: "2026-04-01T00:00:00Z"
generated_by: preset                    # ← 标记来源
preset_source: "mcp2cli-presets"        # ← 仓库标识

commands:
  jira:
    _description: "JIRA project management"
    ...
```

**与 update 命令的交互**：

- `mcp2cli update` 检测到 `generated_by: preset` 时，行为与 `generated_by: ai` 相同——执行 `generate cli --merge` 增量更新
- update 完成后 `generated_by` 更新为 `ai`（因为增量部分由 AI 生成）

## 16.8 配置

```yaml
# ~/.agents/mcp2cli/config.yaml
preset:
  repo_url: "https://raw.githubusercontent.com/<org>/mcp2cli-presets/main"
  auto_check: true          # convert/install 时自动检查 preset（默认 true）
  cache_ttl_hours: 24       # index.json 缓存时间（默认 24）
```

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `preset.repo_url` | 官方仓库 URL | 可替换为企业内部仓库 |
| `preset.auto_check` | `true` | 设为 `false` 等价于所有命令默认 `--no-preset` |
| `preset.cache_ttl_hours` | `24` | index.json 本地缓存有效期 |

## 16.9 代码结构

```
mcp2cli/
├── main.py                    # preset list / preset pull 子命令（支持 @version 语法）
├── preset/                    # preset 包
│   ├── __init__.py
│   ├── models.py              # PresetIndex, PresetEntry, Manifest 数据模型（多版本支持）
│   ├── registry.py            # fetch_index(), find_preset() - 远程索引查询 + 缓存
│   ├── downloader.py          # pull_preset() - 按 manifest 下载文件到目标目录（支持版本路径）
│   ├── checker.py             # check_and_pull_preset() - pipeline 集成的入口函数
│   └── version.py             # parse_preset_spec() - 解析 'name@version' 语法
├── installer/
│   └── pipeline.py            # Step dataclass 扩展 skip_if 字段 + runner 扩展
```

### 模块职责

**`preset/models.py`**：

```python
@dataclass
class PresetEntry:
    """index.json 中单个 preset 的元数据"""
    server: str
    latest: str                    # 最新版本号
    versions: list[str]            # 所有可用版本（降序）
    description: str
    updated_at: str
    server_version: str | None = None  # v1 兼容
    tool_count: int = 0                # v1 兼容

    def resolve_version(self, requested: str | None) -> str:
        """解析请求的版本号，None → latest，不存在 → ValueError"""

@dataclass
class PresetIndex:
    """index.json 的完整内容"""
    version: int
    updated_at: str
    presets: list[PresetEntry]

    def find(self, server_name: str) -> PresetEntry | None:
        """按 server 名查找 preset"""
        return next((p for p in self.presets if p.server == server_name), None)

@dataclass
class Manifest:
    """manifest.json 的完整内容"""
    server: str
    server_version: str | None
    tool_count: int
    cli_hash: str
    generated_at: str
    generated_by: str
    files: list[str]
```

**`preset/registry.py`**：

```python
def fetch_index(force_refresh: bool = False) -> PresetIndex | None:
    """
    下载远程 index.json，带本地缓存。

    - 优先使用缓存（TTL 内）
    - 发送 If-None-Match 条件请求
    - 304 → 使用缓存
    - 200 → 更新缓存
    - 网络失败 → 使用过期缓存（如有）或返回 None

    Returns:
        PresetIndex 或 None（网络不可用且无缓存）
    """

def find_preset(server_name: str) -> PresetEntry | None:
    """查找指定 server 的 preset，便捷封装"""
```

**`preset/downloader.py`**：

```python
def pull_preset(server_name: str, version: str | None = None, force: bool = False) -> bool:
    """
    下载 preset 的所有文件到本地运行时目录。

    流程：
    1. 解析版本：version=None → 从 index 获取 latest
    2. 下载 manifest.json（优先 {server}/{version}/manifest.json，404 回退到 {server}/manifest.json）
    3. 检查本地是否已有文件（非 --force 时提示）
    4. 逐个下载 manifest.files 列表中的文件
       - tools.json → ~/.agents/mcp2cli/tools/<server>.json
       - cli.yaml   → ~/.agents/mcp2cli/cli/<server>.yaml
       - skills/*   → ~/.agents/mcp2cli/skills/<server>/*
    5. 创建 users/ 目录 + .gitkeep（如不存在）

    Returns:
        True 下载成功，False 失败
    """

def download_file(url: str, target_path: Path) -> bool:
    """下载单个文件到目标路径（原子写入：先写临时文件再 rename）"""
```

**`preset/checker.py`**：

```python
def check_and_pull_preset(
    server_name: str,
    version: str | None = None,
    no_preset: bool = False,
    yes: bool = False,
    force: bool = False,
) -> bool:
    """
    pipeline 集成的入口函数。

    在 install/convert pipeline 中作为 preset-check 步骤使用。

    流程：
    1. --no-preset → return False
    2. 拉取 index → 查找 preset → 未找到 → return False
    3. 验证请求版本是否可用（如指定了 version）
    4. 展示 preset 信息 → 用户确认（--yes 跳过）→ 拒绝 → return False
    5. 检查已有文件 → 已有且非 --force → 提示覆盖
    6. 下载 preset（指定版本或 latest）→ 成功 → return True

    Returns:
        True 表示 preset 使用成功（后续步骤可跳过）
        False 表示需要继续正常流程
    """
```

## 16.10 端到端示例

### 16.10.1 Install 时发现 preset

```
$ mcp2cli install mcp-atlassian

🔍 Searching for mcp-atlassian installation info...
   Found: mcp-atlassian (PyPI)
   Source: https://github.com/sooperset/mcp-atlassian

📋 Environment variables required:
   JIRA_URL: > https://mycompany.atlassian.net
   JIRA_API_TOKEN: > ********

✓ servers.yaml: mcp-atlassian added

📦 Pre-generated skill files found for mcp-atlassian:
   Version: 1.2.3 | Tools: 65 | Updated: 2026-04-01
   Pull and use preset? [Y/n] y

⬇ Pulling preset...
   ✓ tools/mcp-atlassian.json (65 tools)
   ✓ cli/mcp-atlassian.yaml (65 commands)
   ✓ skills/mcp-atlassian/ (SKILL.md + 6 reference files + users/workflows.md)
   Skipping: scan, generate cli, generate skill (using preset)

🔗 Syncing skill to AI clients...
   ✓ ~/.claude/skills/mcp-atlassian  copied
   ✓ ~/.cursor/skills/mcp-atlassian  copied
   ✓ ~/.codex/skills/mcp-atlassian   copied
   MCP disabled in: claude, cursor

✅ Installation complete! (preset used, saved ~2 min of AI generation)
   Tip: run 'mcp2cli update mcp-atlassian' if your server version differs from v1.2.3.
```

### 16.10.2 Convert 时发现 preset

```
$ mcp2cli convert mcp-atlassian

🔍 Finding mcp-atlassian in config sources...
   Found in: ~/.claude.json (claude:global)
   Found in: ~/.cursor/mcp.json (cursor)

📋 Extracted config from ~/.claude.json:
   command: uvx
   args: [mcp-atlassian]
   env: JIRA_URL, JIRA_API_TOKEN (2 vars)

✓ servers.yaml: mcp-atlassian added

📦 Pre-generated skill files found for mcp-atlassian (v1.2.3, 65 tools).
   Pull and use preset? [Y/n] y

⬇ Pulling preset... ✓ (tools + cli + skills)
   Skipping: scan, generate cli, generate skill

🔗 Syncing skill...
   ✓ claude ✓ cursor ✓ codex

🔒 MCP server disabled in client configs:
   ✓ ~/.claude.json: mcp-atlassian disabled
   ✓ ~/.cursor/mcp.json: mcp-atlassian disabled

✅ Convert complete! (preset used)
```

### 16.10.3 无 preset 可用

```
$ mcp2cli install some-niche-server

🔍 Searching for some-niche-server installation info...
   Found: some-niche-server (npm)

✓ servers.yaml: some-niche-server added

📦 No preset found for some-niche-server. Proceeding with AI generation.

🔧 Scanning some-niche-server... 8 tools found
🤖 Generating CLI command tree... 8/8 tools ✓
🧩 Generating skill definitions... ✓
🔗 Syncing skill... claude ✓  cursor ✓  codex ✓

✅ Installation complete!
```

### 16.10.4 用户拒绝 preset

```
$ mcp2cli install mcp-atlassian
...
✓ servers.yaml: mcp-atlassian added

📦 Pre-generated skill files found for mcp-atlassian (v1.2.3, 65 tools).
   Pull and use preset? [Y/n] n

🔧 Scanning mcp-atlassian... 65 tools found
🤖 Generating CLI command tree... 65/65 tools ✓
🧩 Generating skill definitions... ✓
🔗 Syncing skill... ✓

✅ Installation complete!
```

### 16.10.5 网络不可用

```
$ mcp2cli install mcp-atlassian
...
✓ servers.yaml: mcp-atlassian added

⚠ Could not reach preset repository. Proceeding with AI generation.

🔧 Scanning mcp-atlassian... 65 tools found
🤖 Generating CLI command tree... 65/65 tools ✓
...
```

### 16.10.6 跳过 preset 检查

```
$ mcp2cli install mcp-atlassian --no-preset
...
✓ servers.yaml: mcp-atlassian added

🔧 Scanning mcp-atlassian... 65 tools found
🤖 Generating CLI command tree... 65/65 tools ✓
🧩 Generating skill definitions... ✓
🔗 Syncing skill... ✓

✅ Installation complete!
```

### 16.10.7 手动浏览和拉取

```
$ mcp2cli preset list
Available presets (from mcp2cli-presets):
  NAME              VERSION   TOOLS   UPDATED
  mcp-atlassian     1.2.3     65      2026-04-01
  playwright        0.5.0     12      2026-03-28
  mcp-github        1.0.0     30      2026-03-25
  mcp-slack         0.8.2     20      2026-03-20

4 presets available. Use 'mcp2cli preset pull <name>' to download.

$ mcp2cli preset pull mcp-github
⬇ Pulling mcp-github preset (v1.0.0, 30 tools)...
   ✓ tools/mcp-github.json
   ✓ cli/mcp-github.yaml
   ✓ skills/mcp-github/ (SKILL.md + 4 reference files + users/workflows.md)
Done! Files written to ~/.agents/mcp2cli/

Next: run 'mcp2cli skill sync mcp-github' to copy to AI clients.

$ mcp2cli preset pull mcp-github --sync
⬇ Pulling mcp-github preset (v1.0.0, 30 tools)... ✓
🔗 Syncing skill... claude ✓  cursor ✓  codex ✓
Done!
```

### 16.10.8 已有本地文件

```
$ mcp2cli preset pull mcp-atlassian

⚠ Local files already exist for mcp-atlassian:
   tools/mcp-atlassian.json
   cli/mcp-atlassian.yaml
   skills/mcp-atlassian/

Overwrite with preset? [Y/n] y

⬇ Pulling preset... ✓
Done!
```

## 16.11 与其他命令的关系

| 命令 | 与 preset 的关系 |
|------|-----------------|
| `mcp2cli install` | pipeline 中 preset-check 步骤自动检查并提示 |
| `mcp2cli convert` | 同上 |
| `mcp2cli update` | 在 preset 拉取的产物基础上增量更新（`generated_by: preset` → `ai`） |
| `mcp2cli remove` | 正常清理 preset 拉取的文件（与 AI 生成的文件处理方式相同） |
| `mcp2cli generate cli` | 不涉及 preset（单步命令，用户已明确要求 AI 生成） |
| `mcp2cli generate skill` | 同上 |
| `mcp2cli scan` | 同上 |
| `mcp2cli skill sync` | preset pull --sync 内部调用 |

## 16.12 错误处理

| 场景 | 处理方式 |
|------|---------|
| 远程仓库不可达（DNS/超时） | 跳过 preset-check，warn 提示，继续正常流程 |
| index.json 下载成功但格式非法 | 跳过，warn 提示 |
| manifest.json 下载失败 | 中止 pull，warn 提示，回退正常流程 |
| 文件下载中途失败 | 清理已下载的不完整文件，回退正常流程 |
| preset 中 `version` 字段格式非法 | 忽略版本比对，正常使用 |
| config.yaml 中 `preset.repo_url` 无效 | 报错，提示检查配置 |
| `--no-preset` | 直接跳过所有 preset 逻辑 |
| `preset.auto_check: false` | 等价于默认 `--no-preset`，但 `preset list/pull` 命令仍可手动使用 |

## 16.13 文件布局变更

运行时目录新增 `.preset-cache/`：

```
~/.agents/mcp2cli/
├── .preset-cache/                    # 新增：preset 缓存
│   ├── index.json                   # 远程 index 的本地缓存
│   └── index.meta.json              # 缓存元数据（ETag、缓存时间）
├── .sessions/
├── tools/
├── cli/
├── skills/
├── config.yaml
├── servers.yaml
├── daemon.pid
├── daemon.sock
└── daemon.log
```

项目源码新增 `preset/` 包：

```
mcp2cli/
└── mcp2cli/
    ├── preset/
    │   ├── __init__.py
    │   ├── models.py               # PresetIndex, PresetEntry（多版本）, Manifest
    │   ├── registry.py             # fetch_index(), find_preset()
    │   ├── downloader.py           # pull_preset(version=), download_file()
    │   ├── checker.py              # check_and_pull_preset(version=)
    │   └── version.py              # parse_preset_spec() — 'name@version' 解析
    ├── installer/
    │   └── pipeline.py             # Step 扩展 skip_if + runner 扩展
    └── main.py                     # preset list / preset pull 命令（@version 语法）
```
