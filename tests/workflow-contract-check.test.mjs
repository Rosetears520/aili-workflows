import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { cp, mkdir, mkdtemp, readFile, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const sourceRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const change = "complete-aili-workflow-orchestration";
const workflowFixture = "docs/harness/fixtures/workflow-orchestration-fixtures.yaml";
const generatedFixture = "docs/harness/fixtures/generated-openspec-adapter-fixtures.yaml";

function run(root, args) {
  return spawnSync("python", args, { cwd: root, encoding: "utf8", timeout: 120_000 });
}

function runWorkflow(root, profile, fixture = workflowFixture) {
  const result = run(root, [
    "scripts/workflow_contract_check.py",
    "--project", ".",
    "--change", change,
    "--profile", profile,
    "--fixture", fixture,
    "--json",
  ]);
  let payload = null;
  try { payload = JSON.parse(result.stdout); } catch {}
  return { ...result, payload };
}

function runWorkflowFinalClosure(root, taskAudit, fixture = workflowFixture) {
  const result = run(root, [
    "scripts/workflow_contract_check.py",
    "--project", ".",
    "--change", change,
    "--profile", "scaffold",
    "--fixture", fixture,
    "--final-closure",
    "--task-audit", taskAudit,
    "--json",
  ]);
  let payload = null;
  try { payload = JSON.parse(result.stdout); } catch {}
  return { ...result, payload };
}

async function writePassingTaskAudit(root, relative = "task-audit.json") {
  const scaffold = runWorkflow(root, "scaffold");
  assert.equal(scaffold.status, 0, scaffold.stderr || scaffold.stdout);
  const audit = {
    schema_version: "1.0",
    owner: "ROSE",
    change,
    unresolved: [],
    runtime_enforcement: {
      uv_id: "UV-001",
      read_only_edit: "verified",
      nested_task: "verified",
      evidence: ["fresh runtime permission probe passed for the final review overlay"],
    },
    rows: scaffold.payload.traceability.task_matrix.map((row) => ({
      ...row,
      "fresh tests/inspection/review evidence": {
        task_id: row.task_id,
        results: [{ command_id: "C-HARNESS", status: "pass", scope: `task ${row.task_id}` }],
      },
      status: "Done",
      findings: [],
      disposition: "ROSE-resolved: pass",
      freshness: "final",
    })),
  };
  await saveJson(root, relative, audit);
  return { relative, audit };
}

async function loadJson(root, relative) {
  return JSON.parse(await readFile(path.join(root, relative), "utf8"));
}

async function saveJson(root, relative, value) {
  await writeFile(path.join(root, relative), `${JSON.stringify(value, null, 2)}\n`, "utf8");
}

async function writeSyntheticOpenSpecFixture(root) {
  const fixture = await loadJson(root, workflowFixture);
  const adapters = await loadJson(root, generatedFixture);
  const changeRoot = path.join(root, "openspec/changes", change);
  const taskIds = fixture.aggregate_traceability.task_evidence_catalog.map((row) => row.task_id);
  assert.equal(taskIds.length, 74);

  await mkdir(path.join(changeRoot, "specs/codegraph-evidence-provider"), { recursive: true });
  await mkdir(path.join(changeRoot, "specs/graphify-periodic-review"), { recursive: true });
  await mkdir(path.join(root, "openspec/changes/integrate-codegraph-graphify-workflow"), { recursive: true });
  await writeFile(
    path.join(changeRoot, "tasks.md"),
    `${taskIds.map((taskId) => `- [ ] ${taskId} Synthetic canonical task ${taskId}`).join("\n")}\n`,
    "utf8"
  );
  await writeFile(path.join(changeRoot, "design.md"), "# Synthetic canonical workflow design\n", "utf8");
  await writeFile(
    path.join(changeRoot, "specs/codegraph-evidence-provider/spec.md"),
    "# Synthetic CodeGraph evidence provider contract\n",
    "utf8"
  );
  await writeFile(
    path.join(changeRoot, "specs/graphify-periodic-review/spec.md"),
    "# Synthetic Graphify periodic review contract\n",
    "utf8"
  );
  for (const adapter of adapters.generated_adapter_boundary.direct_adapter_cases) {
    const target = path.join(root, adapter.adapter_path);
    await mkdir(path.dirname(target), { recursive: true });
    const content = adapter.adapter_path.startsWith(".opencode/commands/")
      ? `# Synthetic OpenSpec adapter\nRoute: /${path.basename(adapter.adapter_path, ".md")}\n`
      : `---\ngeneratedBy: openspec\n---\n# Synthetic OpenSpec adapter\n`;
    await writeFile(target, content, "utf8");
  }
}

test("Package 11 aggregate checkers derive canonical evidence and reject mutated contracts", { timeout: 180_000 }, async (t) => {
  const scratch = await mkdtemp(path.join(tmpdir(), "aili-p11-contract-"));
  const root = path.join(scratch, "repo");
  await cp(sourceRoot, root, {
    recursive: true,
    filter(source) {
      const relative = path.relative(sourceRoot, source);
      const first = relative.split(path.sep)[0];
      return ![".git", ".codegraph", "node_modules", "dist", "memory", "__pycache__", "ideas", "openspec"].includes(first);
    },
  });
  await writeSyntheticOpenSpecFixture(root);

  const pristineWorkflow = await readFile(path.join(root, workflowFixture), "utf8");
  const pristineGenerated = await readFile(path.join(root, generatedFixture), "utf8");
  const pristineIdeate = await readFile(path.join(root, "commands/ideate.md"), "utf8");
  const pristineRegister = await readFile(path.join(root, "docs/harness/workflow-orchestration-source-register.md"), "utf8");
  const pristineReviewFixture = await readFile(path.join(root, "docs/harness/fixtures/review-convergence-fixtures.yaml"), "utf8");
  const pristineManifest = await readFile(path.join(root, "manifests/rose-aili.components.json"), "utf8");
  const pristinePackage = await readFile(path.join(root, "package.json"), "utf8");
  const pristineComponents = await readFile(path.join(root, "workflow.components.yaml"), "utf8");
  const formalSourcePaths = [
    ".agents/skills/parallel-subagent-dispatch/references/agent-selection-matrix.md",
    ".agents/skills/aili-delivery-flow/references/formal-task-board.md",
    ".agents/skills/aili-delivery-flow/references/protocols/subagent-task-packet.md",
    ".agents/skills/aili-delivery-flow/references/protocols/subagent-result.md",
    ".agents/skills/aili-delivery-flow/references/lifecycle.md",
  ];
  const pristineFormalSources = new Map(await Promise.all(formalSourcePaths.map(async (relative) => [
    relative,
    await readFile(path.join(root, relative), "utf8"),
  ])));

  t.after(async () => { await rm(scratch, { recursive: true, force: true }); });
  t.beforeEach(async () => {
    await rm(path.join(root, "ideas"), { recursive: true, force: true });
    await writeFile(path.join(root, workflowFixture), pristineWorkflow, "utf8");
    await writeFile(path.join(root, generatedFixture), pristineGenerated, "utf8");
    await writeFile(path.join(root, "commands/ideate.md"), pristineIdeate, "utf8");
    await writeFile(path.join(root, "docs/harness/workflow-orchestration-source-register.md"), pristineRegister, "utf8");
    await writeFile(path.join(root, "docs/harness/fixtures/review-convergence-fixtures.yaml"), pristineReviewFixture, "utf8");
    await writeFile(path.join(root, "manifests/rose-aili.components.json"), pristineManifest, "utf8");
    await writeFile(path.join(root, "package.json"), pristinePackage, "utf8");
    await writeFile(path.join(root, "workflow.components.yaml"), pristineComponents, "utf8");
    for (const [relative, content] of pristineFormalSources) {
      await writeFile(path.join(root, relative), content, "utf8");
    }
    await writeSyntheticOpenSpecFixture(root);
  });

  await t.test("emits stable JSON and exit contracts for all three profiles", () => {
    const scaffold = runWorkflow(root, "scaffold");
    assert.equal(scaffold.status, 0, scaffold.stderr || scaffold.stdout);
    assert.equal(scaffold.payload.status, "pass");
    assert.equal(scaffold.payload.traceability.requirements, 77);
    assert.equal(scaffold.payload.traceability.authoritative_sources, 27);
    assert.equal(scaffold.payload.traceability.task_ids.length, 74);
    assert.equal(scaffold.payload.traceability.task_matrix.length, 74);
    assert.ok(scaffold.payload.traceability.task_matrix.every((row) => row.status === "Partial"));
    assert.ok(scaffold.payload.traceability.task_matrix.every((row) => Object.keys(row).length === 9));
    assert.ok(scaffold.payload.traceability.task_matrix.every((row) => row.disposition === "ROSE-owned: unresolved"));
    assert.equal(scaffold.payload.formal_agent_orchestration.protocols.selection, "aili-agent-selection/v1");
    assert.equal(scaffold.payload.formal_agent_orchestration.protocols.board, "aili-task-board/v1");
    assert.equal(scaffold.payload.formal_agent_orchestration.canonical_roles.length, 19);
    assert.equal(scaffold.payload.formal_agent_orchestration.cases.length, 21);

    const generated = runWorkflow(root, "generated-adapter-boundary", generatedFixture);
    assert.equal(generated.status, 0, generated.stderr || generated.stdout);
    assert.equal(generated.payload.status, "pass");
    for (const evidence of Object.values(generated.payload.repository_inspection.aili_gate_evidence)) {
      assert.equal(evidence.gates_apply, true);
      assert.equal(evidence.observed_markers.length, evidence.required_markers.length);
    }

    const residual = runWorkflow(root, "residual");
    assert.equal(residual.status, 0, residual.stderr || residual.stdout);
    assert.equal(residual.payload.status, "pass");
    assert.ok(residual.payload.matches.length > 0);
    assert.equal(residual.payload.classifications.some((row) => row.classification === "active violation"), false);
  });

  await t.test("rejects a shrunken formal orchestration fixture case contract", async () => {
    const fixture = await loadJson(root, workflowFixture);
    fixture.formal_agent_orchestration.cases = fixture.formal_agent_orchestration.cases.slice(1);
    await saveJson(root, workflowFixture, fixture);
    const result = runWorkflow(root, "scaffold");
    assert.equal(result.status, 5);
    assert.match(result.payload.errors.join("\n"), /formal_agent_orchestration.*exact shared selection\/Board contract/i);
  });

  await t.test("rejects canonical role matrix drift and general formal ownership", async () => {
    const relative = ".agents/skills/parallel-subagent-dispatch/references/agent-selection-matrix.md";
    const mutated = pristineFormalSources.get(relative)
      .replace(/^\| `web-performance-auditor` .*\n/m, "")
      .replace("| `opensource-sanitizer` |", "| `general` |")
      .replace("`general` is not a canonical specialist role", "`general` is a canonical specialist role");
    await writeFile(path.join(root, relative), mutated, "utf8");
    const result = runWorkflow(root, "scaffold");
    assert.equal(result.status, 5);
    assert.match(result.payload.errors.join("\n"), /role inventory|general role row|selection matrix/i);
  });

  await t.test("rejects formal Board ownership and ordered package-field drift", async () => {
    const relative = ".agents/skills/aili-delivery-flow/references/formal-task-board.md";
    const mutated = pristineFormalSources.get(relative)
      .replace("Every accepted task ID belongs to exactly one current task-execution package.", "Accepted task ownership is flexible.")
      .replace("  - Package kind:", "  - Package type:");
    await writeFile(path.join(root, relative), mutated, "utf8");
    const result = runWorkflow(root, "scaffold");
    assert.equal(result.status, 5);
    assert.match(result.payload.errors.join("\n"), /task Board reference|Board package fields/i);
  });

  await t.test("rejects portable packet and result envelope field drift", async () => {
    const packet = ".agents/skills/aili-delivery-flow/references/protocols/subagent-task-packet.md";
    const resultPath = ".agents/skills/aili-delivery-flow/references/protocols/subagent-result.md";
    await writeFile(
      path.join(root, packet),
      pristineFormalSources.get(packet).replace("Forbidden scope:\n", ""),
      "utf8"
    );
    await writeFile(
      path.join(root, resultPath),
      pristineFormalSources.get(resultPath).replace("continuation_recommendation: same-package | new-package | none\n", ""),
      "utf8"
    );
    const result = runWorkflow(root, "scaffold");
    assert.equal(result.status, 5);
    assert.match(result.payload.errors.join("\n"), /task packet fields|result fields|canonical result/i);
  });

  await t.test("rejects human-artifact claim prefixes in shared formal references", async () => {
    const relative = ".agents/skills/aili-delivery-flow/references/formal-task-board.md";
    await writeFile(path.join(root, relative), `${pristineFormalSources.get(relative)}\n[KNOWN] runtime-only completion proof\n`, "utf8");
    const result = runWorkflow(root, "scaffold");
    assert.equal(result.status, 5);
    assert.match(result.payload.errors.join("\n"), /human-artifact claim prefix/i);
  });

  await t.test("rejects decision and implementation-authorization vocabulary drift", async () => {
    const relative = ".agents/skills/aili-delivery-flow/references/lifecycle.md";
    const mutated = pristineFormalSources.get(relative).replace(
      "`proposed`, `direction-recorded`, `conditional`, `awaiting-confirmation`, `accepted`, `rejected`, or `superseded`",
      "`proposed`, `accepted`, or `rejected`"
    );
    await writeFile(path.join(root, relative), mutated, "utf8");
    const result = runWorkflow(root, "scaffold");
    assert.equal(result.status, 5);
    assert.match(result.payload.errors.join("\n"), /lifecycle\.md: missing formal orchestration marker/i);
  });

  await t.test("private ideas are neither required nor gate inputs", async () => {
    for (const profile of ["scaffold", "residual"]) {
      const withoutIdeas = runWorkflow(root, profile);
      assert.equal(withoutIdeas.status, 0, withoutIdeas.stderr || withoutIdeas.stdout);
    }

    await mkdir(path.join(root, "ideas"));
    await writeFile(path.join(root, "ideas/private-local-only.md"), "baseline-manifest.json as active authority\n", "utf8");

    for (const profile of ["scaffold", "residual"]) {
      const withIdeas = runWorkflow(root, profile);
      assert.equal(withIdeas.status, 0, withIdeas.stderr || withIdeas.stdout);
    }
  });

  await t.test("rejects P6 ownership drift including the dedicated permission test", async () => {
    const fixture = await loadJson(root, workflowFixture);
    const p6 = fixture.package_file_ownership.find((row) => row.package === "P6");
    p6.files = p6.files.filter((entry) => entry !== "tests/opencode-permission-probe.test.mjs");
    for (const source of fixture.sources.filter((row) => row.category === "cross-root")) {
      source.paths = source.paths.filter((entry) => entry !== "tests/opencode-permission-probe.test.mjs");
    }
    await saveJson(root, workflowFixture, fixture);
    const result = runWorkflow(root, "scaffold");
    assert.equal(result.status, 5);
    assert.match(result.payload.errors.join("\n"), /canonical cross-root inventory/);
  });

  await t.test("accepts only the exact inspection-only source path, state, and reason", async () => {
    const fixture = await loadJson(root, workflowFixture);
    const row = fixture.sources.find((entry) => entry.id === "codegraph-generated-boundary-ignore");
    row.paths = ["README.md"];
    row.non_edit_reason = "generic inspection exemption";
    await saveJson(root, workflowFixture, fixture);
    const result = runWorkflow(root, "scaffold");
    assert.equal(result.status, 5);
    assert.match(result.payload.errors.join("\n"), /requires edit ownership or justified inspection-only state/);
  });

  await t.test("binds rejected-machinery allowances to observed occurrence counts", async () => {
    const fixture = await loadJson(root, workflowFixture);
    await writeFile(path.join(root, "commands/ideate.md"), `${pristineIdeate}\nUse baseline-manifest.json as current approval authority.\n`);
    await saveJson(root, workflowFixture, fixture);
    const result = runWorkflow(root, "scaffold");
    assert.equal(result.status, 5);
    assert.match(result.payload.errors.join("\n"), /active rejected machinery semantic/);
  });

  await t.test("derives generated AILI gates from canonical command sources instead of fixture booleans", async () => {
    await writeFile(
      path.join(root, "commands/ideate.md"),
      pristineIdeate.replace("Required behavior:", "Behavior:")
    );
    const fixture = await loadJson(root, generatedFixture);
    assert.equal(fixture.generated_adapter_boundary.aili_routes[0].aili_gates_apply, true);
    const result = runWorkflow(root, "generated-adapter-boundary", generatedFixture);
    assert.equal(result.status, 5);
    assert.match(result.payload.errors.join("\n"), /canonical AILI route lacks required gate evidence/);
  });

  await t.test("derives residual roots from canonical active inventory and rejects fixture-selected subsets", async () => {
    const fixture = await loadJson(root, workflowFixture);
    fixture.residual.scan_roots = ["commands/ideate.md"];
    await saveJson(root, workflowFixture, fixture);
    const result = runWorkflow(root, "residual");
    assert.equal(result.status, 5);
    assert.match(result.payload.errors.join("\n"), /must equal independent registry\/manifest\/source-tree\/package allowlist/);
  });

  await t.test("residual roots do not shrink when a fixture source row is deleted", async () => {
    const fixture = await loadJson(root, workflowFixture);
    fixture.sources = fixture.sources.filter((row) => row.id !== "classifier-delivery");
    await saveJson(root, workflowFixture, fixture);
    const result = runWorkflow(root, "residual");
    assert.equal(result.status, 5);
    assert.match(result.payload.errors.join("\n"), /canonical residual source authority|source inventory/);
  });

  await t.test("coordinated fixture ownership and source omission cannot hide an active residual", async () => {
    const fixture = await loadJson(root, workflowFixture);
    for (const row of fixture.package_file_ownership) {
      row.files = row.files.filter((entry) => entry !== "commands/ideate.md");
    }
    for (const row of fixture.sources) {
      row.paths = row.paths.filter((entry) => entry !== "commands/ideate.md");
    }
    fixture.serial_overlaps = fixture.serial_overlaps.filter((row) => row.path !== "commands/ideate.md");
    await writeFile(path.join(root, "commands/ideate.md"), `${pristineIdeate}\nUse baseline-manifest.json as active authority.\n`);
    await saveJson(root, workflowFixture, fixture);
    const result = runWorkflow(root, "residual");
    assert.equal(result.status, 5);
    assert.match(result.payload.errors.join("\n"), /active violation|independent residual/i);
  });

  await t.test("coordinated component source and package registry omission cannot hide a named skill", async () => {
    const fixture = await loadJson(root, workflowFixture);
    for (const row of fixture.sources) {
      row.paths = row.paths.filter((entry) => !entry.startsWith(".agents/skills/ai-regression-scout"));
    }
    const manifest = await loadJson(root, "manifests/rose-aili.components.json");
    manifest.components.skills = manifest.components.skills.filter((row) => row.name !== "ai-regression-scout");
    const pkg = await loadJson(root, "package.json");
    pkg.files = pkg.files.filter((entry) => entry !== ".agents/");
    await saveJson(root, workflowFixture, fixture);
    await saveJson(root, "manifests/rose-aili.components.json", manifest);
    await saveJson(root, "package.json", pkg);
    const result = runWorkflow(root, "residual");
    assert.equal(result.status, 5);
    assert.match(result.payload.errors.join("\n"), /named source tree|package registry|source registry/i);
  });

  await t.test("residual independently validates the workflow component registry", async () => {
    const components = await loadJson(root, "workflow.components.yaml");
    components.components = components.components.filter((row) => row.id !== "verification");
    await saveJson(root, "workflow.components.yaml", components);
    const result = runWorkflow(root, "residual");
    assert.equal(result.status, 5);
    assert.match(result.payload.errors.join("\n"), /component registry ids/i);
  });

  await t.test("residual allowlists bind exact occurrence locations", async () => {
    const fixture = await loadJson(root, workflowFixture);
    const allowance = fixture.residual.legitimate_matches[0];
    allowance.occurrences[0].line += 1;
    await saveJson(root, workflowFixture, fixture);
    const result = runWorkflow(root, "residual");
    assert.equal(result.status, 5);
    assert.match(result.payload.errors.join("\n"), /exact residual allowance|occurrence/);
  });

  await t.test("generated profile requires cross-fixture ready state consistency", async () => {
    const fixture = await loadJson(root, workflowFixture);
    fixture.profiles["generated-adapter-boundary"].ready = false;
    await saveJson(root, workflowFixture, fixture);
    const result = runWorkflow(root, "generated-adapter-boundary", generatedFixture);
    assert.equal(result.status, 5);
    assert.match(result.payload.errors.join("\n"), /cross-fixture.*ready state/i);
  });

  await t.test("generated adapters must be regular in-repository files", async () => {
    await rm(path.join(root, ".opencode/commands/opsx-apply.md"));
    await writeFile(path.join(root, "outside-adapter.md"), "openspec /opsx-apply\n");
    const { symlink } = await import("node:fs/promises");
    await symlink(path.join(root, "outside-adapter.md"), path.join(root, ".opencode/commands/opsx-apply.md"));
    const result = runWorkflow(root, "generated-adapter-boundary", generatedFixture);
    assert.equal(result.status, 5);
    assert.match(result.payload.errors.join("\n"), /regular in-repository file/);
  });

  for (const [label, mutate, pattern] of [
    ["unknown test", (fixture) => { fixture.aggregate_traceability.requirements[0].tests.positive = ["unknown-case-id"]; }, /unknown test\/case/],
    ["wrong command", (fixture) => { fixture.aggregate_traceability.requirements[0].command_ids = ["C-NODE"]; }, /command.*does not match|wrong command/i],
    ["omitted task evidence", (fixture) => { fixture.aggregate_traceability.task_evidence_catalog = fixture.aggregate_traceability.task_evidence_catalog.slice(1); }, /task evidence.*missing=/i],
    ["duplicate task evidence", (fixture) => { fixture.aggregate_traceability.task_evidence_catalog.push(structuredClone(fixture.aggregate_traceability.task_evidence_catalog[0])); }, /task evidence.*duplicate/i],
    ["missing aggregate task coverage", (fixture) => { fixture.aggregate_traceability.requirements = fixture.aggregate_traceability.requirements.map((row) => ({ ...row, task_ids: row.task_ids.filter((id) => id !== "5.5") })); fixture.aggregate_traceability.authoritative_sources = fixture.aggregate_traceability.authoritative_sources.map((row) => ({ ...row, task_ids: row.task_ids.filter((id) => id !== "5.5") })); }, /aggregate task coverage.*missing/i],
  ]) {
    await t.test(`rejects ${label}`, async () => {
      const fixture = await loadJson(root, workflowFixture);
      mutate(fixture);
      await saveJson(root, workflowFixture, fixture);
      const result = runWorkflow(root, "scaffold");
      assert.equal(result.status, 5);
      assert.match(result.payload.errors.join("\n"), pattern);
    });
  }

  await t.test("rejects coordinated fabricated alias and requirement reference mutation", async () => {
    const fixture = await loadJson(root, workflowFixture);
    const alias = fixture.aggregate_traceability.test_evidence_aliases[0];
    const oldAlias = alias.aliases[0];
    alias.aliases[0] = "fabricated-coordinated-alias";
    alias.actual_id = "fabricated-coordinated-test-id";
    for (const row of fixture.aggregate_traceability.requirements) {
      for (const kind of ["positive", "negative", "recovery"]) {
        row.tests[kind] = row.tests[kind].map((id) => id === oldAlias ? alias.alias : id);
      }
    }
    for (const row of fixture.aggregate_traceability.authoritative_sources) {
      for (const kind of ["positive", "negative", "recovery"]) {
        row.tests[kind] = row.tests[kind].map((id) => id === oldAlias ? alias.alias : id);
      }
    }
    await saveJson(root, workflowFixture, fixture);
    const result = runWorkflow(root, "scaffold");
    assert.equal(result.status, 5);
    assert.match(result.payload.errors.join("\n"), /actual fixture case|executable test id|alias source/i);
  });

  await t.test("P11 audit template cannot be used as final completion evidence", () => {
    const result = runWorkflowFinalClosure(root, workflowFixture);
    assert.equal(result.status, 5);
    assert.match(result.payload.errors.join("\n"), /separate ROSE-owned task-audit|must differ/i);
  });

  await t.test("final closure reads a separate ROSE task audit and accepts 74 resolved Done rows", async () => {
    const { relative } = await writePassingTaskAudit(root);
    const result = runWorkflowFinalClosure(root, relative);
    assert.equal(result.status, 0, result.stderr || result.stdout);
    assert.equal(result.payload.final_task_audit.rows, 74);
    assert.equal(result.payload.traceability.task_matrix.every((row) => row.status === "Partial"), true);
  });

  await t.test("final closure accepts a resolved source-backed N/A row", async () => {
    const { relative, audit } = await writePassingTaskAudit(root);
    const row = audit.rows[0];
    row.status = "N/A";
    row["implementation files/artifacts"] = [];
    row["fresh tests/inspection/review evidence"] = {
      task_id: row.task_id,
      accepted_scope_source: "openspec/changes/complete-aili-workflow-orchestration/tasks.md",
      rationale: "the accepted task scope explicitly requires no implementation artifact",
      confirmed_by: ["convergence-reviewer", "ROSE"],
    };
    row.disposition = "ROSE-resolved: accepted N/A";
    await saveJson(root, relative, audit);
    const result = runWorkflowFinalClosure(root, relative);
    assert.equal(result.status, 0, result.stderr || result.stdout);
  });

  for (const [label, mutate, pattern] of [
    ["unresolved Done disposition", (audit) => { audit.rows[0].disposition = "ROSE-owned: unresolved"; }, /resolved disposition/i],
    ["unresolved source-backed N\/A", (audit) => { audit.rows[0].status = "N/A"; audit.rows[0]["implementation files/artifacts"] = []; audit.rows[0]["fresh tests/inspection/review evidence"] = { task_id: audit.rows[0].task_id, accepted_scope_source: "openspec/changes/complete-aili-workflow-orchestration/tasks.md", rationale: "accepted scope excludes implementation", confirmed_by: ["convergence-reviewer"] }; audit.rows[0].disposition = "ROSE-resolved: accepted N/A"; }, /N\/A.*ROSE confirmation|confirmed_by/i],
    ["stale final evidence", (audit) => { audit.rows[0].freshness = "stale"; }, /final freshness/i],
    ["missing task evidence", (audit) => { audit.rows[0]["fresh tests/inspection/review evidence"] = {}; }, /task-specific.*evidence|fresh evidence/i],
    ["unresolved finding", (audit) => { audit.rows[0].findings = ["still open"]; }, /unresolved findings/i],
    ["unresolved UV-001 runtime enforcement", (audit) => { audit.runtime_enforcement.read_only_edit = "Unverified"; }, /UV-001.*read-only runtime enforcement/i],
  ]) {
    await t.test(`final task audit rejects ${label}`, async () => {
      const { relative, audit } = await writePassingTaskAudit(root);
      mutate(audit);
      await saveJson(root, relative, audit);
      const result = runWorkflowFinalClosure(root, relative);
      assert.equal(result.status, 5);
      assert.match(result.payload.errors.join("\n"), pattern);
    });
  }

  await t.test("Package 12 registry includes the Python unittest aggregate", async () => {
    const fixture = await loadJson(root, workflowFixture);
    assert.equal(
      fixture.aggregate_traceability.commands["C-PYTHON"],
      "python -m unittest discover -s tests -p '*.py'"
    );
    const pkg = await loadJson(root, "package.json");
    assert.match(pkg.scripts.test, /python -m unittest discover -s tests -p '\*\.py'/);
  });

  await t.test("bare natural OpenSpec continuation collisions are routed without route-name hints", async () => {
    const fixture = await loadJson(root, generatedFixture);
    const byId = new Map(fixture.package_2_cases.map((row) => [row.id, row]));
    assert.equal(byId.get("routing-bare-continue-implementation-change")?.input, "continue implementation of change X");
    assert.equal(byId.get("routing-bare-implement-accepted-openspec-change")?.input, "implement the accepted OpenSpec change");
    for (const id of ["routing-bare-continue-implementation-change", "routing-bare-implement-accepted-openspec-change"]) {
      assert.doesNotMatch(byId.get(id).input, /\/(?:build|opsx)|aili-delivery-flow|openspec-apply-change|do not|exclude/i);
    }
  });

  await t.test("rejects the retired BUILD filename as active authority", async () => {
    await writeFile(path.join(root, "commands/build.md"), `${await readFile(path.join(root, "commands/build.md"), "utf8")}\nActive authority: references/build-goal-mode.md\n`);
    const result = runWorkflow(root, "scaffold");
    assert.equal(result.status, 5);
    assert.match(result.payload.errors.join("\n"), /retired BUILD authority path/);
  });

  await t.test("Package 12 final overlay denies attempted edits and nested tasks for test-engineer", async () => {
    const fixture = await loadJson(root, "docs/harness/fixtures/review-convergence-fixtures.yaml");
    const lane = fixture.final_review_overlays.find((row) => row.agent === "agents/test-engineer.md");
    lane.edit = "allow";
    await saveJson(root, "docs/harness/fixtures/review-convergence-fixtures.yaml", fixture);
    const result = run(root, ["scripts/harness_fixture_check.py"]);
    assert.equal(result.status, 1, result.stdout + result.stderr);
    assert.match(result.stdout, /test-engineer.*edit.*deny/i);
  });

  await t.test("harness fixture check derives all 74 task ids from the tracked catalog without OpenSpec", async () => {
    await rm(path.join(root, "openspec"), { recursive: true, force: true });
    const result = run(root, ["scripts/harness_fixture_check.py"]);
    assert.equal(result.status, 0, result.stdout + result.stderr);
  });

  await t.test("harness fixture check rejects a shrunken tracked task catalog without OpenSpec", async () => {
    await rm(path.join(root, "openspec"), { recursive: true, force: true });
    const fixture = await loadJson(root, workflowFixture);
    fixture.aggregate_traceability.task_evidence_catalog = fixture.aggregate_traceability.task_evidence_catalog.slice(1);
    await saveJson(root, workflowFixture, fixture);
    const result = run(root, ["scripts/harness_fixture_check.py"]);
    assert.equal(result.status, 1, result.stdout + result.stderr);
    assert.match(result.stdout, /task_evidence_catalog must contain exactly 74 unique task ids/i);
  });

  await t.test("harness fixture check rejects duplicate tracked task ids without OpenSpec", async () => {
    await rm(path.join(root, "openspec"), { recursive: true, force: true });
    const fixture = await loadJson(root, workflowFixture);
    const catalog = fixture.aggregate_traceability.task_evidence_catalog;
    catalog[catalog.length - 1] = structuredClone(catalog[0]);
    await saveJson(root, workflowFixture, fixture);
    const result = run(root, ["scripts/harness_fixture_check.py"]);
    assert.equal(result.status, 1, result.stdout + result.stderr);
    assert.match(result.stdout, /task_evidence_catalog must contain exactly 74 unique task ids/i);
  });

  await t.test("distinguishes negative documentation but rejects an unsupported active concept", async () => {
    await writeFile(path.join(root, "commands/ideate.md"), `${pristineIdeate}\nUse baseline-manifest.json as current approval authority.\n`);
    const result = runWorkflow(root, "residual");
    assert.equal(result.status, 5);
    assert.match(result.payload.errors.join("\n"), /active violation/);
    assert.ok(result.payload.classifications.some((row) => row.path === "commands/ideate.md" && row.classification === "active violation"));
  });

  for (const mutation of [
    ["missing", (rows) => rows.slice(1), /missing=/],
    ["duplicate", (rows) => [...rows, structuredClone(rows[0])], /duplicate ids/],
    ["undefined", (rows) => [{ ...structuredClone(rows[0]), id: "UNDEFINED-999" }, ...rows.slice(1)], /undefined=/],
    ["ownership drift", (rows) => [{ ...structuredClone(rows[0]), owned_surfaces: ["src/cli.ts"], first_owner: "P5" }, ...rows.slice(1)], /ownership drift/],
  ]) {
    await t.test(`rejects aggregate requirement ${mutation[0]}`, async () => {
      const fixture = await loadJson(root, workflowFixture);
      fixture.aggregate_traceability.requirements = mutation[1](fixture.aggregate_traceability.requirements);
      await saveJson(root, workflowFixture, fixture);
      const result = runWorkflow(root, "scaffold");
      assert.equal(result.status, 5);
      assert.match(result.payload.errors.join("\n"), mutation[2]);
    });
  }

  const fixtureMutations = [
    ["continuity-memory-handoff-fixtures.yaml", (data) => { data.cases = data.cases.filter((row) => row.id !== "handoff-trigger"); }],
    ["dcp-removal-fixtures.yaml", (data) => { data.owner_package = "P5"; }],
    ["review-convergence-fixtures.yaml", (data) => { data.task_ids = data.task_ids.slice(1); }],
    ["upstream-reference-fixtures.yaml", (data) => { data.cases = data.cases.filter((row) => !(row.mapping === "matt-handoff" && row.kind === "negative")); }],
    ["graphify-local-review-fixtures.yaml", (data) => { data.cases = data.cases.filter((row) => row.category !== "architecture-routing"); }],
    ["generated-openspec-adapter-fixtures.yaml", (data) => { data.package_2_cases = data.package_2_cases.filter((row) => row.id !== "automation-modify-reject"); }],
  ];
  for (const [name, mutate] of fixtureMutations) {
    await t.test(`runs ${name} through the actual aggregate fixture validator`, async () => {
      const relative = `docs/harness/fixtures/${name}`;
      const data = await loadJson(root, relative);
      mutate(data);
      await saveJson(root, relative, data);
      const result = run(root, ["scripts/harness_fixture_check.py"]);
      assert.equal(result.status, 1, result.stdout + result.stderr);
      assert.match(result.stdout, new RegExp(name.replaceAll(".", "\\.")));
      await writeFile(path.join(root, relative), await readFile(path.join(sourceRoot, relative)), "utf8");
    });
  }

  await t.test("runs the P6 JSON-v3 fixture through the actual aggregate fixture validator", async () => {
    const relative = "docs/harness/fixtures/cross-worktree-permission-fixtures.yaml";
    const fixture = await loadJson(root, relative);
    assert.ok(fixture.historical_a30.case_ids.includes("effective-merged-tool-inventory"));
    fixture.historical_a30.case_ids = fixture.historical_a30.case_ids.filter(
      (caseId) => caseId !== "effective-merged-tool-inventory"
    );
    assert.equal(fixture.historical_a30.case_ids.includes("effective-merged-tool-inventory"), false);
    await saveJson(root, relative, fixture);
    const result = run(root, ["scripts/harness_fixture_check.py"]);
    assert.equal(result.status, 1, result.stdout + result.stderr);
    assert.match(result.stdout, /cross-worktree-permission-fixtures\.yaml/);
  });

  await t.test("returns exit 2 for usage and exit 5 with JSON for a malformed fixture", async () => {
    const usage = run(root, ["scripts/workflow_contract_check.py"]);
    assert.equal(usage.status, 2);
    const malformed = path.join(root, "docs/harness/fixtures/malformed-workflow.yaml");
    await writeFile(malformed, "{not-json\n", "utf8");
    const result = runWorkflow(root, "scaffold", "docs/harness/fixtures/malformed-workflow.yaml");
    assert.equal(result.status, 5);
    assert.equal(result.payload.profile, "scaffold");
    assert.equal(result.payload.status, "violation");
    assert.ok(result.payload.errors.length > 0);
  });
});
