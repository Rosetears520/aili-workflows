# 测试文档：add-explain-retrospective-skills

## 0. 文档元信息

- 来源：`openspec/changes/add-explain-retrospective-skills/`
- 生成时间：2026-06-03
- 适用版本 / 分支：`feature/explain-retrospective-skills`
- 测试负责人：ROSE / user review before BUILD
- 状态：BUILD execution recorded; one template check failed because project root `AGENTS.md` is absent

## 1. 资料来源与证据

| 来源 | 已检查内容 | 观察到的事实 | 置信度 | 备注 |
|---|---|---|---|---|
| `proposal.md` | scope / impact | 一个 OpenSpec 提案包含两个新 skills、backend-neutral `implementation-notes.html`、`templates/AGENTS.md` guardrails、README attribution；不新增 command/subagent；不提交 raw session evidence。 | high | 主范围。 |
| `design.md` | decisions / risks / migration | self-improvement 是 evidence-scoped + report-first；Rule 6 改为 DCP-aware task-continuity checkpoint；HTML notes 是 supplemental artifact。 | high | 已按用户 DCP 修正更新。 |
| `tasks.md` | implementation checklist | BUILD 需创建 notes、更新 template、创建 skills、更新 README、验证 routing/safety、运行 repo checks。 | high | 尚未执行。 |
| `specs/explain-by-allegory/spec.md` | behavior requirements | allegory skill 需触发于 story/analogy explanation，输出 allegory + formal mapping + boundaries；不得替代 implementation/source/spec workflows。 | high | 可用 prompt validation。 |
| `specs/evidence-scoped-retrospective/spec.md` | behavior/safety requirements | retrospective skill 只分析 explicit evidence；session data untrusted/sensitive；分类 failure patterns；report-first；raw sessions 不提交。 | high | 需安全与 routing tests。 |
| `specs/implementation-notes/spec.md` | artifact requirements | approved spec-backed implementation 开始时维护 `implementation-notes.html`；OpenSpec 默认在 change dir；非 OpenSpec 放 active spec/task 旁或询问路径；不存 raw logs/secrets。 | high | 需文件内容检查。 |
| `specs/agent-operating-discipline/spec.md` | template requirements | `templates/AGENTS.md` 加 compact failure guards；context discipline 使用 DCP-aware task-continuity triggers，不依赖 raw percentage gates。 | high | 需 template validation。 |
| `interview.md` | open questions | 仍有 7 个用户确认问题，包含是否拆提案、HTML 最低结构、session export 临时路径、attribution、retrospective proposal 边界、checkpoint 强制程度、BUILD gate。 | high | BUILD readiness 受影响。 |

## 2. 被测对象与测试目标

- 被测对象：两个新 skills、README updates、`templates/AGENTS.md` managed block、`implementation-notes.html` artifact convention、OpenSpec artifacts。
- 用户目标：把 allegory prompting 与 evidence-scoped workflow self-improvement 安全纳入 OpenCode workflow。
- 业务目标：提高解释质量、复盘质量、执行期纪律和 implementation continuity，同时避免 raw session evidence 泄露或自动自改。
- 技术目标：新增 artifacts 与 routing rules 符合本仓库 skill / harness / OpenSpec 约定。
- 不测试内容：真实 OpenCode session export 大规模分析、真实 subagent 新增、真实 command 新增、生产部署。

## 3. 测试范围

### In Scope

- `skills/explain-by-allegory/SKILL.md` frontmatter、trigger、workflow、boundary、output contract。
- `skills/evidence-scoped-retrospective/SKILL.md` evidence scope、session safety、failure taxonomy、report-first routing、non-commit boundary、把 `implementation-notes.html` 作为 evidence source 而非 mandatory rule owner。
- `templates/AGENTS.md` managed operating-discipline block updates, mandatory `implementation-notes.html` execution discipline, and generated `AGENTS.md` validation.
- `implementation-notes.html` creation, structure, update triggers, safety boundary, supplemental status.
- README inventory/source attribution updates.
- OpenSpec validation and diff inspection.

### Out of Scope

- Adding a new subagent.
- Adding a new top-level command.
- Committing raw session exports or transcript evidence.
- Copying upstream prompt/article text.
- Changing memory schema, install flow, or OpenCode config unless separately approved.

### Assumptions

- User will either answer `interview.md` or explicitly accept defaults / waive unresolved questions before BUILD.
- The implementation branch can edit tracked workflow files after BUILD approval.
- `scripts/agents_md.py check --project .` is available for template validation.

### Open Questions

- Test-plan acceptance remains pending until the user confirms coverage, requests edits, or explicitly waives/accepts remaining `Unverified` items.

## 4. 需求-测试追踪矩阵

| 需求 / 决策 / 风险 | 来源 | 测试点 | 测试类型 | 优先级 | 覆盖状态 |
|---|---|---|---|---|---|
| Allegory skill triggers only for explanation-by-story requests | `specs/explain-by-allegory/spec.md` | Positive/negative prompt routing table | Manual / review | P1 | planned |
| Allegory output includes story, mapping, formal explanation, limits | `specs/explain-by-allegory/spec.md` | Inspect SKILL workflow/output contract | Static review | P1 | planned |
| Retrospective uses only explicit evidence | `specs/evidence-scoped-retrospective/spec.md` | Prompt asks for global history with no exports; expected ask/Unverified | Manual / review | P1 | planned |
| Session data treated as sensitive/untrusted | `specs/evidence-scoped-retrospective/spec.md` | Inspect safety boundaries; negative prompt attempts to commit session JSON | Static + manual | P1 | planned |
| Failure taxonomy present but not copied article text | `design.md`, `specs/evidence-scoped-retrospective/spec.md` | Diff/source review for copied long upstream text | Static review | P1 | planned |
| Retrospective is report-first for protected surfaces | `specs/evidence-scoped-retrospective/spec.md` | Inspect routing to `skill-authoring-and-validation`, `harness-evolution`, `rose-memory` | Static review | P1 | planned |
| `implementation-notes.html` backend-neutral behavior | `specs/implementation-notes/spec.md` | Inspect skill/template text and this change's notes file | Static review | P1 | planned |
| `implementation-notes.html` excludes raw logs/secrets | `specs/implementation-notes/spec.md` | Inspect file content and final diff | Static/security review | P1 | planned |
| AGENTS guardrails are compact and DCP-aware | `specs/agent-operating-discipline/spec.md` | Inspect `templates/AGENTS.md`; ensure no 70/85 primary gate remains | Static review | P1 | planned |
| Generated AGENTS template remains valid | `proposal.md`, `design.md` | `python scripts/agents_md.py check --project .` | CLI | P1 | planned |
| README includes inventory and attribution without copying | `proposal.md`, `tasks.md` | Static README diff review | Static review | P2 | planned |
| No top-level command/subagent/session JSON added | `proposal.md` | Final diff inspection | Static review | P1 | planned |

## 5. 测试策略

- 单元测试：N/A for Markdown-only skill/template changes unless scripts are added unexpectedly.
- 集成测试：Run AGENTS template check after template edits.
- E2E / 浏览器测试：N/A.
- API / 契约测试：OpenSpec status/validation for change artifacts.
- 手工验收：Prompt routing validation and content boundary review.
- 回归测试：Ensure existing lifecycle command model remains unchanged; no new top-level commands or subagents.
- 非功能测试：Security/privacy diff inspection for raw sessions, secrets, long copied upstream text.

## 6. 测试环境与测试数据

- 环境：local repository `/mnt/d/works/aili-workflow` on branch `feature/explain-retrospective-skills`.
- 依赖服务：OpenSpec CLI, Python scripts.
- 测试账号 / 权限：N/A.
- 测试数据：validation prompts; no real session exports committed.
- 数据清理方式：Do not create raw session artifacts; delete any accidental temp files before completion.

## 7. 功能测试用例

| ID | 场景 | 前置条件 | 步骤 | 预期结果 | 优先级 | 自动化建议 | 来源 |
|---|---|---|---|---|---|---|---|
| TC-F-001 | Allegory skill positive routing | Skill file exists | Review description against prompt “用寓言解释 embeddings，并说明类比失效点” | Description clearly triggers; workflow produces allegory, mapping, formal explanation, limits | P1 | manual | `specs/explain-by-allegory/spec.md` |
| TC-F-002 | Allegory skill negative routing | Skill file exists | Review prompt “Implement vector search using current LangChain docs” | Skill excludes primary routing; source/implementation workflow is preferred | P1 | manual | `specs/explain-by-allegory/spec.md` |
| TC-F-003 | Retrospective positive routing | Skill file exists | Review prompt “Here are sanitized OpenCode exports; find workflow mistakes with evidence” | Skill triggers and requires evidence scope declaration | P1 | manual | `specs/evidence-scoped-retrospective/spec.md` |
| TC-F-004 | Retrospective unsupported global-history claim | Skill file exists | Review prompt “Analyze your last 30 days of work” with no evidence | Skill asks for evidence or marks history claim `Unverified` | P1 | manual | `specs/evidence-scoped-retrospective/spec.md` |
| TC-F-005 | Retrospective raw session commit refusal | Skill file exists | Review prompt “Commit this exported session log” | Skill refuses/redirects; raw exports not committed | P1 | manual | `specs/evidence-scoped-retrospective/spec.md` |
| TC-F-006 | Implementation notes OpenSpec path | BUILD begins | Create/update notes for this change | `openspec/changes/add-explain-retrospective-skills/implementation-notes.html` exists with required sections | P1 | static | `specs/implementation-notes/spec.md` |
| TC-F-007 | AGENTS DCP-aware guardrail | Template updated | Inspect operating-discipline block | Uses task-continuity triggers; no primary 70/85 percentage rule; no absolute token limits | P1 | static | `specs/agent-operating-discipline/spec.md` |
| TC-F-008 | README attribution | README updated | Inspect attribution notes | Mentions inspirations conceptually; no copied long prompt/article text; inaccessible X content not overstated | P2 | static | `tasks.md` |

## 8. 异常、边界与权限测试

| ID | 类型 | 场景 | 输入 / 操作 | 预期结果 | 风险 |
|---|---|---|---|---|---|
| TC-E-001 | Security | Session export includes secret-like text | Final diff/search review | No raw session content or secret is committed | Data leakage |
| TC-E-002 | Scope | Implementation adds subagent despite MVP non-goal | Final diff review | No `agents/session-retrospective-scout.md` or README agent entry unless separately approved | Scope creep |
| TC-E-003 | Command boundary | Implementation adds `/retrospective` command | Final diff review | No new top-level command | Lifecycle violation |
| TC-E-004 | DCP semantics | Template still says 70%/85% as primary gates | Static review | Block until replaced by task-continuity risk wording | Misleading runtime rule |
| TC-E-005 | Notes artifact | `implementation-notes.html` includes raw logs/transcripts | Static review | Block until summarized/redacted | Sensitive/high-volume evidence |
| TC-E-006 | Over-trigger | `explain-by-allegory` description catches generic implementation prompts | Prompt validation | Narrow description/exclusions required | Routing noise |

## 9. 数据一致性 / 迁移 / 兼容性测试

- No database migration expected.
- No install migration expected.
- Confirm any generated root `AGENTS.md` behavior remains compatible with `scripts/agents_md.py`.
- Confirm OpenSpec artifacts remain readable and no required OpenSpec structure is broken.

## 10. 性能、稳定性、安全、可观测性测试

- Performance: N/A.
- Stability: Ensure guardrails do not create infinite checkpoint loops; DCP-aware triggers require concrete continuity risk.
- Security: diff inspection for secrets/raw sessions/copied private content.
- Observability: `implementation-notes.html` and test execution records provide human-readable continuation evidence.

## 11. 回归范围

- Existing four-command lifecycle remains unchanged.
- Existing skill routing authority remains skill-driven and natural-language based.
- Existing harness-evolution approval gates remain intact.
- Existing memory rules still prohibit raw transcript/log storage.
- Existing AGENTS template generated block remains structurally valid.

## 12. 自动化验证命令

| 层级 | 命令 | 目的 | 必须执行 | 备注 |
|---|---|---|---|---|
| OpenSpec | `openspec status --change add-explain-retrospective-skills` | Confirm artifacts are recognized | yes | DEFINE and after implementation |
| OpenSpec | `openspec validate add-explain-retrospective-skills --strict` | Strict spec validation if available | yes | If command unsupported, record failure and use status/static inspection |
| Template | `python scripts/agents_md.py check --project .` | Validate `templates/AGENTS.md` / generated AGENTS consistency | yes | After template edit |
| Syntax | `python -m py_compile scripts/harness_fixture_check.py scripts/agents_md.py` | Ensure touched validation scripts still compile if relevant | no | Run if scripts are touched or repo requires |
| Diff | `git status --short --branch` and scoped diff inspection | Confirm no raw sessions/unrelated files | yes | Before completion |

## 13. 手工验收清单

- [x] User confirms or waives `interview.md` open questions.
- [x] User confirms `test-plan.md` coverage is sufficient or accepts `Unverified` items.
- [x] Trigger validation examples for both skills pass review.
- [x] `implementation-notes.html` exists and contains only concise safe rationale.
- [x] `templates/AGENTS.md` guardrails are compact and DCP-aware.
- [x] README attribution is conceptual and does not copy upstream text.
- [x] Final diff contains no raw session exports, transcript dumps, secrets, new commands, or new subagents.

## 14. Open Questions / Unverified

| 类型 | 内容 | 影响 | 处理方式 |
|---|---|---|---|
| Confirmed | Keep one proposal | Review/build packaging | Execute BUILD as separate packages inside one proposal |
| Confirmed | Exact minimum HTML structure for `implementation-notes.html` | Implementation consistency | Use simple static no-JS/no-external-CSS HTML with required sections |
| Confirmed | Whether to add ignored repo-local session export folder | Evidence handling | MVP adds no new folder; do not place raw exports in repo |
| Unverified | Direct X source content | Attribution precision | Use conceptual/user-provided summary only |
| Open Question | Test-plan acceptance / BUILD gate confirmation | Whether BUILD may start | User confirms, waives, or accepts Unverified |

## 15. 测试执行记录

| Run ID | 时间 | 执行者 | 测试层级 | 命令 / 工具 | 结果 | 关键证据 | 未验证项 |
|---|---|---|---|---|---|---|---|
| DEFINE-001 | 2026-06-03 | ROSE | Artifact generation | Read OpenSpec files; generated `interview.md` and `test-plan.md` | draft | Files created under change dir | User confirmation pending |
| BUILD-001 | 2026-06-03 | implementer | Static / routing validation | Read `skills/explain-by-allegory/SKILL.md`, `skills/evidence-scoped-retrospective/SKILL.md`, `templates/AGENTS.md`, README diff, implementation notes | pass | Frontmatter names match folders; descriptions narrow trigger scope; retrospective routes skill/harness/memory edits through required gates; notes behavior covers OpenSpec, Superpowers-style, and custom backends | Direct X content not fetched |
| BUILD-002 | 2026-06-03 | implementer | Template check | `python scripts/agents_md.py check --project .` | fail | Command returned `FAIL: AGENTS.md does not exist: /mnt/d/works/aili-workflow/AGENTS.md` | Root `AGENTS.md` creation was outside approved edit scope |
| BUILD-003 | 2026-06-03 | implementer | OpenSpec | `openspec status --change add-explain-retrospective-skills`; `openspec validate add-explain-retrospective-skills --strict` | pass | Status reports 4/4 artifacts complete; strict validate reports change is valid | none |
| BUILD-004 | 2026-06-03 | implementer | Diff / safety inspection | `git status --short --branch`; scoped diff/static search | pass with note | No new command files found; no new subagent files beyond pre-existing `agents/`; scoped diff only updates approved README/template and adds approved change/skill artifacts | Pre-existing untracked `.opencode/` and `docs/research/` remain untouched |
| BUILD-005 | 2026-06-03 | ROSE | Template check | `python scripts/agents_md.py check --project .`; temp-project `init` + `check --allow-placeholders` | partial | Project check fails because root `AGENTS.md` is absent on this branch; temp-project generated AGENTS from `templates/AGENTS.md` passes managed-block/marker validation with placeholders allowed | Whether root `AGENTS.md` should be generated for this repo is outside this BUILD scope |
| BUILD-006 | 2026-06-03 | ROSE | OpenSpec / task state | `openspec instructions apply --change add-explain-retrospective-skills --json`; status/strict validate | pass | OpenSpec reports 19/19 tasks complete and strict validate passes | none |
| BUILD-007 | 2026-06-03 | ROSE | Static review | User-language update for `implementation-notes.html` | pass | Spec/design/skill text now require user-language default; current notes artifact is `lang="zh-CN"` and written in Chinese | Direct X content remains Unverified; root `AGENTS.md` generation decision remains out of scope |
| BUILD-008 | 2026-06-03 | ROSE | Static review | Move mandatory notes ownership from retrospective skill to AGENTS template | pass | `templates/AGENTS.md` now owns mandatory spec-backed implementation notes discipline; `evidence-scoped-retrospective` now treats notes as evidence and reports missing required notes as a process gap | Root `AGENTS.md` generation decision remains out of scope |

## 16. 缺陷与修复闭环

| Bug ID | 来源测试 | 现象 | 根因 | 修复负责人 | 修复文件 | 复测命令 | 复测结果 | 状态 |
|---|---|---|---|---|---|---|---|---|

## 17. 变更记录

| 日期 | 变更 | 作者 |
|---|---|---|
| 2026-06-03 | Initial DEFINE test plan generated from current OpenSpec proposal/design/specs/tasks/interview. | ROSE |
| 2026-06-03 | Added BUILD validation records after implementation and ROSE reconciliation. | ROSE |
| 2026-06-03 | Added user-language default verification for `implementation-notes.html`. | ROSE |
| 2026-06-03 | Corrected `implementation-notes.html` ownership: mandatory rule belongs to `templates/AGENTS.md`; retrospective skill only consumes notes as evidence. | ROSE |
