## MODIFIED Requirements

### Requirement: BUILD is gated by confirmed or waived DEFINE artifacts

BUILD SHALL NOT start from DEFINE output unless the relevant spec, questionnaire, and test-plan gates are confirmed, explicitly waived, or marked with an explicit unverified status accepted by the user.

For interview/questionnaire artifacts produced through `change-interviewer`, a filled interview form alone SHALL NOT satisfy the questionnaire gate. The interview gate MUST remain blocking when material answers are ambiguous, contradictory, incomplete, untestable, unsupported by required evidence, or in conflict with repository/docs/spec evidence, unless the user explicitly waives the gate or accepts the named unresolved item as `UNVERIFIED`.

#### Scenario: Missing questionnaire blocks build

- **WHEN** BUILD is requested and the questionnaire gate is still unresolved
- **THEN** the system stops and reports the missing gate instead of editing files

#### Scenario: Filled questionnaire is still ambiguous

- **WHEN** BUILD is requested after the user filled an interview packet
- **AND** material answers remain ambiguous, contradictory, untestable, unsupported, or evidence-conflicting
- **THEN** the system reports the questionnaire gate as `BLOCKED`
- **AND** asks for clarification or requires an explicit waiver / accepted `UNVERIFIED` state before implementation
