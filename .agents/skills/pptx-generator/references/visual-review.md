# Visual Review

[FRAME] Rendering creates inspection material; it is not a visual verdict.

## Required Record

[FRAME] A current `visual-review-final.json` contains a non-empty reviewer identity, exact final-PPTX hash, aggregate render hash, the exact ordered slide IDs, findings, an overall disposition, and one page record per slide. Each passing page is `inspected`, contains alignment/spacing/text-wrap/overflow/image-aspect/font-rendering/reference-fidelity checks, and records at least one concrete observation.

[FRAME] Inspect the contact sheet and every per-slide image for clipping, overlap, contrast, hierarchy, alignment, spacing, crop, chart/table readability, font substitution, and deck-wide consistency. Record each finding against a slide ID and resolve it at source before `pass`.

Within those existing per-page observations and findings, also check communication at the intended viewing scale:

- Is the main conclusion immediately distinguishable from labels and supporting evidence, with enough context for the agreed live-talk or standalone-reading use?
- Are the actual values, units, comparison bases, sources, and necessary conditions readable next to the claims they qualify, rather than visually lost or pushed off-screen?
- Does the layout express the planned relationship without implying unsupported sequence, time, or causality? Check comparison alignment and arrow meaning, not just geometry.
- If the slide is crowded, return to the capacity sequence in [`content-planning.md`](content-planning.md#6-organize-delete-and-layer); text that fits only by obscuring conditions or shrinking against the contract is not a repair.

Use the current record's observations/findings and source-repair loop, not a new score, schema, or approval gate. Text-plan review alone does not establish that these visual outcomes passed.

[FRAME] File existence, package validation, text extraction, DOM inspection, issue scans, or a render command succeeding cannot substitute for reading the images. A reviewer without image-reading capability records `Unverified`; delivery remains blocked when visual completion is required.

[FRAME] Any PPTX, render artifact, render manifest, slide-ID set, or source change invalidates the review hash chain and requires a fresh review.

[FRAME] `emit_visual_review_packet.py --review-scope style-proof` targets the proof paths; the default `final` scope targets delivery paths. Both packets start `unreviewed` and never auto-pass. A Style Proof may render a representative ordered subset selected by stable slide IDs; final delivery must cover the complete current outline.

[FRAME] For `template-edit`, the Style Proof binds baseline renders from the controlling template and current renders for the same ordered slide IDs, then covers image-or-chart, longest-text, and densest-numeric roles. A full build requires user confirmation of the current proof hash and role coverage; any bound template, baseline/current render, font environment, proof PPTX/review/preflight, or selected-slide change invalidates confirmation.
