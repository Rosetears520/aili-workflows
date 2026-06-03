## Why

The workflow needs two reusable, narrowly routed skills: one to make complex workflow and technical concepts easier to understand through allegory, and one to turn explicitly provided OpenCode session exports or project evidence into safe, evidence-scoped improvement proposals. This separates low-risk teaching support from higher-risk self-improvement analysis, while avoiding Codex-style assumptions that ROSE can see global history or rewrite its own harness without evidence and approval.

## What Changes

- Add an `explain-by-allegory` skill that explains complex concepts through a short story or analogy, then maps the story back to formal concepts, boundaries, and failure cases.
- Add an `evidence-scoped-retrospective` skill that analyzes user-provided OpenCode session exports and repository evidence for repeated workflow issues, automation opportunities, or skill/subagent/script/memory candidates.
- Have the retrospective skill use a concrete failure-pattern taxonomy inspired by the user-provided 12-rule coding-agent article: assumptions, over-engineering, scope drift, weak success criteria, model use for deterministic work, budget/checkpoint drift, unresolved convention conflicts, insufficient reading before writing, shallow tests, novelty over convention, and silent failure.
- Require retrospective analysis to be evidence-scoped: it must not claim access to global 30-day history, raw hidden memory, or other projects unless the user explicitly provides those artifacts.
- Require retrospective outputs to be report-first proposals. Actual edits to ROSE, commands, skills, subagents, memory policy, install scripts, or harness docs remain gated through the existing lifecycle and harness-evolution approval rules.
- Document that raw OpenCode session exports, transcript dumps, logs, secrets, and private evidence bundles must not be committed; optimized workflow artifacts such as approved skills may be committed after normal verification.
- Add a backend-neutral implementation-note artifact requirement to the generated-project operating discipline: during implementation, maintain an `implementation-notes.html` artifact beside the active spec/task artifacts, regardless of whether the backend is OpenSpec, Superpowers-style, or custom files. The notes record spec deviations, temporary decisions, trade-offs, open questions, and unverified assumptions without storing raw logs or secrets.
- Update the generated-project `AGENTS.md` template to add execution-time guardrails for deterministic work, conflict exposure, read-before-write with read-only scouting, meaningful tests, long-task checkpoints, convention over novelty, and explicit failure reporting.
- Update README skill inventory and conceptual attribution for the new skills without copying upstream prompt text.
- Do not add a new top-level command.
- Do not add a new subagent in the MVP; leave a future option for a read-only session-evidence scout if exported sessions become too large or noisy for ROSE context.

## Capabilities

### New Capabilities

- `explain-by-allegory`: Explain complex concepts through allegory/story plus formal mapping, boundaries, and misconceptions.
- `evidence-scoped-retrospective`: Analyze explicit OpenCode session exports and project evidence to propose bounded workflow self-improvements without storing or committing raw session data.
- `implementation-notes`: Maintain an implementation-time notes artifact for deviations, decisions, trade-offs, open questions, and unverified assumptions across OpenSpec, Superpowers-style, and custom spec backends.

### Modified Capabilities

- `agent-operating-discipline`: Strengthen the managed `templates/AGENTS.md` operating-discipline block with selected Mnilax/Karpathy-style execution guardrails without copying long upstream text.

## Impact

- Adds `skills/explain-by-allegory/SKILL.md`.
- Adds `skills/evidence-scoped-retrospective/SKILL.md`.
- Updates `README.md` skill inventory and conceptual source notes.
- May optionally add small reference templates under the new skill directories if the design requires them.
- No runtime dependencies, scripts, database schema changes, top-level commands, or subagents in the MVP.
- No session JSON or raw transcript artifacts are tracked as part of this change.
- Adds a backend-neutral implementation-note artifact convention. For OpenSpec the default path is `openspec/changes/<change-id>/implementation-notes.html`; other backends use the active task/spec directory or an explicitly approved repository-local path.
- Updates `templates/AGENTS.md` and requires generated project `AGENTS.md` validation through `scripts/agents_md.py check --project .` after implementation.
