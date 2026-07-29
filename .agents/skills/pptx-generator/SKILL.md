---
name: pptx-generator
description: "Generate, edit, inspect, or verify editable PowerPoint/PPTX decks when a .pptx file is the deliverable; use for template-preserving edits and from-scratch slide production, but not for HTML/SVG mockups, PDF-only reports, or presentation advice that needs no PPTX artifact."
---

# PPTX Generator

## Contract

[FRAME] This skill treats a presentation as a communication artifact first and a collection of decorated slides second. The goal is a deck whose argument, information hierarchy, visual grammar, and editable PPTX implementation agree.

Use one of three branches:

| Branch | Trigger | Primary evidence |
|---|---|---|
| Inspect | Read, inventory, summarize, or diagnose an existing PPTX | Extracted content plus package/visual evidence appropriate to the claim |
| Template-preserving edit | Modify a supplied deck while retaining its slide size, masters, layouts, theme, and recurring visual language | Before/after structure and rendered-slide comparison |
| From scratch | Produce a new editable PPTX without a controlling template | Approved brief, slide plan, successful compile, and rendered QA |

Near misses:

- Return HTML/SVG design generation, PDF-only output, and document/spreadsheet artifacts to ROSE for the appropriate artifact owner.
- For outline coaching or slide critique with no PPTX artifact, provide bounded advice directly rather than manufacturing a file workflow.
- Do not silently convert a browser-rendered deck into a PPTX; editable-slide output is a distinct deliverable.

## Capability Boundary

- Required: `artifact.transform` for PPTX/package generation or editing.
- Optional: `repo.read` for local source decks and supporting content; `artifact.store` for the final user-visible file.
- If a required capability is missing, return `blocked` with the missing operation and do not claim a usable PPTX.
- If visual rendering or inspection is unavailable, return `Unverified` for layout, clipping, font substitution, and image-crop claims; text extraction alone is not visual QA.
- Installing a runtime or dependency, reading an external directory, fetching network assets, or writing outside the owning repository retains its separate ROSE approval gate.

## Common Workflow

### 1. Fix the delivery contract

Capture the audience, presentation setting, purpose, language, expected duration or slide count, source material, brand/template constraints, required output path, and whether the user wants native editability or only a visual result.

Completion criterion: the artifact type and any material content, template, or placement decision are explicit.

### 2. Choose the branch before touching slides

- Existing deck plus “keep the format/style” means template-preserving edit.
- Existing deck plus “analyze/review” means inspect unless modification is also explicit.
- No controlling deck means from scratch.

Completion criterion: one branch owns the work; do not mix template preservation with an unrequested clean rebuild.

### 3. Distill the sources and build the per-slide plan

For source-heavy decks, material content selection, or an explicit request to plan every page, follow [`references/content-planning.md`](references/content-planning.md) and write a task-scoped Markdown plan before slide production. Keep each slide entry to `Layout` followed by `Content` unless the user requests another contract; place any page takeaway inside `Content`.

Use [`references/human-design-playbook.md`](references/human-design-playbook.md) for the underlying synthesis methods, information relationships, and practical layout formulas.

Completion criterion: the source is reduced into a coherent deck spine, every planned slide has one primary point and a source-grounded content allocation, and any required Markdown plan is ready to drive implementation.

### 4. Establish the visual grammar

When a template exists, derive the grammar from the deck instead of imposing this skill's defaults. Otherwise choose a coherent style from [`references/design-system.md`](references/design-system.md).

Record the content area, title zone, alignment lines, type hierarchy, palette roles, shape language, image treatment, chart/table treatment, and recurring navigation/footer behavior.

Completion criterion: the deck has one reusable visual system, not independently styled pages.

### 5. Plan pages from information relationships

Assign each slide a base role and a content relationship. Use [`references/slide-types.md`](references/slide-types.md) for cover, navigation, divider, content, and closing roles, then select a parallel, comparison, process, timeline, hierarchy, matrix, cycle, data, table, or image-led layout.

Completion criterion: layout follows meaning; visual variety does not break deck-wide consistency.

### 6. Implement with the selected branch

- **Inspect:** extract text and package metadata; render slides when making visual claims.
- **Template-preserving edit:** follow [`references/editing.md`](references/editing.md).
- **From scratch:** use a supported PPTX runtime and the technical patterns in [`references/pptxgenjs.md`](references/pptxgenjs.md). A modular `slide-XX` plus compile entrypoint structure is recommended for multi-slide decks, but the owning repository controls artifact placement.

Keep source files, generated previews, and final artifacts task-scoped. Do not add a dependency or global package merely because an example command names one.

Completion criterion: all planned slides exist, all user content is mapped, and no placeholder survives.

### 7. Verify content, visuals, and package integrity

Follow [`references/pitfalls.md`](references/pitfalls.md). Run the smallest fresh checks that support the exact completion claim:

1. compile or repack without corruption;
2. extract and compare text/content order;
3. render and inspect every affected slide for clipping, overlap, contrast, alignment, spacing, crop, and font substitution;
4. inspect deck-wide consistency and the presentation's narrative flow;
5. recheck affected slides after each repair.

Completion criterion: fresh evidence supports the stated content, visual, and file-integrity claims; unsupported claims remain `Unverified`.

## Reference Map

| Need | Reference |
|---|---|
| Source distillation and a reusable per-slide Markdown content plan | [`content-planning.md`](references/content-planning.md) |
| Complete English translation of the curated learning notes, including natural-language descriptions of source visuals | [`human-design-playbook.md`](references/human-design-playbook.md) |
| Base slide roles and relationship-led layouts | [`slide-types.md`](references/slide-types.md) |
| Palette, typography, spacing, and shape recipes | [`design-system.md`](references/design-system.md) |
| Existing-template inventory and fidelity-preserving edits | [`editing.md`](references/editing.md) |
| Compile, content, visual, and package QA | [`pitfalls.md`](references/pitfalls.md) |
| PptxGenJS implementation patterns | [`pptxgenjs.md`](references/pptxgenjs.md) |

## Hard Boundaries

- Preserve the original file unless replacement was explicitly requested; write an edited copy by default.
- Do not rebuild a supplied template from scratch merely because generation is easier.
- Do not invent data, citations, logos, customer names, or source claims to fill a slide.
- Do not begin slide production before a required per-slide content plan exists and its material omissions, claims, or structure decisions are resolved.
- Do not hide PPTX corruption or layout defects by shipping only screenshots or a PDF.
- Do not force a page-number badge, palette, font, gradient, animation, or decorative motif when the brief or controlling template does not use it.
- Do not recurse, invoke another process skill, or delegate. Return any routing, research, capability, approval, or independent-work need to ROSE.

## Terminal Outcomes

- `complete`: the requested PPTX work is produced and claim-matched verification is current.
- `need-user`: one material audience, content, template, output, or fidelity decision is unresolved.
- `need-evidence`: required source content or visual/package evidence is unavailable.
- `material-delta`: implementation reveals a new dependency, public artifact contract, permission, or verification-strategy change.
- `blocked`: required transform capability or exact operation approval is missing, or the PPTX remains corrupt.
- `Unverified`: the file exists but one or more claimed visual behaviors could not be freshly inspected.
