# Harness Component Map

Use this map to classify failures before proposing a harness change. Do not modify `agents/rose.md` during normal tasks; agent prompt edits require an explicit harness maintenance task and human approval.

| Category | Owns | Examples | First evidence to check |
|---|---|---|---|
| system-rules | Runtime authority and safety boundaries | ROSE charter, AGENTS template | `agents/rose.md`, `templates/AGENTS.md` |
| command | User entrypoints | `/ideate`, `/define`, `/build`, `/ship` | `commands/*.md` |
| skill | Workflow implementation | delivery flow, harness evolution, review gates | `.agents/skills/*/SKILL.md`, references |
| subagent-config | Delegation contracts | task packets, result reports, specialist boundaries | `agents/*.md`, `.agents/skills/aili-delivery-flow/references/protocols/subagent-*.md` |
| memory | Provenance and receipts | memory writeback, retrieval packs | `.agents/skills/rose-memory/SKILL.md` |
| tool-policy | Tool use and trust boundaries | git, browser, bash, file edits | `docs/harness/tool-policies.md` |
| middleware/hooks | Runtime interception | OpenCode hooks, future middleware | `.opencode/`, setup docs |
| environment | Host constraints | WSL/Linux paths, network, dependencies | setup docs, test-plan |
| workflow-pattern | Lifecycle orchestration | IDEATE/DEFINE/BUILD/SHIP, review-repair | delivery-flow references |
| docs/protocol | Artifact contracts | questionnaires, test plans, reports | `.agents/skills/aili-delivery-flow/references/protocols/*.md`, `docs/harness/*.md` |
| install/setup | Distribution path | command/skill/agent install | `scripts/install_opencode.sh`, setup docs |

## Narrowest-Fix Rule

Classify the failed component first. Only propose `system-rules` or agent prompt changes when narrower command, skill, protocol, tool-policy, setup, or workflow-pattern changes cannot address the root cause, and only after approval.
