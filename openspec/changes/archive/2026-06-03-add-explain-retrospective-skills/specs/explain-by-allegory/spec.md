## ADDED Requirements

### Requirement: Allegory-based explanation workflow
The system SHALL provide an `explain-by-allegory` skill that explains complex concepts through a vivid allegory or story and then translates the allegory into a formal explanation.

#### Scenario: User asks for an allegory
- **WHEN** the user asks to explain a complex concept through a story, allegory, analogy, metaphor, or intuitive teaching example
- **THEN** ROSE SHALL invoke the `explain-by-allegory` skill
- **AND** the skill output SHALL include the allegory and a formal explanation of the concept

#### Scenario: User asks only for implementation guidance
- **WHEN** the user asks to implement code, follow official framework APIs, or produce source-cited technical instructions
- **THEN** ROSE SHALL NOT treat `explain-by-allegory` as the primary skill
- **AND** ROSE SHALL route to the relevant implementation or source-driven workflow instead

### Requirement: Mapping and boundary explanation
The `explain-by-allegory` skill SHALL map story elements back to real concepts and state where the allegory breaks down.

#### Scenario: Allegory is delivered
- **WHEN** the skill provides an allegory for a concept
- **THEN** it SHALL include a mapping from story elements to formal concepts
- **AND** it SHALL identify limits, boundary cases, and common misconceptions that the allegory could create

### Requirement: Explanation-only non-authority boundary
The `explain-by-allegory` skill SHALL make clear that the story is explanatory support and not an authoritative specification, implementation plan, source citation, or acceptance contract.

#### Scenario: Concept affects workflow or architecture decisions
- **WHEN** the explained concept relates to a workflow, architecture, API, spec, or implementation decision
- **THEN** the skill SHALL separate the intuitive explanation from the formal rule or decision
- **AND** it SHALL recommend the appropriate next workflow when the user needs a spec, implementation, source-cited guidance, or decision record
