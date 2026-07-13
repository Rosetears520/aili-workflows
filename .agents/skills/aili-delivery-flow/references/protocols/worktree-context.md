# WT-001 Worktree Context Protocol

Repository source path: `.agents/skills/aili-delivery-flow/references/protocols/worktree-context.md`. Installed runtime target: `$HOME/.agents/skills/aili-delivery-flow/references/protocols/worktree-context.md`.

`WT-001` is the single authority for cross-root target identity and parent-observed evidence. Task packets, results, implementation packages, and backend adapters reference one context by id; they must not copy, rebind, or independently reinterpret its roots, Git identity, approvals, permission boundaries, or evidence. A30 applies only to ROSE Task dispatch in the same OpenCode instance; direct user `@` invocation is outside its guarantees.

## Canonical context

```text
WT-001:
- context_id:
- evidence_version:
- freshness:
- source_session_root:
- target_repo_root:
- target_worktree_root:
- exact_session_root_approval:
  - approved_root:
  - approved_by:
  - approval_scope:
  - approval_status: approved | missing | stale | rejected
- identity_pre:
  - cwd:
  - canonical_root:
  - git_toplevel:
  - git_common_dir:
  - git_head:
  - git_branch:
  - detached_head: true | false | unknown
  - dirty_state:
  - worktree_membership:
- identity_post:
  - cwd:
  - canonical_root:
  - git_toplevel:
  - git_common_dir:
  - git_head:
  - git_branch:
  - detached_head: true | false | unknown
  - dirty_state:
  - worktree_membership:
- allowed_paths:
- forbidden_paths:
- artifact_paths:
- verification:
  - exact_command:
  - exact_cwd:
  - operation_approval: approved | missing | stale | rejected
- soft_boundary_disclosure:
- containment_status: ready | blocked | Unverified
- blocked_reasons:
- unverified:
```

All paths are canonical absolute paths for runtime comparison. An approval binds one exact canonical session root and one evidence version; parent directories, sibling/neighbor roots, symlink aliases, path prefixes, shell cwd, ambient workspace access, and prior-session approvals do not imply approval. `target_repo_root` and `target_worktree_root` must resolve to the same approved identity unless the context explicitly records and blocks the mismatch.

## Required pre/post evidence

Before any cross-root read, edit, command, artifact write, verification, or delegation, capture root, cwd, Git toplevel/common-dir/HEAD/branch, detached state, worktree membership, and dirty state. Repeat the same evidence after each write-capable operation and before accepting a result. Missing Git, detached HEAD, dirty state, changed cwd, symlink resolution change, worktree reassignment, target disappearance, or any pre/post identity mismatch is blocking until explicitly reconciled and re-approved.

For A30 read-only dispatch, ROSE captures exact canonical parent/session root, parent HEAD, parent dirty state, target root, target HEAD, target dirty state, and shared Git common-dir before dispatch and again after the child returns. Parent, target, and common-dir snapshots must be byte-for-byte equivalent for the observed fields. ROSE never auto-integrates, commits, merges, rebases, resets, cleans, repairs, prunes, removes a worktree, or rolls back a target after an A30 result.

Only redacted metadata commands may be pre-approved for identity capture: `git status --short --branch`, `git status --porcelain=v1`, `git branch --show-current`, `git rev-parse --show-toplevel`, `git rev-parse --git-common-dir`, `git rev-parse --verify HEAD`, `git symbolic-ref --short -q HEAD`, and `git worktree list --porcelain`. Content-emitting Git commands, shell search commands, command substitution, pipelines, redirects, metacharacters, and subprocess launchers are not metadata evidence.

## Permission intersection and deny precedence

Effective authority comes from the final runtime-merged child permission rules and their provenance. The conceptual intersection is:

`effective_allow = parent_allow ∩ base_role_allow ∩ task_allow − any_deny`

Any parent, base-role, task-overlay, runtime, external-directory, path, operation, or protocol deny wins. Missing, ambiguous, unsupported, stale, or conflicting permission evidence is a deny. `role_overlay` is evidence and narrowing text, never permission authority: it cannot turn `ask` or `deny` into `allow`, add a tool, clone ROSE permissions, expand external-directory access, or prove the final effective child rules.

Root approval and operation approval are separate. Approval of the exact session root does not approve a test/debug/verification command. Such an operation requires its exact command and exact cwd in this context plus a fresh operation approval. Any argument, cwd, environment, executable, subprocess, redirection, or metacharacter change invalidates that approval.

Delegation is non-transitive. Every non-ROSE subagent has `task: deny`. Only ROSE may dispatch a selected A30 role through its unchanged checked-in Task allowlist.

## Base-role cross-root rules

- Exactly the 15 A30-selected read-only roles may use `read`, `glob`, `grep`, and `list`; `external_directory` is their only ask permission. Their default/unknown permission and every mutation, shell, delegation, LSP, skill, web, plugin, MCP, custom, and browser tool are denied.
- `implementer`, test/debug/browser/E2E roles, and every nonselected role retain `external_directory: deny`. A30 grants no external edit, shell, test, debug, browser, E2E, or artifact-write authority.
- ROSE permission is not cloned into any subagent. ROSE may orchestrate only the roles named by its own checked-in task permission.

The selected roles use `external_directory: ask`; approval, stored `always`, or auto behavior can broaden private-data reads. This privacy exposure must be disclosed before use. The no-mutation and no-nesting claim depends only on the final effective denies for edit, Bash, Task, and all other mutation/delegation-capable tools—not on ask behavior. If final merged child rules, rule provenance, or override absence are unavailable, stale, incomplete, or contradictory, runtime status is `Unverified`, rollout remains disabled, and no safe/no-mutation claim is allowed.

## Soft boundary and fail-closed rule

OpenCode permissions are a soft execution boundary, not an OS sandbox. They may not contain child processes, symlink swaps, already-open descriptors, ambient credentials, plugins, MCP tools, or effects performed outside the permission-aware tool path. Every context must disclose this limitation. Do not claim sandboxing.

Cross-root work is blocked unless the exact A30 production probe exits `0` in real runtime mode against the canonical fixture and a deterministic localhost mock provider. It must use a fully temporary Git repository plus sibling worktree and temporary OpenCode home, exercise real ROSE Task dispatch when supported, and capture final merged child permissions and provenance. A controlled parser/unit stub can test internals but is never rollout-eligible. Missing provider, verified real executable, effective-rule/provenance evidence, or proof that overrides are absent returns exit `3`/`Unverified`; an observed unsafe rule or mutation returns exit `5`. Never manufacture exit `0`, use real user OpenCode state, use a real external worktree, or treat no observed mutation as proof when effective rules are unavailable.

## Reference-only use

Packets and results carry only:

```text
worktree_context_ref:
  protocol_path: .agents/skills/aili-delivery-flow/references/protocols/worktree-context.md
  context_id:
  evidence_version:
  freshness:
```

If a packet or result duplicates/rebinds WT-001 identity, approval, path, Git, dirty-state, command/cwd, or containment facts, the duplicate is non-authoritative and the operation is blocked for reconciliation.
