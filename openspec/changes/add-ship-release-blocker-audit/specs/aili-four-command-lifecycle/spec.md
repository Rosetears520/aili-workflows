## ADDED Requirements

### Requirement: SHIP release-blocker audit
The system SHALL make release-blocker audit an explicit SHIP-mode activity before claiming release, handoff, merge, archive, or closeout readiness.

The audit MUST look for findings that could block release-readiness, including user-impacting behavior regressions, security or permission exposure, unsafe or destructive workflow behavior, data-loss risk, artifact inconsistency, stale or missing evidence, unresolved review/test/security findings, and unverified acceptance criteria.

#### Scenario: Release-blocking issue prevents ready claim
- **WHEN** `/ship` finds a release-blocking issue that is unresolved and not explicitly accepted as risk
- **THEN** the system reports that issue as blocking and does not claim ready, passing, shipped, or archive-ready

#### Scenario: No blocker claim requires fresh evidence
- **WHEN** `/ship` reports that no release-blocking issue was found for the selected scope
- **THEN** the report includes fresh evidence for the audited scope or marks the affected claim as `Unverified`

### Requirement: SHIP audit target selection
The system SHALL resolve and report the release-blocker audit target before running or reporting SHIP readiness.

Supported targets MUST include the active OpenSpec or change artifacts, the current final diff, a comparison against a named baseline or previous-release reference, and a broader repository scan when explicitly requested or risk-triggered.

If multiple plausible targets exist and the current contract does not select one, the system MUST ask for clarification or choose the smallest safe default only when the ambiguity is low-risk and the report explicitly marks broader targets as not audited.

#### Scenario: Current change is the default target
- **WHEN** `/ship` is invoked with an active resolved change or final diff and no broader target is requested
- **THEN** the system audits that change or final diff and states that baseline and whole-codebase scans were not included unless separately requested or triggered

#### Scenario: Baseline comparison requires a baseline
- **WHEN** the user asks `/ship` to compare against a previous release or baseline but no baseline, tag, commit, branch, or release reference is available
- **THEN** the system asks for the missing baseline or marks the baseline comparison as `Open Question` or `Unverified` instead of guessing

#### Scenario: Whole-codebase audit is bounded
- **WHEN** `/ship` is asked to audit the whole codebase
- **THEN** the system reports the scanned scope, evidence sources, skipped lanes, and residual `Unverified` items rather than claiming exhaustive absence of bugs

### Requirement: SHIP finding classification
The system SHALL classify SHIP audit findings before release-readiness verdicts.

Findings MUST be classified as `release-blocking`, `important`, `accepted risk`, `out-of-scope`, or `Unverified`. Release-blocking findings MUST be resolved, disproven with evidence, or explicitly accepted by the user before the system may report ready.

#### Scenario: Findings are reconciled before verdict
- **WHEN** code-review, test, security, artifact, or release-blocker audit findings exist
- **THEN** `/ship` reconciles them into the required classifications and reports the action or decision for each release-blocking or `Unverified` item

#### Scenario: Stale BUILD evidence is not reused silently
- **WHEN** BUILD review, test, or security evidence is stale or affected by changed scope
- **THEN** `/ship` reruns the affected lane or marks the corresponding release-readiness claim as `Unverified`

### Requirement: Release-blocker audit remains internal to SHIP
The system SHALL keep release-blocker audit, review, repair, debug, test verification, and security review as internal lifecycle stages rather than adding a public top-level command for this behavior.

#### Scenario: No extra public audit command is introduced
- **WHEN** the release-blocker audit behavior is added
- **THEN** users still enter the flow through `/ship`, and no new public top-level delivery command is required for blocker review, bug audit, security audit, or release readiness

#### Scenario: Existing helper skills remain internal
- **WHEN** SHIP needs reviewer, tester, or security-auditor evidence
- **THEN** the system may use internal skills or subagents for evidence gathering while keeping `aili-delivery-flow` as the lifecycle authority and ROSE as final reconciler
