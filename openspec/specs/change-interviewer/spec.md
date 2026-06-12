# change-interviewer Specification

## Purpose
Defines the requirements-interview and write-back readiness behavior for the `change-interviewer` skill.

## Requirements

### Requirement: Comprehensive evidence-first interview coverage

`change-interviewer` SHALL generate comprehensive interview coverage for non-trivial change refinement instead of limiting itself to a small number of questions.

For each relevant coverage dimension, the interviewer MUST classify the dimension as `Confirmed by evidence`, `Not applicable`, `Needs question`, `Open Question`, or `Unverified`. Coverage dimensions MUST include goal/success, scope/non-goals, roles/permissions, happy path, failure path, retries/rollback, boundary conditions, data lifecycle, state transitions, API/CLI/UI contracts, compatibility/migration, security/privacy, performance/reliability, observability, acceptance/testability, rollout/rollback, and explicit non-goals.

The interviewer MUST NOT ask the user for information that can be reliably discovered from current code, docs, specs, tests, configs, or official sources.

#### Scenario: Repository evidence answers a coverage dimension

- **WHEN** current repository artifacts or official docs can answer a material interview point
- **THEN** `change-interviewer` records the evidence and classification instead of asking the user to provide that fact

#### Scenario: Coverage dimension is irrelevant

- **WHEN** a coverage dimension does not apply to the change
- **THEN** `change-interviewer` marks it `Not applicable` with a short reason instead of asking a generic question

### Requirement: Interview questions are decision-changing and actionable

Every material question in a `change-interviewer` packet SHALL be capable of changing scope, design, tasks, acceptance criteria, tests, risk handling, or implementation safety.

Each question MUST include why it is asked, what decision or artifact it affects, a recommended default answer when evidence supports one, the trade-offs or consequences of likely answers, the user's answer slot, and the write-back target.

#### Scenario: Question would not affect implementation readiness

- **WHEN** a candidate question is generic or cannot affect scope, design, tasks, acceptance, tests, risk, or implementation safety
- **THEN** `change-interviewer` omits the question or converts it into a non-blocking note

#### Scenario: Recommended answer is proposed

- **WHEN** `change-interviewer` proposes a recommended default answer
- **THEN** the packet explains the evidence or rationale for the recommendation
- **AND** records unresolved or weakly supported recommendations as `Open Question` or `Unverified`

### Requirement: Multi-round answer ingestion blocks ambiguous readiness

After a user fills an interview packet, `change-interviewer` SHALL re-read the on-disk artifact and classify each material answer before write-back.

Answers MUST be classified as confirmed, ambiguous, contradictory, incomplete, untestable, evidence-conflicting, out-of-scope, or `Unverified`. Material ambiguous, contradictory, incomplete, untestable, or evidence-conflicting answers MUST block write-back and BUILD readiness until clarified, explicitly waived, or explicitly accepted as `UNVERIFIED` by the user.

#### Scenario: Filled answer is ambiguous

- **WHEN** a user fills an answer that can be interpreted in materially different ways
- **THEN** `change-interviewer` records the ambiguity and creates a follow-up question round
- **AND** does not write the ambiguous answer into proposal, design, tasks, specs, acceptance criteria, or test plans as fact

#### Scenario: User accepts unverified risk

- **WHEN** the user explicitly accepts proceeding with a named unresolved or unverifiable item
- **THEN** the interviewer may mark that item `UNVERIFIED`
- **AND** the final readiness report names the accepted `UNVERIFIED` item instead of claiming it is confirmed

### Requirement: Interview packet and answer set are stress-tested before readiness

`change-interviewer` SHALL use `strategy-stress-test` as a quality gate after generating an interview packet and after ingesting a filled answer set.

The stress-test MUST check for missed design-changing questions, irrelevant questions, questions answerable by evidence, unsupported recommended defaults, missing failure paths or counterexamples, untestable acceptance criteria, and unmarked `Open Question` / `Unverified` items.

#### Scenario: Stress-test finds missing material question

- **WHEN** the stress-test finds an unresolved missing material question
- **THEN** `change-interviewer` repairs the packet or records the item as a blocker before persisting or reporting readiness

#### Scenario: Stress-test finds unsafe answer ingestion

- **WHEN** the stress-test finds that a filled answer set still contains material ambiguity, contradiction, unsupported default, or untestable acceptance
- **THEN** `change-interviewer` reports `BLOCKED_FOR_CLARIFICATION` or equivalent `BLOCKED` readiness
- **AND** produces follow-up questions instead of starting implementation

### Requirement: Interview readiness states are explicit

`change-interviewer` SHALL report interview gate state as `READY`, `BLOCKED`, `WAIVED`, or `UNVERIFIED`.

`READY` means material questions are answered, answers are coherent with evidence, and acceptance/testability is sufficient for implementation. `BLOCKED` means material ambiguity, contradiction, unsupported default, or untestable acceptance remains. `WAIVED` means the user explicitly waived the gate. `UNVERIFIED` means the user explicitly accepted named unverified items.

#### Scenario: User completed form but answers remain unclear

- **WHEN** all answer slots are filled but material ambiguity or contradiction remains
- **THEN** the interview gate remains `BLOCKED`
- **AND** BUILD does not start from the interview output
