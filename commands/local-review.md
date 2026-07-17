---
description: Run a report-first local review gate over local changes, refs, PRs, or OpenSpec change artifacts.
agent: rose
subtask: false
---

# /local-review

User input:
$ARGUMENTS

Invoke the local review gate workflow. If a dedicated `local-review-gate` skill is installed, route to that skill; otherwise apply this command contract as the local review gate authority until the skill exists.

Purpose:
- Review a selected local target as a standalone non-delivery audit, classify findings first, and report skipped or `Unverified` lanes without mutating remote state.
- A `/local-review` result is not lifecycle acceptance or SHIP, release, merge, archive, or closeout evidence.

Target modes:
- No args: review staged, unstaged, and untracked local changes.
- `--base <branch>`: review the current branch/worktree against the merge base with the named base branch.
- `--commit <sha>`: review the selected commit.
- `--pr <url|number>`: inspect PR metadata and diff only through the exact read-only GitHub CLI allowlist `gh pr view`, `gh pr diff`, and `gh pr list --head` when available; no other `gh` command is allowed in PR mode.
- `--change <id|path>`: review an OpenSpec change contract and evidence artifacts.
- `--focus <text>` or adversarial wording: constrain emphasis, such as security, tests, data loss, performance, or adversarial review.
- `--repair`: enter repair only after a categorized report exists and repair is explicitly authorized.

Required behavior:
- Resolve and report target scope, base/ref/commit/PR/change metadata, included untracked files, unavailable metadata, and skipped lanes before accepting findings.
- For `--change <id|path>`, read the conventional OpenSpec artifact paths directly (for example `openspec/changes/<change-id>/proposal.md`, `design.md`, `tasks.md`, `test-plan.md`, `context.md`, `progress.txt`, `review-report.md`, and `specs/**/spec.md`) instead of relying only on broad globs, because local OpenSpec artifacts may be git-ignored or absent from snapshot-style search indexes.
- Inspect full changed files and relevant tests/config/docs/callers when needed for high-confidence correctness, security, data-loss, compatibility, or test findings; otherwise mark the limitation `Unverified`.
- Review across five axes — correctness, readability, architecture, security, and performance — after reading applicable spec/task artifacts and tests first when present.
- Require Critical/Important findings to include evidence anchors, concrete failure mode, why existing guards do not catch it, and concrete fixes; zero findings is valid only with inspected scope, skipped checks, and confidence recorded.
- Use fail-closed orchestration for selected lanes: missing/status-less lane output, unavailable required context, or unverifiable high-risk findings cannot become a clean `PASS`.
- Require selected review/test lanes to return the canonical result/finding envelope from `aili-delivery-flow/references/protocols/subagent-result.md`.
- For A33 targets, resolve exactly one declared repository/cwd, one current WT-001 reference, applicable narrowing target rules, and an owning-repository report destination; record soft-boundary limitations, do not scan the host broadly, and never duplicate or rebind identity, keys, approvals, Git state, rules, or command/cwd.
- Produce a categorized report before repair. For OpenSpec targets, default to `openspec/changes/<change-id>/review-report.md`; for non-OpenSpec targets, ask once for a repository-local report path or obtain an explicit chat-only waiver with persistence marked `Unverified`.
- Classify each finding by severity, category, source lane, evidence anchor, affected file or artifact, required action, repair owner, status, and re-review requirement.
- Use verdicts: `BLOCKED`, `NEEDS_FIXES`, `NEEDS_REVIEW`, `PASS_WITH_UNVERIFIED`, `PASS`, `REPAIRING`, and `REREVIEW_REQUIRED`.
- Report skipped checks, unavailable tools, stale evidence, and remaining `Unverified` items explicitly.
- For large or harness-sensitive `/local-review --change <id|path>` targets, `NEEDS_FIXES` and `BLOCKED` block BUILD continuation; `PASS_WITH_UNVERIFIED` permits continuation only after the user accepts each named `Unverified` item.

Hard stops:
- Do not override, replace, or depend on OpenCode's built-in `/review` command.
- Do not replace `/ship` or claim release-readiness, merge-readiness, handoff-readiness, archive-readiness, or closeout readiness.
- Do not use this audit as lifecycle acceptance or as SHIP/release/merge/archive evidence.
- Do not push, create PRs, comment on GitHub, approve/request changes, merge, tag, publish, delete, reset, clean, or otherwise mutate remote state.
- Do not run `gh api`, `gh pr checkout`, `gh pr comment`, `gh pr review`, `gh pr merge`, `gh pr create`, `gh repo clone`, or any equivalent push, merge, comment, review, checkout, clone, or remote-mutating command in PR mode.
- Do not perform repair until after the categorized report exists and the user or current active contract explicitly authorizes repair.
- Do not store or print secrets, tokens, private keys, cookies, raw logs, full transcripts, full file dumps, or private data in reports; use redacted path:line/type evidence instead.
- Stop as `BLOCKED` when the target, base, report path, required permission, or evidence source is ambiguous and cannot be safely inferred.

Output contract:
- resolved target, scope, base/ref/commit/PR/change metadata, and report path or chat-only waiver;
- files/artifacts inspected in full and files/artifacts sampled or skipped;
- checks and review lanes run, skipped, or marked `Unverified`, with reasons;
- categorized findings with severity, evidence anchors, required actions, repairability, owner, status, and re-review requirement;
- verdict from the local-review vocabulary and the exact residual risks or `Unverified` items;
- if repair is authorized: repair packages, affected verification to rerun, and re-review status.
