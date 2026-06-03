## Context

本变更原始目标是 `harness-evolution` AHE-lite 治理层。用户填写问卷后，明确将本次范围扩展为一次架构首版落位：可以一次性搭起 `rose.md` 分割、四个命令入口、核心 skills、harness 文档、协议模板、fixtures、安装脚本接入；但不同时做 SQLite schema、自动 benchmark、完整 self-evolution、批量重写所有 subagent 或新增依赖。

因此本 OpenSpec change 保持现有目录 `add-harness-evolution-layer`，但语义上作为 `add-aili-delivery-harness` umbrella 变更执行。若后续需要把目录重命名为 `add-aili-delivery-harness`，需单独获得用户对 rename/move 的明确批准。

## Goals / Non-Goals

Goals:

- 将 `agents/rose.md` 改为 Runtime Charter，保留运行期最小权威，避免继续堆叠完整流程细节。
- 新增四个顶层 OpenCode commands：`/ideate`、`/define`、`/build`、`/ship`。
- 新增 `aili-delivery-flow` skill，作为 IDEATE/DEFINE/BUILD/SHIP 状态机与 backend adapter 的唯一流程权威。
- 新增 `harness-evolution` skill，作为 no-naked-harness-edits 的治理入口，而不是用户常用顶层 `/evolve` 命令。
- 新增 `docs/harness/**` 和 `protocols/**`，把 lifecycle、backend、protocol、subagent evidence、verification、memory、harness change 等规则显式化为可审查文件。
- 新增静态 fixtures 与零依赖 smoke runner，覆盖 command routing、skill routing、subagent dispatch、verification claim 等 harness 行为。
- 更新安装脚本和 OpenCode 文档，使 `commands/*.md` 能随 agents/skills 一起安装。

Non-Goals:

- 不修改 `rose-memory` SQLite schema；如需结构化 harness ledger，另开 OpenSpec change。
- 不做自动 benchmark evolution farm、LLM eval farm 或多 host 全兼容安装器。
- 不允许 agent 自主修改核心 harness 后自动 commit/push。
- 不批量重写所有 subagent；首阶段只改共享 guidance 或少数必要触发短引用。
- 不新增第三方依赖、不修改 lockfile、不改变生产部署行为或公共 API。
- 不暴露内部阶段命令：`/research`、`/questionnaire`、`/test-plan`、`/implement`、`/fix`、`/debug`、`/review`、`/evolve`。

## Decisions

### 1. `agents/rose.md` 变成 Runtime Charter

- Decision: `agents/rose.md` 只保留 ROSE 身份和最终责任、指令优先级、权限/secret/High-Risk Gate/git 边界、IDEATE/DEFINE/BUILD/SHIP 主流程绑定、subagent 编排原则、memory 边界、完成声明 gate、harness evolution gate 与最小 router。
- Rationale: 当前 ROSE 已是集中式 harness 控制面；继续追加流程会扩大漂移风险。Runtime Charter + skill/docs/protocols 分层更可回滚、可审查。
- Boundaries: 不把完整 lifecycle、test lifecycle、memory CLI 细节、subagent packet schema 或 review-fix loop 复制回 `rose.md`。

### 2. 顶层命令只做四个入口

- Decision: 新增 `commands/ideate.md`、`commands/define.md`、`commands/build.md`、`commands/ship.md`。
- Rationale: 四个命令与研究文档中的 command lifecycle 一致；内部阶段留给 `aili-delivery-flow`、skills 和 subagents，避免用户绕过 gate。
- Command semantics:
  - `/ideate`: 想法未确定，只头脑风暴、对比方案、识别不确定点；不得写生产代码。
  - `/define`: 想法基本确定，调研 docs/code/spec，输出 spec、questionnaire、test document 草案并复核；不得实现。
  - `/build`: 用户确认 spec/questionnaire/test document 后，拆 implementation packages，由 implementer/test-engineer/debug-investigator 协作。
  - `/ship`: 实施完成后运行 review-pipeline、repair loop、final verification、archive/sync/memory closeout。

### 3. `aili-delivery-flow` 是 lifecycle 唯一权威

- Decision: 新增 `skills/aili-delivery-flow/SKILL.md` 与 references：`lifecycle.md`、`backend-routing.md`、`artifact-contracts.md`、`questionnaire-policy.md`、`test-document-policy.md`、`implementation-packages.md`、`review-repair-loop.md`。
- Rationale: commands 只触发模式，复杂状态机放入 skill/references，未来改流程不需要改 `rose.md` 或重复改多个入口。
- Backend model: OpenSpec、Superpowers-style plan、自定义文件和 auto detection 都是 backend adapter；lifecycle gates 不随 backend 改变。

### 4. `harness-evolution` 是治理 skill，不是主流程

- Decision: 新增 `skills/harness-evolution/SKILL.md` 与 references：`activation-matrix.md`、`component-taxonomy.md`、`change-report-template.md`、`approval-policy.md`、`verdict-policy.md`。
- Rationale: AHE-lite 的价值是 component/experience/decision observability 与可验证演化，而不是 prompt-only 增强或自动改写。
- Trigger: 用户要求改 workflow/ROSE/skill/command/subagent、同类 workflow failure 重复、subagent 调度错位、verification claim 失败、memory writeback/retrieval 失败、command lifecycle 被绕过、用户指出流程跑偏。

### 5. `docs/harness/**` 和 `protocols/**` 是可观察架构面

- Decision: 新增 harness contract、component map、activation matrix、backend adapters、command lifecycle、failure taxonomy、tool policies、harness change report template、fixtures，以及 protocol templates。
- Rationale: 当前缺口是 harness contract、run observability、eval/regression、change manifest，而不是更多 persona 或更长主控 prompt。
- Authority rule: lifecycle 权威在 `skills/aili-delivery-flow/references/lifecycle.md`；backend 权威在 `backend-routing.md`；harness change 权威在 `skills/harness-evolution/references/change-report-template.md`；subagent packet/result 权威在 `protocols/`；memory 权威仍是 `rose-memory`。

### 6. Fixture runner 零依赖、静态 smoke validation

- Decision: 新增 `scripts/harness_fixture_check.py`，只使用 Python 标准库，对 YAML/Markdown fixture 做必填字段和 smoke validation。
- Rationale: 用户确认需要 runner，但要求不做 LLM eval、benchmark 或新增依赖。
- Boundary: runner 不调用外部服务、不模拟完整 agent，只检查 fixture schema 与关键文本约束。

### 7. 安装脚本必须接入 commands

- Decision: 更新 `scripts/install_opencode.sh` 和 `docs/opencode-setup.md`，把 `$AILI_HOME/commands/*.md` 安装到 `$OPENCODE_HOME/commands/*.md`，与 agents/skills 保持一致。
- Rationale: 如果只新增 command 文件但安装脚本不处理，实际 OpenCode 入口会与文档漂移。

## Risks / Trade-offs

- [多入口重复定义流程] → `rose.md`、commands、README、AGENTS 只短引用权威文件，不复制流程全文。
- [改动面较大] → 分工作包实施：OpenSpec 更新 → docs/protocols skeleton → skills/commands → install/runner → ROSE 瘦身 → shared guidance touchpoints → verification。
- [Runtime Charter 过度瘦身导致规则丢失] → 先保留安全、权限、git、memory、verification、subagent 边界；下沉内容必须有明确目标文件。
- [Fixture runner 变成 benchmark] → runner 只做标准库静态检查。
- [Subagent contract 一次性扩散] → 只改 shared guidance 和必要模板，不批量改全部 subagent。
- [SQLite ledger 诱惑] → 本 change 明确不改 schema；只用 Markdown report、OpenSpec/test-plan 记录和现有 `rose-memory` receipts。

## Migration Plan

1. 将用户 Q1-Q8 决策写回 proposal/design/spec/tasks/questionnaire/test-plan，并重新运行 OpenSpec validation。
2. 派发实现 subagent 执行第一个工作包：创建 `docs/harness/**`、`protocols/**`、`workflow.components.yaml` 和 fixture/runner skeleton。
3. 继续第二工作包：创建 `aili-delivery-flow`、`harness-evolution` skills 和四个 commands。
4. 继续第三工作包：更新安装脚本、README、OpenCode setup 和必要 shared guidance。
5. 最后瘦身 `agents/rose.md` 为 Runtime Charter，确认关键安全/memory/git/verification/subagent 边界未丢失。
6. 运行 `scripts/harness_fixture_check.py`、OpenSpec strict validation、结构/安装脚本 smoke review、scoped status/diff，并把结果写回 `test-plan.md`。

## Open Questions

- Open Question: 是否把 OpenSpec change 目录从 `add-harness-evolution-layer` 重命名为 `add-aili-delivery-harness`。当前未执行 rename/move，避免在未单独批准时移动已创建文件。
