## Why

The two newly added skills, `explain-by-allegory` and `evidence-scoped-retrospective`, are now part of the workflow surface and should be reviewed with the repository's Darwin skill-quality rubric before they are treated as settled.

The previous Darwin optimization change (`openspec/changes/optimize-all-skills-with-darwin/`) already established the safe adaptation for this repository: baseline first, no automatic commits, no Darwin-generated files under `skills/`, and only existing `SKILL.md` files may be edited during optimization. This change applies that same pattern narrowly to the two new skills.

## What Changes

- Evaluate `skills/explain-by-allegory/SKILL.md` and `skills/evidence-scoped-retrospective/SKILL.md` with the Darwin 9-dimension rubric.
- Produce a baseline report under this OpenSpec change package before editing either skill.
- If optimization is approved after the baseline, edit only the two existing `SKILL.md` files.
- Do not create `test-prompts.json`, `results.tsv`, result cards, references, scripts, assets, or any other new file/subdirectory under either skill folder.
- Keep Darwin's default commit/revert ratchet disabled for this scoped optimization unless the user explicitly requests commit/push later.

## Scope

### In Scope

- `skills/explain-by-allegory/SKILL.md`
- `skills/evidence-scoped-retrospective/SKILL.md`
- A baseline/optimization report under `openspec/changes/optimize-new-skills-with-darwin/`
- OpenSpec artifacts for this proposal, design, task list, and requirements

### Out of Scope

- Adding, deleting, or renaming skills.
- Creating any new files or subdirectories under `skills/`.
- Updating README, templates, commands, agents, install scripts, memory policy, or harness docs as part of this change.
- Changing the core purpose of either skill.
- Automatic git commits, pushes, reverts, or result-card generation.

## Success Criteria

- The two target skills have a Darwin baseline score and optimization direction before skill edits.
- Generated prompts, scoring notes, and reports are kept under the OpenSpec change package, not under `skills/`.
- Any accepted optimization strictly improves the skill's score and does not regress safety-critical dimensions: failure modes, checkpoints, boundaries, or anti-pattern coverage.
- Final verification confirms only the two existing `SKILL.md` files were edited under `skills/`.

## Impact

- May modify `skills/explain-by-allegory/SKILL.md`.
- May modify `skills/evidence-scoped-retrospective/SKILL.md`.
- Adds OpenSpec change artifacts under `openspec/changes/optimize-new-skills-with-darwin/`.
- No runtime dependencies, new commands, new subagents, or new skill support files.
