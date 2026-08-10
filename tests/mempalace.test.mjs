import assert from "node:assert/strict";
import path from "node:path";
import test from "node:test";
import {
  MemPalaceUnavailableError,
  inspectMemPalace,
  legacyRoseMemoryMigrationPrompt,
  planMemPalaceMcpConfiguration,
  planMemPalaceOperation,
  requireMemPalaceMemory,
  resolvePalaceMapping,
  runMemPalaceInstall
} from "../dist/mempalace.js";

const repoRoot = process.cwd();

function compatibleRunner(calls) {
  return async (command, args) => {
    calls.push([command, args]);
    if (command === "python3" && args.join(" ") === "--version") return { code: 0, stdout: "Python 3.11.8", detail: "" };
    if (command === "mempalace" && args.join(" ") === "--version") return { code: 0, stdout: "mempalace 3.6.0", detail: "" };
    if (command === "mempalace" && args.join(" ") === "mcp --help") return { code: 0, stdout: "MCP commands are available", detail: "" };
    return { code: 64, stdout: "", detail: `unexpected fake invocation: ${command} ${args.join(" ")}` };
  };
}

test("MemPalace detection and MCP planning use only injected capability probes", async () => {
  const calls = [];
  const readiness = await inspectMemPalace(repoRoot, compatibleRunner(calls));
  const plan = await planMemPalaceMcpConfiguration({ ailiHome: repoRoot, adapter: "opencode", readiness });

  assert.equal(readiness.status, "compatible");
  assert.equal(readiness.observedVersion, "3.6.0");
  assert.equal(readiness.python.status, "compatible");
  assert.equal(readiness.capabilities.mcpConfiguration, "available");
  assert.equal(readiness.capabilities.toolCount, "runtime-detected");
  assert.equal(readiness.concurrentWriteSafety, "Unverified");
  assert.deepEqual(calls, [
    ["python3", ["--version"]],
    ["mempalace", ["--version"]],
    ["mempalace", ["mcp", "--help"]]
  ]);
  assert.equal(plan.status, "requires-approval");
  assert.equal(plan.approval, "fresh-exact-separate");
  assert.deepEqual(plan.configuration, { serverName: "mempalace", command: ["mempalace", "mcp"] });
});

test("MemPalace install preserves version drift and uses the exact isolated command only through a fake runner", async () => {
  const calls = [];
  const mismatchRunner = async (command, args) => {
    calls.push([command, args]);
    if (command === "python3") return { code: 0, stdout: "Python 3.11.8", detail: "" };
    if (command === "mempalace" && args.join(" ") === "--version") return { code: 0, stdout: "mempalace 3.7.0", detail: "" };
    throw new Error(`unexpected fake invocation: ${command} ${args.join(" ")}`);
  };
  const mismatch = await runMemPalaceInstall({ ailiHome: repoRoot, dryRun: false, enabled: true, runner: mismatchRunner });

  assert.equal(mismatch.status, "incompatible");
  assert.equal(calls.some(([command]) => command === "uv"), false);

  let installed = false;
  const installCalls = [];
  const installRunner = async (command, args) => {
    installCalls.push([command, args]);
    if (command === "python3") return { code: 0, stdout: "Python 3.11.8", detail: "" };
    if (command === "mempalace" && args.join(" ") === "--version") {
      return installed ? { code: 0, stdout: "mempalace 3.6.0", detail: "" } : { code: 127, stdout: "", detail: "mempalace command not found" };
    }
    if (command === "mempalace" && args.join(" ") === "mcp --help") return { code: 0, stdout: "MCP commands are available", detail: "" };
    if (command === "uv" && args.join(" ") === "tool install mempalace==3.6.0") {
      installed = true;
      return { code: 0, stdout: "", detail: "" };
    }
    throw new Error(`unexpected fake invocation: ${command} ${args.join(" ")}`);
  };
  const installedSummary = await runMemPalaceInstall({ ailiHome: repoRoot, dryRun: false, enabled: true, runner: installRunner });

  assert.equal(installedSummary.status, "installed");
  assert.deepEqual(installedSummary.argv, ["uv", "tool", "install", "mempalace==3.6.0"]);
  assert.deepEqual(installCalls[2], ["uv", ["tool", "install", "mempalace==3.6.0"]]);
});

test("MemPalace maps one user Palace without creating it and fails required work closed", async () => {
  const project = path.join("/workspace", "project-a");
  const otherProject = path.join("/workspace", "project-b");
  const mapping = resolvePalaceMapping({ projectRoot: project, agent: "rose", home: "/home/tester" });
  const other = resolvePalaceMapping({ projectRoot: otherProject, agent: "rose", home: "/home/tester" });
  const migration = legacyRoseMemoryMigrationPrompt(project);

  assert.equal(mapping.palacePath, "/home/tester/.mempalace/aili-palace");
  assert.notEqual(mapping.projectWing, other.projectWing);
  assert.equal(mapping.sharedWing, "shared");
  assert.equal(mapping.agentDiary, "agents/rose");
  assert.equal(migration.oneTime, true);
  assert.equal(migration.scope, "repository");
  assert.match(migration.prompt, /No data will be inspected, read, written, imported, mined, or deleted/);

  const readiness = await inspectMemPalace(repoRoot, compatibleRunner([]));
  await assert.rejects(
    async () => requireMemPalaceMemory({ readiness, mcp: { status: "already-configured" }, mapping, operation: "write", approvedOperation: "write", possibleConcurrentWriter: true }),
    MemPalaceUnavailableError
  );
  await assert.rejects(
    async () => requireMemPalaceMemory({ readiness, mcp: { status: "requires-approval" }, mapping, operation: "read", approvedOperation: "read" }),
    MemPalaceUnavailableError
  );
  assert.deepEqual(planMemPalaceOperation("delete"), {
    operation: "delete",
    approval: "fresh-exact-separate",
    refusalResult: "The requested MemPalace operation does not run; memory-dependent work remains unavailable or blocked without a fallback."
  });
});
