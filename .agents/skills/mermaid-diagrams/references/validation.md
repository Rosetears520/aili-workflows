# Validation and evidence

Choose checks that support the requested deliverable. A brief conversational diagram does not automatically require rendering.

| Check | Evidence | What it does not establish |
| --- | --- | --- |
| Factual review | Compare nodes, edges, conditions, direction, and labels with supplied facts or inspected source | Parser acceptance or visual quality |
| Parser validation | An actual Mermaid parser accepts the exact source; identify environment/version when known | Correct facts or readable layout |
| Visual inspection | Actually view rendered output in the target or a named environment; inspect labels, clipping, crossings, direction, contrast, and width | Compatibility with every host or correctness of source facts |

Human syntax review is useful but must be named as such. Command success without viewing the result is not visual inspection. Viewing one host's rendering proves nothing about an untested host. Do not claim examples in this Skill have been rendered simply because they are present in a reference.

If an existing renderer is available, needed, and authorized, use it with the current source and preserve its real result. Do not install tools or upload content as an implicit verification step. Renderer errors and timeouts remain failed checks; report the specific limit and return usable source if that satisfies the task.

Without a parser or renderer, deliver source with a concise statement such as “Checked against the supplied process; parser and visual validation were not run.” This is a verification limit, not a blanket block on creating or explaining Mermaid. If export itself is required, missing rendering capability blocks that export.

Check factual uncertainty separately: omit an unsupported edge, label a proposal explicitly, or ask for a material missing relationship. Never fill a factual gap just because a parser accepts it. For image input, distinguish visible labels from unreadable or inferred details. Redact sensitive source details before any approved external disclosure.

For file edits, reread the target and verify that only the requested region changed. For standalone source, check that the file contains raw Mermaid and no Markdown fence. Report only checks actually performed; `Unverified` must stay attached to the unsupported claim.
