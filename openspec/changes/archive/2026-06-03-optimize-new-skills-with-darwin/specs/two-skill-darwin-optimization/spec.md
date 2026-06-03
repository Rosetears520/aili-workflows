## ADDED Requirements

### Requirement: Targeted Darwin baseline for two skills
The system SHALL evaluate only `skills/explain-by-allegory/SKILL.md` and `skills/evidence-scoped-retrospective/SKILL.md` for this Darwin optimization change unless the user explicitly expands scope.

The baseline report MUST include each target skill's Darwin score, dimension-level weaknesses, generated test prompts, risk class, evaluation mode, and recommended optimization direction.

#### Scenario: Baseline precedes edits
- **WHEN** BUILD begins for `optimize-new-skills-with-darwin`
- **THEN** the system writes or updates the baseline report before editing either target `SKILL.md`

#### Scenario: Scope remains two skills
- **WHEN** the optimization target set is assembled
- **THEN** it contains only `explain-by-allegory` and `evidence-scoped-retrospective` unless the user explicitly approves expansion

### Requirement: No generated skill-directory artifacts
The system SHALL NOT create new files or subdirectories under `skills/explain-by-allegory/` or `skills/evidence-scoped-retrospective/` during this change.

Forbidden additions include `test-prompts.json`, `results.tsv`, result-card images, new `references/`, new `scripts/`, new `assets/`, logs, reports, or other generated/support artifacts.

#### Scenario: Test prompts are generated
- **WHEN** Darwin test prompts are derived for either target skill
- **THEN** they are recorded in the OpenSpec baseline report rather than written under the skill directory

#### Scenario: Optimization edit is applied
- **WHEN** an approved optimization changes a skill
- **THEN** the changed path under `skills/` is exactly that skill's existing `SKILL.md`

### Requirement: Safety-preserving score improvement
The system SHALL keep an optimization only when the target skill's total Darwin score strictly improves and safety-critical dimensions do not regress.

Safety-critical dimensions include failure-mode encoding, checkpoint design, scope boundaries, protected-edit routing, session-data safety, and anti-pattern/blacklist coverage where applicable.

#### Scenario: Score fails to improve
- **WHEN** an optimization does not strictly improve the total score
- **THEN** the system restores or revises the edit instead of accepting it as complete

#### Scenario: Safety dimension regresses
- **WHEN** total score improves but a safety-critical dimension regresses
- **THEN** the system rejects the edit unless the user explicitly accepts the risk

### Requirement: Verification proves skill-folder cleanliness
The system SHALL verify that no unrelated or generated artifacts were added under `skills/` before reporting BUILD completion.

#### Scenario: Final verification runs
- **WHEN** reporting BUILD completion for this change
- **THEN** the system inspects the final diff/status and states whether the only `skills/` changes are the two existing `SKILL.md` files

#### Scenario: Verification cannot fully run
- **WHEN** a Darwin full-test, OpenSpec validation, or diff inspection cannot run
- **THEN** the affected claim is labeled `Unverified` with the reason
