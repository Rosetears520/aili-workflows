#!/usr/bin/env node

import { spawnSync } from "node:child_process";
import { createHash, randomBytes } from "node:crypto";
import { chmodSync, existsSync, lstatSync, mkdirSync, mkdtempSync, readFileSync, readdirSync, realpathSync, rmSync, statSync, writeFileSync } from "node:fs";
import { createServer } from "node:http";
import { tmpdir } from "node:os";
import { basename, dirname, isAbsolute, join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const SCHEMA_VERSION = "aili.opencode-permission-probe.a30.v1";
const FIXTURE_SCHEMA = "aili.cross-worktree-permission-fixtures.v3";
const A33_SCHEMA_VERSION = "aili.a33-worktree-evidence.v1";
const MODE = "a30-same-instance-readonly";
const PROVIDER = "local-mock";
const SECRET_MARKERS = ["A30_FAKE_SECRET_DO_NOT_EMIT_7f3a", "A30_FAKE_TOKEN_DO_NOT_EMIT"];
const ROLES = [
  "agent-evaluator", "ai-regression-scout", "code-reviewer", "code-scout", "convergence-reviewer",
  "doc-researcher", "opensource-sanitizer", "plan-auditor", "pr-test-analyzer", "security-auditor",
  "silent-failure-reviewer", "spec-miner", "test-coverage-reviewer", "web-performance-auditor", "web-researcher",
];
const CASE_IDS = [
  "effective-merged-tool-inventory", "unexpected-tool-denied", "direct-invocation-excluded",
  "seeded-parent-edit-allow-blocks", "seeded-parent-bash-allow-blocks", "seeded-parent-task-allow-blocks",
  "external-always-read-broadens", "auto-read-privacy-caveat", "mutation-capable-effective-rule-blocks",
  "clean-external-read-positive", "clean-path-ask", "edit-denied", "bash-denied", "task-denied",
  "commit-denied", "merge-denied", "apply-denied", "parent-unchanged", "target-unchanged",
  "common-dir-unchanged", "no-real-user-state",
];
const REPORT_FIELDS = [
  "schema_version", "mode", "status", "roles", "fixture_identity", "effective_permissions", "cases",
  "parent_before", "parent_after", "target_before", "target_after", "common_dir_before", "common_dir_after",
  "clean_ask", "seeded_always", "override_observability", "blocked", "unverified", "errors", "cleanup",
];
const SNAPSHOT_FIELDS = ["root", "head", "branch_or_detached", "dirty", "tree_digest", "git_admin_digest"];
const EFFECTIVE_FIELDS = [
  "source_anchor", "merged_keys", "allowed", "asked", "denied", "rule_provenance",
  "unexpected_allowed_or_ask", "mutation_capable_overrides",
];

function usageError() {
  process.stderr.write("permission probe usage error\n");
  process.exitCode = 2;
}

export function parseArguments(argv) {
  const options = { mode: MODE, provider: PROVIDER };
  const values = new Map([
    ["--project", "project"], ["--opencode-version", "opencodeVersion"],
    ["--opencode-executable", "opencodeExecutable"], ["--fixture", "fixture"],
    ["--mode", "mode"], ["--provider", "provider"],
  ]);
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === "--json") {
      if (options.json) throw new Error("usage");
      options.json = true;
      continue;
    }
    const key = values.get(arg);
    if (!key || Object.hasOwn(options, key) && !["mode", "provider"].includes(key)) throw new Error("usage");
    if ((key === "mode" && options.mode !== MODE) || (key === "provider" && options.provider !== PROVIDER)) throw new Error("usage");
    const value = argv[++index];
    if (!value || value.startsWith("--")) throw new Error("usage");
    options[key] = value;
  }
  if (!options.project || !options.opencodeVersion || !options.fixture || !options.json) throw new Error("usage");
  if (options.mode !== MODE || options.provider !== PROVIDER) throw new Error("usage");
  if (!/^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$/.test(options.opencodeVersion)) throw new Error("usage");
  return options;
}

function scalar(text, name) {
  return text.match(new RegExp(`^${name}:\\s*["']?([^"'\\n]+)["']?\\s*$`, "m"))?.[1]?.trim();
}

export function parseFixtureText(text, requestedVersion) {
  const fixture = JSON.parse(text);
  const historical = fixture.historical_a30;
  const exits = fixture.exit_codes;
  const fields = historical?.required_report_fields;
  const cases = historical?.case_ids?.map((id) => ({ id, expected: "historical-non-gating" })) ?? [];
  const exitsValid = exits?.safe_observed === 0 && exits?.usage_or_fixture_error === 2
    && exits?.blocked_or_unverified === 3 && exits?.unsafe === 5;
  if (fixture.schema !== FIXTURE_SCHEMA || historical?.mode !== MODE
    || historical?.provider !== PROVIDER || historical?.runtime_mode !== "real"
    || historical?.expected_opencode_version !== requestedVersion
    || historical?.selected_role_count !== 15
    || JSON.stringify(fields) !== JSON.stringify(REPORT_FIELDS)
    || JSON.stringify(historical?.case_ids) !== JSON.stringify(CASE_IDS) || !exitsValid) {
    throw new Error("fixture");
  }
  return { cases, fields };
}

function isWithin(candidate, parent) {
  const path = relative(parent, candidate);
  return path === "" || (!path.startsWith("..") && !isAbsolute(path));
}

function loadFixture(path, project, version) {
  const candidate = isAbsolute(path) ? path : resolve(project, path);
  const canonical = realpathSync(candidate);
  const expected = realpathSync(join(project, "docs", "harness", "fixtures", "cross-worktree-permission-fixtures.yaml"));
  if (canonical !== expected || !isWithin(canonical, project) || !statSync(canonical).isFile()) throw new Error("fixture");
  const text = readFileSync(canonical, "utf8");
  return { ...parseFixtureText(text, version), canonical, sha256: createHash("sha256").update(text).digest("hex") };
}

function run(command, args, { cwd, env, input, preserveOutput = false, timeout = 10_000 } = {}) {
  const result = spawnSync(command, args, { cwd, env, input, encoding: "utf8", timeout, maxBuffer: 1024 * 1024 });
  const stdout = String(result.stdout ?? "");
  const stderr = String(result.stderr ?? "");
  return { status: result.status ?? 127, stdout: preserveOutput ? stdout : stdout.trim(), stderr: preserveOutput ? stderr : stderr.trim() };
}

function git(command, args, cwd, env) {
  const result = run(command, args, { cwd, env });
  if (result.status !== 0) throw new Error("git fixture command failed");
  return result.stdout;
}

function digestDirectory(path) {
  const result = spawnSync("git", ["-C", path, "ls-files", "-s"], { encoding: "utf8", timeout: 5_000 });
  return createHash("sha256").update(String(result.stdout ?? "")).digest("hex");
}

function gitAdminDigest(commonDir) {
  const values = [];
  for (const name of ["HEAD", "packed-refs", "config"]) {
    const path = join(commonDir, name);
    values.push(name, existsSync(path) ? readFileSync(path) : Buffer.alloc(0));
  }
  return createHash("sha256").update(Buffer.concat(values.map((value) => Buffer.isBuffer(value) ? value : Buffer.from(value)))).digest("hex");
}

function snapshot(root, gitCommand, env) {
  const commonRaw = git(gitCommand, ["rev-parse", "--git-common-dir"], root, env);
  const commonDir = realpathSync(resolve(root, commonRaw));
  const branch = run(gitCommand, ["branch", "--show-current"], { cwd: root, env }).stdout;
  return {
    root: realpathSync(root),
    head: git(gitCommand, ["rev-parse", "--verify", "HEAD"], root, env),
    branch_or_detached: branch || "detached",
    dirty: git(gitCommand, ["status", "--porcelain=v1"], root, env),
    tree_digest: digestDirectory(root),
    git_admin_digest: gitAdminDigest(commonDir),
  };
}

function commonSnapshot(commonDir) {
  return { root: realpathSync(commonDir), head: null, branch_or_detached: null, dirty: "", tree_digest: null, git_admin_digest: gitAdminDigest(commonDir) };
}

function exactKeys(object, keys) {
  return object && JSON.stringify(Object.keys(object)) === JSON.stringify(keys);
}

export function parseRuntimeEvidence(stdout, expectedVersion) {
  try {
    const value = JSON.parse(stdout);
    if (!exactKeys(value, ["opencode_version", "dispatch", "effective_permissions", "override_observability"])) return null;
    if (value.opencode_version !== expectedVersion || value.dispatch !== "rose-task") return null;
    if (!exactKeys(value.effective_permissions, EFFECTIVE_FIELDS)) return null;
    if (value.override_observability?.effective_child_rules !== "observed") return null;
    return value;
  } catch {
    return null;
  }
}

export function evaluateEffectivePermissions(effective) {
  if (!effective || !exactKeys(effective, EFFECTIVE_FIELDS)) return { status: "Unverified", reason: "final merged child rules/provenance unavailable" };
  if (!effective.source_anchor || !effective.rule_provenance) return { status: "Unverified", reason: "final merged child rules/provenance unavailable" };
  const exact = JSON.stringify(effective.allowed) === JSON.stringify(["read", "list", "glob", "grep"])
    && JSON.stringify(effective.asked) === JSON.stringify(["external_directory"])
    && Array.isArray(effective.merged_keys) && Array.isArray(effective.denied)
    && effective.merged_keys.every((key) => effective.allowed.includes(key) || effective.asked.includes(key) || effective.denied.includes(key))
    && effective.unexpected_allowed_or_ask.length === 0 && effective.mutation_capable_overrides.length === 0
    && effective.source_anchor && effective.rule_provenance;
  return exact ? { status: "pass" } : { status: "fail", reason: "effective permission inventory is unsafe or incomplete" };
}

function findExecutable(options) {
  const candidates = options.opencodeExecutable ? [options.opencodeExecutable] : (process.env.PATH ?? "").split(":").map((dir) => join(dir, "opencode"));
  for (const candidate of candidates) {
    try {
      const canonical = realpathSync(candidate);
      if (statSync(canonical).isFile()) return canonical;
    } catch {
      // Continue report-only discovery.
    }
  }
  return null;
}

function verifyExecutable(candidate, expectedVersion) {
  if (!candidate) return null;
  let current = dirname(candidate);
  while (dirname(current) !== current) {
    const manifestPath = join(current, "package.json");
    if (existsSync(manifestPath)) {
      try {
        const manifest = JSON.parse(readFileSync(manifestPath, "utf8"));
        const declared = typeof manifest.bin === "string" ? manifest.bin : manifest.bin?.opencode;
        if (manifest.name === "opencode-ai" && manifest.version === expectedVersion && typeof declared === "string"
          && realpathSync(join(current, declared)) === candidate) return candidate;
      } catch {
        return null;
      }
    }
    current = dirname(current);
  }
  return null;
}

async function startMockProvider() {
  const server = createServer((request, response) => {
    request.resume();
    response.writeHead(501, { "content-type": "application/json" });
    response.end(JSON.stringify({ error: { message: "A30 deterministic mock requires explicit probe protocol support" } }));
  });
  await new Promise((resolvePromise, reject) => {
    server.once("error", reject);
    server.listen(0, "127.0.0.1", resolvePromise);
  });
  const address = server.address();
  return { server, endpoint: `http://127.0.0.1:${address.port}` };
}

function redact(serialized) {
  return SECRET_MARKERS.reduce((text, marker) => text.replaceAll(marker, "<redacted>"), serialized);
}

async function execute(options, fixture, project) {
  const root = mkdtempSync(join(tmpdir(), "aili-a30-permission-probe-"));
  const cleanup = { owner: "scripts/opencode_permission_probe.mjs", attempted: false, status: "not_applicable", retained_paths: [], errors: [] };
  const blocked = [];
  const unverified = [];
  const errors = [];
  let unsafe = false;
  let mock = null;
  let parentBefore = null;
  let parentAfter = null;
  let targetBefore = null;
  let targetAfter = null;
  let commonBefore = null;
  let commonAfter = null;
  let effective = {
    source_anchor: null, merged_keys: [], allowed: [], asked: [], denied: [], rule_provenance: null,
    unexpected_allowed_or_ask: [], mutation_capable_overrides: [],
  };
  const override = { auto: "unavailable", yolo: "unavailable", skip_permission: "unavailable", global_tool_override: "unavailable", effective_child_rules: "unavailable" };
  const cases = CASE_IDS.map((id) => ({ id, status: "Unverified", evidence: "provider-backed ROSE Task evidence unavailable" }));
  const setCase = (id, status, evidence) => Object.assign(cases.find((entry) => entry.id === id), { status, evidence });

  try {
    const home = join(root, "home");
    const parent = join(root, "parent");
    const target = join(root, "target");
    mkdirSync(home, { recursive: true });
    mkdirSync(parent);
    const gitCommand = "git";
    const env = {
      HOME: home, XDG_CONFIG_HOME: join(home, ".config"), XDG_DATA_HOME: join(home, ".local", "share"),
      XDG_CACHE_HOME: join(home, ".cache"), TMPDIR: join(root, "tmp"), PATH: process.env.PATH ?? "/usr/bin:/bin",
      LANG: "C.UTF-8", LC_ALL: "C.UTF-8", GIT_CONFIG_NOSYSTEM: "1", GIT_AUTHOR_NAME: "A30 Probe",
      GIT_AUTHOR_EMAIL: "probe@example.invalid", GIT_COMMITTER_NAME: "A30 Probe", GIT_COMMITTER_EMAIL: "probe@example.invalid",
      A30_FAKE_SECRET_DO_NOT_EMIT_7f3a: "A30_FAKE_TOKEN_DO_NOT_EMIT",
    };
    for (const path of [env.XDG_CONFIG_HOME, env.XDG_DATA_HOME, env.XDG_CACHE_HOME, env.TMPDIR]) mkdirSync(path, { recursive: true });
    const seedRoot = join(home, "a30-seeded-parent-states");
    mkdirSync(seedRoot, { recursive: true });
    for (const state of ["edit", "bash", "task", "external_directory"]) {
      writeFileSync(join(seedRoot, `${state}.json`), JSON.stringify({ permission: { [state]: "allow" }, isolated: true }), "utf8");
    }
    git(gitCommand, ["init", "--quiet"], parent, env);
    writeFileSync(join(parent, "approved.txt"), "approved non-secret fixture\n", "utf8");
    git(gitCommand, ["add", "approved.txt"], parent, env);
    git(gitCommand, ["commit", "--quiet", "-m", "A30 fixture"], parent, env);
    git(gitCommand, ["worktree", "add", "--quiet", "-b", "a30-target", target, "HEAD"], parent, env);
    const commonRaw = git(gitCommand, ["rev-parse", "--git-common-dir"], parent, env);
    const commonDir = realpathSync(resolve(parent, commonRaw));
    parentBefore = snapshot(parent, gitCommand, env);
    targetBefore = snapshot(target, gitCommand, env);
    commonBefore = commonSnapshot(commonDir);
    mock = await startMockProvider();

    const executable = verifyExecutable(findExecutable(options), options.opencodeVersion);
    if (!executable) {
      blocked.push({ case: "opencode-executable", reason: "verified real OpenCode executable unavailable" });
    } else {
      const version = run(executable, ["--version"], { cwd: parent, env }).stdout;
      if (version !== options.opencodeVersion) blocked.push({ case: "opencode-version", reason: "verified requested OpenCode version unavailable" });
      else {
        blocked.push({ case: "effective-child-evidence", reason: "OpenCode does not expose a verified A30 final-rule/provenance Task probe interface" });
      }
    }

    setCase("direct-invocation-excluded", "pass", "probe route accepts ROSE Task dispatch only; direct @ is not invoked");
    setCase("auto-read-privacy-caveat", "pass", "no auto/yolo/skip flag used; unavailable override evidence keeps rollout disabled");
    setCase("external-always-read-broadens", "pass", "fixture discloses that always may broaden reads but cannot prove mutation denial without effective rules");
    setCase("no-real-user-state", "pass", `isolated temporary HOME and localhost provider ${mock.endpoint.replace(/:\d+$/, ":<port>")}`);

    parentAfter = snapshot(parent, gitCommand, env);
    targetAfter = snapshot(target, gitCommand, env);
    commonAfter = commonSnapshot(commonDir);
    for (const [id, before, after] of [
      ["parent-unchanged", parentBefore, parentAfter], ["target-unchanged", targetBefore, targetAfter],
      ["common-dir-unchanged", commonBefore, commonAfter],
    ]) {
      const equal = JSON.stringify(before) === JSON.stringify(after);
      setCase(id, equal ? "pass" : "fail", equal ? "temporary fixture snapshot equal" : "temporary fixture snapshot changed");
      if (!equal) unsafe = true;
    }
    unverified.push({ case: "effective-child-rules", reason: "final merged child rules and provenance were not exposed" });
    unverified.push({ case: "override-absence", reason: "auto/yolo/skip/global override absence was not provable" });
  } catch (error) {
    errors.push(String(error?.message ?? error));
    unverified.push({ case: "fixture-runtime", reason: "temporary A30 fixture could not complete" });
  } finally {
    if (mock) await new Promise((resolvePromise) => mock.server.close(resolvePromise));
    cleanup.attempted = true;
    try {
      rmSync(root, { recursive: true, force: true });
      cleanup.status = existsSync(root) ? "failed" : "succeeded";
      if (cleanup.status === "failed") cleanup.retained_paths.push(basename(root));
    } catch (error) {
      cleanup.status = "failed";
      cleanup.retained_paths.push(basename(root));
      cleanup.errors.push(String(error?.message ?? error));
    }
  }

  if (cleanup.status === "failed") unsafe = true;
  const effectiveResult = evaluateEffectivePermissions(effective);
  if (effectiveResult.status === "fail") unsafe = true;
  const status = unsafe ? "fail" : "Unverified";
  const report = {
    schema_version: SCHEMA_VERSION,
    mode: MODE,
    status,
    roles: ROLES,
    fixture_identity: { canonical_realpath: fixture.canonical, sha256: fixture.sha256, expected_opencode_version: options.opencodeVersion, provider: PROVIDER },
    effective_permissions: effective,
    cases,
    parent_before: parentBefore,
    parent_after: parentAfter,
    target_before: targetBefore,
    target_after: targetAfter,
    common_dir_before: commonBefore,
    common_dir_after: commonAfter,
    clean_ask: { requested_path: null, decision: "Unverified", scope: "exact external path only" },
    seeded_always: { seeded: true, read_broadened: true, mutation_authorized: "Unverified", delegation_authorized: "Unverified", data_exposure_disclosed: true },
    override_observability: override,
    blocked,
    unverified,
    errors: errors.map((value) => String(value).replace(/[\r\n\t]+/g, " ").slice(0, 200)),
    cleanup,
  };
  process.stdout.write(`${redact(JSON.stringify(report, null, 2))}\n`);
  process.exitCode = unsafe ? 5 : 3;
}

const A33_MODES = new Set(["a33-runtime-prepare", "a33-runtime-add", "a33-runtime-remove", "a33-runtime-join"]);
const A33_IDENTITY_FIELDS = [
  "identity_state", "declared_root", "path_state", "canonical_root", "git_toplevel", "git_private_dir",
  "git_common_dir", "git_head", "git_branch", "detached_head", "worktree_membership", "dirty_state",
  "tracked_files", "untracked_files", "ignored_files", "artifact_files", "unknown_files",
];
const A33_DIRTY_FIELDS = ["tracked_modified", "tracked_deleted", "untracked_count", "ignored_count"];
const A33_DELTA_FIELDS = [
  "target_path", "worktree_membership", "common_dir_identity", "common_dir_admin_entry", "branch_ref",
  "branch_reflog", "unrelated_common_dir_entries", "unrelated_refs", "config", "hooks",
  "unrelated_worktree_records", "unrelated_prunable_entries", "other_files",
];
const A33_OPERATION_FIELDS = [
  "operation_id", "kind", "operation_class", "source", "destination", "repo_key", "worktree_key",
  "branch", "base_ref", "branch_mode", "reflog_policy",
];
const A33_PENDING_FIELDS = [...A33_OPERATION_FIELDS, "approval_required"];
const A33_APPROVAL_FIELDS = [
  "approval_id", "run_id", "operation_id", "kind", "operation_class", "source", "destination", "repo_key",
  "worktree_key", "branch", "base_ref", "branch_mode", "reflog_policy", "expiry", "decision_ref",
  "trusted_code_risk", "status",
];
const A33_OPERATION_RESULT_FIELDS = [
  "schema_version", "command", "status", "exit_code", "run_id", "operation", "approval", "effect_started",
  "expected_delta", "observed_delta", "evidence_refs", "unverified",
];
const A33_RUNTIME_CASE_FIELDS = [
  "id", "subset", "status", "exit_code", "run_id", "operation_id", "approval_ref", "host_identity",
  "source_identity", "target_identity", "expected_delta", "observed_delta", "evidence_refs", "unverified",
  "cleanup_state",
];
const KEY_PATTERN = /^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$/;
const RESERVED_KEYS = new Set([".", "..", ".git", ".worktrees", "worktrees"]);
const A33_INTERNAL_EVIDENCE_VERSION = "aili.a33-runtime-evidence.internal.v1";
const A33_MANAGED_AGENT_PATHS = Object.freeze([
  "agents/rose.md", "agents/agent-evaluator.md", "agents/ai-regression-scout.md", "agents/browser-qa-runner.md",
  "agents/code-reviewer.md", "agents/code-scout.md", "agents/convergence-reviewer.md", "agents/doc-researcher.md",
  "agents/e2e-artifact-runner.md", "agents/implementer.md", "agents/opensource-sanitizer.md", "agents/plan-auditor.md",
  "agents/pr-test-analyzer.md", "agents/security-auditor.md", "agents/silent-failure-reviewer.md", "agents/spec-miner.md",
  "agents/test-coverage-reviewer.md", "agents/test-engineer.md", "agents/web-performance-auditor.md", "agents/web-researcher.md",
]);
const A33_INSTALL_ENV_CONTROLS = Object.freeze({ OPENCODE_ALLOW_CUSTOM_HOME: "yes", AILI_ALLOW_CROSS_ENV: "yes" });
const A33_MARKER_FIELDS = ["schema_version", "run_root", "run_id", "cleanup_nonce"];
const A33_SNAPSHOT_PRECONDITION_FIELDS = ["destination_present", "registered"];
const A33_OPERATION_SNAPSHOT_FIELDS = ["schema_version", "run_id", ...A33_OPERATION_FIELDS, "preconditions"];
const A33_APPROVAL_SNAPSHOT_FIELDS = ["approval_binding", "operation_snapshot"];
const A33_RAW_INVENTORY_FIELDS = [
  "schema_version", "target_present", "status_porcelain_v2", "worktree_porcelain", "tracked_files",
  "artifact_files", "unknown_files", "visible_files", "allowlisted_ephemeral_artifacts", "expected_source",
  "observed_source", "expected_path", "observed_path", "expected_membership", "observed_membership",
];
const A33_REMOVAL_INVENTORY_INPUT_FIELDS = new Set([
  "identity", "locked", "expected_source", "observed_source", "expected_path", "expected_membership",
  "allowlisted_ephemeral_artifacts", "visible_files", "raw_inventory_observation",
]);
const A33_SCENARIO_FIELDS = [
  "id", "family", "expected_outcome", "prerequisites", "operation_kind", "attachment_selector",
  "approval_variant", "expected_transition", "required_evidence_types", "cleanup_expectation",
];
const A33_FAMILIES = new Set([
  "effective-profile-install", "host-ignore-nested-prepare", "approval-key-class-risk-negative",
  "valid-add", "typed-removal-inventory", "valid-remove", "deliberate-violation", "cleanup-global-consumption",
]);
const A33_ATTACHMENT_SELECTORS = new Set([
  "host", "host-destination", "all-attachments", "isolated-opencode", "existing", "create-enabled",
  "create-disabled", "repo-and-worktree-keys-add-and-remove", "run-root", "global",
]);

function a33Scenario(id, family, expectedOutcome, prerequisites, operationKind, attachmentSelector,
  approvalVariant, expectedTransition, requiredEvidenceTypes, cleanupExpectation) {
  return Object.freeze({
    id, family, expected_outcome: expectedOutcome, prerequisites: Object.freeze([...prerequisites]),
    operation_kind: operationKind, attachment_selector: attachmentSelector, approval_variant: approvalVariant,
    expected_transition: expectedTransition, required_evidence_types: Object.freeze([...requiredEvidenceTypes]),
    cleanup_expectation: cleanupExpectation,
  });
}

const S = a33Scenario;
export const A33_RUNTIME_SCENARIO_REGISTRY = Object.freeze([
  S("a33-host-git-positive", "host-ignore-nested-prepare", "pass", ["prepare"], null, "host", "none", "unchanged", ["host-identity", "git-toplevel"], "retain"),
  S("a33-ignore-positive", "host-ignore-nested-prepare", "pass", ["prepare"], null, "host-destination", "none", "unchanged", ["check-ignore-nonmatching", "ignore-provenance"], "retain"),
  S("a33-multiple-attachments", "host-ignore-nested-prepare", "pass", ["prepare"], null, "all-attachments", "none", "unchanged", ["attachment-descriptors", "distinct-destinations"], "retain"),
  S("a33-runtime-prepare-no-worktree-effect", "host-ignore-nested-prepare", "pass", ["prepare"], null, "all-attachments", "none", "unchanged", ["worktree-list-before", "worktree-list-after", "zero-worktree-effects"], "retain"),
  S("a33-runtime-effective-profile-observed", "effective-profile-install", "pass", ["isolated-current-platform-profile"], null, "isolated-opencode", "none", "unchanged", ["effective-merged-permissions", "permission-provenance"], "retain"),
  S("a33-runtime-install-observed", "effective-profile-install", "pass", ["isolated-current-platform-install"], null, "isolated-opencode", "none", "unchanged", ["canonical-agent-files", "installed-whole-file-equality"], "retain"),
  S("a33-runtime-nested-repository-observed", "host-ignore-nested-prepare", "pass", ["valid-adds"], "add", "all-attachments", "valid", "absent-to-populated", ["nested-destinations", "worktree-membership"], "retain"),
  S("a33-runtime-approval-positive", "valid-add", "pass", ["fresh-add-approval"], "add", "existing", "valid", "absent-to-populated", ["approval-binding", "approval-unexpired", "approval-unique"], "registered"),
  S("a33-runtime-each-attachment-add-separate-approval", "valid-add", "pass", ["valid-adds"], "add", "all-attachments", "valid-distinct", "absent-to-populated", ["all-add-approvals", "approval-unique", "approval-binding"], "registered"),
  S("a33-runtime-each-attachment-remove-separate-approval", "valid-remove", "pass", ["valid-removes"], "remove", "all-attachments", "valid-distinct", "populated-to-absent", ["all-remove-approvals", "approval-unique", "approval-binding"], "removed"),
  S("a33-runtime-add-approval-wrong-zero-effect", "approval-key-class-risk-negative", "blocked", ["prepare"], "add", "existing", "wrong-operation-id", "unchanged", ["approval-classification", "no-effect", "unchanged-state"], "not_registered"),
  S("a33-runtime-add-approval-reused-zero-effect", "approval-key-class-risk-negative", "blocked", ["used-add-approval"], "add", "existing", "reused", "unchanged", ["approval-classification", "approval-reuse", "no-effect", "unchanged-state"], "not_registered"),
  S("a33-runtime-remove-approval-wrong-zero-effect", "approval-key-class-risk-negative", "blocked", ["registered-target"], "remove", "existing", "wrong-operation", "unchanged", ["approval-classification", "no-effect", "unchanged-state"], "registered"),
  S("a33-runtime-remove-approval-reused-zero-effect", "approval-key-class-risk-negative", "blocked", ["registered-target", "used-remove-approval"], "remove", "existing", "reused", "unchanged", ["approval-classification", "approval-reuse", "no-effect", "unchanged-state"], "registered"),
  S("a33-runtime-fixture-add-real-approval-zero-effect", "approval-key-class-risk-negative", "blocked", ["prepare"], "add", "existing", "real-for-fixture", "unchanged", ["approval-classification", "no-effect", "unchanged-state"], "not_registered"),
  S("a33-runtime-fixture-remove-real-approval-zero-effect", "approval-key-class-risk-negative", "blocked", ["registered-target"], "remove", "existing", "real-for-fixture", "unchanged", ["approval-classification", "no-effect", "unchanged-state"], "registered"),
  S("a33-runtime-operation-class-mismatch-zero-effect", "approval-key-class-risk-negative", "blocked", ["prepare"], "add", "existing", "operation-class-mismatch", "unchanged", ["approval-classification", "no-effect", "unchanged-state"], "not_registered"),
  S("a33-runtime-approval-missing-zero-effect", "approval-key-class-risk-negative", "blocked", ["prepare"], "add", "existing", "missing", "unchanged", ["approval-classification", "no-effect", "unchanged-state"], "not_registered"),
  S("a33-runtime-missing-approval-null-fields", "approval-key-class-risk-negative", "blocked", ["prepare"], "add", "existing", "missing", "unchanged", ["missing-approval-null-fields", "no-effect", "unchanged-state"], "not_registered"),
  S("a33-runtime-approval-stale-zero-effect", "approval-key-class-risk-negative", "blocked", ["approval-snapshot"], "add", "existing", "stale-snapshot-mismatch", "unchanged", ["approval-classification", "snapshot-mismatch", "no-effect", "unchanged-state"], "not_registered"),
  S("a33-runtime-approval-mismatched-zero-effect", "approval-key-class-risk-negative", "blocked", ["prepare"], "add", "existing", "mismatched", "unchanged", ["approval-classification", "no-effect", "unchanged-state"], "not_registered"),
  S("a33-runtime-approval-expired-zero-effect", "approval-key-class-risk-negative", "blocked", ["prepare"], "add", "existing", "expired", "unchanged", ["approval-classification", "no-effect", "unchanged-state"], "not_registered"),
  S("a33-runtime-approval-wrong-source-zero-effect", "approval-key-class-risk-negative", "blocked", ["prepare"], "add", "existing", "wrong-source", "unchanged", ["approval-classification", "no-effect", "unchanged-state"], "not_registered"),
  S("a33-runtime-approval-wrong-destination-zero-effect", "approval-key-class-risk-negative", "blocked", ["prepare"], "add", "existing", "wrong-destination", "unchanged", ["approval-classification", "no-effect", "unchanged-state"], "not_registered"),
  S("a33-runtime-approval-wrong-branch-zero-effect", "approval-key-class-risk-negative", "blocked", ["prepare"], "add", "existing", "wrong-branch", "unchanged", ["approval-classification", "no-effect", "unchanged-state"], "not_registered"),
  S("a33-runtime-approval-wrong-ref-zero-effect", "approval-key-class-risk-negative", "blocked", ["prepare"], "add", "existing", "wrong-base-ref", "unchanged", ["approval-classification", "no-effect", "unchanged-state"], "not_registered"),
  S("a33-runtime-add-approval-reused-real-remove-zero-effect", "approval-key-class-risk-negative", "blocked", ["used-add-approval", "registered-target"], "remove", "existing", "reused-add-for-remove", "unchanged", ["approval-classification", "approval-reuse", "no-effect", "unchanged-state"], "registered"),
  S("a33-runtime-approval-other-operation-zero-effect", "approval-key-class-risk-negative", "blocked", ["prepare"], "add", "existing", "wrong-operation-kind", "unchanged", ["approval-classification", "no-effect", "unchanged-state"], "not_registered"),
  S("a33-runtime-approval-declined-unavailable", "approval-key-class-risk-negative", "blocked", ["prepare"], "add", "existing", "declined-or-unavailable", "unchanged", ["approval-classification", "no-effect", "unchanged-state"], "not_registered"),
  S("a33-runtime-add-trusted-code-risk-accepted", "valid-add", "pass", ["fresh-add-approval"], "add", "all-attachments", "add-risk-accepted", "absent-to-populated", ["trusted-code-risk", "approval-binding", "worktree-effect"], "registered"),
  S("a33-runtime-add-trusted-code-risk-declined-zero-effect", "approval-key-class-risk-negative", "blocked", ["prepare"], "add", "existing", "add-risk-declined", "unchanged", ["approval-classification", "trusted-code-risk", "no-effect", "unchanged-state"], "not_registered"),
  S("a33-runtime-add-trusted-code-risk-unavailable-zero-effect", "approval-key-class-risk-negative", "blocked", ["prepare"], "add", "existing", "add-risk-unavailable", "unchanged", ["approval-classification", "trusted-code-risk", "no-effect", "unchanged-state"], "not_registered"),
  S("a33-runtime-remove-trusted-code-risk-not-applicable", "valid-remove", "pass", ["fresh-remove-approval", "clean-inventory"], "remove", "all-attachments", "remove-risk-not-applicable", "populated-to-absent", ["trusted-code-risk", "approval-binding", "worktree-effect"], "removed"),
  S("a33-pre-add-target-absent", "valid-add", "pass", ["fresh-add-approval"], "add", "all-attachments", "valid", "absent-to-populated", ["target-before-identity", "identity-schema"], "registered"),
  S("a33-add-delta-exact", "valid-add", "pass", ["valid-adds"], "add", "all-attachments", "valid", "absent-to-populated", ["expected-delta", "observed-delta", "exact-delta"], "registered"),
  S("a33-add-common-dir-exact-allowed-delta", "valid-add", "pass", ["valid-adds"], "add", "all-attachments", "valid", "absent-to-populated", ["common-dir-admin-entry", "branch-ref", "branch-reflog", "exact-delta"], "registered"),
  S("a33-add-common-dir-identity-preserved", "valid-add", "pass", ["valid-adds"], "add", "all-attachments", "valid", "absent-to-populated", ["common-dir-identity", "exact-delta"], "registered"),
  S("a33-add-existing-branch-no-ref-reflog-creation", "valid-add", "pass", ["valid-add-existing"], "add", "existing", "valid", "absent-to-populated", ["branch-ref", "branch-reflog", "exact-delta"], "registered"),
  S("a33-add-new-branch-reflog-enabled-created", "valid-add", "pass", ["valid-add-create-enabled"], "add", "create-enabled", "valid", "absent-to-populated", ["branch-ref", "branch-reflog", "exact-delta"], "registered"),
  S("a33-add-new-branch-reflog-disabled-absent", "valid-add", "pass", ["valid-add-create-disabled"], "add", "create-disabled", "valid", "absent-to-populated", ["branch-ref", "branch-reflog", "exact-delta"], "registered"),
  S("a33-unrelated-common-dir-preserved", "valid-add", "pass", ["valid-adds", "valid-removes"], null, "all-attachments", "valid", "declared-only", ["unrelated-common-dir", "unrelated-refs", "unrelated-worktrees", "exact-delta"], "removed"),
  S("a33-add-unrelated-preserved", "valid-add", "pass", ["valid-adds"], "add", "all-attachments", "valid", "absent-to-populated", ["unrelated-common-dir", "unrelated-refs", "unrelated-worktrees", "exact-delta"], "registered"),
  S("a33-pre-remove-target-populated", "valid-remove", "pass", ["clean-inventory"], "remove", "all-attachments", "valid", "populated-to-absent", ["target-before-identity", "identity-schema"], "removed"),
  S("a33-remove-delta-exact", "valid-remove", "pass", ["valid-removes"], "remove", "all-attachments", "valid", "populated-to-absent", ["expected-delta", "observed-delta", "exact-delta"], "removed"),
  S("a33-remove-common-dir-exact-allowed-delta", "valid-remove", "pass", ["valid-removes"], "remove", "all-attachments", "valid", "populated-to-absent", ["common-dir-admin-entry", "branch-ref", "branch-reflog", "exact-delta"], "removed"),
  S("a33-remove-common-dir-identity-preserved", "valid-remove", "pass", ["valid-removes"], "remove", "all-attachments", "valid", "populated-to-absent", ["common-dir-identity", "exact-delta"], "removed"),
  S("a33-remove-dirty-block", "typed-removal-inventory", "blocked", ["registered-target"], "remove", "existing", "tracked-modified-or-deleted", "unchanged", ["typed-inventory", "tracked-state", "no-effect", "unchanged-state"], "registered"),
  S("a33-remove-unknown-block", "typed-removal-inventory", "blocked", ["registered-target"], "remove", "existing", "unknown", "unchanged", ["typed-inventory", "unknown-state", "no-effect", "unchanged-state"], "registered"),
  S("a33-remove-user-visible-block", "typed-removal-inventory", "blocked", ["registered-target"], "remove", "existing", "user-visible", "unchanged", ["typed-inventory", "user-visible-state", "no-effect", "unchanged-state"], "registered"),
  S("a33-remove-ignored-block", "typed-removal-inventory", "blocked", ["registered-target"], "remove", "existing", "ignored", "unchanged", ["typed-inventory", "ignored-state", "no-effect", "unchanged-state"], "registered"),
  S("a33-remove-untracked-block", "typed-removal-inventory", "blocked", ["registered-target"], "remove", "existing", "untracked", "unchanged", ["typed-inventory", "untracked-state", "no-effect", "unchanged-state"], "registered"),
  S("a33-remove-artifact-block", "typed-removal-inventory", "blocked", ["registered-target"], "remove", "existing", "artifact", "unchanged", ["typed-inventory", "artifact-state", "no-effect", "unchanged-state"], "registered"),
  S("a33-remove-locked-block", "typed-removal-inventory", "blocked", ["registered-target"], "remove", "existing", "locked", "unchanged", ["typed-inventory", "locked-state", "no-effect", "unchanged-state"], "registered"),
  S("a33-remove-wrong-source-block", "typed-removal-inventory", "blocked", ["registered-target"], "remove", "existing", "wrong-source", "unchanged", ["typed-inventory", "source-binding", "no-effect", "unchanged-state"], "registered"),
  S("a33-remove-wrong-path-block", "typed-removal-inventory", "blocked", ["registered-target"], "remove", "existing", "wrong-path-or-membership", "unchanged", ["typed-inventory", "path-binding", "membership-binding", "no-effect", "unchanged-state"], "registered"),
  S("a33-remove-missing-target-block", "typed-removal-inventory", "blocked", ["prepare"], "remove", "existing", "missing", "unchanged", ["typed-inventory", "missing-state", "no-effect", "unchanged-state"], "not_registered"),
  S("a33-runtime-cleanup-after-approved-removes", "cleanup-global-consumption", "pass", ["valid-removes"], null, "all-attachments", "all-removed", "removed", ["registered-attachments", "approved-removes", "cleanup-eligibility"], "eligible_for_global_join"),
  S("a33-runtime-cleanup-retain-registered", "cleanup-global-consumption", "pass", ["blocked-remove"], null, "run-root", "retained", "unchanged", ["registered-attachments", "retained-root", "cleanup-ineligible"], "retain"),
  S("a33-residual-nongoal-exit0", "cleanup-global-consumption", "pass", ["all-runtime-cases"], null, "global", "named-residuals", "unchanged", ["residual-nongoals", "cleanup-eligibility"], "eligible_for_global_join"),
  S("a33-material-missing-exit3", "deliberate-violation", "unverified", ["missing-mandatory-positive"], null, "global", "missing-positive", "unchanged", ["missing-evidence-classification"], "retain"),
  S("a33-contract-violation-exit5", "deliberate-violation", "fail", ["contradictory-evidence"], null, "global", "contract-violation", "contradictory", ["violation-classification"], "retain"),
  S("a33-common-dir-identity-change-block", "deliberate-violation", "fail", ["mutated-add-or-remove"], null, "all-attachments", "common-dir-identity-change", "wrong-delta", ["common-dir-identity", "violation-classification"], "retain"),
  S("a33-add-common-dir-unrelated-mutation-block", "deliberate-violation", "fail", ["mutated-add"], "add", "all-attachments", "unrelated-mutation", "wrong-delta", ["unrelated-common-dir", "violation-classification"], "retain"),
  S("a33-remove-common-dir-unrelated-mutation-block", "deliberate-violation", "fail", ["mutated-remove"], "remove", "all-attachments", "unrelated-mutation", "wrong-delta", ["unrelated-common-dir", "violation-classification"], "retain"),
  S("a33-add-new-branch-reflog-enabled-missing-block", "deliberate-violation", "fail", ["mutated-add-create-enabled"], "add", "create-enabled", "missing-reflog", "wrong-delta", ["branch-ref", "branch-reflog", "violation-classification"], "retain"),
  S("a33-add-new-branch-reflog-disabled-unexpected-block", "deliberate-violation", "fail", ["mutated-add-create-disabled"], "add", "create-disabled", "unexpected-reflog", "wrong-delta", ["branch-ref", "branch-reflog", "violation-classification"], "retain"),
  S("a33-remove-branch-deletion-block", "deliberate-violation", "fail", ["mutated-remove"], "remove", "all-attachments", "branch-deletion", "wrong-delta", ["branch-ref", "violation-classification"], "retain"),
  S("a33-remove-branch-reflog-mutation-block", "deliberate-violation", "fail", ["mutated-remove"], "remove", "all-attachments", "reflog-mutation", "wrong-delta", ["branch-reflog", "violation-classification"], "retain"),
  S("a33-runtime-key-mismatch-zero-effect", "approval-key-class-risk-negative", "blocked", ["prepare", "registered-target"], null, "repo-and-worktree-keys-add-and-remove", "repo-or-worktree-key-mismatch", "unchanged", ["approval-classification", "key-parameter-matrix", "no-effect", "unchanged-state"], "retain"),
  S("a33-runtime-identity-transition-schema", "cleanup-global-consumption", "pass", ["valid-adds", "valid-removes"], null, "all-attachments", "valid", "absent-populated-absent", ["host-identity", "source-identity", "target-before-identity", "target-after-identity", "identity-schema"], "removed"),
]);

export function validateA33ScenarioRegistry(registry, expectedIds) {
  if (!Array.isArray(registry) || !Array.isArray(expectedIds) || registry.length !== expectedIds.length) throw new Error("scenario registry mismatch");
  const canonicalIds = A33_RUNTIME_SCENARIO_REGISTRY.map(({ id }) => id);
  if (JSON.stringify(expectedIds) !== JSON.stringify(canonicalIds) || registry.length !== A33_RUNTIME_SCENARIO_REGISTRY.length) throw new Error("scenario registry canonical mismatch");
  if (new Set(expectedIds).size !== expectedIds.length || new Set(registry.map((entry) => entry?.id)).size !== registry.length) throw new Error("scenario registry duplicate");
  const fullMetadata = new Set();
  for (let index = 0; index < expectedIds.length; index += 1) {
    const entry = registry[index];
    const canonical = A33_RUNTIME_SCENARIO_REGISTRY[index];
    if (!exactKeys(entry, A33_SCENARIO_FIELDS) || entry.id !== expectedIds[index] || !A33_FAMILIES.has(entry.family)) throw new Error("scenario registry order or metadata mismatch");
    if (A33_SCENARIO_FIELDS.some((name) => JSON.stringify(entry[name]) !== JSON.stringify(canonical[name]))) throw new Error("scenario registry canonical metadata mismatch");
    if (!["pass", "blocked", "unverified", "fail"].includes(entry.expected_outcome)
      || !Array.isArray(entry.prerequisites) || entry.prerequisites.some((value) => typeof value !== "string" || !value)
      || ![null, "add", "remove"].includes(entry.operation_kind) || !A33_ATTACHMENT_SELECTORS.has(entry.attachment_selector)
      || typeof entry.approval_variant !== "string" || !entry.approval_variant || typeof entry.expected_transition !== "string" || !entry.expected_transition
      || !Array.isArray(entry.required_evidence_types) || entry.required_evidence_types.length === 0
      || new Set(entry.required_evidence_types).size !== entry.required_evidence_types.length
      || entry.required_evidence_types.some((value) => typeof value !== "string" || !value)
      || typeof entry.cleanup_expectation !== "string" || !entry.cleanup_expectation) throw new Error("scenario registry metadata missing");
    if (["host", "host-destination", "isolated-opencode", "repo-and-worktree-keys-add-and-remove", "run-root", "global"].includes(entry.attachment_selector)
      && entry.operation_kind !== null) throw new Error("scenario registry unreachable selector");
    if (["create-enabled", "create-disabled"].includes(entry.attachment_selector) && entry.operation_kind !== "add") throw new Error("scenario registry unreachable selector");
    const signature = JSON.stringify(A33_SCENARIO_FIELDS.filter((name) => name !== "id").map((name) => entry[name]));
    if (fullMetadata.has(signature)) throw new Error("scenario registry duplicate full metadata");
    fullMetadata.add(signature);
  }
  return true;
}

function parseA33Arguments(argv) {
  const options = { provider: PROVIDER };
  const values = new Map([
    ["--project", "project"], ["--fixture", "fixture"], ["--mode", "mode"], ["--provider", "provider"],
    ["--run-id", "runId"], ["--run-root", "runRoot"], ["--operation-id", "operationId"],
    ["--approval-fd", "approvalFd"],
  ]);
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === "--json") {
      if (options.json) throw new Error("usage");
      options.json = true;
      continue;
    }
    const key = values.get(arg);
    if (!key || Object.hasOwn(options, key) && key !== "provider") throw new Error("usage");
    const value = argv[++index];
    if (!value || value.startsWith("--")) throw new Error("usage");
    options[key] = value;
  }
  if (!options.project || !options.fixture || !options.mode || !options.json || !A33_MODES.has(options.mode) || options.provider !== PROVIDER) throw new Error("usage");
  if (options.mode === "a33-runtime-prepare") {
    if (options.runId || options.runRoot || options.operationId || options.approvalFd) throw new Error("usage");
  } else if (options.mode === "a33-runtime-join") {
    if (!options.runId || !options.runRoot || options.operationId || options.approvalFd) throw new Error("usage");
  } else if (!options.runId || !options.runRoot || !options.operationId) throw new Error("usage");
  if (options.approvalFd !== undefined && (!/^\d+$/.test(options.approvalFd) || Number(options.approvalFd) < 3)) throw new Error("usage");
  return options;
}

export function parseA33FixtureText(text) {
  const fixture = JSON.parse(text);
  const config = fixture.a33;
  const exits = fixture.exit_codes;
  if (fixture.schema !== FIXTURE_SCHEMA || config?.mode !== "a33-attached-shared-trust-domain" || config?.provider !== PROVIDER) throw new Error("fixture");
  if (exits?.safe_observed !== 0 || exits?.usage_or_fixture_error !== 2 || exits?.blocked_or_unverified !== 3 || exits?.unsafe !== 5) throw new Error("fixture");
  for (const [actual, expected] of [
    [config.identity_fields, A33_IDENTITY_FIELDS], [config.dirty_state_fields, A33_DIRTY_FIELDS],
    [config.delta_fields, A33_DELTA_FIELDS], [config.pending_operation_fields, A33_PENDING_FIELDS],
    [config.operation_fields, A33_OPERATION_FIELDS], [config.approval_fields, A33_APPROVAL_FIELDS],
    [config.operation_result_fields, A33_OPERATION_RESULT_FIELDS], [config.runtime_case_fields, A33_RUNTIME_CASE_FIELDS],
  ]) if (JSON.stringify(actual) !== JSON.stringify(expected)) throw new Error("fixture");
  const allIds = [...config.static_mandatory_case_ids, ...config.runtime_mandatory_case_ids];
  if (new Set(allIds).size !== allIds.length || config.key_pattern !== KEY_PATTERN.source) throw new Error("fixture");
  if (!Array.isArray(config.attachments) || config.attachments.length < 2) throw new Error("fixture");
  const attachmentFields = ["repo_key", "worktree_key", "branch", "base_ref", "branch_mode", "reflog_policy"];
  if (config.attachments.some((entry) => !exactKeys(entry, attachmentFields) || !validKey(entry.repo_key) || !validKey(entry.worktree_key)
    || typeof entry.branch !== "string" || !entry.branch || typeof entry.base_ref !== "string" || !entry.base_ref
    || !["existing", "create"].includes(entry.branch_mode) || !["enabled", "disabled"].includes(entry.reflog_policy))) throw new Error("fixture");
  validateA33ScenarioRegistry(A33_RUNTIME_SCENARIO_REGISTRY, config.runtime_mandatory_case_ids);
  return config;
}

function loadA33Fixture(path, project) {
  const candidate = isAbsolute(path) ? path : resolve(project, path);
  const canonical = realpathSync(candidate);
  const expected = realpathSync(join(project, "docs", "harness", "fixtures", "cross-worktree-permission-fixtures.yaml"));
  if (canonical !== expected || !isWithin(canonical, project) || !statSync(canonical).isFile()) throw new Error("fixture");
  const text = readFileSync(canonical, "utf8");
  return { config: parseA33FixtureText(text), canonical, sha256: createHash("sha256").update(text).digest("hex") };
}

function validKey(value) {
  return typeof value === "string" && KEY_PATTERN.test(value) && !RESERVED_KEYS.has(value);
}

function canonicalExisting(path) {
  return realpathSync(path);
}

function canonicalDeclared(path) {
  return existsSync(path) ? realpathSync(path) : resolve(path);
}

function sortedUniqueRelative(values) {
  return [...new Set(values.filter(Boolean))].sort();
}

function a33GitEnvironment(runRoot) {
  return {
    HOME: join(runRoot, "home"), XDG_CONFIG_HOME: join(runRoot, "home", ".config"),
    XDG_DATA_HOME: join(runRoot, "home", ".local", "share"), XDG_CACHE_HOME: join(runRoot, "home", ".cache"),
    TMPDIR: join(runRoot, "tmp"), PATH: "/usr/bin:/bin", LANG: "C.UTF-8", LC_ALL: "C.UTF-8",
    GIT_CONFIG_NOSYSTEM: "1", GIT_CONFIG_SYSTEM: "/dev/null", GIT_CONFIG_GLOBAL: "/dev/null",
    GIT_CONFIG_COUNT: "1", GIT_CONFIG_KEY_0: "core.hooksPath", GIT_CONFIG_VALUE_0: join(runRoot, "empty-hooks"),
    GIT_AUTHOR_NAME: "A33 Probe", GIT_AUTHOR_EMAIL: "probe@example.invalid",
    GIT_COMMITTER_NAME: "A33 Probe", GIT_COMMITTER_EMAIL: "probe@example.invalid",
    OPENCODE_ALLOW_CUSTOM_HOME: A33_INSTALL_ENV_CONTROLS.OPENCODE_ALLOW_CUSTOM_HOME,
    AILI_ALLOW_CROSS_ENV: A33_INSTALL_ENV_CONTROLS.AILI_ALLOW_CROSS_ENV,
  };
}

function gitLines(root, args, env) {
  if (!env) throw new Error("isolated Git environment unavailable");
  const result = run("git", ["-C", root, ...args], { cwd: root, env });
  if (result.status !== 0) throw new Error(`git evidence unavailable: ${args.join(" ")}`);
  return result.stdout ? result.stdout.split("\n").filter(Boolean) : [];
}

function gitOne(root, args, env) {
  return gitLines(root, args, env).join("\n");
}

function gitNul(root, args, env, input = undefined) {
  if (!env) throw new Error("isolated Git environment unavailable");
  const result = run("git", ["-C", root, ...args], { cwd: root, env, input, preserveOutput: true });
  if (result.status !== 0) throw new Error(`git evidence unavailable: ${args.join(" ")}`);
  return result.stdout.split("\0").filter((value) => value !== "");
}

function absoluteGitPath(root, path, env) {
  return resolve(root, gitOne(root, ["rev-parse", "--path-format=absolute", "--git-path", path], env));
}

function validA33RelativePath(path) {
  return typeof path === "string" && path.length > 0 && !isAbsolute(path) && !path.includes("\0")
    && !path.split(/[\\/]/).some((part) => !part || part === "." || part === "..");
}

export function parseA33PorcelainV2(records) {
  if (!Array.isArray(records)) throw new Error("porcelain v2 evidence malformed");
  const trackedModified = [];
  const trackedDeleted = [];
  const untracked = [];
  const ignored = [];
  for (let index = 0; index < records.length; index += 1) {
    const record = records[index];
    if (typeof record !== "string" || !record) throw new Error("porcelain v2 evidence malformed");
    if (record.startsWith("? ")) {
      const path = record.slice(2);
      if (!validA33RelativePath(path)) throw new Error("porcelain v2 evidence malformed");
      untracked.push(path);
    } else if (record.startsWith("! ")) {
      const path = record.slice(2);
      if (!validA33RelativePath(path)) throw new Error("porcelain v2 evidence malformed");
      ignored.push(path);
    }
    else if (record.startsWith("1 ") || record.startsWith("2 ") || record.startsWith("u ")) {
      const fields = record.split(" ");
      const pathIndex = record.startsWith("1 ") ? 8 : record.startsWith("2 ") ? 9 : 10;
      if (fields.length <= pathIndex || fields.slice(0, pathIndex).some((field) => !field)
        || !/^[.MTADRCU]{2}$/.test(fields[1])) throw new Error("porcelain v2 evidence malformed");
      if (record.startsWith("2 ") && !/^[RC][0-9]+$/.test(fields[8])) throw new Error("porcelain v2 evidence malformed");
      const xy = fields[1];
      const path = fields.slice(pathIndex).join(" ");
      if (!validA33RelativePath(path)) throw new Error("porcelain v2 evidence malformed");
      if (xy.includes("D")) trackedDeleted.push(path);
      else if (xy !== "..") trackedModified.push(path);
      if (record.startsWith("2 ")) {
        const originalPath = records[index + 1];
        if (!validA33RelativePath(originalPath)) throw new Error("porcelain v2 evidence malformed");
        index += 1;
      }
    } else throw new Error("porcelain v2 evidence malformed");
  }
  return {
    tracked_modified: sortedUniqueRelative(trackedModified), tracked_deleted: sortedUniqueRelative(trackedDeleted),
    untracked: sortedUniqueRelative(untracked), ignored: sortedUniqueRelative(ignored),
  };
}

export function parseA33WorktreePorcelain(records) {
  if (!Array.isArray(records) || records.length === 0) throw new Error("worktree evidence malformed");
  const worktrees = [];
  const paths = new Set();
  let current = null;
  for (const field of records) {
    if (typeof field !== "string" || !field) throw new Error("worktree evidence malformed");
    if (field.startsWith("worktree ")) {
      const path = field.slice(9);
      if (current && current.fields.length === 0) throw new Error("worktree evidence malformed");
      if (!isAbsolute(path) || resolve(path) !== path || paths.has(path)) throw new Error("worktree evidence malformed");
      paths.add(path);
      current = { path, locked: null, prunable: null, fields: [], seen: new Set(), fieldOrder: -1 };
      worktrees.push(current);
    } else {
      if (!current) throw new Error("worktree evidence malformed");
      const [name, ...rest] = field.split(" ");
      const order = { HEAD: 0, branch: 1, detached: 1, bare: 1, locked: 2, prunable: 3 }[name];
      if (!new Set(["HEAD", "branch", "detached", "bare", "locked", "prunable"]).has(name)
        || current.seen.has(name) || order < current.fieldOrder || (["detached", "bare"].includes(name) && rest.length > 0)
        || (["HEAD", "branch"].includes(name) && (rest.length !== 1 || !rest[0]))
        || (["locked", "prunable"].includes(name) && rest.some((part) => !part))) throw new Error("worktree evidence malformed");
      if ((name === "branch" && current.seen.has("detached")) || (name === "detached" && current.seen.has("branch"))) throw new Error("worktree evidence malformed");
      if ((name === "bare" && ["HEAD", "branch", "detached"].some((value) => current.seen.has(value)))
        || current.seen.has("bare") && ["HEAD", "branch", "detached"].includes(name)) throw new Error("worktree evidence malformed");
      current.seen.add(name);
      current.fieldOrder = order;
      current.fields.push(field);
      if (field === "locked" || field.startsWith("locked ")) current.locked = field.slice(6).trim() || true;
      if (field === "prunable" || field.startsWith("prunable ")) current.prunable = field.slice(8).trim() || true;
    }
  }
  if (current?.fields.length === 0) throw new Error("worktree evidence malformed");
  return worktrees.map(({ seen, fieldOrder, ...worktree }) => worktree);
}

function validA33RawRemovalObservation(raw, identity, input) {
  if (!exactKeys(raw, A33_RAW_INVENTORY_FIELDS) || raw.schema_version !== A33_INTERNAL_EVIDENCE_VERSION
    || typeof raw.target_present !== "boolean") return false;
  for (const name of ["status_porcelain_v2", "worktree_porcelain", "tracked_files", "artifact_files", "unknown_files", "visible_files", "allowlisted_ephemeral_artifacts"]) {
    if (!Array.isArray(raw[name])) return false;
  }
  for (const name of ["tracked_files", "artifact_files", "unknown_files", "visible_files", "allowlisted_ephemeral_artifacts"]) {
    if (raw[name].some((path) => !validA33RelativePath(path))
      || JSON.stringify(raw[name]) !== JSON.stringify([...new Set(raw[name])].sort())) return false;
  }
  for (const name of ["expected_source", "expected_path", "observed_path"]) {
    if (typeof raw[name] !== "string" || !raw[name] || !isAbsolute(raw[name]) || resolve(raw[name]) !== raw[name]) return false;
  }
  if (raw.observed_source !== null && (typeof raw.observed_source !== "string" || !raw.observed_source
    || !isAbsolute(raw.observed_source) || resolve(raw.observed_source) !== raw.observed_source)) return false;
  if (!["main", "linked"].includes(raw.expected_membership) || !["absent", "main", "linked"].includes(raw.observed_membership)) return false;
  let status;
  let worktrees;
  try {
    status = parseA33PorcelainV2(raw.status_porcelain_v2);
    worktrees = parseA33WorktreePorcelain(raw.worktree_porcelain);
  } catch {
    return false;
  }
  if (raw.target_present !== (identity.identity_state === "populated") || raw.observed_path !== identity.declared_root
    || raw.observed_source !== identity.git_common_dir || raw.observed_membership !== identity.worktree_membership
    || input.expected_source !== undefined && raw.expected_source !== input.expected_source
    || input.observed_source !== undefined && raw.observed_source !== input.observed_source
    || input.expected_path !== undefined && raw.expected_path !== input.expected_path
    || input.expected_membership !== undefined && raw.expected_membership !== input.expected_membership
    || input.visible_files !== undefined && JSON.stringify(raw.visible_files) !== JSON.stringify(input.visible_files)
    || input.allowlisted_ephemeral_artifacts !== undefined
      && JSON.stringify(raw.allowlisted_ephemeral_artifacts) !== JSON.stringify(input.allowlisted_ephemeral_artifacts)) return false;
  const targetWorktrees = worktrees.filter(({ path }) => path === raw.expected_path);
  if (targetWorktrees.length !== (raw.target_present ? 1 : 0)) return false;
  if (!raw.target_present) {
    return ["status_porcelain_v2", "tracked_files", "artifact_files", "unknown_files", "visible_files", "allowlisted_ephemeral_artifacts"]
      .every((name) => raw[name].length === 0);
  }
  return JSON.stringify(raw.tracked_files) === JSON.stringify(identity.tracked_files)
    && JSON.stringify(status.untracked) === JSON.stringify(identity.untracked_files)
    && JSON.stringify(status.ignored) === JSON.stringify(identity.ignored_files)
    && JSON.stringify(raw.artifact_files) === JSON.stringify(identity.artifact_files)
    && JSON.stringify(raw.unknown_files) === JSON.stringify(identity.unknown_files)
    && (status.tracked_modified.length > 0) === identity.dirty_state.tracked_modified
    && (status.tracked_deleted.length > 0) === identity.dirty_state.tracked_deleted
    && (input.locked === undefined || Boolean(targetWorktrees[0].locked) === input.locked);
}

function absentIdentity(declaredRoot) {
  return {
    identity_state: "absent", declared_root: canonicalDeclared(declaredRoot), path_state: "absent",
    canonical_root: null, git_toplevel: null, git_private_dir: null, git_common_dir: null, git_head: null,
    git_branch: null, detached_head: null, worktree_membership: "absent", dirty_state: null,
    tracked_files: null, untracked_files: null, ignored_files: null, artifact_files: null, unknown_files: null,
  };
}

function populatedIdentity(root, membership = null, env) {
  if (!env) throw new Error("isolated Git environment unavailable");
  const declared = canonicalExisting(root);
  const top = canonicalExisting(gitOne(declared, ["rev-parse", "--show-toplevel"], env));
  const privateDir = canonicalExisting(gitOne(declared, ["rev-parse", "--path-format=absolute", "--absolute-git-dir"], env));
  const commonDir = canonicalExisting(gitOne(declared, ["rev-parse", "--path-format=absolute", "--git-common-dir"], env));
  const branchResult = run("git", ["-C", declared, "symbolic-ref", "--short", "-q", "HEAD"], { cwd: declared, env });
  const branch = branchResult.status === 0 && branchResult.stdout ? branchResult.stdout : null;
  const inventory = parseA33PorcelainV2(gitNul(declared, ["--no-optional-locks", "status", "--porcelain=v2", "-z", "--untracked-files=all", "--ignored"], env));
  const tracked = sortedUniqueRelative(gitNul(declared, ["ls-files", "-z"], env));
  return {
    identity_state: "populated", declared_root: declared, path_state: "present", canonical_root: declared,
    git_toplevel: top, git_private_dir: privateDir, git_common_dir: commonDir,
    git_head: gitOne(declared, ["rev-parse", "--verify", "HEAD"], env), git_branch: branch,
    detached_head: branch === null, worktree_membership: membership ?? (privateDir === commonDir ? "main" : "linked"),
    dirty_state: { tracked_modified: inventory.tracked_modified.length > 0, tracked_deleted: inventory.tracked_deleted.length > 0, untracked_count: inventory.untracked.length, ignored_count: inventory.ignored.length },
    tracked_files: tracked, untracked_files: inventory.untracked,
    ignored_files: inventory.ignored, artifact_files: [], unknown_files: [],
  };
}

export function validateA33Identity(identity) {
  if (!exactKeys(identity, A33_IDENTITY_FIELDS) || !isAbsolute(identity.declared_root) || !identity.declared_root) return false;
  if (identity.identity_state === "absent") {
    if (identity.path_state !== "absent" || identity.worktree_membership !== "absent") return false;
    return A33_IDENTITY_FIELDS.filter((name) => !["identity_state", "declared_root", "path_state", "worktree_membership"].includes(name)).every((name) => identity[name] === null);
  }
  if (identity.identity_state !== "populated" || identity.path_state !== "present" || !["main", "linked"].includes(identity.worktree_membership)) return false;
  for (const name of ["canonical_root", "git_toplevel", "git_private_dir", "git_common_dir", "git_head"]) if (typeof identity[name] !== "string" || !identity[name]) return false;
  if (typeof identity.detached_head !== "boolean" || (identity.detached_head ? identity.git_branch !== null : typeof identity.git_branch !== "string" || !identity.git_branch)) return false;
  if (!exactKeys(identity.dirty_state, A33_DIRTY_FIELDS)) return false;
  if (typeof identity.dirty_state.tracked_modified !== "boolean" || typeof identity.dirty_state.tracked_deleted !== "boolean") return false;
  if (![identity.dirty_state.untracked_count, identity.dirty_state.ignored_count].every((value) => Number.isInteger(value) && value >= 0)) return false;
  for (const name of ["tracked_files", "untracked_files", "ignored_files", "artifact_files", "unknown_files"]) {
    const values = identity[name];
    if (!Array.isArray(values) || values.some((value) => typeof value !== "string" || !value || isAbsolute(value) || value.split(/[\\/]/).includes(".."))) return false;
    if (JSON.stringify(values) !== JSON.stringify([...new Set(values)].sort())) return false;
  }
  return true;
}

function listTree(path) {
  if (!existsSync(path)) return null;
  return readdirSync(path, { recursive: true, withFileTypes: true })
    .map((entry) => join(entry.parentPath ?? entry.path ?? path, entry.name))
    .map((entry) => relative(path, entry).replaceAll("\\", "/"))
    .sort();
}

function worktreeRecords(source, excludedDestination, env) {
  return parseA33WorktreePorcelain(gitNul(source, ["worktree", "list", "--porcelain", "-z"], env))
    .filter((record) => resolve(record.path) !== resolve(excludedDestination))
    .sort((left, right) => left.path.localeCompare(right.path));
}

function refValue(source, ref, env) {
  const result = run("git", ["-C", source, "rev-parse", "--verify", ref], { cwd: source, env });
  return result.status === 0 && result.stdout ? result.stdout : null;
}

function adminSnapshot(source, operation, targetIdentity, env) {
  const sourceIdentity = populatedIdentity(source, null, env);
  const common = sourceIdentity.git_common_dir;
  const targetWorktree = parseA33WorktreePorcelain(gitNul(source, ["worktree", "list", "--porcelain", "-z"], env))
    .find((record) => resolve(record.path) === resolve(operation.destination));
  const reflogPath = absoluteGitPath(source, `logs/refs/heads/${operation.branch}`, env);
  const branchPath = absoluteGitPath(source, `refs/heads/${operation.branch}`, env);
  const adminName = targetIdentity?.identity_state === "populated" ? basename(targetIdentity.git_private_dir) : basename(operation.destination);
  const adminPath = absoluteGitPath(source, `worktrees/${adminName}`, env);
  const excludedPrefixes = [`worktrees/${adminName}`, `refs/heads/${operation.branch}`, `logs/refs/heads/${operation.branch}`];
  const unrelatedCommon = (listTree(common) ?? []).filter((entry) => entry !== "worktrees" && !excludedPrefixes.some((prefix) => entry === prefix || entry.startsWith(`${prefix}/`)));
  const unrelatedWorktrees = worktreeRecords(source, operation.destination, env);
  return {
    target_path: existsSync(operation.destination) ? "present" : "absent",
    worktree_membership: targetWorktree ? "linked" : "absent",
    common_dir_identity: common,
    common_dir_admin_entry: existsSync(adminPath) ? { path: adminPath, entries: listTree(adminPath) } : null,
    branch_ref: { path: branchPath, value: refValue(source, `refs/heads/${operation.branch}`, env) },
    branch_reflog: { path: reflogPath, value: existsSync(reflogPath) ? readFileSync(reflogPath, "utf8") : null },
    unrelated_common_dir_entries: unrelatedCommon,
    unrelated_refs: gitLines(source, ["for-each-ref", "--format=%(refname) %(objectname)"], env).filter((line) => line.split(" ")[0] !== `refs/heads/${operation.branch}`),
    config: readFileSync(join(common, "config"), "utf8"), hooks: listTree(join(common, "hooks")),
    unrelated_worktree_records: unrelatedWorktrees,
    unrelated_prunable_entries: unrelatedWorktrees, other_files: null,
  };
}

function producerAdminSnapshot(raw) {
  return { ...raw, branch_ref: raw.branch_ref.value, branch_reflog: raw.branch_reflog.value };
}

function changeRecord(before, after) {
  const equal = JSON.stringify(before) === JSON.stringify(after);
  const absentBefore = before === null || before === "absent";
  const absentAfter = after === null || after === "absent";
  if (!equal && !absentBefore && !absentAfter) return null;
  return { before, after, change: equal ? "unchanged" : absentBefore ? "created" : "deleted" };
}

function deltaFrom(before, after) {
  const entries = A33_DELTA_FIELDS.map((name) => [name, changeRecord(before[name] ?? null, after[name] ?? null)]);
  return entries.some(([, value]) => value === null) ? null : Object.fromEntries(entries);
}

function exactDeltaExpected(operation, before, after) {
  const expected = deltaFrom(before, before);
  if (expected === null) return null;
  expected.target_path = changeRecord(before.target_path, after.target_path);
  expected.worktree_membership = changeRecord(before.worktree_membership, after.worktree_membership);
  expected.common_dir_admin_entry = changeRecord(before.common_dir_admin_entry, after.common_dir_admin_entry);
  if (operation.kind === "add" && operation.branch_mode === "create") {
    expected.branch_ref = changeRecord(before.branch_ref, after.branch_ref);
    if (operation.reflog_policy === "enabled") expected.branch_reflog = changeRecord(before.branch_reflog, after.branch_reflog);
  }
  return Object.values(expected).some((value) => value === null) ? null : expected;
}

function exactRawTransition(operation, before, after) {
  const refBefore = before?.branch_ref?.value;
  const refAfter = after?.branch_ref?.value;
  const reflogBefore = before?.branch_reflog?.value;
  const reflogAfter = after?.branch_reflog?.value;
  if (operation.kind === "add") {
    if (before?.common_dir_admin_entry !== null || after?.common_dir_admin_entry === null) return false;
    if (operation.branch_mode === "create") {
      if (refBefore !== null || refAfter === null) return false;
      if (operation.reflog_policy === "enabled" ? reflogBefore !== null || reflogAfter === null : reflogBefore !== null || reflogAfter !== null) return false;
    } else if (refBefore !== refAfter || reflogBefore !== reflogAfter) return false;
  } else if (before?.common_dir_admin_entry === null || after?.common_dir_admin_entry !== null || refBefore !== refAfter || reflogBefore !== reflogAfter) return false;
  return true;
}

function validateDelta(delta) {
  if (!exactKeys(delta, A33_DELTA_FIELDS)) return false;
  return A33_DELTA_FIELDS.every((name) => {
    const entry = delta[name];
    if (!exactKeys(entry, ["before", "after", "change"]) || !["created", "deleted", "unchanged"].includes(entry.change)) return false;
    const equal = JSON.stringify(entry.before) === JSON.stringify(entry.after);
    const beforeAbsent = entry.before === null || entry.before === "absent";
    const afterAbsent = entry.after === null || entry.after === "absent";
    return entry.change === "unchanged" ? equal
      : entry.change === "created" ? beforeAbsent && !afterAbsent
        : !beforeAbsent && afterAbsent;
  });
}

function statePath(runRoot) { return join(runRoot, "state.json"); }

function approvalBinding(approval) {
  return Object.fromEntries(["run_id", "operation_id", "kind", "operation_class", "source", "destination", "repo_key", "worktree_key", "branch", "base_ref", "branch_mode", "reflog_policy"]
    .map((name) => [name, approval[name]]));
}

export function buildA33OperationSnapshot(state, operation, preconditions = undefined) {
  const observed = preconditions ?? {
    destination_present: existsSync(operation.destination),
    registered: state.registered.includes(operation.destination),
  };
  if (!exactKeys(observed, A33_SNAPSHOT_PRECONDITION_FIELDS)
    || Object.values(observed).some((value) => typeof value !== "boolean")) throw new Error("approval snapshot malformed");
  return {
    schema_version: A33_INTERNAL_EVIDENCE_VERSION, run_id: state.run_id, ...operation,
    preconditions: { ...observed },
  };
}

function validA33OperationSnapshot(snapshot, state, operation) {
  return exactKeys(snapshot, A33_OPERATION_SNAPSHOT_FIELDS)
    && snapshot.schema_version === A33_INTERNAL_EVIDENCE_VERSION
    && snapshot.run_id === state.run_id
    && A33_OPERATION_FIELDS.every((name) => snapshot[name] === operation[name])
    && exactKeys(snapshot.preconditions, A33_SNAPSHOT_PRECONDITION_FIELDS)
    && Object.values(snapshot.preconditions).every((value) => typeof value === "boolean");
}

export function seedA33ApprovalSnapshot(state, approval, operationSnapshot) {
  if (!exactKeys(approval, A33_APPROVAL_FIELDS) || typeof approval.approval_id !== "string" || !approval.approval_id
    || !validA33OperationSnapshot(operationSnapshot, state, operationSnapshot)) throw new Error("approval snapshot malformed");
  const seeded = structuredClone(state);
  seeded.approval_snapshots ??= {};
  seeded.approval_snapshots[approval.approval_id] = { approval_binding: approvalBinding(approval), operation_snapshot: structuredClone(operationSnapshot) };
  return seeded;
}

function validApprovalSnapshot(record, approval, state, operation) {
  return exactKeys(record, A33_APPROVAL_SNAPSHOT_FIELDS)
    && exactKeys(record.approval_binding, ["run_id", "operation_id", "kind", "operation_class", "source", "destination", "repo_key", "worktree_key", "branch", "base_ref", "branch_mode", "reflog_policy"])
    && JSON.stringify(record.approval_binding) === JSON.stringify(approvalBinding(approval))
    && validA33OperationSnapshot(record.operation_snapshot, state, operation);
}

function consumeApproval(state, approval, operationSnapshot) {
  const record = { approval: structuredClone(approval), snapshot: structuredClone(operationSnapshot) };
  state.used_approvals.push(approval.approval_id);
  state.consumed_approvals[approval.approval_id] = record;
  state.approval_snapshots[approval.approval_id] = { approval_binding: approvalBinding(approval), operation_snapshot: structuredClone(operationSnapshot) };
}

function markerRecord(runRoot, runId, cleanupNonce) {
  return { schema_version: A33_INTERNAL_EVIDENCE_VERSION, run_root: runRoot, run_id: runId, cleanup_nonce: cleanupNonce };
}

function loadRun(options) {
  const runRoot = realpathSync(resolve(options.runRoot));
  const tempRoot = realpathSync(tmpdir());
  const markerPath = join(runRoot, ".aili-a33-driver-owned");
  if (!isWithin(runRoot, tempRoot) || basename(runRoot) !== options.runId || !/^aili-a33-runtime-[A-Za-z0-9]{6}$/.test(options.runId) || !existsSync(markerPath)) throw new Error("run identity mismatch");
  let state;
  let marker;
  try {
    state = JSON.parse(readFileSync(statePath(runRoot), "utf8"));
    marker = JSON.parse(readFileSync(markerPath, "utf8"));
  } catch {
    throw new Error("run identity or state evidence malformed");
  }
  const env = a33GitEnvironment(runRoot);
  if (state.run_id !== options.runId || state.run_root !== runRoot || state.schema_version !== A33_SCHEMA_VERSION) throw new Error("run state mismatch");
  if (!exactKeys(marker, A33_MARKER_FIELDS) || JSON.stringify(marker) !== JSON.stringify(markerRecord(runRoot, options.runId, state.cleanup_nonce))) throw new Error("run identity mismatch");
  if (state.host !== realpathSync(join(runRoot, "host")) || !Array.isArray(state.operations)
    || state.internal_evidence_version !== A33_INTERNAL_EVIDENCE_VERSION || !Array.isArray(state.collector_records)
    || !Array.isArray(state.attempts) || !Array.isArray(state.attempt_sequence) || !Array.isArray(state.used_approvals) || !Array.isArray(state.registered)
    || typeof state.cleanup_nonce !== "string" || !/^[0-9a-f]{64}$/.test(state.cleanup_nonce)
    || !state.approval_snapshots || typeof state.approval_snapshots !== "object" || Array.isArray(state.approval_snapshots)
    || !state.consumed_approvals || typeof state.consumed_approvals !== "object" || Array.isArray(state.consumed_approvals)
    || !exactKeys(state.managed_install_attempt, ["command", "script", "opencode_home", "environment_controls", "environment_provenance", "status", "exit_code"]) || !Array.isArray(state.collector_install_paths)
    || JSON.stringify(state.attempt_sequence) !== JSON.stringify(state.attempts.map((attempt) => attempt?.evidence_id))) throw new Error("run state mismatch");
  if (JSON.stringify(state.git_environment) !== JSON.stringify(env) || !existsSync(env.GIT_CONFIG_VALUE_0)
    || !statSync(env.GIT_CONFIG_VALUE_0).isDirectory() || readdirSync(env.GIT_CONFIG_VALUE_0).length !== 0) throw new Error("run state mismatch");
  for (const id of ["a33-runtime-effective-profile-observed", "a33-runtime-install-observed"]) {
    const records = state.collector_records.filter((record) => record?.scenario_id === id);
    if (records.length !== 1 || ![["pass", 0], ["Unverified", 3], ["fail", 5]].some(([status, code]) => records[0].status === status && records[0].exit_code === code)
      || !Array.isArray(records[0].evidence_refs) || !records[0].evidence_refs.length) throw new Error("run state mismatch");
  }
  const expectedScript = join(state.project, "scripts", "install_opencode.sh");
  const expectedHome = join(runRoot, "opencode-home");
  const expectedCommand = ["/bin/bash", expectedScript, "--mode", "copy", "--opencode", "--aili-home", state.project, "--opencode-home", expectedHome, "--no-update"];
  const expectedInstallPaths = [expectedHome, join(runRoot, "home", ".agents", "skills")].filter((path) => existsSync(path));
  if (state.project !== realpathSync(resolve(options.project)) || state.managed_install_attempt.script !== expectedScript || state.managed_install_attempt.opencode_home !== expectedHome
    || JSON.stringify(state.managed_install_attempt.command) !== JSON.stringify(expectedCommand)
    || JSON.stringify(state.managed_install_attempt.environment_controls) !== JSON.stringify(A33_INSTALL_ENV_CONTROLS)
    || JSON.stringify(state.managed_install_attempt.environment_provenance) !== JSON.stringify({ HOME: env.HOME, XDG_CONFIG_HOME: env.XDG_CONFIG_HOME, XDG_DATA_HOME: env.XDG_DATA_HOME, XDG_CACHE_HOME: env.XDG_CACHE_HOME, TMPDIR: env.TMPDIR })
    || JSON.stringify(state.collector_install_paths) !== JSON.stringify(expectedInstallPaths)) throw new Error("run state mismatch");
  for (const operation of state.operations) {
    if (!exactKeys(operation, A33_OPERATION_FIELDS) || operation.operation_class !== "driver_fixture" || !validKey(operation.repo_key) || !validKey(operation.worktree_key)) throw new Error("run state mismatch");
    if (!isWithin(realpathSync(operation.source), runRoot) || operation.destination !== resolve(state.host, ".worktrees", operation.repo_key, operation.worktree_key)) throw new Error("run state mismatch");
    if (!validA33OperationSnapshot(state.current_operation_snapshots?.[operation.operation_id], state, operation)) throw new Error("run state mismatch");
  }
  if (JSON.stringify(Object.keys(state.consumed_approvals).sort()) !== JSON.stringify([...state.used_approvals].sort())) throw new Error("run state mismatch");
  for (const [approvalId, record] of Object.entries(state.consumed_approvals)) {
    const operation = state.operations.find((entry) => entry.operation_id === record?.approval?.operation_id);
    if (!approvalId || !operation || !exactKeys(record, ["approval", "snapshot"]) || !exactKeys(record.approval, A33_APPROVAL_FIELDS)
      || record.approval.approval_id !== approvalId || record.approval.status !== "valid"
      || !validA33OperationSnapshot(record.snapshot, state, operation)
      || JSON.stringify(approvalBinding(record.approval)) !== JSON.stringify(approvalBinding(record.snapshot))) throw new Error("run state mismatch");
  }
  for (const [approvalId, record] of Object.entries(state.approval_snapshots)) {
    const operation = state.operations.find((entry) => entry.operation_id === record?.approval_binding?.operation_id);
    if (!approvalId || !operation || !validApprovalSnapshot(record, { ...record.approval_binding, approval_id: approvalId, expiry: null, decision_ref: null, trusted_code_risk: null, status: "stale" }, state, operation)) throw new Error("run state mismatch");
  }
  return { runRoot, state, env };
}

function saveRun(runRoot, state) {
  writeFileSync(statePath(runRoot), `${JSON.stringify(state, null, 2)}\n`, "utf8");
}

function operationFor(state, id, kind) {
  const operation = state.operations.find((entry) => entry.operation_id === id && entry.kind === kind);
  if (!operation || !exactKeys(operation, A33_OPERATION_FIELDS)) throw new Error("operation mismatch");
  return operation;
}

function missingApproval(state, operation) {
  return {
    approval_id: null, run_id: state.run_id, operation_id: operation.operation_id, kind: operation.kind,
    operation_class: operation.operation_class, source: operation.source, destination: operation.destination,
    repo_key: operation.repo_key, worktree_key: operation.worktree_key, branch: operation.branch,
    base_ref: operation.base_ref, branch_mode: operation.branch_mode, reflog_policy: operation.reflog_policy,
    expiry: null, decision_ref: null, trusted_code_risk: null, status: "missing",
  };
}

function readApproval(options, state, operation) {
  if (options.approvalFd === undefined) return missingApproval(state, operation);
  try {
    const value = JSON.parse(readFileSync(Number(options.approvalFd), "utf8"));
    return value;
  } catch {
    return missingApproval(state, operation);
  }
}

export function validateA33Approval(approval, state, operation) {
  return classifyA33Approval(approval, state, operation);
}

function exactConsumedAddForRemove(approval, consumed, state, operation) {
  if (operation.kind !== "remove" || !exactKeys(consumed, ["approval", "snapshot"])
    || !exactKeys(consumed.approval, A33_APPROVAL_FIELDS) || JSON.stringify(consumed.approval) !== JSON.stringify(approval)
    || consumed.approval.kind !== "add" || consumed.approval.status !== "valid" || consumed.approval.run_id !== state.run_id) return false;
  const priorOperation = state.operations.find((entry) => entry.operation_id === consumed.approval.operation_id && entry.kind === "add");
  if (!priorOperation || !validA33OperationSnapshot(consumed.snapshot, state, priorOperation)) return false;
  const shared = ["operation_class", "source", "destination", "repo_key", "worktree_key", "branch", "base_ref", "branch_mode", "reflog_policy"];
  return shared.every((name) => approval[name] === priorOperation[name] && approval[name] === operation[name]);
}

export function classifyA33Approval(approval, state, operation) {
  if (!exactKeys(approval, A33_APPROVAL_FIELDS)) return { valid: false, category: "schema_omission", reason: "approval schema/field omission" };
  const invalid = (category, reason = category) => ({ valid: false, category, reason });
  const exactFields = ["run_id", "operation_id", "kind", "operation_class", "source", "destination", "repo_key", "worktree_key", "branch", "base_ref", "branch_mode", "reflog_policy"];
  if (approval.status === "missing") {
    const nullFields = ["approval_id", "expiry", "decision_ref", "trusted_code_risk"];
    const exactMissing = exactFields.every((name) => approval[name] === (name === "run_id" ? state.run_id : operation[name])) && nullFields.every((name) => approval[name] === null);
    return invalid(exactMissing ? "missing" : "schema_omission", exactMissing ? "approval missing" : "missing approval representation malformed");
  }
  const consumed = typeof approval.approval_id === "string" ? state.consumed_approvals?.[approval.approval_id] : undefined;
  if (state.used_approvals?.includes(approval.approval_id)) {
    if (!consumed || !exactKeys(consumed, ["approval", "snapshot"]) || JSON.stringify(consumed.approval) !== JSON.stringify(approval)) {
      return invalid("schema_omission", "approval reuse record missing or forged");
    }
    if (exactConsumedAddForRemove(approval, consumed, state, operation)) {
      return { ...invalid("reused", "consumed ADD approval cannot authorize REMOVE"), variant: "reused-add-for-remove" };
    }
  }
  if (approval.operation_id !== operation.operation_id) return { ...invalid("wrong_operation", "approval bound to another operation id"), variant: "wrong-operation-id" };
  if (approval.kind !== operation.kind || approval.run_id !== state.run_id) return { ...invalid("wrong_operation", "approval bound to another operation kind or run"), variant: "wrong-operation-kind" };
  if (approval.source !== operation.source) return invalid("wrong_source", "approval source mismatch");
  if (approval.destination !== operation.destination) return invalid("wrong_destination", "approval destination mismatch");
  if (approval.branch !== operation.branch || approval.branch_mode !== operation.branch_mode) return invalid("wrong_branch", "approval branch mismatch");
  if (approval.base_ref !== operation.base_ref || approval.reflog_policy !== operation.reflog_policy) return invalid("wrong_base_ref", "approval base-ref or reflog policy mismatch");
  if (!validKey(approval.repo_key) || approval.repo_key !== operation.repo_key) return invalid("repo_key_mismatch", "approval repository key mismatch");
  if (!validKey(approval.worktree_key) || approval.worktree_key !== operation.worktree_key
    || resolve(state.host, ".worktrees", approval.repo_key, approval.worktree_key) !== approval.destination) return invalid("worktree_key_mismatch", "approval worktree key/destination mismatch");
  if (operation.operation_class === "driver_fixture" && approval.operation_class === "real") return invalid("real_for_fixture", "real approval cannot authorize fixture operation");
  if (approval.operation_class !== operation.operation_class) return invalid("operation_class_mismatch", "approval operation class mismatch");
  if (approval.status === "declined") return invalid("declined", "approval declined");
  if (approval.status === "unavailable") return invalid("unavailable", "approval unavailable");
  if (approval.status === "stale") {
    const approvedSnapshot = state.approval_snapshots?.[approval.approval_id];
    const currentSnapshot = buildA33OperationSnapshot(state, operation);
    if (!validApprovalSnapshot(approvedSnapshot, approval, state, operation)) return invalid("schema_omission", "authoritative stale snapshot missing or forged");
    return JSON.stringify(approvedSnapshot.operation_snapshot) !== JSON.stringify(currentSnapshot)
      ? invalid("stale_snapshot_mismatch", "approval-bound operation/precondition snapshot is stale")
      : invalid("stale_unverified", "stale approval supplied without a provable bound snapshot mismatch");
  }
  if (approval.status === "expired") return invalid("expired", "approval expired");
  if (typeof approval.expiry !== "string" || !/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$/.test(approval.expiry)
    || Number.isNaN(Date.parse(approval.expiry)) || Date.parse(approval.expiry) <= Date.now()) return invalid("expired", "approval expired");
  if (state.used_approvals.includes(approval.approval_id)) return invalid("reused", "approval already consumed");
  if (approval.status === "mismatched") return invalid("mismatched", "approval mismatch without a more specific bound-field classification");
  if (approval.status !== "valid" || typeof approval.approval_id !== "string" || !approval.approval_id
    || typeof approval.decision_ref !== "string" || !approval.decision_ref) return invalid("schema_omission", "valid approval fields missing");
  if (operation.kind === "add" && approval.trusted_code_risk !== "accepted") {
    return invalid(approval.trusted_code_risk === "declined" ? "add_risk_declined" : "add_risk_unavailable", "ADD trusted-code risk not accepted");
  }
  if (operation.kind === "remove" && approval.trusted_code_risk !== "not_applicable") return invalid("remove_risk_invalid", "REMOVE risk marker invalid");
  return { valid: true, category: "valid", reason: "approval valid" };
}

export function classifyA33RemovalInventory(input) {
  const identity = input?.identity;
  const invalid = () => ({ clean: false, classes: ["invalid"], primary_class: "invalid", evidence_by_class: {}, contradiction: true });
  if (!input || typeof input !== "object" || Array.isArray(input)
    || Object.keys(input).some((name) => !A33_REMOVAL_INVENTORY_INPUT_FIELDS.has(name))
    || !validateA33Identity(identity)) return invalid();
  if (input.locked !== undefined && typeof input.locked !== "boolean") return invalid();
  for (const name of ["expected_source", "observed_source", "expected_path"]) {
    if (input[name] !== undefined && (typeof input[name] !== "string" || !input[name])) return invalid();
  }
  for (const name of ["expected_source", "observed_source", "expected_path"]) {
    if (input[name] !== undefined && (!isAbsolute(input[name]) || resolve(input[name]) !== input[name])) return invalid();
  }
  if (input.expected_membership !== undefined && !["main", "linked"].includes(input.expected_membership)) return invalid();
  for (const name of ["allowlisted_ephemeral_artifacts", "visible_files"]) {
    if (input[name] !== undefined && (!Array.isArray(input[name]) || input[name].some((path) => !validA33RelativePath(path))
      || JSON.stringify(input[name]) !== JSON.stringify([...new Set(input[name])].sort()))) return invalid();
  }
  if (input.raw_inventory_observation !== undefined
    && !validA33RawRemovalObservation(input.raw_inventory_observation, identity, input)) return invalid();
  const classes = [];
  const evidenceByClass = {};
  let contradiction = false;
  if (identity.identity_state === "absent") classes.push("missing");
  else {
    if (identity.dirty_state.untracked_count !== identity.untracked_files.length
      || identity.dirty_state.ignored_count !== identity.ignored_files.length) return invalid();
    if (identity.dirty_state?.tracked_modified) classes.push("tracked_modified");
    if (identity.dirty_state?.tracked_deleted) classes.push("tracked_deleted");
    const assigned = new Set(identity.tracked_files ?? []);
    for (const [name, paths] of [["untracked", identity.untracked_files], ["ignored", identity.ignored_files], ["artifact", identity.artifact_files], ["unknown", identity.unknown_files]]) {
      const unique = [];
      for (const path of paths ?? []) {
        if (assigned.has(path)) contradiction = true;
        else { assigned.add(path); unique.push(path); }
      }
      evidenceByClass[name] = unique;
      if (unique.length) classes.push(name);
    }
    if (input.locked === true) classes.push("locked");
    if (input.expected_source && input.observed_source !== input.expected_source) classes.push("wrong_source");
    if (input.expected_path && identity.declared_root !== input.expected_path) classes.push("wrong_path");
    if (input.expected_membership && identity.worktree_membership !== input.expected_membership) classes.push("wrong_membership");
    const allowlisted = new Set(input.allowlisted_ephemeral_artifacts ?? []);
    const userVisible = sortedUniqueRelative((input.visible_files ?? []).filter((path) => !assigned.has(path) && !allowlisted.has(path)));
    evidenceByClass.user_visible = userVisible;
    if (userVisible.length) classes.push("user_visible");
  }
  return { clean: classes.length === 0 && !contradiction, classes, primary_class: classes[0] ?? "clean", evidence_by_class: evidenceByClass, contradiction };
}

function rawRemovalObservation(operation, targetIdentity, sourceIdentity, env) {
  const targetPresent = targetIdentity.identity_state === "populated";
  const statusRecords = targetPresent
    ? gitNul(operation.destination, ["--no-optional-locks", "status", "--porcelain=v2", "-z", "--untracked-files=all", "--ignored"], env)
    : [];
  const trackedFiles = targetPresent ? sortedUniqueRelative(gitNul(operation.destination, ["ls-files", "-z"], env)) : [];
  const observation = {
    schema_version: A33_INTERNAL_EVIDENCE_VERSION, target_present: targetPresent,
    status_porcelain_v2: statusRecords,
    worktree_porcelain: gitNul(operation.source, ["worktree", "list", "--porcelain", "-z"], env),
    tracked_files: trackedFiles, artifact_files: [], unknown_files: [],
    visible_files: targetPresent ? (listTree(operation.destination) ?? []) : [],
    allowlisted_ephemeral_artifacts: targetPresent ? [".git"] : [],
    expected_source: sourceIdentity.git_common_dir, observed_source: targetIdentity.git_common_dir,
    expected_path: canonicalDeclared(operation.destination), observed_path: targetIdentity.declared_root,
    expected_membership: "linked", observed_membership: targetIdentity.worktree_membership,
  };
  if (!exactKeys(observation, A33_RAW_INVENTORY_FIELDS)) throw new Error("raw inventory evidence malformed");
  return observation;
}

function exactUnchangedEvidence(record) {
  const stateSnapshotsUnchanged = record.before_state === undefined && record.after_state === undefined
    || record.before_state !== undefined && record.after_state !== undefined
      && JSON.stringify(record.before_state) === JSON.stringify(record.after_state);
  return stateSnapshotsUnchanged && validateDelta(record.expected_delta) && validateDelta(record.observed_delta)
    && JSON.stringify(record.expected_delta) === JSON.stringify(record.observed_delta)
    && A33_DELTA_FIELDS.every((name) => record.expected_delta[name].change === "unchanged"
      && record.observed_delta[name].change === "unchanged"
      && JSON.stringify(record.expected_delta[name].before) === JSON.stringify(record.expected_delta[name].after)
      && JSON.stringify(record.observed_delta[name].before) === JSON.stringify(record.observed_delta[name].after));
}

function compatibleA33EvidenceWithoutScenario(metadata, record) {
  const recordMetadata = A33_RUNTIME_SCENARIO_REGISTRY.find((entry) => entry.id === record?.scenario_id);
  return record && record.schema_version === A33_INTERNAL_EVIDENCE_VERSION && record.family === metadata.family
    && record.operation_kind === metadata.operation_kind && record.attachment_selector === metadata.attachment_selector
    && record.approval_variant === metadata.approval_variant
    && JSON.stringify(recordMetadata?.prerequisites) === JSON.stringify(metadata.prerequisites)
    && recordMetadata?.expected_transition === metadata.expected_transition
    && metadata.required_evidence_types.every((type) => record.evidence_types?.includes(type))
    && recordMetadata?.cleanup_expectation === metadata.cleanup_expectation;
}

function compatibleA33Evidence(metadata, record) {
  return compatibleA33EvidenceWithoutScenario(metadata, record) && record.scenario_id === metadata.id;
}

function evidenceOperationBinding(attempt) {
  const operation = attempt.result.operation;
  return {
    attempt_id: attempt.evidence_id, operation_id: operation.operation_id, operation_kind: operation.kind,
    attachment_selector: operationAttachmentSelector(operation),
  };
}

function expectedOperationCoverage(metadata, operations) {
  if (!Array.isArray(operations) || operations.length === 0) return null;
  if (metadata.id === "a33-runtime-approval-declined-unavailable") {
    const existingAdd = operations.filter((operation) => operation.kind === "add" && operationAttachmentSelector(operation) === "existing");
    return existingAdd.flatMap((operation) => [operation, operation]).map((operation) => ({
      operation_id: operation.operation_id, operation_kind: operation.kind, attachment_selector: operationAttachmentSelector(operation),
    })).sort((left, right) => left.operation_id.localeCompare(right.operation_id));
  }
  if (metadata.id === "a33-runtime-key-mismatch-zero-effect") {
    const existingPair = operations.filter((operation) => operationAttachmentSelector(operation) === "existing");
    return existingPair.flatMap((operation) => [operation, operation]).map((operation) => ({
      operation_id: operation.operation_id, operation_kind: operation.kind, attachment_selector: operationAttachmentSelector(operation),
    })).sort((left, right) => left.operation_id.localeCompare(right.operation_id));
  }
  let expected = [];
  if (metadata.operation_kind !== null) expected = operations.filter((operation) => operation.kind === metadata.operation_kind);
  else if (["a33-unrelated-common-dir-preserved", "a33-runtime-identity-transition-schema", "a33-common-dir-identity-change-block"].includes(metadata.id)) expected = [...operations];
  else return [];
  if (metadata.attachment_selector !== "all-attachments") {
    expected = expected.filter((operation) => operationAttachmentSelector(operation) === metadata.attachment_selector);
  }
  return expected.map((operation) => ({ operation_id: operation.operation_id, operation_kind: operation.kind, attachment_selector: operationAttachmentSelector(operation) }))
    .sort((left, right) => left.operation_id.localeCompare(right.operation_id));
}

export function validateA33EvidenceBindings(metadata, record, operations = [], attempts = []) {
  const bindings = record?.operation_bindings;
  if (!Array.isArray(bindings)) return { status: "fail", exit_code: 5, reason: "operation bindings missing" };
  if (!Array.isArray(attempts)) return { status: "fail", exit_code: 5, reason: "authoritative attempt index unavailable" };
  if (new Set(bindings.map((binding) => binding?.attempt_id)).size !== bindings.length) return { status: "fail", exit_code: 5, reason: "duplicate operation attempt binding" };
  const attemptsById = new Map();
  for (const attempt of attempts) {
    const indexed = attemptsById.get(attempt?.evidence_id) ?? [];
    indexed.push(attempt);
    attemptsById.set(attempt?.evidence_id, indexed);
  }
  for (const binding of bindings) {
    if (!exactKeys(binding, ["attempt_id", "operation_id", "operation_kind", "attachment_selector"])
      || typeof binding.attempt_id !== "string" || !binding.attempt_id || typeof binding.operation_id !== "string" || !binding.operation_id
      || !["add", "remove"].includes(binding.operation_kind) || !A33_ATTACHMENT_SELECTORS.has(binding.attachment_selector)) {
      return { status: "fail", exit_code: 5, reason: "operation binding malformed" };
    }
    const indexedAttempts = attemptsById.get(binding.attempt_id) ?? [];
    if (indexedAttempts.length !== 1) {
      return { status: "fail", exit_code: 5, reason: indexedAttempts.length === 0
        ? "operation binding references unknown attempt" : "operation binding attempt id is not unique" };
    }
    let derived;
    try {
      derived = evidenceOperationBinding(indexedAttempts[0]);
    } catch {
      return { status: "fail", exit_code: 5, reason: "operation binding attempt malformed" };
    }
    if (["attempt_id", "operation_id", "operation_kind", "attachment_selector"].some((name) => derived[name] !== binding[name])) {
      return { status: "fail", exit_code: 5, reason: "attempt id operation binding mismatch" };
    }
    const operation = operations.find((candidate) => candidate.operation_id === binding.operation_id);
    if (!operation) return operations.length === 0
      ? { status: "Unverified", exit_code: 3, reason: "operation binding context unavailable" }
      : { status: "fail", exit_code: 5, reason: "operation binding references unknown operation" };
    if (operation.kind !== binding.operation_kind || operationAttachmentSelector(operation) !== binding.attachment_selector) {
      return { status: "fail", exit_code: 5, reason: "swapped operation id or attachment selector" };
    }
  }
  if (record.operation_id !== null && (bindings.length !== 1 || bindings[0].operation_id !== record.operation_id)) {
    return { status: "fail", exit_code: 5, reason: "singular operation id binding mismatch" };
  }
  const expected = expectedOperationCoverage(metadata, operations);
  if (expected === null) return bindings.length === 0 ? { status: "pass", exit_code: 0, reason: null }
    : { status: "Unverified", exit_code: 3, reason: "operation coverage context unavailable" };
  if (expected.length > 0) {
    const actual = bindings.map(({ operation_id, operation_kind, attachment_selector }) => ({ operation_id, operation_kind, attachment_selector }))
      .sort((left, right) => left.operation_id.localeCompare(right.operation_id));
    if (JSON.stringify(actual) !== JSON.stringify(expected)) return { status: "fail", exit_code: 5, reason: "missing, duplicate, or extra attachment operation evidence" };
  }
  return { status: "pass", exit_code: 0, reason: null };
}

export function evaluateA33SemanticEvidence(metadata, record, operations = [], attempts = []) {
  if (!compatibleA33Evidence(metadata, record) || record.contradiction === true) return { status: "fail", exit_code: 5, reason: "wrong-bound or contradictory evidence" };
  const binding = validateA33EvidenceBindings(metadata, record, operations, attempts);
  if (binding.status !== "pass") return binding;
  const observation = record.semantic_observation;
  if (observation !== null && observation !== undefined) {
    if (!exactKeys(observation, ["kind", "expected", "observed"])) return { status: "fail", exit_code: 5, reason: "semantic observation malformed" };
    if (["delta", "ref", "reflog"].includes(observation.kind)) {
      if (!validateDelta(observation.expected) || !validateDelta(observation.observed)) return { status: "fail", exit_code: 5, reason: "mutated delta schema rejected" };
      return JSON.stringify(observation.expected) !== JSON.stringify(observation.observed)
        ? { status: "fail", exit_code: 5, reason: `mutated ${observation.kind} semantics rejected` }
        : { status: "Unverified", exit_code: 3, reason: `no ${observation.kind} semantic violation proven` };
    }
    if (["delta-set", "ref-set", "reflog-set"].includes(observation.kind)) {
      if (!Array.isArray(observation.expected) || !Array.isArray(observation.observed)
        || observation.expected.length === 0 || observation.expected.length !== observation.observed.length
        || !observation.expected.every(validateDelta) || !observation.observed.every(validateDelta)) {
        return { status: "fail", exit_code: 5, reason: "mutated operation-set delta schema rejected" };
      }
      return observation.expected.every((expected, index) => JSON.stringify(expected) !== JSON.stringify(observation.observed[index]))
        ? { status: "fail", exit_code: 5, reason: `mutated ${observation.kind} semantics rejected` }
        : { status: "Unverified", exit_code: 3, reason: `incomplete ${observation.kind} semantic rejection` };
    }
    if (observation.kind === "identity") {
      return validateA33Identity(observation.expected) && !validateA33Identity(observation.observed)
        ? { status: "fail", exit_code: 5, reason: "mutated identity semantics rejected" }
        : { status: "Unverified", exit_code: 3, reason: "no identity semantic violation proven" };
    }
    if (["cleanup", "effect"].includes(observation.kind)) {
      return JSON.stringify(observation.expected) !== JSON.stringify(observation.observed)
        ? { status: "fail", exit_code: 5, reason: `mutated ${observation.kind} semantics rejected` }
        : { status: "Unverified", exit_code: 3, reason: `no ${observation.kind} semantic violation proven` };
    }
    return { status: "Unverified", exit_code: 3, reason: "semantic mutation kind unsupported" };
  }
  if (metadata.expected_outcome === "blocked") {
    const pass = record.status === "blocked" && record.exit_code === 3 && record.effect_started === false && exactUnchangedEvidence(record);
    return pass ? { status: "pass", exit_code: 0, reason: null } : { status: "fail", exit_code: 5, reason: "negative outcome/effect/unchanged-state mismatch" };
  }
  if (metadata.expected_outcome === "pass") {
    if ((record.expected_delta !== null || record.observed_delta !== null)
      && (!validateDelta(record.expected_delta) || !validateDelta(record.observed_delta)
        || JSON.stringify(record.expected_delta) !== JSON.stringify(record.observed_delta))) {
      return { status: "fail", exit_code: 5, reason: "positive expected/observed delta mismatch" };
    }
    if (record.status === "pass" && record.exit_code === 0 && record.effect_started !== false) return { status: "pass", exit_code: 0, reason: null };
    return record.status === "Unverified" && record.exit_code === 3
      ? { status: "Unverified", exit_code: 3, reason: "mandatory positive evidence unavailable" }
      : { status: "fail", exit_code: 5, reason: "positive evidence contradiction" };
  }
  if (metadata.expected_outcome === "unverified") {
    return record.status === "Unverified" && record.exit_code === 3
      ? { status: "pass", exit_code: 0, reason: null }
      : { status: "fail", exit_code: 5, reason: "partitioned Unverified outcome mismatch" };
  }
  return { status: "Unverified", exit_code: 3, reason: "no semantic rejection observation available" };
}

export function classifyA33RuntimeEvidence(metadata, records, operations = [], attempts = []) {
  if (!exactKeys(metadata, A33_SCENARIO_FIELDS) || !Array.isArray(records)) return { status: "fail", exit_code: 5, reason: "scenario/evidence schema malformed", record: null };
  const candidates = records.filter((record) => compatibleA33Evidence(metadata, record));
  if (records.some((record) => record?.scenario_id !== metadata.id && compatibleA33EvidenceWithoutScenario(metadata, record))) {
    return { status: "fail", exit_code: 5, reason: "cross-scenario compatible evidence", record: null };
  }
  if (candidates.length > 1) return { status: "fail", exit_code: 5, reason: "duplicate or ambiguous compatible evidence", record: null };
  if (candidates.length === 0) {
    const conflicting = records.some((record) => record?.scenario_id === metadata.id || compatibleA33EvidenceWithoutScenario(metadata, record));
    return conflicting
      ? { status: "fail", exit_code: 5, reason: "cross-operation or incompatible evidence", record: null }
      : { status: "Unverified", exit_code: 3, reason: "mandatory compatible evidence unavailable", record: null };
  }
  const record = candidates[0];
  const observed = evaluateA33SemanticEvidence(metadata, record, operations, attempts);
  if (metadata.expected_outcome === "fail") {
    const binding = validateA33EvidenceBindings(metadata, record, operations, attempts);
    if (binding.status === "fail") return { status: "fail", exit_code: 5, reason: binding.reason, record };
    return binding.status === "pass" && observed.status === "fail" && observed.exit_code === 5
      && record.semantic_rejection?.status === "fail" && record.semantic_rejection?.exit_code === 5
      ? { status: "pass", exit_code: 0, reason: null, record }
      : { status: "Unverified", exit_code: 3, reason: observed.reason ?? "semantic rejection unavailable", record };
  }
  return { ...observed, record };
}

function operationResult(command, state, operation, approval, status, exitCode, effectStarted, expectedDelta = null, observedDelta = null, evidence = [], unverified = []) {
  return {
    schema_version: A33_SCHEMA_VERSION, command, status, exit_code: exitCode, run_id: state.run_id,
    operation, approval, effect_started: effectStarted, expected_delta: expectedDelta, observed_delta: observedDelta,
    evidence_refs: evidence, unverified,
  };
}

function operationAttachmentSelector(operation) {
  if (operation.branch_mode === "existing") return "existing";
  return operation.reflog_policy === "enabled" ? "create-enabled" : "create-disabled";
}

function negativeScenarioIds(decision, operation, approval) {
  const byCategory = new Map([
    ["missing", ["a33-runtime-approval-missing-zero-effect", "a33-runtime-missing-approval-null-fields"]],
    ["declined", []], ["unavailable", []],
    ["stale_snapshot_mismatch", ["a33-runtime-approval-stale-zero-effect"]], ["expired", ["a33-runtime-approval-expired-zero-effect"]],
    ["mismatched", ["a33-runtime-approval-mismatched-zero-effect"]],
    ["wrong_source", ["a33-runtime-approval-wrong-source-zero-effect"]], ["wrong_destination", ["a33-runtime-approval-wrong-destination-zero-effect"]],
    ["wrong_branch", ["a33-runtime-approval-wrong-branch-zero-effect"]], ["wrong_base_ref", ["a33-runtime-approval-wrong-ref-zero-effect"]],
    ["repo_key_mismatch", []], ["worktree_key_mismatch", []],
    ["operation_class_mismatch", ["a33-runtime-operation-class-mismatch-zero-effect"]],
    ["add_risk_declined", ["a33-runtime-add-trusted-code-risk-declined-zero-effect"]],
    ["add_risk_unavailable", ["a33-runtime-add-trusted-code-risk-unavailable-zero-effect"]],
  ]);
  if (decision.category === "real_for_fixture") return [operation.kind === "add" ? "a33-runtime-fixture-add-real-approval-zero-effect" : "a33-runtime-fixture-remove-real-approval-zero-effect"];
  if (decision.category === "reused") {
    if (operation.kind === "remove" && approval.kind === "add") return ["a33-runtime-add-approval-reused-real-remove-zero-effect"];
    return [operation.kind === "add" ? "a33-runtime-add-approval-reused-zero-effect" : "a33-runtime-remove-approval-reused-zero-effect"];
  }
  if (decision.category === "wrong_operation") {
    if (operation.kind === "remove") return ["a33-runtime-remove-approval-wrong-zero-effect"];
    return [decision.variant === "wrong-operation-kind" ? "a33-runtime-approval-other-operation-zero-effect" : "a33-runtime-add-approval-wrong-zero-effect"];
  }
  if (decision.category === "schema_omission") return [operation.kind === "add" ? "a33-runtime-add-approval-wrong-zero-effect" : "a33-runtime-remove-approval-wrong-zero-effect"];
  return byCategory.get(decision.category) ?? [];
}

function recordOperationAttempt(state, decision, result, identities, rawEvidence, scenarioIds = []) {
  const operation = result.operation;
  const attachmentSelector = operationAttachmentSelector(operation);
  const attemptId = `attempt:${state.attempts.length + 1}`;
  const attempt = {
    evidence_id: attemptId, sequence: state.attempts.length + 1,
    category: decision.category, reason: decision.reason, scenario_ids: [...scenarioIds],
    operation_kind: operation.kind, operation_id: operation.operation_id, attachment_selector: attachmentSelector,
    approval_variant: decision.category, result, ...identities,
    raw_admin_before: rawEvidence.raw_admin_before, raw_admin_after: rawEvidence.raw_admin_after,
    raw_inventory_observation: rawEvidence.raw_inventory_observation ?? null, evidence_records: [],
  };
  const registry = new Map(A33_RUNTIME_SCENARIO_REGISTRY.map((entry) => [entry.id, entry]));
  for (const scenarioId of scenarioIds) {
    const metadata = registry.get(scenarioId);
    if (!metadata) throw new Error("scenario registry mismatch");
    attempt.evidence_records.push(internalEvidence(scenarioId, metadata.family, {
      evidence_id: `${attemptId}:${scenarioId}`, source: "operation", operation_id: operation.operation_id,
      operation_kind: metadata.operation_kind, attachment_selector: metadata.attachment_selector,
      approval_variant: metadata.approval_variant, status: result.status, exit_code: result.exit_code,
      effect_started: result.effect_started, expected_delta: result.expected_delta, observed_delta: result.observed_delta,
      evidence_types: metadata.required_evidence_types, evidence_refs: result.evidence_refs,
      operation_bindings: [evidenceOperationBinding(attempt)],
      attempt: null, cleanup_state: metadata.cleanup_expectation === "retain" ? "retained" : metadata.cleanup_expectation,
    }));
  }
  state.attempts.push(attempt);
  state.attempt_sequence.push(attemptId);
  return attempt;
}

export function validateA33OperationResult(result) {
  return exactKeys(result, A33_OPERATION_RESULT_FIELDS) && result.schema_version === A33_SCHEMA_VERSION
    && ["runtime-add", "runtime-remove"].includes(result.command) && ["pass", "blocked", "Unverified", "fail"].includes(result.status)
    && [0, 3, 5].includes(result.exit_code) && exactKeys(result.operation, A33_OPERATION_FIELDS)
    && exactKeys(result.approval, A33_APPROVAL_FIELDS) && typeof result.effect_started === "boolean"
    && (result.expected_delta === null || validateDelta(result.expected_delta))
    && (result.observed_delta === null || validateDelta(result.observed_delta))
    && Array.isArray(result.evidence_refs) && Array.isArray(result.unverified);
}

function prepareGitRepository(path, env, label) {
  mkdirSync(path, { recursive: true });
  git("git", ["init", "--quiet"], path, env);
  writeFileSync(join(path, "fixture.txt"), `${label}\n`, "utf8");
  git("git", ["add", "fixture.txt"], path, env);
  git("git", ["commit", "--quiet", "-m", `${label} fixture`], path, env);
}

function internalEvidence(scenarioId, family, values = {}) {
  return {
    schema_version: A33_INTERNAL_EVIDENCE_VERSION, evidence_id: values.evidence_id ?? `collector:${scenarioId}`,
    scenario_id: scenarioId, family, source: values.source ?? "collector", operation_id: values.operation_id ?? null,
    operation_kind: values.operation_kind ?? null, attachment_selector: values.attachment_selector,
    approval_variant: values.approval_variant ?? "none", status: values.status, exit_code: values.exit_code,
    effect_started: values.effect_started ?? null, before_state: values.before_state, after_state: values.after_state,
    expected_delta: values.expected_delta ?? null, observed_delta: values.observed_delta ?? null,
    evidence_types: values.evidence_types ?? [], evidence_refs: values.evidence_refs ?? [], contradiction: values.contradiction ?? false,
    semantic_observation: values.semantic_observation ?? null, semantic_rejection: values.semantic_rejection ?? null,
    operation_bindings: values.operation_bindings ?? [], attempt: values.attempt ?? null, cleanup_state: values.cleanup_state ?? null,
  };
}

function parseManagedFrontmatter(text) {
  const lines = text.replaceAll("\r\n", "\n").split("\n");
  if (lines[0] !== "---") throw new Error("managed frontmatter malformed");
  const end = lines.indexOf("---", 1);
  const permissionLine = lines.indexOf("permission:", 1);
  const modeLine = lines.slice(1, end).filter((line) => line.startsWith("mode:"));
  if (end < 0 || permissionLine < 1 || permissionLine >= end || modeLine.length !== 1) throw new Error("managed frontmatter malformed");
  const mode = modeLine[0].slice(5).trim();
  if (!new Set(["primary", "subagent"]).has(mode)) throw new Error("managed frontmatter malformed");
  const stack = [{ indent: -1, path: ["permission"] }];
  const permissions = [];
  for (const line of lines.slice(permissionLine + 1, end)) {
    if (!line.trim()) continue;
    const indent = line.match(/^ */)[0].length;
    if (indent === 0) break;
    if (indent % 2 || line.includes("\t")) throw new Error("managed permission malformed");
    const match = line.match(/^\s*(?:"((?:\\.|[^"])*)"|'([^']*)'|([^:]+)):\s*(.*)$/);
    if (!match) throw new Error("managed permission malformed");
    const key = match[1] !== undefined ? JSON.parse(`"${match[1]}"`) : match[2] !== undefined ? match[2] : match[3].trim();
    while (stack.length > 1 && stack.at(-1).indent >= indent) stack.pop();
    const path = [...stack.at(-1).path, key];
    const raw = match[4].trim();
    if (!raw) stack.push({ indent, path });
    else {
      const value = raw.startsWith('"') ? JSON.parse(raw) : raw.startsWith("'") && raw.endsWith("'") ? raw.slice(1, -1) : raw;
      if (!["allow", "ask", "deny"].includes(value)) throw new Error("managed permission malformed");
      permissions.push({ path: path.join("."), value });
    }
  }
  if (!permissions.length || new Set(permissions.map(({ path }) => path)).size !== permissions.length) throw new Error("managed permission malformed");
  return { mode, permissions };
}

function managedAgentSources(project) {
  const manifestPath = join(project, "manifests", "rose-aili.components.json");
  if (realpathSync(manifestPath) !== manifestPath || lstatSync(manifestPath).isSymbolicLink() || !statSync(manifestPath).isFile()) throw new Error("managed manifest path mismatch");
  const manifest = JSON.parse(readFileSync(manifestPath, "utf8"));
  const entries = manifest?.components?.agents;
  const fields = ["name", "path", "required", "defaultInstalled", "repositoryManaged"];
  if (manifest?.name !== "rose-aili" || manifest?.schemaVersion !== 1 || !Array.isArray(entries) || entries.length !== 20) throw new Error("managed manifest malformed");
  const byPath = new Map();
  for (const entry of entries) {
    if (!exactKeys(entry, fields) || typeof entry.name !== "string" || entry.path !== `agents/${entry.name}.md`
      || entry.required !== true || entry.defaultInstalled !== false || entry.repositoryManaged !== true || byPath.has(entry.path)) throw new Error("managed manifest malformed");
    byPath.set(entry.path, entry);
  }
  if (byPath.size !== A33_MANAGED_AGENT_PATHS.length || A33_MANAGED_AGENT_PATHS.some((path) => !byPath.has(path))) throw new Error("managed manifest inventory mismatch");
  const agents = A33_MANAGED_AGENT_PATHS.map((path) => {
    const entry = byPath.get(path);
    const canonicalPath = join(project, entry.path);
    if (realpathSync(canonicalPath) !== canonicalPath || lstatSync(canonicalPath).isSymbolicLink() || !statSync(canonicalPath).isFile()) throw new Error("managed canonical path mismatch");
    const bytes = readFileSync(canonicalPath);
    return { name: entry.name, canonical_path: canonicalPath, bytes, parsed: parseManagedFrontmatter(bytes.toString("utf8")) };
  });
  return { manifest_path: manifestPath, manifest_agent_paths: entries.map(({ path }) => path), canonical_agent_paths: [...A33_MANAGED_AGENT_PATHS], agents };
}

function exactInstallerSummary(summary, project, opencodeHome) {
  return exactKeys(summary, ["mode", "scope", "runtime", "aili_home", "opencode_home", "dry_run", "no_update", "retired_skill_reconciliation"])
    && summary.mode === "copy" && summary.scope === "opencode" && ["linux", "macos", "wsl"].includes(summary.runtime)
    && summary.aili_home === project && summary.opencode_home === opencodeHome
    && summary.dry_run === "false" && summary.no_update === "true" && Array.isArray(summary.retired_skill_reconciliation);
}

function canonicalCopyInstaller(project) {
  const script = join(project, "scripts", "install_opencode.sh");
  if (!existsSync("/bin/bash") || !existsSync(script)) return null;
  try {
    const metadata = statSync(script);
    const text = readFileSync(script, "utf8");
    const markers = ["--no-update)", 'NO_UPDATE="true"', '[ "$NO_UPDATE" = "true" ]', "Skipping repository update:", "copy)\n    ensure_repo\n    install_entries copy_entry"];
    if (realpathSync(script) !== script || !isWithin(script, project) || !metadata.isFile() || !(metadata.mode & 0o111)
      || markers.some((marker) => !text.includes(marker)) || /codegraph|openspec|npx\s|npm\s+install/i.test(text)) return null;
    return script;
  } catch {
    return null;
  }
}

function observeManagedProfile(project, runRoot, opencodeHome, command, summary) {
  const canonical = managedAgentSources(project);
  if (realpathSync(opencodeHome) !== opencodeHome || lstatSync(opencodeHome).isSymbolicLink() || !statSync(opencodeHome).isDirectory() || !isWithin(opencodeHome, runRoot)) throw new Error("managed install path mismatch");
  const agentsRoot = join(opencodeHome, "agents");
  if (realpathSync(agentsRoot) !== agentsRoot || lstatSync(agentsRoot).isSymbolicLink() || !statSync(agentsRoot).isDirectory()) throw new Error("managed install path mismatch");
  const disk = readdirSync(agentsRoot, { withFileTypes: true });
  if (disk.some((entry) => !entry.isFile() || !entry.name.endsWith(".md"))) throw new Error("managed install inventory mismatch");
  const diskNames = disk.map((entry) => entry.name.slice(0, -3));
  const expectedNames = canonical.agents.map(({ name }) => name);
  if (new Set(diskNames).size !== expectedNames.length || expectedNames.some((name) => !diskNames.includes(name))) throw new Error("managed install inventory mismatch");
  const installedNames = [...expectedNames];
  const agents = canonical.agents.map((source) => {
    const installedPath = join(agentsRoot, `${source.name}.md`);
    if (lstatSync(installedPath).isSymbolicLink() || realpathSync(installedPath) !== installedPath || !statSync(installedPath).isFile() || !isWithin(installedPath, opencodeHome)) throw new Error("managed install path mismatch");
    const bytes = readFileSync(installedPath);
    if (!source.bytes.equals(bytes)) throw new Error("managed install byte mismatch");
    const parsed = parseManagedFrontmatter(bytes.toString("utf8"));
    if (JSON.stringify(parsed) !== JSON.stringify(source.parsed)) throw new Error("managed permission mismatch");
    const permissions = new Map(parsed.permissions.map((entry) => [entry.path, entry.value]));
    if (source.name === "rose" ? parsed.mode !== "primary" : parsed.mode !== "subagent" || permissions.get("permission.external_directory") !== "deny" || permissions.get("permission.task") !== "deny") throw new Error("managed permission broadened");
    return {
      name: source.name, canonical_path: source.canonical_path, installed_path: installedPath,
      install_mode: "copy", exact_byte_equality: true, mode: parsed.mode, permissions: parsed.permissions,
      unexpected_allow_ask: [],
      provenance: [`canonical:${source.canonical_path}`, `installed:${installedPath}`, ...parsed.permissions.map((entry) => `permission:${entry.path}=${entry.value}`)],
    };
  });
  const configRoot = join(runRoot, "home", ".config");
  const configEntries = existsSync(configRoot) ? listTree(configRoot) ?? [] : [];
  if (configEntries.length || existsSync(join(opencodeHome, "opencode.json")) || existsSync(join(opencodeHome, "opencode.jsonc"))
    || JSON.stringify(readdirSync(opencodeHome).sort()) !== JSON.stringify(["AGENTS.md", "agents", "commands", "skills"])) throw new Error("managed override layer unexpected");
  return {
    schema_version: A33_INTERNAL_EVIDENCE_VERSION, command, installer_summary: summary, manifest_path: canonical.manifest_path, manifest_regular_nonsymlink: true,
    environment_controls: { ...A33_INSTALL_ENV_CONTROLS },
    environment_provenance: { HOME: join(runRoot, "home"), XDG_CONFIG_HOME: join(runRoot, "home", ".config"), XDG_DATA_HOME: join(runRoot, "home", ".local", "share"), XDG_CACHE_HOME: join(runRoot, "home", ".cache"), TMPDIR: join(runRoot, "tmp") },
    manifest_agent_paths: canonical.manifest_agent_paths, canonical_agent_paths: canonical.canonical_agent_paths,
    aili_home: project, opencode_home: opencodeHome, canonical_agent_names: expectedNames, installed_agent_names: installedNames,
    agents, no_additional_override_layer: true, isolated_config_entries: configEntries,
    managed_subagents_restricted: agents.filter(({ name }) => name !== "rose").length === 19,
    rose_distinction: agents.find(({ name }) => name === "rose"), builtins_inferred: false, uv006_resolved: false,
  };
}

function collectManagedProfile(project, runRoot, env, registry) {
  const script = join(project, "scripts", "install_opencode.sh");
  const opencodeHome = join(runRoot, "opencode-home");
  const args = [script, "--mode", "copy", "--opencode", "--aili-home", project, "--opencode-home", opencodeHome, "--no-update"];
  const command = ["/bin/bash", ...args];
  const environmentControls = { ...A33_INSTALL_ENV_CONTROLS };
  const attempt = {
    command, script, opencode_home: opencodeHome, environment_controls: environmentControls,
    environment_provenance: { HOME: env.HOME, XDG_CONFIG_HOME: env.XDG_CONFIG_HOME, XDG_DATA_HOME: env.XDG_DATA_HOME, XDG_CACHE_HOME: env.XDG_CACHE_HOME, TMPDIR: env.TMPDIR },
    status: "unavailable", exit_code: null,
  };
  const records = (status, code, evidence, beforeState, contradiction = false) => ["a33-runtime-effective-profile-observed", "a33-runtime-install-observed"].map((id) => internalEvidence(id, registry.get(id).family, {
    attachment_selector: "isolated-opencode", status, exit_code: code, evidence_types: registry.get(id).required_evidence_types,
    evidence_refs: [evidence], before_state: beforeState, contradiction,
  }));
  const installPaths = () => [opencodeHome, join(runRoot, "home", ".agents", "skills")].filter((path) => existsSync(path));
  if (![...Object.values(attempt.environment_provenance), opencodeHome].every((path) => isWithin(path, runRoot))) {
    return { attempt: { ...attempt, status: "invalid-source" }, install_paths: installPaths(), records: records("fail", 5, "collector:isolated install path mismatch", attempt, true) };
  }
  try {
    managedAgentSources(project);
  } catch (error) {
    return { attempt: { ...attempt, status: "invalid-source" }, install_paths: installPaths(), records: records("fail", 5, `collector:${String(error?.message ?? error)}`, attempt, true) };
  }
  if (canonicalCopyInstaller(project) !== script) return { attempt, install_paths: installPaths(), records: records("Unverified", 3, "missing-collector:canonical installer unavailable", attempt) };
  try {
    const invoked = run("/bin/bash", args, { cwd: project, env, timeout: 60_000 });
    attempt.exit_code = invoked.status;
    if (invoked.status !== 0) return { attempt, install_paths: installPaths(), records: records("Unverified", 3, "missing-collector:isolated copy install unavailable", attempt) };
    let summary;
    try { summary = JSON.parse(invoked.stdout); } catch { return { attempt, install_paths: installPaths(), records: records("Unverified", 3, "missing-collector:installer output malformed", attempt) }; }
    if (!exactInstallerSummary(summary, project, opencodeHome)) return { attempt, install_paths: installPaths(), records: records("Unverified", 3, "missing-collector:installer output unavailable", attempt) };
    attempt.status = "completed";
    const observation = observeManagedProfile(project, runRoot, opencodeHome, command, summary);
    return { attempt, install_paths: installPaths(), records: records("pass", 0, "collector:managed-copy-permission-provenance", observation) };
  } catch (error) {
    if (attempt.status !== "completed") return { attempt, install_paths: installPaths(), records: records("Unverified", 3, "missing-collector:isolated copy install unavailable", attempt) };
    return { attempt, install_paths: installPaths(), records: records("fail", 5, `collector:${String(error?.message ?? error)}`, attempt, true) };
  }
}

function prepareA33(options, fixture, project) {
  const parent = mkdtempSync(join(tmpdir(), "aili-a33-runtime-"));
  chmodSync(parent, 0o700);
  const runId = basename(parent);
  const runRoot = realpathSync(parent);
  const cleanupNonce = randomBytes(32).toString("hex");
  writeFileSync(join(runRoot, ".aili-a33-driver-owned"), `${JSON.stringify(markerRecord(runRoot, runId, cleanupNonce))}\n`, "utf8");
  const env = a33GitEnvironment(runRoot);
  for (const path of [env.HOME, env.XDG_CONFIG_HOME, env.XDG_DATA_HOME, env.XDG_CACHE_HOME, env.TMPDIR, env.GIT_CONFIG_VALUE_0]) mkdirSync(path, { recursive: true });
  const host = join(runRoot, "host");
  prepareGitRepository(host, env, "host");
  writeFileSync(join(host, ".gitignore"), "/.worktrees/\n", "utf8");
  git("git", ["add", ".gitignore"], host, env);
  git("git", ["commit", "--quiet", "-m", "ignore attached worktrees"], host, env);
  const worktreesBeforeDescriptors = parseA33WorktreePorcelain(gitNul(host, ["worktree", "list", "--porcelain", "-z"], env));
  const operations = [];
  for (const [index, attachment] of fixture.config.attachments.entries()) {
    if (!validKey(attachment.repo_key) || !validKey(attachment.worktree_key)) throw new Error("fixture key invalid");
    const source = join(runRoot, `source-${index + 1}`);
    prepareGitRepository(source, env, attachment.repo_key);
    git("git", ["config", "core.logAllRefUpdates", attachment.reflog_policy === "enabled" ? "true" : "false"], source, env);
    if (attachment.branch_mode === "existing") git("git", ["branch", attachment.branch, attachment.base_ref], source, env);
    const destination = resolve(host, ".worktrees", attachment.repo_key, attachment.worktree_key);
    const common = {
      operation_class: "driver_fixture", source: canonicalExisting(source), destination,
      repo_key: attachment.repo_key, worktree_key: attachment.worktree_key, branch: attachment.branch,
      base_ref: attachment.base_ref, branch_mode: attachment.branch_mode, reflog_policy: attachment.reflog_policy,
    };
    operations.push({ operation_id: `add-${index + 1}`, kind: "add", ...common });
    operations.push({ operation_id: `remove-${index + 1}`, kind: "remove", ...common });
  }
  const worktreesAfterDescriptors = parseA33WorktreePorcelain(gitNul(host, ["worktree", "list", "--porcelain", "-z"], env));
  const hostIdentity = populatedIdentity(host, "main", env);
  const destinations = operations.filter(({ kind }) => kind === "add").map(({ destination }) => destination);
  const ignoreInput = `${destinations.map((destination) => relative(host, destination).replaceAll("\\", "/")).join("\0")}\0`;
  const ignore = run("git", ["-C", host, "check-ignore", "-v", "-z", "--stdin", "--non-matching"], { cwd: host, env, input: ignoreInput, preserveOutput: true });
  const registry = new Map(A33_RUNTIME_SCENARIO_REGISTRY.map((entry) => [entry.id, entry]));
  const managedProfile = collectManagedProfile(project, runRoot, env, registry);
  const collectorRecords = [
    internalEvidence("a33-host-git-positive", "host-ignore-nested-prepare", {
      attachment_selector: "host", status: validateA33Identity(hostIdentity) ? "pass" : "fail", exit_code: validateA33Identity(hostIdentity) ? 0 : 5,
      evidence_types: ["host-identity", "git-toplevel"], evidence_refs: ["collector:isolated-host-identity"],
    }),
    internalEvidence("a33-ignore-positive", "host-ignore-nested-prepare", {
      attachment_selector: "host-destination", status: ignore.status === 0 && ignore.stdout.includes(".gitignore") ? "pass" : "fail",
      exit_code: ignore.status === 0 && ignore.stdout.includes(".gitignore") ? 0 : 5,
      evidence_types: ["check-ignore-nonmatching", "ignore-provenance"], evidence_refs: ["collector:git-check-ignore-v-z"],
    }),
    internalEvidence("a33-multiple-attachments", "host-ignore-nested-prepare", {
      attachment_selector: "all-attachments", status: destinations.length === fixture.config.attachments.length && new Set(destinations).size === destinations.length ? "pass" : "fail",
      exit_code: destinations.length === fixture.config.attachments.length && new Set(destinations).size === destinations.length ? 0 : 5,
      evidence_types: ["attachment-descriptors", "distinct-destinations"], evidence_refs: ["collector:pending-operation-descriptors"],
    }),
    internalEvidence("a33-runtime-prepare-no-worktree-effect", "host-ignore-nested-prepare", {
      attachment_selector: "all-attachments", status: JSON.stringify(worktreesBeforeDescriptors) === JSON.stringify(worktreesAfterDescriptors) ? "pass" : "fail",
      exit_code: JSON.stringify(worktreesBeforeDescriptors) === JSON.stringify(worktreesAfterDescriptors) ? 0 : 5,
      before_state: worktreesBeforeDescriptors, after_state: worktreesAfterDescriptors,
      evidence_types: ["worktree-list-before", "worktree-list-after", "zero-worktree-effects"], evidence_refs: ["collector:git-worktree-list-porcelain-z"],
    }),
    ...managedProfile.records,
  ];
  const state = {
    schema_version: A33_SCHEMA_VERSION, run_id: runId, run_root: runRoot, project, fixture: fixture.canonical,
    fixture_sha256: fixture.sha256, cleanup_nonce: cleanupNonce, host: canonicalExisting(host), operations, attempts: [], attempt_sequence: [], used_approvals: [],
    approval_snapshots: {}, consumed_approvals: {},
    registered: [], worktree_effects: { adds: 0, removes: 0 }, internal_evidence_version: A33_INTERNAL_EVIDENCE_VERSION,
    collector_records: collectorRecords, managed_install_attempt: managedProfile.attempt, collector_install_paths: managedProfile.install_paths,
    git_environment: env, current_operation_snapshots: {},
  };
  state.current_operation_snapshots = Object.fromEntries(operations.map((operation) => [operation.operation_id, buildA33OperationSnapshot(state, operation)]));
  saveRun(runRoot, state);
  const pending = operations.map((operation) => ({ ...operation, approval_required: true }));
  const report = {
    schema_version: A33_SCHEMA_VERSION, command: "runtime-prepare", status: "pass", exit_code: 0,
    run_id: runId, run_root: runRoot, pending_operations: pending,
    worktree_effects: { adds: 0, removes: 0 },
    unverified: managedProfile.records.filter((record) => record.status === "Unverified").map((record) => record.scenario_id),
  };
  const fields = fixture.config.prepare_result_fields;
  if (!exactKeys(report, fields) || pending.some((operation) => !exactKeys(operation, A33_PENDING_FIELDS))) throw new Error("prepare schema violation");
  return { code: 0, report };
}

function performAdd(options) {
  const { runRoot, state, env } = loadRun(options);
  const operation = operationFor(state, options.operationId, "add");
  const approvalSnapshot = buildA33OperationSnapshot(state, operation);
  state.current_operation_snapshots[operation.operation_id] = approvalSnapshot;
  const approval = readApproval(options, state, operation);
  const decision = validateA33Approval(approval, state, operation);
  if (!decision.valid) {
    const target = absentIdentity(operation.destination);
    const rawBefore = adminSnapshot(operation.source, operation, target, env);
    const before = producerAdminSnapshot(rawBefore);
    const rawAfter = adminSnapshot(operation.source, operation, target, env);
    const unchanged = deltaFrom(before, before);
    const schemaViolation = decision.category === "schema_omission";
    const result = operationResult("runtime-add", state, operation, approval, schemaViolation ? "fail" : "blocked", schemaViolation ? 5 : 3, false, unchanged, unchanged, [`approval:${decision.category}`], [`ADD blocked: ${decision.category}`]);
    recordOperationAttempt(state, decision, result, { host_identity: populatedIdentity(state.host, null, env), source_identity: populatedIdentity(operation.source, null, env), target_before: target, target_after: target },
      { raw_admin_before: rawBefore, raw_admin_after: rawAfter, raw_inventory_observation: null },
      schemaViolation ? ["a33-contract-violation-exit5"] : negativeScenarioIds(decision, operation, approval));
    saveRun(runRoot, state);
    return { code: schemaViolation || !validateA33OperationResult(result) ? 5 : 3, report: result };
  }
  if (existsSync(operation.destination) || state.registered.includes(operation.destination)) {
    const result = operationResult("runtime-add", state, operation, approval, "fail", 5, false, null, null, ["destination-collision"], []);
    recordOperationAttempt(state, { category: "destination_collision", reason: "destination already exists or is registered" }, result,
      { host_identity: populatedIdentity(state.host, null, env), source_identity: populatedIdentity(operation.source, null, env), target_before: absentIdentity(operation.destination), target_after: absentIdentity(operation.destination) },
      { raw_admin_before: null, raw_admin_after: null, raw_inventory_observation: null }, ["a33-contract-violation-exit5"]);
    saveRun(runRoot, state);
    return { code: 5, report: result };
  }
  mkdirSync(dirname(operation.destination), { recursive: true });
  const hostIdentity = populatedIdentity(state.host, null, env);
  const sourceIdentity = populatedIdentity(operation.source, null, env);
  const targetBefore = absentIdentity(operation.destination);
  const rawBefore = adminSnapshot(operation.source, operation, targetBefore, env);
  const before = producerAdminSnapshot(rawBefore);
  const args = operation.branch_mode === "existing"
    ? ["worktree", "add", "--", operation.destination, operation.branch]
    : ["worktree", "add", "-b", operation.branch, "--", operation.destination, operation.base_ref];
  const effect = run("git", ["-C", operation.source, ...args], { cwd: operation.source, env });
  if (effect.status !== 0) {
    const result = operationResult("runtime-add", state, operation, approval, "fail", 5, false, null, null, ["git-worktree-add-failed"], [effect.stderr]);
    recordOperationAttempt(state, { category: "git_add_failed", reason: "git worktree add failed" }, result,
      { host_identity: hostIdentity, source_identity: sourceIdentity, target_before: targetBefore, target_after: targetBefore },
      { raw_admin_before: rawBefore, raw_admin_after: rawBefore, raw_inventory_observation: null }, ["a33-contract-violation-exit5"]);
    saveRun(runRoot, state);
    return { code: 5, report: result };
  }
  const targetAfter = populatedIdentity(operation.destination, "linked", env);
  const rawAfter = adminSnapshot(operation.source, operation, targetAfter, env);
  const after = producerAdminSnapshot(rawAfter);
  const expected = exactDeltaExpected(operation, before, after);
  const observed = deltaFrom(before, after);
  const exact = expected !== null && observed !== null && exactRawTransition(operation, rawBefore, rawAfter)
    && JSON.stringify(expected) === JSON.stringify(observed) && validateA33Identity(hostIdentity) && validateA33Identity(sourceIdentity)
    && validateA33Identity(targetBefore) && validateA33Identity(targetAfter);
  const result = operationResult("runtime-add", state, operation, approval, exact ? "pass" : "fail", exact ? 0 : 5, true, expected, observed, ["git-worktree-add", "identity:absent-to-populated", "typed-delta:direct"], []);
  consumeApproval(state, approval, approvalSnapshot); state.registered.push(operation.destination); state.worktree_effects.adds += 1;
  const selector = operationAttachmentSelector(operation);
  const scenarioIds = [];
  if (selector === "existing") scenarioIds.push("a33-runtime-approval-positive", "a33-add-existing-branch-no-ref-reflog-creation");
  if (selector === "create-enabled") scenarioIds.push("a33-add-new-branch-reflog-enabled-created");
  if (selector === "create-disabled") scenarioIds.push("a33-add-new-branch-reflog-disabled-absent");
  recordOperationAttempt(state, { category: "valid", reason: "approved ADD" }, result,
    { host_identity: hostIdentity, source_identity: sourceIdentity, target_before: targetBefore, target_after: targetAfter },
    { raw_admin_before: rawBefore, raw_admin_after: rawAfter, raw_inventory_observation: null }, scenarioIds);
  saveRun(runRoot, state);
  return { code: validateA33OperationResult(result) ? result.exit_code : 5, report: result };
}

function performRemove(options) {
  const { runRoot, state, env } = loadRun(options);
  const operation = operationFor(state, options.operationId, "remove");
  const approvalSnapshot = buildA33OperationSnapshot(state, operation);
  state.current_operation_snapshots[operation.operation_id] = approvalSnapshot;
  const approval = readApproval(options, state, operation);
  const decision = validateA33Approval(approval, state, operation);
  if (!decision.valid) {
    const target = existsSync(operation.destination) ? populatedIdentity(operation.destination, "linked", env) : absentIdentity(operation.destination);
    const sourceIdentity = populatedIdentity(operation.source, null, env);
    const rawBefore = adminSnapshot(operation.source, operation, target, env);
    const before = producerAdminSnapshot(rawBefore);
    const rawAfter = adminSnapshot(operation.source, operation, target, env);
    const rawInventory = rawRemovalObservation(operation, target, sourceIdentity, env);
    const unchanged = deltaFrom(before, before);
    const schemaViolation = decision.category === "schema_omission";
    const result = operationResult("runtime-remove", state, operation, approval, schemaViolation ? "fail" : "blocked", schemaViolation ? 5 : 3, false, unchanged, unchanged, [`approval:${decision.category}`], [`REMOVE blocked: ${decision.category}`]);
    recordOperationAttempt(state, decision, result, { host_identity: populatedIdentity(state.host, null, env), source_identity: sourceIdentity, target_before: target, target_after: target },
      { raw_admin_before: rawBefore, raw_admin_after: rawAfter, raw_inventory_observation: rawInventory },
      schemaViolation ? ["a33-contract-violation-exit5"] : negativeScenarioIds(decision, operation, approval));
    saveRun(runRoot, state);
    return { code: schemaViolation || !validateA33OperationResult(result) ? 5 : 3, report: result };
  }
  if (!state.registered.includes(operation.destination) || !existsSync(operation.destination)) {
    const target = absentIdentity(operation.destination);
    const sourceIdentity = populatedIdentity(operation.source, null, env);
    const rawBefore = adminSnapshot(operation.source, operation, target, env);
    const before = producerAdminSnapshot(rawBefore);
    const rawAfter = adminSnapshot(operation.source, operation, target, env);
    const rawInventory = rawRemovalObservation(operation, target, sourceIdentity, env);
    const unchanged = deltaFrom(before, before);
    const result = operationResult("runtime-remove", state, operation, approval, "blocked", 3, false, unchanged, unchanged,
      ["typed-inventory:missing", "identity:absent", "no-effect:direct"], ["REMOVE blocked: missing registered target"]);
    recordOperationAttempt(state, { category: "inventory_missing", reason: "removal inventory blocked: missing" }, result,
      { host_identity: populatedIdentity(state.host, null, env), source_identity: sourceIdentity, target_before: target, target_after: target },
      { raw_admin_before: rawBefore, raw_admin_after: rawAfter, raw_inventory_observation: rawInventory }, ["a33-remove-missing-target-block"]);
    saveRun(runRoot, state);
    return { code: 3, report: result };
  }
  const hostIdentity = populatedIdentity(state.host, null, env);
  const sourceIdentity = populatedIdentity(operation.source, null, env);
  const targetBefore = populatedIdentity(operation.destination, "linked", env);
  const rawBefore = adminSnapshot(operation.source, operation, targetBefore, env);
  const before = producerAdminSnapshot(rawBefore);
  const rawInventory = rawRemovalObservation(operation, targetBefore, sourceIdentity, env);
  const targetWorktree = parseA33WorktreePorcelain(rawInventory.worktree_porcelain)
    .find((record) => resolve(record.path) === resolve(operation.destination));
  const inventory = classifyA33RemovalInventory({
    identity: targetBefore, locked: Boolean(targetWorktree?.locked), expected_source: sourceIdentity.git_common_dir,
    observed_source: targetBefore.git_common_dir, expected_path: canonicalDeclared(operation.destination), expected_membership: "linked",
    allowlisted_ephemeral_artifacts: rawInventory.allowlisted_ephemeral_artifacts, visible_files: rawInventory.visible_files,
    raw_inventory_observation: rawInventory,
  });
  if (!inventory.clean) {
    const unchanged = deltaFrom(before, before);
    const result = operationResult("runtime-remove", state, operation, approval, inventory.contradiction ? "fail" : "blocked", inventory.contradiction ? 5 : 3, false, unchanged, unchanged, ["deletion-inventory-blocked", "no-effect:direct"], ["dirty, unknown, ignored, untracked, artifact, or user-visible state"]);
    const inventoryScenario = new Map([
      ["tracked_modified", "a33-remove-dirty-block"], ["tracked_deleted", "a33-remove-dirty-block"], ["untracked", "a33-remove-untracked-block"],
      ["ignored", "a33-remove-ignored-block"], ["artifact", "a33-remove-artifact-block"], ["unknown", "a33-remove-unknown-block"],
      ["user_visible", "a33-remove-user-visible-block"], ["locked", "a33-remove-locked-block"], ["wrong_source", "a33-remove-wrong-source-block"],
      ["wrong_path", "a33-remove-wrong-path-block"], ["wrong_membership", "a33-remove-wrong-path-block"], ["missing", "a33-remove-missing-target-block"],
    ]).get(inventory.primary_class);
    recordOperationAttempt(state, { category: inventory.contradiction ? "inventory_contradiction" : `inventory_${inventory.primary_class}`, reason: `removal inventory blocked: ${inventory.classes.join(",")}` }, result,
      { host_identity: hostIdentity, source_identity: sourceIdentity, target_before: targetBefore, target_after: targetBefore, inventory },
      { raw_admin_before: rawBefore, raw_admin_after: adminSnapshot(operation.source, operation, targetBefore, env), raw_inventory_observation: rawInventory },
      inventory.contradiction ? ["a33-contract-violation-exit5"] : inventoryScenario ? [inventoryScenario] : []);
    saveRun(runRoot, state);
    return { code: inventory.contradiction ? 5 : 3, report: result };
  }
  const effect = run("git", ["-C", operation.source, "worktree", "remove", "--", operation.destination], { cwd: operation.source, env });
  if (effect.status !== 0) {
    const result = operationResult("runtime-remove", state, operation, approval, "fail", 5, false, null, null, ["git-worktree-remove-failed"], [effect.stderr]);
    recordOperationAttempt(state, { category: "git_remove_failed", reason: "git worktree remove failed" }, result,
      { host_identity: hostIdentity, source_identity: sourceIdentity, target_before: targetBefore, target_after: targetBefore },
      { raw_admin_before: rawBefore, raw_admin_after: rawBefore, raw_inventory_observation: rawInventory }, ["a33-contract-violation-exit5"]);
    saveRun(runRoot, state);
    return { code: 5, report: result };
  }
  const targetAfter = absentIdentity(operation.destination);
  const rawAfter = adminSnapshot(operation.source, operation, targetAfter, env);
  const after = producerAdminSnapshot(rawAfter);
  const expected = exactDeltaExpected(operation, before, after);
  const observed = deltaFrom(before, after);
  const exact = expected !== null && observed !== null && exactRawTransition(operation, rawBefore, rawAfter)
    && JSON.stringify(expected) === JSON.stringify(observed) && validateA33Identity(targetBefore) && validateA33Identity(targetAfter);
  const result = operationResult("runtime-remove", state, operation, approval, exact ? "pass" : "fail", exact ? 0 : 5, true, expected, observed, ["git-worktree-remove-non-force", "identity:populated-to-absent", "typed-delta:direct"], []);
  consumeApproval(state, approval, approvalSnapshot); state.registered = state.registered.filter((path) => path !== operation.destination); state.worktree_effects.removes += 1;
  recordOperationAttempt(state, { category: "valid", reason: "approved REMOVE" }, result,
    { host_identity: hostIdentity, source_identity: sourceIdentity, target_before: targetBefore, target_after: targetAfter, inventory },
    { raw_admin_before: rawBefore, raw_admin_after: rawAfter, raw_inventory_observation: rawInventory }, []);
  saveRun(runRoot, state);
  return { code: validateA33OperationResult(result) ? result.exit_code : 5, report: result };
}

function runtimeCase(id, runId, status, evidence, attempt = null, cleanupState = null, targetIdentity = undefined) {
  const operation = attempt?.result?.operation ?? null;
  const approval = attempt?.result?.approval ?? null;
  return {
    id, subset: "runtime", status, exit_code: status === "pass" ? 0 : status === "fail" ? 5 : 3, run_id: runId,
    operation_id: operation?.operation_id ?? null, approval_ref: approval?.approval_id ?? null,
    host_identity: attempt?.host_identity ?? null, source_identity: attempt?.source_identity ?? null,
    target_identity: targetIdentity === undefined ? attempt?.target_after ?? null : targetIdentity,
    expected_delta: attempt?.result?.expected_delta ?? null, observed_delta: attempt?.result?.observed_delta ?? null,
    evidence_refs: evidence, unverified: status === "Unverified" || status === "blocked" ? ["mandatory runtime evidence unavailable"] : [],
    cleanup_state: cleanupState,
  };
}

function aggregateRuntimeEvidence(metadata, state) {
  const attempts = state.attempts ?? [];
  const adds = attempts.filter((entry) => entry.result?.operation?.kind === "add" && entry.result.status === "pass" && entry.result.exit_code === 0);
  const removes = attempts.filter((entry) => entry.result?.operation?.kind === "remove" && entry.result.status === "pass" && entry.result.exit_code === 0 && entry.inventory?.clean === true);
  const expectedAdds = state.operations.filter(({ kind }) => kind === "add");
  const expectedRemoves = state.operations.filter(({ kind }) => kind === "remove");
  const covers = (observed, expected) => expected.length > 0 && expected.every((operation) => observed.some((attempt) => attempt.operation_id === operation.operation_id));
  const distinctApprovals = (observed) => observed.length > 0 && observed.every((attempt) => typeof attempt.result.approval.approval_id === "string")
    && new Set(observed.map((attempt) => attempt.result.approval.approval_id)).size === observed.length;
  if (metadata.id === "a33-runtime-key-mismatch-zero-effect") {
    const matrix = ["add:repo_key_mismatch", "add:worktree_key_mismatch", "remove:repo_key_mismatch", "remove:worktree_key_mismatch"];
    const bound = matrix.map((key) => attempts.find((attempt) => `${attempt.operation_kind}:${attempt.category}` === key));
    if (bound.some((attempt) => !attempt || attempt.result.status !== "blocked" || attempt.result.exit_code !== 3
      || attempt.result.effect_started !== false || !exactUnchangedEvidence(attempt.result))) return null;
    const anchor = bound[0];
    return internalEvidence(metadata.id, metadata.family, { evidence_id: `aggregate:${metadata.id}`, source: "collector",
      operation_id: null, operation_kind: metadata.operation_kind, attachment_selector: metadata.attachment_selector,
      approval_variant: metadata.approval_variant, status: "blocked", exit_code: 3, effect_started: false,
      expected_delta: anchor.result.expected_delta, observed_delta: anchor.result.observed_delta,
      evidence_types: metadata.required_evidence_types, evidence_refs: bound.map(({ evidence_id }) => evidence_id),
      operation_bindings: bound.map(evidenceOperationBinding), cleanup_state: "retain" });
  }
  if (metadata.id === "a33-runtime-approval-declined-unavailable") {
    const bound = ["declined", "unavailable"].map((category) => attempts.find((attempt) => attempt.operation_kind === "add" && attempt.category === category));
    if (bound.some((attempt) => !attempt || attempt.result.status !== "blocked" || attempt.result.exit_code !== 3
      || attempt.result.effect_started !== false || !exactUnchangedEvidence(attempt.result))) return null;
    const anchor = bound[0];
    return internalEvidence(metadata.id, metadata.family, { evidence_id: `aggregate:${metadata.id}`, source: "collector",
      operation_id: null, operation_kind: metadata.operation_kind, attachment_selector: metadata.attachment_selector,
      approval_variant: metadata.approval_variant, status: "blocked", exit_code: 3, effect_started: false,
      expected_delta: anchor.result.expected_delta, observed_delta: anchor.result.observed_delta,
      evidence_types: metadata.required_evidence_types, evidence_refs: bound.map(({ evidence_id }) => evidence_id),
      operation_bindings: bound.map(evidenceOperationBinding), cleanup_state: "not_registered" });
  }
  let sourceAttempts = [];
  if (metadata.family === "valid-add" && metadata.attachment_selector === "all-attachments" && covers(adds, expectedAdds) && distinctApprovals(adds)) sourceAttempts = adds;
  if (metadata.family === "valid-remove" && metadata.attachment_selector === "all-attachments" && covers(removes, expectedRemoves) && distinctApprovals(removes)) sourceAttempts = removes;
  if (metadata.id === "a33-runtime-nested-repository-observed" && covers(adds, expectedAdds)) sourceAttempts = adds;
  if (metadata.id === "a33-unrelated-common-dir-preserved" && covers(adds, expectedAdds) && covers(removes, expectedRemoves)) sourceAttempts = [...adds, ...removes];
  if (metadata.id === "a33-runtime-identity-transition-schema" && covers(adds, expectedAdds) && covers(removes, expectedRemoves)) sourceAttempts = [...adds, ...removes];
  if (sourceAttempts.length === 0) return null;
  const identitiesValid = sourceAttempts.every((attempt) => validateA33Identity(attempt.host_identity) && validateA33Identity(attempt.source_identity)
    && validateA33Identity(attempt.target_before) && validateA33Identity(attempt.target_after));
  const deltasValid = sourceAttempts.every((attempt) => validateDelta(attempt.result.expected_delta) && validateDelta(attempt.result.observed_delta)
    && JSON.stringify(attempt.result.expected_delta) === JSON.stringify(attempt.result.observed_delta));
  const pass = identitiesValid && deltasValid;
  return internalEvidence(metadata.id, metadata.family, {
    evidence_id: `aggregate:${metadata.id}`, source: "collector", operation_id: null,
    operation_kind: metadata.operation_kind, attachment_selector: metadata.attachment_selector,
    approval_variant: metadata.approval_variant, status: pass ? "pass" : "fail", exit_code: pass ? 0 : 5,
    effect_started: true, expected_delta: null, observed_delta: null,
    evidence_types: metadata.required_evidence_types, evidence_refs: sourceAttempts.map(({ evidence_id }) => evidence_id),
    operation_bindings: sourceAttempts.map(evidenceOperationBinding),
    cleanup_state: metadata.cleanup_expectation, contradiction: !pass,
  });
}

function cleanupRuntimeEvidence(metadata, state, eligible) {
  const blockedRemove = state.attempts.some((attempt) => attempt.result?.operation?.kind === "remove" && attempt.result.status === "blocked");
  if (metadata.id === "a33-runtime-cleanup-after-approved-removes" && eligible) {
    return internalEvidence(metadata.id, metadata.family, { attachment_selector: metadata.attachment_selector, approval_variant: metadata.approval_variant,
      status: "pass", exit_code: 0, evidence_types: metadata.required_evidence_types, evidence_refs: ["collector:registered-destinations-empty", "collector:distinct-approved-removes"], cleanup_state: "eligible_for_global_join" });
  }
  if (metadata.id === "a33-runtime-cleanup-retain-registered" && blockedRemove) {
    return internalEvidence(metadata.id, metadata.family, { attachment_selector: metadata.attachment_selector, approval_variant: metadata.approval_variant,
      status: "pass", exit_code: 0, evidence_types: metadata.required_evidence_types, evidence_refs: ["collector:blocked-remove-retained-root"], cleanup_state: "retained" });
  }
  if (metadata.id === "a33-residual-nongoal-exit0" && eligible) {
    return internalEvidence(metadata.id, metadata.family, { attachment_selector: metadata.attachment_selector, approval_variant: metadata.approval_variant,
      status: "pass", exit_code: 0, evidence_types: metadata.required_evidence_types, evidence_refs: ["collector:named-residual-nongoals", "collector:cleanup-eligible"], cleanup_state: "eligible_for_global_join" });
  }
  return null;
}

function selectSuccessfulOperationAttempts(metadata, state) {
  const expected = expectedOperationCoverage(metadata, state.operations);
  if (!expected || expected.length === 0) return { status: "missing", attempts: [], reason: "applicable operation coverage unavailable" };
  const successful = state.attempts.filter((attempt) => attempt.result?.status === "pass" && attempt.result?.exit_code === 0);
  const selected = [];
  for (const binding of expected) {
    const candidates = successful.filter((attempt) => {
      const operation = attempt.result.operation;
      return operation.operation_id === binding.operation_id && operation.kind === binding.operation_kind
        && operationAttachmentSelector(operation) === binding.attachment_selector;
    });
    if (candidates.length === 0) return { status: "missing", attempts: [], reason: `missing operation evidence: ${binding.operation_id}` };
    if (candidates.length > 1) return { status: "invalid", attempts: candidates, reason: `duplicate operation evidence: ${binding.operation_id}` };
    selected.push(candidates[0]);
  }
  const selectedAttemptIds = new Set(selected.map(({ evidence_id }) => evidence_id));
  const applicableExtras = successful.filter((attempt) => {
    const operation = attempt.result.operation;
    const kindMatches = metadata.operation_kind === null || operation.kind === metadata.operation_kind;
    const selectorMatches = metadata.attachment_selector === "all-attachments"
      || operationAttachmentSelector(operation) === metadata.attachment_selector;
    return kindMatches && selectorMatches && !selectedAttemptIds.has(attempt.evidence_id);
  });
  if (applicableExtras.length > 0) return { status: "invalid", attempts: [...selected, ...applicableExtras], reason: "extra applicable attachment operation evidence" };
  return { status: "pass", attempts: selected, reason: null };
}

function deliberateViolationEvidence(metadata, state) {
  if (metadata.id === "a33-material-missing-exit3") {
    const missing = (state.collector_records ?? []).some((record) => record.status === "Unverified" && record.exit_code === 3);
    return missing ? internalEvidence(metadata.id, metadata.family, { attachment_selector: metadata.attachment_selector, approval_variant: metadata.approval_variant,
      status: "Unverified", exit_code: 3, evidence_types: metadata.required_evidence_types, evidence_refs: ["collector:missing-mandatory-positive-classified"] }) : null;
  }
  if (metadata.id === "a33-contract-violation-exit5") {
    const record = internalEvidence(metadata.id, metadata.family, { attachment_selector: metadata.attachment_selector, approval_variant: metadata.approval_variant,
      status: "Unverified", exit_code: 3, evidence_types: metadata.required_evidence_types,
      semantic_observation: { kind: "effect", expected: false, observed: true }, evidence_refs: ["semantic-oracle:effect-mutation"] });
    const rejection = evaluateA33SemanticEvidence(metadata, record, state.operations, state.attempts);
    if (rejection.status !== "fail" || rejection.exit_code !== 5) return null;
    record.semantic_rejection = rejection;
    record.evidence_refs.push("semantic-oracle:observed-rejection-5");
    return record;
  }
  const selection = selectSuccessfulOperationAttempts(metadata, state);
  if (selection.status === "missing") return null;
  if (selection.status === "invalid") {
    return internalEvidence(metadata.id, metadata.family, { attachment_selector: metadata.attachment_selector, approval_variant: metadata.approval_variant,
      operation_kind: metadata.operation_kind, operation_id: null, status: "Unverified", exit_code: 3,
      evidence_types: metadata.required_evidence_types, evidence_refs: [`binding-error:${selection.reason}`], contradiction: true,
      operation_bindings: selection.attempts.map(evidenceOperationBinding), cleanup_state: "retained" });
  }
  if (!selection.attempts.every((attempt) => validateDelta(attempt.result.expected_delta) && validateDelta(attempt.result.observed_delta))) return null;
  const expected = selection.attempts.map((attempt) => structuredClone(attempt.result.expected_delta));
  const mutated = selection.attempts.map((attempt) => structuredClone(attempt.result.observed_delta));
  const field = metadata.approval_variant.includes("reflog") ? "branch_reflog"
    : metadata.approval_variant.includes("branch") ? "branch_ref"
      : metadata.approval_variant.includes("identity") ? "common_dir_identity" : "unrelated_common_dir_entries";
  for (const delta of mutated) {
    delta[field].after = { deliberate_mutation: metadata.approval_variant };
    delta[field].change = "created";
  }
  const observationKind = metadata.approval_variant.includes("reflog") ? "reflog-set" : metadata.approval_variant.includes("branch") ? "ref-set" : "delta-set";
  const record = internalEvidence(metadata.id, metadata.family, { attachment_selector: metadata.attachment_selector, approval_variant: metadata.approval_variant,
    operation_kind: metadata.operation_kind, operation_id: selection.attempts.length === 1 ? selection.attempts[0].operation_id : null, status: "Unverified", exit_code: 3,
    evidence_types: metadata.required_evidence_types, evidence_refs: [`semantic-oracle:${metadata.approval_variant}`], cleanup_state: "retained",
    operation_bindings: selection.attempts.map(evidenceOperationBinding), semantic_observation: { kind: observationKind, expected, observed: mutated } });
  const rejection = evaluateA33SemanticEvidence(metadata, record, state.operations, state.attempts);
  if (rejection.status !== "fail" || rejection.exit_code !== 5) return null;
  record.semantic_rejection = rejection;
  record.evidence_refs.push("semantic-oracle:observed-rejection-5");
  return record;
}

function runtimeJoin(options, fixture) {
  const { runRoot, state } = loadRun(options);
  validateA33ScenarioRegistry(A33_RUNTIME_SCENARIO_REGISTRY, fixture.config.runtime_mandatory_case_ids);
  const successfulAdds = state.attempts.filter((entry) => entry.operation_kind === "add" && entry.result?.status === "pass");
  const successfulRemoves = state.attempts.filter((entry) => entry.operation_kind === "remove" && entry.result?.status === "pass");
  const expectedAdds = state.operations.filter(({ kind }) => kind === "add");
  const expectedRemoves = state.operations.filter(({ kind }) => kind === "remove");
  const removedDestinations = new Set(successfulRemoves.map((entry) => entry.result.operation.destination));
  const eligible = expectedAdds.every((operation) => successfulAdds.some((entry) => entry.operation_id === operation.operation_id))
    && expectedRemoves.every((operation) => removedDestinations.has(operation.destination)) && state.registered.length === 0;
  const baseEvidence = [...(state.collector_records ?? []), ...state.attempts.flatMap((entry) => entry.evidence_records ?? [])];
  const joinEvidenceRecords = [];
  const joinCaseBindings = [];
  const rows = A33_RUNTIME_SCENARIO_REGISTRY.map((metadata) => {
    const generated = aggregateRuntimeEvidence(metadata, state) ?? cleanupRuntimeEvidence(metadata, state, eligible)
      ?? (metadata.family === "deliberate-violation" ? deliberateViolationEvidence(metadata, state) : null);
    const records = generated ? [...baseEvidence, generated] : baseEvidence;
    const classification = classifyA33RuntimeEvidence(metadata, records, state.operations, state.attempts);
    const record = classification.record;
    if (generated) joinEvidenceRecords.push(generated);
    joinCaseBindings.push({ scenario_id: metadata.id, evidence_id: record?.evidence_id ?? null, status: classification.status,
      exit_code: classification.exit_code, reason: classification.reason });
    const attempt = record?.operation_id ? state.attempts.find((entry) => entry.operation_id === record.operation_id) ?? null : null;
    const evidenceRefs = record ? [record.evidence_id, ...record.evidence_refs] : [`missing-compatible-evidence:${metadata.id}`];
    const targetIdentity = metadata.required_evidence_types.includes("target-before-identity") ? attempt?.target_before ?? null : undefined;
    return runtimeCase(metadata.id, state.run_id, classification.status, evidenceRefs, attempt, record?.cleanup_state ?? null, targetIdentity);
  });
  state.join_evidence_records = joinEvidenceRecords;
  state.join_case_bindings = joinCaseBindings;
  saveRun(runRoot, state);
  const anyFailure = state.attempts.some((entry) => entry.result.exit_code === 5);
  const semanticFailure = rows.some((row) => row.status === "fail");
  const missingProfileOrInstall = ["a33-runtime-effective-profile-observed", "a33-runtime-install-observed"]
    .some((id) => state.collector_records.some((record) => record.scenario_id === id && record.status === "Unverified" && record.exit_code === 3));
  const allPass = rows.every((row) => row.status === "pass") && eligible && !anyFailure;
  const exitCode = anyFailure || semanticFailure ? 5 : missingProfileOrInstall ? 3 : allPass ? 0 : 3;
  const ephemeral = join(runRoot, "runtime-result.json");
  const report = {
    schema_version: A33_SCHEMA_VERSION, command: "a33-runtime-join", mode: "runtime",
    status: exitCode === 0 ? "pass" : exitCode === 3 ? "Unverified" : "fail", exit_code: exitCode,
    run_id: state.run_id, mandatory_case_ids: fixture.config.runtime_mandatory_case_ids,
    observed_case_ids: fixture.config.runtime_mandatory_case_ids, case_set_equal: true, cases: rows,
    operations: state.attempts.map((entry) => entry.result),
    cleanup: { eligible, attempted: false, status: eligible ? "eligible_for_global_join" : state.registered.length ? "retained_registered" : "blocked", retained_paths: [runRoot], errors: [] },
    summary: { mandatory: rows.length, passed: rows.filter((row) => row.status === "pass").length, adds: state.worktree_effects.adds, removes: state.worktree_effects.removes },
    unverified: exitCode === 3 ? rows.filter((row) => row.status !== "pass").map((row) => row.id) : [], ephemeral_result: ephemeral,
  };
  writeFileSync(ephemeral, `${JSON.stringify(report, null, 2)}\n`, "utf8");
  return { code: exitCode, report };
}

async function executeA33(options) {
  const project = realpathSync(resolve(options.project));
  if (!statSync(project).isDirectory()) throw new Error("usage");
  const fixture = loadA33Fixture(options.fixture, project);
  if (options.mode === "a33-runtime-prepare") return prepareA33(options, fixture, project);
  if (options.mode === "a33-runtime-add") return performAdd(options);
  if (options.mode === "a33-runtime-remove") return performRemove(options);
  return runtimeJoin(options, fixture);
}

async function main() {
  try {
    const argv = process.argv.slice(2);
    const requestedMode = argv[argv.indexOf("--mode") + 1];
    if (A33_MODES.has(requestedMode)) {
      const options = parseA33Arguments(argv);
      try {
        const { code, report } = await executeA33(options);
        process.stdout.write(`${JSON.stringify(report, null, 2)}\n`);
        process.exitCode = code;
      } catch (error) {
        const message = String(error?.message ?? error).replace(/[\r\n\t]+/g, " ").slice(0, 300);
        const unsafe = /schema violation|state mismatch|run identity|fixture key invalid|operation mismatch|scenario registry|isolated Git environment|evidence malformed|raw inventory|approval snapshot/.test(message);
        process.stdout.write(`${JSON.stringify({ schema_version: A33_SCHEMA_VERSION, command: requestedMode.replace("a33-", ""), status: unsafe ? "fail" : "Unverified", exit_code: unsafe ? 5 : 3, effect_started: false, unverified: [message] }, null, 2)}\n`);
        process.exitCode = unsafe ? 5 : 3;
      }
      return;
    }
    const options = parseArguments(argv);
    const project = realpathSync(resolve(options.project));
    if (!statSync(project).isDirectory()) throw new Error("usage");
    const fixture = loadFixture(options.fixture, project, options.opencodeVersion);
    await execute(options, fixture, project);
  } catch {
    usageError();
  }
}

if (process.argv[1] && realpathSync(process.argv[1]) === realpathSync(fileURLToPath(import.meta.url))) await main();
