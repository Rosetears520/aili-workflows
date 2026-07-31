# aili-workflows

`aili-workflows` 是 [Rosetears](https://rosetears.cn/) 的个人 OpenCode 工作流仓库，用来沉淀常用的 agent、skill、执行规范和辅助工具。

这个仓库不是上游项目的官方发布版，而是面向个人 OpenCode 使用习惯整理的工作流集合。仓库内包含原创编排内容，也包含来自开源项目的 agent/skill 内容。第三方内容的来源和许可在下方单独标明。

## 项目结构

```text
aili-workflows/
├── AGENTS.md                  # OpenCode repo-level thin control plane
├── .gitignore
├── .agents/
│   └── skills/
│       ├── academic-paper-review/
│       ├── agents-md-initialization/ # 项目 AGENTS.md 初始化 workflow
│       ├── ai-regression-scout/
│       ├── aili-delivery-flow/
│       ├── android-native-dev/
│       ├── api-and-interface-design/
│       ├── browser-testing-with-devtools/
│       ├── browser-qa/
│       ├── chart-visualization/
│       ├── ci-cd-and-automation/
│       ├── code-review-and-quality/
│       ├── code-simplification/
│       ├── consulting-analysis/
│       ├── context-engineering/
│       ├── coverage-review/
│       ├── data-analysis/
│       ├── deprecation-and-migration/
│       ├── documentation-and-adrs/
│       ├── e2e-artifact-handling/
│       ├── evidence-scoped-retrospective/
│       ├── explain-by-allegory/
│       ├── flutter-dev/
│       ├── frontend-dev/
│       ├── frontend-ui-engineering/
│       ├── fullstack-dev/
│       ├── git-workflow-and-versioning/
│       ├── github-evidence-triage/
│       ├── harness-evolution/
│       ├── harness-issue-triage/
│       ├── i-have-adhd/
│       ├── idea-refine/
│       ├── incremental-implementation/
│       ├── ios-application-dev/
│       ├── local-review-gate/
│       ├── mature-project-pattern-research/
│       ├── minimax-docx/
│       ├── minimax-pdf/
│       ├── minimax-xlsx/
│       ├── newsletter-generation/
│       ├── parallel-subagent-dispatch/
│       ├── performance-optimization/
│       ├── planning-and-task-breakdown/
│       ├── pptx-generator/
│       ├── pr-test-analysis/
│       ├── react-native-dev/
│       ├── requirements-grilling/
│       ├── rose-memory/             # ROSE project-local SQLite memory skill
│       ├── review-pipeline/
│       ├── security-and-hardening/
│       ├── session-handoff/
│       ├── shader-dev/
│       ├── shipping-and-launch/
│       ├── silent-failure-hunting/
│       ├── write-skills/
│       ├── source-driven-development/
│       ├── spec-driven-development/
│       ├── strategy-stress-test/
│       ├── systematic-literature-review/
│       ├── test-document-generator/
│       └── test-driven-development/
├── agents/
│   ├── rose.md                  # Rosetears 的 OpenCode primary agent
│   ├── code-scout.md            # 只读代码侦察 subagent
│   ├── doc-researcher.md         # 只读本地文档研究 subagent
│   ├── web-researcher.md         # 只读联网资料研究 subagent
│   ├── plan-auditor.md           # 只读计划审计 subagent
│   ├── implementer.md           # 单任务实现 subagent
│   ├── code-reviewer.md         # 代码审查 subagent
│   ├── convergence-reviewer.md  # 只读交付收敛审查 subagent
│   ├── security-auditor.md      # 安全审计 subagent
│   ├── test-engineer.md         # 测试与覆盖率 subagent
│   ├── test-coverage-reviewer.md # 只读覆盖率充分性 review subagent
│   ├── pr-test-analyzer.md      # 只读 PR 测试影响分析 subagent
│   ├── ai-regression-scout.md   # 只读 AI 回归场景侦察 subagent
│   ├── silent-failure-reviewer.md # 只读静默失败审查 subagent
│   ├── browser-qa-runner.md     # 浏览器 QA 验证 subagent
│   ├── e2e-artifact-runner.md   # E2E 证据 artifact subagent
│   ├── web-performance-auditor.md # 只读 Web 性能审计 subagent
│   ├── spec-miner.md            # 只读 spec mining subagent
│   ├── agent-evaluator.md       # 只读 agent 输出评估 subagent
│   └── opensource-sanitizer.md  # 只读 OSS/public exposure 审查 subagent
├── commands/
│   ├── ideate.md                # /ideate：进入 aili-delivery-flow IDEATE
│   ├── define.md                # /define：进入 aili-delivery-flow DEFINE
│   ├── build.md                 # /build：进入 aili-delivery-flow BUILD
│   ├── ship.md                  # /ship：进入 aili-delivery-flow SHIP
│   └── local-review.md          # /local-review：本地 report-first 审查入口，不覆盖 OpenCode /review
├── docs/
│   └── opencode-setup.md        # 给 AI agent 阅读的 OpenCode 安装说明
├── manifests/
│   └── rose-aili.components.json # rose-aili installer component manifest
├── package.json                  # rose-aili Node/TypeScript CLI package metadata
├── scripts/
│   ├── agents_md.py             # 从模板生成/更新/检查项目 AGENTS.md
│   └── install_opencode.sh      # 安全安装全局 AGENTS/agents/skills/commands 到 OpenCode 配置
├── src/                          # rose-aili CLI source
├── templates/
│   ├── AGENTS.md                # 项目 AGENTS.md 的瘦模板源：只放项目事实/本地例外
│   └── opencode-global-AGENTS.md # rose-aili 安装到 OpenCode home 的全局规则源
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
| `agents/code-reviewer.md` | 从 correctness、readability、architecture、security、performance 维度做代码审查 | 改编自 [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) 的 `agents/code-reviewer.md`，遵循 MIT License |
| `agents/convergence-reviewer.md` | 对当前 contract、实现、验证和遗留风险做只读收敛审查，不替代 ROSE 的最终判断 | Rosetears 个人工作流内容 |
| `agents/security-auditor.md` | 做安全审计、威胁建模和漏洞检查 | 改编自 [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) 的 `agents/security-auditor.md`，遵循 MIT License |
| `agents/test-engineer.md` | 做聚焦测试策略、测试补充、角色内安全本地检查执行和覆盖率分析 | 改编自 [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) 的 `agents/test-engineer.md`，遵循 MIT License |
| `agents/web-performance-auditor.md` | 做 Web 性能审计，聚焦 Core Web Vitals、加载、渲染和网络性能，并严格区分测量数据与静态分析潜在影响 | 复制并做 OpenCode 安全包装自 [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) 的 `agents/web-performance-auditor.md`，遵循 MIT License |
| `agents/test-coverage-reviewer.md` | 只读覆盖率充分性、未测路径和验证证据审查 | Rosetears 个人工作流内容 |
| `agents/pr-test-analyzer.md` | 只读 PR / diff 测试影响、CI 日志和最小测试矩阵分析 | Rosetears 个人工作流内容 |
| `agents/ai-regression-scout.md` | 只读 agents / prompts / skills / routing 回归场景侦察 | Rosetears 个人工作流内容 |
| `agents/silent-failure-reviewer.md` | 只读静默失败、误报成功、跳过 gate 和 stale evidence 审查 | Rosetears 个人工作流内容 |
| `agents/browser-qa-runner.md` | 本地浏览器 QA 验证；写截图、trace、报告前要求仓库内 artifact 落点，禁止生产数据变更 | Rosetears 个人工作流内容 |
| `agents/e2e-artifact-runner.md` | E2E trace、video、screenshot、report、failure bundle 证据收集；要求仓库内 artifact 落点，禁止生产数据变更 | Rosetears 个人工作流内容 |
| `agents/spec-miner.md` | 只读 spec mining subagent，从现有代码、测试、文档和 OpenSpec artifact 提炼候选 requirements / scenarios，不批准或编写 specs | Clean-room pattern absorption from [affaan-m/ECC](https://github.com/affaan-m/ECC) agent role |
| `agents/agent-evaluator.md` | 只读 agent / subagent 输出评估 subagent，检查任务匹配、证据质量、claim hygiene、约束遗漏、overclaiming 和 handoff 可用性 | Clean-room pattern absorption from [affaan-m/ECC](https://github.com/affaan-m/ECC) agent role |
| `agents/opensource-sanitizer.md` | 只读 OSS / npm / public-release 暴露面审查 subagent，报告 secrets/private data/package/prompt/provenance 风险且必须脱敏 | Clean-room pattern absorption from [affaan-m/ECC](https://github.com/affaan-m/ECC) agent role |

Canonical agent inventory 是 primary `ROSE` 加 19 个 repository-managed subagents。普通工作先按 `aili-agent-selection/v1` 判断 assignment shape，再选择职责最窄、证据合同最具体的 canonical role；命中现有 trigger 且有具体收益时 prompt dispatch，未命中或被 overlap/dependency/permission/negative-benefit 阻塞时才 direct fallback。正式生命周期使用 `aili-task-board/v1`：ready Agent-owned package 必须派给 exact canonical owner，ROSE-owned package 直接执行，Agent-owned direct path 只允许预先记录的合法 waiver；`general` 不能作为 formal owner。默认并发从 2 开始但不是硬上限；更大 fan-out 必须由模型根据独立非重叠单元、具体收益、合适 owner 和显式 join plan 有界选择。共享合同以 work package identity 为边界，允许 adapter 使用 one-shot task 或 persistent Agent identity；当前 OpenCode Task adapter 仍是 fresh、terminal、不可复用旧 `task_id`，但这不是所有 adapter 的通用 session 限制。失败、partial 或 empty result 不自动授权 retry。19 个 managed profiles 全部保持 non-delegating 和 `external_directory: deny`；只有 ROSE 保留逐 operation 的 external-directory ask，并继续拥有 lifecycle、decision、integration、inspection、verification、disposition 与最终 verdict。`web-researcher` 的角色不变：它仍只负责外部网页研究，web 能力不授予外部本地目录、mutation 或 delegation 权限。内置 `explore` / `general` 不计入这 19 个 managed profiles。

本仓库已移除这些 agent 文本中对 slash command 的直接引用，保留为 OpenCode 主代理自然语言触发和 MainAgent 编排使用。

## Skill 来源

### Rosetears 原创 workflow skills

| Skill | 说明 |
|---|---|
| `agents-md-initialization` | 从 `templates/AGENTS.md` 初始化、更新和检查项目级 `AGENTS.md` |
| `aili-delivery-flow` | AILI 交付生命周期权威：IDEATE、DEFINE、BUILD、SHIP 四模式、后端 adapter、artifact gate、`aili-task-board/v1` formal package/evidence Board、review/repair/closeout |
| `ai-regression-scout` | 当 agents、prompts、skills、routing 或输出契约变更时，路由到只读 AI 回归场景侦察 |
| `browser-qa` | 浏览器 QA 路由；截图、trace、报告等用户可见 artifact 必须先确认仓库内落点，并避免生产数据变更 |
| `build-failure-repair` | build、typecheck、lint、test 或 CI gate 失败时的 root-cause-first 最小修复 workflow；不得跳过 gate 或擅自改依赖/lockfile |
| `code-review-quality-gates` | 代码审查质量 gate、severity/risk/evidence rubric、negative test case、fixture/golden drift 和中文评审报告 profile；不新增重复 reviewer agent |
| `comment-accuracy-review` | 评论、JSDoc、TODO、README 与代码事实一致性审查，以及中文注释/变量名适当性检查 |
| `coverage-review` | 覆盖率充分性、未测路径和验证证据的只读 QA review 路由 |
| `e2e-artifact-handling` | E2E trace、video、screenshot、report、failure bundle 的仓库内 artifact 落点与证据处理路由 |
| `evidence-scoped-retrospective` | 基于显式提供或批准的 session exports、git history、implementation notes 等证据做安全的 report-first 工作流复盘，不假设全局历史、不提交 raw sessions |
| `explain-by-allegory` | 用寓言、故事、类比或隐喻解释复杂概念，并映射回正式概念、边界和误区 |
| `github-evidence-triage` | 对 GitHub issue / PR 做只读证据分流，输出带 URL、commit、文件行号或 `[UNVERIFIED]` 标记的报告 |
| `harness-issue-triage` | 对用户反馈的 harness / workflow 行为问题做只读定位，判断问题属于 command、skill、protocol、docs、installer、memory、subagent packet 或 agent prompt 哪一层，并说明怎么改 |
| `harness-evolution` | 对 ROSE、skills、commands、subagents、memory、install、harness docs 等流程变更执行 report-first 治理 |
| `harness-optimization-audit` | 只读 report-first harness routing、context cost、subagent parallelism、review fan-out、false PASS 和 evidence-loss 审计；只向 ROSE 返回批准修改或未定位缺口，不自动调用下一流程 |
| `parallel-subagent-dispatch` | `aili-agent-selection/v1` canonical role matrix 与 ordinary proactive trigger scan；formal ready package 使用 exact owner；共享合同支持 one-shot/persistent adapter，当前 OpenCode Task context 仍为单 assignment、terminal、不可 resume 或自动重试 |
| `mature-project-pattern-research` | 仅在用户明确要求 prior art，或 ROSE 指出一个会改变决定的成熟项目证据缺口时，研究一个有界问题并返回来源、模式、风险和不确定性 |
| `oss-release-readiness` | OSS、npm 或 public release readiness 非破坏性检查，覆盖 package metadata、dry-run evidence、license/provenance、内部 artifact 暴露和消费端说明 |
| `pr-test-analysis` | PR / diff 测试影响、CI 日志、changed-test 审查和最小测试矩阵路由 |
| `review-pipeline` | 仅在显式 specialist-review intent 或一个直接检查无法覆盖的具体 review 缺口下，路由最多一个 auxiliary capability；不自动 fan-out，也不是最终 PASS gate |
| `requirements-grilling` | AILI DEFINE 的 bounded clarification adapter；默认一次问一个改变决定的问题，多个已知独立 blocker 可生成静态 `interview.md` packet，用户显式要求 batch grilling 时按 dependency-ready decision frontier 分轮提问，且不自动调用其他 process skill 或派发 subagent |
| `rose-memory` | ROSE project-local SQLite memory 工作流 |
| `silent-failure-hunting` | 静默失败、误报成功、吞错、跳过 gate 或 stale evidence 风险的只读 review 路由 |
| `write-skills` | 以 Predictability、Create / Revise / Evaluate 分支和 `SKILL.md + GLOSSARY.md` 信息层级创建、修改或评估本仓库 Agent Skills |
| `strategy-stress-test` | 仅在用户明确要求，或 ROSE 指出具体材料性漏洞时执行一次有界反方检查；不因 write-back、implementation、review 或 completion 自动触发 |
| `test-document-generator` | 在显式 test-plan/QA/acceptance-matrix intent 或正式 DEFINE 的具体 testability gap 下生成紧凑测试文档；不为普通 implementation、TDD、review 或 completion 自动建流程 |

`requirements-grilling` 和 `test-document-generator` 的输出规则是：OpenSpec change 直接写入 change 目录；`requirements-grilling` 继续写 `interview.md`，不写 `grill.md` 或 `requirements-grilling.md`；所有非 OpenSpec 输入都先询问生成位置，包括单个普通文档、目录、多文档、粘贴文本或落点不明确的情况。可选落点包括同级文件、同级文件夹、追加到现有文档或只在聊天中输出。

### 来自 ayghri/i-have-adhd 的适配

| Skill | 说明 |
|---|---|
| `i-have-adhd` | 仅在显式调用或明确请求 ADHD/action-first 低摩擦表达时塑造当前回复：答案或行动优先、必要时编号、抑制旁支、只报告当前增量，并让安全、证据、授权和用户要求的细节优先于简短。它不安装 Hook、flag、service 或全局规则，也不承诺后续轮次或跨会话持续生效。 |

该 Skill 改编自 [ayghri/i-have-adhd](https://github.com/ayghri/i-have-adhd) 固定提交 `34f746dda9664fb5ea52149be5dbab2adc6e60d3`，遵循 MIT License，Copyright (c) 2026 Ayoub Ghriss。固定上游正文、许可证和 notice 以不可运行的 revisioned reference 形式保存在 canonical Skill 内；上游 Hook、vendor metadata、session persistence、强制时长估算和五项列表限制不属于本仓库运行时行为。

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

`using-agent-skills`、`repo-evidence-first` 和 `verification-before-completion` 已退役，不再是 runnable 或 default-installed skill，也没有 compatibility alias。窄能力选择由 ROSE/AILI routing owner 负责；非平凡仓库改动的 source/owner/test/config 取证继续由全局 Evidence Before Edits 规则负责；完成声明继续由 lifecycle/ROSE 选择支持该 claim 的最小 fresh check。

### 来自 MiniMax-AI/skills

以下 skills 来自 [MiniMax-AI/skills](https://github.com/MiniMax-AI/skills)，原项目许可为 MIT License，版权归 MiniMax 所有。本仓库纳入的是适合个人 OpenCode 工作流的开发、文档、移动端、视觉和文件处理类 skills。

| Skill | 说明 |
|---|---|
| `android-native-dev` | Android Native、Kotlin、Compose 和 Material Design 3 |
| `flutter-dev` | Flutter、Riverpod/Bloc、GoRouter 和跨平台开发 |
| `frontend-dev` | 高级前端、视觉设计、动画和媒体增强页面 |
| `fullstack-dev` | 全栈后端架构、REST API、认证和前后端集成 |
| `ios-application-dev` | iOS、UIKit、SnapKit、SwiftUI 和 Apple HIG |
| `minimax-docx` | [框架内] DOCX 唯一 artifact owner；对 installed-help-confirmed 简单操作优先使用 installer-managed OfficeCLI，复杂结构/模板保真保留 OpenXML fallback |
| `minimax-pdf` | PDF 生成、表单填写和视觉重排 |
| `minimax-xlsx` | [框架内] XLSX/CSV/TSV 唯一 artifact owner；简单 `.xlsx` 操作优先使用 installer-managed OfficeCLI，CSV/TSV 分析保留 pandas，`.xlsm`/VBA/高保真场景保留 XML fallback |
| `pptx-generator` | [框架内] 唯一通用 PowerPoint/PPTX workflow owner；采用 workspace-first 可重建工作区，以逐页 Markdown 作为页数、顺序、标题、Layout 与 Content 的唯一语义源，并用 hash-bound outline/build/render/visual-review readiness 失败关闭。模板编辑先确认参考角色和复用范围，再记录 template profile、shape→paragraph→run 样式与 renderer-visible 字体环境；所有可编辑文本形状使用 shape-to-fit-text，且必须通过重算后几何、OfficeCLI issues、图片比例、逐页视觉观察和模板 proof 确认门禁。OfficeCLI 仅为内部非路由 local-prefix tool adapter。[已知\|用户] 该 Skill 继续融合用户批准的 MiniMax 基础、人工 PPT 学习笔记英文译注、图片自然语言描述和脱敏逐页规划方法，不分发原课程 PPT、PDF、图片、会话原文或个人数据。来源：2026-07-29 至 2026-07-30 用户批准的 harness 改造与 accepted change `pptx-workspace-officecli-integration`。 |
| `react-native-dev` | React Native、Expo、导航、状态、测试和发布 |
| `shader-dev` | GLSL、ShaderToy、SDF、粒子和视觉特效 |

未纳入 `vision-analysis`、`gif-sticker-maker`、`minimax-multimodal-toolkit`、`minimax-music-gen`、`minimax-music-playlist`、`buddy-sings`，因为它们更偏 MiniMax API key 驱动的视觉、多模态或音乐娱乐工作流，不属于当前默认个人 OpenCode 工作流范围。

[已知|外部] `pptx-generator` 的 source hierarchy、fingerprint、readiness、render QA 与 delivery-audit 机制以 clean-room 方式选择性参考 [siril9/presentation-skill](https://github.com/siril9/presentation-skill/tree/3a22eed290fa2205b6a1e2de5549b4429c5fffd0) 固定提交 `3a22eed290fa2205b6a1e2de5549b4429c5fffd0`（MIT License，Copyright (c) 2026 Siril Sengolraj）。来源：该固定 GitHub revision。[框架内] 本仓库不复制其文件字节、不 vendoring 或注册其 Skill/plugin/model/subagent/lifecycle runtime，因此不制造 upstream byte mapping 或第二个 PPT 路由入口。

[已知|外部] OfficeCLI adapter 固定 `@officecli/officecli@1.0.143`，其许可为 Apache-2.0。来源：[OfficeCLI v1.0.143](https://github.com/iOfficeAI/OfficeCLI/releases/tag/v1.0.143) 与 installer-owned `manifests/officecli-tool.json`。[框架内] OfficeCLI 是 DOCX/XLSX/PPTX 三个现有 artifact Skills 共用的 non-routable external tool；安装所有权属于 AILI installer，默认 managed target 为 `$HOME/.agents/tools/officecli`。仓库不提交 OfficeCLI binary/node_modules，不注册 OfficeCLI Skill/MCP/public command，不修改 PATH/shell 配置，也不调用 package full installer。[未验证] 本仓库的 fake/temp 检查不证明真实 npm/native install、三格式复杂 round-trip、目标 viewer fidelity 或非 OpenCode Harness 等价性。

### 来自 bytedance/deer-flow 的 clean-room pattern absorption

以下 skills / skill 增量以 clean-room 方式吸收 [bytedance/deer-flow](https://github.com/bytedance/deer-flow) 公共 skill 的工作流模式，原项目许可为 MIT License，版权归 Bytedance Ltd. and/or its affiliates 与 DeerFlow Authors 所有。本仓库没有 vendoring DeerFlow 运行时、工具、路径、provider 配置或品牌文本；除本节来源说明外，新增内容均按 AILI/OpenCode 约束重写，不复制上游 skill 正文。

| Skill / 内容 | 说明 |
|---|---|
| provenance | Clean-room pattern absorption from [bytedance/deer-flow](https://github.com/bytedance/deer-flow); MIT License, Bytedance Ltd. and/or its affiliates / DeerFlow Authors; no DeerFlow runtime, provider configuration, tool paths, or upstream skill正文 are vendored. |
| `academic-paper-review` | 单篇论文的来源锚定综述、方法/证据/可复现性 critique |
| `systematic-literature-review` | 多论文系统综述、检索策略、纳排标准、证据矩阵和 synthesis-over-listing |
| `newsletter-generation` | 从来源材料生成 newsletter / digest，并显式区分事实、编辑角度和未验证项 |
| `consulting-analysis` | 咨询式问题拆解、假设/选项/风险/建议输出，禁止无来源商业断言 |
| `data-analysis` | 数据分析前置真实性检查、质量剖析、清洗说明、限制和发现输出 |
| `chart-visualization` | 图表选择、误导性图表审查、可访问性和数据映射规范 |
| `write-skills` 增量 | 强化 progressive disclosure、trigger eval、外部 skill provenance、runtime-assumption 清理和 claim-matched completion criteria |
| `mature-project-pattern-research` / `github-evidence-triage` / `documentation-and-adrs` 增量 | 强化 synthesis-over-listing、证据分组、来源锚定文档和 `Unverified` 标记 |
| `frontend-ui-engineering` / `browser-testing-with-devtools` 增量 | 强化 anti-generic UI、runtime UI audit、事实性 proof-point 检查和 browser evidence 记录 |

未纳入 DeerFlow provider/media/deploy/runtime 类 skills，也未引入外部依赖、provider API 调用、DeerFlow 专用路径或工具假设。

### 来自 ECC / review-skill prior art 的 clean-room pattern absorption

以下 agents / skills 以 clean-room 方式吸收 [affaan-m/ECC](https://github.com/affaan-m/ECC) agent 角色与若干公开 review-skill prior art 的工作流模式。本仓库没有 vendoring ECC 运行时、工具配置或上游 prompt 正文；新增内容按 AILI/OpenCode 权限、证据、claim hygiene 和 lifecycle 约束重写。

| 内容 | 说明 |
|---|---|
| `agents/spec-miner.md` | 吸收 spec-mining 角色边界，改写为只读候选 requirement / scenario 证据提炼 subagent |
| `agents/agent-evaluator.md` | 吸收 agent-output evaluator 角色边界，改写为只读任务适配、证据质量、claim hygiene、overclaiming 和 handoff 可用性审查 |
| `agents/opensource-sanitizer.md` | 吸收 open-source sanitizer 角色边界，改写为只读、脱敏、非发布、非删除的 OSS/npm/public exposure 审查 |
| `comment-accuracy-review` | 吸收 comment analyzer 思路，改写为 comment/JSDoc/TODO/docs-to-code fact-check skill |
| `oss-release-readiness` | 吸收 open-source sanitizer / packager 方向，改写为非破坏性 OSS/npm release readiness checklist |
| `build-failure-repair` | 吸收 build-error-resolver 方向，改写为先调查、再最小修复、禁止跳过 gate 的 workflow skill |
| `harness-optimization-audit` | 吸收 harness optimizer 方向，改写为 report-first harness routing/cost/quality audit，批准编辑转 `harness-evolution` |
| `code-review-quality-gates` | Clean-room 吸收 [sanyuan0704/sanyuan-skills](https://github.com/sanyuan0704/sanyuan-skills/tree/main/skills/code-review-expert)、[alirezarezvani/claude-skills](https://alirezarezvani.github.io/claude-skills/skills/engineering-team/code-reviewer/) 和 [laolaoshiren/claude-code-skills-zh](https://github.com/laolaoshiren/claude-code-skills-zh/tree/main/skills/zh-code-reviewer) 的 review quality patterns，作为 rubric/test-enhancement skill 而非重复 reviewer agent |

未纳入 ECC 语言专用 reviewer swarm、`type-design-analyzer`、破坏性 open-source forker/publisher 或重复 general code-review agent。

### 思想来源

- `agents/rose.md` 和全局 agent operating discipline 中的少量编码 guardrail 表述，概念上参考了 [Andrej Karpathy 关于 agent coding 行为的帖子](https://x.com/karpathy/status/2015883857489522876) 以及 [forrestchang/andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills) 的 `CLAUDE.md` 方向（如先思考、保持简单、手术式修改、目标驱动执行）。当前仓库未 vendored 该仓库文件；如后续复制上游文本或文件，请先确认并补充对应第三方声明。
- `.agents/skills/explain-by-allegory/SKILL.md` 概念上参考了 Amanda Askell-style allegory / analogy prompting 的解释方式（见 [Amanda Askell](https://askell.io/) 个人页面作为人物来源线索），本仓库仅保留“先讲故事、再映射正式概念、再说明类比失效点”的工作流结构，未复制外部 prompt 文本。
- `.agents/skills/evidence-scoped-retrospective/SKILL.md` 概念上参考了 Vaibhav / VB / Codex-style self-improvement prompting 的“回看近期工作并提出流程改进”方向，但改为 OpenCode 可证据化版本：只分析用户显式提供或批准的证据，不声称可见全局历史，且先报告再走既有变更门禁；未复制外部 prompt 文本。
- `.agents/skills/evidence-scoped-retrospective/SKILL.md` 的 failure-pattern taxonomy 和 `templates/AGENTS.md` 的 selected guardrails 概念上参考了用户提供的 Mnilax / Karpathy / Forrest Chang-style coding-agent discipline summary。用户请求使用 [Mnilax X 链接](https://x.com/Mnilax/status/2053116311132155938) 作为 attribution；direct X content 在本次实现中未直接抓取，按 conceptual / user-provided source 标注，未复制原文。
- `.agents/skills/write-skills/SKILL.md` 的结构原则概念上参考了 OpenAI Codex Agent Skills 的 skill authoring 思路，验证流程概念上参考了 Anthropic skill creator 的访谈、测试和迭代方法；这些来源未 vendored 上游文件。
- `.agents/skills/strategy-stress-test/SKILL.md` 概念上参考了用户提供的 [X 链接](https://x.com/cjzafir/status/2052110266566107321) 中关于 confidence calibration / loophole loop 的提示思想，并工程化为“事实可证高置信、默认 1 轮且最多 3 轮、Open Question / Unverified 标记”的 workflow guardrail。当前仓库未 vendored 上游文本。
- `agents/doc-researcher.md`、`agents/web-researcher.md`、`agents/plan-auditor.md`、`.agents/skills/review-pipeline/SKILL.md`、`.agents/skills/github-evidence-triage/SKILL.md` 以及 `implementer` / `git-workflow-and-versioning` / `strategy-stress-test` 的部分边界设计，概念上吸收了用户提供的 oh-my-opencode / oh-my-openagent 角色拆分建议（上游现名 `oh-my-openagent`，曾用名 `oh-my-opencode`；如 Librarian、Metis、Momus、Hephaestus、git-master、review-work、github-triage、hyperplan 的能力边界），但未复制上游文件文本。
- `requirements-grilling` 直接复制/改编 [Matt Pocock 的 skills](https://github.com/mattpocock/skills) 中 `grill-me`、`grilling`、in-progress `batch-grill-me` 与 `domain-modeling` 的核心行为和 `ADR-FORMAT.md` / `CONTEXT-FORMAT.md` 参考格式，按上游 MIT License 保留精确 inert pin 与来源说明，并加上 AILI/OpenSpec 的单一 canonical skill、Interactive / static Packet / explicit Frontier Batch 三模式、ROSE-owned evidence routing、`interview.md`、`context.md`、`adr.md`、readiness gate 与无新增 `/grill`、`/grill-me`、`/batch-grill-me` 命令约束。其他 workflow 纪律仍仅概念上参考 zoom-out、prototype、to-issues、diagnose、tdd、write-a-skill、improve-codebase-architecture 等方向，未复制上游文本。

## 使用说明

这个仓库面向 OpenCode 使用，核心约定是通过自然语言任务触发 agent 和 skill；同时提供且只提供四个 delivery shortcut：`/ideate`、`/define`、`/build`、`/ship`，分别对应 `commands/{ideate,define,build,ship}.md`，由 `.agents/skills/aili-delivery-flow` 承接。自然语言中的等价 IDEATE、DEFINE、BUILD、SHIP 意图使用同一分类器、门禁和证据契约；shortcut 不获得额外权限。另提供 `/local-review` 作为非 delivery-mode 的本地 report-first 审查入口，可审查 local changes、base branch、commit、PR 或 OpenSpec change，并在修复前先输出分类报告；它不覆盖 OpenCode 内置 `/review`，也不替代 `/ship`。DEFINE 必须先关闭 decision-shaping research / material blockers、保证 artifacts coherent 且 strict-valid，并取得最终 `test-plan.md` acceptance。BUILD 只执行 active contract 导出的 accepted queue 和 progress savepoints，再做一次最小 changed-scope completion check，记录 `IMPLEMENTED_TARGETED_VERIFIED` 后停在 SHIP 之前；不自动增加 package-local tests/reviews/security fanout、commit 或 approval。SHIP 需要新的显式 intent 和当前 implementation evidence，复用仍覆盖 exact content/target/config/toolchain 的 BUILD evidence，只选择 stale、affected、risk、integration、packaging、release、merge-result 或 target-specific checks。仓库不提供 `/loop`、`/schedule`、`/goal`、`/proactive`、`/cycle`、`/watch`、`/objective`、worktree-maintenance 或 Graphify command，也不提供 `/research`、`/questionnaire`、`/grill`、`/grill-me`、`/batch-grill-me`、`/test-plan`、`/implement`、`/fix`、`/debug`、`/review`、`/release-blocker-audit`、`/evolve` 等内部阶段命令。AILI 不注册隐藏或未请求的 cron、scheduler、watcher、webhook、listener、daemon、persistent queue、hook 或 auto-retry runtime；显式 product/repository automation 仍须通过正常 formal/high-risk gates。

已请求且在范围内的安全本地读取、编辑、确定性诊断和 claim-matched 检查不需要逐步微审批；外部/破坏性、依赖/lockfile、schema/auth/security、Git/release 和 A33 ADD/REMOVE 仍使用各自的 exact gate。每个 subagent Task context 都是 single-use terminal session，subagent 不得委派、恢复旧 context 或取得 lifecycle/integration/verdict ownership。

### A33 attached-repository boundary

用户通过在一个 Git repository 中启动 OpenCode 来选择 A33 host；AILI 不提供 host selector，也不移动、排名或广泛扫描 host。每个 attachment 独立使用 current `WT-001` 的 `a33-attached-shared-trust-domain` mode，目标只能是 `<session-root>/.worktrees/<repo_key>/<worktree_key>`；两个 key 都必须匹配 `^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$`、非保留且无 path/worktree/branch collision，并通过 exact root `/.worktrees/` ignore、no re-inclusion、no tracked destination 和 trusted topology admission。`a30-a31-external-read`、A30 runtime results 以及 A32/item-41 readiness evidence 只保留为 historical/stale evidence，不能证明当前 A33 readiness。

一个 host 可以声明多个 attachment，但每个 repository lane 必须分别持有 exact keys、17-field no-digest `A33Identity` pre/post evidence、target rules、artifact destination 和 fresh operation state；不得跨 attachment 复制或重绑定。PREPARE 无 add/remove 效果；每次 real/fixture ADD 需要 fresh exact key/class-bound approval 和 accepted trusted-code risk，之后的 non-force REMOVE 需要另一份 fresh exact approval、完整 deletion inventory 和独立 risk gate。REMOVE 保留 branch ref/reflog，rollback 保留 worktrees 和 evidence。host 与 attachments 必须是 same-owner、same-sensitivity、mutually trusted 的 shared trust domain；OpenCode path/cwd/permission controls 只是 soft coordination boundary，不是 sandbox 或 hard isolation。target rules 只能收窄权限、同级冲突即 block，user-visible artifacts 只能写入 owning target repository。CodeGraph status/query/init evidence 也必须逐 declared target 单独确认，不能用 host 或另一个 attachment 的结果代替。

### OpenCode 设置

[KNOWN] 推荐安装入口是 `rose-aili` Node/TypeScript CLI；Bash 脚本仍保留为兼容 fallback。
[框架内] 默认 `install` / `update` 先同步共享 `$HOME/.agents/skills`，再 detect-or-install installer-managed OfficeCLI；`--skip-officecli` 显式跳过该 tool step。只有显式添加 `--opencode`，才会把全局通用规则从 `templates/opencode-global-AGENTS.md` 安装到 OpenCode home 的 `AGENTS.md`，并安装 agents、commands、OpenCode 专属 skills 及同步 OpenCode config；项目级事实仍由各项目自己的瘦 `AGENTS.md` 管理。

[框架内] 默认 scope 可写共享 `$HOME/.agents/skills` 与固定 OfficeCLI target `$HOME/.agents/tools/officecli`，但不会读取或修改 OpenCode home。`--skip-officecli` 不探测、不创建 tool target、不运行 npm；`--dry-run` 只报告 exact package/target/argv 与 network/dependency effects。`--opencode` 才启用 OpenCode 安装范围；Playwright MCP、CodeGraph、Graphify 和 OpenSpec 仍是独立显式 opt-in，AILI 不安装、检测、配置、迁移或删除 DCP。

```bash
npx -y rose-aili install
npx -y rose-aili install --skip-officecli
npx -y rose-aili install --opencode
```

在 npm 发布前，AI assistant 可从 GitHub package spec 运行同一个 binary（把 `<owner>/<repo>` 替换为用户提供的仓库）：

```bash
npx -y --package github:<owner>/<repo> rose-aili install
```

常用维护命令：

```bash
npx -y rose-aili update
npx -y rose-aili update --skip-officecli
npx -y rose-aili update --opencode
npx -y rose-aili doctor
```

[框架内] `rose-aili install` 默认复用 `scripts/install_opencode.sh` 的条目级安全语义同步 manifest 中目标为 `shared` 的 `.agents/skills`，随后由 installer owner 执行一次 OfficeCLI detect-or-install；compatibility invocation 会抑制重复 tool step。OfficeCLI failure 返回非零并单独报告，但不回滚已完成的 Skill 同步。`--opencode` 在此基础上安装全局 `AGENTS.md`、agents、commands，以及源自 `.opencode/skills` 且 manifest 目标为 `opencode` 的专属 skills；从普通 git clone 安装时使用 selective symlink，从 npm/npx packaged 非 git 目录安装时使用 copy。显式 `install`/`update` 仍只清理能证明由当前 canonical source 管理的退役 skill symlink，其他内容全部保留并报告。OpenSpec 仅在 `--opencode --enable-openspec` 下运行。OpenCode config 同步也只在 `--opencode` 范围启用，并继续保留冲突默认值和既有 model：

[KNOWN] 只有交互式 `rose-aili install --opencode` 才询问 default agent、model override、Playwright MCP、CodeGraph、Graphify CLI 和 OpenSpec；`update --opencode` 询问 CodeGraph 与 Graphify CLI。无 `--opencode` 的交互安装不读取 OpenCode config，也不提出 OpenCode 集成问题。

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
npx -y rose-aili install --yes
npx -y rose-aili install --dry-run
npx -y rose-aili install --skip-officecli
npx -y rose-aili install --opencode --set-default-rose
npx -y rose-aili install --opencode --model anthropic/claude-sonnet-4-5
npx -y rose-aili install --opencode --skip-opencode-config
npx -y rose-aili install --opencode --enable-playwright
npx -y rose-aili install --opencode --enable-codegraph
npx -y rose-aili install --opencode --enable-graphify
npx -y rose-aili install --opencode --skip-graphify
npx -y rose-aili install --opencode --register-graphify-skill
npx -y rose-aili install --opencode --enable-openspec --project-root /absolute/project
npx -y rose-aili install --opencode --skip-openspec
npx -y rose-aili update --opencode --skip-openspec
npx -y rose-aili update --skip-officecli
```

[KNOWN] 非交互或 `--yes` 模式不会假装已经询问用户问题；默认 summary 会报告 `componentInstall.scope: "skills"` 并给出 `--opencode` 后续命令。`--opencode` 范围内的 config 同步会设置/保持 `default_agent: "rose"`，但不会静默启用 Playwright、CodeGraph、Graphify、OpenSpec 或 model override。

[KNOWN] CodeGraph 是 OpenCode 范围内的显式 opt-in：`--opencode --enable-codegraph` 会先运行 `npm install -g @colbymchenry/codegraph@latest`，再运行 `codegraph install --target=opencode --yes`；失败不会否定已完成的 manifest component 安装。

Graphify 也是独立 opt-in，并分成两个不能合并授权的 invocation。`--enable-graphify` 只在已存在 `uv` 时执行官方 `uv tool install graphifyy`；它不安装 uv、Python 或系统包，也不回退到 pip/pipx/APT/Homebrew/source build。CLI 安装完成后，必须在另一次 fresh exact approval 下运行 `--register-graphify-skill`，该阶段只委托官方 `graphify install --platform agents`，目标是上游拥有的 `~/.agents/skills/graphify/`。两个 flag 同时出现会被拒绝；`--yes`、CodeGraph consent、BUILD acceptance 或第一个操作的批准都不授权第二个操作。`--dry-run` 只报告两个 operation packet 和目标 inventory，不执行 uv/Graphify 或写入 home/project。

Graphify 注册验证要求常规 `SKILL.md`、`.graphify_version`、可选 packaged references 与唯一 OpenCode catalog route，并确认当前仓库 `.opencode` 没有变化；该流程不安装项目 plugin/config，不运行 `/graphify`，也不 build/update/query 项目 graph。`doctor` 分开报告 `graphifyCli` 和 `graphifyGlobalSkill` 的 observed upstream-owned 状态。已有可用 graph 时，官方全局 `graphify` skill 只提供一次有界 architecture orientation；exact symbols、source、call paths、tests 和 current impact 仍由 CodeGraph 或当前文件确认。任何项目级 Graphify 运行、升级、重装、注销或删除都是新的独立 operation。

项目内 CodeGraph 初始化不属于全局安装。AI agent 只能在确认当前仓库根目录后，对该仓库运行 `codegraph init -i` 和 `codegraph status`；A33 host 和每个 declared attachment 都必须逐 target 单独确认 root、状态和 approval，不能复用另一个 target 的 CodeGraph 结果。不得因为 CodeGraph 初始化顺手运行 `openspec init`，也不得未经明确授权批量初始化多个仓库。

项目级 `AGENTS.md` 初始化 / 更新应联动检查 CodeGraph：生成或更新 `AGENTS.md` 后先运行/请求 `codegraph status`；如果该仓库尚未初始化，则询问用户是否在当前仓库运行 `codegraph init -i`，同意后再运行 `codegraph status`。CodeGraph 不可用、用户跳过或拒绝时，不阻塞 `AGENTS.md` 完成，但必须在结果中说明没有代码地图覆盖。

[KNOWN] OpenSpec 是 OpenCode 范围内的显式 opt-in：只有 `--opencode --enable-openspec --project-root <absolute-path>` 才会检测/安装 CLI 并运行项目 `update` 或 `init`。

### 分发与来源边界

`package.json#files` 的 npm 分发面包含构建后的 CLI、全部 canonical agents、四个 delivery commands 与独立 `local-review`、`.agents/` 下的 canonical skills/protocols/helpers、`manifests/`、两个 AGENTS 模板、`agents_md.py`、兼容安装脚本、两个明确列出的 Graphify/upstream contract fixtures 以及 README/setup 文档。其他仓库级 checker、测试和 harness fixtures 不属于已安装 runtime；已打包的 `session-handoff` helper 只是该 skill 的确定性实现，不注册为 command 或独立 runnable skill。root `.worktrees/`、visible `worktrees/` 和 historical `.tmp/worktrees/` 都不在 package allowlist 中。

固定上游材料位于现有 canonical skills 的 `references/upstream/` 中，并由 `manifests/upstream-references.json` 记录精确 pin、blob/hash、license/notice、`0644` mode 和 source→local mapping。上游 `SKILL.md` 以 `SKILL.upstream.md` 保存，脚本必须作为 non-executable data；这些文件随 `.agents/` 作为 inert reference data 打包，但不出现在 component manifest 的 skills 列表中，不获得 routing、approval、permission 或 execution authority。canonical AILI adapters 仍是各 skill 顶层唯一的 `SKILL.md`。

当前分发保持 fail-closed：OpenCode `1.17.18` 临时 installed-catalog 对递归 reference data 的排除仍是 `UV-005`，且当前文件系统不能证明所有 upstream script mode 满足 `0644` 时，不得据此声称 distribution/registration/enablement 或 release readiness。`npm pack --dry-run` 只检查计划包内容，不发布，也不解决这些 runtime/mode 缺口。

Graphify 的 CLI 安装、全局 agents-skill 注册和任何项目操作互不授权；每个真实操作都需要自己的 fresh exact approval。AILI 的 installer/doctor 只验证 observed upstream version/path/files/catalog 与当前仓库 `.opencode` 无变化，不承诺上游 support/security/sandbox/index integrity，也不把 Graphify 当作 lifecycle、completion 或 release authority。

### 版本化 session handoff

`session-handoff` 只在用户明确要求 CREATE/LIST/RESUME 或 accepted lifecycle 明确命名 handoff point 时触发。OpenSpec change 使用 `openspec/changes/<change-id>/handoffs/`，普通任务使用已确认 `<task-root>/handoffs/`；旧 `<task-root>/handoff.md` 只作显式选择的只读兼容输入。每个 finalized snapshot 都保留为 timestamped immutable Markdown，`LATEST.md` 是带 exact relative path、snapshot ID、SHA-256 和 finalized time 的 atomic regular-file pointer。

该 skill 内的 `scripts/session_handoff.py` 不是另一个 workflow 或公共命令，而是低自由度的确定性 helper：它统一处理 exclusive collision suffix、containment/symlink validation、draft/finalize、pointer replacement、bounded-frontmatter LIST、exact-first RESOLVE、legacy read-only 和 localized exact-path resume output。没有显式触发时不创建 handoff；没有自动 memory promotion、rotation、archive 或 prune；恢复仍要重新验证当前 root/worktree/Git/contracts/permissions/evidence。

[框架内] Direct Bash fallback 的 `scripts/install_opencode.sh --mode selective` 默认同步共享 skills 并执行同一固定 OfficeCLI detect-or-install contract；传 `--skip-officecli` 可只同步 components。要安装 OpenCode 全局 `AGENTS.md`、agents、commands 和 OpenCode-only skills，使用 `scripts/install_opencode.sh --mode selective --opencode`。

[框架内] Component 默认目标是 `$HOME/.agents/skills/`，OfficeCLI tool 默认目标另为 `$HOME/.agents/tools/officecli`。在 `--opencode` 范围内，agents/commands 安装到 OpenCode home，共享 skills 仍安装到 `$HOME/.agents/skills/`，OpenCode-only skills 从仓库 `.opencode/skills/<name>` 安装到 OpenCode home 的 `skills/<name>`。

项目级 `AGENTS.md` 不走软链接。使用 `agents-md-initialization` skill 调用 `scripts/agents_md.py`，从 `templates/AGENTS.md` 生成到目标项目后再填写项目事实，并用 `check --project .` 放进 CI 或 pre-commit 验证。

典型使用方式：

```text
1. 将本仓库作为个人 OpenCode 工作流配置来源。
2. 默认运行 `rose-aili install`，同步共享 skills 并检查 installer-managed OfficeCLI；不需要该工具时显式传 `--skip-officecli`。
3. 需要 ROSE agents、commands 或 OpenCode 专属 skills 时运行 `rose-aili install --opencode`。
4. OpenCode 从共享 `$HOME/.agents/skills/` 发现 `.agents/skills/`，并从自己的 `skills/` 发现 manifest 声明的 `.opencode/skills/`。
5. `--opencode` 安装后可使用 ROSE primary agent、subagents 和 delivery commands。
```

[框架内] 共享 skill 变化后运行默认安装；该命令也会执行 OfficeCLI detect-or-install，除非传 `--skip-officecli`。agent、command 或 OpenCode-only skill 变化后运行带 `--opencode` 的安装，再重启 OpenCode 或开启新 session。

`docs/harness/**` 是本仓库维护和审查 harness 时读取的源文档，不是普通业务项目运行时必须存在的上下文。通过软链接安装时，OpenCode 会在共享 `$HOME/.agents/skills/<name>` 目标下发现并加载被链接的 `.agents/skills/<name>`；因此运行时必须依赖的 harness 定位规则应放在对应 skill 的 `references/` 中，例如 `.agents/skills/harness-issue-triage/references/`，而不是假设每个目标项目都有 `docs/harness/**`。

`rose-memory` 是随 `.agents/skills/rose-memory/` 分发、安装到共享 `$HOME/.agents/skills/rose-memory` 目标下的 skill。它只提供操作接口，实际 memory state 固定写入当前项目的 `memory/memory.db`。

`frontend-dev` 可用于纯前端设计、实现和动画工作；只有主动使用其中的媒体生成能力时才可能需要额外 MiniMax API key、CLI 或运行时依赖。使用前请阅读对应 `.agents/skills/frontend-dev/` 目录内的 `SKILL.md`、`README.md`、`scripts/` 或 `references/`。

## 第三方声明

本仓库包含 Rosetears 个人编排内容，也包含来自第三方开源项目的 agent/skill 内容；第三方内容保留其原始版权和许可归属。仓库许可证详见根目录 [`LICENSE`](LICENSE)。

第三方内容来源：

| 来源 | 仓库 | 许可 | 版权声明 |
|---|---|---|---|
| Addy Osmani | [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | MIT License | Copyright (c) 2025 Addy Osmani |
| MiniMax | [MiniMax-AI/skills](https://github.com/MiniMax-AI/skills) | MIT License | Copyright (c) 2026 MiniMax |
| Bytedance / DeerFlow Authors | [bytedance/deer-flow](https://github.com/bytedance/deer-flow) | MIT License；clean-room pattern absorption only in this repository | Copyright Bytedance Ltd. and/or its affiliates and DeerFlow Authors; no DeerFlow runtime, provider config, tool paths, branding text, or upstream skill正文 vendored |
| affaan-m / ECC contributors | [affaan-m/ECC](https://github.com/affaan-m/ECC) | MIT License | Copyright (c) 2026 Affaan Mustafa；local-review references adapt ECC review/orchestration/build-fix patterns with provenance; no ECC runtime, tool config, public ECC command, or upstream prompt正文 vendored |
| sanyuan0704 | [sanyuan-skills](https://github.com/sanyuan0704/sanyuan-skills/tree/main/skills/code-review-expert) | 未验证；pattern-only reference；no copied text | Review-quality rubric patterns only; no upstream skill正文 vendored |
| Alireza Rezvani | [claude-skills](https://alirezarezvani.github.io/claude-skills/skills/engineering-team/code-reviewer/) | 未验证；pattern-only reference；no copied text | Review-quality and fixture/golden-output patterns only; no upstream skill正文 vendored |
| laolaoshiren | [claude-code-skills-zh](https://github.com/laolaoshiren/claude-code-skills-zh/tree/main/skills/zh-code-reviewer) | 未验证；pattern-only reference；no copied text | Chinese review-output profile patterns only; no upstream skill正文 vendored |
| Matt Pocock | [mattpocock/skills](https://github.com/mattpocock/skills) | MIT License | `write-skills` 以 AILI 重写 `SKILL.md`，本地 `GLOSSARY.md` 选择性接近改编 `writing-great-skills` 定义；`requirements-grilling` 复制/改编 grilling family 核心行为和参考格式；固定上游文件只作 inert provenance，Copyright (c) 2026 Matt Pocock |
| Amanda Askell | [askell.io](https://askell.io/) | 概念性参考；未纳入上游文本 | allegory / analogy prompting 方向参考 |
| Vaibhav / VB / Codex-style prompting | 用户提供的概念方向 | 概念性参考；未纳入上游文本 | evidence-scoped self-improvement prompting 方向参考；本仓库不声称可见全局历史 |
| Andrej Karpathy | [X post](https://x.com/karpathy/status/2015883857489522876) | 思想来源 | agent coding guardrail 方向参考 |
| Mnilax | [X post](https://x.com/Mnilax/status/2053116311132155938) | 用户提供的概念来源；direct X content 未验证 | coding-agent discipline / retrospective taxonomy 方向参考；未复制原文 |
| cjzafir | [X post](https://x.com/cjzafir/status/2052110266566107321) | 思想来源 | confidence calibration / loophole loop 方向参考；未 vendored 上游文本 |
| code-yeongyu | [oh-my-openagent](https://github.com/code-yeongyu/oh-my-openagent)（曾用名 `oh-my-opencode`） | 概念性参考；未纳入上游文件 | agent / skill 角色边界与工作流拆分方向参考，如 Librarian、Metis、Momus、Hephaestus、git-master、review-work、github-triage、hyperplan |
| Forrest Chang / Andrej Karpathy skills | [forrestchang/andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills) | 概念性参考；未纳入上游文件 | 如后续复制上游文本或文件，需先确认并保留对应版权/许可 |

如果继续从上游同步 agent 或 skill，请同步更新本 README 的来源表和许可说明。
