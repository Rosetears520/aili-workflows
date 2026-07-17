# Tool Policies

## General

- Prefer read-before-edit and complete, appropriately scoped changes.
- Do not invoke network for this work package.
- Do not install packages or add dependencies for fixture validation.
- Do not edit secrets, memory DB/schema, lockfiles, or forbidden harness areas outside approved package scope.
- Prefer executable tool rules: "when user asks X, do Y; if Z, do not A, do B." Avoid abstract-only guidance unless it includes a self-check or concrete flow.

## AILI Tool Strategy Capsules

- When a filename looks obvious, still read the active file/source before editing; do not rely on the name alone.
- When the user says "continue," resolve one active authorized envelope and read only the current mode/dependency evidence needed for its next action; do not infer approval or blanket-reread all artifacts from the word alone.
- When a subagent returns evidence, reconcile the anchors and residual uncertainty; do not treat the recommendation as a final verdict.
- When reporting verification, use fresh command or inspection evidence; do not claim verified from old logs, compression summaries, or memory.
- When writing continuity artifacts, put progress/user feedback in `progress.txt`; put new spec drift/self-corrections in `drift-log.md`; do not use `drift-log.md` or legacy `implementation-notes.html` as chat history or a progress ledger.

## Git

- No commit, push, merge, rebase, or history rewrite in this package.
- Use scoped status/diff only for evidence if requested by the caller.

## Python Runner

- Standard library only.
- Static file/schema checks only.
- No model calls, benchmarks, package installs, external services, or multi-host probing.

## Cross-Root and Optional Tools

- Cross-root work is fail-closed against exact OpenCode `1.17.18` behavior. Root approval is a soft boundary, not sandboxing or process containment. If ask/always/`--auto`, Task-root inheritance, role intersection, symlink/TOCTOU, subprocess, bash-effect, secret, or neighboring-root behavior cannot be safely expressed and freshly proven, do not dispatch or mutate and retain the result as `Unverified`.
- CodeGraph is optional exact-current-root discovery only. Confirm one root, request per-root initialization approval, refuse batch initialization, fall back when stale/noisy/unavailable, and read every final file; CodeGraph is not lifecycle or completion proof.
- Graphify execution is a separate operation requiring explicit approval for the exact synthetic/project run. Missing executable provenance, current security/advisory evidence, enforceable network denial, sanitized isolated environment, argv safety, private output root, or write inventory blocks before process start. Never infer operation permission from lifecycle approval and never claim a run from contract-only checks.

## Completion Claims

- A claim of complete/fixed/verified requires fresh command evidence.
- If evidence is partial, mark the result `Unverified` or return a blocked/needs-review status.
