## ADDED Requirements

### Requirement: Traceability from requirement to verification

Formal AILI change artifacts SHALL maintain traceability from requirement, decision, or risk to task/package, affected file or artifact, verification command or inspection, and evidence or `Unverified` status.

This traceability MAY be represented across `proposal.md`, `design.md`, `tasks.md`, `specs/**/spec.md`, `interview.md`, `test-plan.md`, `progress.txt`, and closeout reports rather than duplicated verbatim in every artifact.

#### Scenario: DEFINE creates traceable implementation contract

- **WHEN** DEFINE creates or updates a formal change package
- **THEN** tasks and test-plan entries map requirements, decisions, or risks to implementation work and verification targets
- **AND** unresolved traceability gaps are labeled `Open Question` or `Unverified`

#### Scenario: BUILD dispatches traceable packages

- **WHEN** BUILD dispatches implementation work from a formal change
- **THEN** each package or worker packet names its requirement/decision/risk source, editable files or artifact boundaries, and expected verification evidence
- **AND** `progress.txt` records returned evidence in that mapping rather than only free-form status

#### Scenario: SHIP checks spec coverage

- **WHEN** SHIP evaluates readiness for a formal change
- **THEN** ROSE performs a spec coverage check that compares accepted requirements/tasks/test-plan items against implementation, verification, review, and security evidence
- **AND** reports uncovered or unverified items before any ready/shipped/archive-ready claim

### Requirement: External prior-art absorption records provenance

When AILI uses public projects or public skills as prior-art evidence, it SHALL record whether the result is clean-room pattern absorption or derivative copying. Derivative copying is allowed only when the user explicitly approves it and the implementation records source, license, notice obligations, and AILI/OpenCode adaptations.

#### Scenario: Public skill inspires an AILI skill

- **WHEN** DeerFlow, ECC, Code-Spec-Plugin, or another public source inspires an AILI skill, agent, or workflow rule
- **THEN** the resulting artifact is written as a clean-room AILI-specific workflow unless derivative copying has been explicitly approved
- **AND** upstream license/provenance requirements are recorded if any text, code, script, asset, placeholder vocabulary, or closely paraphrased structure is copied

#### Scenario: User approves derivative copying with minimal adaptation

- **WHEN** the user explicitly approves copying selected upstream skill content with minimal AILI/OpenCode adaptation
- **THEN** BUILD records the source path, license, notice/provenance, copied/adapted scope, and adaptation rationale
- **AND** changes only upstream-specific placeholders, runtime names, tool names, paths, branding, or provider assumptions needed to fit AILI safely
- **AND** does not silently broaden the copied scope beyond the approved skill set

#### Scenario: Source has runtime-specific assumptions

- **WHEN** a prior-art skill depends on external providers, deployment services, DeerFlow/Claude-specific tools, sandbox paths, or project branding
- **THEN** AILI either adapts the pattern to OpenCode/project-local boundaries or marks the source low-fit
- **AND** does not import the runtime assumption silently
