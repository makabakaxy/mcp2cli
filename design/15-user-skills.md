# 15. 用户自定义 Skill 目录 (`users/`)

本文档是 [0.0-design-overview.md](0.0-design-overview.md) 第六章的补充设计，描述用户自定义 skill 目录的结构和各命令的行为约定。

## 15.1 目的

`mcp2cli generate skill` 生成的文件会在 `update` 或 `--full` 时被覆盖。用户需要一个持久化区域，存放自定义内容（复杂操作组合、团队约定、个人常用参数模板等），且不受自动更新影响。

## 15.2 目录结构

在 `skills/<server>/` 下新增 `users/` 目录：

```
~/.agents/mcp2cli/skills/<server>/
├── SKILL.md              # AI 生成（≤600 tokens）
├── reference/            # AI 生成
└── users/                # 用户自定义（永不被覆盖）
    ├── SKILL.md          # 用户维护的索引文件
    ├── workflows.md      # AI 首次生成的多步骤工作流（之后用户维护）
    └── .gitkeep
```

`users/SKILL.md` 是用户自定义内容的索引，由用户自行维护。首次生成时创建空模板：

```markdown
# User Notes

<!-- Add your custom workflows, team conventions, and tips below. -->
<!-- This file is never overwritten by mcp2cli generate/update. -->
```

用户可在 `users/` 下自由创建 `.md` 文件，并在 `users/SKILL.md` 中索引：

```
users/
├── SKILL.md                    # 索引（用户维护）
├── workflows.md                # AI 首次生成（之后用户维护）
├── complex-workflows.md        # 复杂多步操作
├── team-conventions.md         # 团队约定
└── my-snippets.md              # 个人常用命令片段
```

## 15.3 workflows.md

`users/workflows.md` 由 AI 在首次 `generate skill` 时自动生成，包含 5-10 个常见多步骤工作流场景。之后永不被 generate/update 覆盖，用户可自由编辑和扩展。

**与其他文件的关系**：
- SKILL.md 的 Commands 表 Example 列 → 单条命令示例
- reference/*.md → 每个命令的详细参数和用法
- **users/workflows.md** → 多条命令组合的复杂工作流（如"创建 issue → 分配 → 加入 sprint → 流转状态"）

## 15.4 SKILL.md 引用

SKILL.md 中固定包含 `## User Notes` 段，由 LLM 生成，指向 `users/SKILL.md`：

```markdown
## User Notes

> **MUST READ** [users/SKILL.md](users/SKILL.md) for custom workflows and tips.
> See [users/workflows.md](users/workflows.md) for multi-step workflow examples.
> Not overwritten by updates.
```

agent 先读 `users/SKILL.md` 即可了解用户自定义内容的全貌。

## 15.5 各命令行为

| 命令 | 对 `users/` 的行为 |
|------|-------------------|
| `generate skill`（首次） | 创建 `users/` 目录 + `.gitkeep` + 空模板 `users/SKILL.md` + AI 生成 `users/workflows.md` |
| `generate skill`（增量/`--full`） | **不触碰** `users/` 目录（含 `workflows.md`） |
| `update` | 内部调用 `generate skill`，同上 |
| `skill sync` | 复制整个 `skills/<server>/` 到各客户端目录，但跳过 `users/` 目录；目标已有的 `users/` 保留不覆盖 |
| `remove` | 若 `users/` 非空（排除 `.gitkeep`），打印警告并要求 `--force`，否则中止 |

## 15.6 代码影响

```
mcp2cli/
├── generator/
│   ├── skill_gen.py              # 首次生成后创建 users/ + .gitkeep；增量/--full 不触碰
│   └── templates/
│       ├── skill_gen_skill.md    # 加入 User Notes 段规则
│       └── skill_gen_example.md  # 加入 User Notes 段示例
├── remover/
│   ├── scanner.py                # RemovalPlan 增加 users_has_content 检测
│   └── pipeline.py               # users/ 非空时需 --force
```
