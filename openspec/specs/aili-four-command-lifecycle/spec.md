# aili-four-command-lifecycle Specification

## Purpose
TBD - created by archiving change productize-four-command-lifecycle. Update Purpose after archive.
## Requirements
### Requirement: Four command lifecycle remains the public delivery surface
The system SHALL expose `/ideate`, `/define`, `/build`, and `/ship` as the only public top-level delivery lifecycle commands.

#### Scenario: Internal stage command is not introduced
- **WHEN** the lifecycle command set is inspected
- **THEN** questionnaire, test-plan, debug, review, fix, and evolve stages are not added as public top-level delivery commands

### Requirement: Commands provide explicit boundary contracts
Each public delivery command SHALL state its mode purpose, required behavior, hard stops, and output contract while routing lifecycle authority to `aili-delivery-flow`.

#### Scenario: Command prompt is readable and bounded
- **WHEN** a command prompt is opened
- **THEN** it contains standard frontmatter, the command heading, user input handling, required behavior, hard stops, and output expectations

### Requirement: DEFINE produces OpenSpec change-contract artifacts through dedicated skills
For OpenSpec-backed changes, DEFINE SHALL create or update the implementation-readiness artifacts under `openspec/changes/<change-id>/`, including proposal, tasks, relevant specs, interview, and test-plan artifacts. Interview artifacts MUST be produced through the `change-interviewer` contract, test-plan artifacts MUST be produced through the `test-document-generator` contract, and design artifacts MUST be created for each OpenSpec change according to the confirmed change policy.

#### Scenario: DEFINE creates questionnaire and test plan by default
- **WHEN** `/define` is run for an OpenSpec-backed change
- **THEN** `interview.md` and `test-plan.md` are created or updated as part of the change contract through `change-interviewer` and `test-document-generator` without requiring separate user prompts

### Requirement: Non-OpenSpec DEFINE asks artifact placement once
For non-OpenSpec backends, DEFINE SHALL ask once where questionnaire and test-plan artifacts should be placed before writing them, pass those locations to `change-interviewer` and `test-document-generator`, then record the placement in the active change context.

#### Scenario: Placement decision is reused
- **WHEN** a non-OpenSpec DEFINE flow continues after the user has selected artifact locations
- **THEN** the selected locations are reused without repeatedly asking the same placement question

### Requirement: User-editable artifacts use disk-first freshness
Before using, merging, validating, or overwriting user-editable DEFINE artifacts, ROSE MUST treat conversation context as stale by default and re-read the on-disk artifact as the source of truth.

#### Scenario: Saved questionnaire edit is detected
- **WHEN** the user edits and saves `interview.md` before continuing the lifecycle
- **THEN** ROSE re-reads `interview.md` from disk in the current turn and summarizes detected changes before using or merging the answers

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

### Requirement: Post-cycle bugs follow a revision decision
When bugs or adjustments are discovered after a lifecycle pass, the system SHALL decide whether to update the active change, create a new fix change, or route a harness defect through harness triage and evolution.

#### Scenario: Same-scope unarchived bug updates current change
- **WHEN** a bug is discovered before the change is archived and it has the same intent and overlapping scope
- **THEN** the current change is updated with repair tasks and test-plan coverage instead of starting a new change

#### Scenario: Harness defect routes to harness evolution
- **WHEN** the issue concerns command, skill, workflow, memory, subagent, installer, or tool-policy behavior
- **THEN** the system routes through harness issue triage and harness evolution rather than treating it as a normal product bug

### Requirement: BUILD supervisor harness

BUILD SHALL run as a Supervisor harness in which ROSE coordinates, constrains, verifies, reconciles, and records work instead of acting as the default implementation worker for non-trivial repository changes.

ROSE MUST keep final authority for PASS / FAIL / `Unverified` decisions, task-state updates, memory receipts, and user-facing completion reports. Subagents may perform implementation, verification, review, security assessment, evidence gathering, or debugging, but their outputs are evidence for ROSE to reconcile rather than final status.

#### Scenario: BUILD dispatches implementation by default

- **WHEN** BUILD has a non-trivial repository-affecting implementation increment and the user has not opted out of subagents
- **THEN** ROSE dispatches an implementer or another appropriate worker with a bounded task packet instead of doing the implementation directly

#### Scenario: Worker increment is dynamically sized

- **WHEN** ROSE prepares delegated BUILD work
- **THEN** ROSE sizes the worker increment by verifiability, reviewability, parallel edit conflict risk, clean handoff, context cost, coupling, edit ownership, and verification boundary rather than by a fixed file count
- **AND** may group related small tasks when the result remains reviewable, verifiable, free of parallel ownership conflict, and cleanly handable back to ROSE
- **AND** splits work smaller when scope, conflicts, or verification are unclear

#### Scenario: ROSE owns final status

- **WHEN** workers return implementation, review, test, or security results
- **THEN** ROSE reconciles those results with fresh evidence
- **AND** only ROSE updates final PASS / FAIL / `Unverified` state and reports completion readiness

### Requirement: BUILD progress ledger

BUILD SHALL support a backend-neutral compact progress ledger for long-running and multi-session execution. The selected backend or an explicit user placement decision SHALL resolve the concrete `progress.txt` path.

For OpenSpec-backed BUILD targets, the default progress ledger path SHALL be `openspec/changes/<change-id>/progress.txt`.

The progress ledger MUST record enough state for ROSE or a later session to continue without relying on raw conversation context: current objective, selected increment, worker dispatches, returned evidence, changed or inspected files/artifacts, verification/review/security lane status, blockers, final ROSE decision, and next action.

Only ROSE MAY write or append the progress ledger. Workers MUST NOT write `progress.txt` directly; workers MUST return compact reports and evidence references for ROSE to reconcile into the ledger.

The progress ledger MUST NOT contain secrets, raw logs, full transcripts, full file contents, long grep dumps, or durable memory state. It MUST reference raw evidence by rerun command or approved repository-local artifact path when needed.

#### Scenario: BUILD starts or resumes an OpenSpec target

- **WHEN** BUILD starts or resumes an OpenSpec-backed target
- **THEN** ROSE reads existing `progress.txt` when present
- **AND** ROSE appends or updates a compact entry for the current BUILD run before reporting final BUILD status

#### Scenario: Worker returns progress evidence

- **WHEN** a worker has progress, implementation, review, test, or security evidence for a BUILD increment
- **THEN** the worker returns a compact report to ROSE
- **AND** does not create, edit, or append `progress.txt` directly

#### Scenario: BUILD blocks before completion

- **WHEN** BUILD stops because of a missing approval, failed verification, conflicting worker output, safety gate, or exhausted repair limit
- **THEN** `progress.txt` records the blocker, evidence reference, affected increment, and recommended next action

#### Scenario: Progress ledger does not replace existing artifacts

- **WHEN** BUILD writes `progress.txt`
- **THEN** `test-plan.md` remains the test plan and execution ledger
- **AND** `rose-memory` remains the durable memory/checkpoint system
- **AND** `handoff.md` is still created only when explicitly requested or required by an approved command contract

### Requirement: Non-OpenSpec progress ledger placement

For non-OpenSpec BUILD targets, ROSE SHALL ask once for a repository-local progress ledger placement before creating a `progress.txt`-style artifact, then record and reuse that placement in the active change context.

#### Scenario: Non-OpenSpec BUILD needs long-running ledger

- **WHEN** BUILD is running against a non-OpenSpec target and needs a durable progress ledger
- **THEN** ROSE asks for the ledger path before writing it
- **AND** does not use OS temporary paths for user-visible progress state

#### Scenario: User chooses no ledger

- **WHEN** the user explicitly declines a non-OpenSpec progress ledger
- **THEN** ROSE may continue only if lifecycle state can still be reported with required evidence, memory receipts, and `Unverified` items

### Requirement: IDEATE idea inbox

IDEATE SHALL remain an exploration and option-shaping mode and SHALL NOT create formal change proposals by default.

When a user asks to preserve an idea, when a multi-turn IDEATE discussion creates durable candidate requirements, or when ROSE needs to prevent intent drift before DEFINE, IDEATE MAY update a backend-neutral idea inbox at `ideas/workflow-inbox.md`.

Each inbox entry SHALL record the idea status, source, original intent, current understanding, confirmed decisions, open questions, unverified items, possible backend target, and next action. Inbox entries SHALL remain candidates until `/define` or an explicit user instruction promotes them into a backend-specific change contract.

#### Scenario: IDEATE records an idea without creating a change

- **WHEN** the user says to remember or record an IDEATE-stage idea but has not asked to enter DEFINE
- **THEN** ROSE may update `ideas/workflow-inbox.md`
- **AND** does not create `openspec/changes/<change-id>/proposal.md` or another formal backend contract by default

#### Scenario: Inbox item is promoted

- **WHEN** the user asks to define, formalize, or implement an inbox idea
- **THEN** DEFINE selects the backend and creates or updates the backend-specific artifacts
- **AND** the inbox entry records the promoted backend pointer

### Requirement: Change context ledger

For non-trivial formal changes, DEFINE SHALL create or update a backend-specific `context.md` that preserves the maintained user-intent context for that change.

The context ledger SHALL record current goal, original source or phrasing pointer, confirmed decisions, rejected alternatives, accepted defaults, open questions, unverified items, and write-back mapping to proposal, design, tasks, specs, interview, test-plan, and progress artifacts where applicable.

OpenSpec-backed changes SHALL use `openspec/changes/<change-id>/context.md`. Non-OpenSpec backends SHALL resolve a repository-local context ledger path through the backend adapter or an explicit placement decision before writing.

#### Scenario: DEFINE creates a context ledger

- **WHEN** DEFINE creates or updates a non-trivial formal change contract
- **THEN** ROSE creates or updates that change's backend-specific `context.md`
- **AND** records which decisions have been written back to formal artifacts and which remain open or unverified

#### Scenario: BUILD detects context drift

- **WHEN** BUILD reads `context.md` and finds the requested implementation would contradict confirmed user intent, rejected options, or unresolved open questions
- **THEN** BUILD pauses or routes back to DEFINE instead of silently implementing the conflicting behavior

#### Scenario: SHIP checks against user intent

- **WHEN** SHIP evaluates the final change
- **THEN** SHIP uses `context.md` to check whether delivered behavior still matches the current user goal and confirmed decisions
- **AND** reports accepted risks or `Unverified` intent gaps

### Requirement: Mature-project pattern research workflow

AILI SHALL support a reusable mature-project/pattern research skill workflow when IDEATE needs prior art, when ordinary chat asks variants of “看看别人怎么做 / look at how others do it / reference mature projects / GitHub 上别人怎么做”, when the design would benefit from established public examples, or when ROSE needs evidence about whether an approach is mature enough to adopt.

The workflow MUST be skill-first in the MVP through a `mature-project-pattern-research` skill that wraps existing `web-researcher` for external collection. It MUST NOT add GitHub MCP in the MVP, MUST NOT add a public `/research` command, and MUST defer any dedicated agent unless `web-researcher` proves too generic.

The workflow MUST inspect external public sources through an appropriate read-only research workflow and report sources, maturity signals, evidence anchors, applicable patterns, not-recommended patterns, license risks, security risks, maintenance risks, complexity risks, uncertainty labels, and recommended next decisions. It MUST NOT copy or vendor external code, skill text, or assets, including when public skills are used as design inspiration.

#### Scenario: User asks for mature project inspiration

- **WHEN** the user asks during IDEATE or ordinary chat to search mature projects, learn how others do it, reference public examples, or inspect “GitHub 上别人怎么做”
- **THEN** ROSE runs or delegates the mature-project pattern research workflow
- **AND** returns a compact applicability matrix with sources, maturity signals, evidence anchors, applicable patterns, not-recommended patterns, license/security/maintenance/complexity risks, uncertainty labels, and open questions

#### Scenario: External skills inspire structure without copying

- **WHEN** public skills or public agent examples are used as design inspiration
- **THEN** ROSE may extract general patterns such as concise skill structure, natural-language trigger descriptions, progressive disclosure, source-quality discipline, report-first/read-only behavior, output contracts, and trigger validation
- **AND** does not copy, vendor, or paraphrase external skill text, code, or assets as repository-owned content

#### Scenario: Research is only inspiration

- **WHEN** external project research finds a potentially useful pattern
- **THEN** ROSE treats it as evidence for IDEATE or DEFINE decisions
- **AND** does not implement, vendor, or copy the pattern until the relevant change contract and verification plan are approved
