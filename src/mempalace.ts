import { createHash } from "node:crypto";
import { spawn } from "node:child_process";
import { readFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";

const MEM_PALACE_PACKAGE = "mempalace";
const MEM_PALACE_VERSION = "3.6.0";
const MEM_PALACE_PACKAGE_SPEC = `${MEM_PALACE_PACKAGE}==${MEM_PALACE_VERSION}`;
const MINIMUM_PYTHON = [3, 9] as const;
const MEM_PALACE_OPERATIONS = [
  "install",
  "initialize",
  "mcp-configure",
  "model-download",
  "mining",
  "hooks",
  "read",
  "write",
  "coordination-write",
  "logstream-write",
  "delete"
] as const;

export type MemPalaceOperation = typeof MEM_PALACE_OPERATIONS[number];
export type MemPalaceReadinessStatus = "compatible" | "missing" | "incompatible" | "invalid";
export type MemPalaceMcpPlanStatus = "requires-approval" | "already-configured" | "unavailable" | "unsupported";
export type MemPalaceCommandRunner = (command: string, args: string[]) => Promise<MemPalaceCommandResult>;

export interface MemPalaceCommandResult {
  code: number | null;
  stdout: string;
  detail: string;
}

export interface MemPalaceManifest {
  schemaVersion: 1;
  name: "mempalace";
  package: "mempalace";
  version: "3.6.0";
  packageSpec: "mempalace==3.6.0";
  python: ">=3.9";
  install: {
    command: "uv";
    args: ["tool", "install", "mempalace==3.6.0"];
    effects: string[];
  };
  compatibility: {
    policy: "exact-version";
    mismatch: "report-only-no-silent-replacement";
    upgrade: "requires-manifest-change-refreshed-official-evidence-and-compatibility-tests";
  };
  capabilityDetection: {
    version: ["--version"];
    mcp: ["mcp", "--help"];
    toolCount: "runtime-detected";
  };
  canonicalPalace: {
    defaultRelativePath: ".mempalace/aili-palace";
    overrideEnvironment: "AILI_MEMPALACE_PALACE_PATH";
  };
  operations: MemPalaceOperation[];
}

export interface MemPalaceReadiness {
  status: MemPalaceReadinessStatus;
  expectedVersion: string;
  observedVersion?: string;
  python: {
    required: string;
    observedVersion?: string;
    status: "compatible" | "missing" | "incompatible" | "invalid";
  };
  capabilities: {
    mcpConfiguration: "available" | "unavailable";
    toolCount: "runtime-detected";
  };
  concurrentWriteSafety: "Unverified";
  reason?: string;
}

export interface MemPalaceMcpPlan {
  status: MemPalaceMcpPlanStatus;
  adapter: string;
  operation: "mcp-configure";
  approval: "fresh-exact-separate";
  configuration?: {
    serverName: string;
    command: string[];
  };
  reason: string;
  refusalResult: string;
  concurrentWriteSafety: "Unverified";
}

export interface MemPalaceInstallSummary {
  status: "planned" | "skipped" | "preserved" | "installed" | "incompatible" | "failed";
  package: string;
  expectedVersion: string;
  command: string;
  argv: string[];
  effects: string[];
  readiness: MemPalaceReadiness;
  reason: string;
}

export interface MemPalaceInstallOptions {
  ailiHome: string;
  dryRun: boolean;
  enabled?: boolean;
  skip?: boolean;
  runner?: MemPalaceCommandRunner;
}

export interface PalaceMappingOptions {
  projectRoot: string;
  agent: string;
  home?: string;
  palacePath?: string;
}

export interface PalaceMapping {
  palacePath: string;
  projectRoot: string;
  projectWing: string;
  sharedWing: "shared";
  agentDiary: string;
}

export interface MemoryRequirement {
  readiness: MemPalaceReadiness;
  mcp: Pick<MemPalaceMcpPlan, "status">;
  mapping: PalaceMapping;
  operation: Exclude<MemPalaceOperation, "install" | "mcp-configure">;
  approvedOperation?: MemPalaceOperation;
  possibleConcurrentWriter?: boolean;
}

export class MemPalaceUnavailableError extends Error {
  readonly code = "MEMPALACE_MEMORY_BLOCKED";
}

export async function loadMemPalaceManifest(ailiHome: string): Promise<MemPalaceManifest> {
  const manifestPath = path.join(ailiHome, "manifests", "mempalace-tool.json");
  let raw: unknown;
  try {
    raw = JSON.parse(await readFile(manifestPath, "utf8"));
  } catch (error: unknown) {
    throw new Error(`Unable to load MemPalace tool manifest ${manifestPath}: ${error instanceof Error ? error.message : String(error)}`);
  }
  if (!isMemPalaceManifest(raw)) throw new Error(`MemPalace tool manifest differs from the fixed provider contract: ${manifestPath}`);
  return raw;
}

export async function inspectMemPalace(ailiHome: string, runner: MemPalaceCommandRunner = runMemPalaceCommand): Promise<MemPalaceReadiness> {
  const manifest = await loadMemPalaceManifest(ailiHome);
  const pythonProbe = await runner("python3", ["--version"]);
  const python = inspectPython(pythonProbe.stdout, pythonProbe.code);
  if (python.status !== "compatible") {
    return unavailableReadiness(manifest, "incompatible", python, `Python ${manifest.python} is required: ${python.status === "missing" ? "python3 was not found" : "the observed Python version is incompatible or invalid"}.`);
  }

  const versionProbe = await runner(manifest.package, manifest.capabilityDetection.version);
  if (versionProbe.code !== 0) {
    return unavailableReadiness(manifest, "missing", python, versionProbe.detail || "mempalace command not found");
  }
  const observedVersion = parseVersion(versionProbe.stdout);
  if (!observedVersion) {
    return unavailableReadiness(manifest, "invalid", python, "MemPalace --version output did not contain exactly one semantic version.");
  }
  if (observedVersion !== manifest.version) {
    return unavailableReadiness(manifest, "incompatible", python, `MemPalace version ${observedVersion} differs from the exact supported version ${manifest.version}.`, observedVersion);
  }

  const mcpProbe = await runner(manifest.package, manifest.capabilityDetection.mcp);
  return {
    status: "compatible",
    expectedVersion: manifest.version,
    observedVersion,
    python,
    capabilities: {
      mcpConfiguration: mcpProbe.code === 0 ? "available" : "unavailable",
      toolCount: "runtime-detected"
    },
    concurrentWriteSafety: "Unverified",
    ...(mcpProbe.code === 0 ? {} : { reason: mcpProbe.detail || "MemPalace MCP capability was not detected." })
  };
}

export async function planMemPalaceMcpConfiguration(options: {
  ailiHome: string;
  adapter: string;
  readiness: MemPalaceReadiness;
  configured?: boolean;
}): Promise<MemPalaceMcpPlan> {
  const definition = await loadMemPalaceAdapterDefinition(options.ailiHome, options.adapter);
  const refusalResult = "MemPalace remains unconfigured; memory-dependent operations fail closed without a fallback.";
  const mcp = definition.mcp;
  if (!mcp.supported) {
    return {
      status: "unsupported",
      adapter: options.adapter,
      operation: "mcp-configure",
      approval: "fresh-exact-separate",
      reason: mcp.reason ?? "This adapter has no supported MemPalace MCP configuration path.",
      refusalResult,
      concurrentWriteSafety: "Unverified"
    };
  }
  if (options.readiness.status !== "compatible" || options.readiness.capabilities.mcpConfiguration !== "available") {
    return {
      status: "unavailable",
      adapter: options.adapter,
      operation: "mcp-configure",
      approval: "fresh-exact-separate",
      reason: options.readiness.reason ?? "Compatible MemPalace MCP capability is unavailable.",
      refusalResult,
      concurrentWriteSafety: "Unverified"
    };
  }
  if (!mcp.serverName || !mcp.command) throw new Error(`Supported MemPalace adapter definition is incomplete: ${options.adapter}`);
  const configuration = { serverName: mcp.serverName, command: mcp.command };
  return {
    status: options.configured ? "already-configured" : "requires-approval",
    adapter: options.adapter,
    operation: "mcp-configure",
    approval: "fresh-exact-separate",
    configuration,
    reason: options.configured
      ? "Existing supported MemPalace MCP configuration was observed; no configuration command is planned."
      : "Compatible provider capability was detected; applying this MCP configuration requires a separate exact approval.",
    refusalResult,
    concurrentWriteSafety: "Unverified"
  };
}

export function resolvePalaceMapping(options: PalaceMappingOptions): PalaceMapping {
  const projectRoot = path.resolve(options.projectRoot);
  if (!path.isAbsolute(options.projectRoot)) throw new Error(`MemPalace project root must be absolute: ${options.projectRoot}`);
  const palacePath = resolveCanonicalPalacePath(options);
  const projectWing = `project-${createHash("sha256").update(projectRoot).digest("hex").slice(0, 16)}`;
  return {
    palacePath,
    projectRoot,
    projectWing,
    sharedWing: "shared",
    agentDiary: `agents/${normalizeAgentName(options.agent)}`
  };
}

export function resolveCanonicalPalacePath(options: Pick<PalaceMappingOptions, "home" | "palacePath"> = {}): string {
  const home = options.home ?? process.env.HOME ?? os.homedir();
  if (!path.isAbsolute(home)) throw new Error(`MemPalace HOME must be absolute: ${home || "<empty>"}`);
  const resolvedHome = path.resolve(home);
  if (resolvedHome === path.parse(resolvedHome).root || resolvedHome === path.resolve(os.tmpdir())) {
    throw new Error(`Refusing unsafe MemPalace HOME: ${resolvedHome}`);
  }
  const configured = options.palacePath ?? process.env.AILI_MEMPALACE_PALACE_PATH;
  if (configured && !path.isAbsolute(configured)) throw new Error(`MemPalace Palace path must be absolute: ${configured}`);
  const palacePath = configured ? path.resolve(configured) : path.join(resolvedHome, ".mempalace", "aili-palace");
  if (palacePath === path.parse(palacePath).root || palacePath === path.resolve(os.tmpdir())) {
    throw new Error(`Refusing unsafe MemPalace Palace path: ${palacePath}`);
  }
  return palacePath;
}

export function requireMemPalaceMemory(options: MemoryRequirement): void {
  if (options.readiness.status !== "compatible") {
    throw new MemPalaceUnavailableError(`MemPalace memory operation ${options.operation} is blocked: ${options.readiness.reason ?? options.readiness.status}. No fallback is available.`);
  }
  if (options.mcp.status !== "already-configured") {
    throw new MemPalaceUnavailableError(`MemPalace memory operation ${options.operation} is blocked: supported MCP configuration is required and currently ${options.mcp.status}. No fallback is available.`);
  }
  if (!path.isAbsolute(options.mapping.palacePath) || !options.mapping.projectWing || options.mapping.sharedWing !== "shared" || !options.mapping.agentDiary.startsWith("agents/")) {
    throw new MemPalaceUnavailableError(`MemPalace memory operation ${options.operation} is blocked: canonical Palace/Wing/diary mapping is unavailable. No fallback is available.`);
  }
  if (options.possibleConcurrentWriter) {
    throw new MemPalaceUnavailableError(`MemPalace memory operation ${options.operation} is blocked: concurrent multi-process safety is Unverified and another supported client may write.`);
  }
  if (options.approvedOperation !== options.operation) {
    throw new MemPalaceUnavailableError(`MemPalace memory operation ${options.operation} requires its own fresh exact approval; installation or MCP configuration approval does not apply.`);
  }
}

export function planMemPalaceOperation(operation: MemPalaceOperation): {
  operation: MemPalaceOperation;
  approval: "fresh-exact-separate";
  refusalResult: string;
} {
  return {
    operation,
    approval: "fresh-exact-separate",
    refusalResult: "The requested MemPalace operation does not run; memory-dependent work remains unavailable or blocked without a fallback."
  };
}

export function legacyRoseMemoryMigrationPrompt(projectRoot: string): {
  scope: "repository";
  scopeKey: string;
  oneTime: true;
  prompt: string;
} {
  if (!path.isAbsolute(projectRoot)) throw new Error(`Legacy memory migration scope must be an absolute repository root: ${projectRoot}`);
  const resolved = path.resolve(projectRoot);
  const scopeKey = createHash("sha256").update(resolved).digest("hex").slice(0, 16);
  return {
    scope: "repository",
    scopeKey,
    oneTime: true,
    prompt: `One-time MemPalace migration boundary for repository ${resolved}: legacy rose-memory data is preserved. Do you want to authorize a separate migration plan? No data will be inspected, read, written, imported, mined, or deleted until a separate exact operation is approved.`
  };
}

export async function runMemPalaceInstall(options: MemPalaceInstallOptions): Promise<MemPalaceInstallSummary> {
  const manifest = await loadMemPalaceManifest(options.ailiHome);
  const runner = options.runner ?? runMemPalaceCommand;
  const command = [manifest.install.command, ...manifest.install.args].join(" ");
  const base = {
    package: manifest.packageSpec,
    expectedVersion: manifest.version,
    command,
    argv: [manifest.install.command, ...manifest.install.args],
    effects: manifest.install.effects
  };
  const unprobed = unavailableReadiness(manifest, "missing", { required: manifest.python, status: "invalid" }, "MemPalace was not probed because its install operation was not separately enabled.");
  if (options.skip) return { status: "skipped", ...base, readiness: unprobed, reason: "MemPalace explicitly skipped; no probe or install command ran." };
  if (!options.enabled) return { status: "planned", ...base, readiness: unprobed, reason: "MemPalace is default-selected but requires a separate exact install approval; no probe or install command ran." };
  if (options.dryRun) return { status: "planned", ...base, readiness: unprobed, reason: "Would probe Python and the exact MemPalace version, then run the official isolated install only when absent; dry-run ran no command." };

  const current = await inspectMemPalace(options.ailiHome, runner);
  if (current.status === "compatible") return { status: "preserved", ...base, readiness: current, reason: "Existing exact compatible MemPalace installation was preserved; uv did not run." };
  if (current.status === "incompatible") return { status: "incompatible", ...base, readiness: current, reason: "Observed MemPalace or Python compatibility mismatch was reported; the installer will not silently replace it." };
  const installed = await runner(manifest.install.command, manifest.install.args);
  if (installed.code !== 0) return { status: "failed", ...base, readiness: current, reason: installed.detail || `MemPalace install exited with ${installed.code ?? "unknown status"}.` };
  const verified = await inspectMemPalace(options.ailiHome, runner);
  if (verified.status !== "compatible") return { status: "failed", ...base, readiness: verified, reason: `MemPalace install exited successfully but exact compatibility verification was ${verified.status}.` };
  return { status: "installed", ...base, readiness: verified, reason: "Official isolated install passed exact-version and Python compatibility verification." };
}

interface MemPalaceAdapterDefinition {
  schemaVersion: 1;
  adapter: string;
  provider: "mempalace";
  mcp: {
    supported: boolean;
    serverName?: string;
    command?: string[];
    reason?: string;
    toolCount: "runtime-detected";
  };
}

async function loadMemPalaceAdapterDefinition(ailiHome: string, adapter: string): Promise<MemPalaceAdapterDefinition> {
  const definitionPath = path.join(ailiHome, "adapters", adapter, "mempalace.json");
  let raw: unknown;
  try {
    raw = JSON.parse(await readFile(definitionPath, "utf8"));
  } catch (error: unknown) {
    return {
      schemaVersion: 1,
      adapter,
      provider: "mempalace",
      mcp: { supported: false, reason: `No MemPalace adapter definition is available: ${error instanceof Error ? error.message : String(error)}`, toolCount: "runtime-detected" }
    };
  }
  if (typeof raw !== "object" || raw === null) throw new Error(`Invalid MemPalace adapter definition: ${definitionPath}`);
  const definition = raw as Partial<MemPalaceAdapterDefinition>;
  const validCommon = definition.schemaVersion === 1 && definition.adapter === adapter && definition.provider === "mempalace" && definition.mcp?.toolCount === "runtime-detected";
  const validSupported = definition.mcp?.supported === true && typeof definition.mcp.serverName === "string" && Array.isArray(definition.mcp.command) && definition.mcp.command.every((entry) => typeof entry === "string");
  const validUnsupported = definition.mcp?.supported === false && typeof definition.mcp.reason === "string";
  if (!validCommon || (!validSupported && !validUnsupported)) throw new Error(`Invalid MemPalace adapter definition: ${definitionPath}`);
  return definition as MemPalaceAdapterDefinition;
}

function isMemPalaceManifest(raw: unknown): raw is MemPalaceManifest {
  if (typeof raw !== "object" || raw === null) return false;
  const manifest = raw as Partial<MemPalaceManifest>;
  const detection = manifest.capabilityDetection;
  return manifest.schemaVersion === 1
    && manifest.name === MEM_PALACE_PACKAGE
    && manifest.package === MEM_PALACE_PACKAGE
    && manifest.version === MEM_PALACE_VERSION
    && manifest.packageSpec === MEM_PALACE_PACKAGE_SPEC
    && manifest.python === ">=3.9"
    && manifest.install?.command === "uv"
    && equalStrings(manifest.install.args, ["tool", "install", MEM_PALACE_PACKAGE_SPEC])
    && Array.isArray(manifest.install.effects)
    && manifest.compatibility?.policy === "exact-version"
    && manifest.compatibility.mismatch === "report-only-no-silent-replacement"
    && manifest.compatibility.upgrade === "requires-manifest-change-refreshed-official-evidence-and-compatibility-tests"
    && equalStrings(detection?.version, ["--version"])
    && equalStrings(detection?.mcp, ["mcp", "--help"])
    && detection?.toolCount === "runtime-detected"
    && manifest.canonicalPalace?.defaultRelativePath === ".mempalace/aili-palace"
    && manifest.canonicalPalace.overrideEnvironment === "AILI_MEMPALACE_PALACE_PATH"
    && equalStrings(manifest.operations, [...MEM_PALACE_OPERATIONS]);
}

function unavailableReadiness(manifest: MemPalaceManifest, status: Exclude<MemPalaceReadinessStatus, "compatible">, python: MemPalaceReadiness["python"], reason: string, observedVersion?: string): MemPalaceReadiness {
  return {
    status,
    expectedVersion: manifest.version,
    ...(observedVersion ? { observedVersion } : {}),
    python,
    capabilities: { mcpConfiguration: "unavailable", toolCount: "runtime-detected" },
    concurrentWriteSafety: "Unverified",
    reason
  };
}

function inspectPython(output: string, code: number | null): MemPalaceReadiness["python"] {
  const observedVersion = parseVersion(output);
  if (code !== 0) return { required: ">=3.9", status: "missing" };
  if (!observedVersion) return { required: ">=3.9", status: "invalid" };
  const [major, minor] = observedVersion.split(".").map((entry) => Number.parseInt(entry, 10));
  return {
    required: ">=3.9",
    observedVersion,
    status: major > MINIMUM_PYTHON[0] || (major === MINIMUM_PYTHON[0] && minor >= MINIMUM_PYTHON[1]) ? "compatible" : "incompatible"
  };
}

function parseVersion(output: string): string | undefined {
  const matches = [...output.matchAll(/(?:^|[^0-9])([0-9]+\.[0-9]+\.[0-9]+)(?=$|[^0-9])/gu)].map((match) => match[1]);
  const unique = [...new Set(matches)];
  return unique.length === 1 ? unique[0] : undefined;
}

function normalizeAgentName(agent: string): string {
  if (!/^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$/u.test(agent)) throw new Error(`Invalid stable Agent name for MemPalace diary: ${agent}`);
  return agent;
}

function equalStrings(value: unknown, expected: string[]): boolean {
  return Array.isArray(value) && value.length === expected.length && value.every((entry, index) => entry === expected[index]);
}

function runMemPalaceCommand(command: string, args: string[]): Promise<MemPalaceCommandResult> {
  return new Promise((resolve) => {
    let stdout = "";
    let stderr = "";
    const child = spawn(command, args, {
      stdio: ["ignore", "pipe", "pipe"],
      env: {
        HOME: process.env.HOME || os.homedir(),
        PATH: sanitizedPath(process.env.PATH ?? "/usr/bin:/bin:/usr/sbin:/sbin")
      }
    });
    child.stdout?.setEncoding("utf8");
    child.stdout?.on("data", (chunk: string) => { stdout += chunk; });
    child.stderr?.setEncoding("utf8");
    child.stderr?.on("data", (chunk: string) => { stderr += chunk; });
    child.on("error", (error: NodeJS.ErrnoException) => resolve({ code: null, stdout: stdout.trim(), detail: error.code === "ENOENT" ? `${command} command not found` : error.message }));
    child.on("close", (code) => resolve({ code, stdout: stdout.trim(), detail: stderr.trim() }));
  });
}

function sanitizedPath(rawPath: string): string {
  const cwd = path.resolve(process.cwd());
  const tempDir = path.resolve(os.tmpdir());
  return rawPath.split(path.delimiter).filter((entry) => {
    if (!entry || !path.isAbsolute(entry)) return false;
    const resolved = path.resolve(entry);
    return !isPathOrDescendant(resolved, cwd) && !isPathOrDescendant(resolved, tempDir);
  }).join(path.delimiter);
}

function isPathOrDescendant(candidate: string, parent: string): boolean {
  const relative = path.relative(parent, candidate);
  return relative === "" || (relative !== "" && !relative.startsWith("..") && !path.isAbsolute(relative));
}
