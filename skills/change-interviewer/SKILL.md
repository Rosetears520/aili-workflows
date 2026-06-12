---
name: change-interviewer
description: Generate a source-grounded Chinese requirements interview packet for unclear changes, specs, plans, issues, or user-provided drafts; use repository code/docs, existing specs, official or web sources before asking; grill only for decision-changing requirements/write-back readiness; stress-test packets and filled answers before writing confirmed answers into agreed artifacts.
---

# Change Interviewer

## Purpose

Use this skill to turn an incomplete change idea or draft into an implementable, reviewable change package.

The input can be an OpenSpec change directory, a Superpowers-style plan, a user-pasted paragraph, an issue, a ticket, or one or more custom files. The output should preserve the user's intent, clarify unknowns through interview questions, and persist refined content only to the agreed target files.

## Interview Packet Language

Interview packets are user-facing thinking artifacts. In chat, write them in Simplified Chinese by default for readability and decision traceability.

Keep these items in English or original form:

- file paths
- command names
- code symbols
- API names
- config keys
- OpenSpec requirement headers
- exact source terms

Before persisting an interview packet to the repository, follow the repository's document language convention or ask the user. If no English-only convention exists, persisting the Chinese packet is allowed.

## When to Use

Use this skill when the user wants to refine a change before implementation, especially when the source material is ambiguous, incomplete, or spread across files.

Realistic trigger prompts:

- "Interview me and turn this rough idea into tasks/design/acceptance criteria."
- "Use this Superpowers plan as input and ask what is missing before writing it back."
- "Refine `docs/change.md` with questions first; do not guess requirements."
- "Complete this OpenSpec change package after interviewing me."
- "Grill this requirement / interview packet before write-back or BUILD readiness."
- "I filled `interview.md`; check whether the answers are clear enough to write back."

## When Not to Use

Do not use this skill for:

- implementing the change after requirements are clear
- broad product brainstorming with no intent to produce a change package
- pure plan, design, spec, review, or completion-claim stress-testing with no requirements-interview or write-back target; use `strategy-stress-test` directly
- initializing project-level agent rules or OpenCode setup docs
- rewriting a document without interviewing or preserving author intent
- OpenSpec validation only, with no requirements refinement needed

Non-trigger prompt:

- "Implement task 3 from the accepted plan." Use `incremental-implementation` and `test-driven-development` instead.

## Inputs and Target

First identify the source and persistence target.

Possible sources:

- OpenSpec: `openspec/changes/<change-id>/`
- Superpowers-style plan or task file
- issue, ticket, PR description, pasted user text, or meeting notes
- custom files named by the user

Possible targets:

- the same source files
- a new or existing change document such as `proposal.md`, `design.md`, `tasks.md`, or `acceptance.md`
- OpenSpec files under `openspec/changes/<change-id>/`
- chat-only output, only when the user explicitly selects it

Only OpenSpec change directories have deterministic no-question file output. For every non-OpenSpec source, including a single source document with an obvious sibling path, ask one concise placement question before writing.

## Output Placement Contract

Packet Mode defaults to file output, not chat-first output.

### Quick Reference Flow

```text
source-ground -> resolve placement -> draft packet -> 🔴 stress-test -> repair -> persist -> concise summary
filled answers -> disk re-read -> answer classification -> 🔴 stress-test -> readiness state -> incorporation log -> 🔴 write-back target check -> merge into agreed files -> validate
```

Generate the interview packet, run the stress-test pass, repair the packet, persist the final packet, then summarize the generated path in chat. Do not print the full packet in chat unless the user explicitly asks for chat-only output, writing is blocked by permissions or missing workspace access, or the user chooses chat-only output after the placement question.

OpenSpec change output is the only deterministic no-question placement. For every non-OpenSpec source, ask where to place the output before writing; chat-only is an explicit user-selected fallback.

🔴 STOP before writing when placement is not deterministic: for any non-OpenSpec source, missing workspace access, ambiguous target, existing target ownership conflict, or user-pasted text with no path, ask the placement question and wait. Do not choose a path silently.

Target path resolution:

1. If the source is an OpenSpec change directory, write `openspec/changes/<change-id>/interview.md` without asking.
2. If the source is non-OpenSpec, ask where to place the output before writing, even when the source is a single document:
   - A. create a sibling Markdown file beside the main source file;
   - B. create a sibling folder beside the source directory;
   - C. append a new section to the existing spec/design document;
   - D. print the result in chat only.
3. If the user pasted only free-form text and no source path exists, ask whether to:
   - A. create a new file in a user-specified location;
   - B. append to an existing spec/document;
   - C. print in chat only.
4. If the user explicitly says "print in chat", "do not create files", or "chat only", do not write files.

Use this concise placement question for non-OpenSpec sources:

```text
这个非 OpenSpec 输出需要先确认落点，你选一个：
A. 生成在源文件同级：<path>
B. 在源目录同级新建文件夹：<path>
C. 追加到现有 spec / design 文档末尾
D. 只打印在对话框，不写文件
```

Chat response after persistence should include only:

- generated file path
- source files reviewed
- number of questions
- unresolved `Open Question` / `Unverified` count
- interview readiness state: `READY`, `BLOCKED`, `WAIVED`, or `UNVERIFIED`
- suggested next action

## Interview Modes

Use Packet Mode by default for non-trivial changes:

- generate the Chinese interview packet
- let the user fill it
- ingest answers later

Use Interactive Mode only when:

- the change is small
- one answer materially changes the next question
- the user explicitly wants chat-based interviewing

In Interactive Mode, ask one question at a time.

In Packet Mode, do not interrupt the packet with chat-style single-question turns unless a blocking target or persistence decision is missing.

## Non-Negotiables

- Do not fill in requirements, design, or acceptance criteria by guessing.
- Ask or include questions according to the selected interview mode; record unresolved items as `Open Question:`.
- Preserve existing author content and structure whenever possible.
- If restructuring is necessary, keep original text under `## Appendix: Original Draft` in the same file.
- Never record unconfirmed information as fact. Use `Assumption:` only when the user has accepted it as a working assumption.
- Keep source-specific formats intact, especially OpenSpec requirement headers and scenarios.

## Phase A: Source Grounding

Before generating questions:

1. Read the user-provided source text or files.
2. If the source is an OpenSpec change directory, inventory `tasks.md` or `task.md`, `proposal.md`, `design.md`, and `specs/` files.
3. If the source is a plan, issue, ticket, PR description, or custom file, identify existing sections, task markers, requirements, acceptance criteria, and unresolved assumptions.
4. If repository evidence is needed and the search would be broad or noisy, dispatch `code-scout` as a read-only evidence locator.
5. If external behavior matters, inspect official docs or current web sources before asking the user.
6. Build a concise evidence table that separates Observed Fact, External Source, Inference, Assumption, Open Question, and Unverified.

Do not ask the user for information that can be reliably discovered from current code, docs, specs, tests, configs, or official sources.

Common gaps:

- unclear goal, user, or success criteria
- missing in-scope and out-of-scope boundary
- incomplete happy path, failure path, retry, rollback, or migration flow
- undefined interfaces, API shapes, events, auth, errors, or versioning
- unclear data model, ownership, lifecycle, validation, or constraints
- missing architecture decisions, trade-offs, dependencies, or alternatives
- missing security, privacy, reliability, performance, or observability requirements
- acceptance criteria that are not executable or verifiable

Do not start writing final content until the interview packet is complete. If the user explicitly says to write with current information, proceed only with unresolved material items labeled as `Open Question`, explicitly `WAIVED`, or accepted as named `UNVERIFIED`; never mark the interview gate `READY` from unresolved material ambiguity.

## Readiness States

Report the interview gate with exactly one state whenever a packet is persisted, filled answers are ingested, or write-back / BUILD readiness is discussed:

- `READY`: material questions are answered, answers are coherent with evidence, and acceptance/testability is sufficient for implementation.
- `BLOCKED`: material ambiguity, contradiction, incomplete answer, evidence conflict, unsupported default, out-of-scope answer, or untestable acceptance remains. Use `BLOCKED_FOR_CLARIFICATION` as the detailed reason when the next action is another interview round.
- `WAIVED`: the user explicitly waived the interview gate or a named question despite the missing information.
- `UNVERIFIED`: the user explicitly accepted named unresolved or unverifiable items as `UNVERIFIED`; do not describe those items as confirmed.

## Phase B: Draft Interview Packet

For non-trivial changes, generate a Markdown interview packet instead of asking scattered chat questions.

Default behavior:

- For OpenSpec sources, write `openspec/changes/<change-id>/interview.md` without asking.
- For every non-OpenSpec source, including a single source document, ask for placement before writing.
- Use chat-only output only when the user explicitly asks for it or selects chat-only in the placement question.

Phase B produces a draft packet. Do not present or persist it before Phase C.

The packet must include:

1. `资料来源与证据`
2. `当前理解`
3. `覆盖矩阵与状态`
4. `需要你填写的问题`
5. `设计漏洞 / 证据缺口 / 反例`
6. `填写说明`
7. `后续写回映射`
8. `答案吸收记录`

Use this template:

```markdown
# 变更采访包：<change-name>

## 1. 资料来源与证据

| 来源 | 已检查内容 | 观察到的事实 | 置信度 | 备注 |
|---|---|---|---|---|
| `<path>` | 现有实现 / 文档 / 测试 | ... | high / medium / low | ... |

## 2. 当前理解

- 目标：
- 当前草稿表达的是：
- 现有代码 / 文档显示：
- 已确认约束：
- 暂定非目标：
- 仍不确定的地方：

## 3. 覆盖矩阵与状态

状态只能使用：`Confirmed by evidence`、`Not applicable`、`Needs question`、`Open Question`、`Unverified`。

| 维度 | 状态 | 证据 / 原因 | 关联问题 | 写回目标 |
|---|---|---|---|---|
| goal/success | ... | ... | Q? / N/A | `proposal.md` / `test-plan.md` |
| scope/non-goals | ... | ... | Q? / N/A | `proposal.md` |
| roles/permissions | ... | ... | Q? / N/A | `design.md` / specs |
| happy path | ... | ... | Q? / N/A | `design.md` / specs |
| failure path | ... | ... | Q? / N/A | `design.md` / `test-plan.md` |
| retries/rollback | ... | ... | Q? / N/A | `design.md` / `test-plan.md` |
| boundary conditions | ... | ... | Q? / N/A | specs / `test-plan.md` |
| data lifecycle | ... | ... | Q? / N/A | `design.md` / specs |
| state transitions | ... | ... | Q? / N/A | `design.md` / specs |
| API/CLI/UI contracts | ... | ... | Q? / N/A | specs / `tasks.md` |
| compatibility/migration | ... | ... | Q? / N/A | `design.md` / `tasks.md` |
| security/privacy | ... | ... | Q? / N/A | `design.md` / `test-plan.md` |
| performance/reliability | ... | ... | Q? / N/A | `design.md` / `test-plan.md` |
| observability | ... | ... | Q? / N/A | `design.md` / `tasks.md` |
| acceptance/testability | ... | ... | Q? / N/A | specs / `test-plan.md` |
| rollout/rollback | ... | ... | Q? / N/A | `proposal.md` / `design.md` |
| explicit non-goals | ... | ... | Q? / N/A | `proposal.md` |

## 4. 需要你填写的问题

| ID | 问题 | 为什么要问 | 影响的 artifact / decision | 有证据支撑的推荐默认答案 | 后果 / 取舍 | 你的填写 | 写回位置 |
|---|---|---|---|---|---|---|---|
| Q1 | ... | ... | scope / design / tasks / acceptance / tests / risk / implementation safety | ...（证据：`<path>`） | 选 A 会...；选 B 会... |  | `proposal.md` |

## 5. 设计漏洞 / 证据缺口 / 反例

| ID | 类型 | 说明 | 建议处理方式 | 状态 |
|---|---|---|---|---|
| L1 | Missing evidence | ... | 查代码 / 查官方文档 / 问用户 / Open Question | open |

## 6. 填写说明

- 可以直接在“你的填写”列里写答案。
- 不确定的地方写“不确定”即可。
- 接受推荐默认答案时，写“同意默认”。
- 不进入本次 scope 的内容，写“本次不做”。
- 未填写内容不会被写成事实，只会保留为 `Open Question`。
- 无证据支撑但暂时保留的内容会标为 `Unverified`。
- 如果填写内容仍有歧义、互相矛盾、不可测试、与证据冲突或超出 scope，会进入追问轮，不会直接写回为事实。

## 7. 后续写回映射

| 用户答案 | 将写回到 | 写回方式 | 写回前门禁 |
|---|---|---|---|
| Q1 | `proposal.md` | scope / non-goal | confirmed / waived / accepted `UNVERIFIED` |

## 8. 答案吸收记录

_用户填写后由模型补充。_

| 问题 | 用户答案 | 分类 | 形成的决策 | 已写回位置 | 剩余不确定 / 追问 |
|---|---|---|---|---|---|
```

Coverage matrix dimensions for non-trivial changes:

1. goal/success: who benefits, what pain is solved, what measurable result matters?
2. scope/non-goals and explicit non-goals: what is in scope, out of scope, MVP, follow-up, and deliberately excluded?
3. roles/permissions: actors, owners, authorization, approval, and access boundaries.
4. happy path and failure path: normal flow, error flow, user-visible failures, and recovery expectations.
5. retries/rollback and rollout/rollback: retry/backoff, undo, operational rollback, release boundaries, and safe stop points.
6. boundary conditions: limits, empty/loading/error states, invalid inputs, concurrency, ordering, platform/version boundaries, and edge cases.
7. data lifecycle: creation, validation, retention, cleanup, migration, ownership, privacy class, and audit needs.
8. state transitions: lifecycle states, allowed transitions, blocked transitions, idempotency, and stale-state handling.
9. API/CLI/UI contracts: command syntax, request/response shape, UI copy, compatibility, errors, and versioning.
10. compatibility/migration: backward compatibility, deprecation, upgrade path, and affected existing users or artifacts.
11. security/privacy: secrets, permissions, data exposure, trust boundaries, compliance, and fail-closed behavior.
12. performance/reliability: latency, scale, resource usage, availability, retries, and degradation behavior.
13. observability: logs, metrics, audit trail, user-visible status, debugging evidence, and failure reports.
14. acceptance/testability: executable scenarios, verification commands, manual checks, and acceptance thresholds.

For every dimension, choose one status only:

- `Confirmed by evidence`: current repo/docs/specs/tests/configs/official docs answer it; cite the evidence.
- `Not applicable`: the dimension does not apply; give a short reason.
- `Needs question`: a decision-changing user answer is required; add or link a question.
- `Open Question`: still unresolved and must not be written as fact.
- `Unverified`: retained only as a named unverified item, preferably after user acceptance.

Material question threshold:

- Ask only if the answer can change scope, design, tasks, acceptance criteria, tests, risk handling, rollout, or implementation safety.
- Each question must include why asked, affected artifact/decision, evidence-backed recommended default when available, consequences/trade-offs, answer slot, and write-back target.
- If a candidate question is generic or would not change implementation readiness, omit it or convert it to a non-blocking note.
- If the answer is discoverable from current repository files, tests, configs, specs, docs, or official sources, gather and cite evidence instead of asking.
- If no evidence-backed default exists, mark the default as `Open Question` or `Unverified`; do not present a guess as a recommendation.

In Packet Mode, include questions immediately when mentioned:

- multi-tenancy: isolation model, tenant identifiers, cross-tenant controls, migrations
- offline/background sync: conflict resolution, retry/backoff, reconciliation
- security/privacy/compliance: data retention, audit logs, encryption, PII handling
- UI/UX: empty/loading/error states, permission-denied copy, accessibility, i18n
- agent workflow changes: primary/subagent boundaries, skill routing, verification, memory, and no nested orchestration

If the user says `先这样`, `按目前信息写回`, or equivalent, stop asking only after classifying unresolved material items. Proceed with write-back only when unresolved items are recorded as `Open Question`, explicitly `WAIVED`, or accepted as named `UNVERIFIED`; do not write unresolved material answers as facts or report `READY` until clarified.

## Phase C: Stress-Test the Interview Packet

After generating the draft interview packet, use `strategy-stress-test` to stress-test and repair the draft packet.

🔴 STOP before persistence if the stress-test found an unresolved missing question, unsupported default, non-executable acceptance criterion, or unmarked `Open Question` / `Unverified` item. Repair the packet first or report the blocker.

Check:

- What important question is missing?
- Which question asks the user for information that should be discovered from code/docs instead?
- Which recommended default lacks evidence?
- Which user answer would lead to a completely different design?
- Which acceptance criteria are not executable?
- Which security, privacy, reliability, rollout, migration, compatibility, or observability risks are not covered?
- Which assumptions must be marked `Open Question` or `Unverified`?

Apply fixes to the interview packet before sending it to the user.

After Phase C, persist the final packet according to the Output Placement Contract. Only then present a concise chat summary.

### Grilling Discipline

In Interactive Mode, ask one question at a time when the answer materially changes design or implementation.

For each question:
- explain why it matters
- provide the recommended answer
- state the tradeoff
- wait for the user's answer when the decision is product/domain/architecture-sensitive

If the answer can be discovered from code or docs, inspect the code/docs instead of asking.

During the interview:
- call out conflicts with existing glossary terms
- sharpen vague or overloaded terms into canonical project language
- test domain claims with concrete edge scenarios
- compare user statements against current code behavior
- surface contradictions immediately

## Phase D: Ingest User Answers

After the user fills the interview packet:

1. Re-read the filled packet from disk first; conversation summaries are stale until confirmed against the saved artifact.
2. Classify every material answer as one of: `confirmed`, `ambiguous`, `contradictory`, `incomplete`, `untestable`, `evidence-conflicting`, `out-of-scope`, or `Unverified`.
3. Convert only `confirmed`, explicitly waived, or user-accepted `Unverified` answers into Decisions, Requirements, Design notes, Tasks, Acceptance criteria, and Verification commands.
4. Keep unanswered, ambiguous, contradictory, incomplete, untestable, evidence-conflicting, or out-of-scope answers out of factual write-back.
5. Generate a follow-up question round for each material blocker, including why it blocks, affected artifact/decision, recommended default if evidence supports one, consequences/trade-offs, answer slot, and write-back target.
6. Keep unverifiable external claims as `Unverified` only when named and explicitly accepted by the user; otherwise classify them as blocking or `Open Question`.
7. Do not silently resolve conflicts or treat a filled answer slot as confirmation when the answer remains unclear.
8. Build an incorporation log before write-back that records answer classification, evidence checked, follow-up needed, and readiness state.
9. Use `strategy-stress-test` after answer classification and before write-back to check for unsafe ingestion, missed follow-up questions, evidence conflicts, unsupported defaults, untestable acceptance, or unmarked `Open Question` / `Unverified` items.

If the answer-set stress-test finds material ambiguity, contradiction, incompleteness, untestable acceptance, evidence conflict, or out-of-scope expansion, report readiness as `BLOCKED` / `BLOCKED_FOR_CLARIFICATION`, persist or present the follow-up round according to the placement contract, and do not write the affected answers into proposal, design, tasks, specs, acceptance criteria, or test plans until clarified, waived, or accepted as `UNVERIFIED`.

If the user explicitly says to proceed despite named unresolved items, record whether the gate is `WAIVED` or `UNVERIFIED`, list the accepted items, and keep the risk visible in write-back and completion reports. Do not call it `READY`.

## Phase E: Write Back

Write only to the agreed target files.

🔴 STOP before write-back when the target file is not explicitly agreed, the interview gate is `BLOCKED`, answers conflict, existing content would need replacement instead of merge, or a confirmed answer would change scope/design/tasks beyond the agreed package. Ask or report the conflict instead of overwriting.

BUILD readiness rule: a change package may proceed from the interview gate only when the state is `READY`, explicitly `WAIVED`, or explicitly accepted as `UNVERIFIED` with named unresolved items. A merely completed form is not enough.

General write-back rules:

- Merge rather than overwrite.
- Preserve headings, IDs, task markers, and existing conventions.
- Put details closest to the file that owns them: proposal for why/scope, design for decisions/trade-offs, tasks for execution, specs or acceptance docs for testable behavior.
- Add traceability where useful: requirement -> design decision -> task -> verification.

For OpenSpec targets:

- Preserve required delta headers when present: `## ADDED Requirements`, `## MODIFIED Requirements`, `## REMOVED Requirements`, `## RENAMED Requirements`.
- Preserve `### Requirement:` and `#### Scenario:` structure.
- Keep at least one scenario per requirement when adding requirements.

For Superpowers-style plans or custom documents:

- Preserve the user's plan sections and task ordering.
- Add missing acceptance criteria and verification commands near the tasks they prove.
- Keep unconfirmed details in `Open Questions` instead of turning them into commitments.

## Validation

After write-back:

1. Inspect the diff to confirm the target files changed as intended and unrelated files were not modified.
2. If the target is OpenSpec, run `openspec validate <change-id> --strict` or the repo-local equivalent if available.
3. If the target has a known validation command from project docs, run it.
4. If no command exists, validate by reading the edited files and checking that unresolved items are labeled.
5. Report what was verified and what remains unverified.

## Completion Report

Report:

- Source reviewed
- Questions asked and key answers incorporated
- Files changed
- Interview readiness state: `READY`, `BLOCKED`, `WAIVED`, or `UNVERIFIED`
- Open questions left unresolved
- Validation command or inspection result
