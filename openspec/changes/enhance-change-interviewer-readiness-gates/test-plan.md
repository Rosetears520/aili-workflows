# 测试文档：enhance-change-interviewer-readiness-gates

## 0. 文档元信息

- 来源：`openspec/changes/enhance-change-interviewer-readiness-gates/`
- 生成时间：2026-06-12
- 适用版本 / 分支：`feature/aili-cli-plugin-installer` 当前工作树
- 测试负责人：ROSE / BUILD 阶段验证者
- 状态：draft

## 1. 资料来源与证据

| 来源 | 已检查内容 | 观察到的事实 | 置信度 | 备注 |
|---|---|---|---|---|
| `proposal.md` | Why / What Changes / Non-Goals | change 目标是完整改造 `change-interviewer` 的采访质量、multi-round、ambiguity gate 和 evidence-first rules；不新增顶层命令。 | high | 定义测试范围。 |
| `design.md` | Proposed Design / Risks | 设计要求 coverage matrix、question quality、answer classification、readiness state、stress-test gate。 | high | 转为测试矩阵。 |
| `tasks.md` | implementation checklist | BUILD 任务限制默认不新增 reference，按需更新 README/lifecycle/fixtures，验证命令明确。 | high | 转为执行检查。 |
| `specs/change-interviewer/spec.md` | ADDED requirements | 定义全面 coverage、actionable questions、multi-round answer ingestion、stress-test、readiness states。 | high | 核心验收来源。 |
| `specs/aili-four-command-lifecycle/spec.md` | MODIFIED requirement | 填完但仍有歧义的 questionnaire 不满足 BUILD gate。 | high | lifecycle regression coverage。 |
| `skills/change-interviewer/SKILL.md` | current implementation target | 当前 skill 已有 evidence table、packet template、stress-test、ingestion，但缺少强制多轮/全面/answer gate。 | high | BUILD 前后对照。 |

## 2. 被测对象与测试目标

- 被测对象：`change-interviewer` skill protocol and related DEFINE/BUILD gate documentation.
- 用户目标：采访包全面、有用、多轮；用户答案有歧义时不开始实现。
- 业务目标：降低 harness/spec implementation drift，避免弱问卷导致错误 BUILD。
- 技术目标：OpenSpec delta valid；skill prompt contains enforceable rules; lifecycle gate stays strict.
- 不测试内容：真实 LLM 行为的全自动端到端证明；新增 public command；依赖/installer/memory/schema 行为。

## 3. 测试范围

### In Scope

- OpenSpec artifact structural validation.
- Static inspection of changed `SKILL.md` / related docs for required protocol clauses.
- Regression check that no public top-level command is introduced.
- Verification that any touched `references/*` paths exist, or no new references are added without approval.
- Manual acceptance scenarios for packet generation and filled-answer ingestion behavior.

### Out of Scope

- Automated proof that every future model invocation follows the prompt perfectly.
- Browser/UI/E2E tests.
- Dependency, lockfile, installer, or memory DB testing unless unexpectedly touched.

### Assumptions

- Markdown prompt/protocol changes are primarily verified by OpenSpec validation, static inspection, fixture checks when applicable, and manual scenario review.
- BUILD will read disk state fresh before editing because current working tree already contains unrelated uncommitted changes.

### Confirmed Decisions

- User approves adding `skills/change-interviewer/references/*` if needed for maintainability and all references exist.
- Test strategy is OpenSpec validation plus static/manual prompt acceptance, with fixture/script checks only when touched surfaces require them.

### Open Questions

- Whether README/lifecycle/fixtures become stale after implementation; BUILD must decide from diff/evidence.

## 4. 需求-测试追踪矩阵

| 需求 / 决策 / 风险 | 来源 | 测试点 | 测试类型 | 优先级 | 覆盖状态 |
|---|---|---|---|---|---|
| Comprehensive coverage matrix | `specs/change-interviewer/spec.md` | Changed `SKILL.md` lists coverage dimensions and classification states. | Static inspection | P0 | planned |
| Evidence-first before asking | `specs/change-interviewer/spec.md` | Protocol says code/docs/specs/tests/configs/official docs are checked before user questions. | Static inspection / manual scenario | P0 | planned |
| Decision-changing questions only | `specs/change-interviewer/spec.md` | Protocol rejects generic questions and requires why/impact/default/trade-off/write-back fields. | Static inspection | P0 | planned |
| Multi-round answer ingestion | `specs/change-interviewer/spec.md` | Protocol re-reads filled answers and generates follow-up rounds for ambiguity/contradiction. | Static inspection / manual scenario | P0 | planned |
| Ambiguity blocks BUILD | `specs/aili-four-command-lifecycle/spec.md` | Lifecycle/questionnaire guidance reports `BLOCKED` when filled answers remain ambiguous. | OpenSpec validation / static inspection | P0 | planned |
| Stress-test packet and answer set | `design.md`, `specs/change-interviewer/spec.md` | Protocol requires `strategy-stress-test` after packet generation and answer ingestion. | Static inspection | P0 | planned |
| No new public command | `proposal.md` | Diff does not add command files or advertise `/grill` as top-level command. | Diff inspection | P0 | planned |
| No missing references | `skill-routing-boundaries` | Any new skill-local path exists; if not approved, no new reference file is created. | Static inspection | P1 | planned |

## 5. 测试策略

- 单元测试：Not applicable unless Python/scripts are touched.
- 集成测试：OpenSpec strict validation for change package.
- E2E / 浏览器测试：Not applicable.
- API / 契约测试：OpenSpec spec scenarios serve as contract tests.
- 手工验收：Review prompt text against scenario checklist below.
- 回归测试：Run harness fixture checks if routing/lifecycle/command/fixture files are touched.
- 非功能测试：Security/privacy through static inspection: no secrets/raw transcripts; no copied upstream text; no new dependencies.

## 6. 测试环境与测试数据

- 环境：local repo `/mnt/d/works/aili-workflow`.
- 依赖服务：none.
- 测试账号 / 权限：none.
- 测试数据：OpenSpec artifacts and hypothetical interview inputs.
- 数据清理方式：No generated temp artifacts expected; remove only artifacts created by this change if rollback is needed.

## 7. 功能测试用例

| ID | 场景 | 前置条件 | 步骤 | 预期结果 | 优先级 | 自动化建议 | 来源 |
|---|---|---|---|---|---|---|---|
| FT-01 | Generate comprehensive packet | BUILD has updated `change-interviewer` | Inspect packet template/protocol | Packet requires coverage matrix and all material dimensions classified. | P0 | Static/manual | R1 |
| FT-02 | Avoid evidence-answerable questions | Input references existing docs/specs | Inspect Phase A / question rules | Skill instructs agent to inspect evidence and not ask user for discoverable facts. | P0 | Static/manual | R1 |
| FT-03 | Recommended default is grounded | Question includes default | Inspect question rules | Default includes evidence/rationale or is marked `Unverified` / requires user confirmation. | P0 | Static/manual | R2 |
| FT-04 | Filled ambiguous answer blocks | User answer says “按情况处理” for failure behavior | Inspect ingestion protocol | Answer classified ambiguous; follow-up generated; no write-back as fact; readiness `BLOCKED`. | P0 | Manual scenario | R3 |
| FT-05 | Contradiction with repo evidence blocks | User answer conflicts with current spec | Inspect ingestion protocol | Conflict recorded; asks clarification or marks `UNVERIFIED` only with explicit acceptance. | P0 | Manual scenario | R3 |
| FT-06 | Waiver path is explicit | User explicitly says “accept UNVERIFIED item X” | Inspect readiness reporting | Readiness can be `UNVERIFIED` and final report names item X. | P1 | Manual scenario | R5 |
| FT-07 | No public command introduced | Final diff exists | Inspect `commands/` and skill descriptions | No new `/grill` or other top-level lifecycle command appears. | P0 | Diff inspection | Non-goal |

## 8. 异常、边界与权限测试

| ID | 类型 | 场景 | 输入 / 操作 | 预期结果 | 风险 |
|---|---|---|---|---|---|
| ET-01 | Missing placement | Non-OpenSpec source has no target | Invoke skill contract mentally/static | Placement question remains required before writing. | Wrong artifact location |
| ET-02 | Too many generic questions | Coverage dimension is irrelevant | Inspect rules | Dimension marked `Not applicable`; no useless question asked. | Interview fatigue |
| ET-03 | Unsupported default | No evidence supports recommendation | Inspect rules | Default is not stated as fact; marked `Open Question` or `Unverified`. | False certainty |
| ET-04 | New missing reference | BUILD adds `references/foo.md` mention | Inspect final diff | File exists or change is rejected. | Broken skill resource |
| ET-05 | Dirty tree contamination | Existing unrelated changes present | Inspect final diff paths | Only task-scoped paths are modified by this change. | Mixing unrelated work |

## 9. 数据一致性 / 迁移 / 兼容性测试

- No data migration expected.
- Compatibility: existing OpenSpec deterministic placement and non-OpenSpec placement question must remain unchanged.
- Existing `interview.md` packet sections should remain compatible or be superseded with a documented richer structure.

## 10. 性能、稳定性、安全、可观测性测试

- Performance: packet may be longer; verify rules exclude non-decision-changing questions to control size.
- Reliability: strict readiness states reduce accidental BUILD from ambiguous requirements.
- Security/privacy: verify no raw sessions, secrets, copied upstream text, or external sensitive data are added.
- Observability: readiness report names `READY`, `BLOCKED`, `WAIVED`, or `UNVERIFIED` and lists blockers.

## 11. 回归范围

- `change-interviewer` output placement and answer write-back behavior.
- AILI DEFINE/BUILD questionnaire gate language.
- Skill routing boundary: no new top-level commands; no missing references.
- README or docs only if touched.

## 12. 自动化验证命令

| 层级 | 命令 | 目的 | 必须执行 | 备注 |
|---|---|---|---|---|
| OpenSpec | `openspec validate enhance-change-interviewer-readiness-gates --strict` | Validate change package | yes | DEFINE and BUILD |
| CLI | `python scripts/harness_fixture_check.py` | Validate command/routing fixtures | conditional | Run if lifecycle/commands/fixtures touched |
| CLI | `python scripts/agents_md.py check --project .` | Validate AGENTS template compliance | conditional | Run if AGENTS/templates touched |
| Typecheck | `python -m py_compile scripts/harness_fixture_check.py scripts/agents_md.py` | Validate Python helper syntax | conditional | Run if scripts touched |
| Static | `git diff -- openspec/changes/enhance-change-interviewer-readiness-gates skills/change-interviewer` | Scope and prompt inspection | yes | Include related touched files |

## 13. 手工验收清单

- [ ] `change-interviewer` requires comprehensive coverage classification.
- [ ] Each question must include why / impact / recommended default / trade-off / answer slot / write-back target.
- [ ] Evidence-first rule is preserved and stronger than before.
- [ ] Filled ambiguous answers trigger follow-up and `BLOCKED`, not write-back as facts.
- [ ] `strategy-stress-test` runs after packet generation and answer ingestion.
- [ ] Final report can distinguish `READY`, `BLOCKED`, `WAIVED`, and `UNVERIFIED`.
- [ ] No new public top-level command is introduced.
- [ ] No missing skill-local reference path is introduced.

## 14. Open Questions / Unverified

| 类型 | 内容 | 影响 | 处理方式 |
|---|---|---|---|
| Open Question | Whether README/lifecycle/fixtures need updates. | Verification scope. | Decide from BUILD diff/evidence. |
| Unverified | Exact behavior quality of future model invocations cannot be fully automated. | Residual prompt-following risk. | Static/manual acceptance plus future SHIP review. |

## 15. 测试执行记录

| Run ID | 时间 | 执行者 | 测试层级 | 命令 / 工具 | 结果 | 关键证据 | 未验证项 |
|---|---|---|---|---|---|---|---|
| BUILD-01 | 2026-06-12 | test-engineer | OpenSpec | `openspec validate enhance-change-interviewer-readiness-gates --strict` | PASS | `Change 'enhance-change-interviewer-readiness-gates' is valid` | Future model adherence cannot be fully automated. |
| BUILD-02 | 2026-06-12 | test-engineer | CLI fixture | `python scripts/harness_fixture_check.py` | PASS | `harness fixture check: PASS (5 fixture files + command contracts)` | None for fixture scope. |
| BUILD-03 | 2026-06-12 | test-engineer | AGENTS compliance | `python scripts/agents_md.py check --project .` | PASS | Exit 0. Run because broader dirty tree includes template/agent-script changes outside this task. | This does not validate future prompt-following behavior. |
| BUILD-04 | 2026-06-12 | test-engineer | Python syntax | `python -m py_compile scripts/harness_fixture_check.py scripts/agents_md.py` | PASS | Exit 0, no output. Run because broader dirty tree includes Python script changes outside this task. | This task did not modify Python. |
| BUILD-05 | 2026-06-12 | test-engineer | Static acceptance | Section 13 checklist vs `skills/change-interviewer/SKILL.md` | PASS | Coverage matrix, question fields, evidence-first, ambiguity blocking, dual stress-test gates, readiness states, no public command, no missing references all checked. | Future model adherence cannot be fully automated. |

## 16. 缺陷与修复闭环

| Bug ID | 来源测试 | 现象 | 根因 | 修复负责人 | 修复文件 | 复测命令 | 复测结果 | 状态 |
|---|---|---|---|---|---|---|---|---|

## 17. 变更记录

- 2026-06-12: Initial DEFINE test document generated through `test-document-generator` contract.
