# 变更采访包：add-explain-retrospective-skills

## 1. 资料来源与证据

| 来源 | 已检查内容 | 观察到的事实 | 置信度 | 备注 |
|---|---|---|---|---|
| `proposal.md` | why / what / capabilities / impact | 当前是一个 OpenSpec 提案，包含 `explain-by-allegory`、`evidence-scoped-retrospective`、`implementation-notes`、`agent-operating-discipline` 四个 capability；不新增 top-level command；MVP 不新增 subagent；raw session exports 不提交。 | high | 作为本次 DEFINE 主合同。 |
| `design.md` | goals / non-goals / decisions / risks / migration | 两个新技能走 skill-first；self-improvement evidence-scoped + report-first；`implementation-notes.html` backend-neutral；`templates/AGENTS.md` 增加 selected execution guardrails；Rule 6 已改为 DCP-aware task-continuity checkpoint。 | high | 反映用户最新纠正：DCP 会使 raw percentage 不可靠。 |
| `tasks.md` | implementation tasks / validation | 实施任务包含创建 `implementation-notes.html`、更新 `templates/AGENTS.md`、创建两个 skills、更新 README attribution、验证 routing/safety。 | high | BUILD 前仍未执行。 |
| `specs/**/spec.md` | OpenSpec requirements | 四个 spec 覆盖 allegory 解释、retrospective evidence/safety/classification/report-first、implementation notes、agent operating discipline。 | high | 当前没有实现文件。 |
| 当前用户消息 | `/define` contract | 用户要求补齐 interview.md 与 test-plan.md；不得 implement；报告 BUILD readiness。 | high | 当前模式是 DEFINE。 |

## 2. 当前理解

- 目标：把一个已扩展的 OpenSpec 提案补齐到 BUILD 前的实施准备状态。
- 当前草稿表达的是：新增两个技能，并把自我改进、实现期 notes、执行期 guardrails 纳入同一个变更包。
- 已确认约束：
  - 仍保持一个提案。
  - raw OpenCode session exports / transcripts / logs / secrets 不进 git。
  - 优化后的 skills / workflow artifacts 可在批准、diff 检查、验证后提交。
  - MVP 不新增 retrospective subagent。
  - `implementation-notes.html` 必须 backend-neutral，不限 OpenSpec。
  - task/plan 中“具体 subagent 命名”要求已撤回。
  - Rule 6 不使用绝对 token 数；在 DCP 存在时也不以 raw context percentage 为主信号，改为 task-continuity risk。
- 暂定非目标：新增 top-level command、自动改 ROSE、提交原始会话证据、复制上游 prompt/article 原文。
- 仍不确定的地方：README attribution 的措辞边界、`implementation-notes.html` 的最低 HTML 结构、是否为 session exports 增加专门 ignored folder、是否需要把本提案拆分。

## 3. 需要你填写的问题

| ID | 问题 | 为什么要问 | 推荐默认答案 | 取舍影响 | 你的填写 | 写回位置 |
|---|---|---|---|---|---|---|
| Q1 | 本变更继续保持一个提案，还是拆成两个提案？ | 影响 review 粒度和 BUILD 包划分。 | 保持一个提案，但 BUILD 时分成独立 packages：skills、implementation-notes、AGENTS guardrails、README/verification。 | 一个提案更连贯；拆分更易 review 但需要迁移 artifacts。 | 一个 | `proposal.md`, `tasks.md` |
| Q2 | `implementation-notes.html` 的最低结构是否固定？ | BUILD worker 需要知道创建什么 HTML，不应随意发挥。 | 使用简单静态 HTML：title、metadata、Spec Deviations、Temporary Decisions、Trade-offs、Open Questions、Unverified Assumptions、Evidence Pointers、Update History；不引入 JS/CSS 依赖。 | 固定结构便于 review 和后续 retrospective；太复杂会偏离 MVP。 | 使用简单静态 HTML：title、metadata、Spec Deviations、Temporary Decisions、Trade-offs、Open Questions、Unverified Assumptions、Evidence Pointers、Update History；不引入 JS/CSS 依赖。目的仅是为了方便人类阅读审阅，不用太花哨。 | `specs/implementation-notes/spec.md`, `tasks.md` |
| Q3 | 是否要为 raw/sanitized OpenCode session exports 设置专门 ignored repo-local 路径？ | 当前策略是“不放入 repo”；但 future retrospective 可能需要临时文件落点。 | MVP 不新增路径；继续要求使用 repo 外临时位置或用户显式批准的 ignored path。 | 不新增路径更安全；新增路径更方便但需要 `.gitignore` / retention policy。 | 默认 | `design.md`, `README.md` |
| Q4 | README attribution 应如何写？ | 需要标注概念来源但避免复制不可抓取/未授权原文。 | 只写概念性来源：Amanda Askell-style allegory prompting；Vaibhav/VB/Codex-style self-improvement prompting；user-provided Mnilax/Karpathy/Forrest Chang-style agent discipline summary；标注 direct X content Unverified if not fetched. | 透明但不搬运；不会把外部文本变成 repo 内容。 | 引用这个：https://x.com/Mnilax/status/2053116311132155938 | `README.md` |
| Q5 | `evidence-scoped-retrospective` 的输出是否允许直接创建 OpenSpec proposal 草稿？ | 这决定 self-improvement report-first 后的下一步是否可自动落成提案。 | 允许“建议创建/更新 proposal”并在用户批准后通过 DEFINE/OpenSpec 流程创建；不允许直接修改 protected harness surfaces。 | 保持 report-first；减少自动自改风险。 | 不和openspec绑定，如果需要类似spec的提案，可以看看自己能用什么，然后询问用户 | `specs/evidence-scoped-retrospective/spec.md` |
| Q6 | `templates/AGENTS.md` 的 DCP-aware checkpoint 文案是否作为强制规则还是指导性 guardrail？ | 太强可能打断流畅执行；太弱可能不生效。 | 强制规则：当 task-continuity risk 出现时必须 checkpoint；但不以 raw percentage 为硬门槛。 | 更符合你对 DCP 的修正；可执行性更好。 | 强制规则：当 task-continuity risk 出现时必须 checkpoint；但不以 raw percentage 为硬门槛。 | `specs/agent-operating-discipline/spec.md` |
| Q7 | BUILD 前是否需要先由你确认本 interview 与 test-plan，还是可以把未答问题标为 `Open Question` 后进入受限 BUILD？ | AILI gate 需要确认、豁免或标记 Unverified。 | 先由你确认/填写关键问题；若你说“按默认”，再进入 BUILD。 | 减少实现返工；稍慢。 | 我已经填了 | `tasks.md`, BUILD gate |

## 4. 设计漏洞 / 证据缺口 / 反例

| ID | 类型 | 说明 | 建议处理方式 | 状态 |
|---|---|---|---|---|
| L1 | Unverified external source | X 链接内容无法直接抓取；只有用户粘贴/转述内容可用。 | README attribution 使用“conceptual inspiration / user-provided summary”，不复制原文。 | open |
| L2 | Scope coupling | 一个提案同时改 skills、implementation notes、AGENTS template，review 面较宽。 | BUILD 分包并在 `implementation-notes.html` 记录偏差；如用户要求再拆提案。 | open |
| L3 | Artifact tracking | 当前分支上 `openspec/` 为 untracked；是否最终提交 OpenSpec artifacts 取决于仓库策略。 | 最终 diff 检查时显式报告 tracked/untracked 状态；不提交 raw sessions。 | open |
| L4 | HTML notes complexity | `implementation-notes.html` 若包含样式/脚本可能引入无关复杂度。 | MVP 使用静态、无脚本、可读 HTML。 | open |
| L5 | DCP checkpoint semantics | DCP 会使 context usage 百分比不准确。 | 已改为 task-continuity risk trigger；实现时需确保 template 不残留 70/85 主门槛。 | open |

## 5. 填写说明

- 可以直接在“你的填写”列里写答案。
- 不确定的地方写“不确定”即可。
- 接受推荐默认答案时，写“同意默认”。
- 不进入本次 scope 的内容，写“本次不做”。
- 未填写内容不会被写成事实，只会保留为 `Open Question`。
- 无证据支撑但暂时保留的内容会标为 `Unverified`。

## 6. 后续写回映射

| 用户答案 | 将写回到 | 写回方式 |
|---|---|---|
| Q1 | `proposal.md`, `tasks.md` | 确认单提案或拆分；若保持单提案，明确 BUILD packages。 |
| Q2 | `specs/implementation-notes/spec.md`, `tasks.md` | 固化 HTML 最低结构与安全边界。 |
| Q3 | `design.md`, `README.md` | 更新 session export 临时存放策略。 |
| Q4 | `README.md` | 调整 attribution 文案。 |
| Q5 | `specs/evidence-scoped-retrospective/spec.md` | 明确 retrospective report 到 proposal 的许可边界。 |
| Q6 | `specs/agent-operating-discipline/spec.md` | 明确 DCP-aware checkpoint 的强制程度。 |
| Q7 | BUILD gate | 决定 READY / BLOCKED / WAIVED / UNVERIFIED。 |

## 7. 答案吸收记录

_用户填写后由模型补充。_

| 问题 | 用户答案 | 形成的决策 | 已写回位置 | 剩余不确定 |
|---|---|---|---|---|
| Q1 | 一个 | 保持一个 OpenSpec proposal；BUILD 阶段按独立 packages 执行。 | `tasks.md` | 无 |
| Q2 | 使用简单静态 HTML，不引入 JS/CSS；目的为方便人类阅读审阅。 | `implementation-notes.html` 固定为简单静态 HTML，包含 title、metadata、Spec Deviations、Temporary Decisions、Trade-offs、Open Questions、Unverified Assumptions、Evidence Pointers、Update History。 | `design.md`, `specs/implementation-notes/spec.md` | 无 |
| Q3 | 默认 | MVP 不新增 repo-local session export 路径；继续不把 raw exports 放入 repo，除非未来用户显式批准 ignored path。 | `design.md` | 无 |
| Q4 | 引用 `https://x.com/Mnilax/status/2053116311132155938` | README attribution 使用该链接作为 Mnilax-style agent-discipline source；如直接抓取失败，标注 direct X content Unverified。 | `tasks.md` | 直接 X 内容仍可能 Unverified |
| Q5 | 不和 OpenSpec 绑定；需要类似 spec 的提案时先看当前能用什么，然后询问用户。 | retrospective 不假设 OpenSpec；根据当前项目 backend 选择 OpenSpec / Superpowers-style / custom files，并先问用户。 | `design.md`, `specs/evidence-scoped-retrospective/spec.md` | 无 |
| Q6 | 强制规则；不以 raw percentage 为硬门槛。 | DCP-aware checkpoint 是强制 rule：出现 task-continuity risk 必须 checkpoint；raw percentage 不作主门槛。 | 已由 `specs/agent-operating-discipline/spec.md` 覆盖 | 无 |
| Q7 | 我已经填了 | interview gate 已由用户填写；BUILD 仍需 test-plan 接受或 waiver。 | BUILD gate report | test-plan acceptance pending |
