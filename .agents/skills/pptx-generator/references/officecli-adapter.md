# OfficeCLI Adapter Boundary

[KNOWN|USER] `pptx-generator` remains the only presentation workflow owner; OfficeCLI is a non-routable external tool adapter whose managed installation is owned by the AILI installer. Source: accepted changes `pptx-workspace-officecli-integration` and `share-officecli-across-office-skills`.

[KNOWN|EXTERNAL] The tested package is exactly `@officecli/officecli@1.0.143`, with Apache-2.0 release/license metadata recorded by the installer-owned `manifests/officecli-tool.json`. Source: OfficeCLI tag `v1.0.143` and the accepted `share-officecli-across-office-skills` contract.

Do not call, install, register, load, or route to an upstream OfficeCLI Skill, including `officecli-pptx`. Do not use `officecli load_skill pptx`, `officecli skills install`, or OfficeCLI MCP as a substitute workflow.

## Stable role and decision table

| Situation | Stable OfficeCLI role | Mutation/evidence rule |
|---|---|---|
| Inspect an existing PPTX | Read-only outline, text, stats, issues, query/dump, validate, and render inspection | Default to read-only operations; findings are evidence, not a completion verdict. |
| Template-preserving edit | Structural inspection plus narrow deterministic DOM/batch edits | Preserve the original PPTX unchanged; store the edit plan/batch as replayable authoring source. |
| From-scratch deck | Validate, inspect issues/content, and render the primary renderer's PPTX | Do not make ordinary content/layout changes directly in the derived PPTX. |
| Rebuildable postbuild feature | Apply `patches/officecli-postbuild.batch.json` after every base build | The batch is source, order-preserving, and replayed from the current base before save and validate. |
| Standalone PPTX with no rebuildable source | One bounded patch to a working copy | Preserve the original, record the patch, and label the source/rebuildability limitation. |
| Raw XML fallback | Last resort only when supported DOM/batch operations cannot express the accepted change | Record exact part, selector/XPath, action, and re-run validation; never make raw XML the default edit path. |

## Syntax authority

[FRAME] The adapter has a version-scoped command table for the pinned binary and queries each family with `<command> --help`; it does not assume a `pptx` namespace. The installed help must agree with the table before mutation or evidence capture. If help or the required capability is unavailable, stop rather than guessing or adding a compatibility wrapper.

[FRAME] For pinned `1.0.143`, screenshot help is `officecli view --help`. A single page uses `officecli view <file> screenshot --page <page> --out <path>`; an all-page contact sheet uses `officecli view <file> screenshot --grid <columns> --screenshot-width <width> --screenshot-height <height> --out <path>`. There is no top-level `screenshot` command; `--slide`, `--output`, and `--contact-sheet` are not screenshot options. The render capability probe requires successful help containing `screenshot`, `--page`, `--out`, `--grid`, `--screenshot-width`, and `--screenshot-height`, not merely a successful generic view-help exit.

[FRAME] The default 1600×1200 viewport with `--grid auto` can crop a multi-page deck despite exit status 0. Contact geometry is read from the current PPTX's `ppt/presentation.xml` slide list and slide size, never from the outline or the Style Proof selection. Columns are `ceil(sqrt(page_count))`; rows are `ceil(page_count/columns)`. The thumbnail viewport stays at 1600px wide; row height uses the full column width and slide aspect ratio, plus 96px per row and 96px outer allowance for gutters/labels. Height is at least 1200px. Larger requested widths produced clipped output in the installed backend, so full-size individual slides remain separate artifacts rather than enlarging the contact sheet. Requests above 8192px on either axis or 32 million pixels fail closed, without truncating, silently downscaling, or substituting a partial deck. Missing/invalid geometry also blocks rendering; byte-placeholder PPTX fixtures are not dimension evidence. The internal packet records this full-deck geometry; the manifest retains its existing schema and records viewport arguments in the command evidence. Per-page argv is unchanged.

[UNVERIFIED] The conservative gutter/label allowance is a planning bound, not a measurement of OfficeCLI's browser layout. The host must render and inspect the real two-page and multi-page PNGs (including the final row/bottom edge) before accepting the crop fix. Unit geometry fixtures do not establish visual completeness. When needed for the approved smoke verification, prepend the existing `/home/rosetears/.cache/ms-playwright/chromium-1243/chrome-linux64` to PATH for that command only; do not install browsers or change global PATH.

[FRAME] Probes and all workspace commands set `OFFICECLI_SKIP_UPDATE=1`. Probes may run only `--version` and help/capability queries. Version drift from `1.0.143` requires command-capability revalidation; it never triggers an implicit update or downgrade.

[FRAME] This Skill has no OfficeCLI setup or npm execution path. If the managed binary is absent or drifted, stop and direct recovery to `rose-aili install` or `rose-aili update` without `--skip-officecli`; if OfficeCLI was intentionally skipped, keep the PPTX operation blocked until the installer-managed tool is restored. Do not use a full OfficeCLI installer, a bare auto-install, Skill/MCP setup, or PATH/shell integration. PPT probe/build/render continue to refuse a drifted version rather than guessing pinned syntax.

## Visual evidence boundary

[FRAME] `validate`, issues, outline, text, contact sheets, and per-slide PNGs are separate evidence inputs. `watch` is only a collaborative live preview and selection aid; it is not visual-review proof and is never a completion gate.

[FRAME] The issue report records executable/version, exact argv, current final-PPTX hash, issue count and entries; the render manifest binds its report hash. Every issue is blocking unless layout preflight records a slide/shape-specific non-blocking disposition with a reason and current render observation. Overflow, hidden text, unresolved placeholders, distortion, severe overlap, font substitution, and unknown issues cannot be waived.

[FRAME] Screenshots become visual-review evidence only after the current host actually opens and inspects the bound images for clipping, overlap, hierarchy, crop, contrast, typography, substitution, and deck rhythm. File existence, hashes, help output, or a successful render command cannot mark visual review passed.
