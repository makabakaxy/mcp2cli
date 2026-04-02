# mcp2cli remove / uninstall 设计文档

本文档是 [0.0-design-overview.md](0.0-design-overview.md) 第十一章 `mcp2cli remove` 的展开设计。

## 一、功能概述

`mcp2cli remove` 是 `install` 和 `convert` 的反向操作，清理所有安装/转换产物。

**命令职责分工：**

| 安装/转换命令 | 反向命令 | 职责 |
|------|------|------|
| `mcp2cli install <server>` | `mcp2cli remove <server>` | 全流程清理：symlink → skill → cli → tools → servers.yaml → (可选)package |
| `mcp2cli convert <server>` | `mcp2cli remove <server>` | 同上 + 在客户端配置中**重新启用**被 disable 的 MCP server |
| `mcp2cli mcp install <server>` | `mcp2cli mcp remove <server>` | 仅从 servers.yaml 移除配置 |
| `mcp2cli skill sync <server>` | `mcp2cli skill unsync <server>` | 仅移除客户端 skill 目录的 symlink |

**别名**：`mcp2cli uninstall` 等价于 `mcp2cli remove`。

## 二、清理范围

按 install/convert 的**反向顺序**执行，确保先清理依赖再清理被依赖的：

| 步骤 | 清理内容 | 对应 install/convert 步骤 |
|------|---------|--------------------------|
| 1. skill unsync | 删除各客户端 skill 目录的 symlink | skill sync |
| 2. 删除 skill 文件 | 删除 `~/.agents/mcp2cli/skills/<server>/` 目录 | generate skill |
| 3. 删除 cli 映射 | 删除 `~/.agents/mcp2cli/cli/<server>.yaml` | generate cli |
| 4. 删除 tools 缓存 | 删除 `~/.agents/mcp2cli/tools/<server>.json` | scan |
| 5. 移除 server 配置 | 从 `~/.agents/mcp2cli/servers.yaml` 移除条目 | mcp install / convert 写入 |
| 6. 重新启用原配置 | 在客户端配置中移除 `disabled: true`（仅 convert 场景） | convert 的 disable 步骤 |
| 7. (可选) 卸载 package | `pip uninstall` / `npm uninstall -g` 等 | mcp install 的 pre-install |
| 8. 断开 daemon 连接 | 通知 daemon 关闭该 server 的连接池 | daemon 自动管理 |

## 三、命令接口

### 3.1 mcp2cli remove / uninstall（全流程清理）

```bash
mcp2cli remove <server-name> [OPTIONS]
mcp2cli uninstall <server-name> [OPTIONS]   # 别名

Arguments:
  server-name          要移除的 MCP server 名称

Options:
  --keep-config        保留 servers.yaml 中的配置（仅清理生成文件和 symlink）
  --skip-re-enable     不在客户端配置中重新启用被 disable 的 server
  --purge-package      同时卸载底层 package（默认不卸载）
  --force / -f         跳过确认提示
  --dry-run            仅显示将执行的操作，不实际删除
```

### 3.2 mcp2cli mcp remove（仅移除 servers.yaml 配置）

```bash
mcp2cli mcp remove <server-name> [OPTIONS]

Arguments:
  server-name          要移除的 MCP server 名称

Options:
  --force / -f         跳过确认提示
  --dry-run            仅显示将执行的操作，不实际删除
```

仅从 `~/.agents/mcp2cli/servers.yaml` 中删除指定 server 条目，不清理任何生成文件。

### 3.3 mcp2cli skill unsync（仅移除 symlink）

```bash
mcp2cli skill unsync [server-name] [OPTIONS]

Arguments:
  server-name          要移除 symlink 的 server 名称
                       省略则移除所有 server 的 symlink

Options:
  --targets            从哪些客户端移除 (默认: claude,cursor,codex)
  --dry-run            仅显示将执行的操作
```

## 四、完整流程

### 4.1 mcp2cli remove 主流程

```
mcp2cli remove mcp-atlassian
        │
        ▼
┌─ 0. 预检 ──────────────────────────────────────┐
│  1. 在 servers.yaml 中查找 server 是否存在       │
│  2. 扫描生成文件是否存在（tools/, cli/, skills/）│
│  3. 扫描客户端 symlink 是否存在                  │
│  4. 扫描客户端配置中是否有被 disable 的该 server  │
│  5. 汇总所有将要执行的操作                       │
│                                                 │
│  若 server 在任何位置都不存在 → 报错退出          │
└───────────────────┬─────────────────────────────┘
                    │
                    ▼
┌─ 1. 确认提示 ──────────────────────────────────┐
│  展示将要执行的全部操作列表                      │
│  要求用户确认（--force 跳过）                    │
└───────────────────┬─────────────────────────────┘
                    │
                    ▼
┌─ 2. Step Pipeline ─────────────────────────────┐
│                                                │
│  Step 1: skill unsync                          │
│    删除各客户端 skill 目录的 symlink             │
│    - ~/.claude/skills/<server>                 │
│    - ~/.cursor/skills/<server>                 │
│    - ~/.codex/skills/<server>                  │
│    - ~/.agents/skills/<server>                 │
│         │                                      │
│         ▼                                      │
│  Step 2: 删除 skill 文件                        │
│    rm -rf ~/.agents/mcp2cli/skills/<server>/   │
│         │                                      │
│         ▼                                      │
│  Step 3: 删除 cli 映射                          │
│    rm ~/.agents/mcp2cli/cli/<server>.yaml      │
│         │                                      │
│         ▼                                      │
│  Step 4: 删除 tools 缓存                        │
│    rm ~/.agents/mcp2cli/tools/<server>.json    │
│         │                                      │
│         ▼                                      │
│  Step 5: 移除 servers.yaml 配置                 │
│    (--keep-config 时跳过)                       │
│         │                                      │
│         ▼                                      │
│  Step 6: 重新启用客户端配置                      │
│    (仅当检测到被 disable 的配置时)               │
│    (--skip-re-enable 时跳过)                    │
│         │                                      │
│         ▼                                      │
│  Step 7: 卸载 package (可选)                    │
│    (仅 --purge-package 时执行)                  │
│         │                                      │
│         ▼                                      │
│  Step 8: 通知 daemon 断开连接                    │
│    (daemon 未运行时跳过)                         │
│                                                │
└────────────────────────────────────────────────┘
```

### 4.2 预检扫描

预检阶段收集所有需要操作的目标，用于确认提示和 dry-run 展示：

```python
@dataclass
class RemovalPlan:
    server_name: str

    # 生成文件
    tools_json: Path | None        # ~/.agents/mcp2cli/tools/<server>.json
    cli_yaml: Path | None          # ~/.agents/mcp2cli/cli/<server>.yaml
    skills_dir: Path | None        # ~/.agents/mcp2cli/skills/<server>/

    # symlink
    skill_symlinks: list[Path]     # 各客户端 skill 目录中的 symlink
    agents_symlink: Path | None    # ~/.agents/skills/<server>

    # 配置
    servers_yaml_entry: bool       # servers.yaml 中是否存在
    disabled_sources: list[ConfigSource]  # 客户端配置中被 disable 的条目

    # package 信息（用于 --purge-package）
    package_info: PackageInfo | None  # command 类型、包名等

    def is_empty(self) -> bool:
        """任何位置都没有该 server 的痕迹"""
        ...

    def summary(self) -> str:
        """生成人类可读的操作摘要"""
        ...
```

### 4.3 重新启用客户端配置（re-enable）

当 `mcp2cli convert` 将客户端配置中的 server 设为 `disabled: true` 后，`remove` 应将其恢复。

**检测逻辑**：扫描所有客户端配置文件，查找 `server_name` 对应条目中 `disabled: true` 的情况。

**恢复操作**：移除 `disabled` 字段（而非设为 `false`），使配置恢复到 convert 之前的状态。

```
re_enable_in_clients(server_name, disabled_sources)
        │
        ├── 遍历 disabled_sources
        │
        ├── ~/.claude.json
        │   → 读取 JSON
        │   → del mcpServers["mcp-atlassian"]["disabled"]
        │   → 写回（原子写入）
        │
        ├── ~/.cursor/mcp.json
        │   → 读取 JSON
        │   → del mcpServers["mcp-atlassian"]["disabled"]
        │   → 写回（原子写入）
        │
        └── ~/.codex/config.toml
            → 读取 TOML (tomlkit)
            → del mcp_servers["mcp-atlassian"]["disabled"]
            → 写回（原子写入）
```

**安全措施**：
- 只在条目确实有 `disabled: true` 时才操作，没有则跳过
- 使用与 convert 的 `config_disabler.py` 相同的原子写入策略
- 写入前在内存中备份原内容，写入失败时可恢复

### 4.4 Package 卸载

默认**不卸载** package，仅在 `--purge-package` 时执行。

从 `servers.yaml` 中提取 `command` 字段推断包管理器和卸载命令：

| command | 卸载命令 | 说明 |
|---------|---------|------|
| `uvx` | `uv pip uninstall <args[0]>` | Python 包 |
| `npx` | `npm uninstall -g <args[0]>` | Node.js 包 |
| `pip` / `python` | `pip uninstall -y <args[0]>` | Python 包 |
| `node` | 不支持自动卸载，提示手动处理 | 本地脚本 |
| 其他 | 不支持自动卸载，提示手动处理 | |

**风险提示**：在卸载前打印警告，提醒用户该 package 可能被其他项目依赖。

### 4.5 Daemon 连接断开

通知 daemon 释放该 server 的连接：

```
daemon_disconnect(server_name)
        │
        ├── 检查 daemon 是否运行（读 PID 文件 + 进程存活检查）
        │
        ├── 未运行 → 跳过，打印 "Daemon not running, skipped"
        │
        └── 运行中 → 发送 IPC 消息
            → {"action": "disconnect", "server": "mcp-atlassian"}
            → daemon 关闭该 server 的子进程并释放连接
```

## 五、Pipeline 定义

复用 `installer/pipeline.py` 的 Step dataclass 和 runner：

```python
def build_remove_pipeline(
    plan: RemovalPlan,
    keep_config: bool = False,
    skip_re_enable: bool = False,
    purge_package: bool = False,
) -> list[Step]:

    steps = []

    # Step 1: 移除 skill symlink
    if plan.skill_symlinks or plan.agents_symlink:
        steps.append(Step(
            name="skill-unsync",
            run=lambda: unsync_skills(plan.server_name, plan.skill_symlinks, plan.agents_symlink),
            retry_cmd=f"mcp2cli skill unsync {plan.server_name}",
        ))

    # Step 2: 删除 skill 文件
    if plan.skills_dir:
        steps.append(Step(
            name="delete-skills",
            run=lambda: delete_dir(plan.skills_dir),
            retry_cmd=f"rm -rf {plan.skills_dir}",
            depends_on=["skill-unsync"] if plan.skill_symlinks else [],
        ))

    # Step 3: 删除 cli 映射
    if plan.cli_yaml:
        steps.append(Step(
            name="delete-cli",
            run=lambda: delete_file(plan.cli_yaml),
            retry_cmd=f"rm {plan.cli_yaml}",
        ))

    # Step 4: 删除 tools 缓存
    if plan.tools_json:
        steps.append(Step(
            name="delete-tools",
            run=lambda: delete_file(plan.tools_json),
            retry_cmd=f"rm {plan.tools_json}",
        ))

    # Step 5: 移除 servers.yaml 配置
    if plan.servers_yaml_entry and not keep_config:
        steps.append(Step(
            name="remove-config",
            run=lambda: remove_from_servers_yaml(plan.server_name),
            retry_cmd=f"mcp2cli mcp remove {plan.server_name}",
        ))

    # Step 6: 重新启用客户端配置
    if plan.disabled_sources and not skip_re_enable:
        steps.append(Step(
            name="re-enable-clients",
            run=lambda: re_enable_in_clients(plan.server_name, plan.disabled_sources),
            retry_cmd='(手动在配置文件中移除 "disabled": true)',
        ))

    # Step 7: 卸载 package（可选）
    if purge_package and plan.package_info:
        steps.append(Step(
            name="purge-package",
            run=lambda: purge_package_fn(plan.package_info),
            retry_cmd=f"(手动卸载: {plan.package_info.uninstall_cmd})",
        ))

    # Step 8: daemon 断开连接
    steps.append(Step(
        name="daemon-disconnect",
        run=lambda: daemon_disconnect(plan.server_name),
        retry_cmd="(daemon 下次空闲回收时自动清理)",
    ))

    return steps
```

**设计说明**：
- 每步失败只打警告，不中止 pipeline（文件不存在等跳过即可）
- 仅存在的资源才生成对应 Step，避免空操作
- re-enable 和 purge-package 是独立操作，不依赖其他步骤

## 六、Symlink 安全检查

删除 symlink 前进行安全验证，防止误删用户手动创建的文件：

```python
def safe_remove_symlink(symlink_path: Path, expected_target_prefix: Path) -> bool:
    """
    安全删除 symlink。

    仅在以下条件同时满足时才删除：
    1. 路径是一个 symlink（而非普通文件/目录）
    2. symlink 的目标以 expected_target_prefix 开头
       （即指向 ~/.agents/mcp2cli/skills/<server>/）

    Returns:
        True 删除成功，False 跳过（不满足条件时打印警告）
    """
    if not symlink_path.is_symlink():
        warn(f"Skipping {symlink_path}: not a symlink")
        return False

    target = symlink_path.resolve()
    if not str(target).startswith(str(expected_target_prefix)):
        warn(f"Skipping {symlink_path}: points to {target}, not managed by mcp2cli")
        return False

    symlink_path.unlink()
    return True
```

## 七、servers.yaml 写入

从 `servers.yaml` 中删除条目：

```python
def remove_from_servers_yaml(server_name: str) -> bool:
    """
    从 ~/.agents/mcp2cli/servers.yaml 中删除 server 条目。

    使用 ruamel.yaml 或 PyYAML 读取，删除 servers 字典中的对应 key，写回文件。
    文件中无该 key 时返回 True（幂等）。
    servers 字典变空后保留空结构 `servers: {}`，不删除文件。
    """
```

## 八、错误处理

| 场景 | 处理方式 |
|------|---------|
| server 在任何位置都不存在 | 报错退出，提示用 `mcp2cli list` 查看可用 server |
| 部分文件已手动删除 | 跳过不存在的文件，不报错（幂等） |
| symlink 不指向 mcp2cli 管理的目录 | 跳过该 symlink，打印警告 |
| 客户端配置文件无写入权限 | re-enable 步骤报警告，提示手动移除 `disabled` 字段 |
| daemon 未运行 | 跳过 daemon disconnect，打印提示 |
| `--purge-package` 但无法确定卸载命令 | 打印警告，提示手动卸载 |
| servers.yaml 文件不存在 | 跳过该步骤 |
| `--dry-run` 模式 | 展示所有计划操作，不修改任何文件 |

## 九、端到端示例

### 9.1 标准移除流程（install 过的 server）

```
$ mcp2cli remove mcp-atlassian

🔍 Scanning mcp-atlassian artifacts...

📋 The following will be removed:

  Symlinks:
    ~/.claude/skills/mcp-atlassian    → ~/.agents/mcp2cli/skills/mcp-atlassian/
    ~/.cursor/skills/mcp-atlassian    → ~/.agents/mcp2cli/skills/mcp-atlassian/
    ~/.codex/skills/mcp-atlassian     → ~/.agents/mcp2cli/skills/mcp-atlassian/
    ~/.agents/skills/mcp-atlassian    → ~/.agents/mcp2cli/skills/mcp-atlassian/

  Generated files:
    ~/.agents/mcp2cli/skills/mcp-atlassian/  (SKILL.md + reference/ + examples/)
    ~/.agents/mcp2cli/cli/mcp-atlassian.yaml
    ~/.agents/mcp2cli/tools/mcp-atlassian.json

  Config:
    servers.yaml: remove mcp-atlassian entry

  Proceed? [Y/n] y

🔗 Removing skill symlinks...
   ✓ ~/.claude/skills/mcp-atlassian  removed
   ✓ ~/.cursor/skills/mcp-atlassian  removed
   ✓ ~/.codex/skills/mcp-atlassian   removed
   ✓ ~/.agents/skills/mcp-atlassian  removed

🧩 Removing skill files...
   ✓ ~/.agents/mcp2cli/skills/mcp-atlassian/  removed

📝 Removing generated files...
   ✓ ~/.agents/mcp2cli/cli/mcp-atlassian.yaml   removed
   ✓ ~/.agents/mcp2cli/tools/mcp-atlassian.json  removed

⚙️  Removing from servers.yaml...
   ✓ mcp-atlassian removed from servers.yaml

🔌 Notifying daemon...
   ✓ mcp-atlassian disconnected

✅ mcp-atlassian removed successfully!
```

### 9.2 移除 convert 过的 server（含 re-enable）

```
$ mcp2cli remove mcp-atlassian

🔍 Scanning mcp-atlassian artifacts...

📋 The following will be removed:

  Symlinks:
    ~/.claude/skills/mcp-atlassian  (4 symlinks)

  Generated files:
    skills/, cli/, tools/  (3 items)

  Config:
    servers.yaml: remove mcp-atlassian entry

  Re-enable (undo convert):
    ~/.claude.json: re-enable mcp-atlassian (remove disabled: true)
    ~/.cursor/mcp.json: re-enable mcp-atlassian (remove disabled: true)

  Proceed? [Y/n] y

🔗 Removing skill symlinks... ✓
🧩 Removing skill files... ✓
📝 Removing generated files... ✓
⚙️  Removing from servers.yaml... ✓

🔓 Re-enabling MCP server in client configs...
   ✓ ~/.claude.json: mcp-atlassian re-enabled
   ✓ ~/.cursor/mcp.json: mcp-atlassian re-enabled

🔌 Notifying daemon... ✓

✅ mcp-atlassian removed successfully!
   MCP server re-enabled in Claude and Cursor configs.
```

### 9.3 Dry-run 模式

```
$ mcp2cli remove mcp-atlassian --dry-run

🔍 Scanning mcp-atlassian artifacts...

[DRY RUN] Would perform the following:

  Remove symlinks:
    ~/.claude/skills/mcp-atlassian
    ~/.cursor/skills/mcp-atlassian
    ~/.codex/skills/mcp-atlassian
    ~/.agents/skills/mcp-atlassian

  Delete files:
    ~/.agents/mcp2cli/skills/mcp-atlassian/
    ~/.agents/mcp2cli/cli/mcp-atlassian.yaml
    ~/.agents/mcp2cli/tools/mcp-atlassian.json

  Remove from servers.yaml:
    mcp-atlassian

  Re-enable in client configs:
    ~/.claude.json: remove disabled flag
    ~/.cursor/mcp.json: remove disabled flag

No files were modified.
```

### 9.4 带 --purge-package

```
$ mcp2cli remove mcp-atlassian --purge-package

🔍 Scanning mcp-atlassian artifacts...

📋 The following will be removed:
  ... (同上)

  Package:
    ⚠ Will uninstall: uv pip uninstall mcp-atlassian
      Warning: This package may be used by other projects!

  Proceed? [Y/n] y

  ... (同上)

📦 Uninstalling package...
   $ uv pip uninstall mcp-atlassian
   ✓ mcp-atlassian uninstalled

✅ mcp-atlassian removed successfully!
```

### 9.5 仅移除 servers.yaml 配置

```
$ mcp2cli mcp remove mcp-atlassian

⚙️  Remove mcp-atlassian from servers.yaml? [Y/n] y
✓ mcp-atlassian removed from servers.yaml

Note: Generated files (tools/, cli/, skills/) were NOT removed.
      Use `mcp2cli remove mcp-atlassian` for full cleanup.
```

### 9.6 Server 不存在

```
$ mcp2cli remove mcp-jiraa

✗ Server "mcp-jiraa" not found.

  No artifacts found in:
  - servers.yaml
  - tools/, cli/, skills/
  - Client configs (claude, cursor, codex)

  Available servers:
    mcp-atlassian    (servers.yaml + skills)
    playwright       (claude:global)

  Use `mcp2cli list` to see all configured servers.
```

### 9.7 保留配置，仅清理生成文件

```
$ mcp2cli remove mcp-atlassian --keep-config

📋 The following will be removed:
  Symlinks: (4 items)
  Generated files: skills/, cli/, tools/

  Config:
    servers.yaml: KEPT (--keep-config)

  Proceed? [Y/n] y

... (清理 symlink 和生成文件)

✅ Generated files removed. servers.yaml config preserved.
   Run `mcp2cli install mcp-atlassian --skip-generate` to regenerate.
```

## 十、代码结构

```
mcp2cli/
├── main.py                          # 新增 remove/uninstall 子命令
│                                    # 新增 mcp remove 子命令
│                                    # 新增 skill unsync 子命令
├── remover/                         # 新增包
│   ├── __init__.py
│   ├── scanner.py                   # 预检扫描：收集所有 server 产物 → RemovalPlan
│   ├── cleaner.py                   # 文件删除、symlink 移除（含安全检查）
│   ├── config_re_enabler.py         # 在客户端配置中移除 disabled（复用 converter/ 的原子写入）
│   ├── package_purger.py            # 推断卸载命令并执行
│   └── pipeline.py                  # remove 专属 pipeline 组装
├── installer/                       # 已有，复用
│   ├── pipeline.py                  # Step dataclass + runner（共享）
│   ├── servers_writer.py            # 读写 servers.yaml（扩展 remove 方法）
│   └── skill_sync.py               # 扩展 unsync 方法
├── converter/                       # 已有，复用原子写入逻辑
│   └── config_disabler.py           # re_enabler 复用其原子写入策略
```

### 模块职责

**`remover/scanner.py`**：

```python
def scan_removal_targets(server_name: str) -> RemovalPlan:
    """
    扫描所有可能存在的 server 产物，构建 RemovalPlan。

    扫描范围：
    - ~/.agents/mcp2cli/tools/<server>.json
    - ~/.agents/mcp2cli/cli/<server>.yaml
    - ~/.agents/mcp2cli/skills/<server>/
    - ~/.claude/skills/<server>  (symlink)
    - ~/.cursor/skills/<server>  (symlink)
    - ~/.codex/skills/<server>   (symlink)
    - ~/.agents/skills/<server>  (symlink)
    - ~/.agents/mcp2cli/servers.yaml 中的条目
    - ~/.claude.json 等客户端配置中 disabled 的条目
    """
```

**`remover/cleaner.py`**：

```python
def unsync_skills(
    server_name: str,
    symlinks: list[Path],
    agents_symlink: Path | None,
) -> bool:
    """移除所有 skill symlink，含安全检查。"""

def delete_skills_dir(skills_dir: Path) -> bool:
    """删除 skill 文件目录。"""

def delete_file(file_path: Path) -> bool:
    """删除单个文件（幂等：不存在时返回 True）。"""
```

**`remover/config_re_enabler.py`**：

```python
def re_enable_server(
    server_name: str,
    config_path: Path,
    config_format: str,  # "claude_json" | "cursor_json" | "codex_toml"
) -> bool:
    """在客户端配置文件中移除 server 的 disabled 字段。"""

def re_enable_in_clients(
    server_name: str,
    sources: list[ConfigSource],
) -> bool:
    """在所有包含该 server disabled 条目的配置中重新启用。"""
```

**`remover/package_purger.py`**：

```python
@dataclass
class PackageInfo:
    command: str          # "uvx", "npx", "pip", etc.
    package_name: str     # args[0]
    uninstall_cmd: str    # 推断出的卸载命令

def detect_package_info(server_name: str, servers_yaml_entry: dict) -> PackageInfo | None:
    """从 servers.yaml 条目中推断包管理器和卸载命令。"""

def purge_package(info: PackageInfo) -> bool:
    """执行卸载命令。"""
```

## 十一、与现有模块的关系

```
mcp2cli remove <server>
    │
    ├── remover/scanner.py
    │     扫描产物 → RemovalPlan
    │     调用 config/reader.py 枚举配置
    │
    ├── remover/cleaner.py
    │     删除 symlink + 生成文件
    │     调用 installer/skill_sync.py 的 unsync 逻辑
    │
    ├── installer/servers_writer.py    ← 扩展
    │     remove_from_servers_yaml()
    │
    ├── remover/config_re_enabler.py
    │     复用 converter/config_disabler.py 的原子写入策略
    │
    ├── remover/package_purger.py
    │     推断并执行卸载命令
    │
    ├── daemon/client.py               ← 扩展
    │     发送 disconnect 消息
    │
    └── installer/pipeline.py          ← 复用 Step + runner
```
