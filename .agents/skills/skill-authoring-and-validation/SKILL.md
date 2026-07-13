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
.agents/skills/<skill-name>/
  SKILL.md              # required
  references/           # optional long-form details
  scripts/              # optional deterministic tooling
  assets/               # optional templates or static resources
```

`$HOME/.agents/skills/<skill-name>` is the installed shared runtime target; repository source lives under `.agents/skills/<skill-name>`.

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

## Description as Routing Surface

Treat the frontmatter `description` as the skill's routing surface, not as a tagline.

It must tell the agent:

- what capability the skill provides
- when to use it
- likely trigger phrases, file types, task shapes, or contexts
- when not to use it when overlap with another skill is likely

A vague description makes the skill invisible. An over-broad description makes it over-trigger and waste context. Write the description so a routing decision is obvious from the user's request.

## Body Writing Rules

Write `SKILL.md` for agent execution, not for marketing.

- Start with purpose and when-to-use guidance.
- Put the core workflow in ordered steps.
- Include boundaries, failure modes, and verification.
- Keep instructions short enough to load cheaply.
- Link to `references/` for deep background instead of duplicating it.
- Put exact, repeatable commands in `scripts/` when reliability matters.
- Avoid copying long upstream content unless exact pin, license, notice, inert placement, and repository provenance data are handled before distribution.
- If borrowing an external skill pattern, rewrite the workflow in this repository's voice, remove upstream runtime/tool assumptions, and add explicit provenance either in the skill or `README.md`.

A good skill gives the agent enough structure to avoid drift while preserving judgement where the task needs it.

## Progressive Disclosure and Provenance

- Keep the loaded `SKILL.md` small and actionable; move long examples, rubrics, prompts, and deterministic helpers into optional `references/`, `assets/`, or `scripts/` only when the agent needs them on demand.
- Evaluate routing before content volume: a useful skill has a narrow trigger, clear near-misses, and an obvious handoff to adjacent skills.
- Prefer clean-room pattern absorption over vendoring. When text, code, assets, or templates are copied, include license, copyright, source URL, and notice requirements before shipping.
- Remove foreign runtime assumptions such as project-specific paths, unavailable tools, provider configuration, hosted environments, or branding before adapting a skill to AILI/OpenCode.
- If provenance is uncertain, mark it `Unverified` and do not present the skill as original or ready for distribution.

### Pinned upstream adaptation

Matt Pocock 的 pinned `writing-great-skills` 与 glossary 仅作为 inert reference data 保存在 `references/upstream/`。本 canonical skill 薄适配 predictability、清晰 invocation branches、information hierarchy/progressive disclosure、single source of truth、可检查 completion criteria，以及 duplication/sediment/no-op pruning。应用时仍以本仓库的 ROSE routing、approval、provenance、artifact placement 和 validation gates 为准；不得注册 upstream frontmatter 或把 reference 当作审批/完整性权威。

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
3. Check existing `.agents/skills/*/SKILL.md` to avoid overlap or duplicate routing.
4. Draft the frontmatter first, especially `description`.
5. Draft the body as a compact workflow with boundaries, near-misses, provenance, and verification.
6. Move long examples, reference material, or templates into `references/` only when they are useful on demand.
7. Add scripts only for deterministic operations with clear inputs and safe failure behavior.
8. Update repository documentation and third-party attribution when adding, removing, or vendoring content.
9. Validate triggering with realistic prompts.
10. Iterate until the skill is useful, bounded, and cheap to load.

🔴 **CHECKPOINT · Draft approval gate:** before writing or replacing `SKILL.md`, show the proposed trigger boundary, non-goals, and file/resource changes. Wait for explicit approval when the skill is new, broad, overlaps existing skills, or changes routing behavior.

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

### Over-Trigger Fallbacks

| Trigger condition | First response | If still unresolved |
|---|---|---|
| A prompt could reasonably trigger multiple skills | Name the competing skills and choose the narrowest matching skill | Add an explicit exclusion to the description or stop for user routing input |
| The description uses catch-all wording such as "any development task" | Rewrite it around concrete task shapes, files, or trigger phrases | Do not ship the skill until the routing boundary is narrow enough to test |
| Validation prompts show the skill triggers for another skill's job | Add a `When NOT to use` or exclusion clause in the description/body | Re-run the same prompt; if still ambiguous, keep the skill unapproved |
| The workflow depends on a runtime-specific command or platform | Mark the dependency explicitly or provide a repository-supported fallback | Do not imply cross-runtime support that was not validated |
| The skill adapts external content or patterns | Add source/license/provenance notes and remove copied runtime assumptions | If source/license is unknown, block distribution until provenance is resolved |

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

🛑 **STOP · Do-not-proceed conditions:** do not create or update a skill if it would override ROSE lifecycle authority, duplicate an existing skill without a narrower boundary, require unapproved new dependencies, store project memory, or add scripts/references/assets outside the user's approved scope.

## Verification

Before reporting completion:

- Read the new or changed `SKILL.md` frontmatter.
- Check that `name` matches the folder name.
- Check that the `description` has clear trigger boundaries.
- Check that `README.md` structure and source tables remain accurate when applicable.
- Inspect the diff for accidental vendored text, secrets, generated files, or unrelated changes.
- Report the validation prompts or the reason they were unnecessary.

🔴 **CHECKPOINT · Validation gate:** if frontmatter, trigger prompts, resource paths, ROSE compatibility, or diff inspection fails, report the failure and do not mark the skill ready. Fix only the scoped issue, then repeat this gate.
