[KNOWN] ## Evidence

[KNOWN] External research identified `https://github.com/affaan-m/ECC` as the primary ECC source.
[KNOWN] External research identified `https://github.com/affaan-m/ECC/tree/main/agents` as the ECC agents directory.
[KNOWN] External research found 67 Markdown agent files under that source.
[KNOWN] External research noted an ambiguity candidate, `https://github.com/sifxprime/kodelyth-ecc`, but the selected source remains `affaan-m/ECC` unless the user redirects.

[KNOWN] Local manifest evidence shows current AILI agents: `code-reviewer`, `code-scout`, `debug-investigator`, `doc-researcher`, `implementer`, `plan-auditor`, `rose`, `security-auditor`, `test-coverage-reviewer`, `test-engineer`, `pr-test-analyzer`, `ai-regression-scout`, `silent-failure-reviewer`, `browser-qa-runner`, `e2e-artifact-runner`, and `web-researcher`.
[KNOWN] Local manifest evidence shows current AILI skills include QA, testing, browser, E2E, review, security, research, documentation, planning, and language/platform development skills.

[KNOWN] Read-only local review identified first-class gaps for reverse spec mining, type-invariant review, comment accuracy review, open-source release sanitization, and agent-output evaluation.
[KNOWN] Read-only prior-art review identified ECC roles `spec-miner`, `type-design-analyzer`, `comment-analyzer`, `agent-evaluator`, `opensource-sanitizer`, and `build-error-resolver` as useful sources for AILI-native adaptations.
[KNOWN] The user later removed `type-design-analyzer` from the selected implementation package because specialized TypeScript/type-design review is expected to be low-value for their usage.
[KNOWN] The user later confirmed `harness-optimization-audit` should be included and all selected agents/skills should be default-installed workflow components.

[KNOWN] Read-only review-quality prior-art research checked three public skills: `https://github.com/sanyuan0704/sanyuan-skills/tree/main/skills/code-review-expert`, `https://alirezarezvani.github.io/claude-skills/skills/engineering-team/code-reviewer/`, and `https://github.com/laolaoshiren/claude-code-skills-zh/tree/main/skills/zh-code-reviewer`.
[KNOWN] The review-quality sources were assessed as better suited to a skill/rubric enhancement than to new default general review agents.

[KNOWN] ## Design Decisions

[KNOWN] ### Classification labels

[KNOWN] - `direct absorb`: good AILI fit as a new agent/skill with minimal adaptation and clear trigger boundaries.
[KNOWN] - `merge into existing`: useful behavior already belongs in an existing AILI agent/skill and should not become a separate role.
[KNOWN] - `needs rewrite`: useful concept exists, but the ECC form is too runtime-specific, domain-specific, broad, or risky to import directly.
[KNOWN] - `unsuitable`: not aligned with this workflow repository or not worth carrying as a ROSE/AILI component.

[KNOWN] ### No raw prompt import during DEFINE

[INFERRED] Listing and classification are enough for a BUILD decision and avoid licensing/provenance drift from prompt copying.

[KNOWN] ### Narrow force-add policy

[INFERRED] Force-adding every ignored OpenSpec artifact in the repository would mix unrelated historical changes into this task.
[KNOWN] This change force-adds only task-scoped OpenSpec artifacts: the new ECC classification change and the immediately preceding `add-shared-agents-skills-qa-traceability` closeout artifacts.

[KNOWN] ### Refined absorption package plan

[KNOWN] The user selected the following future additions and explicitly excluded dedicated per-language agents from this package.

| Priority | Component | Kind | Source ECC role | Permission / behavior boundary | Rationale |
|---|---|---|---|---|---|
| [INFERRED] P0 | `spec-miner` | agent | `spec-miner` | [INFERRED] Read-only; extracts observed behavior and candidate OpenSpec scenarios from code/tests/docs; does not invent product requirements | [INFERRED] Fills a gap that `code-scout` does not cover because scouting locates evidence but does not produce spec candidates |
| [INFERRED] P0 | `comment-accuracy-review` | skill | `comment-analyzer` | [INFERRED] Read-only review workflow for comments/JSDoc/TODO/docs-to-code factual consistency | [INFERRED] Better as a skill than default agent because the surface is narrow and partly covered by existing review/docs skills |
| [INFERRED] P1 | `agent-evaluator` | agent | `agent-evaluator` | [INFERRED] Read-only; evaluates agent/subagent output quality, evidence quality, and overclaiming; does not redo the original task | [INFERRED] Complements `ai-regression-scout`, which finds scenarios rather than grading a delivered output |
| [INFERRED] P1 | `opensource-sanitizer` | agent | `opensource-sanitizer` | [INFERRED] Read-only; reports secrets/private paths/internal refs/license/provenance/package exposure; must not delete, publish, move files, or print secret values | [INFERRED] Fills a release/security gap not fully covered by generic security review |
| [INFERRED] P1 | `oss-release-readiness` | skill | `opensource-sanitizer` / `opensource-packager` | [INFERRED] Non-destructive checklist for npm/open-source/public-release readiness; excludes `opensource-forker` destructive behavior | [INFERRED] Captures packaging/provenance hygiene without granting publication authority |
| [INFERRED] P1 | `build-failure-repair` | skill | `build-error-resolver` | [INFERRED] Workflow skill for root-cause-first minimal repair of build/typecheck failures; implementation remains through approved edit lanes | [INFERRED] Avoids an editable resolver agent that could bypass `debug-investigator` plus `implementer` boundaries |
| [INFERRED] P1 | `code-review-quality-gates` | skill | `sanyuan code-review-expert`, `alirezarezvani code-reviewer`, `zh-code-reviewer` | [INFERRED] Review-quality rubric and test-enhancement skill; strengthens `code-reviewer`, `review-pipeline`, `test-engineer`, and fixture expectations; does not create duplicate reviewer agents | [INFERRED] Captures severity/risk/file-priority, evidence-anchored findings, Chinese report profile, and review-output regression tests |
| [INFERRED] P1 | `harness-optimization-audit` | skill | `harness-optimizer` | [INFERRED] Read-only/report-first audit of agent/skill routing, trigger noise, token/context cost, subagent parallelism, review-pipeline fan-out, false PASS risk, and evidence loss | [INFERRED] Gives a bounded way to optimize the harness after adding more agents/skills without directly editing core harness controls |

[KNOWN] The selected agents and skills are default-installed workflow components for this package.

[INFERRED] The package is not missing a mandatory ECC testing role. Optional follow-ups are optional language reviewers, `type-design-analyzer`, and `database-change-review`, but those should remain P2 or project opt-in unless user demand appears.

[KNOWN] ### Review-quality prior-art incorporation

| Source | Fit | AILI adaptation |
|---|---|---|
| [KNOWN] `sanyuan0704/sanyuan-skills` `code-review-expert` | [INFERRED] Strong rubric source | [INFERRED] Absorb severity tiers, SOLID/code-smell reminders, race/TOCTOU, boundary, swallowed-error, N+1, and removal-safety checks into review gates and test-negative-case guidance |
| [KNOWN] `alirezarezvani/claude-skills` `code-reviewer` | [INFERRED] Strong test/fixture source | [INFERRED] Absorb risk scoring, file priority, labelled fixtures, expected-output drift, and review-regression negative cases; do not import analyzer scripts as authoritative gates |
| [KNOWN] `laolaoshiren/claude-code-skills-zh` `zh-code-reviewer` | [INFERRED] Useful Chinese-output source | [INFERRED] Absorb Chinese report profile, Chinese comment/variable-name appropriateness, and English technical-term preservation; keep AILI evidence/verdict/Unverified fields mandatory |

[INFERRED] `comment-accuracy-review` remains narrow: comment/JSDoc/TODO/README factual consistency and Chinese comment appropriateness. `code-review-quality-gates` is broader: generic review rubric, output contract, severity/risk mapping, review-derived tests, and fixture/golden expectations.

[KNOWN] ### Parallelism analysis for future BUILD

[INFERRED] Shared serial scaffold: update component source-of-truth and manifest conventions once before parallel component edits, because all new agents/skills consume `manifests/rose-aili.components.json`, README provenance, and fixture expectations.
[INFERRED] Safe parallel lanes after scaffold: `spec-miner` agent, `comment-accuracy-review` skill, `agent-evaluator` agent, `opensource-sanitizer` agent, `oss-release-readiness` / `build-failure-repair` skills, `code-review-quality-gates` skill, and `harness-optimization-audit` skill can be implemented in mostly non-overlapping files if each lane returns required manifest/test/doc deltas.
[INFERRED] Serial dependency: final manifest, README/provenance, ROSE routing, review-pipeline routing, and harness fixture tests must be integrated after lanes return to avoid conflicting edits.
[INFERRED] Join point: ROSE reconciles lane outputs, checks over-trigger risks, runs focused manifest/fixture tests, then broader `npm run build`, `npm test`, and OpenSpec validation.
[INFERRED] Blockers: BUILD must not start until the updated DEFINE artifacts and test-plan/interview gate are accepted or explicitly waived.

[KNOWN] ## Alternatives Considered

[KNOWN] - Full import of all ECC agents in one BUILD package.
[INFERRED] Rejected because it would create role overlap, trigger noise, and unverified tool/runtime assumptions.

[KNOWN] - Dedicated per-language agent set for this package.
[INFERRED] Rejected for this package because current user direction excludes it and because language reviewers should be optional or demand-gated rather than default-installed.

[KNOWN] - Separate default general code-review agents from the three review-quality sources.
[INFERRED] Rejected because local `code-reviewer` and `review-pipeline` already own general review; duplicating reviewer agents would add routing noise and split final authority.

[KNOWN] - Only keep the previously absorbed QA subset.
[INFERRED] Rejected because the user explicitly requested full ECC inventory and classification.

[KNOWN] - Force-add all ignored OpenSpec directories.
[INFERRED] Rejected as too broad for this task and likely to commit stale historical artifacts.

[KNOWN] ## Risks

[KNOWN] - ECC source ambiguity remains if the user intended a fork instead of `affaan-m/ECC`.
[INFERRED] Mitigation is to record the ambiguity and rerun classification if the user names a different ECC source.

[KNOWN] - Some categories are judgment calls.
[INFERRED] Mitigation is to keep classification editable before BUILD and require explicit BUILD package approval.

[INFERRED] - New `agent-evaluator` and `opensource-sanitizer` lanes can become false-authority gates if they overstate quality, legal, or security conclusions.
[INFERRED] Mitigation is to keep them read-only, require evidence anchors, and tag unsupported claims as `Unverified`.

[INFERRED] - New `code-review-quality-gates` can over-trigger or become a second review pipeline if scoped too broadly.
[INFERRED] Mitigation is to make it a skill/rubric source for existing review components, not a new final-verdict agent or command.

[INFERRED] - New `harness-optimization-audit` can become meta-process sprawl if it tries to edit harness controls directly.
[INFERRED] Mitigation is to keep it report-first and route approved harness edits through `harness-evolution`.
