---
name: using-agent-skills
description: Discovers and invokes agent skills. Use when starting a session or when you need to discover which skill applies to the current task. This is the meta-skill that governs how all other skills are discovered and invoked.
---

# Using Agent Skills

## Overview

Agent Skills is a collection of engineering workflow skills organized by development phase. Each skill encodes a specific process that senior engineers follow. This meta-skill helps you discover and apply the right skill for your current task.

## Skill Discovery

When a task arrives, identify the development phase and apply the corresponding skill:

```
Task arrives
    │
    ├── Vague idea/need refinement? ──→ idea-refine
    ├── Refining a change draft? ─────→ change-interviewer
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
    ├── Stress-testing a draft/claim? → strategy-stress-test
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
- **Simplicity first**: choose the boring, smallest design that satisfies the accepted contract; avoid abstractions that do not earn their complexity.
- **Surgical changes**: touch only the files needed for the task, preserve existing names/APIs/patterns, and report unrelated findings rather than fixing them opportunistically.
- **Goal-driven execution**: keep progress tied to the user’s requested outcome; push back on clearly harmful approaches with concrete tradeoffs, then respect an informed decision.
- **Verify, don’t assume**: every skill ends with evidence such as targeted tests, build/lint output, diff inspection, or a clear manual verification path.
- **Stress-test material artifacts**: for non-trivial interview packets, specs, plans, reconciliations, reviews, or completion claims, use `strategy-stress-test` before accepting the artifact. If the runtime cannot load that skill, perform the same compact loophole/evidence-gap check directly and mark runtime availability as `Unverified`.

## Domain and File-Output Routing

Use these boundaries before defaulting to generic implementation skills:

### Document Output Routing

- Use `minimax-docx` only when the user explicitly requests Word, DOCX, `.docx`, an editable Office document, or a DOCX template workflow.
- Use `minimax-pdf` when the user requests PDF, print-ready output, PDF form filling, visual page fidelity, or a final non-editable deliverable.
- Use `minimax-xlsx` when the user requests Excel, XLSX, CSV, spreadsheet formulas, financial tables, tabular modeling, or workbook formatting.
- Use `pptx-generator` when the user requests slides, decks, PowerPoint, PPTX, presentation generation, or slide editing.

| User intent / output | Primary skill | Boundary |
|---|---|---|
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
| Stress-testing drafts or claims | `strategy-stress-test` | Use after a first artifact exists and before accepting, writing back, dispatching, implementing, reviewing as final, or claiming completion. Do not use for tiny obvious edits or pure brainstorming. |
| About to claim complete/fixed/passing/verified | `verification-before-completion` | Use fresh evidence before completion claims. |
| Clarifying or writing back change drafts | `change-interviewer` | Use when an existing spec, plan, issue, or change draft needs source-grounded interview questions or a Chinese interview packet for user-filled decisions before write-back. |

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

## Lifecycle Sequence

For a complete feature, the typical skill sequence is:

```
1. idea-refine                 → Refine vague ideas
2. spec-driven-development     → Define what we're building
3. planning-and-task-breakdown → Break into verifiable chunks
4. context-engineering         → Load the right context
5. source-driven-development   → Verify against official docs
6. incremental-implementation  → Build slice by slice
7. test-driven-development     → Prove each slice works
8. code-review-and-quality     → Review before merge
9. git-workflow-and-versioning → Clean commit history
10. documentation-and-adrs     → Document decisions
11. shipping-and-launch        → Deploy safely
```

Use `strategy-stress-test` conditionally whenever a material artifact or claim exists and risk warrants it, such as before accepting a spec, plan, review, reconciliation, or completion claim. If the skill is not available in the current runtime, perform the same compact check directly instead of skipping the guardrail.

Not every task needs every skill. A bug fix might only need: `debugging-and-error-recovery` → `test-driven-development` → `code-review-and-quality`.

## Quick Reference

| Phase | Skill | One-Line Summary |
|-------|-------|-----------------|
| Define | idea-refine | Refine ideas through structured divergent and convergent thinking |
| Define | change-interviewer | Interview to clarify and write back change drafts |
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
| Verify | browser-testing-with-devtools | OpenCode Playwright browser tools for runtime verification |
| Verify | debugging-and-error-recovery | Reproduce → localize → fix → guard |
| Verify | verification-before-completion | Fresh evidence before completion claims |
| Verify | strategy-stress-test | Find material loopholes, evidence gaps, counterexamples, and verification gaps before accepting artifacts or claims |
| Review | code-review-and-quality | Five-axis review with quality gates |
| Review | security-and-hardening | OWASP prevention, input validation, least privilege |
| Review | performance-optimization | Measure first, optimize only what matters |
| Ship | git-workflow-and-versioning | Atomic commits, clean history |
| Ship | ci-cd-and-automation | Automated quality gates on every change |
| Ship | documentation-and-adrs | Document the why, not just the what |
| Ship | skill-authoring-and-validation | Create, revise, and validate repository Agent Skills |
| Ship | shipping-and-launch | Pre-launch checklist, monitoring, rollback plan |
