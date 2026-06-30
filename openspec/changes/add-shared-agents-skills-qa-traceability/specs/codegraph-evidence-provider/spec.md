## ADDED Requirements

### Requirement: Project-local CodeGraph readiness is explicit

AILI workflows and doctor checks SHALL report project-local CodeGraph readiness explicitly when a task may benefit from graph evidence.

Missing CodeGraph initialization SHALL NOT be treated as a successful graph-backed evidence source, and SHALL NOT block unrelated base workflow installation when search/read fallback evidence is sufficient.

#### Scenario: CodeGraph is uninitialized during planning

- **WHEN** ROSE checks CodeGraph for the current repository and the index is not initialized
- **THEN** ROSE reports CodeGraph as unavailable for that repository
- **AND** uses read/search/scouting fallback evidence where sufficient
- **AND** marks graph evidence `Unverified` only when the missing graph materially affects confidence

#### Scenario: User approves project-local initialization

- **WHEN** the user explicitly asks to initialize CodeGraph for the current repository or accepts a doctor follow-up
- **THEN** the workflow confirms the repository root before running project-local CodeGraph commands
- **AND** may run `codegraph init -i` followed by `codegraph status` for that repository only
- **AND** does not run OpenSpec initialization as part of CodeGraph initialization

#### Scenario: Graph artifacts could be committed

- **WHEN** CodeGraph initialization creates `.codegraph/` or other source-derived graph artifacts
- **THEN** those artifacts remain ignored/local and are not staged, packaged, or exposed
- **AND** doctor/SHIP checks report any accidental tracked graph artifacts as blockers
