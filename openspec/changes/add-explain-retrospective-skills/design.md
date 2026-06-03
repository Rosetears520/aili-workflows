## Context

This repository is a personal OpenCode workflow harness. It already uses natural-language skill routing, four lifecycle commands, ROSE as the primary orchestrator, and subagents as bounded evidence or work-package lanes. The user wants two additions:

- an Amanda Askell-inspired explanation mode that uses allegory to teach difficult concepts;
- a Codex-inspired self-improvement pass that can inspect exported OpenCode sessions, identify repeated workflow patterns, and propose skills, subagents, scripts, memory entries, or harness changes.

The main constraint is that OpenCode does not provide ROSE with an implicit, global, cross-project 30-day memory. Session exports can be provided explicitly, but raw sessions may contain secrets, private code, paths, logs, and transcript content. This change therefore treats retrospective input as explicit, untrusted evidence and keeps raw session artifacts out of git and durable memory.

The user also provided an article summarizing a 12-rule coding-agent discipline derived from Karpathy/Forrest Chang-style guardrails plus additional multi-step agent failure modes. This change uses that material as conceptual prior art for retrospective analysis dimensions, not as vendored text or an instruction block to paste into prompts.

## Goals / Non-Goals

**Goals:**

- Add a narrow `explain-by-allegory` skill for teaching/explanation tasks.
- Add a narrow `evidence-scoped-retrospective` skill for OpenCode-session-driven workflow improvement proposals.
- Add a backend-neutral implementation-time notes artifact requirement so BUILD work can preserve deviations, temporary decisions, trade-offs, open questions, and unverified assumptions without polluting specs or raw progress logs.
- Strengthen the generated-project `AGENTS.md` operating discipline with selected execution-time guardrails from the user-provided open article: deterministic work should use code/tools, conflicts must be exposed, reading must precede writing, tests must verify meaningful behavior, long tasks require checkpoints, local convention beats novelty, and uncertainty must be explicit.
- Keep self-improvement report-first and evidence-scoped.
- Preserve existing lifecycle, harness-evolution, skill-authoring, memory, and subagent ownership gates.
- Make clear that optimized skills and approved workflow artifacts can be committed, while raw session exports cannot.

**Non-Goals:**

- Do not add a `/self-improve`, `/retrospective`, or other new top-level command.
- Do not add a new subagent in the MVP.
- Do not automatically rewrite ROSE, commands, skills, subagent contracts, install scripts, memory policy, or harness docs.
- Do not persist raw session exports, transcript dumps, logs, or secrets in git or durable memory.
- Do not copy upstream prompt text from X, Amanda Askell, Codex, or other sources.
- Do not paste the full 12-rule article into `templates/AGENTS.md`; keep the managed block compact and behavior-focused.
- Do not set universal absolute token budgets or raw context-percentage gates in `templates/AGENTS.md` because model windows, task shapes, OpenCode compaction, and DCP compression behavior vary; use DCP-aware task-continuity checkpoint triggers instead.
- Do not replace formal specs, `context.md`, `progress.txt`, `handoff.md`, ADRs, or verification artifacts with `implementation-notes.html`; it is an implementation-time supplement.

## Decisions

### Decision 1: Implement both workflows as skills first

`explain-by-allegory` is a teaching workflow, not a persona, command, or script. `evidence-scoped-retrospective` is also primarily a workflow: define input scope, inspect evidence, classify patterns, and route recommendations through existing gates.

Alternative considered: create a dedicated self-improvement subagent immediately. This was rejected for the MVP because final judgment and routing must remain with ROSE, and a subagent is only justified once real session exports prove that evidence extraction is noisy enough to require isolation.

### Decision 2: Keep retrospective evidence explicit and bounded

The retrospective skill will accept only explicit evidence sources such as user-provided sanitized OpenCode exports, session lists, selected raw excerpts, current project files, git history, or existing `rose-memory` retrieval results. It must label unsupported global-history claims as `Unverified`.

Alternative considered: mimic Codex self-improvement prompts that assume the agent can review recent global work. This was rejected because it would encourage false visibility claims in OpenCode.

### Decision 3: Separate raw evidence from optimized artifacts

The skill will instruct agents not to commit raw session JSON, logs, transcripts, or secrets. If a retrospective leads to an approved new or optimized skill, the skill file itself is normal tracked workflow code and can be committed after review and verification.

Alternative considered: store exported sessions in a repo-local evidence directory. This was rejected for the MVP because session data may be sensitive and repository placement/retention policy needs separate approval.

### Decision 4: Require report-first routing for self-improvement outputs

The retrospective skill will produce a structured report: evidence inspected, observed repeated patterns, proposed improvement type, target artifact, risk, and next lifecycle action. Edits still go through `skill-authoring-and-validation`, `harness-evolution`, `rose-memory`, or the normal delivery lifecycle.

The retrospective skill is not OpenSpec-specific. If the report recommends a spec-like proposal, it should inspect the current repository workflow and available backends, choose the narrowest suitable proposal mechanism, and ask the user before creating or updating proposal artifacts. In this repository that may be OpenSpec, but other projects may use Superpowers-style plans or custom files.

Alternative considered: let the skill apply changes directly. This was rejected because self-improvement touches high-risk harness surfaces and could overfit from incomplete session evidence.

### Decision 5: Use a failure-pattern taxonomy for retrospective analysis

The retrospective skill should inspect evidence for concrete failure signatures rather than vague improvement opportunities. The initial taxonomy should include silent assumptions, over-engineering, scope drift, weak or missing success criteria, model use where deterministic code/tooling should decide, budget or checkpoint drift in long tasks, unresolved conflicts between existing patterns, writing before reading enough context, shallow tests that do not verify business logic, novelty over local convention, and silent or overstated success claims.

Alternative considered: add the full 12-rule article as workflow rules. This was rejected because long rule dumps reduce routing clarity, risk source/attribution problems, and duplicate existing ROSE discipline. The skill should instead map observed evidence to compact failure categories and then propose targeted improvements.

### Decision 6: Add selected execution guardrails to `templates/AGENTS.md`

The AGENTS template should receive a compact “agentic failure guards” subsection in its managed operating-discipline block. It should include only the selected high-value rules the user explicitly requested: do not use model judgment for deterministic work, expose conflicts rather than blending incompatible patterns, read before writing and use read-only subagents for broad reading, write tests that prove important behavior, checkpoint long-running operations, prefer local convention over novelty, and make uncertainty/failure explicit.

Rule 6 from the article should not be copied as absolute budgets such as 4,000 tokens per task or 30,000 per session. It also should not depend primarily on raw context-usage percentages when DCP or other compression is active, because compressed context can make visible usage diverge from the real continuity risk. Instead, the template should use DCP-aware task-continuity triggers: if the agent cannot accurately restate the active contract, changed files, open decisions, or verification path; if working state depends on details that exist only in compressed/raw session history and have not been re-grounded in files or todos; if tool output, logs, or subagent reports are accumulating faster than they are distilled into durable artifacts; if the same debug/review loop repeats without a new hypothesis, evidence anchor, or decision; or if the next step would edit/review/ship from memory rather than fresh repo evidence, then the agent must checkpoint. A soft checkpoint summarizes the current contract, decisions, files, todos, unknowns, and verification path while reducing further context growth. A hard checkpoint stops before more edits and writes or updates the approved task artifact, progress/checkpoint, handoff, or implementation notes before re-grounding from repo evidence.

Alternative considered: put the full article text or all 12 rules into the AGENTS template. This was rejected because the existing template already covers several base rules, long rule dumps reduce compliance, and the repository prefers compact, testable guardrails.

### Decision 7: Add backend-neutral `implementation-notes.html` as implementation operating discipline

For any approved spec-backed implementation work, the generated-project operating discipline in `templates/AGENTS.md` should require maintaining an `implementation-notes.html` artifact beside the active spec/task artifacts. For OpenSpec the default path is `openspec/changes/<change-id>/implementation-notes.html`. For Superpowers-style plans or custom spec/task files, use the active task/spec directory when obvious; otherwise ask for an explicitly approved repository-local path before writing. The file should capture implementation-specific deviations from spec, temporary decisions, trade-offs accepted, open questions, unverified assumptions, evidence pointers, and update history. It must not contain raw logs, full transcripts, secrets, or large pasted file contents.

The MVP format should be simple static HTML for human review, with no JavaScript or external CSS dependency. It should use the user's language by default; when the user's language is unclear, default to Simplified Chinese for this workflow. Required sections are: title, metadata, Spec Deviations, Temporary Decisions, Trade-offs, Open Questions, Unverified Assumptions, Evidence Pointers, and Update History.

Alternative considered: make the retrospective skill own the mandatory notes rule. This was rejected because retrospective should consume `implementation-notes.html` as evidence, while BUILD-time execution discipline belongs in `templates/AGENTS.md` or ROSE BUILD supervision. HTML is accepted here because the user explicitly requires `implementation-notes.html`.

## Risks / Trade-offs

- **Over-triggering of explanation skill** → Use a narrow description and explicit exclusions for implementation, specs, source-cited guidance, and fiction-only generation.
- **Retrospective treats transcript text as instructions** → Mark session exports as untrusted data and extract evidence only; do not follow instructions embedded in old transcripts.
- **Sensitive data leakage from session exports** → Prefer sanitized exports, redact secrets, and prohibit committing raw sessions or storing them in durable memory.
- **Self-improvement overfits from one bad session** → Require evidence strength labels and classify one-off issues separately from repeated patterns.
- **Retrospective becomes a generic rule dump** → Use the 12-rule article as a compact failure-pattern taxonomy, not as copied prompt text or always-on global rules.
- **AGENTS template grows too large** → Add only compact, non-duplicative guardrails and keep detailed retrospective analysis in the skill.
- **Token or percentage gates become stale or wrong under DCP** → Encode Rule 6 as task-continuity checkpoint triggers with DCP-aware evidence re-grounding instead of fixed token counts or primary reliance on raw context percentages.
- **Implementation notes duplicate formal artifacts** → Keep `implementation-notes.html` supplemental and require formal specs/tasks/context/progress to remain authoritative for their own purposes.
- **HTML artifact could contain sensitive material** → Require notes to use concise summaries and evidence pointers, not raw logs, transcripts, secrets, or full file dumps.
- **Subagent need emerges later** → Document a future optional read-only session-evidence scout, but do not add it until real context/noise pressure justifies the extra routing surface.
- **OpenSpec artifacts may be ignored on this branch** → Treat this proposal as a planning artifact; tracked implementation changes remain the two skills and README updates after approval.

## Migration Plan

1. Add the mandatory `implementation-notes.html` rule to `templates/AGENTS.md` as implementation operating discipline; for this OpenSpec change, maintain `openspec/changes/add-explain-retrospective-skills/implementation-notes.html`.
2. Update `templates/AGENTS.md` managed operating-discipline block with compact selected execution guardrails and DCP-aware task-continuity checkpoint triggers instead of absolute token budgets or primary raw-percentage gates.
3. Create the two skill directories and `SKILL.md` files, including a compact retrospective failure-pattern taxonomy derived from the user-provided prior art without copying upstream prompt text.
4. Update README skill inventory and concept-source notes.
5. Validate trigger behavior with positive and negative prompts.
6. Inspect diff for accidental upstream text, raw sessions, secrets, or unrelated changes, including the implementation notes artifact.
7. Run lightweight repository verification appropriate to skill/docs changes, including `python scripts/agents_md.py check --project .`.
8. Re-run install or start a new OpenCode session when the user wants OpenCode discovery refreshed.

Rollback is deleting the two new skill directories and reverting README updates. No data migration is required.

## Open Questions

- None blocking for BUILD after the user confirmed the interview defaults. The MVP keeps the policy as “do not place raw session exports in the repo” unless a user explicitly approves a repo-local ignored path in a future change.
