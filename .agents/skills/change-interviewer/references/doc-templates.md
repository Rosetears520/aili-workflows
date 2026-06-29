# Change Interviewer Document Templates

Use these as merge-in templates. Do not blindly overwrite existing author structure.

## Generic Change Document

- `## Summary`
- `## Why`
- `## Goals`
- `## Non-Goals`
- `## Scope`
- `## Success Metrics`
- `## Key Flows`
- `## Acceptance Criteria`
- `## Verification`
- `## Risks`
- `## Open Questions`

## Task Document

- A short scope and success preface when missing.
- Checkbox tasks in execution order, each with:
- `ACCEPT:` objective pass/fail condition.
- `TEST:` runnable command or manual verification steps.

## Design Document

- `## Summary`
- `## Architecture`
- `## Data Model`
- `## Interfaces`
- `## Key Flows`
- `## Failure Handling`
- `## Security & Privacy`
- `## Observability`
- `## Performance`
- `## Migration / Compatibility`
- `## Alternatives Considered`
- `## Decision Log`
- `## Open Questions`

## OpenSpec Delta-Friendly Pattern

- `## ADDED|MODIFIED|REMOVED|RENAMED Requirements`
- Each requirement:
- `### Requirement: <Name>`
- Narrative requirement text.
- At least one scenario:
- `#### Scenario: <Name>`
- `- **GIVEN** ...`
- `- **WHEN** ...`
- `- **THEN** ...`

## Traceability

Add a short table in the most relevant file when it helps implementation or review.

| Ref | Requirement | Design decision | Acceptance / Test |
|-----|-------------|-----------------|-------------------|
| R?  | ...         | ...             | ...               |
