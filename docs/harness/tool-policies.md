# Tool Policies

## General

- Prefer read-before-edit and smallest scoped change.
- Do not invoke network for this work package.
- Do not install packages or add dependencies for fixture validation.
- Do not edit secrets, memory DB/schema, lockfiles, or forbidden harness areas outside approved package scope.
- Prefer executable tool rules: "when user asks X, do Y; if Z, do not A, do B." Avoid abstract-only guidance unless it includes a self-check or concrete flow.

## AILI Tool Strategy Capsules

- When a filename looks obvious, still read the active file/source before editing; do not rely on the name alone.
- When the user says "continue," hydrate lifecycle state and confirm the approved/ready BUILD item before implementation; do not infer approval from the word alone.
- When a subagent returns evidence, reconcile the anchors and residual uncertainty; do not treat the recommendation as a final verdict.
- When reporting verification, use fresh command or inspection evidence; do not claim verified from old logs, DCP summaries, or memory.
- When writing continuity artifacts, put progress/user feedback in `progress.txt`; do not use `implementation-notes.html` as chat history or a progress ledger.

## Git

- No commit, push, merge, rebase, or history rewrite in this package.
- Use scoped status/diff only for evidence if requested by the caller.

## Python Runner

- Standard library only.
- Static file/schema checks only.
- No model calls, benchmarks, package installs, external services, or multi-host probing.

## Completion Claims

- A claim of complete/fixed/verified requires fresh command evidence.
- If evidence is partial, mark the result `Unverified` or return a blocked/needs-review status.
