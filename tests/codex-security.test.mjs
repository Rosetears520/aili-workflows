import assert from "node:assert/strict";
import test from "node:test";
import {
  convergeCodexSecurityOutcomes,
  inspectCodexSecurity,
  planCodexSecurityReview,
  runCodexSecurityDryRuns
} from "../dist/codex-security.js";

const repoRoot = process.cwd();
const context = {
  repositoryRoot: "/worktrees/product/repository",
  enclosingWorktreeRoot: "/worktrees/product",
  privateOutput: { path: "/private/codex-security/run-7", declaredPrivate: true }
};

function compatibleRunner(calls) {
  return async (command, args, options = {}) => {
    calls.push({ command, args, options });
    if (command === "node" && args.join(" ") === "--version") return { code: 0, stdout: "v22.13.0", detail: "" };
    if (command === "python3" && args.join(" ") === "--version") return { code: 0, stdout: "Python 3.10.14", detail: "" };
    if (command === "npx" && args.join(" ") === "--no-install @openai/codex-security@0.1.8 --version") return { code: 0, stdout: "codex-security 0.1.8", detail: "" };
    if (command === "npx" && args.includes("--dry-run")) return { code: 0, stdout: "dry-run only", detail: "" };
    return { code: 64, stdout: "", detail: `unexpected fake invocation: ${command} ${args.join(" ")}` };
  };
}

test("Codex Security preflight and default dry-run use only the exact injected no-install commands", async () => {
  const calls = [];
  const summary = await runCodexSecurityDryRuns({
    ailiHome: repoRoot,
    context,
    target: { kind: "default-working-tree", base: "HEAD", untrackedPaths: ["src/new.ts", "docs/readme.md"] },
    runner: compatibleRunner(calls)
  });

  assert.equal(summary.package, "@openai/codex-security@0.1.8");
  assert.equal(summary.preflight.status, "ready");
  assert.equal(summary.preflight.credentials, "not-read-by-adapter");
  assert.deepEqual(summary.units.map((unit) => unit.id), [
    "tracked-working-tree:.",
    "untracked-path:src/new.ts",
    "untracked-path:docs/readme.md"
  ]);
  assert.equal(summary.units[0].previewApproval.operation, "preview-unit");
  assert.equal(summary.units[0].sourceTransmissionApproval.operation, "source-transmission-scan-unit");
  assert.notDeepEqual(summary.units[0].previewApproval, summary.units[0].sourceTransmissionApproval);
  assert.deepEqual(summary.sourceTransmissionBoundary, {
    status: "Unverified",
    properties: [
      "exact-transmitted-source-scope",
      "provider-endpoints",
      "provider-retention",
      "provider-encryption",
      "provider-telemetry",
      "proxy-behavior",
      "backend-untracked-file-inclusion"
    ]
  });
  assert.equal(summary.acquisitionApproval, undefined);
  assert.deepEqual(summary.dryRuns.map((entry) => entry.status), ["planned", "planned", "planned"]);
  assert.deepEqual(calls.slice(0, 3).map(({ command, args }) => [command, args]), [
    ["node", ["--version"]],
    ["python3", ["--version"]],
    ["npx", ["--no-install", "@openai/codex-security@0.1.8", "--version"]]
  ]);
  for (const call of calls.slice(3)) {
    assert.equal(call.command, "npx");
    assert.equal(call.args.includes("--dry-run"), true);
    assert.equal(call.args.includes("--auth"), false);
    assert.equal(call.options.cwd, context.repositoryRoot);
  }
  assert.deepEqual(calls[3].args, [
    "--no-install", "@openai/codex-security@0.1.8", "scan", context.repositoryRoot,
    "--working-tree", "--base", "HEAD", "--output-dir", context.privateOutput.path, "--dry-run"
  ]);
  assert.deepEqual(calls[4].args, [
    "--no-install", "@openai/codex-security@0.1.8", "scan", context.repositoryRoot,
    "--path", "src/new.ts", "--output-dir", context.privateOutput.path, "--dry-run"
  ]);
});

test("Codex Security normalizes path, diff, and whole-repository targets and rejects output inside either boundary", async () => {
  const paths = await planCodexSecurityReview(repoRoot, context, { kind: "paths", paths: ["src/auth", "/worktrees/product/repository/src/auth"] });
  const diff = await planCodexSecurityReview(repoRoot, context, { kind: "diff", base: "origin/main", head: "8f31d7a" });
  const whole = await planCodexSecurityReview(repoRoot, context, { kind: "whole-repository" });

  assert.deepEqual(paths.units.map((unit) => unit.repositoryRelativeIdentity), ["src/auth"]);
  assert.deepEqual(diff.units[0].cliArgs.slice(2, 6), ["--diff", "origin/main", "--head", "8f31d7a"]);
  assert.deepEqual(whole.units[0].cliArgs.slice(2, 4), ["--output-dir", context.privateOutput.path]);
  assert.match(paths.privateOutput.privacy, /Unverified/);

  await assert.rejects(
    () => planCodexSecurityReview(repoRoot, { ...context, privateOutput: { path: "/worktrees/product/repository/security-output", declaredPrivate: true } }, { kind: "whole-repository" }),
    /outside the scanned repository and its enclosing Git worktree/
  );
  await assert.rejects(
    () => planCodexSecurityReview(repoRoot, { ...context, privateOutput: { path: "/worktrees/product/security-output", declaredPrivate: true } }, { kind: "whole-repository" }),
    /outside the scanned repository and its enclosing Git worktree/
  );
  await assert.rejects(
    () => planCodexSecurityReview(repoRoot, context, { kind: "paths", paths: ["../outside"] }),
    /remain inside the repository/
  );
});

test("Codex Security convergence deduplicates repository identities, retains source-scan references, and marks incomplete units", () => {
  const converged = convergeCodexSecurityOutcomes(context, [
    {
      repositoryRelativeIdentity: "src/auth.ts",
      status: "planned",
      sourceScanReferences: ["scan-tracked", "scan-tracked"],
      outputReferences: [{ kind: "manifest", path: "/private/codex-security/run-7/scan-manifest.json" }]
    },
    {
      repositoryRelativeIdentity: "/worktrees/product/repository/src/auth.ts",
      status: "approved",
      sourceScanReferences: ["scan-path"],
      outputReferences: [
        { kind: "findings", path: "/private/codex-security/run-7/findings.json" },
        { kind: "report", path: "/worktrees/product/repository/report.md" }
      ]
    },
    { repositoryRelativeIdentity: "src/refused.ts", status: "refused", sourceScanReferences: ["scan-refused"] },
    { repositoryRelativeIdentity: "src/failed.ts", status: "failed" },
    { repositoryRelativeIdentity: "src/uncovered.ts", status: "uncovered" },
    { repositoryRelativeIdentity: "src/unsupported.ts", status: "unsupported" }
  ]);

  const auth = converged.find((entry) => entry.repositoryRelativeIdentity === "src/auth.ts");
  assert.deepEqual(auth.statuses, ["planned", "approved"]);
  assert.equal(auth.state, "pending");
  assert.deepEqual(auth.sourceScanReferences, ["scan-tracked", "scan-path"]);
  assert.deepEqual(auth.outputReferences, [
    { kind: "manifest", path: "/private/codex-security/run-7/scan-manifest.json" },
    { kind: "findings", path: "/private/codex-security/run-7/findings.json" }
  ]);
  assert.equal(auth.discardedOutputReferences, 1);
  assert.equal(auth.sourceBearingOutputCopied, false);
  for (const identity of ["src/refused.ts", "src/failed.ts", "src/uncovered.ts", "src/unsupported.ts"]) {
    assert.equal(converged.find((entry) => entry.repositoryRelativeIdentity === identity).state, "incomplete");
  }
});

test("Codex Security preflight fails closed on a missing exact CLI without a dry-run", async () => {
  const calls = [];
  const runner = async (command, args, options = {}) => {
    calls.push({ command, args, options });
    if (command === "node") return { code: 0, stdout: "v24.0.0", detail: "" };
    if (command === "python3") return { code: 0, stdout: "Python 3.11.0", detail: "" };
    return { code: 127, stdout: "", detail: "npx command not found" };
  };
  const readiness = await inspectCodexSecurity(repoRoot, runner);
  const summary = await runCodexSecurityDryRuns({
    ailiHome: repoRoot,
    context,
    target: { kind: "whole-repository" },
    runner
  });

  assert.equal(readiness.status, "missing");
  assert.equal(readiness.localExactCli, "unavailable");
  assert.equal(summary.dryRuns[0].status, "blocked");
  assert.deepEqual(summary.acquisitionApproval, {
    required: true,
    operation: "dependency-network-cache-write-acquisition",
    package: "@openai/codex-security@0.1.8",
    effects: ["dependency", "network", "cache-write"],
    separateFromSourceTransmissionApproval: true,
    execution: "not-executed-by-adapter"
  });
  assert.equal(calls.some((call) => call.args.includes("--dry-run")), false);
  assert.equal(calls.some((call) => call.command === "npx" && !call.args.includes("--no-install")), false);
});
