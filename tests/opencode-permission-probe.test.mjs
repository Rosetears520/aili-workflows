import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import test from "node:test";

const project = new URL("..", import.meta.url).pathname;
const probe = new URL("../scripts/opencode_permission_probe.mjs", import.meta.url).pathname;
const checker = new URL("../scripts/delegation_protocols_check.py", import.meta.url).pathname;
const fixture = new URL("../docs/harness/fixtures/cross-worktree-permission-fixtures.yaml", import.meta.url).pathname;
const fixtureText = readFileSync(fixture, "utf8");
const fixtureValue = JSON.parse(fixtureText);
const a33 = fixtureValue.a33;
const schema = "aili.a33-worktree-evidence.v1";

// Checker-owner compatibility markers retained for static_source_failures:
// A33 agent installs preserve whole-file equality in copy and selective modes
// a33-runtime-key-mismatch-zero-effect
// delete_each

function operation(kind = "add", index = 1, selector = "existing") {
  const create = selector !== "existing";
  return {
    operation_id: `${kind}-${index}`, kind, operation_class: "driver_fixture", source: `/tmp/run/source-${index}`,
    destination: `/tmp/run/host/.worktrees/foreign-${index}/${selector}`, repo_key: `foreign-${index}`,
    worktree_key: selector, branch: `fixture-${selector}`, base_ref: "HEAD",
    branch_mode: create ? "create" : "existing", reflog_policy: selector === "create-disabled" ? "disabled" : "enabled",
  };
}

function stateFor(operations = [operation()]) {
  return { run_id: "run", host: "/tmp/run/host", operations, used_approvals: [], consumed_approvals: {}, approval_snapshots: {}, registered: [] };
}

function approvalFor(op, overrides = {}) {
  return {
    approval_id: `approval-${op.operation_id}`, run_id: "run", operation_id: op.operation_id, kind: op.kind,
    operation_class: op.operation_class, source: op.source, destination: op.destination, repo_key: op.repo_key,
    worktree_key: op.worktree_key, branch: op.branch, base_ref: op.base_ref, branch_mode: op.branch_mode,
    reflog_policy: op.reflog_policy, expiry: "2999-01-01T00:00:00Z", decision_ref: "decision",
    trusted_code_risk: op.kind === "add" ? "accepted" : "not_applicable", status: "valid", ...overrides,
  };
}

function unchangedDelta() {
  return Object.fromEntries(a33.delta_fields.map((name) => [name, { before: null, after: null, change: "unchanged" }]));
}

function evidenceRecord(metadata, overrides = {}) {
  return {
    schema_version: "aili.a33-runtime-evidence.internal.v1", evidence_id: `collector:${metadata.id}`,
    scenario_id: metadata.id, family: metadata.family, source: "collector", operation_id: null,
    operation_kind: metadata.operation_kind, attachment_selector: metadata.attachment_selector,
    approval_variant: metadata.approval_variant, status: metadata.expected_outcome === "blocked" ? "blocked" : "pass",
    exit_code: metadata.expected_outcome === "blocked" ? 3 : 0, effect_started: metadata.expected_outcome === "blocked" ? false : null,
    before_state: null, after_state: null, expected_delta: null, observed_delta: null,
    evidence_types: [...metadata.required_evidence_types], evidence_refs: ["direct:evidence"], contradiction: false,
    semantic_observation: null, semantic_rejection: null, operation_bindings: [], attempt: null,
    cleanup_state: metadata.cleanup_expectation, ...overrides,
  };
}

function populatedIdentity(overrides = {}) {
  return {
    identity_state: "populated", declared_root: "/tmp/run/host/.worktrees/foreign-1/existing", path_state: "present",
    canonical_root: "/tmp/run/host/.worktrees/foreign-1/existing", git_toplevel: "/tmp/run/host/.worktrees/foreign-1/existing",
    git_private_dir: "/tmp/run/source-1/.git/worktrees/existing", git_common_dir: "/tmp/run/source-1/.git",
    git_head: "0123456789012345678901234567890123456789", git_branch: "fixture-existing", detached_head: false,
    worktree_membership: "linked", dirty_state: { tracked_modified: false, tracked_deleted: false, untracked_count: 0, ignored_count: 0 },
    tracked_files: ["fixture.txt"], untracked_files: [], ignored_files: [], artifact_files: [], unknown_files: [], ...overrides,
  };
}

function absentIdentity(overrides = {}) {
  return {
    identity_state: "absent", declared_root: "/tmp/run/host/.worktrees/foreign-1/existing", path_state: "absent",
    canonical_root: null, git_toplevel: null, git_private_dir: null, git_common_dir: null, git_head: null,
    git_branch: null, detached_head: null, worktree_membership: "absent", dirty_state: null,
    tracked_files: null, untracked_files: null, ignored_files: null, artifact_files: null, unknown_files: null,
    ...overrides,
  };
}

test("A33 internal registry is the exact ordered 70-case fixture registry and rejects every registry mutation class", async () => {
  const { A33_RUNTIME_SCENARIO_REGISTRY, parseA33FixtureText, validateA33ScenarioRegistry } = await import(probe);
  const config = parseA33FixtureText(fixtureText);
  assert.equal(A33_RUNTIME_SCENARIO_REGISTRY.length, 70);
  assert.deepEqual(A33_RUNTIME_SCENARIO_REGISTRY.map(({ id }) => id), config.runtime_mandatory_case_ids);
  assert.equal(validateA33ScenarioRegistry(A33_RUNTIME_SCENARIO_REGISTRY, config.runtime_mandatory_case_ids), true);
  const mutations = [];
  const swapped = structuredClone(A33_RUNTIME_SCENARIO_REGISTRY); [swapped[0], swapped[1]] = [swapped[1], swapped[0]]; mutations.push(swapped);
  mutations.push(structuredClone(A33_RUNTIME_SCENARIO_REGISTRY).slice(1));
  mutations.push([...structuredClone(A33_RUNTIME_SCENARIO_REGISTRY), structuredClone(A33_RUNTIME_SCENARIO_REGISTRY[0])]);
  const duplicate = structuredClone(A33_RUNTIME_SCENARIO_REGISTRY); duplicate[1].id = duplicate[0].id; mutations.push(duplicate);
  const metadata = structuredClone(A33_RUNTIME_SCENARIO_REGISTRY); metadata[0].family = "valid-add"; mutations.push(metadata);
  for (const mutation of mutations) assert.throws(() => validateA33ScenarioRegistry(mutation, config.runtime_mandatory_case_ids));
});

test("A33 approval taxonomy is exact, precedence-sensitive, and binds consumed ADD reuse to its authoritative record", async () => {
  const { buildA33OperationSnapshot, classifyA33Approval, seedA33ApprovalSnapshot } = await import(probe);
  const add = operation("add");
  const baseState = stateFor([add]);
  const valid = approvalFor(add);
  const omitted = { ...valid }; delete omitted.repo_key;
  const cases = [
    [omitted, {}, "schema_omission"],
    [approvalFor(add, { approval_id: null, expiry: null, decision_ref: null, trusted_code_risk: null, status: "missing" }), {}, "missing"],
    [approvalFor(add, { status: "declined" }), {}, "declined"],
    [approvalFor(add, { status: "unavailable" }), {}, "unavailable"],
    [approvalFor(add, { status: "expired" }), {}, "expired"],
    [approvalFor(add, { operation_id: "other" }), {}, "wrong_operation"],
    [approvalFor(add, { kind: "remove" }), {}, "wrong_operation"],
    [approvalFor(add, { source: "/wrong" }), {}, "wrong_source"],
    [approvalFor(add, { destination: "/wrong" }), {}, "wrong_destination"],
    [approvalFor(add, { branch: "wrong" }), {}, "wrong_branch"],
    [approvalFor(add, { base_ref: "wrong" }), {}, "wrong_base_ref"],
    [approvalFor(add, { repo_key: "wrong" }), {}, "repo_key_mismatch"],
    [approvalFor(add, { worktree_key: "wrong" }), {}, "worktree_key_mismatch"],
    [approvalFor(add, { operation_class: "real" }), {}, "real_for_fixture"],
    [approvalFor(add, { operation_class: "other" }), {}, "operation_class_mismatch"],
    [approvalFor(add, { status: "mismatched" }), {}, "mismatched"],
    [approvalFor(add, { trusted_code_risk: "declined" }), {}, "add_risk_declined"],
    [approvalFor(add, { trusted_code_risk: "unavailable" }), {}, "add_risk_unavailable"],
  ];
  for (const [approval, statePatch, category] of cases) {
    assert.equal(classifyA33Approval(approval, { ...baseState, ...statePatch }, add).category, category, category);
  }
  assert.equal(classifyA33Approval(approvalFor(add, { status: "declined", source: "/wrong" }), baseState, add).category, "wrong_source");
  const stale = approvalFor(add, { status: "stale", approval_id: "stale" });
  const staleSnapshot = buildA33OperationSnapshot(baseState, add, { destination_present: true, registered: false });
  const staleState = seedA33ApprovalSnapshot(baseState, stale, staleSnapshot);
  assert.equal(classifyA33Approval(stale, staleState, add).category, "stale_snapshot_mismatch");
  const currentSnapshot = buildA33OperationSnapshot(baseState, add, { destination_present: false, registered: false });
  assert.equal(classifyA33Approval(stale, seedA33ApprovalSnapshot(baseState, stale, currentSnapshot), add).category, "stale_unverified");

  const remove = { ...operation("remove"), source: add.source, destination: add.destination, repo_key: add.repo_key, worktree_key: add.worktree_key, branch: add.branch };
  assert.equal(classifyA33Approval(approvalFor(remove, { trusted_code_risk: "accepted" }), stateFor([remove]), remove).category, "remove_risk_invalid");
  const consumedState = stateFor([add, remove]);
  consumedState.used_approvals = [valid.approval_id];
  consumedState.consumed_approvals[valid.approval_id] = { approval: valid, snapshot: buildA33OperationSnapshot(consumedState, add, { destination_present: false, registered: false }) };
  const reuse = classifyA33Approval(valid, consumedState, remove);
  assert.deepEqual([reuse.category, reuse.variant], ["reused", "reused-add-for-remove"]);
  const forged = structuredClone(consumedState); forged.consumed_approvals[valid.approval_id].approval.decision_ref = "forged";
  assert.equal(classifyA33Approval(valid, forged, remove).category, "schema_omission");
  assert.equal(classifyA33Approval(valid, { ...baseState, used_approvals: [valid.approval_id] }, add).category, "schema_omission");
});

test("A33 NUL-record parsers preserve typed status and worktree flags and fail closed on malformed records", async () => {
  const { parseA33PorcelainV2, parseA33WorktreePorcelain } = await import(probe);
  const status = parseA33PorcelainV2([
    "1 .M N... 100644 100644 100644 a b modified.txt",
    "1 D. N... 100644 100644 000000 a b deleted.txt", "? untracked.txt", "! ignored.txt",
  ]);
  assert.deepEqual(status, { tracked_modified: ["modified.txt"], tracked_deleted: ["deleted.txt"], untracked: ["untracked.txt"], ignored: ["ignored.txt"] });
  const worktrees = parseA33WorktreePorcelain(["worktree /tmp/main", "HEAD abc", "worktree /tmp/linked", "locked reason", "prunable stale"]);
  assert.deepEqual(worktrees.map(({ path, locked, prunable }) => ({ path, locked, prunable })), [
    { path: "/tmp/main", locked: null, prunable: null }, { path: "/tmp/linked", locked: "reason", prunable: "stale" },
  ]);
  for (const malformed of [null, ["bad"], ["2 R. N... 100644 100644 100644 a b R100 new.txt"], [7]]) {
    assert.throws(() => parseA33PorcelainV2(malformed));
  }
  for (const malformed of [null, ["HEAD abc"], ["worktree "], [7]]) assert.throws(() => parseA33WorktreePorcelain(malformed));
});

test("A33 typed removal inventory keeps exact classes, rejects double credit, and narrows user-visible evidence", async () => {
  const { classifyA33RemovalInventory, validateA33Identity } = await import(probe);
  const identity = populatedIdentity({
    dirty_state: { tracked_modified: true, tracked_deleted: true, untracked_count: 1, ignored_count: 1 },
    untracked_files: ["u"], ignored_files: ["i"], artifact_files: ["a"], unknown_files: ["x"],
  });
  const result = classifyA33RemovalInventory({ identity, locked: true, expected_source: "/expected", observed_source: "/actual",
    expected_path: "/expected/path", expected_membership: "main", visible_files: [".git", "a", "fixture.txt", "i", "u", "user.txt", "x"],
    allowlisted_ephemeral_artifacts: [".git"] });
  assert.deepEqual(result.classes, ["tracked_modified", "tracked_deleted", "untracked", "ignored", "artifact", "unknown", "locked", "wrong_source", "wrong_path", "wrong_membership", "user_visible"]);
  assert.deepEqual(result.evidence_by_class.user_visible, ["user.txt"]);
  const duplicate = populatedIdentity({ untracked_files: ["fixture.txt"] });
  assert.equal(classifyA33RemovalInventory({ identity: duplicate }).contradiction, true);
  const absent = absentIdentity();
  assert.equal(validateA33Identity(absent), true);
  assert.deepEqual(classifyA33RemovalInventory({ identity: absent }).classes, ["missing"]);
  const malformedAbsent = { identity_state: "absent", path_state: "absent" };
  assert.equal(validateA33Identity(malformedAbsent), false);
  assert.deepEqual(classifyA33RemovalInventory({ identity: malformedAbsent }), {
    clean: false, classes: ["invalid"], primary_class: "invalid", evidence_by_class: {}, contradiction: true,
  });
  for (const malformed of [populatedIdentity({ tracked_files: "fixture.txt" }), populatedIdentity({ untracked_files: [7] })]) {
    assert.equal(validateA33Identity(malformed), false);
    assert.notEqual(classifyA33RemovalInventory({ identity: malformed }).clean, true);
  }
});

test("A33 evidence binding resolves authoritative attempts and requires exact all-attachment coverage", async () => {
  const { A33_RUNTIME_SCENARIO_REGISTRY, validateA33EvidenceBindings } = await import(probe);
  const metadata = A33_RUNTIME_SCENARIO_REGISTRY.find(({ id }) => id === "a33-runtime-each-attachment-add-separate-approval");
  const operations = [operation("add", 1, "existing"), operation("add", 2, "create-enabled"), operation("add", 3, "create-disabled")];
  const attempts = operations.map((op, index) => ({ evidence_id: `attempt:${index + 1}`, result: { operation: op } }));
  const bindings = attempts.map((attempt) => ({ attempt_id: attempt.evidence_id, operation_id: attempt.result.operation.operation_id,
    operation_kind: "add", attachment_selector: attempt.result.operation.worktree_key }));
  const record = { operation_id: null, operation_bindings: bindings };
  assert.equal(validateA33EvidenceBindings(metadata, record, operations, attempts).status, "pass");
  const mutations = [];
  const swapped = structuredClone(record); [swapped.operation_bindings[0].attempt_id, swapped.operation_bindings[1].attempt_id] = [swapped.operation_bindings[1].attempt_id, swapped.operation_bindings[0].attempt_id]; mutations.push(swapped);
  const missing = structuredClone(record); missing.operation_bindings.pop(); mutations.push(missing);
  const duplicate = structuredClone(record); duplicate.operation_bindings.push(structuredClone(duplicate.operation_bindings[0])); mutations.push(duplicate);
  const extra = structuredClone(record); extra.operation_bindings.push({ attempt_id: "attempt:extra", operation_id: "add-extra", operation_kind: "add", attachment_selector: "existing" }); mutations.push(extra);
  const cross = structuredClone(record); cross.operation_bindings[0].operation_kind = "remove"; mutations.push(cross);
  for (const mutation of mutations) assert.equal(validateA33EvidenceBindings(metadata, mutation, operations, attempts).exit_code, 5);
  const firstSuccess = structuredClone(record); firstSuccess.operation_bindings = firstSuccess.operation_bindings.map((binding) => ({ ...binding, attempt_id: "attempt:1" }));
  assert.equal(validateA33EvidenceBindings(metadata, firstSuccess, operations, attempts).exit_code, 5);
});

test("A33 semantic oracle partitions blocked, missing-positive, effect, binding, delta, ref, and reflog outcomes", async () => {
  const { A33_RUNTIME_SCENARIO_REGISTRY, classifyA33RuntimeEvidence } = await import(probe);
  const blocked = A33_RUNTIME_SCENARIO_REGISTRY.find(({ id }) => id === "a33-runtime-approval-missing-zero-effect");
  const unchanged = unchangedDelta();
  const op = operation("add", 1, "existing");
  const attempt = { evidence_id: "attempt:negative", result: { operation: op } };
  const binding = { attempt_id: attempt.evidence_id, operation_id: op.operation_id, operation_kind: op.kind, attachment_selector: "existing" };
  const negative = evidenceRecord(blocked, {
    source: "operation", operation_id: op.operation_id, status: "blocked", exit_code: 3, effect_started: false,
    expected_delta: unchanged, observed_delta: unchanged, operation_bindings: [binding],
  });
  assert.equal(classifyA33RuntimeEvidence(blocked, [negative], [op], [attempt]).status, "pass", "valid blocked evidence");
  assert.equal(classifyA33RuntimeEvidence(blocked, []).exit_code, 3);
  const mutations = [
    ["effect_started true", { ...negative, effect_started: true }],
    ["unresolved authoritative attempt binding", { ...negative, operation_bindings: [{ ...binding, attempt_id: "attempt:missing" }] }],
    ["changed observed delta", { ...negative, observed_delta: { ...unchanged, target_path: { before: null, after: "present", change: "created" } } }],
  ];
  for (const [name, mutation] of mutations) {
    const result = classifyA33RuntimeEvidence(blocked, [mutation], [op], [attempt]);
    assert.equal(result.exit_code, 5, `${name}: ${JSON.stringify(result)}`);
  }
  const violation = A33_RUNTIME_SCENARIO_REGISTRY.find(({ id }) => id === "a33-remove-branch-reflog-mutation-block");
  for (const kind of ["delta", "ref", "reflog"]) {
    const observed = structuredClone(unchanged); observed.branch_reflog = { before: null, after: "changed", change: "created" };
    const record = evidenceRecord(violation, { semantic_observation: { kind, expected: unchanged, observed }, semantic_rejection: { status: "fail", exit_code: 5 } });
    assert.equal(classifyA33RuntimeEvidence(violation, [record]).status, "pass");
  }
  const modified = structuredClone(unchanged); modified.config = { before: "a", after: "b", change: "unchanged" };
  assert.equal(classifyA33RuntimeEvidence(violation, [evidenceRecord(violation, { semantic_observation: { kind: "delta", expected: unchanged, observed: modified } })]).exit_code, 3);
});

test("A33 operation result public schema remains exact", async () => {
  const { validateA33OperationResult } = await import(probe);
  const op = operation();
  const result = { schema_version: schema, command: "runtime-add", status: "blocked", exit_code: 3, run_id: "run",
    operation: op, approval: approvalFor(op), effect_started: false, expected_delta: null, observed_delta: null,
    evidence_refs: ["approval:missing"], unverified: [] };
  assert.equal(validateA33OperationResult(result), true);
  for (const mutation of [{ ...result, extra: true }, { ...result, effect_started: null }, { ...result, evidence_refs: "x" }]) {
    assert.equal(validateA33OperationResult(mutation), false);
  }
});

test("schema-valid synthetic A33 runtime join without authentic sibling state fails closed", () => {
  const root = mkdtempSync(join(tmpdir(), "a33-nonworktree-join-"));
  const staticPath = join(root, "static.json");
  const runtimePath = join(root, "runtime.json");
  try {
    const staticRun = spawnSync("python", [checker, "--project", project, "--fixture", fixture, "--mode", "a33-static", "--ephemeral-result", staticPath, "--json"], { encoding: "utf8" });
    assert.equal(staticRun.status, 0, staticRun.stderr || staticRun.stdout);
    const runtimeCases = a33.runtime_mandatory_case_ids.map((id) => ({
      id, subset: "runtime", status: "Unverified", exit_code: 3, run_id: "synthetic-static-contract-only",
      operation_id: null, approval_ref: null, host_identity: null, source_identity: null, target_identity: null,
      expected_delta: null, observed_delta: null, evidence_refs: [`unavailable:${id}`], unverified: ["runtime not executed"], cleanup_state: null,
    }));
    const runtimeResult = { schema_version: schema, command: "a33-runtime-join", mode: "runtime", status: "Unverified", exit_code: 3,
      run_id: "synthetic-static-contract-only", mandatory_case_ids: a33.runtime_mandatory_case_ids,
      observed_case_ids: a33.runtime_mandatory_case_ids, case_set_equal: true, cases: runtimeCases, operations: [],
      cleanup: { eligible: false, attempted: false, status: "blocked", retained_paths: [root], errors: [] },
      summary: { mandatory: runtimeCases.length, passed: 0 }, unverified: ["runtime not executed"], ephemeral_result: runtimePath };
    writeFileSync(runtimePath, `${JSON.stringify(runtimeResult, null, 2)}\n`, "utf8");
    const joined = spawnSync("python", [checker, "--project", project, "--fixture", fixture, "--mode", "a33-join", "--static-result", staticPath, "--runtime-result", runtimePath, "--json"], { encoding: "utf8" });
    assert.equal(joined.status, 5, joined.stderr || joined.stdout);
    const report = JSON.parse(joined.stdout);
    assert.equal(report.status, "fail");
    assert.equal(report.exit_code, 5);
    assert.match(report.unverified.join(" "), /state|runtime/i);
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});
