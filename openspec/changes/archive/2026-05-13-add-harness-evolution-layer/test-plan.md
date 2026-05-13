# 测试文档：add-harness-evolution-layer / add-aili-delivery-harness umbrella

## 0. 文档元信息

- 来源：`docs/research/agent-harness/**`、用户填写的 Q1-Q8 决策、`openspec/changes/add-harness-evolution-layer/**`
- 生成时间：2026-05-11
- 适用版本 / 分支：`docs/testing-lifecycle-gate`
- 测试负责人：ROSE / subagents / user review
- 状态：completed; final static verification and memory writeback passed

## 1. 资料来源与证据

| 来源 | 已检查内容 | 观察到的事实 | 置信度 | 备注 |
|---|---|---|---|---|
| `docs/research/agent-harness/command-lifecycle.md` | command lifecycle gates | 顶层入口限定为 `/ideate`、`/define`、`/build`、`/ship`；OpenSpec 是 backend adapter；define 首轮需 spec + questionnaire + test document | high | 用于验证 commands 与 delivery flow |
| `docs/research/agent-harness/project-upgrade-inspirations.md` | harness 工程系统建议 | 推荐可观察、可评估、可回滚、可演化的 harness contract、subagent evidence schema、fixtures | high | 用于验证 docs/harness、protocols、fixtures |
| `docs/research/agent-harness/ahe-lite-transformation-plan.md` | AHE-lite minimum deliverable | 推荐 `harness-evolution` skill、component map、activation matrix、change report template、fixtures；首阶段不改 SQLite schema | high | 用于验证治理 skill 和非目标 |
| 用户填写内容 | Q1-Q8 / umbrella scope | 用户确认本次做架构落位：`rose.md` 分割、四 commands、核心 skills、docs/harness、protocols、fixtures、安装脚本接入 | high | 同时确认不做 SQLite schema、新依赖、自动 self-evolution、批量 subagent rewrite |
| `proposal.md` | What/why/scope | 本 change 语义扩展为 `add-aili-delivery-harness` umbrella，但暂不移动目录 | high | OpenSpec proposal source |
| `design.md` | Technical design | 定义 Runtime Charter、commands、delivery flow、harness evolution、docs/protocols、runner、install 接入 | high | Design source |
| `specs/aili-delivery-harness/spec.md` | Requirements/scenarios | 定义 runtime charter、commands、delivery flow、backend adapter、protocols、docs、install、runner | high | New umbrella spec |
| `specs/harness-evolution/spec.md` | Requirements/scenarios | 定义 report gate、component map、activation matrix、change report、subagent evidence、fixtures、approval、memory | high | Governance spec |
| `questionnaire.md` | Decisions | Q1-Q8 已吸收，剩余 Open Question 仅为是否重命名 change 目录 | high | Build scope source |

## 2. 被测对象与测试目标

- 被测对象：OpenSpec change `add-harness-evolution-layer` 及后续架构落位 artifacts。
- 用户目标：一次性搭起 AILI delivery harness 首版架构，但保持受控边界和可验证增量。
- 业务目标：降低 harness 规则膨胀和入口漂移，使未来 agent workflow 可观察、可评估、可回滚、可演化。
- 技术目标：确认 OpenSpec artifacts、commands、skills、docs/harness、protocols、fixtures、install script、Runtime Charter 与验收边界一致。
- 不测试内容：不测试 SQLite schema migration；不执行 LLM benchmark；不验证多 host 安装兼容；不测试生产部署；不自动 commit/push。

## 3. 测试范围

### In Scope

- OpenSpec artifact 完整性：proposal、design、tasks、questionnaire、test-plan、`specs/aili-delivery-harness/spec.md`、`specs/harness-evolution/spec.md`。
- Commands：仅创建 `/ideate`、`/define`、`/build`、`/ship` 四个入口。
- Skills：`aili-delivery-flow` 与 `harness-evolution` 结构、触发、stop conditions、references。
- Docs/protocols：`docs/harness/**`、`protocols/**`、`workflow.components.yaml` 的存在性、权威边界和避免重复复制。
- Install：`scripts/install_opencode.sh`、`docs/opencode-setup.md`、`README.md` 包含 commands 安装/使用说明。
- Runtime Charter：`agents/rose.md` 分割后保留安全、权限、git、memory、subagent、verification 等核心边界。
- Fixtures/runner：`docs/harness/fixtures/*.yaml` 与 `scripts/harness_fixture_check.py` 零依赖静态验证。

### Out of Scope

- SQLite schema、raw SQLite writes、memory sidecar。
- 第三方依赖、lockfile、package manager install。
- 自动 self-evolution、自动 benchmark runner、外部 LLM eval。
- 批量重写所有 subagent。
- 自动 commit、push、merge、archive。

### Assumptions

- 当前 implementation 可在现有 branch/workspace 中进行，但不得触碰 unrelated `.gitignore` 或 `.opencode/` dirt。
- `commands/` 当前不存在，因此会新建目录和四个 command 文件。
- Python 标准库可用于 fixture runner。

### Open Questions

- Open Question: 是否把 OpenSpec change 目录重命名为 `add-aili-delivery-harness`。当前不执行 rename/move。

## 4. 需求-测试追踪矩阵

| 需求 / 决策 / 风险 | 来源 | 测试点 | 测试类型 | 优先级 | 覆盖状态 |
|---|---|---|---|---|---|
| Runtime charter split | `specs/aili-delivery-harness/spec.md` | `agents/rose.md` 保留 runtime authority，流程细节下沉并短引用 | Review / grep | P0 | pass: fourth package |
| Four top-level commands | spec/design | 只存在 `commands/ideate.md`, `define.md`, `build.md`, `ship.md`；无内部阶段 command | Structure check | P0 | pass: second package |
| Delivery flow skill | spec/design | `skills/aili-delivery-flow/SKILL.md` 和 references 存在，DEFINE stop、BUILD approval gate 明确 | Document review | P0 | pass: second package |
| Backend adapters preserve gates | spec/design | OpenSpec/Superpowers/custom/auto 只是 backend，不绕过 lifecycle gates | Document review | P0 | pass: first/final package |
| Protocol templates | spec/design | `protocols/*.md` 覆盖 10 个模板，subagent packet/result 权威位置明确 | Structure review | P1 | pass: first package |
| Harness docs | spec/design | `docs/harness/*.md` 覆盖 contract/map/matrix/backend/lifecycle/taxonomy/policies/report/fixtures | Structure review | P0 | pass: first package |
| Commands install path | spec/design | install script/docs/README 处理 commands | Script/doc review | P0 | pass: third package |
| Static fixture runner | spec/design | `python scripts/harness_fixture_check.py` pass；无第三方依赖 | CLI | P0 | pass: final runner, 5 fixture files |
| Harness evolution report gate | `specs/harness-evolution/spec.md` | `harness-evolution` 默认 report-first，缺 approval 不 silent apply | Review / fixture | P0 | pass: second package |
| Explicit approval policy | user answers/spec | 缺明确批准时只能停在 report/proposal | Review / fixture | P0 | pass: second/fourth package |
| No SQLite schema/new deps/auto commit | user answers/spec/tasks | diff/status 检查无 schema/lockfile/deps/git automation | Diff review | P0 | pass: final scoped diff/status |

## 5. 测试策略

- 单元测试：本次主要是 harness 文档/脚本；runner 可通过 CLI smoke 覆盖。
- 集成测试：OpenSpec status/strict validation；fixture runner；install script dry-read/structure review。
- API / 契约测试：OpenSpec requirement/scenario 格式；protocol templates 必填字段。
- 手工验收：审查 `rose.md` Runtime Charter 是否保留必要边界，且长流程未复制回多个入口。
- 回归测试：fixtures 覆盖 command routing、skill routing、subagent dispatch、verification claim、AGENTS/template smoke。
- 非功能测试：确认无新依赖、无 SQLite schema、无自动 commit/push、无 raw log memory 设计。

## 6. 测试环境与测试数据

- 环境：本地仓库 `/mnt/d/works/aili-workflow`。
- 依赖服务：无。
- 测试账号 / 权限：无。
- 测试数据：OpenSpec change files、research docs、fixtures YAML/Markdown、scripts。
- 数据清理方式：不创建运行时数据；不写 memory schema；仅通过 `rose-memory` CLI 写 task receipt。

## 7. 功能测试用例

| ID | 场景 | 前置条件 | 步骤 | 预期结果 | 优先级 | 自动化建议 | 来源 |
|---|---|---|---|---|---|---|---|
| TC-DH-001 | OpenSpec artifacts 完整 | change 已更新 | 运行 `openspec status --change "add-harness-evolution-layer"` | proposal/design/specs/tasks apply-ready | P0 | CLI | OpenSpec |
| TC-DH-002 | OpenSpec strict valid | artifacts 完整 | 运行 `openspec validate "add-harness-evolution-layer" --strict` | validation pass | P0 | CLI | OpenSpec |
| TC-DH-003 | Four command surface | implementation 完成 | 检查 `commands/*.md` | 仅四个入口存在且分别路由到 IDEATE/DEFINE/BUILD/SHIP | P0 | script/manual | command lifecycle |
| TC-DH-004 | Delivery flow references | implementation 完成 | 检查 `skills/aili-delivery-flow/references/*.md` | 7 个 references 存在且含 stop conditions/adapter rules | P0 | manual | design |
| TC-DH-005 | Harness evolution report-first | implementation 完成 | 检查 `skills/harness-evolution/SKILL.md` | 默认报告，不默认改文件；approval policy 明确 | P0 | manual/fixture | AHE-lite |
| TC-DH-006 | Protocol templates | implementation 完成 | 检查 `protocols/*.md` | 10 个模板存在，subagent task/result 字段明确 | P1 | manual | user answer |
| TC-DH-007 | Fixture runner | fixtures 存在 | 运行 `python scripts/harness_fixture_check.py` | pass；缺必填字段时应 fail | P0 | CLI | user answer |
| TC-DH-008 | Install commands support | script/docs 更新 | 审查 `scripts/install_opencode.sh` 与 docs | commands 安装路径被处理且无新依赖 | P0 | manual/shell dry review | user answer |
| TC-DH-009 | Runtime Charter retained gates | `rose.md` 已分割 | 审查关键 heading/规则 | 安全、权限、git、memory、subagent、verification 边界未丢 | P0 | manual/grep | user answer |

## 8. 异常、边界与权限测试

| ID | 类型 | 场景 | 输入 / 操作 | 预期结果 | 风险 |
|---|---|---|---|---|---|
| NEG-DH-001 | Command surface | 提议新增 `/review` 或 `/evolve` | 检查 `commands/` | 不创建内部阶段 command | 中：gate 绕过 |
| NEG-DH-002 | Prompt bloat | 大段流程复制回 `agents/rose.md` | review `agents/rose.md` | 要求迁回 skill/docs/protocols | 高：维护漂移 |
| NEG-DH-003 | Dependency | runner 引入 PyYAML 或其他依赖 | diff/status | 拒绝；使用标准库 | 高：scope creep |
| NEG-DH-004 | SQLite | 修改 memory schema 或直接写 SQLite | diff/status | 拒绝；另开 change | 高：数据风险 |
| NEG-DH-005 | Silent apply | 缺 approval 仍修改 core harness | review tasks/report | 标为 violation；必须有用户批准 | 高：治理失败 |
| NEG-DH-006 | Subagent blast radius | 批量重写所有 subagent | scoped diff | 拒绝；只改 shared guidance/必要短引用 | 高：回归风险 |

## 9. 数据一致性 / 迁移 / 兼容性测试

- 检查本 change 不修改 `memory/memory.db` schema。
- 检查不新增 dependencies/lockfiles/package manager artifacts。
- 检查 `workflow.components.yaml` 与 docs/protocol/skills/commands 路径一致。
- 检查 `commands/` 安装说明与实际 `scripts/install_opencode.sh` 逻辑一致。

## 10. 性能、稳定性、安全、可观测性测试

- 性能：不适用；无 runtime hot path。
- 稳定性：activation matrix 和 fixtures 防止 gate 过触发/漏触发。
- 安全：不得记录 secrets/raw logs；不得绕过 approval gate；不得自动 push/commit。
- 可观测性：harness change report、closeout protocol、test-plan execution record 必须保留 evidence pointers。

## 11. 回归范围

- Command routing fixture：四命令与内部阶段 non-trigger。
- Skill routing fixture：`aili-delivery-flow` / `harness-evolution` trigger 与 non-trigger。
- Subagent dispatch fixture：packet/result 包含 trace、coverage、unknowns、failure signal。
- Verification claim fixture：完成声明必须有 fresh evidence 或标为 `Unverified`。
- AGENTS/template smoke：OpenSpec test-plan placement 与 non-OpenSpec placement decision。

## 12. 自动化验证命令

| 层级 | 命令 | 目的 | 必须执行 | 备注 |
|---|---|---|---|---|
| OpenSpec status | `openspec status --change "add-harness-evolution-layer"` | 检查 artifact graph 是否 apply-ready | yes | OpenSpec 更新后执行 |
| OpenSpec strict validation | `openspec validate "add-harness-evolution-layer" --strict` | 检查 OpenSpec 格式和 spec scenario 结构 | yes | OpenSpec 更新后执行 |
| Fixture runner | `python scripts/harness_fixture_check.py` | 检查 fixture required coverage | yes | runner 创建后执行 |
| Scoped status | `git status --short -- commands skills docs protocols scripts README.md agents/rose.md templates/AGENTS.md openspec/changes/add-harness-evolution-layer workflow.components.yaml` | 检查变更范围与异常文件 | yes | 最终执行 |
| Dependency/schema check | `git diff --name-only` plus targeted diff review | 确认无 lockfile/dependency/SQLite schema/auto git 行为 | yes | 最终执行 |

## 13. 手工验收清单

- [x] `proposal.md` / `design.md` 已反映 umbrella scope 与 non-goals。
- [x] `specs/aili-delivery-harness/spec.md` 与 `specs/harness-evolution/spec.md` strict validation 通过。
- [x] `commands/ideate.md`、`define.md`、`build.md`、`ship.md` 存在且薄入口。
- [x] `skills/aili-delivery-flow/**` 与 `skills/harness-evolution/**` 存在且 details 在 references。
- [x] `docs/harness/**` 与 `protocols/**` 存在，且定义唯一权威边界。
- [x] `scripts/harness_fixture_check.py` 通过。
- [x] `scripts/install_opencode.sh`、`docs/opencode-setup.md`、`README.md` 支持 commands。
- [x] `agents/rose.md` 已瘦身成 Runtime Charter，安全/memory/git/verification/subagent gate 未丢失。
- [x] 无 SQLite schema、第三方依赖、lockfile、自动 commit/push 行为。

## 14. Open Questions / Unverified

| 类型 | 内容 | 影响 | 处理方式 |
|---|---|---|---|
| Open Question | 是否将 OpenSpec change 目录重命名为 `add-aili-delivery-harness` | 影响路径和历史 traceability | 当前不移动；如用户批准再执行 rename |
| Unverified | 实际执行 `scripts/install_opencode.sh` 安装流程 | installer 没有安全 dry-run，执行会调用 `ensure_repo` 并可能 `git pull` / `git clone` 或写入全局 OpenCode 目录 | 已验证 `bash -n`、结构、文档和 command 文件；不把实际安装作为本次完成证据 |

## 15. 测试执行记录

| Run ID | 时间 | 执行者 | 测试层级 | 命令 / 工具 | 结果 | 关键证据 | 未验证项 |
|---|---|---|---|---|---|---|---|
| RUN-20260511-001 | 2026-05-11 | ROSE | OpenSpec status | `openspec status --change "add-harness-evolution-layer"` | pass | `Progress: 4/4 artifacts complete`; proposal/design/specs/tasks all checked | superseded by expanded scope; rerun required |
| RUN-20260511-002 | 2026-05-11 | ROSE | OpenSpec strict validation | `openspec validate "add-harness-evolution-layer" --strict` | pass | `Change 'add-harness-evolution-layer' is valid` | superseded by expanded scope; rerun required |
| RUN-20260511-003 | 2026-05-11 | ROSE | Manual artifact review | read proposal/design/spec/tasks/questionnaire/test-plan | pass | Required artifacts exist; spec scenarios use `####`; tasks start with questionnaire/approval gates | superseded by expanded scope; rerun required |
| RUN-20260511-004 | 2026-05-11 | ROSE | Scoped status review | `git status --short -- "openspec/changes/add-harness-evolution-layer"` | pass | Only the approved change directory is untracked in scoped status | unrelated pre-existing workspace dirt remains outside this path |
| RUN-20260511-005 | 2026-05-11 | `plan-auditor` | Read-only package audit | source docs + OpenSpec package audit | pass | `STATUS: PASS`; safe to hand off as source-grounded, gated OpenSpec change package | superseded by expanded scope; new audit/validation may be needed |
| RUN-20260511-006 | 2026-05-11 | ROSE | OpenSpec status / validation | `openspec status --change "add-harness-evolution-layer" && openspec validate "add-harness-evolution-layer" --strict` | pass | `Progress: 4/4 artifacts complete`; `Change 'add-harness-evolution-layer' is valid` | implementation artifacts still in progress |
| RUN-20260511-007 | 2026-05-11 | ROSE | Fixture runner | `python scripts/harness_fixture_check.py` | pass | `harness fixture check: PASS (4 fixture files)` | validates static fixture coverage only |
| RUN-20260511-008 | 2026-05-11 | ROSE | First package scoped status | `git status --short -- "docs/harness" "protocols" "workflow.components.yaml" "scripts/harness_fixture_check.py" "openspec/changes/add-harness-evolution-layer/tasks.md"` | pass | Scoped status shows only first-package paths plus tasks file | unrelated workspace dirt remains outside this scope |
| RUN-20260511-009 | 2026-05-11 | ROSE | Skills/commands package | `python scripts/harness_fixture_check.py`; Python command-file structure check; `openspec validate "add-harness-evolution-layer" --strict` | pass | exactly `build.md`, `define.md`, `ideate.md`, `ship.md`; no forbidden internal-stage commands; strict validation pass | install docs/script and Runtime Charter still pending |
| RUN-20260511-010 | 2026-05-11 | ROSE | Install/docs package | `bash -n scripts/install_opencode.sh`; `python scripts/harness_fixture_check.py`; command structure check; `openspec validate "add-harness-evolution-layer" --strict` | pass | shell syntax clean; docs mention four command entrypoints; installer handles `commands/`; strict validation pass | no actual install run; installer has no safe dry-run and would call `ensure_repo` |
| RUN-20260511-011 | 2026-05-11 | ROSE | Runtime Charter/shared guidance package | `python scripts/harness_fixture_check.py`; Python runtime/package structure check; `bash -n scripts/install_opencode.sh`; `openspec validate "add-harness-evolution-layer" --strict`; scoped status for package 5 paths | pass | `agents/rose.md` is 140 lines and contains lifecycle, harness-evolution, memory, verification, command, git/safety/secret references; shared skills/templates point to lifecycle/protocols without copying full flow; strict validation pass | broader final diff/status review still pending |
| RUN-20260511-012 | 2026-05-11 | ROSE | Review fix + final static verification | `python scripts/harness_fixture_check.py`; Python final structure check; `bash -n scripts/install_opencode.sh`; `openspec status --change "add-harness-evolution-layer"`; `openspec validate "add-harness-evolution-layer" --strict`; dependency/schema diff; scoped status | pass | fixture runner reports `PASS (5 fixture files)` including AGENTS/template smoke; final structure check pass; OpenSpec progress `4/4`; strict validation valid; dependency/schema diff empty; scoped status excludes unrelated `.opencode/` | actual installer execution remains unverified by design |
| RUN-20260511-013 | 2026-05-11 | ROSE | Memory writeback | `rose-memory checkpoint` / `rose-memory complete` via bundled CLI fallback | pass | checkpoint receipt `wr_20260511T154509Z_1a4a0f10`; completion receipt `wr_20260511T154509Z_49599fc3`; `--no-durable-memory-promoted` | none |

## 16. 缺陷与修复闭环

| Bug ID | 来源测试 | 现象 | 根因 | 修复负责人 | 修复文件 | 复测命令 | 复测结果 | 状态 |
|---|---|---|---|---|---|---|---|---|
| BUG-DH-001 | review-pipeline / fixture coverage | `specs/harness-evolution/spec.md` 要求 AGENTS/template smoke fixture，但 runner 只验证 4 个 fixtures | fixture coverage 漏项 | ROSE | `scripts/harness_fixture_check.py`, `docs/harness/fixtures/agents-template-fixtures.yaml` | `python scripts/harness_fixture_check.py` | pass: `PASS (5 fixture files)` | closed |
| BUG-DH-002 | security-auditor / Runtime Charter | `agents/rose.md` 默认 permission 为 `"*": allow`，High-Risk Gate 未显式命名 | Runtime Charter fail-open 默认过宽 | ROSE | `agents/rose.md` | Python final structure check | pass: contains `"*": ask` and `High-Risk Gate` | closed |
| BUG-DH-003 | test-engineer / closure evidence | final no-deps/schema evidence和 7.4/7.5 closure 尚未记录 | final evidence ledger 未更新 | ROSE | `test-plan.md`, `tasks.md` | dependency/schema diff + scoped status | pass: targeted dependency/schema diff empty; scoped status limited to task paths | closed |

## 17. 变更记录

- 2026-05-11: 初版测试文档，基于 OpenSpec proposal/design/spec/questionnaire 草案生成。
- 2026-05-11: 根据用户填写的 Q1-Q8 决策扩展为 `add-aili-delivery-harness` umbrella scope，更新测试范围、追踪矩阵、验收标准与待执行验证。
- 2026-05-11: 首个实现包完成并验证：`docs/harness/**`、`protocols/**`、`workflow.components.yaml`、fixtures 和 `scripts/harness_fixture_check.py`。
- 2026-05-11: 第二个实现包完成并验证：`skills/aili-delivery-flow/**`、`skills/harness-evolution/**` 和四个 thin `commands/*.md`。
- 2026-05-11: 第三个实现包完成并验证：`scripts/install_opencode.sh`、`docs/opencode-setup.md`、`README.md` 已接入 commands 安装/说明。
- 2026-05-11: 第四个实现包完成并验证：`agents/rose.md` 已瘦身为 Runtime Charter，shared guidance 仅保留短引用，OpenSpec strict validation 通过。
- 2026-05-11: review-pipeline 阻塞项已修复并完成最终静态验证：新增 AGENTS/template smoke fixture，Runner 覆盖 5 个 fixture 文件，Runtime Charter 默认权限改为 ask，OpenSpec strict validation 通过，dependency/schema diff 为空。
- 2026-05-11: 完成 memory writeback：checkpoint `wr_20260511T154509Z_1a4a0f10`，completion `wr_20260511T154509Z_49599fc3`，未提升 durable memory。
