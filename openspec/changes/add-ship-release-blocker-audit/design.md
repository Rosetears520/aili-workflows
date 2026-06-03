## Context

`/ship` is the existing AILI mode for release-readiness review, repair, verification, and closeout. Current evidence shows the harness already forbids stale ready claims and keeps `/ideate`, `/define`, `/build`, and `/ship` as the only public delivery commands, while review/test/security and repair remain internal stages. The missing piece is explicit language for a release-blocker audit that answers the user's practical question: whether the selected change, diff, baseline comparison, or broader codebase state contains bugs or risks that should block handoff, merge, archive, or release.

## Goals / Non-Goals

**Goals:**

- Make release-blocker audit a named SHIP activity.
- Define target-scope selection so `/ship` can inspect a specific proposal/change, current diff, baseline comparison, or broader repository scan without guessing.
- Define release-blocking categories: user-impacting regressions, security exposure, permission/trust issues, unsafe operations, data-loss risk, artifact inconsistency, stale or missing evidence, unresolved review/test/security findings, and unverified acceptance criteria.
- Preserve fresh-evidence and explicit `Unverified` reporting requirements.
- Keep this as part of the existing `/ship` flow and `aili-delivery-flow` references.

**Non-Goals:**

- Do not add a new public top-level command for review, bug audit, security scan, or release-blocker checking.
- Do not add a new skill unless implementation evidence proves the existing SHIP/review-pipeline split cannot express the behavior.
- Do not change `/build` implementation gates except where SHIP needs to decide whether BUILD evidence is fresh or stale.
- Do not implement runtime code, dependency changes, lockfile changes, memory schema changes, install script changes, or automated scanning tools as part of this DEFINE proposal.

## Decisions

1. **Use `/ship` as the user-facing entrypoint.**
   - Rationale: repository rules and docs already define only four top-level delivery commands, and `/ship` already owns release-readiness.
   - Alternative considered: create a separate review/audit command. Rejected because current lifecycle explicitly treats review, repair, debug, and related stages as internal.

2. **Represent release-blocker audit as a SHIP sub-stage, not a standalone skill.**
   - Rationale: `aili-delivery-flow` is the lifecycle authority and already routes SHIP review/repair/closeout. The existing `review-pipeline` can remain an internal reviewer orchestration helper.
   - Alternative considered: create a `release-blocker-audit` skill. Deferred unless implementation discovers repeated logic that does not belong in SHIP references or review-pipeline.

3. **Default audit target should be the current resolved change/final diff.**
   - Rationale: this is the smallest safe default and aligns with existing SHIP inputs: implementation result, BUILD evidence, review targets, verification commands, and closeout expectations.
   - Alternative considered: scan the whole codebase by default. Rejected as too broad and expensive; reserve it for explicit request, risk triggers, or absent narrower target.

4. **Baseline and full-codebase modes require explicit target or risk trigger.**
   - Rationale: comparing with a previous release or scanning the full repository requires a known baseline, release marker, or accepted broader scope. Without that, findings and verification boundaries become ambiguous.

5. **Finding classification must drive release-readiness.**
   - Rationale: SHIP must separate release-blocking issues from important/non-blocking findings, accepted risks, out-of-scope items, and `Unverified` gaps before claiming ready.

## Risks / Trade-offs

- [Risk] Over-broad audits could make `/ship` slow or noisy. → Mitigation: default to current resolved change/final diff; broaden only when requested or risk-triggered.
- [Risk] The term “bug” may be too narrow for release readiness. → Mitigation: use “release-blocker audit” and include user-impacting defects, security exposure, unsafe operations, data risk, and evidence gaps.
- [Risk] SHIP could duplicate BUILD review/test/security gates. → Mitigation: SHIP checks freshness and reruns only stale or scope-affected lanes rather than blindly repeating all BUILD work.
- [Risk] Baseline comparison is under-specified. → Mitigation: require a named baseline/previous-release reference, otherwise mark baseline audit as `Open Question` or `Unverified`.
- [Risk] Full-codebase scan may imply a guarantee of exhaustive absence of bugs. → Mitigation: report scanned scope, evidence limits, and residual `Unverified` items; do not claim exhaustive safety.

## Migration Plan

1. Update `/ship` command wording to name release-blocker audit and target-scope handling.
2. Update SHIP lifecycle and review-repair references with audit stages, categories, freshness rules, and classification output.
3. Update closeout/artifact docs only if the new audit status needs an explicit output field.
4. Update README/harness docs to keep public-command guidance consistent.
5. Run OpenSpec validation plus existing harness smoke checks.
6. Rollback by reverting the command/reference/docs changes and keeping `/ship` on its prior release-readiness wording.

## Open Questions

- Open Question: Should `/ship` ask the user to choose an audit target when multiple plausible targets exist, or should it prefer current final diff and mark broader scans as optional?
- Open Question: What baseline name or release marker should be used when the user asks for “和上次发版对比” and no release tag/commit is supplied?
- Open Question: Should closeout reports add a dedicated `release_blocker_audit` section, or is the existing review/repair status enough once wording is clarified?
