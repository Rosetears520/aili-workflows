---
name: requirements-grilling
description: Canonical AILI requirements-grilling workflow for evidence-first requirements clarification, change-interviewer compatibility, Chinese interview packet generation, OpenSpec interview.md write-back readiness, domain-modeling, ADR gating, and grill/interview packet trigger phrases before BUILD.
---

# Requirements Grilling

## Purpose

Use this skill to turn an incomplete change idea or draft into an implementable, reviewable change package by grilling the requirements, sharpening domain language, and preserving AILI DEFINE artifacts.

The input can be an OpenSpec change directory, a Superpowers-style plan, a user-pasted paragraph, an issue, a ticket, or one or more custom files. The output should preserve the user's intent, clarify unknowns through interview questions, and persist refined content only to the agreed target files.

`requirements-grilling` is the canonical capability name. Old terms such as `change-interviewer`, “interview packet”, and “change interview” are compatibility trigger phrases only; they route to this same flow and must not create a second user-facing skill or artifact contract.

## Provenance

This skill is the AILI adaptation of upstream Matt Pocock skills `grilling` and `domain-modeling`, copied/adapted under the upstream MIT License. It combines their questioning and domain-modeling disciplines with AILI/OpenSpec artifact placement, `interview.md` compatibility, `context.md` Language handling, `adr.md` gating, answer ingestion, and readiness states.

Upstream-originated reference formats are preserved by name in this skill's `references/` directory:

- `references/CONTEXT-FORMAT.md`
- `references/ADR-FORMAT.md`
- `references/INTERVIEW-PACKET-FORMAT.md`
- `references/MIT-LICENSE-MATT-POCOCK.md`

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

Use this skill when the user wants to refine, grill, challenge, interview, or write back a change before implementation, especially when source material is ambiguous, incomplete, or spread across files.

This skill owns user-facing clarification,方案 discussion, no-objection/approval capture, waiver capture, write-back readiness, and `interview.md` answer ingestion. It does not own the evidence lanes themselves: official/API docs route to `source-driven-development`, mature public-project prior art routes to `mature-project-pattern-research`, local repository facts route to `repo-evidence-first`, and test-plan artifacts route to `test-document-generator`.

Realistic trigger prompts:

- "Interview me and turn this rough idea into tasks/design/acceptance criteria."
- "Use this Superpowers plan as input and ask what is missing before writing it back."
- "Refine `docs/change.md` with questions first; do not guess requirements."
- "Complete this OpenSpec change package after interviewing me."
- "Grill this requirement / interview packet before write-back or BUILD readiness."
- "I filled `interview.md`; check whether the answers are clear enough to write back."
- "Research/docs first, then give me a方案 before implementation."
- Any old `change-interviewer` request, interview packet request, or DEFINE/BUILD readiness discussion where official/API docs, fast-changing/version-sensitive sources, model uncertainty, explicit user-requested research, or industry/GitHub similar projects materially affect the方案.

## When Not to Use

Do not use this skill for:

- implementing the change after requirements are clear
- broad product brainstorming with no intent to produce a change package
- pure plan, design, spec, review, or completion-claim stress-testing with no requirements-grilling or write-back target; use `strategy-stress-test` directly
- initializing project-level agent rules or OpenCode setup docs
- rewriting a document without grilling, interviewing, or preserving author intent
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
- temporary chat preview, only when the user explicitly asks for it; it is not a readiness source until persisted to an agreed file

Only OpenSpec change directories have deterministic no-question file output. For every non-OpenSpec source, including a single source document with an obvious sibling path, ask one concise placement question before writing.

## Output Placement Contract

Initial Packet Mode defaults to persistent artifact output; unresolved readiness follow-up defaults to chat-first interaction with AI write-back.

### Quick Reference Flow

```text
source-ground -> resolve placement -> draft packet -> 🔴 stress-test -> repair -> persist -> concise summary
unresolved readiness question -> ask in chat by default -> write accepted answer/waiver/UNVERIFIED state to artifact -> disk re-read -> answer classification/readiness -> domain-language/ADR check -> 🔴 stress-test -> follow-up round or incorporation log -> 🔴 write-back target check -> merge into agreed files -> validate
```

Generate the initial interview packet, run the stress-test pass, repair the packet, persist the final packet, then summarize the generated path in chat. Do not print the full packet in chat unless the user explicitly asks for a temporary preview, writing is blocked by permissions or missing workspace access, or the user chooses preview-before-placement after the placement question. A chat preview is not a completed requirements-grilling artifact and cannot satisfy BUILD readiness.

After the initial packet exists, do not require the user to manually edit `interview.md` by default. When unresolved OpenSpec readiness questions remain, ask the blocking question in chat, write the user's accepted answer, accepted default, explicit waiver, or accepted `UNVERIFIED` state into `interview.md`, then re-read the file from disk before classifying answers or claiming readiness. Direct user edits to `interview.md` remain a supported fallback, but disk content must be re-read and reconciled before use.

OpenSpec change output is the only deterministic no-question placement. For every non-OpenSpec source, ask where to place the output before writing; chat preview is an explicit temporary fallback only, and the gate remains `BLOCKED_FOR_CLARIFICATION` until the packet or follow-up round is persisted to an agreed file or explicitly waived.

🔴 STOP before writing when placement is not deterministic: for any non-OpenSpec source, missing workspace access, ambiguous target, existing target ownership conflict, or user-pasted text with no path, ask the placement question and wait. Do not choose a path silently.

Target path resolution:

1. If the source is an OpenSpec change directory, write `openspec/changes/<change-id>/interview.md` without asking.
2. If the source is non-OpenSpec, ask where to place the output before writing, even when the source is a single document:
   - A. create a sibling Markdown file beside the main source file;
   - B. create a sibling folder beside the source directory;
   - C. append a new section to the existing spec/design document;
   - D. preview in chat first, then choose a file target before readiness or write-back.
3. If the user pasted only free-form text and no source path exists, ask whether to:
   - A. create a new file in a user-specified location;
   - B. append to an existing spec/document;
   - C. preview in chat first, then choose a file target before readiness or write-back.
4. If the user explicitly says "print in chat", "do not create files", or "chat only", provide a temporary preview and report `BLOCKED_FOR_CLARIFICATION` until the user either selects a persistence target, explicitly waives file persistence for a named reason, or accepts the result as `UNVERIFIED`. Do not call the packet `READY` from chat-only content.

Use this concise placement question for non-OpenSpec sources:

```text
这个非 OpenSpec 输出需要先确认落点，你选一个：
A. 生成在源文件同级：<path>
B. 在源目录同级新建文件夹：<path>
C. 追加到现有 spec / design 文档末尾
D. 先在对话框预览；之后仍需选择 A/B/C 写回文件，才能进入 READY / BUILD
```

Chat response after persistence should include only:

- generated file path
- source files reviewed
- number of questions
- unresolved `Open Question` / `Unverified` count
- requirements-grilling readiness state: `READY`, `BLOCKED`, `WAIVED`, or `UNVERIFIED`
- suggested next action

## Interview Modes

Use Packet Mode by default for non-trivial changes:

- generate the Chinese interview packet at `interview.md` for OpenSpec sources
- treat that packet as the durable AI-maintained record, not as a manual form the user must fill by default
- ask unresolved blocking follow-up questions in chat by default, then write accepted answers, waivers, or accepted `UNVERIFIED` states back into the same artifact
- re-read answers from disk before classification, readiness, or write-back
- append Round 2+ follow-up sections in the same artifact when material blockers remain, after recording the chat question/answer trail or direct-file fallback

Use Interactive Mode only when:

- the change is small
- one answer materially changes the next question
- the user explicitly wants chat-based interviewing

In Interactive Mode, ask one question at a time.

Interactive chat answers must still be persisted. After a material answer is accepted, append or merge the question, answer, classification, and write-back target into `interview.md` for OpenSpec sources or the agreed non-OpenSpec target, then re-read that artifact from disk before claiming readiness. If persistence is blocked, report `BLOCKED_FOR_CLARIFICATION` and the exact file target still needed.

In Packet Mode, do not interrupt the packet with chat-style single-question turns unless a blocking target or persistence decision is missing.

## Grilling Discipline

The upstream `grilling` discipline is part of this flow:

```text
Interview me relentlessly about every aspect of this plan until we reach a shared understanding. Walk down each branch of the design tree, resolving dependencies between decisions one-by-one. For each question, provide your recommended answer.

Ask the questions one at a time, waiting for feedback on each question before continuing. Asking multiple questions at once is bewildering.

If a question can be answered by exploring the codebase, explore the codebase instead.
```

AILI adaptations:

- In Interactive Mode, ask one material question at a time and wait.
- In Packet Mode, group the initial question set in `interview.md`, but preserve dependency order; after the packet exists, ask unresolved OpenSpec readiness follow-ups in chat by default, write the accepted outcome to the artifact, re-read it from disk, and make Round 2+ follow-ups one decision branch at a time when answers diverge.
- For each question, explain why it matters, name the affected artifact or decision, provide an evidence-backed recommended answer when available, state the tradeoff, include an answer slot, and name the write-back target.
- If the answer can be discovered from code, docs, specs, tests, configs, or official sources, inspect those sources instead of asking.
- If no evidence-backed default exists, use `Open Question` or `Unverified`; do not present a model guess as a recommendation.

## Domain-Modeling Discipline

Apply domain-modeling as an active discipline, not as passive glossary lookup.

During grilling:

- challenge conflicts with existing glossary terms, artifact names, lifecycle terms, source-of-truth ownership, readiness states, or code/docs language
- sharpen fuzzy or overloaded terms into project-specific canonical language
- discuss concrete happy-path, failure-path, boundary, stale-state, partial-answer, contradiction, waiver, and unverified scenarios
- cross-reference current code, docs, specs, tests, configs, and approved source evidence before accepting domain claims
- update the change-local `context.md` `## Language` section only when project-specific terms or conflicts are discovered and resolved
- keep `context.md` Language glossary-like: tight definitions, `_Avoid_` alternatives, and project-specific terms only
- keep implementation decisions, trade-offs, scratchpad notes, generic programming terms, and architecture rationale out of Language; use `design.md`, `adr.md`, tasks, specs, or `drift-log.md` as appropriate

Use `references/CONTEXT-FORMAT.md` for Language structure. For OpenSpec changes, `context.md` remains beside `interview.md` unless a future accepted change says otherwise.

## ADR Handling

Offer an ADR sparingly and only when all three are true:

1. The decision is hard to reverse.
2. The decision would be surprising without context.
3. The decision is the result of a real trade-off.

Use `references/ADR-FORMAT.md` for structure. ADRs for an OpenSpec change live as `openspec/changes/<change-id>/adr.md` beside `interview.md` unless a future accepted change says otherwise.

Keep ADRs short. The value is recording the decision and why; status, options, and consequences are optional when useful. Use `Status: Proposed` unless the user or accepted change authority explicitly confirms the decision as accepted.

## Non-Negotiables

- Do not fill in requirements, design, or acceptance criteria by guessing.
- Ask or include questions according to the selected interview mode; record unresolved items as `Open Question:`.
- Treat files as the source of truth: chat questions and answers are temporary until written to `interview.md` or the agreed target and re-read from disk.
- Preserve existing author content and structure whenever possible.
- If restructuring is necessary, keep original text under `## Appendix: Original Draft` in the same file.
- Never record unconfirmed information as fact. Use `Assumption:` only when the user has accepted it as a working assumption.
- Keep source-specific formats intact, especially OpenSpec requirement headers and scenarios.
- Keep `/ideate`, `/define`, `/build`, and `/ship` as the only public top-level delivery commands; do not add `/grill`, `/grill-me`, or `/interview`.
- Keep the artifact name `interview.md`; do not create `grill.md`, `grilling.md`, or `requirements-grilling.md` for the same OpenSpec clarification flow.

## Anti-Patterns / Blacklist

- Do not treat chat-only questioning, dry-run output, or a preview as the final requirements artifact.
- Do not mark `READY` until material chat answers have been persisted to `interview.md` or the agreed target and re-read from disk.
- Do not confirm broad-label requirements such as “security”, “idempotency”, “quota”, or “audit” without concrete behavior, boundaries, source-of-truth, and testable acceptance.
- Do not create parallel artifacts such as `grill.md`, `grilling.md`, or `requirements-grilling.md` for an OpenSpec clarification flow.
- Do not write back to unagreed files, and do not overwrite existing user-authored material when a merge is possible.
- Do not invent requirements or recommended defaults when repo/docs/official evidence can answer the question.

## Phase A: Source Grounding

Before generating questions:

1. Read the user-provided source text or files.
2. If the source is an OpenSpec change directory, inventory `tasks.md` or `task.md`, `proposal.md`, `design.md`, `context.md`, `adr.md`, and `specs/` files.
3. If the source is a plan, issue, ticket, PR description, or custom file, identify existing sections, task markers, requirements, acceptance criteria, and unresolved assumptions.
4. If repository evidence is needed and the search would be broad or noisy, dispatch `code-scout` as a read-only evidence locator. If `code-scout` is unavailable, inspect the targeted files directly when the scope is narrow; otherwise report the evidence gap and keep affected rows as `Open Question` / `Unverified`.
5. If external behavior matters, route official/API documentation through `source-driven-development` and current/prior-art sources through the appropriate research lane before asking the user.
6. If the planning gate is triggered by fast-changing/version-sensitive docs and APIs, provider docs such as DeepSeek, SDK/framework/changelog-sensitive behavior, model uncertainty, explicit user-requested research, or industry/GitHub similar-project research, synthesize an evidence-backed方案 before implementation.
7. Build a concise evidence table that separates Observed Fact, External Source, Inference, Assumption, Open Question, and Unverified.
8. Build or refine the domain model: candidate terms, conflicting names, boundary examples, source-of-truth owners, and code/doc contradictions.

Do not ask the user for information that can be reliably discovered from current code, docs, specs, tests, configs, or official sources.

Research-first planning sequence: gather docs/evidence, investigate, synthesize方案 with tradeoffs and `Unverified` items, discuss/confirm no objection or approval, then allow implementation only when the方案 is `READY`, explicitly `WAIVED`, or explicitly accepted as `UNVERIFIED`. A completed packet or confident model answer is not enough.

Common gaps:

- unclear goal, user, or success criteria
- missing in-scope and out-of-scope boundary
- incomplete happy path, failure path, retry, rollback, or migration flow
- undefined interfaces, API shapes, events, auth, errors, or versioning
- unclear data model, ownership, lifecycle, validation, or constraints
- fuzzy, conflicting, or overloaded domain terms
- missing architecture decisions, trade-offs, dependencies, or alternatives
- missing security, privacy, reliability, performance, or observability requirements
- acceptance criteria that are not executable or verifiable

Do not start writing final content until the interview packet is complete. If the user explicitly says to write with current information, proceed only with unresolved material items labeled as `Open Question`, explicitly `WAIVED`, or accepted as named `UNVERIFIED`; never mark the requirements-grilling gate `READY` from unresolved material ambiguity.

## Readiness States

Report the requirements-grilling gate with exactly one state whenever a packet is persisted, chat or direct-file answers are ingested, follow-up rounds are appended, or write-back / BUILD readiness is discussed:

- `READY`: material questions are answered, answers are coherent with evidence, domain language is not contradictory, every material policy has concrete behavior/boundaries, and acceptance/testability is sufficient for implementation.
- `BLOCKED`: material ambiguity, contradiction, incomplete answer, evidence conflict, unsupported default, out-of-scope answer, fuzzy domain term, source-of-truth conflict, or untestable acceptance remains. Use `BLOCKED_FOR_CLARIFICATION` as the detailed reason when the next action is another grilling round.
- `WAIVED`: the user explicitly waived the gate or a named question despite the missing information.
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
6. `术语 / 领域模型挑战`
7. `填写说明`
8. `后续写回映射`
9. `答案吸收记录`

Use `references/INTERVIEW-PACKET-FORMAT.md` as the packet template. Keep the full Markdown skeleton out of `SKILL.md` so this file stays focused on routing, gates, and workflow rules.

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
11. terminology/domain model: canonical terms, avoided terms, source-of-truth ownership, conflicting names, and boundary examples.
12. security/privacy: secrets, permissions, data exposure, trust boundaries, compliance, and fail-closed behavior.
13. performance/reliability: latency, scale, resource usage, availability, retries, and degradation behavior.
14. observability: logs, metrics, audit trail, user-visible status, debugging evidence, and failure reports.
15. acceptance/testability: executable scenarios, verification commands, manual checks, and acceptance thresholds.

For every dimension, choose one status only:

- `Confirmed by evidence`: current repo/docs/specs/tests/configs/official docs answer it with exact behavior, boundary, a source-of-truth anchor such as code/test/config/docs or an explicit owner, and a testable acceptance/verification signal; cite the evidence. A term, heading, checklist label, or broad phrase alone is not evidence that the dimension is confirmed.
- `Not applicable`: the dimension does not apply; give a short reason.
- `Needs question`: a decision-changing user answer is required; add or link a question.
- `Open Question`: still unresolved and must not be written as fact.
- `Unverified`: retained only as a named unverified item, preferably after user acceptance.

Material question threshold:

- Ask only if the answer can change scope, design, tasks, acceptance criteria, tests, risk handling, rollout, terminology, domain model, or implementation safety.
- Each question must include why asked, affected artifact/decision, evidence-backed recommended default when available, consequences/trade-offs, answer slot, and write-back target.
- If a candidate question is generic or would not change implementation readiness, omit it or convert it to a non-blocking note.
- If the answer is discoverable from current repository files, tests, configs, specs, docs, or official sources, gather and cite evidence instead of asking.
- If no evidence-backed default exists, mark the default as `Open Question` or `Unverified`; do not present a guess as a recommendation.
- If a source only names a material topic but does not define behavior, boundary, failure handling, owner/source-of-truth, or acceptance criteria, treat it as `Needs question` or `Open Question`, not `Confirmed by evidence`.
- Slogan-level phrases such as “安全策略”, “违规内容”, “重复处理”, “幂等”, “回滚”, “失败处理”, “权限”, “quota”, “view 策略”, “清理策略”, “日志”, or “audit” require follow-up when they affect implementation or tests and no concrete policy is cited.

In Packet Mode, treat these as material-question candidates when mentioned. Include a question immediately only when the topic is material and the cited source does not already define the concrete behavior, boundary, source-of-truth anchor, and acceptance signal:

- multi-tenancy: isolation model, tenant identifiers, cross-tenant controls, migrations
- offline/background sync: conflict resolution, retry/backoff, reconciliation
- security/privacy/compliance: data retention, audit logs, encryption, PII handling
- backend/product semantics: duplicate writes, overwrite versus reject versus versioning, retry counting, quota counting, deletion access, scrub/cleanup failure visibility, snapshot/view isolation, response headers, and log/audit redaction
- UI/UX: empty/loading/error states, permission-denied copy, accessibility, i18n
- agent workflow changes: primary/subagent boundaries, skill routing, verification, memory, and no nested orchestration
- terminology or artifact-name changes: old/new names, compatibility aliases, user-visible vs invisible routing, and artifact contract boundaries

If the user says `先这样`, `按目前信息写回`, or equivalent, stop asking only after classifying unresolved material items. Proceed with write-back only when unresolved items are recorded as `Open Question`, explicitly `WAIVED`, or accepted as named `UNVERIFIED`; do not write unresolved material answers as facts or report `READY` until clarified.

## Phase C: Stress-Test the Interview Packet

After generating the draft interview packet, use `strategy-stress-test` to stress-test and repair the draft packet. If that skill or a review lane is unavailable, run the checklist below directly and report the missing independent review as an `Unverified` limitation when it matters.

🔴 STOP before persistence if the stress-test found an unresolved missing question, unsupported default, non-executable acceptance criterion, fuzzy domain term, missing boundary scenario, ADR misuse, or unmarked `Open Question` / `Unverified` item. Repair the packet first or report the blocker.

Check:

- What important question is missing?
- Which question asks the user for information that should be discovered from code/docs instead?
- Which recommended default lacks evidence?
- Which user answer would lead to a completely different design?
- Which acceptance criteria are not executable?
- Which rows were marked `Confirmed by evidence` from keyword presence, broad headings, or checklist labels instead of exact requirements?
- Which security, privacy, reliability, rollout, migration, compatibility, or observability risks are not covered?
- Which repeated-write, overwrite/versioning, retry, quota, cleanup, view/isolation, or audit/log behavior is named but not specified?
- Which terms conflict with project language or artifact names?
- Which boundary scenario would break the current model?
- Which potential ADR fails one of the three ADR gate criteria?
- Which assumptions must be marked `Open Question` or `Unverified`?

Apply fixes to the interview packet before sending it to the user.

After Phase C, persist the final packet according to the Output Placement Contract. Only then present a concise chat summary. If the user asked questions interactively, persist the accepted question/answer/classification trail before reporting readiness.

## Phase D: Ingest User Answers

After the user answers in chat or directly edits the interview packet:

1. Re-read the artifact from disk first; compatibility marker: Re-read the filled packet from disk. Conversation summaries and chat-only answers are stale until confirmed against the saved artifact. If answers were collected in chat, write them to the agreed artifact first, then re-read from disk before classification or readiness. If the user edited the file directly, treat the on-disk content as the fallback source of truth after re-reading and reconciling material changes.
2. Classify every material answer as one of: `confirmed`, `ambiguous`, `contradictory`, `incomplete`, `untestable`, `evidence-conflicting`, `out-of-scope`, or `Unverified`.
   - Answers that repeat broad labels such as “做安全策略”, “按幂等处理”, “正常回滚”, “走 quota”, “写 audit”, or “按现有逻辑” without concrete behavior, boundary, source-of-truth, and testable acceptance remain `incomplete` or `untestable` until clarified, waived, or accepted as named `UNVERIFIED`.
3. Convert only `confirmed`, explicitly waived, or user-accepted `Unverified` answers into Decisions, Requirements, Design notes, Tasks, Acceptance criteria, Verification commands, Language updates, or ADR proposals.
4. Keep unanswered, ambiguous, contradictory, incomplete, untestable, evidence-conflicting, out-of-scope, or terminology-conflicting answers out of factual write-back.
5. Generate a follow-up question round for each material blocker, including why it blocks, affected artifact/decision, recommended default if evidence supports one, consequences/trade-offs, answer slot, and write-back target.
6. Append Round 2+ follow-up rounds to the same `interview.md` artifact for OpenSpec sources; do not create `grill.md`, `requirements-grilling.md`, or a parallel artifact.
7. Keep unverifiable external claims as `Unverified` only when named and explicitly accepted by the user; otherwise classify them as blocking or `Open Question`.
8. Do not silently resolve conflicts or treat a filled answer slot as confirmation when the answer remains unclear.
9. Build an incorporation log before write-back that records answer classification, evidence checked, domain-language changes, ADR gate result, follow-up needed, and readiness state.
10. Use `strategy-stress-test` after answer classification and before write-back to check for unsafe ingestion, missed follow-up questions, evidence conflicts, unsupported defaults, untestable acceptance, domain-model contradictions, ADR misuse, or unmarked `Open Question` / `Unverified` items.

If the answer-set stress-test finds material ambiguity, contradiction, incompleteness, untestable acceptance, evidence conflict, terminology conflict, or out-of-scope expansion, report readiness as `BLOCKED` / `BLOCKED_FOR_CLARIFICATION`, persist or present the follow-up round according to the placement contract, and do not write the affected answers into proposal, design, tasks, specs, acceptance criteria, Language, ADR, or test plans until clarified, waived, or accepted as `UNVERIFIED`.

If the user explicitly says to proceed despite named unresolved items, record whether the gate is `WAIVED` or `UNVERIFIED`, list the accepted items, and keep the risk visible in write-back and completion reports. Do not call it `READY`.

## Phase E: Write Back

Write only to the agreed target files.

🔴 STOP before write-back when the target file is not explicitly agreed, the requirements-grilling gate is `BLOCKED`, answers conflict, existing content would need replacement instead of merge, a confirmed answer would change scope/design/tasks beyond the agreed package, Language would absorb an implementation decision, or an ADR would be created without passing the ADR gate. Ask or report the conflict instead of overwriting.

BUILD readiness rule: a change package may proceed from the requirements-grilling gate only when the state is `READY`, explicitly `WAIVED`, or explicitly accepted as `UNVERIFIED` with named unresolved items. A merely completed form is not enough.

General write-back rules:

- Merge rather than overwrite.
- Preserve headings, IDs, task markers, and existing conventions.
- Put details closest to the file that owns them: proposal for why/scope, design for decisions/trade-offs, tasks for execution, specs or acceptance docs for testable behavior, `context.md` Language for resolved project-specific terms, and `adr.md` for gated hard-to-reverse trade-offs.
- Add traceability where useful: requirement -> design decision -> task -> verification.

For OpenSpec targets:

- Preserve required delta headers when present: `## ADDED Requirements`, `## MODIFIED Requirements`, `## REMOVED Requirements`, `## RENAMED Requirements`.
- Preserve `### Requirement:` and `#### Scenario:` structure.
- Keep at least one scenario per requirement when adding requirements.
- Keep `interview.md`, `context.md`, and `adr.md` beside the change artifacts unless a future accepted change changes placement.

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
- Requirements-grilling readiness state: `READY`, `BLOCKED`, `WAIVED`, or `UNVERIFIED`
- Open questions left unresolved
- Validation command or inspection result
