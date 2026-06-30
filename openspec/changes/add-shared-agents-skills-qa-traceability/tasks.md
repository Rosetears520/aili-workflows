## 1. Freshness and Scope Grounding

- [x] 1.1 Re-read `AGENTS.md`, `templates/AGENTS.md`, `README.md`, `docs/opencode-setup.md`, `.gitignore`, `package.json`, `.github/workflows/*`, and current OpenSpec specs before implementation.
- [x] 1.2 Re-read `scripts/install_opencode.sh`, `src/installer.ts`, `src/manifest.ts`, `src/doctor.ts`, `manifests/rose-aili.components.json`, and related installer tests.
- [x] 1.3 Confirm `.playwright-mcp/` and any unrelated untracked/dirty paths are left untouched.
- [x] 1.4 Implement the user-confirmed source-directory relocation: `.agents/skills` becomes the canonical skill source, while any `skills/` compatibility output is generated or explicitly non-authoritative.

## 2. Manifest and Shared Skills Layer

- [x] 2.1 Extend the component manifest schema/data to describe `.agents/skills` as the canonical skill source plus OpenCode-native generated/copied targets.
- [x] 2.2 Update TypeScript manifest handling so install/package/doctor logic can consume component targets instead of relying on duplicated disk globs.
- [x] 2.3 Update `scripts/install_opencode.sh` or its compatibility path so Bash behavior stays aligned with the manifest-driven target set.
- [x] 2.4 Move repository-managed skill source into `.agents/skills` and update references, package files, docs, checks, and tests that still assume `skills/` is canonical.
- [x] 2.5 Preserve existing OpenCode-native `.opencode`/global skills, agents, commands, and config behavior.
- [x] 2.6 Update `package.json` package file inclusion if `.agents/skills` or manifest target metadata must ship in the npm package.
- [x] 2.7 Update docs to distinguish source files, shared `.agents/skills` outputs, and OpenCode-native outputs.

## 3. QA/Testing Agents and Skills

- [x] 3.1 Add `agents/test-coverage-reviewer.md` with read-only coverage-gap review behavior and evidence output.
- [x] 3.2 Add `agents/pr-test-analyzer.md` for change-level test quality analysis.
- [x] 3.3 Add `agents/ai-regression-scout.md` for AI-regression failure modes.
- [x] 3.4 Add `agents/silent-failure-reviewer.md` for swallowed errors, unsafe fallbacks, and hidden failure paths.
- [x] 3.5 Add `agents/browser-qa-runner.md` with browser/manual evidence boundaries and artifact placement gates.
- [x] 3.6 Add `agents/e2e-artifact-runner.md` with E2E journey/artifact/flakiness boundaries.
- [x] 3.7 Add matching skills for coverage review, PR test analysis, AI regression testing, silent failure hunting, browser QA, and E2E artifact handling.
- [x] 3.8 Update `agents/rose.md`, `review-pipeline`, and subagent routing guidance to call these lanes only when relevant and with correct ownership (`subagent:review` or `subagent:test`).
- [x] 3.9 Add trigger/near-miss tests or static checks to prevent QA lane over-triggering where practical.

## 4. Code-Spec Traceability Absorption

- [x] 4.1 Add requirement/decision/risk → task/package → file/artifact → verification/evidence mapping to relevant lifecycle references.
- [x] 4.2 Update `tasks.md`/BUILD package guidance so each implementation package names files/artifacts and verification commands.
- [x] 4.3 Update `test-plan` guidance so the requirements-test traceability matrix is mandatory for formal changes.
- [x] 4.4 Add SHIP spec coverage check guidance before readiness claims.
- [x] 4.5 Ensure unresolved traceability gaps are labeled `Open Question` or `Unverified`, not silently treated as covered.

## 5. AGENTS Freshness and Local Docs

- [x] 5.1 Update `templates/AGENTS.md` / root `AGENTS.md` handling so the reusable template remains generic while this repo's `AGENTS.md` facts match current repo reality.
- [x] 5.2 Regenerate or update root `AGENTS.md` through the documented generated-source path/check semantics.
- [x] 5.3 Update `scripts/agents_md.py` checks if needed to catch stale project facts.
- [x] 5.4 Update README/setup docs for `.agents/skills`, manifest authority, QA lane catalog, and CodeGraph readiness.

## 6. CodeGraph Readiness

- [x] 6.1 Update doctor/setup output to report project-local CodeGraph status separately from core install status.
- [x] 6.2 Ensure CodeGraph init is offered only for the confirmed current repository root and is not run implicitly during DEFINE.
- [x] 6.3 Confirm `.codegraph/` remains ignored and no graph index artifacts are staged or packaged.

## 7. DeerFlow Skill Pattern Absorption

- [x] 7.1 Update skill-authoring guidance with trigger evals, near-miss examples, progressive disclosure, validation loop patterns, and upstream provenance requirements.
- [x] 7.2 Update research/report skills or protocols with synthesis-over-listing, source quality, confidence, disagreement, gap, and data authenticity expectations.
- [x] 7.3 Record upstream provenance policy for DeerFlow/ECC/Code-Spec-inspired or copied content, including license notices where required.
- [x] 7.4 Add the user-confirmed DeerFlow scope: workflow/meta/research/report/data-authenticity patterns, `academic-paper-review`, `systematic-literature-review`, `newsletter-generation`, `frontend-design` anti-generic UI rules, and `web-design-guidelines` UI audit ideas.
- [x] 7.5 For any copied or closely paraphrased upstream content, perform only the smallest necessary AILI/OpenCode adaptation of placeholders, tool names, paths, and branding; do not import DeerFlow runtime assumptions.

## 8. Tests and Verification

- [x] 8.1 Run `openspec validate add-shared-agents-skills-qa-traceability --strict` after spec changes.
- [x] 8.2 Run `npm run typecheck` after TypeScript changes.
- [x] 8.3 Run `npm test` after installer/manifest/package changes.
- [x] 8.4 Run `npm run build` if package or TypeScript source changes.
- [x] 8.5 Run `bash -n scripts/install_opencode.sh` after Bash installer changes.
- [x] 8.6 Run `python -m py_compile scripts/harness_fixture_check.py scripts/agents_md.py` after Python check changes.
- [x] 8.7 Run `python scripts/harness_fixture_check.py` after command/skill/harness fixture changes.
- [x] 8.8 Run `python scripts/agents_md.py check --project .` after AGENTS/template changes.
- [x] 8.9 Run `npm pack --dry-run` if package files or shipped component paths change.
- [x] 8.10 Inspect the final diff for unrelated `.playwright-mcp/`, `.codegraph/`, generated indexes, unprovenanced upstream prompts/code, secrets, and unintended public command additions.

## 9. Review and Closeout

- [x] 9.1 Run post-implementation code review, test review, and security review lanes for installer/manifest/agent/skill changes.
- [x] 9.2 Include specialized QA lanes in review only where their triggers match the implemented diff.
- [x] 9.3 Update `progress.txt` during BUILD and `implementation-notes.html` only for spec deviations/trade-offs/open questions if this change enters BUILD.
- [x] 9.4 Report verification evidence, remaining `Open Question` / `Unverified` items, and whether `.agents/skills` and OpenCode-native outputs are both covered.
