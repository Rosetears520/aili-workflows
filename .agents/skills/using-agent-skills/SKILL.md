---
name: using-agent-skills
description: Discovers and invokes agent skills. Use when starting a session or when you need to discover which skill applies to the current task. This is the meta-skill that governs how all other skills are discovered and invoked.
---

# Using Agent Skills

## Overview

Agent Skills is a collection of engineering workflow skills organized by development phase. Each skill encodes a specific process that senior engineers follow. This meta-skill helps you discover and apply the right skill for your current task.

## Skill Discovery

Skills must be installed or linked into an OpenCode discovery path before the runtime can load them, such as global `~/.config/opencode/skills/` or a supported project-local skills directory. In this repository, run `scripts/install_opencode.sh --mode selective` after adding, deleting, or renaming skills, then restart OpenCode or open a new session to refresh discovery.

When a task arrives, identify the development phase and apply the corresponding skill:

```
Task arrives
    │
    ├── Delivery lifecycle command/mode? → aili-delivery-flow
    ├── Harness/workflow behavior complaint? → harness-issue-triage
    ├── Approved harness/process/ROSE/skill/command/subagent/memory/install change? → harness-evolution
    ├── Vague idea/need refinement? ──→ idea-refine
    ├── Refining a change draft? ─────→ change-interviewer
    ├── Generating test docs / QA plan / test matrix? ─→ test-document-generator
    ├── Triage GitHub issue/PR read-only? → github-evidence-triage
    ├── New project/feature/change? ──→ spec-driven-development
    ├── Have a spec, need tasks? ──────→ planning-and-task-breakdown
    ├── Implementing code? ────────────→ incremental-implementation
    │   ├── Full-stack/backend+frontend? → fullstack-dev
    │   ├── Production app UI? ───────→ frontend-ui-engineering
    │   ├── Marketing/media frontend? ─→ frontend-dev
    │   ├── API work? ────────────────→ api-and-interface-design
    │   ├── Mobile native/cross-platform? → android-native-dev / ios-application-dev / flutter-dev / react-native-dev
    │   ├── GLSL/shader effects? ─────→ shader-dev
    │   ├── Need better context? ─────→ context-engineering
    │   ├── Library/API docs or setup? → source-driven-development
    │   └── Need doc-verified code? ───→ source-driven-development
    ├── Writing/running tests? ────────→ test-driven-development
    │   └── Browser-based? ───────────→ browser-testing-with-devtools
    ├── Creating editable Word/DOCX? ──→ minimax-docx
    ├── Creating print-ready PDF? ─────→ minimax-pdf
    ├── Spreadsheet/workbook/table? ───→ minimax-xlsx
    ├── Slides/deck/presentation? ─────→ pptx-generator
    ├── Need project memory? ──────────→ rose-memory
    ├── Something broke? ──────────────→ debugging-and-error-recovery
    ├── Multiple independent work packages? → parallel-subagent-dispatch
    ├── Explicitly stress-testing an existing artifact/claim? → strategy-stress-test
    ├── Reviewing implementation after changes? → review-pipeline
    ├── Reviewing code? ───────────────→ code-review-and-quality
    │   ├── Security concerns? ───────→ security-and-hardening
    │   └── Performance concerns? ────→ performance-optimization
    ├── Committing/branching? ─────────→ git-workflow-and-versioning
    ├── CI/CD pipeline work? ──────────→ ci-cd-and-automation
    ├── Writing docs/ADRs? ───────────→ documentation-and-adrs
    ├── Creating/revising skills? ─────→ skill-authoring-and-validation
    ├── Initializing AGENTS.md? ───────→ agents-md-initialization
    ├── About to claim complete/fixed/passing? → verification-before-completion
    └── Deploying/launching? ─────────→ shipping-and-launch
```

## Core Operating Behaviors

These behaviors apply at all times, across all skills. ROSE’s canonical guardrails live in `agents/rose.md`; this skill only summarizes them so the routing guidance does not duplicate long operating rules.

- **Think before coding**: understand the goal, constraints, assumptions, and existing patterns before editing. If requirements or sources conflict, stop and ask instead of guessing.
- **Simplicity first**: choose the boring, simplest complete design that satisfies the accepted contract; avoid abstractions that do not earn their complexity.
- **Surgical changes**: touch only the files needed for the task, preserve existing names/APIs/patterns, and report unrelated findings rather than fixing them opportunistically.
- **Goal-driven execution**: keep progress tied to the user’s requested outcome; push back on clearly harmful approaches with concrete tradeoffs, then respect an informed decision.
- **Verify, don’t assume**: every skill ends with evidence such as targeted tests, build/lint output, diff inspection, or a clear manual verification path.
- **Stress-test material artifacts**: for non-trivial interview packets, specs, plans, reconciliations, reviews, or completion claims, use `strategy-stress-test` before accepting the artifact. If the runtime cannot load that skill, perform the same compact loophole/evidence-gap check directly; mark only the affected claim as `Unverified` when needed.

## Domain and File-Output Routing

Use these boundaries before defaulting to generic implementation skills:

🔴 CHECKPOINT for routing conflicts: when two or more skills plausibly apply, choose the skill that owns the user's current artifact or lifecycle gate, then use narrower skills only as sub-steps. Do not let this router restate or override `aili-delivery-flow`, ROSE, review gates, or subagent ownership rules.

| Conflict | Choose first | Fallback if still ambiguous |
|---|---|---|
| `/ideate`, `/define`, `/build`, `/ship` vs any phase skill | `aili-delivery-flow` | Stop and ask which lifecycle mode the user wants |
| Harness behavior complaint vs approved harness edit | `harness-issue-triage` before `harness-evolution` | Do not edit core harness controls until approval exists |
| Implementation plus independent subagent lanes | `parallel-subagent-dispatch` for packet routing, then the domain skill inside each packet | If edit scopes overlap, use sequential work or ask ROSE/user |
| Review after implementation vs direct code review | `review-pipeline` for non-trivial completed changes; `code-review-and-quality` for a single review lane | If blockers cannot be reconciled, keep final PASS blocked |
| Artifact format skill vs generic docs/test planning | Use the explicit output format skill (`minimax-*`, `pptx-generator`) | Ask for output format/placement before writing |

Interview packets and generated test documents are durable project artifacts. For OpenSpec changes, write the repository-local Markdown artifact in the change directory without asking.

For every non-OpenSpec source, including a single source document with an obvious sibling path, ask where to place the artifact before writing; chat-only remains an explicit user-selected fallback.

### Subagent Evidence Routing

- Use `code-scout` for local code discovery: source files, tests, configs, symbols, call chains, and existing implementation patterns.
- Use `doc-researcher` for local documentation discovery: `AGENTS.md`, `rose.md`, skills, OpenSpec changes, README, docs, design notes, and project-local guidance.
- Use `web-researcher` for external research: official documentation, public GitHub README/issues/releases, plugin docs, installation commands, API behavior, compatibility, and deprecation checks.
- Use `plan-auditor` before implementation when a spec, plan, task breakdown, or acceptance story is ambiguous, cross-module, high-risk, or verification-heavy.

### Document Output Routing

- Use `minimax-docx` only when the user explicitly requests Word, DOCX, `.docx`, an editable Office document, or a DOCX template workflow.
- Use `minimax-pdf` when the user requests PDF, print-ready output, PDF form filling, visual page fidelity, or a final non-editable deliverable.
- Use `minimax-xlsx` when the user requests Excel, XLSX, CSV, spreadsheet formulas, financial tables, tabular modeling, or workbook formatting.
- Use `pptx-generator` when the user requests slides, decks, PowerPoint, PPTX, presentation generation, or slide editing.

| User intent / output | Primary skill | Boundary |
|---|---|---|
| `/ideate`, `/define`, `/build`, `/ship`, or delivery lifecycle mode selection | `aili-delivery-flow` | Lifecycle authority for the four top-level modes. Do not duplicate its full flow in this router. |
| User says workflow/ROSE/command/skill/subagent/memory/install behavior is wrong and asks where the issue lives | `harness-issue-triage` | Read-only localization first. Do not edit core harness controls. |
| Approved workflow/process, ROSE, skill, command, subagent, memory, install/setup, hook, or harness-doc changes; repeated workflow failures after localization | `harness-evolution` | Report-first harness governance. Do not edit core harness controls without explicit approval. |
| Explicit Word, `.docx`, editable Office document, or DOCX template workflow | `minimax-docx` | Use only when the output or input workflow is Word/DOCX/editable Office. Do not route generic “report” requests here unless the user wants DOCX/editability/template editing. |
| PDF, print-ready/final non-editable deliverable, PDF form filling, or visual page fidelity | `minimax-pdf` | Use when the artifact is a PDF or page appearance is the deliverable. If the user needs editable Word output, use `minimax-docx`. |
| Excel, `.xlsx`, `.xlsm`, `.csv`, spreadsheet formulas, financial tables, tabular modeling, or workbook formatting | `minimax-xlsx` | Use for workbook/data-table artifacts and formula-preserving edits. Do not use for prose documents or slides. |
| Slides, deck, PowerPoint, `.pptx`, or presentation generation/editing | `pptx-generator` | Use for presentation artifacts. Use `parallel-subagent-dispatch` only for independent slide groups. |
| Backend + frontend integration, service layers, auth, file uploads, realtime, API clients | `fullstack-dev` | Use for end-to-end app/service work. For interface-only contracts use `api-and-interface-design`; for UI-only work use frontend skills. |
| Library/API docs, setup commands, framework examples, or version-sensitive implementation | `source-driven-development` | If Context7 was installed by `npx ctx7 setup --opencode`, prefer the installed Context7 CLI or MCP capability. If unavailable, use official documentation sources. Do not route directly to a core `context7` workflow skill. |
| Rich marketing pages, cinematic motion, AI media assets, persuasive copy, generative art | `frontend-dev` | Use for high-impact standalone frontend experiences. For production UI inside an existing app use `frontend-ui-engineering`. |
| Production UI components, layouts, state, accessibility in an app | `frontend-ui-engineering` | Use for app UI engineering without the media/cinematic stack. |
| Android native Kotlin/Compose or Android platform APIs | `android-native-dev` | Use for native Android only, not React Native/Flutter/web React. |
| iOS native UIKit/SwiftUI/SnapKit or Apple platform APIs | `ios-application-dev` | Use for native iOS only, not React Native/Flutter/web React. |
| Flutter/Dart cross-platform apps | `flutter-dev` | Use for Flutter projects and widgets, not web React or native-only Android/iOS. |
| React Native or Expo mobile apps | `react-native-dev` | Use for mobile RN/Expo, not browser React. |
| GLSL, shader code, ShaderToy/WebGL shader effects, SDF/ray marching/procedural visuals | `shader-dev` | Use only for shader/procedural visual-effect work, not generic CSS/JS animation. |
| Durable project memory or focused retrieval/writeback | `rose-memory` | Use when a task needs ROSE project-local SQLite memory. |
| Create/update/validate Agent Skills | `skill-authoring-and-validation` | Use for skill authoring and package validation work. |
| Independent work packages for subagents | `parallel-subagent-dispatch` | Use when work can safely run in parallel and then be merged. |
| Explicit loophole/evidence-gap audit of an existing artifact or claim | `strategy-stress-test` | Use as standalone only when the user asks to stress-test/review a draft, plan, claim, or strategy. Otherwise call it as a sub-step inside the owning skill. |
| Post-implementation review orchestration | `review-pipeline` | Use after non-trivial implementation to fan out relevant reviewer agents, reconcile findings, run a bounded fix loop, and gate final PASS. |
| Read-only GitHub issue/PR triage | `github-evidence-triage` | Use when analyzing GitHub issues or PRs without comments, labels, reviews, merges, pushes, or other write actions. |
| About to claim complete/fixed/passing/verified | `verification-before-completion` | Use fresh evidence before completion claims. |
| Clarifying or writing back change drafts | `change-interviewer` | Use when an existing spec, plan, issue, or change draft needs source-grounded interview questions or a Chinese interview packet for user-filled decisions before write-back. |
| Test docs, QA plans, test matrices, or regression checklists | `test-document-generator` | Use when tests must be documented from specs/plans/descriptions without writing or running test code. |

## Failure Modes to Avoid

These are the subtle errors that look like productivity but create problems:

1. Making wrong assumptions without checking
2. Not managing your own confusion — plowing ahead when lost
3. Not surfacing inconsistencies you notice
4. Not presenting tradeoffs on non-obvious decisions
5. Being sycophantic ("Of course!") to approaches with clear problems
6. Overcomplicating code and APIs
7. Modifying code or comments orthogonal to the task
8. Removing things you don't fully understand
9. Building without a spec because "it's obvious"
10. Skipping verification because "it looks right"

## Skill Rules

1. **Check for an applicable skill before starting work.** Skills encode processes that prevent common mistakes.

2. **Skills are workflows, not suggestions.** Follow the steps in order. Don't skip verification steps.

3. **Multiple skills can apply.** A feature implementation might involve `idea-refine` → `spec-driven-development` → `planning-and-task-breakdown` → `incremental-implementation` → `test-driven-development` → `code-review-and-quality` → `shipping-and-launch` in sequence.

4. **When in doubt, start with a spec.** If the task is non-trivial and there's no spec, begin with `spec-driven-development`.

## Lifecycle Boundary

Do not duplicate the full delivery lifecycle here. If the user invokes `/ideate`, `/define`, `/build`, `/ship`, or asks for AILI lifecycle routing, hand control to `aili-delivery-flow` and let that skill own mode transitions, gates, and final routing.

For ordinary non-lifecycle work, choose only the narrowest applicable chain. Example: a bug fix might need `debugging-and-error-recovery` → `test-driven-development` → `code-review-and-quality`; a completed non-trivial diff might go directly to `review-pipeline`.

Use `strategy-stress-test` conditionally whenever a material artifact or claim exists and risk warrants it, such as before accepting a spec, plan, review, reconciliation, or completion claim. If the skill is not available in the current runtime, perform the same compact check directly instead of skipping the guardrail.

## Quick Reference

| Phase | Skill | One-Line Summary |
|-------|-------|-----------------|
| Define | idea-refine | Refine ideas through structured divergent and convergent thinking |
| Define | change-interviewer | Interview to clarify and write back change drafts |
| Define | github-evidence-triage | Read-only GitHub issue/PR triage with evidence links |
| Define | spec-driven-development | Requirements and acceptance criteria before code |
| Define | agents-md-initialization | Generate project AGENTS.md from the shared template |
| Plan | planning-and-task-breakdown | Decompose into small, verifiable tasks |
| Build | incremental-implementation | Thin vertical slices, test each before expanding |
| Build | source-driven-development | Verify against official docs before implementing |
| Build | context-engineering | Right context at the right time |
| Build | fullstack-dev | Backend + frontend integration and production service patterns |
| Build | frontend-dev | Rich marketing/media/cinematic frontend experiences |
| Build | frontend-ui-engineering | Production-quality UI with accessibility |
| Build | api-and-interface-design | Stable interfaces with clear contracts |
| Build | android-native-dev | Native Android, Kotlin, Compose, Material 3 |
| Build | ios-application-dev | Native iOS, UIKit, SwiftUI, Apple HIG |
| Build | flutter-dev | Flutter/Dart cross-platform applications |
| Build | react-native-dev | React Native and Expo mobile applications |
| Build | shader-dev | GLSL shaders and procedural visual effects |
| Build | minimax-docx | Editable Word/DOCX document workflows |
| Build | minimax-pdf | Print-ready PDF generation, styling, and form filling |
| Build | minimax-xlsx | Excel/CSV/spreadsheet formulas and workbook formatting |
| Build | pptx-generator | PowerPoint slides, decks, and presentations |
| Build | parallel-subagent-dispatch | Split independent work packages across subagents |
| Build | rose-memory | Project-local SQLite memory retrieval/writeback |
| Verify | test-driven-development | Failing test first, then make it pass |
| Verify | test-document-generator | Generate evidence-grounded test plans, test matrices, QA docs, and regression checklists from specs/plans/descriptions |
| Verify | browser-testing-with-devtools | OpenCode Playwright browser tools for runtime verification |
| Verify | debugging-and-error-recovery | Reproduce → localize → fix → guard |
| Verify | verification-before-completion | Fresh evidence before completion claims |
| Verify | strategy-stress-test | Find material loopholes, evidence gaps, counterexamples, and verification gaps before accepting artifacts or claims |
| Review | review-pipeline | Orchestrate post-implementation review, reconcile findings, and gate final PASS |
| Review | code-review-and-quality | Five-axis review with quality gates |
| Review | security-and-hardening | OWASP prevention, input validation, least privilege |
| Review | performance-optimization | Measure first, optimize only what matters |
| Ship | git-workflow-and-versioning | Atomic commits, clean history |
| Ship | ci-cd-and-automation | Automated quality gates on every change |
| Ship | documentation-and-adrs | Document the why, not just the what |
| Ship | skill-authoring-and-validation | Create, revise, and validate repository Agent Skills |
| Ship | shipping-and-launch | Pre-launch checklist, monitoring, rollback plan |
