## 1. Evidence and Scope

- [x] 1.1 Re-read `skills/change-interviewer/SKILL.md`, `skills/strategy-stress-test/SKILL.md`, `skills/test-document-generator/SKILL.md`, `skills/aili-delivery-flow/references/questionnaire-policy.md`, and relevant OpenSpec specs before implementation.
- [x] 1.2 Confirm this is a harness/skill behavior repair, not product-code work and not a new top-level command.
- [x] 1.3 Confirm the implementation does not add dependencies, lockfile changes, memory schema changes, installer behavior changes, or public command entrypoints.
- [x] 1.4 If the overhaul becomes too long for a readable single `SKILL.md`, add task-scoped `skills/change-interviewer/references/*` files as approved by the user; verify every referenced path exists. No new reference file was needed.

## 2. Interview Packet Protocol

- [x] 2.1 Add a comprehensive coverage matrix covering goal/success, scope, roles/permissions, happy/failure paths, retries/rollback, boundaries, data lifecycle, state transitions, contracts, compatibility/migration, security/privacy, performance/reliability, observability, tests/acceptance, rollout/rollback, and non-goals.
- [x] 2.2 Require each coverage dimension to be classified as confirmed by evidence, not applicable, needs question, `Open Question`, or `Unverified`.
- [x] 2.3 Require every material question to include why asked, impact, recommended default answer, consequences/trade-offs, answer slot, and write-back target.
- [x] 2.4 Forbid generic questions that do not affect scope, design, tasks, acceptance criteria, tests, risk, or implementation safety.
- [x] 2.5 Preserve evidence-first behavior: if repo/docs/specs/tests/configs/official docs can answer a point, gather evidence instead of asking the user.

## 3. Multi-Round Answer Ingestion

- [x] 3.1 After a user fills `interview.md`, require disk-first re-read before answer ingestion.
- [x] 3.2 Classify answers as confirmed, ambiguous, contradictory, incomplete, untestable, evidence-conflicting, out-of-scope, or `Unverified`.
- [x] 3.3 Generate follow-up rounds for material ambiguous/contradictory/incomplete answers instead of writing them back as facts.
- [x] 3.4 Add or document `BLOCKED_FOR_CLARIFICATION` behavior for unresolved material ambiguity.
- [x] 3.5 Keep confirmed answers traceable to proposal, design, tasks, specs, acceptance criteria, and test-plan updates.

## 4. Stress-Test and Readiness Gates

- [x] 4.1 Require `strategy-stress-test` after draft packet generation and after filled-answer ingestion.
- [x] 4.2 Stress-test for missed design-changing questions, irrelevant questions, evidence-answerable questions, unsupported defaults, missing failure/counterexample coverage, and untestable acceptance.
- [x] 4.3 Define BUILD readiness states for interview gate: `READY`, `BLOCKED`, `WAIVED`, and `UNVERIFIED`.
- [x] 4.4 Ensure BUILD remains blocked unless spec, interview/questionnaire, and test-plan gates are confirmed, explicitly waived, or explicitly accepted as `UNVERIFIED`.

## 5. Documentation and Fixture Consistency

- [x] 5.1 Update README skill description only if the public summary becomes stale after the skill change. Not changed: README already has unrelated dirty edits and current public summary is not required for the gate behavior.
- [x] 5.2 Update `aili-delivery-flow` questionnaire guidance only if it conflicts with the new interviewer gate. Not changed: current policy already blocks until answers are confirmed, waived, or accepted as `UNVERIFIED` and requires disk freshness.
- [x] 5.3 Update harness fixtures/docs only if existing fixture checks cover the changed behavior or would otherwise drift. Not changed: fixtures do not cover detailed `change-interviewer` prompt behavior.

## 6. Verification

- [x] 6.1 Run `openspec validate enhance-change-interviewer-readiness-gates --strict` after OpenSpec artifact updates. PASS in BUILD verification lane.
- [x] 6.2 Run `python scripts/harness_fixture_check.py` if skill routing, command prompts, lifecycle references, or fixtures are touched. PASS in BUILD verification lane.
- [x] 6.3 Run `python scripts/agents_md.py check --project .` if `AGENTS.md` or templates are touched. PASS in BUILD verification lane because the broader dirty tree includes template/agent-script changes outside this task.
- [x] 6.4 Run `python -m py_compile scripts/harness_fixture_check.py scripts/agents_md.py` if Python scripts are touched. PASS in BUILD verification lane because the broader dirty tree includes Python script changes outside this task.
- [x] 6.5 Inspect the final diff for scope creep, copied upstream skill text, missing skill-local references, unrelated formatting, and accidental edits to existing dirty files. Scoped diff is limited to `skills/change-interviewer/SKILL.md` plus this ignored OpenSpec change directory; no new reference files or public commands were added. Existing unrelated dirty files remain outside this task.

## 7. Closeout

- [x] 7.1 Report changed files, final interview protocol behavior, verification evidence, skipped checks, and remaining `Unverified` items.
- [x] 7.2 Do not archive, commit, push, or merge unless separately approved.
