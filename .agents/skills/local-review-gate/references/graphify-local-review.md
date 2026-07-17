# Graphify Local-Review Adapter

This reference defines the only AILI Graphify path. It is an optional, explicit-operation local-review input, not an installation path, plugin, hook, scheduler, lifecycle gate, correctness oracle, or completion authority.

## Pinned baseline and fresh-evidence boundary

- Repository: `Graphify-Labs/graphify`
- Release: `v0.9.12`
- Commit: `35665a76ba26da0e1bfcab074fede19c94fc5c89`
- PyPI distribution: `graphifyy`
- Console executable: `graphify`
- Python: `>=3.10`
- License: MIT
- Approved artifact: `graphifyy-0.9.12-py3-none-any.whl`, SHA-256 `94f9d0d7ef68455a2055c7623fb9574c7a781afb1473d26c7936d1abfc14d62c`

Official evidence URLs, checked on 2026-07-11 for this adapter:

- pinned source and metadata: <https://github.com/Graphify-Labs/graphify/tree/35665a76ba26da0e1bfcab074fede19c94fc5c89> and <https://raw.githubusercontent.com/Graphify-Labs/graphify/35665a76ba26da0e1bfcab074fede19c94fc5c89/pyproject.toml>
- release: <https://github.com/Graphify-Labs/graphify/releases/tag/v0.9.12>
- package metadata: <https://pypi.org/pypi/graphifyy/0.9.12/json>
- license: <https://raw.githubusercontent.com/Graphify-Labs/graphify/35665a76ba26da0e1bfcab074fede19c94fc5c89/LICENSE>
- pinned security-policy record: <https://raw.githubusercontent.com/Graphify-Labs/graphify/35665a76ba26da0e1bfcab074fede19c94fc5c89/SECURITY.md>
- current security policy: <https://raw.githubusercontent.com/Graphify-Labs/graphify/main/SECURITY.md>
- repository advisories: <https://api.github.com/repos/Graphify-Labs/graphify/security-advisories>
- current security CI: <https://raw.githubusercontent.com/Graphify-Labs/graphify/main/.github/workflows/ci.yml>
- dependency advisories: <https://api.osv.dev/v1/query>

Pinned provenance and current execution eligibility are separate evidence sets. The commit, source metadata, license, approved wheel filename/digest, installed distribution identity, console entry point, and installed `RECORD` hashes establish pinned provenance. Fresh default-branch security-policy and CI files, repository advisories, and OSV queries establish current eligibility. A stale current source blocks today's execution without making the approved pin permanently unreachable after upstream evidence changes.

As fetched on 2026-07-11, the current security policy names only `0.1.x` as supported while this adapter pins `0.9.12`; the pinned-commit policy had named `0.3.x`. The current CI evidence is evaluated independently rather than inheriting the pinned commit's non-blocking Bandit/pip-audit state. These are support/CI evidence concerns, not proof of a vulnerability, and current missing support keeps optional execution `Unverified` until fresh official support and complete installed root/dependency advisory evidence resolve it. Empty repository-advisory output is not proof that the package or its dependencies are safe.

Every operation re-fetches current public evidence through `scripts/graphify_baseline_check.py --mode security-evidence`; this dated record is provenance, not a substitute for that preflight.

## Forbidden integration

Never run or recommend these commands in this workflow:

- `graphify install --platform opencode`
- `graphify opencode install`

They can mutate OpenCode/plugin state or `AGENTS.md`. Do not install, update, repair, register, hook, schedule, background-run, auto-run, or lifecycle-gate Graphify. Do not add a Graphify command, plugin, listener, daemon, cron entry, manifest registration, or generated adapter.

## Sole guarded launcher and modes

Only `scripts/graphify_baseline_check.py` may launch Graphify for this workflow. Call the launcher with an argv-preserving API; never interpolate target or output paths into a shell command.

- `contract`: validates the pinned contract, policy surfaces, fixture coverage, exact argv shapes, and fail-closed controls. It does not start Graphify.
- `security-evidence`: inspects current public official package/advisory/security/CI evidence plus local executable/distribution/dependency evidence. It does not start Graphify.
- `execute-synthetic`: optional synthetic-repository execution only after separate exact operation permission and all controls pass.
- `execute-project`: optional exact approved project/output execution only after separate exact operation permission and all controls pass.

Exit codes are `0` for the exact mode contract/result, `3` for blocked or `Unverified` evidence/control with no Graphify start, and `5` for an unsafe contract/effect mismatch. JSON output is versioned. A nonzero execution result must retain `process_started:false` when Graphify did not start; it must never be described as a run.

The current user's permission to implement or inspect this contract is not permission to invoke either execution mode. `--require-operation-permission` is valid only when the caller has separately obtained and recorded permission for that exact mode, target root, output root, and operation.

## Exact operation contract

After all preflight controls pass, the launcher appends these literal arrays after the sandbox delimiter and invokes the resulting argv with `subprocess.Popen(..., shell=False)` under enforceable network denial:

```text
[<verified-python-path>, "-I", "-m", "graphify", "extract", <repo>, "--code-only", "--no-cluster", "--out", <local-output-root>]
[<verified-python-path>, "-I", "-m", "graphify", "cluster-only", "--graph", <local-output-root>/graphify-out/graph.json, "--no-label", "--no-viz"]
```

No flag, order, graph path, or broader command may be substituted. Spaces, `$()`, semicolons, quotes, leading-dash path components, Unicode, and newlines remain one literal argv element. Unsupported flags or expected paths block; there is no direct or shell-form fallback.

Before Graphify starts, require all of the following:

1. canonical executable realpath mapped uniquely to a non-editable installed `graphifyy==0.9.12`, the exact console entry point, and the trusted approved PyPI wheel; only security-evidence mode downloads that exact wheel, verifies its approved SHA-256, parses its internal `RECORD`, and compares every wheel path/digest plus installed extras against the installed distribution. The generated console launcher is never executed: the sandbox invokes the verified checker interpreter with isolated module mode (`-I -m graphify`) only after that wheel binding succeeds. Editable, duplicate, substituted, extra-file, missing-file, missing-hash, or incomplete installs block without install/upgrade/repair;
2. current official repository advisory, security-policy and CI evidence plus marker-evaluated recursive installed dependency closure; query OSV for the `graphifyy` root and every active installed dependency;
3. enforceable denied networking around the exact extract and cluster processes—not a weaker canary alone—and isolated user, PID, IPC, UTS, and network namespaces with private proc and dev;
4. isolated private `HOME`, `XDG_CONFIG_HOME`, `XDG_CACHE_HOME`, `XDG_DATA_HOME`, `XDG_STATE_HOME`, `XDG_RUNTIME_DIR`, and `TMPDIR`/`TMP`/`TEMP`, with the process working directory set to the empty isolated home rather than the source root;
5. credential/token/cloud/Git/SSH variables removed, `GRAPHIFY_GOOGLE_WORKSPACE` absent, and `GRAPHIFY_QUERY_LOG_DISABLE=1`;
6. no integration, cloud, backend, URL, proxy, or workspace configuration;
7. a new empty task-owned output root created with mode `0700` under `umask 077`, with no symlink component, source overlap, overwrite, tracked path, or staged path;
8. pre/post inventory of every writable sandbox root: output, isolated HOME/all XDG roots/TMP, query/cache/log/config, and unexpected effects. The deny-by-default filesystem sandbox must make writes outside those roots impossible. It mounts only the verified executable, interpreter, Python stdlib excluding neighboring site-packages, active installed dependency package roots, resolved runtime libraries, the target read-only, and the named writable roots; it never read-binds `/` and fails closed when this minimal runtime cannot be constructed.
9. inherited POSIX limits for CPU time, address space, process count, file size, and open files, plus an active supervisor that bounds combined streaming stdout/stderr to 1 MiB and enforces cumulative writable-tree quotas of 512 MiB and 100,000 inodes throughout each child. The JSON report records those limits and measured usage. If supervision or any limit cannot be applied, execution blocks; there is no unrestricted fallback.

If any item cannot be proven, return `3` before Graphify starts and preserve `UV-003`. Unsafe mismatch returns `5`. Never bypass unavailable network denial, executable provenance, advisory evidence, output safety, resource limits, or inventory controls. The launcher records `launch_attempted:true` immediately before spawn. `process_started` means the direct Graphify child is known to have started; a timeout after spawn attempt records an unknown start state, never `false`. Bubblewrap discovery, namespace canaries, sandbox setup, or a failed child exec do not count. Every path after temporary-root creation uses one cleanup finalizer, and `temp_cleanup.removed` is populated only after the root is confirmed absent.

Contract mode derives its integration scan from tracked, untracked, and explicitly enumerated ignored registration roots. It scans `package.json`, the local-review skill, commands, agents, manifests, plugins, OpenCode config, workflows/CI, and root registration files with exact path-and-context occurrence allowlists. It rejects Graphify install/register/hook/scheduler/auto-run mutations on those surfaces and fails closed when a source-like registration file is unreadable, oversized, or enumeration is incomplete. Fixed policy markers alone are not evidence that no integration surface exists.

Outputs remain local and uncommitted. They may contain absolute paths. Do not add broad ignore patterns, overwrite/reuse/clean an old output, create an automatic report/task/issue/change/memory record, or publish output. Graphify findings are advisory leads only: reconcile them against final source, tests, docs, and the user's goal before disposition; unresolved claims stay `Unverified`.
