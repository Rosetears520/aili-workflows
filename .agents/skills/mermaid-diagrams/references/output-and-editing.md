# Output and local editing

## Conversation

Return a fenced `mermaid` block and a short ordinary-language summary. The summary should explain the main relationship even when the client cannot render the block. Do not ask for a file path, add anchors, save source, or export images for conversational output. An explanation-only request can be answered in prose without reproducing or modifying the diagram.

## Markdown

1. Read the target file and nearby heading, prose, and code blocks before editing. Identify the requested diagram by existing context or an existing anchor. No HTML anchor is required.
2. If several blocks fit, ask which one. If the intended insertion point is clear, insert only the requested Mermaid block there; preserve all other content.
3. Replace only the selected block for updates. Keep headings, prose, other diagrams, surrounding whitespace, and unrelated code unchanged. Do not reformat the document or add an unrequested summary paragraph to it; the reply can carry the summary.
4. Reread the edited region and inspect the change for accidental edits outside the block. Report the target and actual verification performed. If read or write permission is missing, stop the file operation and return the precise limitation; do not claim the document was updated.

For example, if a document has “Payment” and “Delivery” Mermaid blocks and the request changes the delivery cancellation branch, read both contexts to locate the target, then edit only “Delivery.” A formatting problem in “Payment” remains outside scope.

## Standalone source

Create `.mmd` or `.mermaid` only when standalone source is requested and placement is known. The file contains raw Mermaid source only: no Markdown fences, explanatory prose, or companion files. Put the summary and verification limits in the reply. Read an existing file before updating it and preserve portions outside the requested change. Confirm before overwriting unrelated content.

## Export

An explicit image/export request requires an available, authorized renderer and an agreed artifact location. Report a missing capability as `blocked` for export, and offer source where useful. Do not silently install a renderer, download dependencies, upload private source, or switch to ASCII art. A renderer error or timeout is evidence of an unsuccessful check; report it without claiming successful export or bypassing permission.
