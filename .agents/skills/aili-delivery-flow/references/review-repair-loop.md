# Review and Repair Loop

This loop triggers only on explicit review/repair intent or one concrete blocking finding in an affected completion/SHIP claim. Direct inspection is the default; entering BUILD or SHIP does not automatically activate specialist review.

1. Resolve the accepted scope, final diff, applicable task rows, one repository/cwd, owning artifact destination, and checks already run. For A33, require one current WT-001 reference, re-read target rules, disclose the soft boundary, and do not scan the host broadly.
2. ROSE inspects the diff/task coverage and runs the smallest check that proves each required claim.
3. Select at most one auxiliary review capability when the user requests it or a concrete gap cannot be covered directly; that capability may use at most two independent read-only contexts and must use the canonical result envelope.
4. Reconcile their evidence without voting; subagents never own the final verdict or duplicate/rebind WT identity, keys, approvals, Git state, rules, or command/cwd.
5. If one blocking issue is found, apply one targeted repair and rerun only the affected check. Report any remaining blocker instead of starting another cycle.
6. Keep uncovered requirements, skipped checks, stale evidence, and unsupported readiness claims `Open Question` or `Unverified`.

Run a spec coverage check for formal changes that maps requirements/tasks/test-plan items to implementation, verification, review, and security evidence without requiring automatic specialist lanes.

BUILD's completion inspection performs one minimal changed-scope direct check, may use one auxiliary capability for a concrete gap, permits at most one targeted repair/recheck, records `IMPLEMENTED_TARGETED_VERIFIED` or blocks, and stops before SHIP. SHIP requires fresh explicit intent and reuses evidence unless an affected event stales it. Unchanged transport preserves evidence; relevant hook, tree/content, config, dependency, toolchain, target, or changed-merge events stale only affected rows. CI failure reports and stops for user decision; it never auto-repairs, commits, or pushes.

Do not create an automatic code/test/security/coverage/convergence swarm, a full-suite requirement without claim need, or a fixed multi-cycle review loop.
