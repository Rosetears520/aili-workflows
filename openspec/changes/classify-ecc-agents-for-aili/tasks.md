[KNOWN] ## 1. Evidence and Inventory

- [x] [KNOWN] Identify the ECC source repository and agents directory.
- [x] [KNOWN] Enumerate the full ECC agent list from the selected source.
- [x] [KNOWN] Record source ambiguity and evidence anchors.

[KNOWN] ## 2. Classification

- [x] [KNOWN] Classify every ECC agent into `direct absorb`, `merge into existing`, `unsuitable`, or `needs rewrite`.
- [x] [KNOWN] Map merge candidates to existing AILI agents or skills.
- [x] [KNOWN] Mark runtime-specific, domain-specific, or risky agents as `needs rewrite` or `unsuitable` instead of direct import.

[KNOWN] ## 3. OpenSpec Artifacts

- [x] [KNOWN] Create proposal, design, context, tasks, test plan, classification artifact, and spec delta.
- [x] [KNOWN] Run strict OpenSpec validation.
- [x] [KNOWN] Force-add ignored OpenSpec artifacts in the scoped path after validation.

[KNOWN] ## 4. BUILD Gate

- [x] [KNOWN] Incorporate user-selected additions into the DEFINE package plan.
- [x] [KNOWN] Record that dedicated per-language agents are out of scope for this package.
- [x] [KNOWN] Record that `harness-optimization-audit` is in scope for this package.
- [x] [KNOWN] Record that selected agents and skills use the existing default-installed workflow component model.
- [x] [KNOWN] Wait for explicit BUILD approval before creating, merging, or rewriting any agents/skills.
- [x] [KNOWN] If BUILD is approved, split implementation into scaffold, parallel component lanes, and final integration/review lanes.

[KNOWN] ## 5. Future BUILD Package Queue

- [x] [INFERRED] Package A scaffold: confirm names, manifest entries, routing boundaries, README/provenance placement, and fixture test expectations.
- [x] [INFERRED] Package B agent: add read-only `spec-miner`.
- [x] [INFERRED] Package C skill: add `comment-accuracy-review`.
- [x] [INFERRED] Package D agents: add read-only `agent-evaluator` and `opensource-sanitizer`.
- [x] [INFERRED] Package E skills: add `oss-release-readiness` and `build-failure-repair`.
- [x] [INFERRED] Package F skill: add `code-review-quality-gates` and apply its rubric/test-enhancement guidance to existing review/test components.
- [x] [INFERRED] Package G skill: add `harness-optimization-audit` as report-first harness routing/cost/quality audit guidance.
- [x] [INFERRED] Package H integration: update ROSE routing, review/lifecycle docs, manifest, README/provenance, fixtures, tests, and OpenSpec progress/test-plan evidence.

[KNOWN] ## 6. BUILD Verification and Review

- [x] [KNOWN] Run strict OpenSpec validation for `classify-ecc-agents-for-aili`.
- [x] [KNOWN] Run strict OpenSpec validation for `add-shared-agents-skills-qa-traceability` while its artifacts remain staged.
- [x] [KNOWN] Run TypeScript, build, Node test, fixture, AGENTS, delegation, Bash syntax, and diff whitespace checks.
- [x] [KNOWN] Run relevant post-implementation review lanes and reconcile findings before completion.
- [x] [KNOWN] Record final verification evidence and remaining `Unverified` items in `progress.txt` / `test-plan.md`.
