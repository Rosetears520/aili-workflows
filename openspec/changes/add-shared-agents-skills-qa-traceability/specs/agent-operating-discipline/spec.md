## ADDED Requirements

### Requirement: Generated project AGENTS facts remain fresh

Project-local `AGENTS.md` facts SHALL be kept consistent with the repository's actual tracked structure, commands, package metadata, CI, tests, and generated/local artifact rules.

When project `AGENTS.md` is generated, updates SHALL be made through the documented source template or generator path unless an emergency repair explicitly records why the generated file was edited directly.

#### Scenario: Repository structure changes

- **WHEN** the repository has tracked `src/`, tests, CI workflows, package metadata, or setup/test commands
- **THEN** generated project AGENTS facts SHALL describe those current facts accurately
- **AND** SHALL NOT retain stale initialization-era claims such as no `src/`, no tracked tests, or no CI

#### Scenario: AGENTS check runs

- **WHEN** the AGENTS template compliance check runs
- **THEN** it detects or prevents drift between generated project facts and the source template/check expectations where practical
- **AND** reports whether the generated `AGENTS.md` should be regenerated from `templates/AGENTS.md`

### Requirement: Skill authoring uses trigger and validation evidence

New or substantially revised AILI skills SHALL include concrete trigger boundaries and, where practical for high-impact skills, positive and near-miss validation prompts inspired by prior-art skill validation patterns.

#### Scenario: Specialized QA skill is added

- **WHEN** BUILD adds a specialized QA/testing skill
- **THEN** its `description` clearly states when it should trigger and what it does not own
- **AND** the implementation adds validation evidence or static checks sufficient to reduce over-triggering risk
