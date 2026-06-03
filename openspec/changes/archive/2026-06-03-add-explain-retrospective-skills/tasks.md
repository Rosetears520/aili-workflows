## 1. Skill Authoring

- [x] 1.1 Create `openspec/changes/add-explain-retrospective-skills/implementation-notes.html` for this OpenSpec change and ensure `templates/AGENTS.md` owns the mandatory implementation-notes rule for OpenSpec, Superpowers-style, and custom spec backends.
- [x] 1.2 Update `templates/AGENTS.md` managed operating-discipline block with selected agentic failure guards: deterministic work via tools/code, conflict exposure, read-before-write with read-only scouting, meaningful tests, long-task checkpoints, convention over novelty, explicit failure, and DCP-aware task-continuity checkpointing instead of absolute token limits or primary raw context-percentage gates.
- [x] 1.3 Create `skills/explain-by-allegory/SKILL.md` with narrow trigger description, workflow, boundaries, output contract, and verification checklist.
- [x] 1.4 Create `skills/evidence-scoped-retrospective/SKILL.md` with explicit evidence scope rules, session-data safety rules, failure-pattern taxonomy, classification workflow, report-first output contract, routing gates, implementation-notes-as-evidence awareness, and verification checklist.
- [x] 1.5 Ensure both skill frontmatter `name` values match their folder names and descriptions avoid over-triggering.

Implementation packaging note: keep this as one OpenSpec proposal, but execute BUILD in separable packages: implementation notes, AGENTS template guardrails, two skills, README/attribution, and verification.

## 2. Documentation and Attribution

- [x] 2.1 Update README project structure / skill inventory to include both new skills.
- [x] 2.2 Update README Rosetears workflow skill table with short descriptions for both new skills.
- [x] 2.3 Update README conceptual source notes to mention Amanda Askell-style allegory prompting and Codex/Vaibhav-style self-improvement prompting as conceptual inspirations without copying upstream prompt text.
- [x] 2.4 Update README conceptual source notes to mention the user-provided Karpathy/Forrest Chang/Mnilax-style 12-rule coding-agent discipline as conceptual prior art for retrospective failure-pattern taxonomy, without copying article text.
- [x] 2.5 Use `https://x.com/Mnilax/status/2053116311132155938` as the requested attribution link for the Mnilax-style agent-discipline source when adding README notes, while marking direct X content as unverified if it cannot be fetched directly.

## 3. Safety and Routing Validation

- [x] 3.1 Validate positive and negative trigger prompts for `explain-by-allegory`, including story/explanation prompts and non-trigger implementation/spec prompts.
- [x] 3.2 Validate positive and negative trigger prompts for `evidence-scoped-retrospective`, including sanitized OpenCode session export analysis, unsupported global-history claims, attempts to commit raw session logs, and classification of at least three concrete failure patterns from the taxonomy.
- [x] 3.3 Confirm the retrospective skill routes skill edits through `skill-authoring-and-validation`, core harness edits through `harness-evolution`, and durable findings through `rose-memory` rather than editing directly.
- [x] 3.4 Confirm implementation-notes behavior is backend-neutral and does not assume OpenSpec-only artifact placement.
- [x] 3.5 Confirm `templates/AGENTS.md` guardrails remain compact, non-duplicative with existing rules, and use DCP-aware task-continuity checkpoint triggers rather than hard-coded absolute token budgets or primary raw context-percentage gates.

## 4. Repository Verification

- [x] 4.1 Inspect the final diff for unrelated changes, raw session JSON, transcripts, logs, secrets, copied upstream prompt text, or generated/vendor artifacts.
- [x] 4.2 Inspect `implementation-notes.html` for raw logs, full transcripts, secrets, private data, or contradictions with formal specs/tasks/context/progress.
- [x] 4.3 Run lightweight repository checks relevant to Markdown/skill/template changes, including `python scripts/agents_md.py check --project .` when available on the implementation branch.
- [x] 4.4 Report remaining `Unverified` items, including the fact that X content was not directly fetched if it remains inaccessible.
