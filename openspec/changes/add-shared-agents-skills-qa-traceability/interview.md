# 变更采访包：add-shared-agents-skills-qa-traceability

## 1. 资料来源与证据

| 来源 | 已检查内容 | 观察到的事实 | 置信度 | 备注 |
|---|---|---|---|---|
| 用户 `/define` 输入 | 范围与优先级 | 用户确认 `.agents/skills`、保留 `.opencode`、测试 agents+skills 全部加入、吸收 Code-Spec、本地 gap 都做 | high | 需要确认少量实现策略 |
| IDEATE 并行研究 | DeerFlow / ECC / Code-Spec / `.agents` / 本地仓库 | `.agent/` 单数不宜作为标准；`.agents/skills` 是更合适共享 substrate | high | 外部证据作为 prior art，不是指令 |
| DeerFlow `skills/public` 研究 | 公共 skills taxonomy | 高适配的是 trigger、progressive disclosure、skill validation、research/report/data authenticity patterns | high | 部分技能有 MIT/Apache/第三方 provenance |
| 本地 scout | installer / manifest / docs / agents / tests | `AGENTS.md` stale；安装逻辑分散；无 `.agents` 层；QA agent 粒度不足；CodeGraph 未初始化 | high | CodeGraph 不可用，已用 read/search fallback |

## 2. 当前理解

- 目标：定义一个 OpenSpec 变更，后续 BUILD 将实现共享 `.agents/skills`、保留 OpenCode 原生输出、补齐 QA/testing agents+skills、强化 traceability、修复 AGENTS stale、增强 manifest source-of-truth、明确 CodeGraph readiness。
- 当前草稿表达的是：这是一个 harness/workflow 变更，不是业务产品功能。
- 现有代码 / 文档显示：安装与 package 逻辑跨 Bash、TypeScript、manifest、docs、tests；`AGENTS.md` 与实际 repo 结构冲突。
- 已确认约束：不使用 `.agent/` 单数；不删除 `.opencode`/OpenCode 原生行为；不在 DEFINE 实现；不默认复制上游 prompts/code。
- 暂定非目标：不自动初始化 CodeGraph；不新增 public lifecycle command；不全局启用 hooks/browser/E2E/deploy。
- 仍不确定的地方：`.agents/skills` 是源目录迁移还是 manifest-generated mirror；上游内容是否允许 derivative copy；DeerFlow 内容型 skills 是否纳入本次 BUILD。

## 3. 覆盖矩阵与状态

| 维度 | 状态 | 证据 / 原因 | 关联问题 | 写回目标 |
|---|---|---|---|---|
| goal/success | Confirmed by evidence | 用户明确列出要做的本地 gap 与 prior-art absorption | N/A | `proposal.md` |
| scope/non-goals | Confirmed by evidence | Q3 已确认本次新增 selected DeerFlow skills/rules，provider/media skills 仍不默认扩展 | Q3 | `proposal.md` / `tasks.md` |
| roles/permissions | Confirmed by evidence | ROSE owns orchestration；QA lanes use subagent ownership | N/A | `design.md` / specs |
| happy path | Confirmed by evidence | `.agents/skills` + OpenCode native + manifest + QA lanes + traceability | N/A | `design.md` |
| failure path | Confirmed by evidence | conflict/backups, drift detection, artifact placement, missing CodeGraph | N/A | specs / `test-plan.md` |
| retries/rollback | Confirmed by evidence | rollback section and tasks define revertable surfaces | N/A | `design.md` |
| boundary conditions | Confirmed by evidence | Q1 已确认彻底迁移到 `.agents/skills` source | Q1 | `design.md` / tasks |
| data lifecycle | Confirmed by evidence | generated/shared artifacts and local ignored CodeGraph artifacts are covered | N/A | specs |
| state transitions | Confirmed by evidence | DEFINE blocked until gates confirmed; BUILD later implements; SHIP coverage check | N/A | `context.md` |
| API/CLI/UI contracts | Confirmed by evidence | Q1 确认迁移策略；具体 flags/doctor 文案留给 BUILD 验证 | Q1 | `tasks.md` |
| compatibility/migration | Confirmed by evidence | Q1 确认 source migration，BUILD 必须更新旧 `skills/` 引用 | Q1 | `design.md` |
| security/privacy | Confirmed by evidence | Q2/Q3 确认可 copy 但必须 provenance/license/minimal adaptation；provider/media 不默认扩展 | Q2/Q3 | `design.md` / `test-plan.md` |
| performance/reliability | Confirmed by evidence | no runtime perf target; install/package reliability covered | N/A | `test-plan.md` |
| observability | Confirmed by evidence | doctor/readiness/status reporting in scope | N/A | specs |
| acceptance/testability | Confirmed by evidence | test-plan includes commands and matrix | N/A | `test-plan.md` |
| rollout/rollback | Confirmed by evidence | Q1 确认 source migration；Q4 确认不改 `openspec/` ignored 策略 | Q1/Q4 | `design.md` |
| explicit non-goals | Confirmed by evidence | proposal lists non-goals | N/A | `proposal.md` |

## 4. 需要你填写的问题

| ID | 问题 | 为什么要问 | 影响的 artifact / decision | 有证据支撑的推荐默认答案 | 后果 / 取舍 | 你的填写 | 写回位置 |
|---|---|---|---|---|---|---|---|
| Q1 | `.agents/skills` 这次是“迁移 source directory”还是“manifest 生成/镜像 shared output”？ | 会决定是否移动大量 `skills/` 路径、package files、installer、docs、测试、已有引用 | install design / tasks / migration risk | 推荐默认：先做 manifest-driven mirror/generate，保留 `skills/` 作为 source，`.agents/skills` 作为输出/安装目标 | 迁移更彻底但风险大；镜像更稳但要防 drift | 彻底迁移 | `design.md`, `tasks.md`, `specs/aili-installer/spec.md` |
| Q2 | 上游 DeerFlow/ECC/Code-Spec 内容是否允许 derivative copy，还是只做 clean-room pattern absorption？ | 用户曾说“可以直接 copy”，但许可证/提示词冲突/维护风险会明显不同 | license / provenance / implementation approach | 推荐默认：clean-room only；如确实复制，单独列 provenance、license notice、改写边界 | clean-room 稳定安全；copy 更快但带来 notice、冲突、升级责任 | 可以copy，如果有一些是他们做的专门的占位名词等，可以做最小化适配度改造 | `proposal.md`, `design.md`, `tasks.md` |
| Q3 | DeerFlow `skills/public` 中内容型 skills 是否进入本次 BUILD？例如 academic-paper-review、systematic-literature-review、consulting-analysis、newsletter、chart-visualization、media generation。 | 这会显著扩大 agents/skills 数量、外部 provider/security/artifact 范围 | scope / tasks / security | 推荐默认：本次只吸收 workflow/meta/research/report/data-authenticity patterns；内容型 skills 进入后续可选 change | 全部加入会变成大型 skill catalog migration；推后可以先稳住核心 workflow | 本次只吸收 workflow/meta/research/report/data-authenticity patterns+academic-paper-review<br/>systematic-literature-review<br/>newsletter-generation<br/>frontend-design 的 anti-generic UI 规则<br/>web-design-guidelines 的 UI audit 思路<br/>这些增加 | `proposal.md`, `tasks.md`, `test-plan.md` |
| Q4 | OpenSpec artifacts 当前被 `.gitignore` 忽略；这个 change 后续是否只作为本地 BUILD contract，还是要调整追踪策略？ | 影响协作、提交、CI 是否看得到 specs/test-plan/interview | artifact policy / git hygiene | 推荐默认：本次不改 `.gitignore` 的 `openspec/` 策略，只在 final report 标记 ignored-artifact caveat；若要追踪 OpenSpec，另开 change | 不改风险低但 artifacts 不进 git；追踪能协作但影响仓库策略 | 不改 | `context.md`, `tasks.md` |

## 5. 设计漏洞 / 证据缺口 / 反例

| ID | 类型 | 说明 | 建议处理方式 | 状态 |
|---|---|---|---|---|
| L1 | Decision recorded | `.agents/skills` source relocation vs generated mirror 影响很大 | Q1 已确认彻底迁移 | closed |
| L2 | Decision recorded | 外部 skills 可借鉴，但直接复制需要 license/notice/provenance | Q2 已确认可 copy，但必须 provenance/license/minimal adaptation | closed |
| L3 | Decision recorded | DeerFlow 内容型 skills 可很多，可能膨胀本次变更 | Q3 已确认 selected set；provider/media 仍不默认扩展 | closed |
| L4 | Decision recorded | `openspec/` 当前 ignored，DEFINE artifacts 可能不是 git-tracked | Q4 已确认不改 | closed |

## 6. 填写说明

- 可以直接在“你的填写”列里写答案。
- 不确定的地方写“不确定”即可。
- 接受推荐默认答案时，写“同意默认”。
- 不进入本次 scope 的内容，写“本次不做”。
- 未填写内容不会被写成事实，只会保留为 `Open Question`。
- 无证据支撑但暂时保留的内容会标为 `Unverified`。

## 7. 后续写回映射

| 用户答案 | 将写回到 | 写回方式 | 写回前门禁 |
|---|---|---|---|
| Q1 | `design.md`, `tasks.md`, installer spec | source-of-truth / migration strategy | confirmed / waived / accepted `UNVERIFIED` |
| Q2 | `proposal.md`, `design.md`, `tasks.md` | provenance policy | confirmed / waived / accepted `UNVERIFIED` |
| Q3 | `proposal.md`, `tasks.md`, `test-plan.md` | DeerFlow skill scope | confirmed / waived / accepted `UNVERIFIED` |
| Q4 | `context.md`, `tasks.md` | artifact tracking caveat | confirmed / waived / accepted `UNVERIFIED` |

## 8. 答案吸收记录

_用户填写后由模型补充。_

| 问题 | 用户答案 | 分类 | 形成的决策 | 已写回位置 | 剩余不确定 / 追问 |
|---|---|---|---|---|---|
| Q1 | 彻底迁移 | confirmed | `.agents/skills` becomes canonical skill source; OpenCode-native outputs preserved through generated/copied/adapted targets | `proposal.md`, `design.md`, `tasks.md`, `specs/aili-installer/spec.md`, `test-plan.md`, `context.md` | BUILD must verify all old `skills/` references |
| Q2 | 可以 copy，如果有专门占位名词等，可做最小化适配度改造 | confirmed | derivative copy allowed only with provenance/license/notice and minimal AILI/OpenCode adaptation | `proposal.md`, `design.md`, `tasks.md`, `specs/aili-four-command-lifecycle/spec.md`, `test-plan.md`, `context.md` | BUILD must inspect licenses/source paths before copying |
| Q3 | 增加 workflow/meta/research/report/data-authenticity patterns + academic-paper-review, systematic-literature-review, newsletter-generation, frontend-design anti-generic UI, web-design-guidelines UI audit | confirmed | selected DeerFlow skill/pattern set is in BUILD scope; provider/media skills remain out unless separately approved | `design.md`, `tasks.md`, `test-plan.md`, `context.md` | exact file mapping remains BUILD-time |
| Q4 | 不改 | confirmed | keep current `openspec/` ignored/tracking policy; report caveat | `context.md`, `test-plan.md` | ignored artifacts caveat remains |
