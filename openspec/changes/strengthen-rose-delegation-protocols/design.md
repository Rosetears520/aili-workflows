## Context

当前仓库已经有若干相关但分散的约束：`agents/rose.md` 说明 ROSE 负责 orchestration/final acceptance，并已有 Cost-Aware Subagent Routing、Context Evidence Gate 和“subagent output is evidence, not truth”的规则；`skills/parallel-subagent-dispatch/SKILL.md` 已经支持 context-saving dispatch；`agents/code-scout.md` 已要求只读定位证据并返回 compact anchors。

缺口在于这些规则还没有形成一个清晰、可执行、可测试的 follow-up 合约：

- 直接执行边界还不够具体，容易把“单文件”误解为“可直接改”。
- context-saving dispatch 仍像偏好而非强制门禁。
- repo evidence 规则嵌在 ROSE/template 中，没有独立中文技能可路由。
- code-scout 已能定位 evidence，但没有明确产出 upstream/downstream/peer/test/freshness 的 locality map。
- 当前没有 dedicated `session-handoff` 技能。
- subagent task/result 协议需要更明确地区分 facts、inferences、recommendations。

另有一个重要约束：原 active OpenSpec change `add-harness-evolution-layer` 覆盖过 delivery harness 与 harness evolution 的大框架，并使用过顶层 `protocols/**` 作为协议表面。BUILD 前 reconciliation 发现该 change 的任务勾选与当前工作树文件存在 stale/missing 冲突；用户确认先归档/修复旧 change，最终将其移动到 `openspec/changes/archive/2026-05-13-add-harness-evolution-layer/` 且不把旧 delta specs 同步为当前 main specs。本 change 现在作为当前 BUILD 权威，协议权威路径仍固定为 `skills/aili-delivery-flow/references/protocols/`。

## Goals / Non-Goals

**Goals:**

- 明确 ROSE 直接执行 allowlist：只允许 exact、low-risk、local、locally verifiable 的小改。
- 把 context-saving read-only scout 从“推荐”提升为“满足触发条件时必须派发”。
- 将 `code-scout` 定义为 code locality mapping agent，而不是普通 grep worker。
- 新增中文 `repo-evidence-first` skill 合约，要求没有证据锚点就不得声称项目事实。
- 新增 `session-handoff` skill 合约，支持用户明确要求时为长会话、压缩前、BLOCKED/IDLE 和切换 session 生成交接文档。
- 将 subagent task packet/result 协议升级为 evidence-first、facts/inferences/recommendations 分离的结构。
- 保持 `agents/rose.md` 短 router 化：只增加最小路由提示，不复制长规则。

**Non-Goals:**

- 不在未批准状态下直接修改核心 harness 文件；本 BUILD 已获用户批准修改 `agents/rose.md`、skills 和 canonical protocol references。
- 不新增 `/research`、`/review`、`/debug`、`/evolve` 等内部阶段顶层命令。
- 不批量重写所有 subagent persona。
- 不改 `rose-memory` SQLite schema，不把 session handoff 自动长期写入 memory。
- 不新增依赖、lockfile、install 脚本行为或外部服务调用。
- 不同步已归档 `add-harness-evolution-layer` 的旧 delta specs；它的 missing/stale 文件声明不作为当前实现事实。

## Decisions

### 1. Direct allowlist 使用四条件，而不是“单文件”规则

- Decision: ROSE 只有在任务 exact-file/exact-symbol、low-risk、surgical、locally verifiable 且不需要项目传统发现时，才可直接编辑。
- Rationale: “单文件”仍可能是高风险核心 harness、schema、CI、安全或语义变更；四条件能防止过度直接执行。
- Alternative considered: 凡是单文件小改都直接做。Rejected，因为会绕过证据 gate 和 high-risk approval。

### 2. Context-saving dispatch 是强制门禁

- Decision: broad grep/list/search、3+ relevant files、2+ directories/subsystems、2+ likely search passes、noisy logs/tests、active/stale/generated 判断、上下游/同级模式定位等场景必须派发只读 scout。
- Rationale: subagent 的核心价值是保护 MainAgent context，而不是只有主 agent“做不了”才派。
- Alternative considered: 保持“prefer subagent”的软建议。Rejected，因为用户明确要求 subagent 更积极，并且软建议不可验证。

### 3. `code-scout` 产出 code locality map

- Decision: `code-scout` 结果必须能回答 target、upstream、downstream、peer patterns、tests/verification、recommended next reads、risk notes 和 conclusion。
- Rationale: ROSE 需要知道代码邻域和项目已有做法，而不是只拿到关键词命中。
- Alternative considered: 新建一个 `code-locality-scout` agent。Rejected for first phase，因为现有 `code-scout` 已覆盖只读代码定位，先增强职责和结果协议即可。

### 4. `repo-evidence-first` 作为独立中文 skill

- Decision: 新增 `skills/repo-evidence-first/SKILL.md`，正文中文，路径和 skill name 保持英文。
- Rationale: 用户要求最终文档中文；英文路径便于技能路由和仓库一致性。
- Alternative considered: 继续只在 `agents/rose.md` 中保留 Context Evidence Gate。Rejected，因为这会继续膨胀主控 prompt，且无法作为独立 gate 路由。

### 5. `session-handoff` 不等同于 memory

- Decision: 新增 `skills/session-handoff/SKILL.md`，仅在用户明确要求或后续已批准的命令合同要求时写入交接文档；OpenSpec change 默认写入当前 change 目录，用于 current-task continuity；长期 durable facts 仍由 `rose-memory` 通过 CLI 管理。
- Rationale: handoff 面向下一 session 的目标、证据、决策、未验证项和 continuation prompt；memory 面向长期可复用事实和 completion receipts。
- Alternative considered: 全部写入 rose-memory。Rejected，因为 raw handoff 容易污染长期记忆并带入日志/对话噪声。

### 6. Subagent results 分层为事实、推断和建议

- Decision: subagent result protocol 必须分离 observed facts、inferences、recommendations、unknowns 和 MainAgent next reads，并标注 evidence/freshness/confidence。
- Rationale: ROSE 不能把 subagent output 当 authority；分层格式能降低二次臆测风险。
- Alternative considered: 只要求 compact anchors。Rejected，因为 compact 不等于事实/建议边界清楚。

### 6a. 协议权威路径固定到 `aili-delivery-flow` references

- Decision: 本 change 的 canonical subagent packet/result protocol 路径是 `skills/aili-delivery-flow/references/protocols/`。如果顶层 `protocols/**` 在既有或后续变更中存在，它只能作为兼容索引、迁移入口或链接，不得复制另一套冲突规则。
- Rationale: 当前 runtime charter 和已安装 `aili-delivery-flow` skill 都把 lifecycle/protocol 细节放在 skill references；把协议放回该 skill 下可以减少顶层 docs 与 skill references 的双权威风险。
- Alternative considered: 沿用 `add-harness-evolution-layer` 中的顶层 `protocols/**`。Rejected for this change，因为用户本次明确指定 `skills/aili-delivery-flow/references/protocols/...`，且 top-level protocols 与 skill-local references 会形成双写。

### 7. `agents/rose.md` 只加短 router

- Decision: 后续实现时，`agents/rose.md` 只添加 direct/delegated work 与 minimal routing additions 的短引用。
- Rationale: 详细规则放入 skills/references/protocols，更容易审查、回滚和局部演进。
- Alternative considered: 把完整 direct-vs-delegated、repo-evidence、handoff 规则写进 ROSE。Rejected，因为会反向增加主上下文负担。

## Risks / Trade-offs

- [过度 subagent 化导致简单任务变慢] → Direct allowlist 明确保留 typo、文档措辞、注释、Markdown、小段 README/示例/测试说明和 tiny local code fix。
- [规则分散到多个文件后互相冲突] → `agents/rose.md` 只做 router；authority 文件按 direct-vs-delegated、repo-evidence、session-handoff、subagent protocols 分责。
- [与 `add-harness-evolution-layer` 重叠] → BUILD 前已归档旧 change 且未同步旧 delta specs；当前实现不得重新引入顶层 `protocols/**` 双权威。
- [subagent 协议过重] → 只对非平凡、harness-sensitive、evidence-heavy 或 review/test/security/debug 场景强制；小改不要求完整协议。
- [handoff 泄露 raw logs/secrets] → session-handoff 明确禁止 raw logs、完整 grep dumps、文件全文、secrets、tokens、cookies、credentials。

## Migration Plan

1. 完成本 OpenSpec proposal/design/spec/tasks，并运行 OpenSpec validation。
2. BUILD 前已确认并归档 `add-harness-evolution-layer`，不把旧顶层 `protocols/**` proposal 当作当前权威。
3. 第一实现包：新增 `direct-vs-delegated-work.md`、`repo-evidence-first/SKILL.md`、`session-handoff/SKILL.md`。
4. 第二实现包：更新 `parallel-subagent-dispatch`、subagent task/result protocol、`code-scout` result expectations。
5. 第三实现包：只给 `agents/rose.md` 添加短 router，不复制长文。
6. 验证：OpenSpec strict validation、零依赖结构/内容检查脚本、diff review、code-reviewer + test-engineer；security-auditor 仅在触及 secrets/tool permissions/memory/install/hook 时必跑。

## Confirmed Decisions From Interview

- `add-harness-evolution-layer` 已按用户批准归档，不同步其旧 delta specs；本 change 继续作为当前 BUILD 权威。
- `repo-evidence-first` 和 `session-handoff` 直接落到仓库 `skills/`，作为可审查、可版本化 runtime artifacts。
- subagent task/result 协议权威路径固定为 `skills/aili-delivery-flow/references/protocols/`；未来如需恢复/新增顶层 `protocols/`，只能作为索引/兼容层或另开变更。
- `session-handoff` 只在用户明确要求或后续已批准命令合同要求时创建交接文件。
