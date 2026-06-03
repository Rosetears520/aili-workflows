## ADDED Requirements

### Requirement: Backend-neutral implementation notes artifact
The system SHALL maintain an `implementation-notes.html` artifact during approved spec-backed implementation work regardless of whether the active backend is OpenSpec, Superpowers-style, or custom files.

#### Scenario: Implementation begins for an OpenSpec change
- **WHEN** ROSE or an implementation worker starts applying an approved OpenSpec change
- **THEN** the implementation workflow SHALL create or update `openspec/changes/<change-id>/implementation-notes.html`
- **AND** the artifact SHALL be placed in the same OpenSpec change directory as `proposal.md`, `design.md`, and `tasks.md`

#### Scenario: Implementation begins for a Superpowers-style or custom spec
- **WHEN** ROSE or an implementation worker starts applying an approved Superpowers-style plan, custom spec, task file, or other non-OpenSpec backend
- **THEN** the implementation workflow SHALL create or update an `implementation-notes.html` artifact beside the active spec/task artifacts when the location is obvious
- **AND** if the location is not obvious, ROSE SHALL ask for an explicitly approved repository-local path before writing the artifact

### Requirement: Implementation notes content
The `implementation-notes.html` artifact SHALL record implementation-specific rationale that is useful for review, continuation, and future self-improvement analysis.

#### Scenario: Notes artifact is created
- **WHEN** the implementation workflow creates an `implementation-notes.html` artifact
- **THEN** it SHALL use simple static HTML intended for human review
- **AND** it SHALL NOT require JavaScript or external CSS dependencies
- **AND** it SHALL use the user's language by default; when the user's language is unclear, it SHALL default to Simplified Chinese for this workflow
- **AND** it SHALL include sections for title, metadata, Spec Deviations, Temporary Decisions, Trade-offs, Open Questions, Unverified Assumptions, Evidence Pointers, and Update History

#### Scenario: Implementation diverges from the plan
- **WHEN** implementation deviates from the approved spec, task plan, or expected design
- **THEN** the notes SHALL record the deviation, reason, affected files or tasks, risk, and whether the formal spec/tasks need follow-up updates

#### Scenario: Temporary decision or trade-off is made
- **WHEN** implementation makes a temporary decision, accepts a trade-off, leaves an open question, or carries an unverified assumption
- **THEN** the notes SHALL record the decision or assumption, alternatives considered when relevant, evidence pointer, owner for follow-up, and current status

### Requirement: Implementation notes safety boundary
The `implementation-notes.html` artifact SHALL be a concise implementation rationale trail and SHALL NOT store raw sensitive or high-volume evidence.

#### Scenario: Evidence includes logs, transcripts, exports, or secrets
- **WHEN** implementation evidence includes raw logs, OpenCode session exports, transcript text, secrets, credentials, cookies, tokens, private keys, private data, or full file dumps
- **THEN** the notes SHALL summarize the relevant point and cite a safe evidence pointer when possible
- **AND** it SHALL NOT include the raw sensitive or high-volume content

### Requirement: Implementation notes do not replace formal artifacts
The `implementation-notes.html` artifact SHALL supplement, not replace, the active spec, task, progress, context, handoff, ADR, test, review, or lifecycle artifacts for the chosen backend.

#### Scenario: Notes reveal a spec-level change
- **WHEN** implementation notes identify a behavior change, acceptance-criteria change, or scope decision that affects the formal contract
- **THEN** ROSE SHALL update or request approval to update the relevant formal artifact instead of treating the note as the contract
- **AND** the note SHALL link to or describe that formal follow-up state
