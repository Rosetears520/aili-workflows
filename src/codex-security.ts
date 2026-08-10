import { readFile } from "node:fs/promises";
import path from "node:path";

const CODEX_SECURITY_PACKAGE = "@openai/codex-security";
const CODEX_SECURITY_VERSION = "0.1.8";
const CODEX_SECURITY_PACKAGE_SPEC = `${CODEX_SECURITY_PACKAGE}@${CODEX_SECURITY_VERSION}`;
const SAFE_RESULT_REFERENCE_KINDS = ["manifest", "findings", "coverage", "report", "artifact"] as const;
const UNVERIFIED_SOURCE_TRANSMISSION_PROPERTIES = [
  "exact-transmitted-source-scope",
  "provider-endpoints",
  "provider-retention",
  "provider-encryption",
  "provider-telemetry",
  "proxy-behavior",
  "backend-untracked-file-inclusion"
] as const;
const INCOMPLETE_STATUSES = new Set<CodexSecurityUnitStatus>(["refused", "failed", "uncovered", "unsupported"]);

export type CodexSecurityCommandRunner = (
  command: string,
  args: string[],
  options: { cwd?: string }
) => Promise<CodexSecurityCommandResult>;

export interface CodexSecurityCommandResult {
  code: number | null;
  stdout: string;
  detail: string;
}

export interface CodexSecurityManifest {
  schemaVersion: 1;
  name: "codex-security";
  package: "@openai/codex-security";
  version: "0.1.8";
  packageSpec: "@openai/codex-security@0.1.8";
  launcher: {
    command: "npx";
    args: ["--no-install", "@openai/codex-security@0.1.8"];
  };
  preflight: {
    version: ["--version"];
    node: "22.13.0+ on 22.x, 24.x, or 26.x";
    python: ">=3.10";
  };
  scan: {
    command: "scan";
    outputDirectoryFlag: "--output-dir";
    dryRunFlag: "--dry-run";
    targets: {
      workingTree: ["--working-tree", "--base", "{base}"];
      path: ["--path", "{path}"];
      diff: ["--diff", "{base}", "--head", "{head}"];
      wholeRepository: [];
    };
  };
  safety: {
    credentialHandling: "adapter-never-reads-or-infers-credentials";
    execution: "injected-runner-only";
    output: "caller-declared-private-location-outside-repository-and-enclosing-worktree";
    storedResults: CodexSecuritySafeResultReferenceKind[];
    sourceBearingOutput: "reference-only-never-copy-into-repository-by-default";
    acquisition: "separate-dependency-network-cache-write-approval-when-exact-cli-is-unavailable";
    unverifiedSourceTransmission: CodexSecurityUnverifiedSourceTransmissionProperty[];
  };
}

export type CodexSecuritySafeResultReferenceKind = typeof SAFE_RESULT_REFERENCE_KINDS[number];
export type CodexSecurityUnverifiedSourceTransmissionProperty = typeof UNVERIFIED_SOURCE_TRANSMISSION_PROPERTIES[number];
export type CodexSecurityTarget =
  | { kind: "default-working-tree"; base?: string; untrackedPaths: string[] }
  | { kind: "paths"; paths: string[] }
  | { kind: "diff"; base: string; head: string }
  | { kind: "whole-repository" };
export type CodexSecurityUnitStatus = "planned" | "approved" | "completed" | "refused" | "failed" | "uncovered" | "unsupported";

export interface CodexSecurityPrivateOutput {
  path: string;
  declaredPrivate: true;
}

export interface CodexSecurityReviewContext {
  repositoryRoot: string;
  enclosingWorktreeRoot: string;
  privateOutput: CodexSecurityPrivateOutput;
}

export interface CodexSecurityRuntimeProbe {
  required: string;
  status: "compatible" | "missing" | "incompatible" | "invalid";
  observedVersion?: string;
}

export interface CodexSecurityReadiness {
  status: "ready" | "missing" | "incompatible" | "invalid";
  expectedVersion: "0.1.8";
  localExactCli: "available" | "unavailable";
  observedVersion?: string;
  node: CodexSecurityRuntimeProbe;
  python: CodexSecurityRuntimeProbe;
  credentials: "not-read-by-adapter";
  reason?: string;
}

export interface CodexSecurityApprovalRequirement {
  required: true;
  operation: "preview-unit" | "source-transmission-scan-unit";
  unitId: string;
}

export interface CodexSecurityDependencyAcquisitionApproval {
  required: true;
  operation: "dependency-network-cache-write-acquisition";
  package: "@openai/codex-security@0.1.8";
  effects: ["dependency", "network", "cache-write"];
  separateFromSourceTransmissionApproval: true;
  execution: "not-executed-by-adapter";
}

export interface CodexSecuritySourceTransmissionBoundary {
  status: "Unverified";
  properties: CodexSecurityUnverifiedSourceTransmissionProperty[];
}

export interface CodexSecurityScanUnit {
  id: string;
  kind: "tracked-working-tree" | "untracked-path" | "path" | "diff" | "whole-repository";
  repositoryRelativeIdentity: string;
  cliArgs: string[];
  dryRun: {
    command: "npx";
    args: string[];
    cwd: string;
    nonScanning: true;
  };
  previewApproval: CodexSecurityApprovalRequirement;
  sourceTransmissionApproval: CodexSecurityApprovalRequirement;
}

export interface CodexSecurityReviewPlan {
  package: "@openai/codex-security@0.1.8";
  repositoryRoot: string;
  enclosingWorktreeRoot: string;
  privateOutput: {
    path: string;
    privacy: "caller-declared-private; filesystem permissions and symlink topology Unverified";
    sourceBearingOutput: "reference-only-never-copy-into-repository-by-default";
  };
  credentials: "not-read-by-adapter";
  sourceTransmissionBoundary: CodexSecuritySourceTransmissionBoundary;
  units: CodexSecurityScanUnit[];
}

export interface CodexSecurityDryRunResult {
  unitId: string;
  status: "planned" | "blocked" | "failed";
  exitCode?: number | null;
  reason?: string;
}

export interface CodexSecurityDryRunSummary extends CodexSecurityReviewPlan {
  preflight: CodexSecurityReadiness;
  acquisitionApproval?: CodexSecurityDependencyAcquisitionApproval;
  dryRuns: CodexSecurityDryRunResult[];
}

export interface CodexSecuritySafeResultReference {
  kind: CodexSecuritySafeResultReferenceKind;
  path: string;
}

export interface CodexSecurityUnitOutcome {
  repositoryRelativeIdentity: string;
  status: CodexSecurityUnitStatus;
  sourceScanReferences?: string[];
  outputReferences?: CodexSecuritySafeResultReference[];
}

export interface CodexSecurityConvergedOutcome {
  repositoryRelativeIdentity: string;
  statuses: CodexSecurityUnitStatus[];
  state: "pending" | "complete" | "incomplete";
  sourceScanReferences: string[];
  outputReferences: CodexSecuritySafeResultReference[];
  discardedOutputReferences: number;
  sourceBearingOutputCopied: false;
}

export async function loadCodexSecurityManifest(ailiHome: string): Promise<CodexSecurityManifest> {
  const manifestPath = path.join(ailiHome, "manifests", "codex-security-tool.json");
  let raw: unknown;
  try {
    raw = JSON.parse(await readFile(manifestPath, "utf8"));
  } catch (error: unknown) {
    throw new Error(`Unable to load Codex Security tool manifest ${manifestPath}: ${error instanceof Error ? error.message : String(error)}`);
  }
  if (!isCodexSecurityManifest(raw)) {
    throw new Error(`Codex Security tool manifest differs from the fixed standalone CLI contract: ${manifestPath}`);
  }
  return raw;
}

export async function inspectCodexSecurity(
  ailiHome: string,
  runner: CodexSecurityCommandRunner
): Promise<CodexSecurityReadiness> {
  const manifest = await loadCodexSecurityManifest(ailiHome);
  const nodeProbe = await safelyRun(runner, "node", ["--version"]);
  const pythonProbe = await safelyRun(runner, "python3", ["--version"]);
  const cliProbe = await safelyRun(runner, manifest.launcher.command, [...manifest.launcher.args, ...manifest.preflight.version]);
  const node = inspectNode(nodeProbe);
  const python = inspectPython(pythonProbe);
  const observedVersion = parseVersion(cliProbe.stdout);

  if (cliProbe.code !== 0) {
    return unavailableReadiness("missing", "unavailable", node, python, cliProbe.detail || "The exact Codex Security CLI launcher was unavailable.");
  }
  if (!observedVersion) {
    return unavailableReadiness("invalid", "available", node, python, "Codex Security --version output did not contain exactly one semantic version.");
  }
  if (observedVersion !== manifest.version) {
    return unavailableReadiness("incompatible", "available", node, python, `Codex Security version ${observedVersion} differs from the exact supported version ${manifest.version}.`, observedVersion);
  }
  if (node.status !== "compatible") {
    return unavailableReadiness(node.status === "missing" ? "missing" : node.status, "available", node, python, `Node ${manifest.preflight.node} is required.`, observedVersion);
  }
  if (python.status !== "compatible") {
    return unavailableReadiness(python.status === "missing" ? "missing" : python.status, "available", node, python, `Python ${manifest.preflight.python} is required.`, observedVersion);
  }
  return {
    status: "ready",
    expectedVersion: manifest.version,
    localExactCli: "available",
    observedVersion,
    node,
    python,
    credentials: "not-read-by-adapter"
  };
}

export async function planCodexSecurityReview(
  ailiHome: string,
  context: CodexSecurityReviewContext,
  target: CodexSecurityTarget
): Promise<CodexSecurityReviewPlan> {
  const manifest = await loadCodexSecurityManifest(ailiHome);
  const boundaries = normalizeBoundaries(context);
  const unitInputs = normalizeTarget(target, boundaries.repositoryRoot);
  const units = unitInputs.map((unit) => buildScanUnit(manifest, boundaries, unit));
  return {
    package: manifest.packageSpec,
    repositoryRoot: boundaries.repositoryRoot,
    enclosingWorktreeRoot: boundaries.enclosingWorktreeRoot,
    privateOutput: {
      path: boundaries.privateOutput,
      privacy: "caller-declared-private; filesystem permissions and symlink topology Unverified",
      sourceBearingOutput: "reference-only-never-copy-into-repository-by-default"
    },
    credentials: "not-read-by-adapter",
    sourceTransmissionBoundary: {
      status: "Unverified",
      properties: [...UNVERIFIED_SOURCE_TRANSMISSION_PROPERTIES]
    },
    units
  };
}

export async function runCodexSecurityDryRuns(options: {
  ailiHome: string;
  context: CodexSecurityReviewContext;
  target: CodexSecurityTarget;
  runner: CodexSecurityCommandRunner;
}): Promise<CodexSecurityDryRunSummary> {
  const plan = await planCodexSecurityReview(options.ailiHome, options.context, options.target);
  const preflight = await inspectCodexSecurity(options.ailiHome, options.runner);
  const acquisitionApproval = preflight.localExactCli === "unavailable" ? buildAcquisitionApproval() : undefined;
  if (preflight.status !== "ready") {
    return {
      ...plan,
      preflight,
      ...(acquisitionApproval ? { acquisitionApproval } : {}),
      dryRuns: plan.units.map((unit) => ({
        unitId: unit.id,
        status: "blocked",
        reason: `Exact local preflight is ${preflight.status}: ${preflight.reason ?? "not ready"}`
      }))
    };
  }
  const dryRuns = await Promise.all(plan.units.map(async (unit) => {
    const result = await safelyRun(options.runner, unit.dryRun.command, unit.dryRun.args, { cwd: unit.dryRun.cwd });
    return result.code === 0
      ? { unitId: unit.id, status: "planned" as const, exitCode: result.code }
      : { unitId: unit.id, status: "failed" as const, exitCode: result.code, reason: result.detail || `Dry-run exited with ${result.code ?? "unknown status"}.` };
  }));
  return { ...plan, preflight, dryRuns };
}

export function convergeCodexSecurityOutcomes(
  context: CodexSecurityReviewContext,
  outcomes: CodexSecurityUnitOutcome[]
): CodexSecurityConvergedOutcome[] {
  const boundaries = normalizeBoundaries(context);
  const merged = new Map<string, CodexSecurityConvergedOutcome>();
  for (const outcome of outcomes) {
    const identity = normalizeRepositoryIdentity(boundaries.repositoryRoot, outcome.repositoryRelativeIdentity);
    const current = merged.get(identity) ?? {
      repositoryRelativeIdentity: identity,
      statuses: [],
      state: "pending" as const,
      sourceScanReferences: [],
      outputReferences: [],
      discardedOutputReferences: 0,
      sourceBearingOutputCopied: false as const
    };
    current.statuses.push(outcome.status);
    current.sourceScanReferences = uniqueStrings([...current.sourceScanReferences, ...(outcome.sourceScanReferences ?? [])]);
    for (const reference of outcome.outputReferences ?? []) {
      if (isSafeOutputReference(reference, boundaries.privateOutput)) {
        if (!current.outputReferences.some((entry) => entry.kind === reference.kind && entry.path === path.resolve(reference.path))) {
          current.outputReferences.push({ kind: reference.kind, path: path.resolve(reference.path) });
        }
      } else {
        current.discardedOutputReferences += 1;
      }
    }
    current.state = convergenceState(current.statuses);
    merged.set(identity, current);
  }
  return [...merged.values()].sort((left, right) => left.repositoryRelativeIdentity.localeCompare(right.repositoryRelativeIdentity));
}

interface NormalizedBoundaries {
  repositoryRoot: string;
  enclosingWorktreeRoot: string;
  privateOutput: string;
}

interface NormalizedUnitInput {
  id: string;
  kind: CodexSecurityScanUnit["kind"];
  repositoryRelativeIdentity: string;
  targetArgs: string[];
}

function normalizeBoundaries(context: CodexSecurityReviewContext): NormalizedBoundaries {
  const repositoryRoot = requireAbsolutePath("repository root", context.repositoryRoot);
  const enclosingWorktreeRoot = requireAbsolutePath("enclosing Git worktree root", context.enclosingWorktreeRoot);
  const privateOutput = requireAbsolutePath("private output location", context.privateOutput.path);
  if (context.privateOutput.declaredPrivate !== true) throw new Error("Codex Security output location must be explicitly declared private.");
  if (!isPathOrDescendant(repositoryRoot, enclosingWorktreeRoot)) {
    throw new Error(`Codex Security repository root must be inside the declared enclosing Git worktree: ${repositoryRoot}`);
  }
  if (isPathOrDescendant(privateOutput, repositoryRoot) || isPathOrDescendant(privateOutput, enclosingWorktreeRoot)) {
    throw new Error(`Codex Security private output location must be outside the scanned repository and its enclosing Git worktree: ${privateOutput}`);
  }
  return { repositoryRoot, enclosingWorktreeRoot, privateOutput };
}

function normalizeTarget(target: CodexSecurityTarget, repositoryRoot: string): NormalizedUnitInput[] {
  switch (target.kind) {
    case "default-working-tree": {
      const base = normalizeRevision(target.base ?? "HEAD", "working-tree base");
      const untracked = uniqueStrings(target.untrackedPaths.map((entry) => normalizeRepositoryIdentity(repositoryRoot, entry)));
      return [
        {
          id: "tracked-working-tree:.",
          kind: "tracked-working-tree",
          repositoryRelativeIdentity: ".",
          targetArgs: ["--working-tree", "--base", base]
        },
        ...untracked.map((entry) => ({
          id: `untracked-path:${entry}`,
          kind: "untracked-path" as const,
          repositoryRelativeIdentity: entry,
          targetArgs: ["--path", entry]
        }))
      ];
    }
    case "paths": {
      const paths = uniqueStrings(target.paths.map((entry) => normalizeRepositoryIdentity(repositoryRoot, entry)));
      if (paths.length === 0) throw new Error("Codex Security path target requires at least one repository-relative path.");
      return paths.map((entry) => ({
        id: `path:${entry}`,
        kind: "path" as const,
        repositoryRelativeIdentity: entry,
        targetArgs: ["--path", entry]
      }));
    }
    case "diff": {
      const base = normalizeRevision(target.base, "diff base");
      const head = normalizeRevision(target.head, "diff head");
      return [{
        id: `diff:${base}...${head}`,
        kind: "diff",
        repositoryRelativeIdentity: ".",
        targetArgs: ["--diff", base, "--head", head]
      }];
    }
    case "whole-repository":
      return [{ id: "whole-repository:.", kind: "whole-repository", repositoryRelativeIdentity: ".", targetArgs: [] }];
  }
}

function buildScanUnit(
  manifest: CodexSecurityManifest,
  boundaries: NormalizedBoundaries,
  input: NormalizedUnitInput
): CodexSecurityScanUnit {
  const cliArgs = [
    manifest.scan.command,
    boundaries.repositoryRoot,
    ...input.targetArgs,
    manifest.scan.outputDirectoryFlag,
    boundaries.privateOutput,
    manifest.scan.dryRunFlag
  ];
  return {
    id: input.id,
    kind: input.kind,
    repositoryRelativeIdentity: input.repositoryRelativeIdentity,
    cliArgs,
    dryRun: {
      command: manifest.launcher.command,
      args: [...manifest.launcher.args, ...cliArgs],
      cwd: boundaries.repositoryRoot,
      nonScanning: true
    },
    previewApproval: { required: true, operation: "preview-unit", unitId: input.id },
    sourceTransmissionApproval: { required: true, operation: "source-transmission-scan-unit", unitId: input.id }
  };
}

function isCodexSecurityManifest(raw: unknown): raw is CodexSecurityManifest {
  if (typeof raw !== "object" || raw === null) return false;
  const manifest = raw as Partial<CodexSecurityManifest>;
  return manifest.schemaVersion === 1
    && manifest.name === "codex-security"
    && manifest.package === CODEX_SECURITY_PACKAGE
    && manifest.version === CODEX_SECURITY_VERSION
    && manifest.packageSpec === CODEX_SECURITY_PACKAGE_SPEC
    && manifest.launcher?.command === "npx"
    && equalStrings(manifest.launcher.args, ["--no-install", CODEX_SECURITY_PACKAGE_SPEC])
    && equalStrings(manifest.preflight?.version, ["--version"])
    && manifest.preflight?.node === "22.13.0+ on 22.x, 24.x, or 26.x"
    && manifest.preflight?.python === ">=3.10"
    && manifest.scan?.command === "scan"
    && manifest.scan.outputDirectoryFlag === "--output-dir"
    && manifest.scan.dryRunFlag === "--dry-run"
    && equalStrings(manifest.scan.targets?.workingTree, ["--working-tree", "--base", "{base}"])
    && equalStrings(manifest.scan.targets?.path, ["--path", "{path}"])
    && equalStrings(manifest.scan.targets?.diff, ["--diff", "{base}", "--head", "{head}"])
    && equalStrings(manifest.scan.targets?.wholeRepository, [])
    && manifest.safety?.credentialHandling === "adapter-never-reads-or-infers-credentials"
    && manifest.safety.execution === "injected-runner-only"
    && manifest.safety.output === "caller-declared-private-location-outside-repository-and-enclosing-worktree"
    && equalStrings(manifest.safety.storedResults, [...SAFE_RESULT_REFERENCE_KINDS])
    && manifest.safety.sourceBearingOutput === "reference-only-never-copy-into-repository-by-default"
    && manifest.safety.acquisition === "separate-dependency-network-cache-write-approval-when-exact-cli-is-unavailable"
    && equalStrings(manifest.safety.unverifiedSourceTransmission, [...UNVERIFIED_SOURCE_TRANSMISSION_PROPERTIES]);
}

function inspectNode(result: CodexSecurityCommandResult): CodexSecurityRuntimeProbe {
  const observedVersion = parseVersion(result.stdout);
  if (result.code !== 0) return { required: "22.13.0+ on 22.x, 24.x, or 26.x", status: "missing" };
  if (!observedVersion) return { required: "22.13.0+ on 22.x, 24.x, or 26.x", status: "invalid" };
  const [major, minor] = observedVersion.split(".").map((entry) => Number.parseInt(entry, 10));
  const compatible = major === 22 ? minor >= 13 : major === 24 || major === 26;
  return { required: "22.13.0+ on 22.x, 24.x, or 26.x", observedVersion, status: compatible ? "compatible" : "incompatible" };
}

function inspectPython(result: CodexSecurityCommandResult): CodexSecurityRuntimeProbe {
  const observedVersion = parseVersion(result.stdout);
  if (result.code !== 0) return { required: ">=3.10", status: "missing" };
  if (!observedVersion) return { required: ">=3.10", status: "invalid" };
  const [major, minor] = observedVersion.split(".").map((entry) => Number.parseInt(entry, 10));
  return { required: ">=3.10", observedVersion, status: major > 3 || (major === 3 && minor >= 10) ? "compatible" : "incompatible" };
}

function unavailableReadiness(
  status: Exclude<CodexSecurityReadiness["status"], "ready">,
  localExactCli: CodexSecurityReadiness["localExactCli"],
  node: CodexSecurityRuntimeProbe,
  python: CodexSecurityRuntimeProbe,
  reason: string,
  observedVersion?: string
): CodexSecurityReadiness {
  return {
    status,
    expectedVersion: CODEX_SECURITY_VERSION,
    localExactCli,
    ...(observedVersion ? { observedVersion } : {}),
    node,
    python,
    credentials: "not-read-by-adapter",
    reason
  };
}

function buildAcquisitionApproval(): CodexSecurityDependencyAcquisitionApproval {
  return {
    required: true,
    operation: "dependency-network-cache-write-acquisition",
    package: CODEX_SECURITY_PACKAGE_SPEC,
    effects: ["dependency", "network", "cache-write"],
    separateFromSourceTransmissionApproval: true,
    execution: "not-executed-by-adapter"
  };
}

function normalizeRepositoryIdentity(repositoryRoot: string, value: string): string {
  if (!value || value.includes("\0")) throw new Error("Codex Security repository-relative identity must be non-empty and contain no NUL byte.");
  const candidate = path.isAbsolute(value) ? path.resolve(value) : path.resolve(repositoryRoot, value);
  if (!isPathOrDescendant(candidate, repositoryRoot)) {
    throw new Error(`Codex Security target must remain inside the repository: ${value}`);
  }
  const relative = path.relative(repositoryRoot, candidate);
  return relative === "" ? "." : relative.split(path.sep).join("/");
}

function normalizeRevision(value: string, label: string): string {
  const normalized = value.trim();
  if (!normalized || normalized.startsWith("-") || normalized.includes("\0") || normalized.includes("\n") || normalized.includes("\r")) {
    throw new Error(`Codex Security ${label} must be a non-empty revision value, not an option.`);
  }
  return normalized;
}

function requireAbsolutePath(label: string, value: string): string {
  if (!value || !path.isAbsolute(value)) throw new Error(`Codex Security ${label} must be an absolute path: ${value || "<empty>"}`);
  return path.resolve(value);
}

function isSafeOutputReference(reference: CodexSecuritySafeResultReference, privateOutput: string): boolean {
  return SAFE_RESULT_REFERENCE_KINDS.includes(reference.kind) && path.isAbsolute(reference.path) && isPathOrDescendant(path.resolve(reference.path), privateOutput);
}

function convergenceState(statuses: CodexSecurityUnitStatus[]): CodexSecurityConvergedOutcome["state"] {
  if (statuses.some((status) => INCOMPLETE_STATUSES.has(status))) return "incomplete";
  return statuses.every((status) => status === "completed") ? "complete" : "pending";
}

function parseVersion(output: string): string | undefined {
  const matches = [...output.matchAll(/(?:^|[^0-9])([0-9]+\.[0-9]+\.[0-9]+)(?=$|[^0-9])/gu)].map((match) => match[1]);
  const unique = [...new Set(matches)];
  return unique.length === 1 ? unique[0] : undefined;
}

function equalStrings(value: unknown, expected: readonly string[]): boolean {
  return Array.isArray(value) && value.length === expected.length && value.every((entry, index) => entry === expected[index]);
}

function uniqueStrings(values: string[]): string[] {
  return [...new Set(values)];
}

function isPathOrDescendant(candidate: string, parent: string): boolean {
  const relative = path.relative(parent, candidate);
  return relative === "" || (relative !== "" && !relative.startsWith("..") && !path.isAbsolute(relative));
}

async function safelyRun(
  runner: CodexSecurityCommandRunner,
  command: string,
  args: string[],
  options: { cwd?: string } = {}
): Promise<CodexSecurityCommandResult> {
  try {
    return await runner(command, args, options);
  } catch (error: unknown) {
    return { code: null, stdout: "", detail: error instanceof Error ? error.message : String(error) };
  }
}
