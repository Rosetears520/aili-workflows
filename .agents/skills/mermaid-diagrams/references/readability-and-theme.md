# Readability and theme

- Answer one main question per diagram. Keep the level of detail consistent; place implementation internals in a separate detail view when they obscure the main relationship.
- Remove redundant decoration and repeated wording, while keeping facts that change the explanation. Distinct identities, responsibilities, and states remain distinct even when merging them would reduce crossings.
- Use consistent shape semantics. In a flowchart, rectangles can represent actions, diamonds decisions, and cylinders stores. Do not assign different shapes merely to make each concept look unique. Other diagram types have their own notation.
- Label every decision exit with its condition or result. Label relationships with useful verbs, message names, or events. A reader should understand an edge without guessing from its position or color.
- Choose `TD` for a compact vertical flow or `LR` where horizontal comparison helps and the display is wide enough. Neither direction is universal. Keep labels concise and readable, including complete Chinese words such as “校验失败” and “等待审核”. Preserve exact code identifiers when relevant.
- Split a dense view into overview and detail when it becomes hard to trace. There is no fixed node or edge limit. Do not shrink text, erase necessary paths, or invent a distributor to satisfy a layout target.
- Inherit the host theme by default. If color is needed, make it auxiliary to labels and shape semantics, and check text, fill, and border together in light and dark contexts. Do not impose brand fonts, fixed colors, manual SVG geometry, or precise pixel placement.
- Add a brief plain-language summary outside the diagram. Where the target host supports them, `accTitle` and `accDescr` can improve accessibility; they do not replace the summary for nonrendering clients.

Official references: [themes](https://mermaid.js.org/config/theming.html), [accessibility](https://mermaid.js.org/config/accessibility.html), [flowcharts and layout](https://mermaid.js.org/syntax/flowchart.html). Support and resulting layout depend on the actual host and Mermaid version.
