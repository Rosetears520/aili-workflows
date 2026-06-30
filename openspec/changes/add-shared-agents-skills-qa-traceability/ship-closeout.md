# SHIP Closeout: add-shared-agents-skills-qa-traceability

Date: 2026-06-29
Mode: `/ship`
Backend: OpenSpec
Branch observed: `main` (user previously authorized this task's edits on `main`)

## Verdict

PASS for release readiness, with residual risks listed below.

The SHIP audit initially found release-blocking gaps in direct Bash manifest validation, doctor source-readiness reporting, stale source-path docs/artifacts, and missing closeout. Those gaps were repaired and the final verification suite passed.

No commit, push, archive, stash, destructive cleanup, or `.playwright-mcp/` inspection/deletion was performed.

## Implemented Scope Summary

- Migrated canonical repository skill sources from `skills/*` to `.agents/skills/*` while preserving OpenCode-native installed targets as `skills/<name>`.
- Made manifest data the component source of truth for agents, commands, and skills, including source paths, fallback paths, and install targets.
- Added manifest drift validation to TypeScript installer/doctor paths and direct Bash install behavior.
- Extended doctor reporting to separate core OpenCode installation, shared `.agents/skills` source readiness, manifest-vs-disk drift, root `AGENTS.md` freshness, and optional CodeGraph readiness.
- Added QA/testing subagents and matching skills for coverage review, PR test analysis, AI regression scouting, silent-failure review, browser QA, and E2E artifact handling.
- Added clean-room DeerFlow-inspired skills/patterns and README provenance notes, including `bytedance/deer-flow` in the third-party table.
- Added Code-Spec-style traceability guidance across lifecycle/test/review artifacts.
- Updated docs, harness checks, package inclusion, and OpenSpec artifacts to reflect `.agents/skills` as canonical source and `skills/<name>` as runtime install target only.

## Release-Blocking Findings Closed

| Finding | Resolution | Evidence |
|---|---|---|
| Direct Bash installer globbed repo components without manifest drift validation | `scripts/install_opencode.sh` now validates manifest/disk drift before mutation and uses `.agents/skills` as canonical skill source | Direct Bash drift tests passed in `npm test` |
| Doctor missed shared skill source, manifest drift, and AGENTS freshness reporting | `src/doctor.ts` and manifest helpers now report source readiness separately from core install status | Doctor source-readiness tests passed in `npm test` |
| Stale docs used `skills/` as repo source | Updated listed agents/skills/protocol docs to use `.agents/skills` for repo source and reserve `skills/<name>` for installed runtime targets | Harness/delegation/AGENTS checks passed |
| README missing DeerFlow provenance table row | Added Bytedance/DeerFlow provenance row and refreshed skill tree/catalog wording | `npm pack --dry-run` and docs checks passed |
| OpenSpec artifacts contained stale BUILD-time unknowns | Updated `context.md`, `proposal.md`, `test-plan.md`, `progress.txt`, and task state | `openspec validate ... --strict` passed |
| Closeout artifact missing | Created this `ship-closeout.md` after repairs and final verification | This file |

## Fresh Verification Evidence

Final post-repair command chain passed:

- `openspec validate add-shared-agents-skills-qa-traceability --strict`: PASS
- `npm run typecheck`: PASS
- `npm run build`: PASS
- `npm test`: PASS, 70 passed / 1 skipped
- `bash -n scripts/install_opencode.sh`: PASS
- `python -m py_compile scripts/harness_fixture_check.py scripts/agents_md.py scripts/delegation_protocols_check.py`: PASS
- `python scripts/harness_fixture_check.py`: PASS
- `python scripts/agents_md.py check --project .`: PASS
- `python scripts/delegation_protocols_check.py`: PASS
- `npm pack --dry-run`: PASS, tarball includes `.agents/skills`, agents, commands, docs, manifest, and built CLI package files
- `npm audit --omit=dev`: PASS, 0 vulnerabilities
- `git diff --check`: PASS

## Residual Risks / Unverified

- CodeGraph project index remains uninitialized by user instruction; graph-backed evidence is unavailable until explicit project-local init.
- Live OpenCode runtime discovery/routing was structurally verified through install/package/manifest tests, but not exercised end-to-end in a real OpenCode session.
- Existing `.playwright-mcp/` contents were intentionally not inspected, deleted, moved, or modified.
- Previous-release baseline comparison remains Unverified because no previous-release baseline artifact was provided.

## Dirty State Classification

- Task-scoped tracked changes: `.agents/skills` migration, manifest/installer/doctor/tests/docs/AGENTS/README/harness scripts, QA agents, clean-room skills, `.gitignore` hygiene, OpenSpec artifacts.
- Task-scoped untracked files: new QA/DeerFlow-inspired skill directories under `.agents/skills/*`, new QA agent markdown files under `agents/`, and this closeout artifact.
- Ignored generated/local outputs: `dist/` rebuilt by verification; `.playwright-mcp/` remains ignored local residue and untouched.

## Next User Decision

Choose whether to commit/stage, archive the OpenSpec change, or perform additional review. No push/archive/commit/destructive cleanup will be done without explicit approval.
