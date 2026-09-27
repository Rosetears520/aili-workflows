# Syntax pitfalls

Use the chosen type's official documentation and the target host/version for syntax questions. These are source-review reminders, not a parser or a claim of universal compatibility.

- Keep identifiers stable, unique, and separate from display labels. For flowcharts, `review["审核申请"]` gives a simple identifier and a quoted Chinese label. Quote labels with punctuation that may otherwise be read as syntax.
- Match each type's syntax. Flowchart shape delimiters, sequence participants, and ER cardinalities are different languages within Mermaid; do not mix their edge forms.
- In flowcharts, lowercase `end` has special significance; choose a different identifier and use a quoted display label where needed. Spacing around links helps avoid unintended circle/cross edge notation when identifiers begin with `o` or `x`. Consult the official flowchart warnings for the exact form being used.
- Prefer `flowchart` as the local writing convention. `graph` is also official flowchart syntax; do not call it obsolete or claim it lacks all modern features.
- Do not promise a nested subgraph's direction will control layout: external links to its nodes can affect that direction. Preserve topology and try a different overall direction or a separate detail view.
- Keep short labels on one line where possible. HTML line breaks, Markdown labels, configuration directives, icons, newer shapes, mindmaps, and timelines depend on version and host settings. Verify support before relying on them; do not lower security settings to make a label render.
- For parse failures, use the actual error location and nearby statement, make the smallest meaning-preserving correction, and rerun the available parser if authorized. Bracket counting or a hand-written regex cannot establish Mermaid parser acceptance.

Official references: [flowchart syntax and warnings](https://mermaid.js.org/syntax/flowchart.html), [sequence syntax](https://mermaid.js.org/syntax/sequenceDiagram.html), [configuration](https://mermaid.js.org/config/configuration.html). Current web documentation may describe a newer release than the target host.
