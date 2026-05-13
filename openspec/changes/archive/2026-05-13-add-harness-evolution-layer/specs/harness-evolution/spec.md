## ADDED Requirements

### Requirement: Harness evolution report gate
The system SHALL provide a `harness-evolution` workflow that produces a structured report before any harness file is modified when a harness failure signal is observed.

Harness failure signals MUST include at least explicit user requests to change ROSE, commands, skills, subagents, memory, install scripts, or harness docs; repeated workflow failures; user corrections that indicate rule drift; subagent boundary failures; verification gate gaps; memory writeback/provenance gaps; tool-policy mismatches; middleware/hook issues; environment constraints; command lifecycle bypasses; and workflow-pattern defects.

#### Scenario: Failure signal produces report before edits
- **WHEN** an agent identifies a harness failure signal during a task
- **THEN** the agent produces a harness evolution report containing observed failure or rationale, evidence, affected component, root cause, proposed change, predicted fix, at-risk regression, verification trigger, rollback plan, unknowns, and approval status before modifying harness files

#### Scenario: No autonomous core harness edit
- **WHEN** a harness evolution report proposes a change to core harness controls such as ROSE rules, commands, skill routing, subagent contracts, memory policy, install scripts, or OpenCode hooks
- **THEN** the system MUST require explicit human approval before applying the proposed change

### Requirement: Component classification map
The system SHALL define a component map for harness failures and changes.

The component map MUST include system-rules, command, skill, subagent-config, memory, tool-policy, middleware/hooks, environment, workflow-pattern, docs/protocol, and install/setup categories, and MUST guide agents away from defaulting all fixes to `agents/rose.md`.

#### Scenario: Failure is classified to a component
- **WHEN** a harness failure report is created
- **THEN** the report records one primary affected component and any secondary components using the component map categories

#### Scenario: Rose rules are not the default target
- **WHEN** a failure could be fixed by changing a command, skill, subagent packet, protocol, tool policy, memory workflow, hook, environment note, installation path, or workflow pattern
- **THEN** the report MUST identify that narrower component before proposing any change to `agents/rose.md`

### Requirement: Activation matrix for gates
The system SHALL define an activation matrix that maps task types to required, optional, skipped, and approval-gated harness gates.

The activation matrix MUST prevent both gate over-triggering on simple tasks and gate under-triggering on high-risk tasks.

#### Scenario: Simple task avoids unnecessary gates
- **WHEN** a task is local, low-risk, and does not involve harness failure signals, broad verification claims, security/trust-model concerns, or cross-module changes
- **THEN** the activation matrix identifies which gates can be skipped or kept optional

#### Scenario: High-risk task requires gates
- **WHEN** a task involves harness rules, command lifecycle, subagent boundaries, memory policy, security/trust-model behavior, broad residual scanning, or completion claims that require independent evidence
- **THEN** the activation matrix identifies the required gates and any approval-gated actions before implementation or final acceptance

### Requirement: Harness change report contract
The system SHALL provide a reusable harness change report template for any proposed harness change.

The template MUST require observed failure or rationale, evidence anchors, affected component, root cause, proposed change, predicted fix, at-risk regression, verification trigger, rollback plan, unknowns, approval status, application status, and final verdict.

#### Scenario: Proposed harness change has prediction and rollback
- **WHEN** an agent proposes a harness change
- **THEN** the report includes the predicted behavior change, a regression risk list, a verification trigger, and a rollback plan before the change can be applied

#### Scenario: Verdict is recorded after verification
- **WHEN** a proposed harness change is applied and verification runs
- **THEN** the report records the verification result, verdict, remaining risks, and evidence pointers

### Requirement: Subagent evidence contract
The system SHALL define a structured evidence contract for subagent task packets and results used in harness-sensitive work.

Task packets MUST be able to identify `trace_id`, `work_package_type`, `artifact_target`, `coverage_expectation`, and `known_exclusions`. Results MUST be able to identify status, confidence, evidence anchors, coverage, skipped work, unknowns, recommended next reads, and harness failure signals.

#### Scenario: Subagent packet declares scope and coverage
- **WHEN** ROSE dispatches a subagent for harness-sensitive evidence gathering, review, testing, security, implementation, or residual scanning
- **THEN** the task packet states the trace identifier, work package type, target artifact or subsystem, expected coverage, forbidden scope, and known exclusions

#### Scenario: Subagent result separates evidence from conclusions
- **WHEN** a subagent returns a result for harness-sensitive work
- **THEN** the result separates status, confidence, evidence anchors, coverage, skipped work, unknowns, recommended next reads, and any harness failure signal

### Requirement: Minimal harness regression fixtures
The system SHALL define minimal regression fixtures for the delivery harness and harness evolution layer.

The fixtures MUST cover command routing, skill routing, subagent dispatch, verification claim handling, and AGENTS/template smoke behavior.

#### Scenario: Fixtures cover required harness behaviors
- **WHEN** the harness architecture landing is implemented
- **THEN** fixture files exist for command routing, skill routing, subagent dispatch, verification claim, and AGENTS/template smoke scenarios

#### Scenario: Fixtures are usable without new dependencies
- **WHEN** a reviewer or test engineer evaluates the first implementation phase
- **THEN** the fixtures can be inspected or exercised through the zero-dependency static runner without installing third-party dependencies

### Requirement: Explicit approval policy for harness changes
The system SHALL define explicit human approval for core harness changes as approval in conversation, PR review, or OpenSpec approval record.

If approval is missing, an agent may stop at report/proposal/spec/test-plan artifacts but MUST NOT silently apply changes to ROSE, commands, skills, subagents, memory policy, install scripts, or harness docs.

#### Scenario: Missing approval blocks apply
- **WHEN** a harness change report or OpenSpec package proposes a core harness change without explicit approval
- **THEN** implementation stops before file edits and records the missing approval as an Open Question or blocked task

### Requirement: Memory and provenance remain CLI-backed
The system SHALL keep memory/provenance recording inside the existing `rose-memory` CLI workflow during the first phase.

The first phase MUST NOT modify the SQLite schema, write raw SQLite manually, or store raw logs/secrets in memory. It MUST use receipts and evidence pointers when recording task outcomes or harness verdicts.

#### Scenario: Harness verdict uses receipt and evidence pointer
- **WHEN** a harness evolution task records an outcome in memory
- **THEN** it uses the approved `rose-memory` CLI to store a receipt, summary, and evidence pointer rather than writing directly to SQLite

#### Scenario: Schema expansion is deferred
- **WHEN** a proposed harness change requires new durable memory entities beyond current CLI support
- **THEN** the change is deferred to a separate approved OpenSpec proposal instead of modifying the SQLite schema in this phase
