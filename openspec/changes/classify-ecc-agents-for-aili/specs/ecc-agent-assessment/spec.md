## ADDED Requirements

### Requirement: ECC agent absorption is classification-gated

[KNOWN] AILI SHALL classify each ECC agent into `direct absorb`, `merge into existing`, `unsuitable`, or `needs rewrite` before any BUILD package creates or modifies production agents/skills from ECC prior art.

#### Scenario: ECC agent is directly absorbable

- **WHEN** [KNOWN] an ECC agent has a clear AILI-compatible role, narrow trigger, bounded permissions, and low overlap with existing components
- **THEN** [KNOWN] the change may classify it as `direct absorb`
- **AND** [KNOWN] a future BUILD package must still define files, manifest updates, tests, and provenance before implementation

#### Scenario: ECC agent overlaps existing AILI components

- **WHEN** [KNOWN] an ECC agent's useful behavior fits an existing AILI agent, skill, or lifecycle rule
- **THEN** [KNOWN] the change must classify it as `merge into existing`
- **AND** [KNOWN] a future BUILD package must update the existing component instead of creating a duplicate role unless the user approves an exception

#### Scenario: ECC agent needs rewrite

- **WHEN** [KNOWN] an ECC agent has useful intent but includes runtime-specific, domain-specific, risky, or insufficiently bounded behavior
- **THEN** [KNOWN] the change must classify it as `needs rewrite`
- **AND** [KNOWN] a future BUILD package must adapt it to ROSE ownership, OpenCode tooling, permission gates, artifact placement, and verification rules before use

#### Scenario: ECC agent is unsuitable

- **WHEN** [KNOWN] an ECC agent is outside AILI workflow scope or would add unjustified maintenance/routing burden
- **THEN** [KNOWN] the change must classify it as `unsuitable`
- **AND** [KNOWN] it must not be implemented without a later explicit user decision that changes the scope

### Requirement: ECC absorption package selection is explicit and bounded

[KNOWN] AILI SHALL define the selected ECC-derived agents and skills, their boundaries, and their non-goals before BUILD implements any selected component.

#### Scenario: User selects a bounded package

- **WHEN** [KNOWN] the user selects a bounded set of ECC-derived additions
- **THEN** [KNOWN] the DEFINE artifacts must list each selected agent or skill by name
- **AND** [KNOWN] the DEFINE artifacts must identify whether each selected component is an agent or skill
- **AND** [KNOWN] the DEFINE artifacts must record permission boundaries or non-destructive behavior where relevant

#### Scenario: User excludes per-language agents

- **WHEN** [KNOWN] the user excludes dedicated per-language agents from the package
- **THEN** [KNOWN] BUILD must not add language-specific default agents in that package
- **AND** [KNOWN] any future language reviewer pack must require a separate explicit decision

#### Scenario: BUILD package is parallelized

- **WHEN** [KNOWN] multiple selected agents or skills can be implemented independently
- **THEN** [KNOWN] the BUILD plan must separate shared scaffold work from independent component lanes
- **AND** [KNOWN] ROSE must reconcile manifest, docs, routing, tests, and OpenSpec evidence at the integration join point

#### Scenario: Selected components are default-installed

- **WHEN** [KNOWN] the user selects agents or skills for this package and confirms the default installation model
- **THEN** [KNOWN] BUILD must register selected agents and skills as default-installed workflow components
- **AND** [KNOWN] BUILD must update manifest, installation documentation, fixture checks, and doctor/manifest validation expectations as needed
