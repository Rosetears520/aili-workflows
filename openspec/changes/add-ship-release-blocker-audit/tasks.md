## 1. Contract and Scope

- [x] 1.1 Re-read `proposal.md`, `design.md`, `specs/aili-four-command-lifecycle/spec.md`, `interview.md`, and `test-plan.md` from disk before BUILD edits.
- [x] 1.2 Confirm or explicitly waive unresolved DEFINE gates, including audit target defaults, baseline handling, and closeout report shape.
- [x] 1.3 Record implementation boundaries: no new public top-level command, no dependency or lockfile changes, no SQLite or memory schema changes, no install-script changes, no commit/push.

## 2. SHIP Command and Lifecycle Contract

- [x] 2.1 Update `commands/ship.md` to name release-blocker audit, supported target scopes, hard stops, and output expectations.
- [x] 2.2 Update `skills/aili-delivery-flow/references/lifecycle.md` so SHIP inputs/actions/outputs include audit target selection, release-blocking categories, freshness checks, and explicit `Unverified` reporting.
- [x] 2.3 Update `skills/aili-delivery-flow/references/review-repair-loop.md` so SHIP finding classification includes `release-blocking`, `important`, `accepted risk`, `out-of-scope`, and `Unverified`.
- [x] 2.4 Update `skills/aili-delivery-flow/references/artifact-contracts.md` or closeout protocol templates only if implementation needs a dedicated release-blocker audit output field.

## 3. Documentation and Spec Consistency

- [x] 3.1 Update `docs/harness/command-lifecycle.md` to describe `/ship` as the release-blocker audit entrypoint while preserving the four-command lifecycle.
- [x] 3.2 Update `docs/harness/aili-harness-contract.md` only if the architecture contract needs an explicit SHIP blocker-audit stop rule.
- [x] 3.3 Update `README.md` usage text so `/ship` describes release-blocker audit without introducing internal-stage commands.
- [x] 3.4 Keep OpenSpec delta requirements synchronized with the implementation and do not edit archived OpenSpec changes except through archive/sync flow.

## 4. Verification and Review

- [x] 4.1 Run `openspec validate "add-ship-release-blocker-audit" --strict` after artifact creation and after implementation changes.
- [x] 4.2 Run `python scripts/harness_fixture_check.py` to ensure lifecycle/fixture smoke checks still pass.
- [x] 4.3 Run `python scripts/agents_md.py check --project .` if `AGENTS.md` or template-facing rules are touched; otherwise record why it was skipped.
- [x] 4.4 Inspect `git diff --name-only` and `git diff --check` to confirm the change is surgical and no ignored/local runtime files or unrelated edits were included.
- [x] 4.5 Run SHIP review lanes or `review-pipeline` as appropriate after implementation, including security review if command/tool-policy/security-sensitive behavior is touched.

## 5. Closeout

- [x] 5.1 Report release-blocker audit behavior, files changed, verification evidence, skipped checks, residual risks, and `Unverified` items.
- [x] 5.2 Stop before archive, push, merge, or commit unless the user explicitly approves those follow-up actions.
