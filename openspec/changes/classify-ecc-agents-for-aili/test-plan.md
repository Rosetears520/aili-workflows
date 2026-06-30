[KNOWN] # Test Plan: classify-ecc-agents-for-aili

[KNOWN] ## 0. Document Metadata

[KNOWN] - Source: `openspec/changes/classify-ecc-agents-for-aili/` plus user-selected package list from `/define` input.
[KNOWN] - Branch: `main`.
[KNOWN] - Status: BUILD test document; execution evidence must be recorded after commands run.
[KNOWN] - Scope: classification, implementation-readiness contract, and the approved 8 default-installed production components.

[KNOWN] ## 1. Evidence Sources

| Source | Checked content | Observed fact | Confidence | Notes |
|---|---|---|---|---|
| [KNOWN] `context.md` | user direction and evidence anchors | [KNOWN] Selected ECC source is `affaan-m/ECC`; source ambiguity remains recorded | medium | [KNOWN] User has not explicitly re-confirmed fork choice in this turn |
| [KNOWN] `ecc-agents-classification.md` | 67-agent table and updated package plan | [KNOWN] Each ECC agent has a classification; selected package list is recorded | high | [KNOWN] Static document inspection required before BUILD |
| [KNOWN] `design.md` | decisions, parallelism, risks | [KNOWN] User excluded dedicated per-language agents and duplicate general review agents, included `harness-optimization-audit`, and selected default installation for all selected components | high | [KNOWN] Future language packs require separate approval |
| [KNOWN] local subagent evidence | local gap review, ECC prior-art review, plan audit | [KNOWN] Three read-only lanes recommended the selected additions or adjacent adjustments | medium | [KNOWN] Full ECC prompt-by-prompt legal/provenance review is not complete |
| [KNOWN] review-quality prior-art subagents | three external code-review skills | [KNOWN] Sources should feed `code-review-quality-gates` as a skill/rubric/test enhancement, not duplicate reviewer agents | medium | [KNOWN] No upstream prompt text copied |

[KNOWN] ## 2. Object Under Test and Goals

[KNOWN] Object under test: OpenSpec artifacts and production integration for `classify-ecc-agents-for-aili`.

[KNOWN] Test goals:
- [KNOWN] Verify that ECC full inventory and classification remain intact.
- [KNOWN] Verify that the selected future additions are explicitly named and bounded.
- [KNOWN] Verify that dedicated per-language agents are excluded from this package.
- [KNOWN] Verify that the three code-review prior-art sources map to `code-review-quality-gates` skill and review/test fixture enhancements.
- [KNOWN] Verify that `harness-optimization-audit` is included in the selected package.
- [KNOWN] Verify that selected agents/skills use the default-installed workflow component model.
- [KNOWN] Verify that BUILD approval is recorded before production agent/skill implementation.
- [KNOWN] Verify that the selected agents/skills are registered in the manifest, discoverable at their canonical paths, and routed by ROSE/review-pipeline where applicable.
- [KNOWN] Verify that scoped ignored OpenSpec files are staged when requested.

[KNOWN] Not fully tested in BUILD:
- [UNVERIFIED] Live OpenCode runtime routing in an actual OpenCode session.
- [UNVERIFIED] Full legal review of upstream ECC / review-skill prompt text beyond clean-room non-copying discipline.

[KNOWN] ## 3. Scope

[KNOWN] ### In Scope
- [KNOWN] Proposal/design/tasks/spec/interview/test-plan/progress consistency.
- [KNOWN] Production files for selected agents/skills.
- [KNOWN] Manifest, ROSE routing, review-pipeline routing, README/provenance, and Node tests.
- [KNOWN] Classification-to-package traceability.
- [KNOWN] OpenSpec strict validation.
- [KNOWN] Git staged path inspection for scoped ignored OpenSpec artifacts.

[KNOWN] ### Out of Scope
- [KNOWN] Live OpenCode session execution.
- [KNOWN] Publishing or npm release mutation.
- [KNOWN] Adding language-specific default agents.
- [KNOWN] Adding duplicate default general code-review agents.

[KNOWN] ### Assumptions
- [INFERRED] `affaan-m/ECC` remains the selected source unless the user redirects to another fork.
- [INFERRED] User-selected package list is the intended BUILD candidate set unless the user asks for additions/removals.

[KNOWN] ### Open Questions
- [KNOWN] None for the selected package scope after the user confirmed `harness-optimization-audit` and default installation.

[KNOWN] ## 4. Requirement-Test Traceability Matrix

| Requirement / Decision / Risk | Source | Task / Package | File / Artifact | Verification command / check | Evidence | Coverage status |
|---|---|---|---|---|---|---|
| [KNOWN] ECC source is identified | `context.md`, `design.md` | Evidence | `context.md`, `design.md` | [KNOWN] Static inspection | [KNOWN] Source URL recorded | Planned |
| [KNOWN] Full ECC agent list is included | `ecc-agents-classification.md` | Classification | `ecc-agents-classification.md` | [KNOWN] Count rows 1-67 | [KNOWN] 67 table rows expected | Planned |
| [KNOWN] Every ECC agent has one category | spec requirement | Classification | `ecc-agents-classification.md` | [KNOWN] Static inspection of category column | [KNOWN] Four allowed categories | Planned |
| [KNOWN] Selected additions are explicit | user `/define` input plus later removal of `type-design-analyzer`, review-quality skill decision, and harness audit inclusion | Package A-H | `proposal.md`, `design.md`, `tasks.md`, `ecc-agents-classification.md` | [KNOWN] Static inspection for eight names | [KNOWN] Eight selected component names expected | Planned |
| [KNOWN] Dedicated per-language agents are excluded | user `/define` input | Non-goal | `proposal.md`, `design.md`, `spec.md` | [KNOWN] Static inspection | [KNOWN] Exclusion statement expected | Planned |
| [KNOWN] Duplicate review agents are excluded | user review-source decision | Non-goal | `proposal.md`, `design.md`, `ecc-agents-classification.md` | [KNOWN] Static inspection | [KNOWN] Sources map to skill, not agents | Planned |
| [KNOWN] Review-quality tests are planned | review-quality prior art | Package F | `design.md`, `test-plan.md` | [KNOWN] Static inspection | [KNOWN] Fixtures/golden/negative cases expected | Planned |
| [KNOWN] Harness audit is included | user confirmation | Package G | `proposal.md`, `design.md`, `tasks.md`, `ecc-agents-classification.md` | [KNOWN] Static inspection | [KNOWN] `harness-optimization-audit` expected | Planned |
| [KNOWN] Selected components default-install | user confirmation | Package H | `proposal.md`, `design.md`, `tasks.md`, `spec.md` | [KNOWN] Static inspection | [KNOWN] Default-installed component model expected | Planned |
| [KNOWN] Future components have behavior boundaries | design decision | Package A-F | `design.md`, `spec.md` | [KNOWN] Static inspection | [KNOWN] Read-only/non-destructive/root-cause-first boundaries expected | Planned |
| [KNOWN] BUILD approval is recorded | lifecycle rule plus user approval | BUILD Gate | `tasks.md`, `progress.txt` | [KNOWN] Static inspection | [KNOWN] completed BUILD approval task expected | Planned |
| [KNOWN] Selected agents are manifest-registered | default install decision | Packages B/D/H | `manifests/rose-aili.components.json`, `tests/rose-aili.test.mjs` | [KNOWN] `npm test` focused manifest test | [KNOWN] 3 agent entries and files expected | Planned |
| [KNOWN] Selected skills are manifest-registered | default install decision | Packages C/E/F/G/H | `manifests/rose-aili.components.json`, `tests/rose-aili.test.mjs` | [KNOWN] `npm test` focused manifest test | [KNOWN] 5 skill entries and install targets expected | Planned |
| [KNOWN] ROSE can route new evidence/release lanes | routing decision | Package H | `agents/rose.md` | [KNOWN] Static inspection and Node assertions | [KNOWN] task allowlist and roster entries expected | Planned |
| [KNOWN] Review-pipeline can route evaluator/sanitizer/quality-gates | review decision | Package H | `.agents/skills/review-pipeline/SKILL.md` | [KNOWN] Static inspection and Node assertions | [KNOWN] lane references expected | Planned |
| [KNOWN] OpenSpec artifacts validate | OpenSpec backend | Validation | change directory | [KNOWN] `openspec validate classify-ecc-agents-for-aili --strict` | [KNOWN] Exit code must be 0 | Planned |
| [KNOWN] Production implementation stays task-scoped | BUILD scope | Scope | git diff | [KNOWN] `git status --short --branch`, `git diff --check`, review lanes | [KNOWN] Only selected agents/skills/integration/OpenSpec files expected | Planned |
| [KNOWN] Force-added OpenSpec files stay scoped | user request | Git staging | git index | [KNOWN] `git diff --cached --name-only` | [KNOWN] Only selected OpenSpec paths expected unless production files are later staged by explicit commit flow | Planned |

[KNOWN] ## 5. Test Strategy

- [KNOWN] Unit tests: Node manifest/routing tests via `npm test` after `npm run build`.
- [KNOWN] Integration tests: OpenSpec strict validation and CLI/build checks.
- [KNOWN] CLI / contract checks: manifest registration, repo install targets, fixture smoke, AGENTS template check, delegation protocol check, shell syntax, git diff inspection, and `git diff --check`.
- [KNOWN] Manual checks: verify selected component list, non-goals, boundaries, and open questions.
- [KNOWN] Regression checks: ensure prior `add-shared-agents-skills-qa-traceability` change still validates because its force-added artifacts remain staged.

[KNOWN] ## 6. Environment and Test Data

- [KNOWN] Environment: local repository `/mnt/d/works/aili-workflow`.
- [KNOWN] Test data: OpenSpec artifacts and staged git index.
- [KNOWN] No external service credentials or production data are required.

[KNOWN] ## 7. Functional Test Cases

| ID | Scenario | Preconditions | Steps | Expected result | Priority | Automation | Source |
|---|---|---|---|---|---|---|---|
| [KNOWN] F-01 | Validate OpenSpec change | artifacts updated | Run `openspec validate classify-ecc-agents-for-aili --strict` | [KNOWN] Change is valid | P0 | yes | `spec.md` |
| [KNOWN] F-02 | Verify selected additions appear | artifacts updated | Inspect proposal/design/tasks/classification | [KNOWN] Eight selected components appear and `type-design-analyzer` is not selected | P0 | manual/static | user input |
| [KNOWN] F-03 | Verify per-language agents excluded | artifacts updated | Inspect proposal/design/spec | [KNOWN] Dedicated per-language default agents excluded | P0 | manual/static | user input |
| [KNOWN] F-04 | Verify selected production files exist | BUILD implemented | Inspect files and run manifest tests | [KNOWN] 3 agents and 5 skills exist at canonical paths | P0 | yes/static | BUILD scope |
| [KNOWN] F-05 | Verify prior staged OpenSpec change remains valid | prior artifacts staged | Run `openspec validate add-shared-agents-skills-qa-traceability --strict` | [KNOWN] Change remains valid | P1 | yes | force-add scope |
| [KNOWN] F-06 | Verify review-quality prior art maps to skill | artifacts updated | Inspect design/classification/tasks | [KNOWN] Three sources map to `code-review-quality-gates`, not duplicate agents | P0 | manual/static | user input |
| [KNOWN] F-07 | Verify harness audit and default install decisions | artifacts updated | Inspect proposal/design/tasks/spec | [KNOWN] `harness-optimization-audit` included and selected components default-install | P0 | manual/static | user input |
| [KNOWN] F-08 | Verify manifest and install targets | manifest updated | Run `npm test` after build | [KNOWN] selected agents/skills are default-installed and canonical paths/install targets match existing model | P0 | yes | manifest test |
| [KNOWN] F-09 | Verify routing surfaces | ROSE/review-pipeline updated | Run `npm test` after build and static review | [KNOWN] ROSE allows/routes selected agents and review-pipeline names relevant new lanes | P0 | yes/static | routing decision |

[KNOWN] ## 8. Failure, Boundary, and Permission Tests

| ID | Type | Scenario | Input / Operation | Expected result | Risk |
|---|---|---|---|---|---|
| [KNOWN] B-01 | Scope boundary | BUILD starts without explicit approval | User asks to proceed ambiguously | [KNOWN] ROSE must ask for BUILD approval/package confirmation | Lifecycle bypass |
| [KNOWN] B-02 | Permission boundary | Future sanitizer attempts deletion/publication | Future BUILD design review | [KNOWN] Component remains read-only/non-destructive | Destructive release action |
| [KNOWN] B-03 | Trigger boundary | Future `comment-accuracy-review` over-triggers on all reviews | Future trigger validation | [KNOWN] Trigger stays limited to comments/JSDoc/TODO/doc drift | Token/routing noise |
| [KNOWN] B-04 | Source ambiguity | User intended a different ECC fork | User redirects source | [KNOWN] Re-run inventory/classification before BUILD | Wrong prior-art source |
| [KNOWN] B-05 | Review boundary | Future `code-review-quality-gates` becomes a second final review pipeline | Future design review | [KNOWN] It remains a skill/rubric source; ROSE/review-pipeline keep final reconciliation | Authority split |
| [KNOWN] B-06 | Harness boundary | Future `harness-optimization-audit` tries to edit core harness controls | Future design review | [KNOWN] It remains report-first; approved edits route through `harness-evolution` | Meta-process sprawl |

[KNOWN] ## 9. Compatibility / Migration Tests

[KNOWN] No production migration is introduced by this BUILD package.

[KNOWN] BUILD must verify manifest install paths, OpenCode installed targets, README provenance, and existing harness fixture checks after adding agents/skills.

[KNOWN] ## 10. Security / Reliability / Observability Tests

- [KNOWN] `opensource-sanitizer` static/review checks must verify secret redaction and non-destructive behavior.
- [KNOWN] `agent-evaluator` static/review checks must verify it does not redo the original task and does not claim PASS without evidence anchors.
- [KNOWN] `build-failure-repair` static/review checks must verify root-cause-first behavior and no dependency/lockfile changes without approval.
- [KNOWN] `code-review-quality-gates` static/review checks must verify severity/evidence/Unverified/verification-story output markers, negative cases, Chinese report profile, and expected-output drift handling.
- [KNOWN] `harness-optimization-audit` static/review checks must verify report-first behavior, no direct core-harness edits, routing/cost/evidence-quality coverage, and no false PASS claims.

[KNOWN] ## 11. Regression Scope

- [KNOWN] `openspec validate classify-ecc-agents-for-aili --strict`.
- [KNOWN] `openspec validate add-shared-agents-skills-qa-traceability --strict`.
- [KNOWN] `git diff --cached --check`.
- [KNOWN] BUILD regression includes `npm run typecheck`, `npm run build`, `npm test`, `python scripts/harness_fixture_check.py`, `python scripts/agents_md.py check --project .`, `python scripts/delegation_protocols_check.py`, `bash -n scripts/install_opencode.sh`, and `git diff --check`.

[KNOWN] ## 12. Automation Verification Commands

| Level | Command | Purpose | Must execute | Notes |
|---|---|---|---|---|
| OpenSpec | `openspec validate classify-ecc-agents-for-aili --strict` | [KNOWN] Validate this change | yes | BUILD closeout |
| OpenSpec | `openspec validate add-shared-agents-skills-qa-traceability --strict` | [KNOWN] Validate staged prior change | yes | force-add scope |
| Git | `git diff --cached --check` | [KNOWN] Check staged whitespace/conflict markers | yes | before report |
| Git | `git status --short --branch` | [KNOWN] Report staged scope | yes | before report |
| Git | `git diff --cached --name-only` | [KNOWN] Confirm scoped staged paths | yes | before report |
| TypeScript | `npm run typecheck` | [KNOWN] Typecheck CLI/test imports | yes | after production edits |
| Build | `npm run build` | [KNOWN] Compile CLI before Node tests | yes | after production edits |
| Node tests | `npm test` | [KNOWN] Run manifest/routing and installer regression tests | yes | after build |
| Fixture | `python scripts/harness_fixture_check.py` | [KNOWN] Validate harness fixture command contracts | yes | after prompt/skill edits |
| AGENTS | `python scripts/agents_md.py check --project .` | [KNOWN] Validate project AGENTS template compliance | yes | after docs/rules edits |
| Delegation | `python scripts/delegation_protocols_check.py` | [KNOWN] Validate delegation protocol contracts | yes | after ROSE/subagent routing edits |
| Shell | `bash -n scripts/install_opencode.sh` | [KNOWN] Validate installer shell syntax | yes | regression gate |
| Git | `git diff --check` | [KNOWN] Check whitespace/conflict markers across unstaged/staged diff | yes | before final report |

[KNOWN] ## 13. Manual Acceptance Checklist

- [ ] [KNOWN] Confirm the ECC source is the intended one.
- [ ] [KNOWN] Confirm selected additions: `spec-miner`, `comment-accuracy-review`, `agent-evaluator`, `opensource-sanitizer`, `oss-release-readiness`, `build-failure-repair`, `code-review-quality-gates`, `harness-optimization-audit`.
- [ ] [KNOWN] Confirm selected agents/skills are default-installed workflow components.
- [ ] [KNOWN] Confirm `type-design-analyzer` remains out of scope for this package.
- [ ] [KNOWN] Confirm dedicated per-language agents remain out of scope for this package.
- [ ] [KNOWN] Confirm the three review-quality prior-art sources become skill/rubric/test enhancements, not new general review agents.
- [ ] [KNOWN] Confirm no raw ECC prompt text is copied into production components during BUILD.
- [ ] [KNOWN] Confirm force-added OpenSpec files are limited to scoped paths.
- [ ] [KNOWN] Confirm manifest, ROSE routing, review-pipeline routing, README provenance, and Node tests cover the 8 selected components.

[KNOWN] ## 14. Open Questions / Unverified

| Type | Content | Impact | Handling |
|---|---|---|---|
| [KNOWN] | `harness-optimization-audit` inclusion | [KNOWN] User confirmed it should be included | Write into package queue |
| [KNOWN] | default-installed vs optional/demand-gated status | [KNOWN] User confirmed all selected agents/skills are default-installed workflow components | Use existing component model |
| [UNVERIFIED] | Full ECC prompt-by-prompt porting/legal review is not complete | [INFERRED] This BUILD rewrites concepts rather than copying prompt text | Keep no-raw-import rule |
| [UNVERIFIED] | Full prompt-by-prompt review of the three code-review skills is not complete | [INFERRED] This BUILD extracts patterns and preserves provenance without copying upstream text | Keep no-raw-import rule |

[KNOWN] ## 15. Test Execution Record

| Run ID | Time | Executor | Level | Command / Tool | Result | Evidence | Unverified items |
|---|---|---|---|---|---|---|---|
| [KNOWN] build-local-20260630 | 2026-06-30 | ROSE | OpenSpec | `openspec validate classify-ecc-agents-for-aili --strict` | PASS | `Change 'classify-ecc-agents-for-aili' is valid` | [UNVERIFIED] Live OpenCode runtime routing |
| [KNOWN] build-local-20260630 | 2026-06-30 | ROSE | OpenSpec | `openspec validate add-shared-agents-skills-qa-traceability --strict` | PASS | `Change 'add-shared-agents-skills-qa-traceability' is valid` | [UNVERIFIED] Live OpenCode runtime routing |
| [KNOWN] build-local-20260630 | 2026-06-30 | ROSE | TypeScript | `npm run typecheck` | PASS | command exited 0 | [UNVERIFIED] Live OpenCode runtime routing |
| [KNOWN] build-local-20260630 | 2026-06-30 | ROSE | Build/Test | `npm run build && npm test` with 120s timeout | PARTIAL | `npm run build` completed; `npm test` was interrupted by tool timeout after partial passing output | [KNOWN] Superseded by 300s `npm test` rerun |
| [KNOWN] build-local-20260630 | 2026-06-30 | ROSE | Build/Test | `npm test` after boundary/regression fixes | PASS | 73 tests, 72 pass, 1 skipped, 0 fail | [UNVERIFIED] Live OpenCode runtime routing |
| [KNOWN] build-local-20260630 | 2026-06-30 | ROSE | Fixture | `python scripts/harness_fixture_check.py` | PASS | `harness fixture check: PASS (5 fixture files + command contracts)` | [UNVERIFIED] Live OpenCode runtime routing |
| [KNOWN] build-local-20260630 | 2026-06-30 | ROSE | AGENTS | `python scripts/agents_md.py check --project .` | PASS | `PASS: /mnt/d/works/aili-workflow/AGENTS.md follows /mnt/d/works/aili-workflow/templates/AGENTS.md` | [UNVERIFIED] Live OpenCode runtime routing |
| [KNOWN] build-local-20260630 | 2026-06-30 | ROSE | Delegation | `python scripts/delegation_protocols_check.py` | PASS | `PASS delegation protocol checks`; `Checked 14 files` | [UNVERIFIED] Live OpenCode runtime routing |
| [KNOWN] build-local-20260630 | 2026-06-30 | ROSE | Shell/Git | `bash -n scripts/install_opencode.sh`; `git diff --check`; `git diff --cached --check` | PASS | commands exited 0 with no output | [UNVERIFIED] Live OpenCode runtime routing |
| [KNOWN] review-local-20260630 | 2026-06-30 | subagent:review | Code review | `code-reviewer` review lane | PASS | no blocking findings; one staging-scope Suggestion | [UNVERIFIED] Live OpenCode runtime routing |
| [KNOWN] review-local-20260630 | 2026-06-30 | subagent:review | Coverage review | `test-coverage-reviewer` review lane | PASS | no blocking findings; one untracked-file inclusion Suggestion | [UNVERIFIED] Live OpenCode runtime routing |
| [KNOWN] review-local-20260630 | 2026-06-30 | subagent:review | Security review | `security-auditor` second re-review | PASS | no findings after permission/provenance/test fixes | [UNVERIFIED] Full upstream legal/provenance validation |
| [KNOWN] review-local-20260630 | 2026-06-30 | subagent:test | AI regression review | `ai-regression-scout` re-review | PASS | no findings after routing/test/docs fixes | [UNVERIFIED] Live model routing experiments |
| [KNOWN] review-local-20260630 | 2026-06-30 | subagent:review | Silent-failure review | `silent-failure-reviewer` second re-review | PASS | no findings after execution-record fixes | [UNVERIFIED] Live OpenCode runtime routing |

[KNOWN] ## 16. Defect and Retest Closure

| Bug ID | Source test | Symptom | Root cause | Fix owner | Fix files | Retest command | Retest result | Status |
|---|---|---|---|---|---|---|---|---|
| [KNOWN] None recorded | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |

[KNOWN] ## 17. Change Log

- [KNOWN] 2026-06-29: Updated test plan for user-selected ECC-derived additions and deferred per-language agents.
- [KNOWN] 2026-06-29: Added `code-review-quality-gates` as a skill/rubric/test enhancement sourced from three external code-review skills.
- [KNOWN] 2026-06-29: Included `harness-optimization-audit` and default-installed component model by user confirmation.
- [KNOWN] 2026-06-30: Updated test plan from DEFINE-only to BUILD implementation and verification scope.
