# compact-evidence Specification

## Purpose
TBD - created by archiving change add-compact-evidence-protocol. Update Purpose after archive.
## Requirements
### Requirement: Compact evidence pack for noisy evidence

AILI BUILD and SHIP workflows MUST summarize noisy or bulky evidence into a compact evidence pack instead of pasting full raw logs, long grep dumps, long diffs, or full file contents into chat, memory, subagent results, or final reports.

#### Scenario: Test command fails with verbose output

- **WHEN** a BUILD verification command fails and emits verbose output
- **THEN** ROSE reports the command, scope, exit code, concise failure summary, minimal key error excerpt, and exact rerun command
- **AND** ROSE does not paste the full raw log into the final report or memory
- **AND** any unavailable raw evidence is marked `Unverified` with a reason.

#### Scenario: Broad repository search returns many matches

- **WHEN** evidence collection produces broad search results or long grep output
- **THEN** the scout or ROSE returns compact evidence anchors with inspected scope, relevant file/line anchors, unknowns, and next reads
- **AND** excludes unrelated exploratory output and long dumps.

### Requirement: Compact evidence remains verifiable

Compact evidence packs MUST preserve proof value by naming the evidence source, scope, freshness, result, and raw evidence access path or rerun command when applicable.

#### Scenario: SHIP uses prior BUILD evidence

- **WHEN** SHIP evaluates release readiness using BUILD evidence
- **THEN** SHIP checks whether the evidence is fresh for the current diff/scope
- **AND** reruns stale or scope-affected checks when required by lifecycle rules
- **AND** marks remaining gaps as `Unverified` instead of treating old summaries as proof.

#### Scenario: Raw evidence is available only as tool output

- **WHEN** raw evidence was inspected in tool output but not persisted as a repository artifact
- **THEN** the compact evidence pack records the command or inspection needed to reproduce it
- **AND** reports raw artifact access as rerun-required rather than inventing a file path.

### Requirement: Raw evidence placement is explicit and safe

AILI workflows MUST NOT create user-visible raw log, trace, screenshot, or report artifacts unless the active contract or project rules provide a repository-local placement decision.

#### Scenario: A subagent may generate a report or trace

- **WHEN** ROSE dispatches a subagent that may create user-visible evidence artifacts
- **THEN** the task packet names the repository-local placement or says `no files`
- **AND** OS temp paths are used only for ephemeral scratch data that the user does not need to open.

#### Scenario: Evidence may contain secrets or sensitive data

- **WHEN** command output, logs, diffs, or external data may include secrets, credentials, cookies, tokens, or production-sensitive values
- **THEN** the compact evidence pack redacts or excludes sensitive content
- **AND** memory writeback stores only a safe compact summary.

### Requirement: Final reports cite key evidence, not raw dumps

BUILD and SHIP final reports MUST cite the compact evidence that supports status claims and MUST explicitly list skipped checks, partial evidence, and remaining `Unverified` items.

#### Scenario: BUILD completes a package with passing checks

- **WHEN** a BUILD package completes
- **THEN** the final BUILD summary lists changed files, verification commands/results, review lanes, and compact evidence references
- **AND** avoids full command output unless the user explicitly asks for it and it is safe to show.

#### Scenario: SHIP closeout has a release-readiness verdict

- **WHEN** SHIP reports a release-readiness verdict
- **THEN** the closeout includes compact fresh evidence, finding classifications, repair result, skipped checks, and residual risks
- **AND** does not claim `ready` if required evidence is stale, unavailable, or only partially inspected.
