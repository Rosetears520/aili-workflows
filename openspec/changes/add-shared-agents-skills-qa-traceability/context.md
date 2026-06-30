# Context: add-shared-agents-skills-qa-traceability

## Source Signal

The user first requested IDEATE research on DeerFlow, ECC, Code-Spec-Plugin, and `.agent/.agents` install conventions, explicitly asking for parallel subagent research. After the IDEATE result, the user entered DEFINE and confirmed the desired direction:

- put skills under `.agents/skills` while keeping `.opencode` behavior as-is;
- add all testing-related agents and skills, not split into first/second batches;
- absorb Code-Spec-Plugin traceability patterns;
- address the local gaps found by scouting: stale `AGENTS.md`, scattered installer logic, no `.agents` shared layer, insufficient specialized testing agents, and uninitialized CodeGraph;
- additionally inspect DeerFlow `skills/public` and decide what can be absorbed.

## Confirmed Direction

- OpenSpec backend.
- Change id: `add-shared-agents-skills-qa-traceability`.
- User explicitly authorized writing DEFINE artifacts on `main` after branch/status showed `main` with untracked `.playwright-mcp/`.
- `.agent/` singular is rejected; `.agents/skills` plural is the shared skill substrate.
- OpenCode-native installation remains preserved.
- Testing agent+skill expansion is in scope as a single change, though BUILD may still sequence implementation safely.
- Code-Spec-style traceability is in scope.
- CodeGraph initialization is not executed during DEFINE; BUILD should define doctor/readiness and optional init behavior.
- User filled `interview.md` and confirmed `.agents/skills` should be a full source migration, not only a generated mirror.
- User approved copying selected upstream content when license/provenance is handled and DeerFlow-specific placeholders or names receive minimal AILI/OpenCode adaptation.
- User confirmed this change should include workflow/meta/research/report/data-authenticity patterns plus `academic-paper-review`, `systematic-literature-review`, `newsletter-generation`, `frontend-design` anti-generic UI rules, and `web-design-guidelines` UI audit ideas.
- User confirmed `openspec/` ignored/tracking policy should not change in this change.

## Evidence Anchors

- IDEATE external research found `.agents/skills` supported by multiple tools, while `.agent/` singular is not a broad standard.
- IDEATE ECC research found useful QA/testing taxonomy: coverage review, PR test analysis, browser QA, E2E, AI regression, silent failure hunting, TDD, verification loop, and eval harness patterns.
- IDEATE Code-Spec-Plugin research found useful traceability: spec/requirement → task → files → verification → coverage check.
- DEFINE DeerFlow public skills research found high-fit patterns: trigger design, progressive disclosure, skill validation loop, evidence-first research, synthesis-over-listing, data authenticity, and report handoff discipline.
- Local scouting found installer/source-of-truth anchors in `scripts/install_opencode.sh`, `src/installer.ts`, `src/manifest.ts`, `src/doctor.ts`, `manifests/rose-aili.components.json`, `package.json`, and docs.
- Local scouting found stale generated `AGENTS.md` facts and no local `.agents/` or `.agent/` directory.
- CodeGraph status reported not initialized in `/mnt/d/works/aili-workflow`.

## Rejected / Deprioritized Options

- Do not standardize on `.agent/` singular.
- Do not replace OpenCode-native install directories with only `.agents/skills`.
- Do not copy DeerFlow/ECC/Code-Spec prompts/code without provenance, license handling, and minimal AILI/OpenCode adaptation.
- Do not run CodeGraph init during DEFINE.
- Do not add public top-level commands for testing/research beyond the existing four delivery commands.

## Decisions from Filled Interview

- Q1: `.agents/skills` is a full source migration; OpenCode-native behavior remains preserved through generated/copied/adapted targets.
- Q2: derivative copy is allowed for selected upstream skill content with license/provenance/notice handling and minimal AILI/OpenCode adaptation.
- Q3: include workflow/meta/research/report/data-authenticity patterns plus `academic-paper-review`, `systematic-literature-review`, `newsletter-generation`, `frontend-design` anti-generic UI rules, and `web-design-guidelines` UI audit ideas.
- Q4: do not change the current `openspec/` ignored/tracking policy in this change.

## Unverified Items / Residual Risks

- BUILD evidence in `progress.txt` superseded the earlier unverified exact file-set and package-inclusion items: final verification passed, package output includes `.agents/skills`, and old canonical `skills/` package/source assumptions were excluded by tests.
- CodeGraph index is absent; graph coverage remains unavailable until explicit project-local initialization.
- Live OpenCode runtime discovery/routing was structurally tested through install/package/manifest checks, but not exercised end-to-end in a real OpenCode session.
- Existing untracked `.playwright-mcp/` is unrelated and must remain untouched unless separately scoped; its contents were intentionally not inspected or deleted.

## Write-back Mapping

- `proposal.md`: rationale, scope, capabilities, impact, non-goals, BUILD readiness.
- `design.md`: architecture decisions, alternatives, risks, rollback.
- `tasks.md`: implementation and verification queue.
- `specs/aili-installer/spec.md`: `.agents/skills`, manifest authority, install/doctor behavior.
- `specs/quality-assurance-lanes/spec.md`: QA agents/skills and review/test routing.
- `specs/aili-four-command-lifecycle/spec.md`: traceability and spec coverage behavior.
- `specs/agent-operating-discipline/spec.md`: generated AGENTS freshness and upstream pattern absorption policy.
- `specs/codegraph-evidence-provider/spec.md`: CodeGraph readiness/init status behavior.
- `interview.md`: user-facing clarification packet.
- `test-plan.md`: source-grounded verification plan.

## DEFINE Gate State

- 2026-06-29: `/define` selected OpenSpec backend.
- 2026-06-29: Branch/status gate found `main` and untracked `.playwright-mcp/`; user explicitly chose “Write on main”.
- 2026-06-29: Read-only evidence lanes completed for DeerFlow public skills and local repository artifact surface.
- 2026-06-29: Proposal, design, tasks, context, spec deltas, interview, and test plan were drafted.
- 2026-06-29: User filled `interview.md`; answers were classified as confirmed and written back to proposal, design, tasks, specs, context, and test-plan.
- BUILD readiness is `READY` after strict OpenSpec validation, subject to normal BUILD git/worktree safety and the known ignored-OpenSpec artifact caveat.
