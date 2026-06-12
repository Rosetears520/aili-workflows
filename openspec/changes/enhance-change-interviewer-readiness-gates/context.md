# Context: enhance-change-interviewer-readiness-gates

## Source Signal

User asked to fully overhaul `change-interviewer` after IDEATE/triage found the current interview output too weak, one-sided, and insufficiently useful for implementation readiness.

Exact user requirement captured during IDEATE: “采访不止一轮。我比如我写完了，但是写的有歧义，这也是不能开始工作的。不用小修，直接完整修复完成就好了。问题不要少而狠，要全面。”

## Confirmed Direction

- Use OpenSpec backend for DEFINE artifacts.
- Complete repair, not a tiny wording tweak.
- Strengthen `change-interviewer` with comprehensive multi-round interviews.
- Add ambiguity/contradiction detection after user-filled answers.
- Block implementation readiness when answers are unclear, contradictory, untestable, or evidence-conflicting.
- Include grill-style recommended answers, why/impact/trade-offs, and evidence-first rules.
- Use `strategy-stress-test` as a mandatory packet and answer-set quality gate.

## Out of Scope

- No implementation during DEFINE.
- No new public top-level commands.
- No dependency, lockfile, memory schema, installer, or OpenCode runtime config changes.
- No copying upstream `mattpocock/skills` text.
- New `skills/change-interviewer/references/*` files are allowed during BUILD if they are needed for maintainability, task-scoped, and every referenced path exists.

## Evidence Anchors

- `skills/change-interviewer/SKILL.md` currently supports evidence tables, OpenSpec `interview.md`, recommended defaults, stress-test before persistence, and answer ingestion.
- `skills/strategy-stress-test/SKILL.md` already provides loophole categories suitable for packet and answer-set quality gates.
- `skills/test-document-generator/SKILL.md` provides a peer pattern for test document critical-gap blocking.
- `openspec/specs/aili-four-command-lifecycle/spec.md` requires DEFINE interview/test-plan artifacts and blocks BUILD until gates are confirmed/waived/accepted as `UNVERIFIED`.
- `openspec/specs/skill-routing-boundaries/spec.md` requires touched skill references to exist and long skill splitting to require explicit approval.
- `strategy-stress-test` remains the owner for pure plan/design/spec/review/completion-claim stress-testing; `change-interviewer` trigger expansion, if any, must stay limited to requirements interview and write-back readiness.

## Confirmed Decisions From Filled Interview

- BUILD may add new `skills/change-interviewer/references/*` files if needed for maintainability; missing-reference checks are mandatory.
- Add requirements-interview / write-back oriented grill triggers; pure plan/design/spec/review/completion-claim stress-testing remains owned by `strategy-stress-test`.
- Coverage matrix, question threshold, recommended-default evidence, multi-round ambiguity gate, explicit waiver/`UNVERIFIED` path, and dual stress-test gate are confirmed.
- Test strategy is confirmed as OpenSpec validation plus static/manual prompt acceptance, with harness fixture/script checks only when relevant files are touched.
- Current DEFINE artifacts are confirmed as sufficient BUILD input.

## Open Questions

- Whether README and lifecycle questionnaire policy need updates after the skill prompt change; default is update only if stale/conflicting.
- Whether harness fixtures currently cover this behavior; default is update only if existing fixture checks would drift.

## Artifact Mapping

- `proposal.md`: why, scope, non-goals, likely impact.
- `design.md`: evidence, design decisions, alternatives, risks.
- `tasks.md`: implementation and verification package checklist.
- `specs/change-interviewer/spec.md`: new behavior requirements for interview coverage, question quality, multi-round ingestion, stress-test, readiness states.
- `specs/aili-four-command-lifecycle/spec.md`: modified BUILD gate behavior for ambiguous filled questionnaire artifacts.
- `interview.md`: user-facing questions and readiness gate.
- `test-plan.md`: verification matrix and acceptance checks.

## DEFINE Gate State

- 2026-06-12: `/define` selected OpenSpec backend.
- 2026-06-12: User approved continuing in current dirty working tree after git-status gate reported existing unrelated uncommitted changes.
- 2026-06-12: User filled `interview.md`; ROSE re-read from disk and classified Q1-Q10 as confirmed with no material ambiguity.
- BUILD readiness is `READY` for this OpenSpec change, pending an explicit `/build` command or equivalent current-task implementation approval.
