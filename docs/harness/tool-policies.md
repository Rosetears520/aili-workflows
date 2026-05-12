# Tool Policies

## General

- Prefer read-before-edit and smallest scoped change.
- Do not invoke network for this work package.
- Do not install packages or add dependencies for fixture validation.
- Do not edit secrets, memory DB/schema, lockfiles, or forbidden harness areas outside approved package scope.

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
