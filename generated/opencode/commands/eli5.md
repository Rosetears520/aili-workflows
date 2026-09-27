---
description: "Explain something in simple plain language, optionally with a visual HTML explainer"
argument-hint: "[--html] <topic>"
agent: rose
subtask: false
---

<!-- GENERATED: aili-runtime-projections/v1; canonical_inputs: adapters/opencode/adapter.json, adapters/pi/adapter.json, core/commands/eli5.md, core/governance/decision-core.md, core/governance/operating-discipline.md, core/roles/roles.json, manifests/runtime-projections.json; input_sha256: 25134e1d167dfde93353ef9e2e70baf633dd8959333e22d441c3d3f56ca23c0a; do not edit directly -->

# /eli5

User input: `$ARGUMENTS`

Explain the requested topic like I'm someone who knows nothing about it.

Default behavior:

Give a concise, natural plain-text explanation directly in chat.

Do not use Markdown formatting, headings, tables, or unnecessary bullet lists.

Prefer simple language and concrete analogies when they help.

Do not oversimplify away important facts.

If the topic depends on the current project, inspect the relevant code, files, logs, or context before explaining it.

If $ARGUMENTS contains --html:

Still give the concise plain-text explanation in chat.

Also create a self-contained HTML visual explainer.

The HTML should favor large visuals, diagrams, arrows, and few words.

Do not dump the HTML source into chat; create the file and return its path.

Treat --html as an output option, not part of the topic.

Request: $ARGUMENTS
