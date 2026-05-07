---
name: skill-authoring-and-validation
description: Create, revise, and validate Agent Skills for this repository. Use when the user wants to add a new SKILL.md, improve an existing skill, convert repeated workflow instructions into a skill, optimize skill triggering, split references/scripts/assets, or check whether a skill is too broad, too long, or likely to over-trigger.
---

# Skill Authoring and Validation

## Purpose

Create and maintain Agent Skills that fit this OpenCode workflow repository.

Use Codex-style Agent Skills as the primary authoring model: concise `SKILL.md`, clear `name` and `description`, progressive disclosure through optional `references/`, `scripts/`, and `assets/`, and no platform-specific runtime assumptions unless this repository explicitly needs them.

Borrow Claude-style skill creation only for the human workflow and validation loop: interview the user, capture real examples, test trigger behavior, and iterate when the skill is important or ambiguous.

## When to Create a Skill

Create or revise a skill when a workflow is:

- repeated across projects or sessions
- easy for an agent to forget, skip, or mis-sequence
- specific enough to have clear trigger phrases and boundaries
- useful as a reusable process, not just one-off project documentation
- compatible with ROSE natural-language skill invocation

Do not create a skill for:

- general knowledge the model already has
- project facts that belong in `AGENTS.md`, `README.md`, docs, or memory
- broad personas or roles that belong under `agents/`
- slash-command-only orchestration that conflicts with this repository's natural-language model
- scripts without a workflow explaining when and why to use them

## Required Structure

Every skill must live in a self-contained folder:

```text
skills/<skill-name>/
  SKILL.md              # required
  references/           # optional long-form details
  scripts/              # optional deterministic tooling
  assets/               # optional templates or static resources
```

Keep the directory name and frontmatter `name` identical, lowercase, and kebab-case.

Do not add platform-specific files such as `agents/openai.yaml` unless this repository adopts that platform contract explicitly.

## Frontmatter Rules

`SKILL.md` must start with YAML frontmatter:

```markdown
---
name: skill-name
description: One sentence that states what the skill does and when to use it.
---
```

The `description` is the primary trigger surface. It should:

- include likely user phrases and task intents
- state clear use cases and boundaries
- avoid generic wording such as "helps with development"
- avoid pushy catch-all language that causes over-triggering
- mention important exclusions when confusion is likely

Prefer one dense, accurate paragraph over many metadata fields.

## Body Writing Rules

Write `SKILL.md` for agent execution, not for marketing.

- Start with purpose and when-to-use guidance.
- Put the core workflow in ordered steps.
- Include boundaries, failure modes, and verification.
- Keep instructions short enough to load cheaply.
- Link to `references/` for deep background instead of duplicating it.
- Put exact, repeatable commands in `scripts/` when reliability matters.
- Avoid copying long upstream content unless license and source attribution are handled in `README.md`.

A good skill gives the agent enough structure to avoid drift while preserving judgement where the task needs it.

## Freedom-Level Choice

Choose the level of control based on task fragility:

| Level | Use For | Skill Form |
|---|---|---|
| High freedom | judgement-heavy workflows, reviews, planning, writing | principles, checklists, examples |
| Medium freedom | semi-structured transformations or repeatable decisions | templates, decision tables, pseudocode |
| Low freedom | error-prone, deterministic, or stateful operations | scripts with explicit arguments and verification |

Do not turn every workflow into a script. Scripts are best for actions that must be consistent across runs.

## Authoring Workflow

1. Identify the real workflow the user wants to preserve.
2. Ask only the missing questions needed to determine scope, trigger conditions, inputs, outputs, success criteria, and non-goals.
3. Check existing `skills/*/SKILL.md` to avoid overlap or duplicate routing.
4. Draft the frontmatter first, especially `description`.
5. Draft the body as a compact workflow with boundaries and verification.
6. Move long examples, reference material, or templates into `references/` only when they are useful on demand.
7. Add scripts only for deterministic operations with clear inputs and safe failure behavior.
8. Update repository documentation and third-party attribution when adding, removing, or vendoring content.
9. Validate triggering with realistic prompts.
10. Iterate until the skill is useful, bounded, and cheap to load.

## Trigger Validation

For each new or materially changed skill, write 2-3 realistic prompts a user might say.

For each prompt, check:

- Should this skill trigger?
- Which other skills might also trigger?
- Does the `description` make the intended routing obvious?
- Is there an over-trigger case where this skill should not run?
- Does the expected output match the workflow and repository conventions?

Example validation table:

| Prompt | Expected | Notes |
|---|---|---|
| "Create a reusable skill for release checklists" | trigger | authoring a new `SKILL.md` |
| "Review this existing skill for over-triggering" | trigger | validation request |
| "Initialize AGENTS.md in this repo" | do not trigger | belongs to `agents-md-initialization` |

## Optional Advanced Eval Loop

Use this only for important, broad, or high-risk skills.

1. Capture baseline behavior without the skill.
2. Run the same prompts with the skill available.
3. Compare trigger accuracy, output usefulness, missed constraints, and unnecessary context use.
4. Revise `description`, boundaries, or examples.
5. Repeat until the skill improves behavior without causing over-triggering.

This repository does not assume Claude-specific eval tooling. Use available local tests, review prompts, or manual comparison unless a dedicated eval harness is added later.

## ROSE Compatibility Checks

Before finishing, confirm:

- The skill can be invoked through natural-language intent, not only slash commands.
- The skill does not override `agents/rose.md` as the primary control plane.
- The skill does not duplicate project memory; durable facts belong in `rose-memory` when appropriate.
- The skill distinguishes workflow instructions from persona behavior.
- The skill has clear handoff points to other skills when needed.

## Verification

Before reporting completion:

- Read the new or changed `SKILL.md` frontmatter.
- Check that `name` matches the folder name.
- Check that the `description` has clear trigger boundaries.
- Check that `README.md` structure and source tables remain accurate when applicable.
- Inspect the diff for accidental vendored text, secrets, generated files, or unrelated changes.
- Report the validation prompts or the reason they were unnecessary.
