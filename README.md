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
│   ├── code-scout.md            # 只读代码侦察 subagent
│   ├── doc-researcher.md         # 只读本地文档研究 subagent
│   ├── web-researcher.md         # 只读联网资料研究 subagent
│   ├── plan-auditor.md           # 只读计划审计 subagent
│   ├── implementer.md           # 单任务实现 subagent
│   ├── debug-investigator.md     # 只读根因排查 subagent
│   ├── code-reviewer.md         # 代码审查 subagent
│   ├── security-auditor.md      # 安全审计 subagent
│   └── test-engineer.md         # 测试与覆盖率 subagent
├── commands/
│   ├── ideate.md                # /ideate：进入 aili-delivery-flow IDEATE
│   ├── define.md                # /define：进入 aili-delivery-flow DEFINE
│   ├── build.md                 # /build：进入 aili-delivery-flow BUILD
│   └── ship.md                  # /ship：进入 aili-delivery-flow SHIP
├── docs/
│   └── opencode-setup.md        # 给 AI agent 阅读的 OpenCode 安装说明
├── manifests/
│   └── rose-aili.components.json # rose-aili installer component manifest
├── package.json                  # rose-aili Node/TypeScript CLI package metadata
├── scripts/
│   ├── agents_md.py             # 从模板生成/更新/检查项目 AGENTS.md
│   └── install_opencode.sh      # 安全安装 agents/skills/commands 到 OpenCode 全局配置
├── src/                          # rose-aili CLI source
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
│   ├── evidence-scoped-retrospective/
│   ├── explain-by-allegory/
│   ├── flutter-dev/
│   ├── frontend-dev/
│   ├── frontend-ui-engineering/
│   ├── fullstack-dev/
│   ├── git-workflow-and-versioning/
│   ├── github-evidence-triage/
│   ├── harness-issue-triage/
│   ├── idea-refine/
│   ├── incremental-implementation/
│   ├── ios-application-dev/
│   ├── mature-project-pattern-research/
│   ├── minimax-docx/
│   ├── minimax-pdf/
│   ├── minimax-xlsx/
│   ├── parallel-subagent-dispatch/
│   ├── performance-optimization/
│   ├── planning-and-task-breakdown/
│   ├── pptx-generator/
│   ├── react-native-dev/
│   ├── rose-memory/             # ROSE project-local SQLite memory skill
│   ├── review-pipeline/
│   ├── security-and-hardening/
│   ├── shader-dev/
│   ├── shipping-and-launch/
│   ├── skill-authoring-and-validation/
│   ├── source-driven-development/
│   ├── spec-driven-development/
│   ├── strategy-stress-test/
│   ├── test-document-generator/
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
| `agents/code-scout.md` | 只读代码侦察 subagent，用于定位文件、符号、测试、调用路径、配置、schema、文档、现有模式和约束，并返回 evidence anchors | Rosetears 个人工作流内容 |
| `agents/doc-researcher.md` | 只读本地文档研究 subagent，用于查找 AGENTS.md、rose.md、skills、OpenSpec、README、docs、设计文档和项目本地规则 | Rosetears 个人工作流内容 |
| `agents/web-researcher.md` | 只读联网资料研究 subagent，用于官方文档、公开 GitHub README/issues/releases、插件文档、安装命令、API 行为、兼容性和弃用检查 | Rosetears 个人工作流内容 |
| `agents/plan-auditor.md` | 只读计划审计 subagent，用于实施前检查 plan/spec/tasks/acceptance/test-plan 的缺口、冲突、过度设计和验证薄弱点 | Rosetears 个人工作流内容 |
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
| `aili-delivery-flow` | AILI 交付生命周期权威：IDEATE、DEFINE、BUILD、SHIP 四模式、后端 adapter、artifact gate、review/repair/closeout |
| `change-interviewer` | 为 OpenSpec、Superpowers、用户文本或自定义文件中的 change draft 生成证据驱动中文问卷包，吸收用户答案后写回目标文件 |
| `evidence-scoped-retrospective` | 基于显式提供或批准的 session exports、git history、implementation notes 等证据做安全的 report-first 工作流复盘，不假设全局历史、不提交 raw sessions |
| `explain-by-allegory` | 用寓言、故事、类比或隐喻解释复杂概念，并映射回正式概念、边界和误区 |
| `github-evidence-triage` | 对 GitHub issue / PR 做只读证据分流，输出带 URL、commit、文件行号或 `[UNVERIFIED]` 标记的报告 |
| `harness-issue-triage` | 对用户反馈的 harness / workflow 行为问题做只读定位，判断问题属于 command、skill、protocol、docs、installer、memory、subagent packet 或 agent prompt 哪一层，并说明怎么改 |
| `harness-evolution` | 对 ROSE、skills、commands、subagents、memory、install、harness docs 等流程变更执行 report-first 治理 |
| `mature-project-pattern-research` | 在 IDEATE 或普通聊天中研究成熟公开项目的 prior art，输出来源、成熟度信号、可借鉴/不推荐模式、风险、不确定性和下一步决策 |
| `review-pipeline` | 实现后编排 code-reviewer、test-engineer、security-auditor 等 reviewer，收敛 findings、执行 fix loop，并作为最终 PASS 前的 gate |
| `rose-memory` | ROSE project-local SQLite memory 工作流 |
| `skill-authoring-and-validation` | 创建、修改和验证本仓库 Agent Skills 的工作流 |
| `strategy-stress-test` | 非平凡方案、问卷、计划、reconciliation、review 或完成声明接受前的反方审稿 / 证据校准 workflow guardrail |
| `test-document-generator` | 根据 spec、方案、issue、描述或 OpenSpec change 生成详细测试文档、测试矩阵、回归范围和验收清单，默认写入仓库内 Markdown 文件 |

`change-interviewer` 和 `test-document-generator` 的输出规则是：OpenSpec change 直接写入 change 目录；所有非 OpenSpec 输入都先询问生成位置，包括单个普通文档、目录、多文档、粘贴文本或落点不明确的情况。可选落点包括同级文件、同级文件夹、追加到现有文档或只在聊天中输出。

### 来自 obra/superpowers

以下内容参考或改编自 [obra/superpowers](https://github.com/obra/superpowers) 的 skills，原项目许可为 MIT License，版权归 Jesse Vincent 所有。本仓库未 vendoring Superpowers 整体系统，仅将部分流程思想改写为适合个人 OpenCode / ROSE 工作流的 skills 和 subagents。

| 内容 | 说明 |
|---|---|
| `parallel-subagent-dispatch` | 将高噪音只读证据收集隔离到 subagent，或将独立 work packages 并行派发给 subagents，并由 ROSE 收敛证据 |
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
- `skills/explain-by-allegory/SKILL.md` 概念上参考了 Amanda Askell-style allegory / analogy prompting 的解释方式（见 [Amanda Askell](https://askell.io/) 个人页面作为人物来源线索），本仓库仅保留“先讲故事、再映射正式概念、再说明类比失效点”的工作流结构，未复制外部 prompt 文本。
- `skills/evidence-scoped-retrospective/SKILL.md` 概念上参考了 Vaibhav / VB / Codex-style self-improvement prompting 的“回看近期工作并提出流程改进”方向，但改为 OpenCode 可证据化版本：只分析用户显式提供或批准的证据，不声称可见全局历史，且先报告再走既有变更门禁；未复制外部 prompt 文本。
- `skills/evidence-scoped-retrospective/SKILL.md` 的 failure-pattern taxonomy 和 `templates/AGENTS.md` 的 selected guardrails 概念上参考了用户提供的 Mnilax / Karpathy / Forrest Chang-style coding-agent discipline summary。用户请求使用 [Mnilax X 链接](https://x.com/Mnilax/status/2053116311132155938) 作为 attribution；direct X content 在本次实现中未直接抓取，按 conceptual / user-provided source 标注，未复制原文。
- `skills/skill-authoring-and-validation/SKILL.md` 的结构原则概念上参考了 OpenAI Codex Agent Skills 的 skill authoring 思路，验证流程概念上参考了 Anthropic skill creator 的访谈、测试和迭代方法；当前仓库未 vendored 上游文件。
- `skills/strategy-stress-test/SKILL.md` 概念上参考了用户提供的 [X 链接](https://x.com/cjzafir/status/2052110266566107321) 中关于 confidence calibration / loophole loop 的提示思想，并工程化为“事实可证高置信、默认 1 轮且最多 3 轮、Open Question / Unverified 标记”的 workflow guardrail。当前仓库未 vendored 上游文本。
- `agents/doc-researcher.md`、`agents/web-researcher.md`、`agents/plan-auditor.md`、`skills/review-pipeline/SKILL.md`、`skills/github-evidence-triage/SKILL.md` 以及 `implementer` / `git-workflow-and-versioning` / `strategy-stress-test` 的部分边界设计，概念上吸收了用户提供的 oh-my-opencode / oh-my-openagent 角色拆分建议（上游现名 `oh-my-openagent`，曾用名 `oh-my-opencode`；如 Librarian、Metis、Momus、Hephaestus、git-master、review-work、github-triage、hyperplan 的能力边界），但未复制上游文件文本。
- 若干 workflow 纪律在现有 skills 中概念上吸收了 [Matt Pocock 的 skills](https://github.com/mattpocock/skills) 方向，包括 zoom-out、prototype、to-issues、grill-with-docs、diagnose、tdd、write-a-skill、improve-codebase-architecture 等。当前仓库没有新增 Matt 风格 skill，也未 vendored 上游文件；如后续复制上游文本或文件，请保留其 MIT License 版权声明。

## 使用说明

这个仓库面向 OpenCode 使用，核心约定是通过自然语言任务触发 agent 和 skill；同时提供四个可选 slash command 入口：`/ideate`、`/define`、`/build`、`/ship`，分别对应 `commands/{ideate,define,build,ship}.md`，由 `skills/aili-delivery-flow` 承接。`/build` 是批准范围内的自动实现流水线，会把实现结果带过本地 code review、test verification 和必要的 security review；`/ship` 是更完整的 release-readiness 流水线，会复用或刷新 BUILD 证据，对当前变更/最终 diff 或明确指定的 baseline/整库范围执行 release-blocker audit，并补上 closeout、交付/合并/发布风险与后续动作。仓库不提供 `/research`、`/questionnaire`、`/test-plan`、`/implement`、`/fix`、`/debug`、`/review`、`/release-blocker-audit` 或 `/evolve` 等内部阶段命令。

### OpenCode 设置

推荐安装入口是 `rose-aili` Node/TypeScript CLI；Bash 脚本仍保留为兼容 fallback。

```bash
npx -y rose-aili install
```

在 npm 发布前，AI assistant 可从 GitHub package spec 运行同一个 binary（把 `<owner>/<repo>` 替换为用户提供的仓库）：

```bash
npx -y --package github:<owner>/<repo> rose-aili install
```

常用维护命令：

```bash
npx -y rose-aili update
npx -y rose-aili doctor
```

`rose-aili install` 默认复用 `scripts/install_opencode.sh` 的条目级安全安装语义，安装 agents、skills 和 commands；从普通 git clone 安装时使用 selective symlink，从 npm/npx 的 packaged 非 git 目录安装时使用 copy，避免把 OpenCode 链接到临时 package cache。安装时可选择把 `rose` 设为 OpenCode 默认 primary agent，并把模型偏好写入 OpenCode 用户配置，而不是写入 `agents/rose.md`：

交互式 `rose-aili install` 在发现 OpenCode JSON/JSONC 中还没有 `agent.rose.model` 时，会在同一次安装对话中询问模型值（格式如 `provider/model`）。直接回车留空会跳过模型写入；之后也可以用 `--model <provider/model>` 非交互设置。模型偏好始终写入 OpenCode JSON/JSONC 的 `agent.rose.model`，不会为了用户偏好修改 `agents/rose.md`。

```jsonc
{
  "default_agent": "rose",
  "agent": {
    "rose": {
      "model": "anthropic/claude-sonnet-4-5"
    }
  }
}
```

自动化或 AI 代理可用显式 flag 避免交互：

```bash
npx -y rose-aili install --yes --model anthropic/claude-sonnet-4-5
npx -y rose-aili install --enable-playwright
```

安装方式也可采用文档驱动：把 [`docs/opencode-setup.md`](docs/opencode-setup.md) 给 AI agent 看，让它先判断 OpenCode 运行在 WSL/Linux 还是 Windows native，再使用默认的条目级软链接安装。WSL/Linux 可直接调用 `scripts/install_opencode.sh --mode selective` 安装 agents、skills 和 commands。

默认目标是 OpenCode 全局配置目录：Linux/macOS/WSL 为 `~/.config/opencode/`，Windows native 为 `%USERPROFILE%\.config\opencode\`。安装必须保留全局 `agents/`、`skills/` 和 `commands/` 目录，只在目录内部链接具体 agent 文件、skill 目录和 command 文件。项目记忆数据库始终保存在具体项目的 `memory/memory.db`，不会写入全局配置目录。

项目级 `AGENTS.md` 不走软链接。使用 `agents-md-initialization` skill 调用 `scripts/agents_md.py`，从 `templates/AGENTS.md` 生成到目标项目后再填写项目事实，并用 `check --project .` 放进 CI 或 pre-commit 验证。

典型使用方式：

```text
1. 将本仓库作为个人 OpenCode 工作流配置来源。
2. 让 OpenCode 发现 `agents/` 中的自定义 agent。
3. 让 OpenCode 通过安装脚本链接后的全局 `~/.config/opencode/skills/` 发现本仓库 `skills/` 中的 SKILL.md 工作流。
4. 可选使用全局 `~/.config/opencode/commands/` 中的 `/ideate`、`/define`、`/build`、`/ship` 入口。
5. 由 `rose.md` 作为 primary agent，按任务需要调用对应 skills 和 subagents。
```

新增、删除或重命名 skill 或 command 后，重新运行 `scripts/install_opencode.sh --mode selective`，然后重启 OpenCode 或开启新 session，确保 discovery 刷新。

`docs/harness/**` 是本仓库维护和审查 harness 时读取的源文档，不是普通业务项目运行时必须存在的上下文。通过软链接安装时，OpenCode 会发现并加载被链接的 `skills/*`；因此运行时必须依赖的 harness 定位规则应放在对应 skill 的 `references/` 中，例如 `skills/harness-issue-triage/references/`，而不是假设每个目标项目都有 `docs/harness/**`。

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
| Matt Pocock | [mattpocock/skills](https://github.com/mattpocock/skills) | 概念性参考；未纳入上游文件 | 如后续复制上游文本或文件，需保留 MIT License 与 Copyright (c) 2025 Matt Pocock |
| Amanda Askell | [askell.io](https://askell.io/) | 概念性参考；未纳入上游文本 | allegory / analogy prompting 方向参考 |
| Vaibhav / VB / Codex-style prompting | 用户提供的概念方向 | 概念性参考；未纳入上游文本 | evidence-scoped self-improvement prompting 方向参考；本仓库不声称可见全局历史 |
| Andrej Karpathy | [X post](https://x.com/karpathy/status/2015883857489522876) | 思想来源 | agent coding guardrail 方向参考 |
| Mnilax | [X post](https://x.com/Mnilax/status/2053116311132155938) | 用户提供的概念来源；direct X content 未验证 | coding-agent discipline / retrospective taxonomy 方向参考；未复制原文 |
| cjzafir | [X post](https://x.com/cjzafir/status/2052110266566107321) | 思想来源 | confidence calibration / loophole loop 方向参考；未 vendored 上游文本 |
| code-yeongyu | [oh-my-openagent](https://github.com/code-yeongyu/oh-my-openagent)（曾用名 `oh-my-opencode`） | 概念性参考；未纳入上游文件 | agent / skill 角色边界与工作流拆分方向参考，如 Librarian、Metis、Momus、Hephaestus、git-master、review-work、github-triage、hyperplan |
| Forrest Chang / Andrej Karpathy skills | [forrestchang/andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills) | 概念性参考；未纳入上游文件 | 如后续复制上游文本或文件，需先确认并保留对应版权/许可 |

如果继续从上游同步 agent 或 skill，请同步更新本 README 的来源表和许可说明。
