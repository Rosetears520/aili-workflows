[KNOWN] # 变更采访包：classify-ecc-agents-for-aili

[KNOWN] ## 1. 资料来源与证据

| 来源 | 已检查内容 | 观察到的事实 | 置信度 | 备注 |
|---|---|---|---|---|
| [KNOWN] 用户 `/define` 输入与后续修正 | 选定新增项与非目标 | [KNOWN] 用户要求新增 `spec-miner`、`comment-accuracy-review`、`agent-evaluator`、`opensource-sanitizer`、`oss-release-readiness`、`build-failure-repair`，不做专门语言 agent，并移除 `type-design-analyzer` | high | [KNOWN] 当前写回以此为最高优先级 |
| [KNOWN] `ecc-agents-classification.md` | ECC 67 agent 分类 | [KNOWN] 初始分类已覆盖 67 个 ECC agents | high | [KNOWN] 后续 BUILD 只针对选中子集 |
| [KNOWN] subagent local gap review | 本地 agents/skills 覆盖 | [KNOWN] 复核指出 reverse spec mining、type-invariant review、comment accuracy、OSS sanitization、agent-output evaluation 是真实缺口 | medium | [KNOWN] 未运行生产测试 |
| [KNOWN] subagent prior-art review | ECC 外部角色摘要 | [KNOWN] 复核建议提升 `agent-evaluator` 和 `opensource-sanitizer` 优先级 | medium | [KNOWN] 不复制 ECC prompt 原文 |
| [KNOWN] plan audit | 分类/方案审计 | [KNOWN] 审计曾建议把 `comment-analyzer` 降级为 skill，把 `spec-miner` 和 `type-design-analyzer` 保持为只读 agents；用户后续移除了 `type-design-analyzer` | medium | [KNOWN] 用户修正优先于审计建议 |
| [KNOWN] review-quality prior-art review | 三个外部 code-review skills | [KNOWN] 用户确认这三个更应该作为 skills 的参考来源；推荐新增 `code-review-quality-gates` skill，而不是新增通用 reviewer agents | medium | [KNOWN] 不复制上游 prompt 原文 |

[KNOWN] ## 2. 当前理解

- [KNOWN] 目标：把 ECC 全量 agent 评估结果推进到可执行 BUILD 合同，但仍停留在 DEFINE，不实现生产 agents/skills。
- [KNOWN] 当前草稿表达的是：分类先行、禁止全量照搬、只在用户批准后按 package 实现。
- [KNOWN] 已确认约束：不新增专门语言 agents；不复制 ECC prompt 原文；不绕过 ROSE 生命周期、review/security/verification gate。
- [KNOWN] 暂定非目标：不新增 `type-design-analyzer`、`loop-operator`、`opensource-forker`、语言 reviewer swarm、domain/network/healthcare/GAN agents、重复通用 code-review agents。
- [KNOWN] 已确认新增：`harness-optimization-audit` 纳入本包；所有选中 agents/skills 按现有默认安装模型处理。
- [INFERRED] 仍不确定的地方：是否开始生产文件 BUILD 实现。

[KNOWN] ## 3. 覆盖矩阵与状态

状态只能使用：`Confirmed by evidence`、`Not applicable`、`Needs question`、`Open Question`、`Unverified`。

| 维度 | 状态 | 证据 / 原因 | 关联问题 | 写回目标 |
|---|---|---|---|---|
| goal/success | Confirmed by evidence | [KNOWN] 用户选择了具体新增项，并确认三个 code-review 项目写进提案作为 skill 增强来源 | N/A | `proposal.md` / `tasks.md` |
| scope/non-goals | Confirmed by evidence | [KNOWN] 用户明确“不做专门语言的agent” | N/A | `proposal.md` / `design.md` |
| roles/permissions | Confirmed by evidence | [KNOWN] 方案记录 `spec-miner`、`agent-evaluator`、`opensource-sanitizer` 为只读或非破坏性；`code-review-quality-gates` 是 skill/rubric source；`type-design-analyzer` 不进入本包 | N/A | `design.md` / specs |
| happy path | Confirmed by evidence | [INFERRED] BUILD 可按 scaffold → parallel component lanes → integration 顺序执行 | N/A | `design.md` / `tasks.md` |
| failure path | Confirmed by evidence | [INFERRED] BUILD 缺审批、source ambiguity、over-trigger、secret disclosure 都列为风险 | N/A | `design.md` / `test-plan.md` |
| retries/rollback | Not applicable | [KNOWN] DEFINE-only artifacts不引入运行时重试/回滚 | N/A | `test-plan.md` |
| boundary conditions | Confirmed by evidence | [KNOWN] per-language agents excluded; destructive `opensource-forker` excluded | N/A | `proposal.md` / specs |
| data lifecycle | Not applicable | [KNOWN] DEFINE-only docs不创建业务数据 | N/A | `test-plan.md` |
| state transitions | Confirmed by evidence | [KNOWN] DEFINE → BUILD 需要用户确认/批准 | N/A | `tasks.md` |
| API/CLI/UI contracts | Not applicable | [KNOWN] 本 change 不定义用户 CLI/API/UI | N/A | N/A |
| compatibility/migration | Confirmed by evidence | [INFERRED] 未来 BUILD 需验证 manifest/install/docs，但 DEFINE不改 runtime | N/A | `test-plan.md` |
| security/privacy | Confirmed by evidence | [KNOWN] 用户确认 `harness-optimization-audit` 纳入本包，且设计为 report-first harness audit | N/A | `design.md` / `tasks.md` |
| performance/reliability | Confirmed by evidence | [INFERRED] 不做语言 swarm 可降低 routing/token 噪音 | N/A | `design.md` |
| observability | Confirmed by evidence | [INFERRED] 未来 BUILD 通过 OpenSpec progress/test-plan 记录证据 | N/A | `tasks.md` / `test-plan.md` |
| acceptance/testability | Confirmed by evidence | [KNOWN] `test-plan.md` 记录 validation、git diff、manual checklist | N/A | `test-plan.md` |
| rollout/rollback | Confirmed by evidence | [KNOWN] 用户确认所有选中 agents/skills 默认安装 | N/A | `design.md` / `tasks.md` |
| explicit non-goals | Confirmed by evidence | [KNOWN] proposal 记录不做全量吸收/语言 swarm/新 lifecycle commands | N/A | `proposal.md` |

[KNOWN] ## 4. 需要你填写的问题

| ID | 问题 | 为什么要问 | 影响的 artifact / decision | 有证据支撑的推荐默认答案 | 后果 / 取舍 | 你的填写 | 写回位置 |
|---|---|---|---|---|---|---|---|
| Q1 | [KNOWN] `harness-optimization-audit` 要不要纳入首批 BUILD？ | [INFERRED] subagent 认为它是 P1/P2 有价值项 | scope / tasks / risk | [KNOWN] 用户已选择纳入 | 纳入会增强 harness 调优审计，但扩大首批 scope | [KNOWN] 做 | `design.md` / `tasks.md` |
| Q2 | [KNOWN] 未来这些组件是否全部默认安装？ | [INFERRED] 当前 manifest 多为默认安装；optional pack 会改变 installer/manifest设计范围 | manifest / installer / acceptance | [KNOWN] 用户已选择默认安装 | 默认安装简单且符合现有组件模型 | [KNOWN] 用户确认原 7 个默认安装，且 `harness-optimization-audit` 也纳入本包；最终选中 8 个组件默认安装 | `design.md` / `tasks.md` |

[KNOWN] ## 5. 设计漏洞 / 证据缺口 / 反例

| ID | 类型 | 说明 | 建议处理方式 | 状态 |
|---|---|---|---|---|
| L1 | [UNVERIFIED] Full prompt review | [KNOWN] 当前分类未完成 ECC prompt-by-prompt port review | [INFERRED] BUILD 阶段只 clean-room rewrite concepts，不复制 prompt 原文 | open |
| L2 | [OPEN QUESTION] Source fork ambiguity | [KNOWN] `affaan-m/ECC` 是选定源，但存在 fork ambiguity | [INFERRED] 若用户指定其他 fork，重新分类 | open |
| L3 | [INFERRED] Over-trigger risk | [INFERRED] 新增 agents/skills 太多可能制造 routing 噪音 | [INFERRED] 首批限制为选中 7 个组件，语言 agents、重复通用 reviewer agents 和 `type-design-analyzer` 不进本包 | mitigated |
| L4 | [UNVERIFIED] Review-source prompt review | [KNOWN] 三个 code-review skill 只完成 prior-art 模式提炼，未完成逐字 prompt port review | [INFERRED] BUILD 阶段只提炼模式，不复制 prompt 原文 | open |

[KNOWN] ## 6. 填写说明

- [KNOWN] 可以直接在“你的填写”列里写答案。
- [KNOWN] 接受推荐默认答案时，写“同意默认”。
- [KNOWN] 本次不做的内容，写“本次不做”。
- [KNOWN] 未填写内容不会被写成事实，只会保留为 `Open Question`。
- [KNOWN] 如果你明确批准 BUILD，需要说明批准哪个 package 或是否批准整个选中队列。

[KNOWN] ## 7. 后续写回映射

| 用户答案 | 将写回到 | 写回方式 | 写回前门禁 |
|---|---|---|---|
| Q1 | `design.md`, `tasks.md` | [KNOWN] 调整 P2/首批 scope | confirmed / waived / accepted `UNVERIFIED` |
| Q2 | `design.md`, `tasks.md`, future manifest design | [KNOWN] 调整默认安装/optional策略 | confirmed / waived / accepted `UNVERIFIED` |

[KNOWN] ## 8. 答案吸收记录

_用户填写后由模型补充。_

| 问题 | 用户答案 | 分类 | 形成的决策 | 已写回位置 | 剩余不确定 / 追问 |
|---|---|---|---|---|---|
| [KNOWN] remove type-design-analyzer | [KNOWN] 用户表示不要这种专门代码审查，TS 可能用得少 | confirmed | [KNOWN] `type-design-analyzer` 不进入当前 BUILD package | `proposal.md`, `design.md`, `tasks.md`, `ecc-agents-classification.md`, `test-plan.md` | [KNOWN] 无 |
| [KNOWN] add code-review-quality-gates | [KNOWN] 用户确认三个 code-review 项目应作为 skills 来源并要求写进提案 | confirmed | [KNOWN] 新增 `code-review-quality-gates` skill，吸收 review rubric、输出契约、risk/file-priority、fixture/golden、中文报告 profile；不新增重复 reviewer agents | `proposal.md`, `design.md`, `tasks.md`, `ecc-agents-classification.md`, `test-plan.md` | [KNOWN] 无 |
| [KNOWN] include harness-optimization-audit | [KNOWN] 用户表示 `harness-optimization-audit` 做 | confirmed | [KNOWN] `harness-optimization-audit` 纳入当前 package queue | `proposal.md`, `design.md`, `tasks.md`, `ecc-agents-classification.md`, `test-plan.md` | [KNOWN] 无 |
| [KNOWN] default install selected components | [KNOWN] 用户表示默认安装，skills、agents 都默认安装；加入 `harness-optimization-audit` 后最终选中 8 个组件 | confirmed | [KNOWN] 所有选中 agents/skills 使用现有默认安装模型 | `proposal.md`, `design.md`, `tasks.md`, `test-plan.md` | [KNOWN] 无 |

[KNOWN] ## Interview Readiness

[KNOWN] State: `READY`.

[KNOWN] Reason: material interview questions Q1/Q2 are answered; BUILD implementation still requires explicit production-edit approval if the user wants implementation to start.
