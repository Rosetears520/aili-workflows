---
name: explain-by-allegory
description: Explain a complex concept through a short allegory, story, analogy, metaphor, or intuitive teaching example, then map it back to formal concepts and limits; do not use as the primary skill for implementation, specs, source-cited API guidance, or fiction-only writing.
---

# Explain by Allegory

## Purpose

Use this skill when the user asks to understand a difficult concept through a story, allegory, analogy, metaphor, or intuitive example.

The goal is teaching support: make the idea easier to grasp, then clearly translate the story back into accurate formal terms.

## When to Use

Use for prompts such as:

- "用寓言解释 embeddings，并说明哪里不准确。"
- "Explain consensus algorithms with a story."
- "Give me an analogy for DCP/context compression and then map it to the real workflow."

## When Not to Use

Do not use this as the primary skill when the user asks to:

- implement code, fix a bug, or change files;
- design a public API or acceptance contract;
- follow current official framework/library documentation;
- produce source-cited technical instructions;
- write fiction where the story itself is the deliverable.

If the concept affects an implementation, architecture, workflow, or spec decision, keep the allegory separate from the formal decision and route the decision through the appropriate workflow.

## Workflow

1. Identify the real concept and the user's desired depth.
2. Choose a compact allegory that preserves the most important structure of the concept.
3. Tell the allegory in a few paragraphs; avoid overfitting every detail.
4. Map story elements back to formal concepts.
5. Give the formal explanation in direct technical language.
6. State where the allegory breaks down, including boundary cases and misconceptions it could create.
7. If the user needs action after understanding, recommend the next workflow, such as source-driven development, spec-driven development, implementation, documentation, or ADRs.

## Output Contract

Return these sections unless the user asks for a different format:

```text
Allegory:
- <short story or analogy>

Mapping:
- <story element> -> <formal concept>

Formal Explanation:
- <plain technical explanation>

Limits and Misconceptions:
- <where the allegory fails or can mislead>

Next Step, if needed:
- <appropriate workflow or question>
```

## Verification

Before answering, check:

- The output includes both the story and the formal explanation.
- Important story elements are mapped back to real concepts.
- Limits, boundary cases, or common misconceptions are stated.
- The story is not presented as an authoritative spec, source citation, implementation plan, or acceptance contract.
- Any needed next workflow is named without doing out-of-scope work.
