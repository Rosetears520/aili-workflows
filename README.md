# aili-workflows

`aili-workflows` 是 [Rosetears](https://rosetears.cn/) 的个人 OpenCode 工作流仓库，用来沉淀常用的 agent、skill、执行规范和辅助工具。

这个仓库不是上游项目的官方发布版，而是面向个人 OpenCode 使用习惯整理的工作流集合。仓库内包含原创编排内容，也包含来自开源项目的 agent/skill 内容。第三方内容的来源和许可在下方单独标明。

## 项目结构

```text
aili-workflows/
├── AGENTS.md                  # OpenCode repo-level thin control plane
├── .gitignore
├── agents/
│   ├── rose.md                  # Rosetears 的 OpenCode primary agent
│   ├── implementer.md           # 单任务实现 subagent
│   ├── debug-investigator.md     # 只读根因排查 subagent
│   ├── code-reviewer.md         # 代码审查 subagent
│   ├── security-auditor.md      # 安全审计 subagent
│   └── test-engineer.md         # 测试与覆盖率 subagent
├── docs/
│   └── opencode-setup.md        # 给 AI agent 阅读的 OpenCode 安装说明
├── scripts/
│   ├── agents_md.py             # 从模板生成/更新/检查项目 AGENTS.md
│   └── install_opencode.sh      # 安全安装 agents/skills 到 OpenCode 全局配置
├── skills/
│   ├── agents-md-initialization/ # 项目 AGENTS.md 初始化 workflow
│   ├── android-native-dev/
│   ├── api-and-interface-design/
│   ├── browser-testing-with-devtools/
│   ├── change-interviewer/
│   ├── ci-cd-and-automation/
│   ├── code-review-and-quality/
│   ├── code-simplification/
│   ├── context-engineering/
│   ├── debugging-and-error-recovery/
│   ├── deprecation-and-migration/
│   ├── documentation-and-adrs/
│   ├── flutter-dev/
│   ├── frontend-dev/
│   ├── frontend-ui-engineering/
│   ├── fullstack-dev/
│   ├── git-workflow-and-versioning/
│   ├── idea-refine/
│   ├── incremental-implementation/
│   ├── ios-application-dev/
│   ├── minimax-docx/
│   ├── minimax-pdf/
│   ├── minimax-xlsx/
│   ├── parallel-subagent-dispatch/
│   ├── performance-optimization/
│   ├── planning-and-task-breakdown/
│   ├── pptx-generator/
│   ├── react-native-dev/
│   ├── rose-memory/             # ROSE project-local SQLite memory skill
│   ├── security-and-hardening/
│   ├── shader-dev/
│   ├── shipping-and-launch/
│   ├── skill-authoring-and-validation/
│   ├── source-driven-development/
│   ├── spec-driven-development/
│   ├── test-driven-development/
│   ├── using-agent-skills/
│   └── verification-before-completion/
├── templates/
│   └── AGENTS.md                # 项目 AGENTS.md 的唯一模板源
├── tests/
└── README.md
```

## Agent 来源

| Agent | 用途 | 来源与说明 |
|---|---|---|
| `agents/rose.md` | OpenCode primary agent，负责个人主工作流、任务契约、记忆门禁、执行边界和子代理编排 | Rosetears 个人工作流内容 |
| `agents/implementer.md` | 执行一个明确边界的代码实现任务 | Rosetears 个人工作流内容 |
| `agents/debug-investigator.md` | 只读根因调查 subagent，用于修复前的失败定位和证据收集 | Rosetears 个人工作流内容，调试纪律参考 obra/superpowers |
| `agents/code-reviewer.md` | 从 correctness、readability、architecture、security、performance 维度做代码审查 | 改编自 [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) 的 `agents/code-reviewer.md`，遵循 MIT License |
| `agents/security-auditor.md` | 做安全审计、威胁建模和漏洞检查 | 改编自 [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) 的 `agents/security-auditor.md`，遵循 MIT License |
| `agents/test-engineer.md` | 做测试策略、测试补充和覆盖率分析 | 改编自 [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) 的 `agents/test-engineer.md`，遵循 MIT License |

本仓库已移除这些 agent 文本中对 slash command 的直接引用，保留为 OpenCode 主代理自然语言触发和 MainAgent 编排使用。

## Skill 来源

### Rosetears 原创 workflow skills

| Skill | 说明 |
|---|---|
| `agents-md-initialization` | 从 `templates/AGENTS.md` 初始化、更新和检查项目级 `AGENTS.md` |
| `change-interviewer` | 通过采访澄清 OpenSpec、Superpowers、用户文本或自定义文件中的 change draft，并写回目标文件 |
| `rose-memory` | ROSE project-local SQLite memory 工作流 |
| `skill-authoring-and-validation` | 创建、修改和验证本仓库 Agent Skills 的工作流 |

### 来自 obra/superpowers

以下内容参考或改编自 [obra/superpowers](https://github.com/obra/superpowers) 的 skills，原项目许可为 MIT License，版权归 Jesse Vincent 所有。本仓库未 vendoring Superpowers 整体系统，仅将部分流程思想改写为适合个人 OpenCode / ROSE 工作流的 skills 和 subagents。

| 内容 | 说明 |
|---|---|
| `parallel-subagent-dispatch` | 将独立 work packages 并行派发给 subagents，并由 ROSE 收敛证据 |
| `verification-before-completion` | 在声明 complete/fixed/passing/verified 前要求 fresh evidence |
| `debugging-and-error-recovery` | 合入 root-cause-first 调试纪律，避免先猜修复再找证据 |
| `agents/debug-investigator.md` | 本地化为只读根因调查 subagent，配合 ROSE/implementer 分工 |

### 来自 addyosmani/agent-skills

以下 skills 来自 [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills)，原项目许可为 MIT License，版权归 Addy Osmani 所有。本仓库用于个人 OpenCode 工作流整理，并保留来源说明。

| Skill | 说明 |
|---|---|
| `api-and-interface-design` | API、模块边界和接口设计 |
| `browser-testing-with-devtools` | 浏览器运行时验证和调试 |
| `ci-cd-and-automation` | CI/CD 与自动化质量门禁 |
| `code-review-and-quality` | 多维度代码审查流程 |
| `code-simplification` | 保持行为不变的代码简化 |
| `context-engineering` | agent 上下文组织和规则文件管理 |
| `debugging-and-error-recovery` | 根因调试和错误恢复 |
| `deprecation-and-migration` | 废弃、迁移和旧系统下线 |
| `documentation-and-adrs` | 文档和 ADR 记录 |
| `frontend-ui-engineering` | 生产级 UI 工程实践 |
| `git-workflow-and-versioning` | Git 工作流和版本管理 |
| `idea-refine` | 想法发散、收敛和澄清 |
| `incremental-implementation` | 小步增量实现 |
| `performance-optimization` | 性能测量和优化 |
| `planning-and-task-breakdown` | 任务拆解和执行计划 |
| `security-and-hardening` | 安全加固和 OWASP 基线 |
| `shipping-and-launch` | 发布前检查、监控和回滚 |
| `source-driven-development` | 基于官方文档的实现决策 |
| `spec-driven-development` | 规格先行开发 |
| `test-driven-development` | 测试驱动开发 |
| `using-agent-skills` | skill 选择和调用的元说明 |

### 来自 MiniMax-AI/skills

以下 skills 来自 [MiniMax-AI/skills](https://github.com/MiniMax-AI/skills)，原项目许可为 MIT License，版权归 MiniMax 所有。本仓库纳入的是适合个人 OpenCode 工作流的开发、文档、移动端、视觉和文件处理类 skills。

| Skill | 说明 |
|---|---|
| `android-native-dev` | Android Native、Kotlin、Compose 和 Material Design 3 |
| `flutter-dev` | Flutter、Riverpod/Bloc、GoRouter 和跨平台开发 |
| `frontend-dev` | 高级前端、视觉设计、动画和媒体增强页面 |
| `fullstack-dev` | 全栈后端架构、REST API、认证和前后端集成 |
| `ios-application-dev` | iOS、UIKit、SnapKit、SwiftUI 和 Apple HIG |
| `minimax-docx` | DOCX 创建、编辑、填充和模板格式化 |
| `minimax-pdf` | PDF 生成、表单填写和视觉重排 |
| `minimax-xlsx` | Excel、CSV、公式、财务表格和格式保真编辑 |
| `pptx-generator` | PowerPoint 生成、编辑和读取 |
| `react-native-dev` | React Native、Expo、导航、状态、测试和发布 |
| `shader-dev` | GLSL、ShaderToy、SDF、粒子和视觉特效 |

未纳入 `vision-analysis`、`gif-sticker-maker`、`minimax-multimodal-toolkit`、`minimax-music-gen`、`minimax-music-playlist`、`buddy-sings`，因为它们更偏 MiniMax API key 驱动的视觉、多模态或音乐娱乐工作流，不属于当前默认个人 OpenCode 工作流范围。

### 思想来源

- `agents/rose.md` 和 `skills/using-agent-skills/SKILL.md` 中的少量编码 guardrail 表述，概念上参考了 [Andrej Karpathy 关于 agent coding 行为的帖子](https://x.com/karpathy/status/2015883857489522876) 以及 [forrestchang/andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills) 的 `CLAUDE.md` 方向（如先思考、保持简单、手术式修改、目标驱动执行）。当前仓库未 vendored 该仓库文件；如后续复制上游文本或文件，请先确认并补充对应第三方声明。
- `skills/skill-authoring-and-validation/SKILL.md` 的结构原则概念上参考了 OpenAI Codex Agent Skills 的 skill authoring 思路，验证流程概念上参考了 Anthropic skill creator 的访谈、测试和迭代方法；当前仓库未 vendored 上游文件。

## 使用说明

这个仓库面向 OpenCode 使用，核心约定是通过自然语言任务触发 agent 和 skill，而不是依赖 slash command 文件。

### OpenCode 设置

安装方式采用文档驱动：把 [`docs/opencode-setup.md`](docs/opencode-setup.md) 给 AI agent 看，让它先判断 OpenCode 运行在 WSL/Linux 还是 Windows native，再使用默认的条目级软链接安装。WSL/Linux 可直接调用 `scripts/install_opencode.sh --mode selective`；复制仅作为软链接不可用或明确要求时的 fallback。

默认目标是 OpenCode 全局配置目录：Linux/macOS/WSL 为 `~/.config/opencode/`，Windows native 为 `%USERPROFILE%\.config\opencode\`。安装必须保留全局 `agents/` 和 `skills/` 目录，只在目录内部链接具体 agent 文件和 skill 目录。项目记忆数据库始终保存在具体项目的 `memory/memory.db`，不会写入全局配置目录。

项目级 `AGENTS.md` 不走软链接。使用 `agents-md-initialization` skill 调用 `scripts/agents_md.py`，从 `templates/AGENTS.md` 生成到目标项目后再填写项目事实，并用 `check --project .` 放进 CI 或 pre-commit 验证。

典型使用方式：

```text
1. 将本仓库作为个人 OpenCode 工作流配置来源。
2. 让 OpenCode 发现 `agents/` 中的自定义 agent。
3. 让 OpenCode 发现 `skills/` 中的 SKILL.md 工作流。
4. 由 `rose.md` 作为 primary agent，按任务需要调用对应 skills 和 subagents。
```

`rose-memory` 是随 `skills/rose-memory/` 分发的全局 skill。它只提供操作接口，实际 memory state 固定写入当前项目的 `memory/memory.db`。

`frontend-dev` 可用于纯前端设计、实现和动画工作；只有主动使用其中的媒体生成能力时才可能需要额外 MiniMax API key、CLI 或运行时依赖。使用前请阅读对应 skill 目录内的 `SKILL.md`、`README.md`、`scripts/` 或 `references/`。

## 第三方声明

本仓库包含 Rosetears 个人编排内容，也包含来自第三方开源项目的 agent/skill 内容；第三方内容保留其原始版权和许可归属。仓库许可证详见根目录 [`LICENSE`](LICENSE)。

第三方内容来源：

| 来源 | 仓库 | 许可 | 版权声明 |
|---|---|---|---|
| Addy Osmani | [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | MIT License | Copyright (c) 2025 Addy Osmani |
| MiniMax | [MiniMax-AI/skills](https://github.com/MiniMax-AI/skills) | MIT License | Copyright (c) 2026 MiniMax |
| Superpowers | [obra/superpowers](https://github.com/obra/superpowers) | MIT License | Copyright (c) 2025 Jesse Vincent |
| Andrej Karpathy | [X post](https://x.com/karpathy/status/2015883857489522876) | 思想来源 | agent coding guardrail 方向参考 |
| Forrest Chang / Andrej Karpathy skills | [forrestchang/andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills) | 概念性参考；未纳入上游文件 | 如后续复制上游文本或文件，需先确认并保留对应版权/许可 |

如果继续从上游同步 agent 或 skill，请同步更新本 README 的来源表和许可说明。
