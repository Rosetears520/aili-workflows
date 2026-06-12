## Overview

This change makes `change-interviewer` a stronger DEFINE artifact skill. The key design shift is from “generate a question packet” to “run a comprehensive readiness interrogation loop whose output can safely gate implementation.”

The protocol must remain file-oriented for non-trivial changes, especially OpenSpec, but it should also support an explicit interactive grill mode when the user asks for chat-based questioning or when one answer determines the next branch.

## Current Evidence

- `skills/change-interviewer/SKILL.md` already supports OpenSpec `interview.md` placement, evidence tables, recommended defaults, stress-testing before persistence, and answer ingestion.
- `skills/change-interviewer/SKILL.md` currently frames Packet Mode as the default and Interactive Mode as one-question-at-a-time, but it does not require multi-round answer-quality checks or a comprehensive coverage matrix.
- `skills/strategy-stress-test/SKILL.md` already defines useful loophole classes such as missing evidence, hidden assumptions, contradictions, edge cases, dependency/order problems, security/privacy/reliability risks, verification gaps, and user decisions required.
- `skills/test-document-generator/SKILL.md` provides a peer pattern for source-grounded test plans, critical-gap blocking, and stress-test before persistence.
- `openspec/specs/aili-four-command-lifecycle/spec.md` requires DEFINE to create/update `interview.md` and blocks BUILD until spec, questionnaire, and test-plan gates are confirmed, waived, or accepted as `UNVERIFIED`.
- User requirement: “采访不止一轮…写完了但是有歧义…不能开始工作…不用小修，直接完整修复完成…问题不要少而狠，要全面。”

## Proposed Design

1. Add a comprehensive coverage matrix to `change-interviewer`.
   - Dimensions: goal/success, scope/non-goals, roles/permissions, happy path, failure path, retries/rollback, boundary conditions, data lifecycle, state transitions, API/CLI/UI contracts, compatibility/migration, security/privacy, performance/reliability, observability, testability/acceptance, rollout/rollback, and explicit non-goals.
   - For each dimension, classify as `Confirmed by evidence`, `Not applicable`, `Needs question`, `Open Question`, or `Unverified`.
2. Strengthen question quality rules.
   - Ask comprehensive questions, not artificially few questions.
   - Exclude generic questions that cannot change scope, design, tasks, acceptance, tests, or risk.
   - Each question must include why, impact, recommended default, consequences/trade-offs, answer slot, and write-back target.
3. Add multi-round answer ingestion.
   - After answers are filled, re-read `interview.md` from disk.
   - Classify every answer as confirmed, ambiguous, contradictory, incomplete, untestable, evidence-conflicting, out-of-scope, or `Unverified`.
   - Generate follow-up questions for unresolved items instead of silently writing vague answers into specs.
4. Add readiness gate language.
   - `READY` only when specs, interview answers, and test plan are confirmed enough for implementation.
   - `BLOCKED` when material ambiguity, contradiction, unsupported default, or untestable acceptance remains.
   - `WAIVED` only when the user explicitly waives the gate.
   - `UNVERIFIED` only when the user explicitly accepts proceeding with named unverified items.
5. Reuse `strategy-stress-test` as a mandatory quality gate.
   - Run it after draft packet generation and after filled-answer ingestion.
   - Check for missed design-changing questions, irrelevant questions, questions answerable by repo evidence, unsupported defaults, missing failure paths, missing counterexamples, and untestable acceptance.
6. Keep output placement and lifecycle boundaries unchanged.
   - OpenSpec output remains `openspec/changes/<change-id>/interview.md`.
   - Non-OpenSpec output still asks placement once.
   - No new public command is introduced.
   - User approved adding `skills/change-interviewer/references/*` during BUILD if needed for maintainability; any new reference must be task-scoped, actually referenced, and covered by missing-reference checks.

## Alternatives Considered

- Small wording tweak to question generation: rejected because it would not fix multi-round ambiguity detection or readiness gating.
- New standalone `design-grill` skill: rejected for now because it overlaps `change-interviewer` and would create another routing surface.
- Only interactive one-question-at-a-time grilling: rejected because the user explicitly wants comprehensive questions and durable interview artifacts.

## Risks and Mitigations

- Risk: interview packets become too long. Mitigation: comprehensive coverage is required, but generic/non-decision-changing questions are excluded; dimensions marked `Not applicable` do not need full questions.
- Risk: model asks users questions that repo evidence can answer. Mitigation: evidence-first rule and stress-test checks for this specific failure.
- Risk: user-filled vague answers are treated as facts. Mitigation: answer-quality classification and `BLOCKED_FOR_CLARIFICATION` gate.
- Risk: adding new skill references violates skill boundary rules. Mitigation: user has approved `skills/change-interviewer/references/*` only if needed for maintainability; any referenced path must exist and remain task-scoped.

## Rollback Plan

Revert the touched skill/protocol documentation and OpenSpec delta. No runtime state, dependency, schema, or installer changes are expected.
