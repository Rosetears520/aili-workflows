import { spawn } from "node:child_process";
import { createHash } from "node:crypto";
import { lstat, readFile, readdir, readlink } from "node:fs/promises";
import os from "node:os";
import path from "node:path";

const OFFICECLI_PACKAGE = "@officecli/officecli";
const OFFICECLI_VERSION = "1.0.143";
const OFFICECLI_PACKAGE_SPEC = `${OFFICECLI_PACKAGE}@${OFFICECLI_VERSION}`;
const OFFICECLI_TARGET = ".agents/tools/officecli";
const OFFICECLI_SHIM = "node_modules/.bin/officecli";
const OFFICECLI_INSTALL_ARGS = ["install", "--prefix", "{target}", "--no-save", "--no-package-lock", OFFICECLI_PACKAGE_SPEC];
const OFFICECLI_INSTALL_EFFECTS = ["network dependency resolution", "local-prefix package files under the managed target"];
const OFFICECLI_RECOVERY_PREFIX = "Rerun rose-aili install, or run the fixed local-prefix command: ";

export interface OfficeCliManifest {
  schemaVersion: 1;
  name: "officecli";
  package: string;
  version: string;
  packageSpec: string;
  registry: string;
  license: string;
  source: string;
  managedTarget: string;
  shimPath: string;
  install: {
    command: "npm";
    args: string[];
    effects: string[];
  };
  environment: { OFFICECLI_SKIP_UPDATE: "1" };
  upgradePolicy: "exact-pin-only";
}

export type OfficeCliReadinessStatus = "ready" | "missing" | "drift" | "invalid";

export interface OfficeCliReadiness {
  status: OfficeCliReadinessStatus;
  target: string;
  shim: string;
  expectedVersion: string;
  observedVersion?: string;
  reason?: string;
  recovery: string;
}

export interface OfficeCliInstallSummary {
  status: "planned" | "skipped" | "preserved" | "installed" | "failed";
  package: string;
  expectedVersion: string;
  observedVersion?: string;
  target: string;
  shim: string;
  command: string;
  argv: string[];
  effects: string[];
  reason?: string;
  recovery: string;
  exitCode?: number | null;
}

export interface OfficeCliInstallOptions {
  ailiHome: string;
  opencodeHome: string;
  dryRun: boolean;
  enabled?: boolean;
  skip?: boolean;
}

export async function loadOfficeCliManifest(ailiHome: string): Promise<OfficeCliManifest> {
  const manifestPath = path.join(ailiHome, "manifests", "officecli-tool.json");
  let raw: unknown;
  try {
    raw = JSON.parse(await readFile(manifestPath, "utf8"));
  } catch (error: unknown) {
    throw new Error(`Unable to load OfficeCLI tool manifest ${manifestPath}: ${error instanceof Error ? error.message : String(error)}`);
  }
  if (typeof raw !== "object" || raw === null) throw new Error(`Invalid OfficeCLI tool manifest: ${manifestPath}`);
  const manifest = raw as Partial<OfficeCliManifest>;
  const valid = manifest.schemaVersion === 1
    && manifest.name === "officecli"
    && manifest.package === OFFICECLI_PACKAGE
    && manifest.version === OFFICECLI_VERSION
    && manifest.packageSpec === OFFICECLI_PACKAGE_SPEC
    && manifest.registry === "https://registry.npmjs.org"
    && manifest.license === "Apache-2.0"
    && manifest.source === "https://github.com/iOfficeAI/OfficeCLI/tree/v1.0.143"
    && manifest.managedTarget === OFFICECLI_TARGET
    && manifest.shimPath === OFFICECLI_SHIM
    && manifest.install?.command === "npm"
    && Array.isArray(manifest.install.args)
    && manifest.install.args.length === OFFICECLI_INSTALL_ARGS.length
    && manifest.install.args.every((entry, index) => entry === OFFICECLI_INSTALL_ARGS[index])
    && Array.isArray(manifest.install.effects)
    && manifest.install.effects.length === OFFICECLI_INSTALL_EFFECTS.length
    && manifest.install.effects.every((entry, index) => entry === OFFICECLI_INSTALL_EFFECTS[index])
    && manifest.environment?.OFFICECLI_SKIP_UPDATE === "1"
    && manifest.upgradePolicy === "exact-pin-only";
  if (!valid) throw new Error(`OfficeCLI tool manifest differs from the fixed managed-install contract: ${manifestPath}`);
  return manifest as OfficeCliManifest;
}

export function managedOfficeCliTarget(home = process.env.HOME || os.homedir()): string {
  if (!home || !path.isAbsolute(home)) throw new Error(`Refusing unsafe HOME for OfficeCLI managed target: ${home || "<empty>"}`);
  const resolvedHome = path.resolve(home);
  if (resolvedHome === path.parse(resolvedHome).root || resolvedHome === path.resolve(os.tmpdir())) {
    throw new Error(`Refusing unsafe HOME for OfficeCLI managed target: ${resolvedHome}`);
  }
  return path.join(resolvedHome, OFFICECLI_TARGET);
}

export async function inspectOfficeCli(ailiHome: string): Promise<OfficeCliReadiness> {
  const manifest = await loadOfficeCliManifest(ailiHome);
  const target = managedOfficeCliTarget();
  return inspectManagedOfficeCli(manifest, target);
}

export async function runOfficeCliInstall(options: OfficeCliInstallOptions): Promise<OfficeCliInstallSummary> {
  let manifest: OfficeCliManifest;
  let target: string;
  try {
    manifest = await loadOfficeCliManifest(options.ailiHome);
    target = managedOfficeCliTarget();
  } catch (error: unknown) {
    const home = process.env.HOME || os.homedir();
    const fallbackTarget = path.isAbsolute(home) ? path.join(path.resolve(home), OFFICECLI_TARGET) : path.join("<invalid-home>", OFFICECLI_TARGET);
    const fallbackArgs = OFFICECLI_INSTALL_ARGS.map((entry) => entry === "{target}" ? fallbackTarget : entry);
    const fallbackArgv = ["npm", ...fallbackArgs];
    return {
      status: "failed",
      package: OFFICECLI_PACKAGE_SPEC,
      expectedVersion: OFFICECLI_VERSION,
      target: fallbackTarget,
      shim: path.join(fallbackTarget, OFFICECLI_SHIM),
      command: fallbackArgv.join(" "),
      argv: fallbackArgv,
      effects: OFFICECLI_INSTALL_EFFECTS,
      reason: error instanceof Error ? error.message : String(error),
      recovery: `${OFFICECLI_RECOVERY_PREFIX}${fallbackArgv.join(" ")}`
    };
  }
  const shim = path.join(target, manifest.shimPath);
  const args = manifest.install.args.map((entry) => entry === "{target}" ? target : entry);
  const argv = [manifest.install.command, ...args];
  const command = argv.join(" ");
  const recovery = `${OFFICECLI_RECOVERY_PREFIX}${command}`;
  const base = {
    package: manifest.packageSpec,
    expectedVersion: manifest.version,
    target,
    shim,
    command,
    argv,
    effects: manifest.install.effects,
    recovery
  };

  if (options.skip) return { status: "skipped", ...base, reason: "OfficeCLI explicitly skipped; no probe or install command ran." };
  if (!options.enabled) return { status: "planned", ...base, reason: "OfficeCLI is default-selected but requires a separate exact install approval; no probe or install command ran." };
  if (options.dryRun) return { status: "planned", ...base, reason: "Would detect the managed exact version and install only if missing or drifted; dry-run performed no probe, directory creation, or command execution." };

  const protectedPaths = officeCliProtectedPaths(options.opencodeHome);
  const beforeProtected = await fingerprintPaths(protectedPaths);
  const current = await inspectManagedOfficeCli(manifest, target);
  const afterProbeProtected = await fingerprintPaths(protectedPaths);
  const probeMutation = changedFingerprints(beforeProtected, afterProbeProtected);
  if (probeMutation.length > 0) {
    return { status: "failed", ...base, observedVersion: current.observedVersion, reason: `OfficeCLI version probe changed protected integration paths: ${probeMutation.join(", ")}` };
  }
  if (current.status === "ready") {
    return { status: "preserved", ...base, observedVersion: current.observedVersion, reason: "Existing exact managed OfficeCLI version preserved; npm did not run." };
  }

  const installed = await runCommand(manifest.install.command, args);
  if (installed.code !== 0) {
    const afterFailureProtected = await fingerprintPaths(protectedPaths);
    const changed = changedFingerprints(beforeProtected, afterFailureProtected);
    const detail = installed.detail || `command exited with ${installed.code ?? "unknown status"}`;
    const mutation = changed.length > 0 ? `; protected integration paths changed: ${changed.join(", ")}` : "";
    return { status: "failed", ...base, observedVersion: current.observedVersion, exitCode: installed.code, reason: `${detail}${mutation}` };
  }

  const verified = await inspectManagedOfficeCli(manifest, target);
  const afterProtected = await fingerprintPaths(protectedPaths);
  const changed = changedFingerprints(beforeProtected, afterProtected);
  if (changed.length > 0) {
    return { status: "failed", ...base, observedVersion: verified.observedVersion, exitCode: installed.code, reason: `OfficeCLI local-prefix install changed protected Skill/MCP/shell integration paths: ${changed.join(", ")}` };
  }
  if (verified.status !== "ready") {
    return {
      status: "failed",
      ...base,
      observedVersion: verified.observedVersion,
      exitCode: installed.code,
      reason: `npm exited successfully but managed postinstall verification was ${verified.status}: ${verified.reason ?? "exact version was not ready"}`
    };
  }
  return { status: "installed", ...base, observedVersion: verified.observedVersion, exitCode: installed.code, reason: "Fixed local-prefix install passed managed shim and exact-version verification." };
}

async function inspectManagedOfficeCli(manifest: OfficeCliManifest, target: string): Promise<OfficeCliReadiness> {
  const shim = path.join(target, manifest.shimPath);
  const command = [manifest.install.command, ...manifest.install.args.map((entry) => entry === "{target}" ? target : entry)].join(" ");
  const recovery = `${OFFICECLI_RECOVERY_PREFIX}${command}`;
  try {
    const shimStat = await lstat(shim);
    if (!shimStat.isFile() && !shimStat.isSymbolicLink()) {
      return { status: "invalid", target, shim, expectedVersion: manifest.version, reason: "Managed OfficeCLI shim is not a file or symlink.", recovery };
    }
  } catch (error: unknown) {
    const code = (error as NodeJS.ErrnoException).code;
    return code === "ENOENT"
      ? { status: "missing", target, shim, expectedVersion: manifest.version, reason: "Managed OfficeCLI shim is missing.", recovery }
      : { status: "invalid", target, shim, expectedVersion: manifest.version, reason: `Managed OfficeCLI shim could not be inspected: ${error instanceof Error ? error.message : String(error)}`, recovery };
  }

  const probe = await runCommand(shim, ["--version"]);
  if (probe.code !== 0) {
    return { status: "invalid", target, shim, expectedVersion: manifest.version, reason: probe.detail || `managed --version exited with ${probe.code ?? "unknown status"}`, recovery };
  }
  const observedVersion = parseOfficeCliVersion(probe.stdout);
  if (!observedVersion) {
    return { status: "invalid", target, shim, expectedVersion: manifest.version, reason: "Managed OfficeCLI --version output did not contain exactly one semantic version.", recovery };
  }
  if (observedVersion !== manifest.version) {
    return { status: "drift", target, shim, expectedVersion: manifest.version, observedVersion, reason: `Managed OfficeCLI version ${observedVersion} differs from ${manifest.version}.`, recovery };
  }
  return { status: "ready", target, shim, expectedVersion: manifest.version, observedVersion, recovery };
}

function parseOfficeCliVersion(output: string): string | undefined {
  const matches = [...output.matchAll(/(?:^|[^0-9])([0-9]+\.[0-9]+\.[0-9]+)(?=$|[^0-9])/gu)].map((match) => match[1]);
  const unique = [...new Set(matches)];
  return unique.length === 1 ? unique[0] : undefined;
}

function runCommand(command: string, args: string[]): Promise<{ code: number | null; stdout: string; detail: string }> {
  return new Promise((resolve) => {
    let stdout = "";
    let stderr = "";
    let settled = false;
    const finish = (result: { code: number | null; stdout: string; detail: string }) => {
      if (settled) return;
      settled = true;
      resolve(result);
    };
    const child = spawn(command, args, {
      stdio: ["ignore", "pipe", "pipe"],
      env: {
        HOME: process.env.HOME || os.homedir(),
        PATH: sanitizedOfficeCliPath(process.env.PATH ?? "/usr/bin:/bin:/usr/sbin:/sbin"),
        OFFICECLI_SKIP_UPDATE: "1"
      }
    });
    child.stdout?.setEncoding("utf8");
    child.stdout?.on("data", (chunk: string) => { stdout += chunk; });
    child.stderr?.setEncoding("utf8");
    child.stderr?.on("data", (chunk: string) => { stderr += chunk; });
    child.on("error", (error: NodeJS.ErrnoException) => finish({ code: null, stdout: stdout.trim(), detail: error.code === "ENOENT" ? `${command} command not found` : error.message }));
    child.on("close", (code) => finish({ code, stdout: stdout.trim(), detail: stderr.trim() }));
  });
}

function sanitizedOfficeCliPath(rawPath: string): string {
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

function officeCliProtectedPaths(opencodeHome: string): string[] {
  const home = path.resolve(process.env.HOME || os.homedir());
  const openCodeHomes = new Set([path.join(home, ".config", "opencode"), path.resolve(opencodeHome)]);
  const protectedPaths = [
    ...["officecli", "officecli-docx", "officecli-xlsx", "officecli-pptx"].map((name) => path.join(home, ".agents", "skills", name)),
    ...[".bashrc", ".bash_profile", ".profile", ".zshrc"].map((name) => path.join(home, name))
  ];
  for (const root of openCodeHomes) {
    protectedPaths.push(path.join(root, "opencode.json"), path.join(root, "opencode.jsonc"));
    for (const name of ["officecli", "officecli-docx", "officecli-xlsx", "officecli-pptx"]) protectedPaths.push(path.join(root, "skills", name));
  }
  return [...new Set(protectedPaths)];
}

async function fingerprintPaths(paths: string[]): Promise<Map<string, string>> {
  return new Map(await Promise.all(paths.map(async (entry) => [entry, await fingerprintPath(entry)] as const)));
}

function changedFingerprints(before: Map<string, string>, after: Map<string, string>): string[] {
  return [...before.keys()].filter((entry) => before.get(entry) !== after.get(entry));
}

async function fingerprintPath(filePath: string): Promise<string> {
  try {
    const target = await lstat(filePath);
    if (target.isSymbolicLink()) return `link:${await readlink(filePath)}`;
    if (target.isFile()) {
      const digest = createHash("sha256").update(await readFile(filePath)).digest("hex");
      return `file:${target.mode & 0o777}:${digest}`;
    }
    if (target.isDirectory()) {
      const entries = (await readdir(filePath)).sort();
      const children = await Promise.all(entries.map(async (entry) => `${entry}:${await fingerprintPath(path.join(filePath, entry))}`));
      return `directory:${target.mode & 0o777}:${children.join("|")}`;
    }
    return `other:${target.mode}`;
  } catch (error: unknown) {
    const code = (error as NodeJS.ErrnoException).code;
    return code === "ENOENT" ? "missing" : `error:${code ?? (error instanceof Error ? error.message : String(error))}`;
  }
}
