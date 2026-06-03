## MODIFIED Requirements

### Requirement: Agent operating discipline includes selected agentic failure guards
The generated-project `AGENTS.md` template SHALL include compact execution-time guardrails that prevent common multi-step coding-agent failures without pasting long upstream rule text.

#### Scenario: Deterministic work is available
- **WHEN** a task decision can be made by a status code, schema, test, typechecker, script, existing config, deterministic transformation, or explicit project rule
- **THEN** the agent SHALL use that deterministic source instead of asking the model to guess the decision

#### Scenario: Repository patterns conflict
- **WHEN** two existing project patterns or conventions conflict
- **THEN** the agent SHALL expose the conflict, choose the better-supported, newer, or more tested pattern when safe, and mark the other pattern as follow-up instead of blending both silently

#### Scenario: Context must be read before writing
- **WHEN** the agent needs to add or modify non-trivial code, tests, docs, config, or workflow files
- **THEN** the agent SHALL read relevant exports, callers, shared utilities, tests, docs, or specs before writing
- **AND** the agent SHALL use a read-only subagent when broad repository reading would pollute the main context

#### Scenario: Tests are used as evidence
- **WHEN** the agent writes, updates, or relies on tests
- **THEN** the tests SHALL verify why the behavior matters and fail when important business or workflow logic is wrong, not merely execute code or assert superficial output

#### Scenario: Operation is long-running or multi-step
- **WHEN** a task spans multiple phases, large logs, repeated tool calls, multiple files, or enough context that the agent can no longer accurately recount current state
- **THEN** the agent SHALL checkpoint before continuing by stating what changed, what was verified, what remains, and any blockers or uncertainty

#### Scenario: New pattern conflicts with local convention
- **WHEN** a novel style, dependency, framework, abstraction, or pattern would diverge from established local convention
- **THEN** the agent SHALL follow local convention unless the user explicitly approves the divergence after trade-offs are explained

#### Scenario: Success is uncertain
- **WHEN** checks are skipped, records are ignored, boundary cases remain unverified, migrations skip items, or evidence does not prove the full claim
- **THEN** the agent SHALL report the uncertainty explicitly and SHALL NOT claim success, completion, readiness, or tests passing beyond the evidence

#### Scenario: Approved spec-backed implementation begins
- **WHEN** the agent starts approved spec-backed implementation work
- **THEN** the agent SHALL maintain `implementation-notes.html` beside the active spec/task artifacts
- **AND** the notes SHALL use the user's language by default, or Simplified Chinese when the language is unclear
- **AND** the notes SHALL record spec deviations, temporary decisions, trade-offs, open questions, unverified assumptions, safe evidence pointers, and update history without storing raw logs, full transcripts, secrets, private data, or large file dumps

### Requirement: Context continuity uses DCP-aware checkpoints instead of raw token or percentage gates
The generated-project `AGENTS.md` template SHALL express context discipline as DCP-aware task-continuity checkpoint triggers rather than hard-coded universal token limits or primary reliance on raw context-usage percentages.

#### Scenario: Task continuity is at risk
- **WHEN** DCP, compression, conversation context, logs, tool output, or repeated debugging loops make raw context usage an unreliable signal for task continuity
- **THEN** the agent SHALL use task-continuity risk as the checkpoint trigger rather than raw context percentage
- **AND** soft checkpoint triggers SHALL include inability to accurately restate the active contract, changed files, open decisions, or verification path; state depending on compressed/raw session history that has not been re-grounded in files or todos; tool output, logs, or subagent reports accumulating faster than they are distilled into durable artifacts; repeated loops without new hypotheses, evidence anchors, or decisions; or the next step depending on memory instead of fresh repo evidence
- **AND** a soft checkpoint SHALL summarize the current contract, decisions, files, todos, unknowns, and verification path while reducing further context growth
- **AND** a hard checkpoint SHALL stop before more edits and write or update the approved task artifact, progress/checkpoint, handoff, or implementation notes, then re-ground from repo evidence before continuing
- **AND** the template SHALL NOT require universal fixed absolute token budgets or treat raw percentage thresholds as authoritative when DCP/compression is active
