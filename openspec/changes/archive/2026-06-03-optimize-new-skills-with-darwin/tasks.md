# Tasks: optimize two new skills with Darwin

## 0. DEFINE Gate

- [x] Create proposal, design, spec delta, and task list.
- [x] Validate the OpenSpec change.
- [x] User confirms BUILD readiness before any skill edits.

## 1. Baseline Report

- [x] Re-read `skills/explain-by-allegory/SKILL.md` and `skills/evidence-scoped-retrospective/SKILL.md` from disk.
- [x] Generate 2-3 realistic Darwin test prompts per target skill.
- [x] Score both skills with Darwin's 9-dimension rubric.
- [x] Record evaluation mode for each score (`full_test`, `dry_run`, or `static_only`).
- [x] Write prompts, scores, weaknesses, risk class, and optimization direction to `openspec/changes/optimize-new-skills-with-darwin/baseline-report.md`.
- [x] Stop for user review before editing skill files.

## 2. Scoped Optimization After Approval

- [x] Confirm which target skill(s) the user wants optimized after reading the baseline report.
- [x] Edit only existing `skills/explain-by-allegory/SKILL.md` and/or `skills/evidence-scoped-retrospective/SKILL.md`.
- [x] Do not create any file or subdirectory under either target skill folder.
- [x] Re-score each edited skill and keep only strict score improvements with no safety-dimension regression.
- [x] Preserve each skill's core purpose and routing boundary.

## 3. Verification

- [x] Run subagent review for optimized skill diffs and safety regressions.
- [x] Run `openspec validate optimize-new-skills-with-darwin --strict`.
- [x] Inspect final git diff/status to confirm the only `skills/` changes are the approved target `SKILL.md` files.
- [x] Confirm no `test-prompts.json`, `results.tsv`, result cards, `references/`, `scripts/`, `assets/`, logs, or reports were added under `skills/`.
- [x] Confirm frontmatter `name` values still match folder names.
- [x] Report remaining `Unverified` items, including any dry-run/static-only Darwin scoring.
