## ADDED Requirements

### Requirement: Shared `.agents/skills` canonical skill source

The installer and package model SHALL support `.agents/skills` as the canonical repository-managed skill source while preserving existing OpenCode-native skills installation behavior.

OpenCode-native skill outputs MAY be copied, generated, linked, or adapted from `.agents/skills`, but they MUST NOT become an undocumented second source of truth. The implementation MUST NOT assume `.agent/` singular is a portable tool convention.

#### Scenario: Shared skills are installed without removing OpenCode skills

- **GIVEN** a user runs the AILI install flow with shared skills enabled by default or explicit option
- **WHEN** repository-managed skills are installed
- **THEN** the skills are available from the canonical `.agents/skills` source according to the manifest
- **AND** OpenCode-native skills remain installed or preserved in the existing OpenCode target
- **AND** existing OpenCode agents, commands, plugins, and config behavior are not removed solely because the shared target exists

#### Scenario: `.agent` singular is requested by assumption

- **WHEN** a user or agent suggests `.agent/` singular as the universal install target
- **THEN** the installer/docs SHALL prefer `.agents/skills` for shared Agent Skills unless current official evidence proves otherwise
- **AND** SHALL document that `.agent/` singular is not the supported AILI shared target

#### Scenario: Shared source or target conflict exists

- **GIVEN** a `.agents/skills/<skill>` source path or generated target path already exists and is not owned by AILI
- **WHEN** the installer needs to place a repository-managed skill there
- **THEN** it SHALL preserve or back up the conflicting user-owned path according to the existing safe install conflict policy
- **AND** report the conflict without replacing the whole `.agents` parent directory by default

### Requirement: Component manifest is install source of truth

The component manifest SHALL define repository-managed agents, skills, commands, canonical `.agents/skills` source paths, OpenCode-native targets, package inclusion expectations, provenance, default install state, and validation metadata used by installers and doctor checks.

Installers SHOULD consume this manifest rather than independently globbing component directories as the authoritative component list. Compatibility scripts MAY retain fallback behavior only when they validate against the manifest and report drift.

#### Scenario: Installer plans component targets

- **WHEN** the installer computes a dry-run or real install plan
- **THEN** it uses the manifest to identify component source paths and target outputs
- **AND** reports shared `.agents/skills` and OpenCode-native targets separately

#### Scenario: Disk and manifest drift

- **GIVEN** a repository component exists on disk but is missing from the manifest, or a manifest component source is missing from disk
- **WHEN** validation, doctor, CI, or packaging checks run
- **THEN** the drift is reported as a hard validation failure or explicit `Unverified` install item
- **AND** the package/install flow does not silently ship unmanaged workflow components

#### Scenario: Package file list changes

- **WHEN** `.agents/skills` shared outputs or target metadata are included in the npm package
- **THEN** package metadata and dry-run package verification SHALL confirm the intended files are included
- **AND** generated indexes, `.codegraph/`, secrets, and unrelated local runtime state are excluded

### Requirement: Doctor reports shared skills and optional evidence providers

`rose-aili doctor` SHALL report shared `.agents/skills` status, OpenCode-native install status, manifest drift, stale generated project facts, and optional CodeGraph readiness separately.

#### Scenario: Doctor checks shared and native targets

- **WHEN** a user runs `rose-aili doctor`
- **THEN** the report includes whether repository-managed skills are present in `.agents/skills`
- **AND** whether OpenCode-native agents, skills, and commands are present in their expected targets
- **AND** whether manifest entries match package/installable disk state

#### Scenario: CodeGraph is not initialized

- **GIVEN** the current repository has no initialized CodeGraph index
- **WHEN** doctor checks optional evidence providers
- **THEN** it reports CodeGraph as optional and not initialized for the current repository
- **AND** provides the project-local follow-up path without treating base AILI installation as failed solely for missing CodeGraph
