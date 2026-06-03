# Design: Darwin review for two new skills

## Overview

This change reuses the repository's existing Darwin adaptation from `optimize-all-skills-with-darwin`, but narrows the target set to exactly two skills:

- `skills/explain-by-allegory/SKILL.md`
- `skills/evidence-scoped-retrospective/SKILL.md`

The design is report-first and file-clean: Darwin may inform scoring and optimization, but generated evaluation artifacts stay in the OpenSpec change package. The only allowed future edits under `skills/` are edits to the two existing `SKILL.md` files.

## Evidence Used

| Evidence | Finding | Design Impact |
|---|---|---|
| `openspec/changes/optimize-all-skills-with-darwin/proposal.md` | Prior Darwin change requires baseline first, clean skill dirs, no auto commits, no generated files under `skills/`. | Reuse these constraints for the narrower two-skill pass. |
| `openspec/changes/optimize-all-skills-with-darwin/specs/skill-optimization-workflow/spec.md` | Requirements define baseline report, clean skill directories, score-improvement threshold, and verification labels. | Mirror the same requirements with target-specific paths. |
| `skills/explain-by-allegory/SKILL.md` | New teaching skill is compact and likely low-risk, but needs Darwin scoring for failure modes/checkpoints/blacklist strength. | Evaluate and optimize only its instruction quality, not its purpose. |
| `skills/evidence-scoped-retrospective/SKILL.md` | New retrospective/self-improvement skill touches safety and workflow routing, so it is higher risk than the allegory skill. | Treat as high-risk for optimization; require explicit approval after baseline before edits. |
| Current user instruction | Only skill files may be modified, and no unrelated extra products may be added under `skills/`. | Enforce `SKILL.md`-only edits under `skills/`; reports live in OpenSpec. |

## Workflow

### Phase 1: Baseline report

1. Re-read both target `SKILL.md` files from disk.
2. Design 2-3 test prompts per skill for Darwin effect scoring.
3. Score each skill with Darwin's 9 dimensions:
   - frontmatter quality;
   - workflow clarity;
   - failure-mode encoding;
   - checkpoint design;
   - executable specificity;
   - resource integration;
   - architecture/readability;
   - tested behavior;
   - anti-pattern / blacklist coverage.
4. Write the baseline report to `openspec/changes/optimize-new-skills-with-darwin/baseline-report.md`.
5. Stop for user review before any skill edit.

### Phase 2: Scoped optimization after approval

1. Confirm which of the two skills to optimize after baseline review.
2. For each approved skill, apply the smallest safe edit to the existing `SKILL.md`.
3. Do not create any new file or directory under `skills/explain-by-allegory/` or `skills/evidence-scoped-retrospective/`.
4. Re-score the edited skill.
5. Keep the edit only if the total score improves and safety dimensions do not regress.
6. Report diff, score delta, and remaining `Unverified` items.

### Phase 3: Verification

1. Validate this OpenSpec change.
2. Inspect git status/diff to confirm the only `skills/` paths changed are the two target `SKILL.md` files.
3. Confirm no `test-prompts.json`, `results.tsv`, result cards, references, scripts, assets, or generated/support files were added under the target skill directories.
4. Confirm frontmatter names still match folders and descriptions remain narrow.

## Risk Controls

- `evidence-scoped-retrospective` is safety-sensitive because it routes workflow improvement and harness recommendations. Treat it as high-risk and require explicit approval after baseline before edits.
- Do not optimize away safety gates, non-goals, evidence boundaries, or protected-edit routing for either skill.
- Darwin `full_test` is preferred. If only dry-run/static scoring is possible, label the affected score `Unverified`.
- No automatic commit, revert, push, or archive actions are part of this change.

## Artifact Plan

| Artifact | Path | Purpose |
|---|---|---|
| Baseline report | `openspec/changes/optimize-new-skills-with-darwin/baseline-report.md` | Scores, prompts, weaknesses, optimization directions. |
| Skill edits | existing target `SKILL.md` files only | Future approved optimization output. |

## Non-Goals

- Do not add support files inside `skills/`.
- Do not update repository docs unless a later user approval expands scope.
- Do not use this change to modify the general Darwin workflow or core harness behavior.
