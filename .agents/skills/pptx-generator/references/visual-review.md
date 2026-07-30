# Visual Review

[FRAME] Rendering creates inspection material; it is not a visual verdict.

## Required Record

[FRAME] A current `visual-review-final.json` contains a non-empty reviewer identity, exact final-PPTX hash, aggregate render hash, the exact ordered slide IDs, findings, and an overall disposition.

[FRAME] Inspect the contact sheet and every per-slide image for clipping, overlap, contrast, hierarchy, alignment, spacing, crop, chart/table readability, font substitution, and deck-wide consistency. Record each finding against a slide ID and resolve it at source before `pass`.

[FRAME] File existence, package validation, text extraction, DOM inspection, issue scans, or a render command succeeding cannot substitute for reading the images. A reviewer without image-reading capability records `Unverified`; delivery remains blocked when visual completion is required.

[FRAME] Any PPTX, render artifact, render manifest, slide-ID set, or source change invalidates the review hash chain and requires a fresh review.

[FRAME] `emit_visual_review_packet.py --review-scope style-proof` targets the proof paths; the default `final` scope targets delivery paths. Both packets start `unreviewed` and never auto-pass. A Style Proof may render a representative ordered subset selected by stable slide IDs; final delivery must cover the complete current outline.
