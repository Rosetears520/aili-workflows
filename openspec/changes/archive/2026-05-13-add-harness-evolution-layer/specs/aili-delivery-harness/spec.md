## ADDED Requirements

### Requirement: Runtime charter split
The system SHALL split ROSE runtime authority from task-family workflow details by keeping `agents/rose.md` as a concise Runtime Charter.

The Runtime Charter MUST preserve identity/final responsibility, instruction precedence, permission and safety gates, delivery lifecycle binding, subagent orchestration boundary, memory boundary, verification/final acceptance, harness evolution gate, and a minimal router. Detailed lifecycle, backend routing, protocol templates, testing policy, memory CLI details, and review-repair loops MUST live in skills, protocols, or harness docs instead of being duplicated in `agents/rose.md`.

#### Scenario: ROSE retains runtime safety authority
- **WHEN** `agents/rose.md` is refactored
- **THEN** it still contains explicit boundaries for user instruction precedence, secrets, High-Risk Gate, git/push/destructive commands, memory access through `rose-memory`, subagent orchestration, and fresh-evidence completion claims

#### Scenario: Workflow detail moves out of ROSE
- **WHEN** lifecycle details for IDEATE, DEFINE, BUILD, or SHIP are needed
- **THEN** `agents/rose.md` references the authoritative skill or protocol files instead of embedding full workflow instructions

### Requirement: Four top-level command entries
The system SHALL expose exactly four user-facing delivery command entries: `/ideate`, `/define`, `/build`, and `/ship`.

Internal stages such as research, questionnaire, test-plan, implementation, debugging, review, repair loop, and harness evolution MUST remain internal skill/subagent phases unless a later approved change explicitly adds a new command.

#### Scenario: Commands map to lifecycle modes
- **WHEN** a user invokes `/ideate`, `/define`, `/build`, or `/ship`
- **THEN** the command routes to `aili-delivery-flow` in IDEATE, DEFINE, BUILD, or SHIP mode respectively

#### Scenario: Internal stages are not top-level commands
- **WHEN** the command directory is inspected
- **THEN** it does not include top-level command files for `/research`, `/questionnaire`, `/test-plan`, `/implement`, `/fix`, `/debug`, `/review`, or `/evolve`

### Requirement: Delivery flow skill owns lifecycle state
The system SHALL provide `skills/aili-delivery-flow/SKILL.md` as the delivery lifecycle state machine.

The skill MUST define IDEATE, DEFINE, BUILD, and SHIP modes, strong stop conditions, backend adapter selection, required artifacts, implementation package boundaries, review-repair loop handoff, and verification/memory closeout expectations. Detailed policy MUST be stored in reference files rather than copied into command files or `agents/rose.md`.

#### Scenario: DEFINE stops before implementation
- **WHEN** a task enters DEFINE mode
- **THEN** the flow may produce or update a spec, questionnaire, and test document, but MUST stop before implementation until blocking answers and explicit approval exist

#### Scenario: BUILD requires approved artifacts
- **WHEN** a task enters BUILD mode
- **THEN** the flow checks that spec/questionnaire/test document gates are closed or explicitly waived before implementation packages are dispatched

### Requirement: Backend adapters preserve lifecycle gates
The system SHALL treat OpenSpec, Superpowers-style plans, custom files, and auto detection as backend adapters for the same delivery lifecycle.

Backend-specific commands or artifact graphs MUST NOT weaken the lifecycle requirement that uncertain ideas ideate first, definitions stop before build, builds follow approved scope, and shipping runs review/repair/final verification/closeout.

#### Scenario: OpenSpec remains an adapter
- **WHEN** an OpenSpec change is used for DEFINE or BUILD
- **THEN** OpenSpec artifacts provide backend storage, while `aili-delivery-flow` lifecycle gates still control whether implementation may start

### Requirement: Protocol templates define artifact contracts
The system SHALL provide reusable protocol templates for delivery artifacts.

The first version MUST include templates for idea brief, research evidence pack, spec draft, alignment questionnaire, acceptance test plan, implementation package, subagent task packet, subagent result, review report, and closeout report.

#### Scenario: Subagent packet uses shared protocol
- **WHEN** ROSE dispatches a harness-sensitive subagent task
- **THEN** the packet can reference `protocols/subagent-task-packet.md` instead of redefining packet fields ad hoc

#### Scenario: Completion report uses closeout protocol
- **WHEN** SHIP completes or pauses
- **THEN** the closeout report can record outcome, evidence, remaining issues, memory writeback, and next steps using the shared protocol

### Requirement: Harness docs expose architecture boundaries
The system SHALL provide `docs/harness/**` as the observable architecture surface for the delivery harness.

The first version MUST include harness contract, component map, activation matrix, backend adapters, command lifecycle, failure taxonomy, tool policies, harness change report template, and fixtures.

#### Scenario: Unique authority files avoid duplicated flow rules
- **WHEN** README, commands, templates, or ROSE need to describe lifecycle, backend routing, harness changes, subagent evidence, verification, or memory
- **THEN** they reference the relevant authority file instead of copying long workflow rules

### Requirement: Commands install with OpenCode setup
The system SHALL install or link command entry files through the existing OpenCode setup path.

`scripts/install_opencode.sh` and setup documentation MUST handle `commands/*.md` in addition to agents and skills, without requiring new third-party dependencies.

#### Scenario: Install script includes commands
- **WHEN** the OpenCode install script runs in a supported local environment
- **THEN** managed command entries are copied or linked into the configured OpenCode commands directory along with agents and skills

### Requirement: Static harness fixture runner
The system SHALL provide a zero-dependency static smoke runner for harness fixtures.

The runner MUST use only the Python standard library and MUST check required fields or marker strings for command routing, skill routing, subagent dispatch, verification claim, and related fixtures. It MUST NOT run LLM benchmarks, call external services, or require dependency installation.

#### Scenario: Fixture runner validates required smoke cases
- **WHEN** `python scripts/harness_fixture_check.py` is executed
- **THEN** it verifies required fixture files and fields exist and exits non-zero on missing required fixture coverage

#### Scenario: Runner avoids benchmark scope creep
- **WHEN** fixture validation runs
- **THEN** it does not invoke model APIs, external network calls, package installs, or multi-host compatibility checks
