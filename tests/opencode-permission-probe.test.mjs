import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { cpSync, mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import test from "node:test";

const project = new URL("..", import.meta.url).pathname;
const probe = new URL("../scripts/opencode_permission_probe.mjs", import.meta.url).pathname;
const checker = new URL("../scripts/delegation_protocols_check.py", import.meta.url).pathname;
const fixture = new URL("../docs/harness/fixtures/cross-worktree-permission-fixtures.yaml", import.meta.url).pathname;
const roles = [
  "agent-evaluator", "ai-regression-scout", "code-reviewer", "code-scout", "convergence-reviewer",
  "doc-researcher", "opensource-sanitizer", "plan-auditor", "pr-test-analyzer", "security-auditor",
  "silent-failure-reviewer", "spec-miner", "test-coverage-reviewer", "web-performance-auditor", "web-researcher",
];
const cases = [
  "effective-merged-tool-inventory", "unexpected-tool-denied", "direct-invocation-excluded",
  "seeded-parent-edit-allow-blocks", "seeded-parent-bash-allow-blocks", "seeded-parent-task-allow-blocks",
  "external-always-read-broadens", "auto-read-privacy-caveat", "mutation-capable-effective-rule-blocks",
  "clean-external-read-positive", "clean-path-ask", "edit-denied", "bash-denied", "task-denied",
  "commit-denied", "merge-denied", "apply-denied", "parent-unchanged", "target-unchanged",
  "common-dir-unchanged", "no-real-user-state",
];
const reportFields = [
  "schema_version", "mode", "status", "roles", "fixture_identity", "effective_permissions", "cases",
  "parent_before", "parent_after", "target_before", "target_after", "common_dir_before", "common_dir_after",
  "clean_ask", "seeded_always", "override_observability", "blocked", "unverified", "errors", "cleanup",
];

function runProbe(args, env = process.env) {
  return spawnSync(process.execPath, [probe, ...args], { encoding: "utf8", timeout: 30_000, env });
}

test("permission probe rejects invalid A30 CLI values with exit 2", () => {
  for (const args of [[], ["--project"], ["--unknown"], ["--mode", "other"], ["--provider", "other"]]) {
    const result = runProbe(args);
    assert.equal(result.status, 2, result.stderr || result.stdout);
    assert.equal(result.stderr, "permission probe usage error\n");
    assert.equal(result.stdout, "");
  }
});

test("permission probe is fail-closed, exact, secret-free, and cleans temporary state", () => {
  const result = runProbe([
    "--project", project, "--opencode-version", "1.17.18", "--fixture", fixture,
    "--mode", "a30-same-instance-readonly", "--provider", "local-mock", "--json",
  ], { ...process.env, A30_FAKE_SECRET_DO_NOT_EMIT_7f3a: "ambient-secret" });
  assert.equal(result.status, 3, result.stderr || result.stdout);
  assert.doesNotMatch(result.stdout, /A30_FAKE_(?:SECRET|TOKEN)_DO_NOT_EMIT/);
  const report = JSON.parse(result.stdout);
  assert.deepEqual(Object.keys(report), reportFields);
  assert.equal(report.schema_version, "aili.opencode-permission-probe.a30.v1");
  assert.equal(report.mode, "a30-same-instance-readonly");
  assert.equal(report.status, "Unverified");
  assert.ok(report.blocked.some((entry) => ["opencode-executable", "effective-child-evidence"].includes(entry.case)));
  assert.deepEqual(report.roles, roles);
  assert.deepEqual(report.cases.map((entry) => entry.id), cases);
  assert.ok(report.cases.every((entry) => Object.keys(entry).join(",") === "id,status,evidence"));
  assert.ok(report.cases.every((entry) => ["pass", "blocked", "Unverified", "fail"].includes(entry.status)));
  assert.equal(report.override_observability.effective_child_rules, "unavailable");
  assert.ok(report.unverified.some((entry) => entry.case === "effective-child-rules"));
  assert.deepEqual(report.parent_after, report.parent_before);
  assert.deepEqual(report.target_after, report.target_before);
  assert.deepEqual(report.common_dir_after, report.common_dir_before);
  assert.equal(report.cleanup.owner, "scripts/opencode_permission_probe.mjs");
  assert.equal(report.cleanup.attempted, true);
  assert.equal(report.cleanup.status, "succeeded");
  assert.deepEqual(report.cleanup.retained_paths, []);
  assert.deepEqual(report.cleanup.errors, []);
});

test("legacy invocation remains compatible but cannot become rollout-eligible", () => {
  const result = runProbe(["--project", project, "--opencode-version", "1.17.18", "--fixture", fixture, "--json"]);
  assert.equal(result.status, 3, result.stderr || result.stdout);
  assert.equal(JSON.parse(result.stdout).status, "Unverified");
});

test("controlled parser and effective-rule units never manufacture runtime exit zero", async () => {
  const module = await import(probe);
  const parsed = module.parseFixtureText(readFileSync(fixture, "utf8"), "1.17.18");
  assert.deepEqual(parsed.cases.map((entry) => entry.id), cases);
  assert.throws(() => module.parseFixtureText(readFileSync(fixture, "utf8").replace("provider: local-mock", "provider: fake"), "1.17.18"));
  assert.deepEqual(module.evaluateEffectivePermissions(null), { status: "Unverified", reason: "final merged child rules/provenance unavailable" });
  const unsafe = {
    source_anchor: "stub", merged_keys: ["read", "edit"], allowed: ["read", "edit"], asked: [], denied: [],
    rule_provenance: "stub", unexpected_allowed_or_ask: ["edit"], mutation_capable_overrides: ["edit"],
  };
  assert.equal(module.evaluateEffectivePermissions(unsafe).status, "fail");
  assert.equal(module.parseRuntimeEvidence(JSON.stringify({}), "1.17.18"), null);
});

test("C-OPENCODE-A30-STATIC rejects every role omission, key omission, order change, and unexpected allow/ask", () => {
  const root = mkdtempSync(join(tmpdir(), "a30-static-mutations-"));
  mkdirSync(join(root, ".agents", "skills", "aili-delivery-flow", "references", "protocols"), { recursive: true });
  mkdirSync(join(root, ".agents", "skills", "parallel-subagent-dispatch"), { recursive: true });
  cpSync(join(project, "agents"), join(root, "agents"), { recursive: true });
  for (const relative of [
    "worktree-context.md", "subagent-task-packet.md", "subagent-result.md",
  ]) cpSync(join(project, ".agents", "skills", "aili-delivery-flow", "references", "protocols", relative), join(root, ".agents", "skills", "aili-delivery-flow", "references", "protocols", relative));
  cpSync(join(project, ".agents", "skills", "parallel-subagent-dispatch", "SKILL.md"), join(root, ".agents", "skills", "parallel-subagent-dispatch", "SKILL.md"));

  const python = String.raw`
import importlib.util, pathlib, sys
spec = importlib.util.spec_from_file_location("a30check", sys.argv[1])
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
m.ROOT = pathlib.Path(sys.argv[2])
assert not m.p6_permission_failures(), m.p6_permission_failures()
rose = m.ROOT / "agents/rose.md"
rose_original = rose.read_text()
rose.write_text(rose_original.replace("\n  external_directory: deny\n", "\n  external_directory: ask\n", 1))
assert m.p6_permission_failures(), "ROSE external_directory complement"
rose.write_text(rose_original)
for rel in m.A30_SELECTED_ROLE_FILES:
    p = m.ROOT / rel; original = p.read_text()
    p.write_text(original.replace("\n  external_directory: ask\n", "\n", 1))
    assert m.p6_permission_failures(), rel
    p.write_text(original)
sample = m.ROOT / m.A30_SELECTED_ROLE_FILES[0]
original = sample.read_text()
for key in m.A30_PERMISSION_KEY_ORDER:
    if key == "read":
        mutated = original.replace("\n  read:\n", "\n", 1)
    else:
        value = "ask" if key == "external_directory" else ("allow" if key in {"list", "glob", "grep"} else "deny")
        label = '"*"' if key == "*" else key
        mutated = original.replace(f"\n  {label}: {value}\n", "\n", 1)
    sample.write_text(mutated)
    assert m.p6_permission_failures(), key
    sample.write_text(original)
sample.write_text(original.replace("\n  list: allow\n  glob: allow\n", "\n  glob: allow\n  list: allow\n", 1))
assert m.p6_permission_failures(), "order"
sample.write_text(original.replace("\n  edit: deny\n", "\n  edit: allow\n", 1))
assert m.p6_permission_failures(), "unexpected allow"
sample.write_text(original.replace("\n  edit: deny\n", "\n  edit: ask\n", 1))
assert m.p6_permission_failures(), "unexpected ask"
`;
  const result = spawnSync("python", ["-c", python, checker, root], { encoding: "utf8" });
  rmSync(root, { recursive: true, force: true });
  assert.equal(result.status, 0, result.stderr || result.stdout);
});

test("fixture rejects case order and expected mutations", async () => {
  const { parseFixtureText } = await import(probe);
  const text = readFileSync(fixture, "utf8");
  assert.throws(() => parseFixtureText(text.replace("effective-merged-tool-inventory", "changed-case"), "1.17.18"));
  assert.throws(() => parseFixtureText(text.replace("selected_role_count: 15", "selected_role_count: 14"), "1.17.18"));
});
