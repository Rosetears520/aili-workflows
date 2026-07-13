---
name: review-pipeline
description: Orchestrates post-implementation review before final PASS. Use after non-trivial changes to fan out only relevant code, test, security, coverage, PR-test, AI-regression, silent-failure, convergence, browser-QA, E2E-artifact, agent-output, or OSS-sanitizer lanes, reconcile findings, run a bounded fix loop, and gate completion without pushing or merging.
---

# Review Pipeline

## Purpose

Use this skill after non-trivial implementation and before ROSE claims `PASS`, `ready`, or equivalent acceptance.

It is an orchestration workflow, not a reviewer persona. ROSE owns dispatch, reconciliation, and final acceptance.

Apply the global Evidence-Driven Claim Hygiene rule while reconciling review lanes: internal lane packets/results use English claim tags and `CONFIDENCE: HIGH | MED | LOW | VERY LOW | UNKNOWN`; user-facing review/readiness conclusions use the user's language with localized tags/confidence labels when available. Do not remove `Unverified` or localized uncertainty without new evidence.

In the AILI lifecycle, this skill is normally entered from `aili-delivery-flow` SHIP mode; keep lifecycle gates there and keep this file focused on review orchestration.

## When to Use

Use after changes that are multi-file, behavior-changing, security-sensitive, permission-related, test-heavy, release-impacting, or hard to verify by a single narrow command.

Do not use for tiny documentation or one-line edits where diff inspection and a narrow check are sufficient.

## Workflow

### Upstream orchestration lessons activated

The local review gate and this pipeline adapt MIT-licensed ECC orchestration and addyosmani review patterns through `.agents/skills/local-review-gate/references/orchestration-adaptation.md` and `addyosmani-code-review-rubric.md`: main-agent-only orchestration, no router personas, parallel fan-out only for independent evidence lanes, fail-closed incomplete review, blocking/advisory split, dedupe, adversarial verification for Critical/Important findings, and user-driven lifecycle pipelines. Do not import public `multi-*` commands, `.claude` paths, Claude-only teams/tools, Codex/Gemini runtime dependencies, or remote mutation defaults.

### Phase 1: Identify Review Target

Collect:

- original user goal and accepted scope
- changed files and diff range
- acceptance criteria
- formal-change traceability mapping from requirement/decision/risk to task/package, files/artifacts, verification/evidence, and coverage status when applicable
- verification commands already run and results
- known skipped checks or `Unverified` items

### Phase 2: Fan Out Review

Dispatch only relevant review/test lanes; none are always-on:

🔴 CHECKPOINT before dispatch: review lanes must be read-only, test runner lanes must be bounded to the approved verification target, and every lane must be relevant to the changed surface and given the same review target, accepted scope, diff/files, verification evidence, artifact placement constraints, data-mutation constraints, and stop conditions. Do not dispatch security, QA, or test lanes away when the changed surface makes them relevant. Every Package 12 final-review packet must deny nested task dispatch, and each lane must return independently and directly to ROSE.

- `code-reviewer`: correctness, maintainability, architecture, performance, and context adequacy
- `test-engineer`: ordinary product-code test design/writing/execution, coverage gaps, test quality, and verification story
- `ai-regression-scout`: prompt, agent, skill, model/tool routing, harness-fixture, and generated-output regression scenarios; it does not replace `test-engineer` for ordinary product-code tests. When both surfaces change, dispatch both with distinct evidence questions.
- `security-auditor`: auth, permissions, secrets, command execution, network, dependency, deployment, schema, or data risk
- `test-coverage-reviewer`: coverage adequacy or untested-path review when verification sufficiency is uncertain
- `pr-test-analyzer`: PR/diff test impact, changed-test review, CI-log interpretation, and focused command matrix recommendations
- `ai-regression-scout`: prompt, agent, skill, model/tool routing, harness fixture, or generated-output regression scenario scouting
- `silent-failure-reviewer`: false-success, swallowed-error, skipped-gate, partial-artifact, stale-evidence, or misleading-report risk review
- `convergence-reviewer`: formal-change, OpenSpec, multi-phase, or harness-sensitive convergence review that compares proposal/design/tasks/specs/interview/test-plan/context/progress/drift or legacy implementation notes/final diff/review/verification evidence; it is read-only and is not final PASS authority
- `browser-qa-runner`: local browser UI, DOM/accessibility, console/network, and screenshot evidence when UI/browser behavior changed
- `e2e-artifact-runner`: E2E trace, video, screenshot, report, or failure-bundle evidence when durable artifacts are needed
- `agent-evaluator`: quality, evidence, claim-hygiene, scope-fit, and handoff-usability review only for disputed, critical, acceptance-blocking, or user-requested agent/subagent outputs; do not evaluate every lane by default
- `opensource-sanitizer`: public/npm/open-source exposure, prompt exposure, package exposure, secrets/private-data redaction, and provenance risk review for public or release-facing changes
- `oss-release-readiness`: non-destructive public/npm release checklist for package metadata, provenance, included files, dry-run evidence, and consumer readiness when the user asks whether a repository/package is ready to publish or open-source
- `code-review-quality-gates`: optional rubric overlay for severity, evidence anchors, negative test cases, Chinese review profile, and fixture/golden-output drift classification; it is not a separate final reviewer
- `code-scout`: context mining only when a reviewer reports missing repository context

When the changed surface is cross-file, high-risk, or likely to miss callers/consumers/tests, ROSE may request optional CodeGraph-assisted residual impact evidence for the exact current repository root from the relevant review/test lane or scout. Confirm the root per operation; any initialization needs separate approval for that one root, while batch/multi-repository initialization is refused even under broad approval. Treat it as scope discovery only; stale/noisy/unavailable evidence falls back to ordinary search/read, reviewers and testers must still read final critical files and inspect the diff, tests, commands, or behavior before conclusions, and a gap becomes `Unverified` only when material to confidence. CodeGraph never supplies lifecycle, correctness, completion, or readiness authority.

Do not ask reviewers to edit files. Do not let reviewers spawn nested agents except where their own agent contract explicitly allows `code-scout`. Browser/E2E lanes must avoid production data mutation and must not write user-visible screenshots, traces, videos, reports, or bundles until ROSE/user provides a repository-local artifact path; otherwise keep evidence inline/ephemeral and mark durable artifacts `Unverified`.

For Package 12 or another formal final convergence pass, policy requires a final-review overlay stricter than ordinary lane capability: every final-review subagent, including `test-engineer`, receives explicit `edit: deny` and `task: deny`, may not mutate tests or other files, and returns directly to ROSE. Declarative frontmatter, fixture fields, and packet text do not prove runtime enforcement; retain `UV-001` as `Unverified` until an executable runtime permission probe demonstrates the effective overlay. Dispatch independent diverse lanes in parallel where scopes do not conflict: canonical convergence, code, test/coverage, security, AI regression, silent failure, generated/docs/manifests, and other specialists justified by the final diff. Missing or empty required lane evidence blocks reconciliation; do not replace a missing lane with adjacent-lane confidence.

### Shared result envelope

Every review, test, security, coverage, convergence, evaluator, or focused-recheck lane returns the canonical envelope from `.agents/skills/aili-delivery-flow/references/protocols/subagent-result.md`. Each finding includes stable `finding_id`, `source`, `claim`, `severity`, `evidence_anchors`, `affected_requirement`, worker `proposed_disposition`, `required_action`, and `verification`; the result also names inspected scope, checks, freshness, skipped checks, blockers, and `Unverified` items. Worker dispositions are proposals only. ROSE owns final disposition and acceptance.

A no-finding lane still returns the complete no-findings envelope. A disputed, blocking, cross-session, or materially inconsistent finding references exactly `openspec/changes/<change-id>/review-arbitration.md`, preserving the finding, counter-evidence, and disposition history. Do not create that artifact for routine agreement or in advance of a real qualifying dispute.

### Phase 3: Reconcile

Merge duplicate findings and classify each as:

- Critical: blocks acceptance or could cause data loss, security exposure, broken behavior, or irreversible workflow damage
- Important: should be fixed before acceptance unless user explicitly accepts the risk
- Suggestion: non-blocking improvement or follow-up

Name conflicts between reviewers and resolve them with evidence. If evidence is insufficient, mark the item `Unverified` instead of approving it. Never use majority voting, lane counts, or averaged confidence. A credible material minority finding remains open until fixed and rechecked, refuted with counter-evidence, accepted as a named risk by the authorized owner, or blocked as `Unverified`.

For Critical or Important findings, run an adversarial verification pass during reconciliation: check cited context, tests, types, existing guards, and project rules for disproof before keeping the item blocking. Findings that cannot be verified but could hide security, data-loss, broken-behavior, or irreversible workflow damage remain blocking until checked or explicitly accepted. Refuted or low-risk items move to advisory notes.

For formal changes, reconcile review findings against the traceability mapping: each accepted requirement, decision, or risk should have implementation files/artifacts plus verification, review, and security evidence or an explicit skip reason. Missing coverage is `Open Question` when a decision is needed, or `Unverified` when evidence is missing.

When a convergence lane runs, reconcile its `missing`, `partial`, `contradicts`, `unrequested`, `pseudo-complete`, `unchecked-task`, `stale-progress`, and `evidence-gap` labels against the report before accepting any local-review or lifecycle PASS claim. Convergence evidence can block or require repair/re-review, but it does not make its own final PASS authoritative.

🔴 CHECKPOINT before accepting reconciliation: each blocker must be fixed, disproven with cited evidence, or explicitly accepted by the user. ROSE remains responsible for the final gate; reviewers provide evidence and recommendations, not final PASS.

| Reconciliation failure | Required action | Do not do |
|---|---|---|
| Reviewers disagree on severity or correctness | Read cited evidence, classify by user scope and acceptance criteria, and request one focused follow-up only if needed | Average the opinions or choose the convenient result |
| A finding has no concrete evidence | Mark `Unverified` and ask for bounded evidence if it affects acceptance | Treat reviewer confidence as proof |
| A security/test lane reports missing context | Dispatch `code-scout` or a focused re-check for that context | Let ROSE invent context or waive the gate silently |
| Fix verification passes but reviewer concern remains plausible | Re-run only the relevant reviewer lane with the new diff and evidence | Claim PASS from the command result alone |
| Graph-assisted residual scan finds high-risk targets not inspected | Inspect or dispatch the responsible lane for those targets, or mark them `Unverified` | Treat graph output alone as proof of impact or safety |

### Phase 4: Fix Loop

If blocking issues exist:

1. Send a bounded work package to `implementer` or fix directly when the edit is small and safe.
2. Run the narrowest verification that proves the fix.
3. Re-run only the relevant reviewer pass.
4. 🛑 STOP after three non-converging loops on the same finding class; report `BLOCKED_VERIFICATION` or `BLOCKED_REVIEW` with the attempts, evidence, and remaining decision needed.

For the formal Package 12 gate, the budget is at most three holistic repair/retest/re-review cycles total, not three per finding or lane. Each cycle may repair all in-scope findings, then must rerun affected lanes and the complete task matrix. A fourth cycle, dropped minority finding, reduced matrix, or manufactured pass is forbidden.

### Phase 5: Completion Gate

Return `PASS` only when blocking issues are resolved, disproven with evidence, or explicitly accepted by the user. Do not support a formal-change `ready` claim until the spec coverage check has no uncovered item except items explicitly reported as accepted `Open Question` or `Unverified` risk.

Never push, create PRs, merge, delete branches, or clean worktrees from this skill without explicit user approval.

For `complete-aili-workflow-orchestration`, the existing `agents/convergence-reviewer.md` is the sole canonical all-74-task completeness owner. `plan-auditor` remains pre-implementation and `silent-failure-reviewer` remains complementary. Package 1–11 savepoints are lightweight traceability only; Package 12 is the sole mandatory convergence gate.

## Output Contract

```text
REVIEW PIPELINE STATUS: PASS | NEEDS_FIXES | BLOCKED | SKIPPED
CONFIDENCE: HIGH | MED | LOW | VERY LOW | UNKNOWN

REVIEW TARGET:
- Diff/files:
- User goal:
- Traceability/spec coverage:
- Verification already run:

SKIPPED CHECKS:
- <check/lane not run> - <explicit reason or N/A>

FINDINGS:
- [Critical|Important|Suggestion] source - finding - evidence - required action

FIX LOOP:
- <fixes applied and verification, or N/A>

REMAINING UNVERIFIED:
- <item or N/A>

COMPLETION GATE:
- Safe to claim PASS: yes | no | conditional
- Reason:
```
