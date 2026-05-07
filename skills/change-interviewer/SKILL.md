---
name: change-interviewer
description: Interview the user to clarify and complete a proposed change from OpenSpec files, Superpowers-style plans, pasted instructions, issue text, or user-provided files, then write the refined requirements, design, tasks, and acceptance criteria back to the agreed target files when persistence is requested.
---

# Change Interviewer

## Purpose

Use this skill to turn an incomplete change idea or draft into an implementable, reviewable change package.

The input can be an OpenSpec change directory, a Superpowers-style plan, a user-pasted paragraph, an issue, a ticket, or one or more custom files. The output should preserve the user's intent, clarify unknowns through interview questions, and persist refined content only to the agreed target files.

## When to Use

Use this skill when the user wants to refine a change before implementation, especially when the source material is ambiguous, incomplete, or spread across files.

Realistic trigger prompts:

- "Interview me and turn this rough idea into tasks/design/acceptance criteria."
- "Use this Superpowers plan as input and ask what is missing before writing it back."
- "Refine `docs/change.md` with questions first; do not guess requirements."
- "Complete this OpenSpec change package after interviewing me."

## When Not to Use

Do not use this skill for:

- implementing the change after requirements are clear
- broad product brainstorming with no intent to produce a change package
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
- no file edits yet, if the user only wants interview questions

If the target is unclear, ask one question before writing. Do not create files or directories without confirmation.

## Non-Negotiables

- Do not fill in requirements, design, or acceptance criteria by guessing.
- Ask questions; record unresolved items as `Open Question:`.
- Preserve existing author content and structure whenever possible.
- If restructuring is necessary, keep original text under `## Appendix: Original Draft` in the same file.
- Never record unconfirmed information as fact. Use `Assumption:` only when the user has accepted it as a working assumption.
- Keep source-specific formats intact, especially OpenSpec requirement headers and scenarios.

## Phase A: Read and Diagnose

Before interviewing:

1. Read the user-provided source text or files.
2. If the source is an OpenSpec change directory, inventory `tasks.md` or `task.md`, `proposal.md`, `design.md`, and `specs/` files.
3. If the source is a plan or custom file, identify its existing sections, task markers, requirements, and acceptance criteria.
4. Build a concise gap list focused on what would block implementation or review.

Common gaps:

- unclear goal, user, or success criteria
- missing in-scope and out-of-scope boundary
- incomplete happy path, failure path, retry, rollback, or migration flow
- undefined interfaces, API shapes, events, auth, errors, or versioning
- unclear data model, ownership, lifecycle, validation, or constraints
- missing architecture decisions, trade-offs, dependencies, or alternatives
- missing security, privacy, reliability, performance, or observability requirements
- acceptance criteria that are not executable or verifiable

Do not start writing final content until the first interview round is complete unless the user explicitly says to write with current information.

## Phase B: Interview

Ask high-information-gain questions in rounds. Start broad, then drill down. Use Markdown ordered lists and write `1.` for every question to avoid numbering gaps.

Question order:

1. Goals and success: who benefits, what pain is solved, what measurable result matters?
1. Scope boundaries: what is in scope, out of scope, MVP, and follow-up?
1. Key flows: happy path, failure behavior, retries, rollback, permissions, and edge cases.
1. Data and interfaces: entities, fields, APIs, events, ownership, validation, and error handling.
1. Architecture and trade-offs: where logic lives, alternatives rejected, compatibility, scaling, and constraints.
1. Risks and acceptance: risk register, test strategy, manual checks, rollout, and executable acceptance criteria.

Ask immediately when mentioned:

- multi-tenancy: isolation model, tenant identifiers, cross-tenant controls, migrations
- offline/background sync: conflict resolution, retry/backoff, reconciliation
- security/privacy/compliance: data retention, audit logs, encryption, PII handling
- UI/UX: empty/loading/error states, permission-denied copy, accessibility, i18n
- agent workflow changes: primary/subagent boundaries, skill routing, verification, memory, and no nested orchestration

If the user says `先这样`, `按目前信息写回`, or equivalent, stop asking and proceed with unresolved items recorded as open questions.

## Phase C: Write Back

Write only to the agreed target files.

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
- Open questions left unresolved
- Validation command or inspection result
