# requirements-grilling Specification

## Purpose

Defines the requirements-grilling, domain-modeling, interview artifact, and write-back readiness behavior for the canonical `requirements-grilling` skill.

## Requirements

### Requirement: Canonical skill name with interview artifact compatibility

`requirements-grilling` SHALL be the canonical requirements clarification skill for AILI DEFINE flows.

The skill SHALL preserve `interview.md` as the durable user-fillable OpenSpec artifact. It SHALL NOT create `grill.md`, `grilling.md`, or `requirements-grilling.md` for the same OpenSpec clarification flow unless a future accepted spec changes the artifact contract.

Old `change-interviewer` and “interview packet” triggers MAY route to the same flow for compatibility, but the system SHALL NOT expose a parallel second user-facing skill.

#### Scenario: DEFINE creates the grilling artifact

- **WHEN** an OpenSpec-backed DEFINE flow needs requirement clarification
- **THEN** `requirements-grilling` creates or updates `openspec/changes/<change-id>/interview.md`
- **AND** no parallel grill artifact is required

### Requirement: Comprehensive evidence-first grilling coverage

`requirements-grilling` SHALL generate comprehensive interview coverage for non-trivial change refinement instead of limiting itself to a small number of questions.

For each relevant coverage dimension, the skill MUST classify the dimension as `Confirmed by evidence`, `Not applicable`, `Needs question`, `Open Question`, or `Unverified`. Coverage dimensions MUST include goal/success, scope/non-goals, roles/permissions, happy path, failure path, retries/rollback, boundary conditions, data lifecycle, state transitions, API/CLI/UI contracts, compatibility/migration, terminology/domain model, security/privacy, performance/reliability, observability, acceptance/testability, rollout/rollback, and explicit non-goals.

The skill MUST NOT ask the user for information that can be reliably discovered from current code, docs, specs, tests, configs, or official sources.

#### Scenario: Repository evidence answers a coverage dimension

- **WHEN** current repository artifacts or official docs can answer a material grilling point
- **THEN** `requirements-grilling` records the evidence and classification instead of asking the user to provide that fact

#### Scenario: Coverage dimension is irrelevant

- **WHEN** a coverage dimension does not apply to the change
- **THEN** `requirements-grilling` marks it `Not applicable` with a short reason instead of asking a generic question

### Requirement: Questions are decision-changing and actionable

Every material question in a `requirements-grilling` packet SHALL be capable of changing scope, design, tasks, acceptance criteria, tests, risk handling, rollout, terminology, domain model, or implementation safety.

Each question MUST include why it is asked, what decision or artifact it affects, a recommended default answer when evidence supports one, the trade-offs or consequences of likely answers, the user's answer slot, and the write-back target.

Recommended defaults MUST cite evidence. Unsupported recommended defaults MUST be recorded as `Open Question` or `Unverified`.

#### Scenario: Question would not affect implementation readiness

- **WHEN** a candidate question is generic or cannot affect implementation readiness
- **THEN** `requirements-grilling` omits the question or converts it into a non-blocking note

#### Scenario: Recommended answer lacks evidence

- **WHEN** no current evidence supports a recommended answer
- **THEN** the packet records the field as `Open Question` or `Unverified`
- **AND** does not present the model's guess as advice

### Requirement: Domain-modeling discipline

`requirements-grilling` SHALL actively challenge terminology conflicts, fuzzy domain terms, ownership boundaries, source-of-truth conflicts, and concrete boundary scenarios.

Resolved project-specific terms SHALL be recorded in the change-local `context.md` Language section with tight definitions and `_Avoid_` alternatives. The Language section SHALL NOT absorb implementation decisions, generic programming terms, scratchpad notes, or architecture rationale.

#### Scenario: Term is resolved during grilling

- **WHEN** the user and model resolve a material project-specific term
- **THEN** `requirements-grilling` updates `context.md` Language with the canonical term, tight definition, and avoided alternatives
- **AND** keeps decision rationale outside the glossary

### Requirement: ADR gate

`requirements-grilling` SHALL create or update `adr.md` only for decisions that are hard to reverse, surprising without context, and involve a real trade-off.

`adr.md` MUST remain `Status: Proposed` unless the user or accepted change authority explicitly confirms the decision as accepted.

#### Scenario: ADR gate fails

- **WHEN** a clarified answer is not hard to reverse, surprising without context, and a real trade-off
- **THEN** `requirements-grilling` does not create an ADR for that answer

### Requirement: Multi-round answer ingestion blocks ambiguous readiness

After a user fills an interview packet, `requirements-grilling` SHALL re-read the on-disk artifact and classify each material answer before write-back.

Answers MUST be classified as confirmed, ambiguous, contradictory, incomplete, untestable, evidence-conflicting, out-of-scope, terminology-conflicting, or `Unverified`. Material ambiguous, contradictory, incomplete, untestable, evidence-conflicting, terminology-conflicting, or out-of-scope answers MUST block write-back and BUILD readiness until clarified, explicitly waived, or explicitly accepted as `UNVERIFIED` by the user.

#### Scenario: Filled answer is ambiguous

- **WHEN** a user fills an answer that can be interpreted in materially different ways
- **THEN** `requirements-grilling` records the ambiguity and appends a follow-up question round to `interview.md`
- **AND** does not write the ambiguous answer into proposal, design, tasks, specs, acceptance criteria, Language, ADR, or test plans as fact

#### Scenario: User accepts unverified risk

- **WHEN** the user explicitly accepts proceeding with a named unresolved or unverifiable item
- **THEN** the skill may mark that item `UNVERIFIED`
- **AND** the final readiness report names the accepted `UNVERIFIED` item instead of claiming it is confirmed

### Requirement: Packet and answer set are stress-tested before readiness

`requirements-grilling` SHALL use `strategy-stress-test` as a quality gate after generating an interview packet and after ingesting a filled answer set.

The stress-test MUST check for missed design-changing questions, irrelevant questions, questions answerable by evidence, unsupported recommended defaults, missing failure paths or counterexamples, untestable acceptance criteria, terminology/domain-model conflicts, ADR misuse, and unmarked `Open Question` / `Unverified` items.

#### Scenario: Stress-test finds unsafe answer ingestion

- **WHEN** the stress-test finds material ambiguity, contradiction, unsupported default, untestable acceptance, terminology conflict, or ADR misuse
- **THEN** `requirements-grilling` reports `BLOCKED_FOR_CLARIFICATION` or equivalent `BLOCKED` readiness
- **AND** produces follow-up questions instead of starting implementation

### Requirement: Readiness states are explicit

`requirements-grilling` SHALL report gate state as `READY`, `BLOCKED`, `WAIVED`, or `UNVERIFIED`.

`READY` means material questions are answered, answers are coherent with evidence, domain language is not contradictory, and acceptance/testability is sufficient for implementation. `BLOCKED` means material ambiguity, contradiction, unsupported default, terminology conflict, or untestable acceptance remains. `WAIVED` means the user explicitly waived the gate. `UNVERIFIED` means the user explicitly accepted named unverified items.

#### Scenario: User completed form but answers remain unclear

- **WHEN** all answer slots are filled but material ambiguity or contradiction remains
- **THEN** the requirements-grilling gate remains `BLOCKED`
- **AND** BUILD does not start from the interview output
