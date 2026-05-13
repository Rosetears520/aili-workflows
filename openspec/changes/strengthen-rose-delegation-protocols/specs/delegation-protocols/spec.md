## ADDED Requirements

### Requirement: Direct work allowlist
The system SHALL allow ROSE to directly perform only small, exact, low-risk, locally verifiable work that does not require repository-wide convention discovery or specialist judgment.

Direct work MUST be limited to typo fixes, documentation wording, comments, Markdown formatting, unimportant display text, small README/example/test-instruction paragraphs, a single non-security/non-release/non-data-semantic parameter, or a tiny local code fix with an exact target and simple verification path.

Even when the final edit appears small, ROSE MUST NOT use the direct allowlist if opening a read-only subagent would materially save MainAgent context during evidence discovery.

#### Scenario: Trivial exact edit proceeds directly
- **WHEN** the user asks for a typo, wording, comment, Markdown formatting, or other exact low-risk local change
- **THEN** ROSE may perform the edit without dispatching a subagent, provided the verification path is local and no broader project convention evidence is required

#### Scenario: Single file is not automatically direct
- **WHEN** a requested single-file edit touches ROSE/runtime rules, skills, commands, subagent contracts, memory policy, schema, CI, dependencies, security, release, install behavior, or data semantics
- **THEN** ROSE MUST treat the task as delegated, approval-gated, or evidence-gated instead of relying on the direct allowlist

### Requirement: Context-saving mandatory delegation
The system SHALL require read-only subagent dispatch when evidence collection in MainAgent would materially pollute or consume MainAgent context.

Mandatory dispatch triggers MUST include broad grep/list/search output, three or more relevant files, two or more directories or subsystems, two or more likely search passes, noisy logs/test/CI output, active/current/stale/archived/generated reference judgment, all-reference scans, upstream/downstream/peer implementation mapping, test coverage mapping, and convention discovery before non-trivial edits.

#### Scenario: Small final change still dispatches scout
- **WHEN** the final code or documentation change may be small but locating the correct target requires broad search, multiple files, noisy logs, or active-vs-stale judgment
- **THEN** ROSE MUST dispatch an appropriate read-only scout and receive compact evidence anchors before editing

#### Scenario: MainAgent skips delegation only with justification
- **WHEN** ROSE chooses not to dispatch a subagent for a non-trivial task
- **THEN** ROSE MUST state why the task fits the direct allowlist and why subagent dispatch would not add material evidence or context savings

### Requirement: Repo evidence first gate
The system SHALL provide a `repo-evidence-first` workflow that prevents ROSE from presenting project facts without repository evidence anchors.

The workflow MUST classify claims as grounded facts only when supported by file paths with lines or symbols, command output summaries, test names/results, spec/task/protocol sections, existing artifact formats, explicit user instruction, or subagent evidence anchors. Unsupported claims MUST be marked as hypotheses, delegated for evidence, asked to the user, or blocked.

#### Scenario: Project convention claim requires evidence
- **WHEN** ROSE needs to claim how the project normally structures files, names artifacts, routes skills, verifies changes, or handles a behavior
- **THEN** ROSE MUST cite project evidence anchors or mark the statement as a hypothesis instead of a fact

#### Scenario: Evidence conflict blocks editing
- **WHEN** evidence sources conflict, appear stale, are generated/archived, or are insufficient for a non-trivial edit
- **THEN** ROSE MUST delegate more scouting, ask the user, or block the edit instead of guessing

#### Scenario: Evidence source routes to the lightest specialist
- **WHEN** ROSE needs evidence that is primarily local code, local documentation, external official documentation, verification coverage, or security/trust-model related
- **THEN** ROSE MUST route to the lightest appropriate specialist source such as `code-scout`, `doc-researcher`, `web-researcher`, `test-engineer`, or `security-auditor`, or explain why direct evidence collection is cheaper and sufficient

### Requirement: Code locality mapping
The system SHALL define `code-scout` as a code locality mapping agent, not merely a keyword search worker.

`code-scout` results for relevant tasks MUST map the target implementation, upstream callers or entrypoints, downstream consumers or output paths, sibling/peer implementations, tests or docs defining expected behavior, freshness status, recommended next reads, risk notes, and a conclusion of `GROUNDED`, `PARTIAL`, or `NOT FOUND`.

#### Scenario: Call chain evidence is needed
- **WHEN** a task requires understanding how a symbol, command, route, config key, template, schema, or behavior is implemented and consumed
- **THEN** ROSE MUST use code locality evidence that covers upstream, downstream, peer patterns, and verification targets before planning or editing

#### Scenario: Raw grep dump is rejected
- **WHEN** `code-scout` returns evidence to ROSE
- **THEN** the result MUST use compact anchors and structured locality fields instead of raw grep dumps, long logs, or unrelated exploratory output

### Requirement: Session handoff workflow
The system SHALL provide a `session-handoff` workflow for current-task continuity during long sessions, context compression, BLOCKED/IDLE states, and session transitions, but it SHALL create or persist a handoff artifact only when the user explicitly requests it or an approved command contract requires it.

The handoff MUST include current goal, active contract, lifecycle mode, backend/artifact source, scope boundary, touched files/artifacts, evidence anchors, subagent activity, decisions made, open questions, risks/unknowns, verification state, blocked reason, next action, and a suggested next-session prompt. It MUST NOT include raw logs, full grep dumps, full file contents, secrets, credentials, cookies, tokens, irrelevant conversation history, or durable memory by default.

#### Scenario: Explicitly requested compression-ready handoff
- **WHEN** the user explicitly requests a handoff for a long task that is about to be compressed, paused, marked BLOCKED/IDLE, or continued in another session
- **THEN** ROSE MUST produce a concise session handoff artifact that lets a fresh session resume without relying on raw conversation context

#### Scenario: Handoff is not durable memory
- **WHEN** a session handoff contains current-task state rather than durable project findings
- **THEN** ROSE MUST keep it as a handoff artifact and MUST NOT promote it to long-term `rose-memory` unless a separate durable memory condition is met

#### Scenario: Handoff placement follows artifact source
- **WHEN** a session handoff is explicitly requested for an OpenSpec change, an existing current-task directory, or a non-OpenSpec task
- **THEN** ROSE MUST place it in the OpenSpec change directory, the existing current-task directory, or an explicitly approved non-OpenSpec location respectively, and MUST NOT write it to an OS temp directory or durable memory by default

### Requirement: Subagent task packet contract
The system SHALL define a structured task packet contract for subagent dispatch used in non-trivial or harness-sensitive work.

The task packet MUST include goal, context, allowed scope, forbidden scope, edit permission, evidence required, expected return format, stop conditions, and placement or artifact rules when relevant. For harness-sensitive work, packets SHOULD also include trace or work package identifiers, artifact targets, coverage expectations, and known exclusions.

#### Scenario: Scoped subagent dispatch
- **WHEN** ROSE dispatches a subagent for evidence gathering, implementation, review, testing, security, debugging, or harness-sensitive work
- **THEN** the packet MUST define scope, forbidden work, edit permission, expected evidence, return format, and stop conditions before the subagent starts

#### Scenario: Subagent does not inherit main context implicitly
- **WHEN** ROSE creates a subagent packet
- **THEN** the packet MUST include all context required for that bounded work package and MUST NOT rely on the subagent knowing the main conversation implicitly

### Requirement: Canonical protocol authority
The system SHALL keep subagent task/result protocol authority in one canonical location for this change.

The canonical protocol path for this change MUST be `skills/aili-delivery-flow/references/protocols/`. Any top-level `protocols/**` path used by older or adjacent changes MUST be treated as a compatibility index, link, migration source, or separately approved authority change, not a second independent source of protocol truth.

#### Scenario: Duplicate protocol path is found
- **WHEN** implementation discovers both `skills/aili-delivery-flow/references/protocols/` and top-level `protocols/**` contain subagent task/result protocol content
- **THEN** implementation MUST preserve `skills/aili-delivery-flow/references/protocols/` as canonical for this change and convert the other path to a pointer, migration note, or blocked reconciliation item before claiming completion

### Requirement: Subagent result evidence separation
The system SHALL define a subagent result protocol that separates observed facts, inferences, recommendations, unknowns, and MainAgent next reads.

Observed facts MUST include evidence anchors, freshness classification, confidence, and inspected scope where relevant. Inferences MUST state what evidence they are based on and their risk. Recommendations MUST be treated as proposed actions for ROSE to reconcile, not authoritative decisions.

#### Scenario: ROSE reconciles subagent output
- **WHEN** a subagent returns findings
- **THEN** ROSE MUST compare the findings against evidence anchors, identify conflicts or gaps, and make final judgment instead of treating the subagent output as truth

#### Scenario: Facts and recommendations remain distinct
- **WHEN** a subagent suggests a fix, route, test, or implementation step
- **THEN** the result MUST distinguish the recommendation from observed facts so ROSE can verify and accept, reject, or revise it

### Requirement: Minimal ROSE router update
The system SHALL keep ROSE runtime prompt changes minimal when adding delegation protocol behavior.

`agents/rose.md` updates for this change MUST be limited to short routing and boundary references for direct-vs-delegated work, repo-evidence-first, session-handoff, code locality mapping, and subagent protocols. Detailed workflows MUST live in skills, references, or protocol files.

#### Scenario: ROSE references authority files
- **WHEN** implementation adds delegation protocol rules
- **THEN** `agents/rose.md` contains concise pointers and does not duplicate the full Direct vs Delegated Work, Repo Evidence First, Session Handoff, or subagent result protocol text

#### Scenario: Harness edits remain approval-gated
- **WHEN** the proposal is ready but implementation approval has not been granted
- **THEN** no core harness files such as ROSE rules, skills, commands, subagent contracts, memory policy, install scripts, or hooks are modified
