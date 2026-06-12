# 变更采访包：enhance-change-interviewer-readiness-gates

## 1. 资料来源与证据

| 来源 | 已检查内容 | 观察到的事实 | 置信度 | 备注 |
|---|---|---|---|---|
| 用户 `/define` 输入 | 目标描述 | 用户要求完整改造 `change-interviewer`：全面多轮采访、用户回答歧义检测、阻塞实现门禁、grill-style 推荐答案和证据优先规则。 | high | 当前 DEFINE 范围直接来自用户。 |
| IDEATE 摘要 | 需求澄清 | 用户明确要求“采访不止一轮”、用户写完仍有歧义不能开工、不是小修、问题要全面。 | high | 作为本 change 的核心验收标准。 |
| `skills/change-interviewer/SKILL.md` | 现有 skill 合约 | 现有协议已有 OpenSpec 输出、证据表、推荐默认答案、stress-test、答案吸收和写回规则，但未强制全面 coverage matrix、多轮答案歧义检测或明确 readiness states。 | high | BUILD 主要编辑目标。 |
| `skills/strategy-stress-test/SKILL.md` | 质量门禁能力 | 已有 missing evidence、hidden assumption、counterexample、contradiction、verification gap、user decision required 等漏洞分类，可复用于 interview packet / answer-set gate。 | high | 复用而非新增审稿机制。 |
| `skills/test-document-generator/SKILL.md` | 同类 artifact skill | 已要求 source-grounding、critical-gap blocking、stress-test、持久化测试文档。 | high | 作为 blocking/test-plan pattern。 |
| `openspec/specs/aili-four-command-lifecycle/spec.md` | DEFINE/BUILD gate | DEFINE 要创建/更新 interview/test-plan；BUILD 不得在 spec/questionnaire/test-plan gate 未确认、未 waiver、未接受 `UNVERIFIED` 时开始。 | high | 需要补充“填完但含歧义仍 BLOCKED”。 |
| `openspec/specs/skill-routing-boundaries/spec.md` | skill 修改边界 | touched skills 的 `references/*` 必须存在；长 skill 拆分到新 references 需要用户明确批准。 | high | 默认 BUILD 不新增 skill-local reference 文件。 |
| `README.md` | public skill description | README 描述 `change-interviewer` 生成证据驱动中文问卷包并写回目标文件。 | medium | BUILD 后若描述过时再更新。 |

## 2. 当前理解

- 目标：把 `change-interviewer` 变成全面、多轮、证据优先、能阻塞不清晰实现的需求采访协议。
- 当前草稿表达的是：不再接受“生成一份较短问卷就算完成”；必须覆盖所有实现相关维度，问题要有影响力和推荐默认答案，用户回答后还要检查歧义/冲突/不可测试项。
- 现有代码 / 文档显示：现有 skill 已有很多基础机制，但缺少强制性 coverage matrix、answer quality gate、multi-round follow-up 和明确 readiness state。
- 已确认约束：DEFINE 不实现；不新增顶层命令；不复制上游 skill 文本；默认不新增 skill-local reference 文件；保持 OpenSpec deterministic placement。
- 暂定非目标：独立 `design-grill` skill；公开 `/grill` 命令；改 memory schema、installer、dependency、lockfile；把所有 artifact skill 都重写。
- 仍不确定的地方：BUILD 是否允许新增 `skills/change-interviewer/references/*`；README/lifecycle questionnaire policy 是否必须同步；是否需要新增/更新 fixture。

## 3. 需要你填写的问题

| ID | 覆盖维度 | 问题 | 为什么要问 | 推荐默认答案 | 取舍影响 | 你的填写 | 写回位置 |
|---|---|---|---|---|---|---|---|
| Q1 | Scope / file boundary | BUILD 是否允许把 `change-interviewer` 拆成新的 `skills/change-interviewer/references/*` 文件？ | `skill-routing-boundaries` 要求长 skill 拆分必须获批；这决定实现是内联改 `SKILL.md` 还是可拆 reference。 | 默认不允许新增 reference；先内联完成完整修复，只有明显过长再另行请求。 | 不新增文件最小、风险低；新增 reference 可读性更好但扩大 edit surface。 | 可以 | `design.md`, `tasks.md` |
| Q2 | Trigger / UX | 是否需要在 `change-interviewer` description / triggers 中显式加入“interview me / grill requirements / 拷问需求 / 追问我直到能写 spec”类触发，同时避免接管纯“压测方案/评审方案”请求？ | 这影响 skill routing 和用户能否自然触发新模式，同时要避免和 `strategy-stress-test` 的方案压测职责冲突。 | 加入需求采访/写回导向的 grill 触发；纯“帮我压测这个设计/计划/完成声明”仍路由 `strategy-stress-test`。不新增顶层命令。 | 加触发提升可发现性；明确边界可避免抢占 strategy-stress-test；不加触发 diff 更小但用户仍可能不知道如何调用。 | 加入 | `skills/change-interviewer/SKILL.md`, maybe `README.md` |
| Q3 | Comprehensive coverage | coverage matrix 是否必须完整列出每个维度的状态，即使某维度是 `Not applicable`？ | 用户要求“问题要全面”，但也要避免无意义问题。 | 是：每个维度都要分类；`Not applicable` 写简短理由，不必问问题。 | 全列出更可审计但文档较长；只列问题更短但容易漏项。 | 是的 | `specs/change-interviewer/spec.md`, `SKILL.md` |
| Q4 | Question threshold | 是否接受“全面但非泛化”的问题规则：不限制问题数量，但每个问题必须能改变 scope/design/tasks/acceptance/tests/risk/safety？ | 避免从“少而狠”反弹到“多而废”。 | 接受。全面覆盖维度，但删除不会改变实现准备度的泛泛问题。 | 质量阈值能控制噪音；完全不筛选会造成用户填写负担。 | 接受 | `design.md`, `SKILL.md` |
| Q5 | Recommended defaults | 推荐默认答案是否必须有证据或明确标为 `Assumption` / `Unverified`？ | grill-style 推荐答案如果无证据，可能误导用户。 | 是。推荐默认答案要说明证据/理由；证据不足就标为 `Unverified` 或让用户确认。 | 安全但更啰嗦；无证据默认答案更快但会制造假确定性。 | 是。推荐默认答案要说明证据/理由；证据不足就标为 `Unverified` 或让用户确认。 | `specs/change-interviewer/spec.md`, `SKILL.md` |
| Q6 | Multi-round gate | 用户填完第一轮后，只要存在材料性歧义/冲突/不可测试答案，是否必须进入第二轮/第三轮而不是写回并开工？ | 这是用户明确痛点：填了但有歧义不能开始工作。 | 是，必须 `BLOCKED_FOR_CLARIFICATION` 或等价 `BLOCKED`，直到澄清/waive/accepted `UNVERIFIED`。 | 严格 gate 防止错做；允许模糊开工更快但风险高。 | 是，必须 `BLOCKED_FOR_CLARIFICATION` 或等价 `BLOCKED`，直到澄清/waive/accepted `UNVERIFIED`。 | `specs/change-interviewer/spec.md`, `aili-four-command-lifecycle/spec.md` |
| Q7 | Waiver / UNVERIFIED | 如果用户说“先这样”或“接受风险”，是否允许带 `UNVERIFIED` 进入 BUILD？ | AILI lifecycle 已允许 explicit `UNVERIFIED`，但必须命名风险。 | 允许，但只能在用户明确接受具体未验证项后；最终报告必须列出。 | 保留速度出口；也防止模型把风险伪装成已解决。 | 允许，但只能在用户明确接受具体未验证项后；最终报告必须列出。 | `context.md`, final DEFINE report, `SKILL.md` |
| Q8 | Stress-test usage | 是否将 `strategy-stress-test` 强制用于两个节点：生成 packet 后、吸收答案后？ | 只检查初稿不能发现用户回答里的新歧义。 | 是，两处都强制；失败要修复 packet 或生成 follow-up round。 | 更可靠但多一步；只做一次更轻但不覆盖 answer quality。 | 是，两处都强制；失败要修复 packet 或生成 follow-up round。 | `tasks.md`, `specs/change-interviewer/spec.md` |
| Q9 | Test plan acceptance | 是否确认本 change 的测试应重点验证 prompt/protocol 行为，而不是写自动化运行时测试？ | 这是 Markdown skill 变更；现有自动化主要验证 OpenSpec/fixtures/scripts。 | 是。以 OpenSpec validation、harness fixture checks（若触发）、static inspection、可执行场景表为主。 | 符合仓库现状；新增自动化可能超出范围。 | 是。以 OpenSpec validation、harness fixture checks（若触发）、static inspection、可执行场景表为主。 | `test-plan.md` |
| Q10 | Build readiness | 你是否确认本 DEFINE artifacts（proposal/design/tasks/spec/interview/test-plan）足以作为 BUILD 输入？ | AILI hard stop 要求 spec/questionnaire/test-plan gate 被确认/waived/accepted `UNVERIFIED` 后才能 BUILD。 | 如果接受推荐默认答案，可回复“确认全部推荐默认，进入 BUILD”；否则填写上表。 | 不确认则 BUILD readiness 为 `BLOCKED`；确认后可进入 BUILD 但仍需显式 `/build`。 | 可以 | final DEFINE report |

## 4. 设计漏洞 / 证据缺口 / 反例

| ID | 类型 | 说明 | 建议处理方式 | 状态 |
|---|---|---|---|---|
| L1 | Scope creep risk | 为了提高采访质量，可能顺手改 `strategy-stress-test`、`test-document-generator`、lifecycle docs、README、fixtures，导致 broad harness rewrite。 | BUILD 只改与新协议直接冲突/过时的文件；README/lifecycle/fixtures 仅在 stale 或验证需要时更新。 | open |
| L2 | Missing approval | 新增 skill-local reference 文件需要明确批准，目前未批准。 | 默认内联修改；如 BUILD 发现必须拆分，先停下问。 | open |
| L3 | Counterexample | “全面提问”若不设质量阈值，会产生大量无用问题，恶化用户体验。 | 用 decision-changing threshold 删除不会影响实现准备度的问题。 | addressed in design |
| L4 | Verification gap | Markdown skill 行为很难用单元测试完全证明。 | 用 OpenSpec scenarios、harness fixture/static inspection、test-plan 手工验收场景覆盖。 | open |
| L5 | User decision required | Q1/Q2/Q10 会影响 BUILD edit surface、routing discoverability / skill ownership 边界和 gate state。 | 用户填写或回复“接受推荐默认”。 | open |

## 5. 填写说明

- 可以直接在“你的填写”列里写答案。
- 接受推荐默认答案时，写“同意默认”或直接回复“确认全部推荐默认”。
- 不确定的地方写“不确定”，我会生成下一轮 follow-up，不会开工。
- 不进入本次 scope 的内容写“本次不做”。
- 未填写内容不会被写成事实，只会保留为 `Open Question`。
- 无证据支撑但你愿意继续的内容必须明确标为 `UNVERIFIED`。

## 6. 后续写回映射

| 用户答案 | 将写回到 | 写回方式 |
|---|---|---|
| Q1 | `design.md`, `tasks.md` | 调整新增 reference 文件边界。 |
| Q2 | `proposal.md`, `tasks.md`, possibly README / skill description | 调整 trigger/discoverability scope，并保留 `strategy-stress-test` 的纯方案压测职责。 |
| Q3-Q5 | `specs/change-interviewer/spec.md`, `SKILL.md` | 调整 coverage、question threshold、recommended default 规则。 |
| Q6-Q8 | `specs/change-interviewer/spec.md`, `specs/aili-four-command-lifecycle/spec.md`, `SKILL.md` | 调整 multi-round、readiness、stress-test gate。 |
| Q9 | `test-plan.md`, `tasks.md` | 调整验证策略和必跑命令。 |
| Q10 | `context.md`, final DEFINE report | 形成 BUILD readiness state。 |

## 7. 答案吸收记录

| 问题 | 用户答案 | 形成的决策 | 已写回位置 | 剩余不确定 |
|---|---|---|---|---|
| Q1 | 可以 | BUILD 可在需要时新增 `skills/change-interviewer/references/*`；必须 task-scoped 且无 missing reference。 | `proposal.md`, `design.md`, `tasks.md`, `context.md`, `test-plan.md` | 无 |
| Q2 | 加入 | 加入需求采访/写回导向 grill 触发；纯方案压测仍归 `strategy-stress-test`。 | `proposal.md`, `context.md` | 无 |
| Q3 | 是的 | coverage matrix 必须完整列维度状态，`Not applicable` 写理由。 | specs/design 已覆盖 | 无 |
| Q4 | 接受 | 问题不限数量，但必须 decision-changing，避免泛泛问题。 | specs/design 已覆盖 | 无 |
| Q5 | 是。推荐默认答案要说明证据/理由；证据不足就标为 `Unverified` 或让用户确认。 | 推荐默认答案必须有证据或明确标记不确定性。 | specs/design 已覆盖 | 无 |
| Q6 | 是，必须 `BLOCKED_FOR_CLARIFICATION` 或等价 `BLOCKED`，直到澄清/waive/accepted `UNVERIFIED`。 | 第一轮答案仍有材料性歧义时必须继续追问并阻塞 BUILD。 | specs/design 已覆盖 | 无 |
| Q7 | 允许，但只能在用户明确接受具体未验证项后；最终报告必须列出。 | `UNVERIFIED` 是显式风险接受路径，不等于 confirmed。 | specs/design/context 已覆盖 | 无 |
| Q8 | 是，两处都强制；失败要修复 packet 或生成 follow-up round。 | `strategy-stress-test` 用于 packet 生成后和答案吸收后。 | specs/design/tasks 已覆盖 | 无 |
| Q9 | 是。以 OpenSpec validation、harness fixture checks（若触发）、static inspection、可执行场景表为主。 | 测试策略确认。 | `test-plan.md`, `context.md` | 无 |
| Q10 | 可以 | 当前 DEFINE artifacts 足以作为 BUILD 输入；BUILD readiness 可置为 `READY`。 | `context.md`, final DEFINE report | 无 |

## 8. Stress-test 摘要

- Confidence: high
- Current artifact / claim: 本采访包覆盖了完整改造 `change-interviewer` 所需的范围、证据优先、全面问题、多轮歧义检测、readiness gate、stress-test gate 和验证策略。
- Material loopholes found:
  - [User decision required] Q1/Q2/Q10 影响 BUILD edit surface、触发发现性和 gate state。Status: resolved by filled answers。
  - [Verification gap] Markdown prompt 行为不能完全由自动测试证明。Status: test-plan includes static/manual acceptance checks。
  - [Scope creep risk] 同步更新 peer skills/docs/fixtures 可能扩大范围。Status: tasks constrain updates to stale/conflicting surfaces only。
  - [Skill ownership conflict] “压测设计”触发可能属于 `strategy-stress-test`。Status: Q2 推荐默认已缩窄为需求采访/写回导向，纯方案压测仍归 `strategy-stress-test`。
- Fixes applied: 增加 Q1/Q2/Q10；把 fixture/docs 更新设为条件任务；把无自动化证明风险写入 test-plan。
- Remaining open questions: none for BUILD readiness; README/lifecycle/fixtures 是否需更新留给 BUILD 阶段按 diff/evidence 判断。
- Remaining unverified items: future model behavior cannot be fully automated; BUILD 最终是否需要改 README/lifecycle/fixtures，需实施阶段重读后确认。
- Evidence used: 本文件第 1 节证据表；`proposal.md`；`design.md`；`tasks.md`；OpenSpec delta。
- Safe to proceed: yes for BUILD readiness after explicit `/build` or equivalent implementation approval; no material ambiguity remains in the filled interview.
