# Harness Component Map

Use this map to classify failures before proposing a harness change. Do not modify `agents/rose.md` during normal tasks; agent prompt edits require an explicit harness maintenance task and human approval.

| Category | Owns | Examples | First evidence to check |
|---|---|---|---|
| system-rules | Runtime authority and safety boundaries | ROSE charter, AGENTS template | `agents/rose.md`, `templates/AGENTS.md` |
| command | User entrypoints | Exactly four delivery shortcuts `/ideate`, `/define`, `/build`, `/ship`; standalone non-delivery `/local-review` | `commands/*.md` |
| skill | Workflow implementation | delivery flow, harness evolution, review gates | `.agents/skills/*/SKILL.md`, references |
| subagent-config | Delegation contracts | task packets, result reports, specialist boundaries | `agents/*.md`, `.agents/skills/aili-delivery-flow/references/protocols/subagent-*.md` |
| memory | Provenance and receipts | memory writeback, retrieval packs | `.agents/skills/rose-memory/SKILL.md` |
| tool-policy | Tool use and trust boundaries | git, browser, bash, file edits | `docs/harness/tool-policies.md` |
| middleware/hooks | Runtime interception | OpenCode hooks, future middleware | `.opencode/`, setup docs |
| environment | Host constraints | WSL/Linux paths, network, dependencies | setup docs, test-plan |
| workflow-pattern | Lifecycle orchestration | IDEATE/DEFINE/BUILD/SHIP, review-repair | delivery-flow references |
| docs/protocol | Artifact contracts | questionnaires, test plans, reports | `.agents/skills/aili-delivery-flow/references/protocols/*.md`, `docs/harness/*.md` |
| install/setup | Distribution path | command/skill/agent install | `scripts/install_opencode.sh`, setup docs |
| source-boundary | Canonical/generated/upstream classification | AILI source, generated/installed adapters, inert upstream data | `docs/harness/workflow-orchestration-source-register.md`, `manifests/upstream-references.json` |
| distribution | npm package contents and provenance | agents, canonical skills/protocols, inert references, required runtime helper data | `package.json`, `manifests/rose-aili.components.json`, `manifests/upstream-references.json` |

## Narrowest-Fix Rule

Classify the failed component first. Only propose `system-rules` or agent prompt changes when narrower command, skill, protocol, tool-policy, setup, or workflow-pattern changes cannot address the root cause, and only after approval.

## Source Classes

- **Canonical source**: AILI-owned command, top-level skill, agent, protocol, template/generator, manifest, CLI, or installer source. Edit this layer when it owns the behavior.
- **Generated/installed adapter**: root `AGENTS.md`, `dist/`, installed OpenCode/shared-skill targets, and current `.opencode` OpenSpec direct adapters. Do not hand-edit generated output when a canonical source exists.
- **Upstream reference**: pinned licensed data under an existing canonical skill's `references/upstream/`. It is shipped as data only, never registered or routed as a command, skill, agent, hook, or executable.
- **Upstream runtime**: OpenCode/OpenSpec/Graphify or another external runtime. Its direct behavior is not AILI lifecycle evidence unless an AILI-owned route independently applies and records its gates.
