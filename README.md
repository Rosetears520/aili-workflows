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
│       ├── debugging-and-error-recovery/
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
│       ├── repo-evidence-first/
│       ├── requirements-grilling/
│       ├── rose-memory/             # ROSE project-local SQLite memory skill
│       ├── review-pipeline/
│       ├── security-and-hardening/
│       ├── session-handoff/
│       ├── shader-dev/
│       ├── shipping-and-launch/
│       ├── silent-failure-hunting/
│       ├── skill-authoring-and-validation/
│       ├── source-driven-development/
│       ├── spec-driven-development/
│       ├── strategy-stress-test/
│       ├── systematic-literature-review/
│       ├── test-document-generator/
│       ├── test-driven-development/
│       ├── using-agent-skills/
│       └── verification-before-completion/
├── agents/
│   ├── rose.md                  # Rosetears 的 OpenCode primary agent
│   ├── code-scout.md            # 只读代码侦察 subagent
│   ├── doc-researcher.md         # 只读本地文档研究 subagent
│   ├── web-researcher.md         # 只读联网资料研究 subagent
│   ├── plan-auditor.md           # 只读计划审计 subagent
│   ├── implementer.md           # 单任务实现 subagent
│   ├── debug-investigator.md     # 只读根因排查 subagent
│   ├── code-reviewer.md         # 代码审查 subagent
│   ├── convergence-reviewer.md  # 只读交付收敛审查 subagent
│   ├── security-auditor.md      # 安全审计 subagent
│   ├── test-engineer.md         # 测试与覆盖率 subagent
│   ├── test-coverage-reviewer.md # 只读覆盖率充分性 review subagent
│   ├── pr-test-analyzer.md      # 只读 PR 测试影响分析 subagent
│   ├── ai-regression-scout.md   # 只读 AI 回归场景侦察 subagent
│   ├── silent-failure-reviewer.md # 只读静默失败审查 subagent
│   ├── browser-qa-runner.md     # 浏览器 QA 验证 subagent
│   └── e2e-artifact-runner.md   # E2E 证据 artifact subagent
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
| `agents/debug-investigator.md` | 只读根因调查 subagent，用于修复前的失败定位和证据收集 | Rosetears 个人工作流内容，调试纪律参考 obra/superpowers |
| `agents/code-reviewer.md` | 从 correctness、readability、architecture、security、performance 维度做代码审查 | 改编自 [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) 的 `agents/code-reviewer.md`，遵循 MIT License |
| `agents/security-auditor.md` | 做安全审计、威胁建模和漏洞检查 | 改编自 [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) 的 `agents/security-auditor.md`，遵循 MIT License |
| `agents/test-engineer.md` | 做测试策略、测试补充和覆盖率分析 | 改编自 [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) 的 `agents/test-engineer.md`，遵循 MIT License |
| `agents/test-coverage-reviewer.md` | 只读覆盖率充分性、未测路径和验证证据审查 | Rosetears 个人工作流内容 |
| `agents/pr-test-analyzer.md` | 只读 PR / diff 测试影响、CI 日志和最小测试矩阵分析 | Rosetears 个人工作流内容 |
| `agents/ai-regression-scout.md` | 只读 agents / prompts / skills / routing 回归场景侦察 | Rosetears 个人工作流内容 |
| `agents/silent-failure-reviewer.md` | 只读静默失败、误报成功、跳过 gate 和 stale evidence 审查 | Rosetears 个人工作流内容 |
| `agents/browser-qa-runner.md` | 本地浏览器 QA 验证；写截图、trace、报告前要求仓库内 artifact 落点，禁止生产数据变更 | Rosetears 个人工作流内容 |
| `agents/e2e-artifact-runner.md` | E2E trace、video、screenshot、report、failure bundle 证据收集；要求仓库内 artifact 落点，禁止生产数据变更 | Rosetears 个人工作流内容 |
| `agents/spec-miner.md` | 只读 spec mining subagent，从现有代码、测试、文档和 OpenSpec artifact 提炼候选 requirements / scenarios，不批准或编写 specs | Clean-room pattern absorption from [affaan-m/ECC](https://github.com/affaan-m/ECC) agent role |
| `agents/agent-evaluator.md` | 只读 agent / subagent 输出评估 subagent，检查任务匹配、证据质量、claim hygiene、约束遗漏、overclaiming 和 handoff 可用性 | Clean-room pattern absorption from [affaan-m/ECC](https://github.com/affaan-m/ECC) agent role |
| `agents/opensource-sanitizer.md` | 只读 OSS / npm / public-release 暴露面审查 subagent，报告 secrets/private data/package/prompt/provenance 风险且必须脱敏 | Clean-room pattern absorption from [affaan-m/ECC](https://github.com/affaan-m/ECC) agent role |

本仓库已移除这些 agent 文本中对 slash command 的直接引用，保留为 OpenCode 主代理自然语言触发和 MainAgent 编排使用。

## Skill 来源

### Rosetears 原创 workflow skills

| Skill | 说明 |
|---|---|
| `agents-md-initialization` | 从 `templates/AGENTS.md` 初始化、更新和检查项目级 `AGENTS.md` |
| `aili-delivery-flow` | AILI 交付生命周期权威：IDEATE、DEFINE、BUILD、SHIP 四模式、后端 adapter、artifact gate、review/repair/closeout |
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
| `harness-optimization-audit` | 只读 report-first harness routing、context cost、subagent parallelism、review fan-out、false PASS 和 evidence-loss 审计；批准修改后转 `harness-evolution` |
| `mature-project-pattern-research` | 在 IDEATE 或普通聊天中研究成熟公开项目的 prior art，输出来源、成熟度信号、可借鉴/不推荐模式、风险、不确定性和下一步决策 |
| `oss-release-readiness` | OSS、npm 或 public release readiness 非破坏性检查，覆盖 package metadata、dry-run evidence、license/provenance、内部 artifact 暴露和消费端说明 |
| `pr-test-analysis` | PR / diff 测试影响、CI 日志、changed-test 审查和最小测试矩阵路由 |
| `review-pipeline` | 实现后编排 code-reviewer、test-engineer、security-auditor 等 reviewer，收敛 findings、执行 fix loop，并作为最终 PASS 前的 gate |
| `requirements-grilling` | AILI DEFINE 的 canonical requirements grilling skill；保留 `interview.md` artifact，兼容旧 `change-interviewer`/interview packet 触发，并吸收用户答案后写回目标文件 |
| `rose-memory` | ROSE project-local SQLite memory 工作流 |
| `silent-failure-hunting` | 静默失败、误报成功、吞错、跳过 gate 或 stale evidence 风险的只读 review 路由 |
| `skill-authoring-and-validation` | 创建、修改和验证本仓库 Agent Skills 的工作流 |
| `strategy-stress-test` | 非平凡方案、问卷、计划、reconciliation、review 或完成声明接受前的反方审稿 / 证据校准 workflow guardrail |
| `test-document-generator` | 根据 spec、方案、issue、描述或 OpenSpec change 生成详细测试文档、测试矩阵、回归范围和验收清单，默认写入仓库内 Markdown 文件 |

`requirements-grilling` 和 `test-document-generator` 的输出规则是：OpenSpec change 直接写入 change 目录；`requirements-grilling` 继续写 `interview.md`，不写 `grill.md` 或 `requirements-grilling.md`；所有非 OpenSpec 输入都先询问生成位置，包括单个普通文档、目录、多文档、粘贴文本或落点不明确的情况。可选落点包括同级文件、同级文件夹、追加到现有文档或只在聊天中输出。

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
| `skill-authoring-and-validation` 增量 | 强化 progressive disclosure、trigger eval、外部 skill provenance 和 runtime-assumption 清理 |
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

- `agents/rose.md` 和 `.agents/skills/using-agent-skills/SKILL.md` 中的少量编码 guardrail 表述，概念上参考了 [Andrej Karpathy 关于 agent coding 行为的帖子](https://x.com/karpathy/status/2015883857489522876) 以及 [forrestchang/andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills) 的 `CLAUDE.md` 方向（如先思考、保持简单、手术式修改、目标驱动执行）。当前仓库未 vendored 该仓库文件；如后续复制上游文本或文件，请先确认并补充对应第三方声明。
- `.agents/skills/explain-by-allegory/SKILL.md` 概念上参考了 Amanda Askell-style allegory / analogy prompting 的解释方式（见 [Amanda Askell](https://askell.io/) 个人页面作为人物来源线索），本仓库仅保留“先讲故事、再映射正式概念、再说明类比失效点”的工作流结构，未复制外部 prompt 文本。
- `.agents/skills/evidence-scoped-retrospective/SKILL.md` 概念上参考了 Vaibhav / VB / Codex-style self-improvement prompting 的“回看近期工作并提出流程改进”方向，但改为 OpenCode 可证据化版本：只分析用户显式提供或批准的证据，不声称可见全局历史，且先报告再走既有变更门禁；未复制外部 prompt 文本。
- `.agents/skills/evidence-scoped-retrospective/SKILL.md` 的 failure-pattern taxonomy 和 `templates/AGENTS.md` 的 selected guardrails 概念上参考了用户提供的 Mnilax / Karpathy / Forrest Chang-style coding-agent discipline summary。用户请求使用 [Mnilax X 链接](https://x.com/Mnilax/status/2053116311132155938) 作为 attribution；direct X content 在本次实现中未直接抓取，按 conceptual / user-provided source 标注，未复制原文。
- `.agents/skills/skill-authoring-and-validation/SKILL.md` 的结构原则概念上参考了 OpenAI Codex Agent Skills 的 skill authoring 思路，验证流程概念上参考了 Anthropic skill creator 的访谈、测试和迭代方法；当前仓库未 vendored 上游文件。
- `.agents/skills/strategy-stress-test/SKILL.md` 概念上参考了用户提供的 [X 链接](https://x.com/cjzafir/status/2052110266566107321) 中关于 confidence calibration / loophole loop 的提示思想，并工程化为“事实可证高置信、默认 1 轮且最多 3 轮、Open Question / Unverified 标记”的 workflow guardrail。当前仓库未 vendored 上游文本。
- `agents/doc-researcher.md`、`agents/web-researcher.md`、`agents/plan-auditor.md`、`.agents/skills/review-pipeline/SKILL.md`、`.agents/skills/github-evidence-triage/SKILL.md` 以及 `implementer` / `git-workflow-and-versioning` / `strategy-stress-test` 的部分边界设计，概念上吸收了用户提供的 oh-my-opencode / oh-my-openagent 角色拆分建议（上游现名 `oh-my-openagent`，曾用名 `oh-my-opencode`；如 Librarian、Metis、Momus、Hephaestus、git-master、review-work、github-triage、hyperplan 的能力边界），但未复制上游文件文本。
- `requirements-grilling` 直接复制/改编 [Matt Pocock 的 skills](https://github.com/mattpocock/skills) 中 `grilling` 与 `domain-modeling` 的核心行为和 `ADR-FORMAT.md` / `CONTEXT-FORMAT.md` 参考格式，按上游 MIT License 保留来源说明，并加上 AILI/OpenSpec 的 `interview.md`、`context.md`、`adr.md`、readiness gate 与无新增 `/grill` 命令约束。其他 workflow 纪律仍仅概念上参考 zoom-out、prototype、to-issues、diagnose、tdd、write-a-skill、improve-codebase-architecture 等方向，未复制上游文本。

## 使用说明

这个仓库面向 OpenCode 使用，核心约定是通过自然语言任务触发 agent 和 skill；同时提供四个可选 delivery slash command 入口：`/ideate`、`/define`、`/build`、`/ship`，分别对应 `commands/{ideate,define,build,ship}.md`，由 `.agents/skills/aili-delivery-flow` 承接。另提供 `/local-review` 作为本地 report-first 审查入口，可审查 local changes、base branch、commit、PR 或 OpenSpec change，并在修复前先输出分类报告；它不覆盖 OpenCode 内置 `/review`，也不替代 `/ship`。`/build` 是批准范围内的自动实现流水线，会把实现结果带过本地 code review、test verification 和必要的 security review；`/ship` 是更完整的 release-readiness 流水线，会复用或刷新 BUILD 证据，对当前变更/最终 diff 或明确指定的 baseline/整库范围执行 release-blocker audit，并补上 closeout、交付/合并/发布风险与后续动作。仓库不提供 `/research`、`/questionnaire`、`/test-plan`、`/implement`、`/fix`、`/debug`、`/review`、`/release-blocker-audit` 或 `/evolve` 等内部阶段命令。

### OpenCode 设置

推荐安装入口是 `rose-aili` Node/TypeScript CLI；Bash 脚本仍保留为兼容 fallback。
安装会把全局通用规则从 `templates/opencode-global-AGENTS.md` 安装到 OpenCode home 的 `AGENTS.md`；项目级事实、命令、测试位置、产物落点和本地例外仍通过各项目自己的瘦 `AGENTS.md` 管理。

安装/更新默认会写入 OpenCode 全局配置目录、共享 `$HOME/.agents/skills`，并 best-effort 检测/补装 DCP 与 OpenSpec；不需要这些全局或项目侧效果时，请使用下方 `--skip-*` 选项。

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

`rose-aili install` 默认复用 `scripts/install_opencode.sh` 的条目级安全安装语义，安装全局 `AGENTS.md`、agents、skills 和 commands；从普通 git clone 安装时使用 selective symlink，从 npm/npx 的 packaged 非 git 目录安装时使用 copy，避免把 OpenCode 链接到临时 package cache。`install` 和 `update` 都会默认检测/补装 DCP 与 OpenSpec，并同步 DCP/OpenCode 推荐配置；显式传 `--skip-dcp`、`--skip-openspec` 或 `--skip-opencode-config` 可关闭对应默认行为。`--enable-dcp` / `--enable-openspec` 保留兼容但不再必要。打包后的 `dist/cli.js` 带 Node shebang 和 executable mode，供 npm/npx 直接执行。OpenCode config 同步默认只在缺失或已为 `rose` 时保持 `default_agent: "rose"`，冲突默认值除非传 `--force-default-agent` 否则保留；模型偏好只在显式传 `--model` 时写入 OpenCode 用户配置，而不是写入 `agents/rose.md`：

交互式 `rose-aili install` 会询问是否启用 Playwright MCP、是否安装 CodeGraph OpenCode 集成；DCP、OpenSpec 和 OpenCode config 同步属于 install/update 默认行为，不再询问 yes/no，只有显式 `--skip-dcp`、`--skip-openspec` / `--skip-opencode-config` 才会关闭。交互式 `rose-aili update` 只询问新增的 CodeGraph 集成，不询问 default agent / model。模型偏好只通过 `--model <provider/model>` 非交互设置，始终写入 OpenCode JSON/JSONC 的 `agent.rose.model`，不会为了用户偏好修改 `agents/rose.md`。

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
npx -y rose-aili install --set-default-rose
npx -y rose-aili install --model anthropic/claude-sonnet-4-5
npx -y rose-aili install --skip-opencode-config
npx -y rose-aili install --enable-playwright
npx -y rose-aili install --skip-dcp
npx -y rose-aili install --enable-codegraph
npx -y rose-aili install --skip-openspec
npx -y rose-aili update --skip-dcp
npx -y rose-aili update --skip-openspec
```

非交互或 `--yes` 模式不会假装已经询问用户问题；输出 summary 会列出跳过/待决定项和精确后续命令。OpenCode config 默认同步会设置/保持 `default_agent: "rose"`（不覆盖冲突的既有默认，除非加 `--force-default-agent`），但不会静默启用 CodeGraph，也不会在未传 `--model` 时静默固定模型。`install` / `update` 会按默认行为检测/补装 DCP 和 OpenSpec；不需要它们时显式加 `--skip-dcp` / `--skip-openspec`。只想默认进入 `rose` 且继续使用 OpenCode 默认模型时，不要传 `--model`。

DCP 在 `install` 和 `update` 中默认启用：安装器会先用 `opencode plugin list` best-effort 检测插件；未检测到或无法确认时才委托执行 `opencode plugin @tarquinen/opencode-dcp@latest --global`，已安装则不重复安装。无论是否需要补装，都会在 `--opencode-home` 指向的目录写入/合并 `dcp.jsonc`/`dcp.json` 推荐配置（包含 `compress.minContextLimit: "65%"`、`compress.maxContextLimit: "85%"`、range compression、turn protection、deduplication 和 purgeErrors）。已有 `dcp.jsonc`/`dcp.json` 的无关键会尽量保留；符号链接或非普通文件会拒绝写入。该命令使用第三方 `@latest` 包，版本可能漂移；失败只会在 summary 中标记 DCP 可选项失败，不会单独把核心全局 `AGENTS.md`/agents/skills/commands 安装判为失败。DCP 只负责 late-stage compression；长任务采用 MiMo-style checkpoint-first，由 ROSE/AILI 在压缩前优先更新 `progress.txt`，并仅在 spec-backed drift/自我纠正、临时决策、取舍、开放问题、未验证假设或需要 DEFINE 回写时更新 `drift-log.md`；旧 `implementation-notes.html` 只作为迁移证据读取，除非当前活动契约明确要求旧 HTML 格式。具体配置见 [`docs/opencode-setup.md`](docs/opencode-setup.md)，重启后可用 `/dcp` 验证配置生效。

CodeGraph 是显式 opt-in：`--enable-codegraph` 会先运行 `npm install -g @colbymchenry/codegraph@latest`，再运行 `codegraph install --target=opencode --yes`，完成后需要重启 OpenCode 让 MCP 集成生效。任一命令失败只会在 summary 中标记 CodeGraph 可选项失败，并给出手动恢复命令，不会单独把核心全局 `AGENTS.md`/agents/skills/commands 安装判为失败。

项目内 CodeGraph 初始化不属于全局安装。AI agent 只能在确认当前仓库根目录后，对该仓库运行 `codegraph init -i` 和 `codegraph status`；不得因为 CodeGraph 初始化顺手运行 `openspec init`，也不得未经明确授权批量初始化多个仓库。

项目级 `AGENTS.md` 初始化 / 更新应联动检查 CodeGraph：生成或更新 `AGENTS.md` 后先运行/请求 `codegraph status`；如果该仓库尚未初始化，则询问用户是否在当前仓库运行 `codegraph init -i`，同意后再运行 `codegraph status`。CodeGraph 不可用、用户跳过或拒绝时，不阻塞 `AGENTS.md` 完成，但必须在结果中说明没有代码地图覆盖。

OpenSpec 在 `install` 和 `update` 中默认启用，除非显式 `--skip-openspec`；`--enable-openspec` 保留兼容但不再必要。OpenSpec 要求 Node.js `20.19.0+`，会先用 `openspec --version` 检测 CLI；未检测到时运行 `npm install -g @fission-ai/openspec@latest`，然后在当前项目中检测既有 OpenSpec 标记；已有项目运行 `openspec update`，首次项目运行 `openspec init`。扩展 workflow 的 `openspec config profile` 仍是手动后续步骤。

安装方式也可采用文档驱动：把 [`docs/opencode-setup.md`](docs/opencode-setup.md) 给 AI agent 看，让它先判断 OpenCode 运行在 WSL/Linux 还是 Windows native，再使用默认的条目级软链接安装。WSL/Linux 可直接调用 `scripts/install_opencode.sh --mode selective` 安装全局 `AGENTS.md`、agents、skills 和 commands。

默认目标是 OpenCode 全局配置目录和共享 skill 目录：agents/commands 安装到 Linux/macOS/WSL 的 `~/.config/opencode/` 或 Windows native 的 `%USERPROFILE%\.config\opencode\`，skills 安装到 `$HOME/.agents/skills/`。安装必须保留全局 `agents/` 和 `commands/` 目录，只在目录内部链接具体 agent 文件和 command 文件；skill 目录链接到共享 `.agents/skills` 位置。项目记忆数据库始终保存在具体项目的 `memory/memory.db`，不会写入全局配置目录。

项目级 `AGENTS.md` 不走软链接。使用 `agents-md-initialization` skill 调用 `scripts/agents_md.py`，从 `templates/AGENTS.md` 生成到目标项目后再填写项目事实，并用 `check --project .` 放进 CI 或 pre-commit 验证。

典型使用方式：

```text
1. 将本仓库作为个人 OpenCode 工作流配置来源。
2. 让 OpenCode 发现 `agents/` 中的自定义 agent。
3. 让 OpenCode 通过安装脚本链接后的共享 `$HOME/.agents/skills/` 发现本仓库 `.agents/skills/` 中的 SKILL.md 工作流。
4. 可选使用全局 `~/.config/opencode/commands/` 中的 `/ideate`、`/define`、`/build`、`/ship` 入口。
5. 由 `rose.md` 作为 primary agent，按任务需要调用对应 skills 和 subagents。
```

新增、删除或重命名 skill 或 command 后，重新运行 `scripts/install_opencode.sh --mode selective`，然后重启 OpenCode 或开启新 session，确保 discovery 刷新。

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
| Superpowers | [obra/superpowers](https://github.com/obra/superpowers) | MIT License | Copyright (c) 2025 Jesse Vincent |
| Bytedance / DeerFlow Authors | [bytedance/deer-flow](https://github.com/bytedance/deer-flow) | MIT License；clean-room pattern absorption only in this repository | Copyright Bytedance Ltd. and/or its affiliates and DeerFlow Authors; no DeerFlow runtime, provider config, tool paths, branding text, or upstream skill正文 vendored |
| affaan-m / ECC contributors | [affaan-m/ECC](https://github.com/affaan-m/ECC) | MIT License | Copyright (c) 2026 Affaan Mustafa；local-review references adapt ECC review/orchestration/build-fix patterns with provenance; no ECC runtime, tool config, public ECC command, or upstream prompt正文 vendored |
| sanyuan0704 | [sanyuan-skills](https://github.com/sanyuan0704/sanyuan-skills/tree/main/skills/code-review-expert) | 未验证；pattern-only reference；no copied text | Review-quality rubric patterns only; no upstream skill正文 vendored |
| Alireza Rezvani | [claude-skills](https://alirezarezvani.github.io/claude-skills/skills/engineering-team/code-reviewer/) | 未验证；pattern-only reference；no copied text | Review-quality and fixture/golden-output patterns only; no upstream skill正文 vendored |
| laolaoshiren | [claude-code-skills-zh](https://github.com/laolaoshiren/claude-code-skills-zh/tree/main/skills/zh-code-reviewer) | 未验证；pattern-only reference；no copied text | Chinese review-output profile patterns only; no upstream skill正文 vendored |
| Matt Pocock | [mattpocock/skills](https://github.com/mattpocock/skills) | MIT License | `requirements-grilling` 复制/改编 `grilling`、`domain-modeling` 核心行为和 `ADR-FORMAT.md` / `CONTEXT-FORMAT.md` 参考格式；Copyright (c) 2026 Matt Pocock |
| Amanda Askell | [askell.io](https://askell.io/) | 概念性参考；未纳入上游文本 | allegory / analogy prompting 方向参考 |
| Vaibhav / VB / Codex-style prompting | 用户提供的概念方向 | 概念性参考；未纳入上游文本 | evidence-scoped self-improvement prompting 方向参考；本仓库不声称可见全局历史 |
| Andrej Karpathy | [X post](https://x.com/karpathy/status/2015883857489522876) | 思想来源 | agent coding guardrail 方向参考 |
| Mnilax | [X post](https://x.com/Mnilax/status/2053116311132155938) | 用户提供的概念来源；direct X content 未验证 | coding-agent discipline / retrospective taxonomy 方向参考；未复制原文 |
| cjzafir | [X post](https://x.com/cjzafir/status/2052110266566107321) | 思想来源 | confidence calibration / loophole loop 方向参考；未 vendored 上游文本 |
| code-yeongyu | [oh-my-openagent](https://github.com/code-yeongyu/oh-my-openagent)（曾用名 `oh-my-opencode`） | 概念性参考；未纳入上游文件 | agent / skill 角色边界与工作流拆分方向参考，如 Librarian、Metis、Momus、Hephaestus、git-master、review-work、github-triage、hyperplan |
| Forrest Chang / Andrej Karpathy skills | [forrestchang/andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills) | 概念性参考；未纳入上游文件 | 如后续复制上游文本或文件，需先确认并保留对应版权/许可 |

如果继续从上游同步 agent 或 skill，请同步更新本 README 的来源表和许可说明。
