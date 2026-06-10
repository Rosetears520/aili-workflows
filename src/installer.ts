import { spawn } from "node:child_process";
import { constants } from "node:fs";
import { access, readdir, stat } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { mergeOpenCodeConfig } from "./config.js";
import { ComponentManifest, findMcp, findPlugin, loadManifest } from "./manifest.js";

export interface InstallOptions {
  dryRun: boolean;
  opencodeHome: string;
  ailiHome: string;
  yes?: boolean;
  setDefaultRose?: boolean;
  model?: string;
  forceDefaultAgent?: boolean;
  forceModel?: boolean;
  enablePlaywright?: boolean;
  skipPlaywright?: boolean;
  enableDcp?: boolean;
  skipDcp?: boolean;
  enableOpenspec?: boolean;
  skipOpenspec?: boolean;
  plugins: string[];
  json?: boolean;
}

type OptionalStatus = "configured" | "planned" | "skipped" | "failed" | "unverified";

interface OptionalSummary {
  status: OptionalStatus;
  command?: string;
  reason?: string;
  recovery?: string;
}

export interface InstallSummary {
  command: "install" | "update";
  dryRun: boolean;
  ailiHome: string;
  opencodeHome: string;
  componentInstall: { status: "planned" | "completed"; code: number | null };
  config: Awaited<ReturnType<typeof mergeOpenCodeConfig>>;
  mcp: { playwright: "configured" | "planned" | "skipped" };
  optionalDecisions: Array<{ name: string; status: "configured" | "planned" | "skipped"; nextStep?: string; reason?: string }>;
  dcp: OptionalSummary;
  openspec: OptionalSummary;
  plugins: Array<{ name: string; status: "skipped" | "unverified"; reason: string; source?: string }>;
}

const DCP_COMMAND = ["opencode", "plugin", "@tarquinen/opencode-dcp@latest", "--global"];
const OPENSPEC_INSTALL_COMMAND = ["npm", "install", "-g", "@fission-ai/openspec@latest"];
const MIN_OPENSPEC_NODE = [20, 19, 0] as const;

export function defaultAiliHome(): string {
  const here = path.dirname(fileURLToPath(import.meta.url));
  return path.resolve(here, "..");
}

export async function runInstall(command: "install" | "update", options: InstallOptions): Promise<InstallSummary> {
  validateOpenCodeHome(options.opencodeHome);
  const manifest = await loadManifest(options.ailiHome);
  await validateManifestAllowlist(options.ailiHome, manifest);
  const playwright = findMcp(manifest, "playwright");
  const shouldConfigurePlaywright = Boolean(options.enablePlaywright && !options.skipPlaywright);
  const pluginStatuses = validatePlugins(manifest, options.plugins);
  const unknown = pluginStatuses.find((plugin) => plugin.status === "unverified" && !plugin.source);
  if (unknown) {
    throw new Error(`Unknown plugin is not manifest-defined and will not be installed: ${unknown.name}`);
  }

  const setDefault = Boolean(options.setDefaultRose || options.yes);
  const configRequest = {
    opencodeHome: options.opencodeHome,
    dryRun: options.dryRun,
    setDefaultRose: setDefault,
    forceDefaultAgent: options.forceDefaultAgent,
    model: options.model,
    forceModel: options.forceModel,
    playwrightConfig: shouldConfigurePlaywright ? playwright?.config : undefined
  };
  const shouldMergeConfig = Boolean(setDefault || options.model || shouldConfigurePlaywright);
  const preflightConfig = shouldMergeConfig
    ? await mergeOpenCodeConfig({ ...configRequest, dryRun: true })
    : await mergeOpenCodeConfig(configRequest);

  const componentInstall = await runCompatibilityInstaller(options);
  const config = shouldMergeConfig && !options.dryRun ? await mergeOpenCodeConfig(configRequest) : preflightConfig;
  const dcp = await runDcpInstall(options);
  const openspec = await runOpenSpecInstall(options);

  return {
    command,
    dryRun: options.dryRun,
    ailiHome: options.ailiHome,
    opencodeHome: options.opencodeHome,
    componentInstall,
    config,
    mcp: { playwright: shouldConfigurePlaywright ? (options.dryRun ? "planned" : "configured") : "skipped" },
    optionalDecisions: buildOptionalDecisions(options, shouldConfigurePlaywright),
    dcp,
    openspec,
    plugins: pluginStatuses
  };
}

function buildOptionalDecisions(options: InstallOptions, shouldConfigurePlaywright: boolean): InstallSummary["optionalDecisions"] {
  const decisions: InstallSummary["optionalDecisions"] = [];
  if (!options.setDefaultRose && !options.yes) {
    decisions.push({
      name: "default rose",
      status: "skipped",
      reason: "not configured in this install",
      nextStep: "rose-aili install --set-default-rose"
    });
  }
  if (!options.model) {
    decisions.push({
      name: "rose model override",
      status: "skipped",
      reason: "not configured in this install; omit this to use OpenCode's default model behavior",
      nextStep: "rose-aili install --model <provider/model>"
    });
  }
  if (!shouldConfigurePlaywright) {
    decisions.push({
      name: "Playwright MCP",
      status: "skipped",
      reason: options.skipPlaywright ? "explicitly skipped" : "not configured in this install",
      nextStep: "rose-aili install --enable-playwright"
    });
  }
  if (!options.enableDcp) {
    decisions.push({
      name: "DCP plugin",
      status: "skipped",
      reason: options.skipDcp ? "explicitly skipped" : "not configured in this install",
      nextStep: "rose-aili install --enable-dcp"
    });
  }
  if (!options.enableOpenspec) {
    decisions.push({
      name: "OpenSpec",
      status: "skipped",
      reason: options.skipOpenspec ? "explicitly skipped" : "not configured in this install",
      nextStep: "rose-aili install --enable-openspec"
    });
  }
  return decisions;
}

async function runDcpInstall(options: InstallOptions): Promise<OptionalSummary> {
  const command = DCP_COMMAND.join(" ");
  if (!options.enableDcp || options.skipDcp) {
    return { status: "skipped", command, reason: "DCP is explicit opt-in only; run rose-aili install --enable-dcp." };
  }
  if (options.dryRun) return { status: "planned", command };
  const result = await spawnOptional(DCP_COMMAND[0], DCP_COMMAND.slice(1), options);
  if (result.code === 0) return { status: "configured", command, reason: "Duplicate detection is delegated to OpenCode plugin command; Unverified." };
  return {
    status: "failed",
    command,
    reason: result.detail || `command exited with ${result.code ?? "unknown status"}`,
    recovery: "Install DCP manually with: opencode plugin @tarquinen/opencode-dcp@latest --global"
  };
}

async function runOpenSpecInstall(options: InstallOptions): Promise<OptionalSummary> {
  if (!options.enableOpenspec || options.skipOpenspec) {
    return { status: "skipped", command: "rose-aili install --enable-openspec", reason: "OpenSpec is explicit opt-in only." };
  }
  if (!supportsOpenSpecNode(process.versions.node)) {
    return {
      status: "failed",
      command: OPENSPEC_INSTALL_COMMAND.join(" "),
      reason: `OpenSpec requires Node.js 20.19.0 or higher; current Node.js is ${process.versions.node}.`,
      recovery: "Upgrade Node.js to 20.19.0+ and rerun: rose-aili install --enable-openspec"
    };
  }
  const projectCommand = await hasOpenSpecProject(process.cwd()) ? "update" : "init";
  const command = `${OPENSPEC_INSTALL_COMMAND.join(" ")} && openspec ${projectCommand}`;
  if (options.dryRun) return { status: "planned", command };
  const installResult = await spawnOptional(OPENSPEC_INSTALL_COMMAND[0], OPENSPEC_INSTALL_COMMAND.slice(1), options);
  if (installResult.code !== 0) {
    return {
      status: "failed",
      command: OPENSPEC_INSTALL_COMMAND.join(" "),
      reason: installResult.detail || `command exited with ${installResult.code ?? "unknown status"}`,
      recovery: "Install OpenSpec manually with: npm install -g @fission-ai/openspec@latest"
    };
  }
  const projectResult = await spawnOptional("openspec", [projectCommand], options, process.cwd());
  if (projectResult.code !== 0) {
    return {
      status: "failed",
      command: `openspec ${projectCommand}`,
      reason: projectResult.detail || `command exited with ${projectResult.code ?? "unknown status"}`,
      recovery: `Run manually inside the target project: openspec ${projectCommand}`
    };
  }
  return { status: "configured", command };
}

function supportsOpenSpecNode(version: string): boolean {
  const parts = version.split(".").map((part) => Number.parseInt(part, 10));
  return parts[0] > MIN_OPENSPEC_NODE[0]
    || (parts[0] === MIN_OPENSPEC_NODE[0] && parts[1] > MIN_OPENSPEC_NODE[1])
    || (parts[0] === MIN_OPENSPEC_NODE[0] && parts[1] === MIN_OPENSPEC_NODE[1] && parts[2] >= MIN_OPENSPEC_NODE[2]);
}

async function hasOpenSpecProject(cwd: string): Promise<boolean> {
  for (const name of ["openspec", "openspec.json", "openspec.yaml", "openspec.yml"] as const) {
    try {
      const marker = await stat(path.join(cwd, name));
      if (name === "openspec" ? marker.isDirectory() : marker.isFile()) return true;
    } catch {
      // keep checking known OpenSpec markers
    }
  }
  return false;
}

function spawnOptional(command: string, args: string[], options: InstallOptions, cwd?: string): Promise<{ code: number | null; detail: string }> {
  return new Promise((resolve) => {
    let stderr = "";
    const env = sanitizedOptionalEnv(options);
    if (!env.PATH) {
      resolve({ code: null, detail: `${command} command not found in sanitized PATH` });
      return;
    }
    const child = spawn(command, args, {
      cwd,
      stdio: ["ignore", "ignore", "pipe"],
      env
    });
    child.stderr?.setEncoding("utf8");
    child.stderr?.on("data", (chunk: string) => {
      stderr += chunk;
    });
    child.on("error", (error: NodeJS.ErrnoException) => {
      resolve({ code: null, detail: error.code === "ENOENT" ? `${command} command not found` : error.message });
    });
    child.on("close", (code) => {
      resolve({ code, detail: stderr.trim() });
    });
  });
}

function sanitizedOptionalEnv(options: InstallOptions): NodeJS.ProcessEnv {
  return {
    HOME: os.homedir(),
    PATH: sanitizedOptionalPath(process.env.PATH ?? "/usr/bin:/bin:/usr/sbin:/sbin"),
    OPENCODE_HOME: options.opencodeHome,
    OPENCODE_ALLOW_CUSTOM_HOME: "yes",
    AILI_ALLOW_PACKAGE_HOME: "yes"
  };
}

function sanitizedOptionalPath(rawPath: string): string {
  const cwd = path.resolve(process.cwd());
  const entries = rawPath.split(path.delimiter).filter((entry) => {
    if (!entry || !path.isAbsolute(entry)) return false;
    return path.resolve(entry) !== cwd;
  });
  return entries.join(path.delimiter);
}

async function runCompatibilityInstaller(options: InstallOptions): Promise<{ status: "planned" | "completed"; code: number | null }> {
  const script = path.join(options.ailiHome, "scripts", "install_opencode.sh");
  await access(script, constants.F_OK);
  const mode = await isGitRepository(options.ailiHome) ? "selective" : "copy";
  const args = [script, "--mode", mode, "--aili-home", options.ailiHome, "--opencode-home", options.opencodeHome];
  if (options.dryRun) args.push("--dry-run");
  const code = await spawnInstaller(args, options);
  return { status: options.dryRun ? "planned" : "completed", code };
}

function spawnInstaller(args: string[], options: InstallOptions): Promise<number> {
  return new Promise((resolve, reject) => {
    let stderr = "";
    const child = spawn("/bin/bash", args, {
      stdio: options.json ? ["ignore", "ignore", "pipe"] : "inherit",
      env: {
        HOME: os.homedir(),
        PATH: "/usr/bin:/bin:/usr/sbin:/sbin",
        OPENCODE_HOME: options.opencodeHome,
        OPENCODE_ALLOW_CUSTOM_HOME: "yes",
        AILI_ALLOW_PACKAGE_HOME: "yes",
        AILI_INSTALLER_DRY_RUN: options.dryRun ? "1" : "0"
      }
    });
    if (options.json && child.stderr) {
      child.stderr.setEncoding("utf8");
      child.stderr.on("data", (chunk: string) => {
        stderr += chunk;
      });
    }
    child.on("error", reject);
    child.on("close", (code) => {
      if (code === 0) resolve(code);
      else {
        const detail = stderr.trim();
        reject(new Error(`Compatibility installer failed with exit code ${code ?? "unknown"}${detail ? `: ${detail}` : ""}`));
      }
    });
  });
}

async function isGitRepository(ailiHome: string): Promise<boolean> {
  try {
    await access(path.join(ailiHome, ".git"), constants.F_OK);
    return true;
  } catch {
    return false;
  }
}

export function validateOpenCodeHome(opencodeHome: string): void {
  if (!opencodeHome) throw new Error("Refusing empty OPENCODE_HOME.");
  if (!path.isAbsolute(opencodeHome)) throw new Error(`Refusing relative OPENCODE_HOME: ${opencodeHome}`);
  const resolved = path.resolve(opencodeHome);
  if (resolved === path.parse(resolved).root) throw new Error(`Refusing unsafe OPENCODE_HOME: ${opencodeHome}`);
  if (resolved === path.resolve(os.homedir())) throw new Error(`Refusing unsafe OPENCODE_HOME: ${opencodeHome}`);
}

async function validateManifestAllowlist(ailiHome: string, manifest: ComponentManifest): Promise<void> {
  const agents = manifest.components.agents.map((entry) => validateRepoEntry("agents", entry.name, entry.path, `agents/${entry.name}.md`));
  const commands = manifest.components.commands.map((entry) => validateRepoEntry("commands", entry.name, entry.path, `commands/${entry.name}.md`));
  const skills = manifest.components.skills.map((entry) => validateRepoEntry("skills", entry.name, entry.path, `skills/${entry.name}`));
  await assertCompleteAllowlist("agents", agents, await listAgentNames(ailiHome));
  await assertCompleteAllowlist("commands", commands, await listCommandNames(ailiHome));
  await assertCompleteAllowlist("skills", skills, await listSkillNames(ailiHome));
}

function validateRepoEntry(type: string, name: string, entryPath: string, expectedPath: string): string {
  if (!name) throw new Error(`Invalid manifest ${type} entry without name.`);
  if (path.isAbsolute(entryPath) || entryPath.split(/[\\/]/).includes("..")) {
    throw new Error(`Invalid manifest ${type} path for ${name}: ${entryPath}`);
  }
  if (entryPath !== expectedPath) {
    throw new Error(`Invalid manifest ${type} path for ${name}: expected ${expectedPath}, got ${entryPath}`);
  }
  return name;
}

async function assertCompleteAllowlist(type: string, manifestNames: string[], diskNames: string[]): Promise<void> {
  const manifestSet = new Set(manifestNames);
  if (manifestSet.size !== manifestNames.length) throw new Error(`Duplicate manifest ${type} entry.`);
  const extra = diskNames.filter((name) => !manifestSet.has(name));
  const missing = manifestNames.filter((name) => !diskNames.includes(name));
  if (extra.length > 0) throw new Error(`Unmanifested ${type} component(s): ${extra.join(", ")}`);
  if (missing.length > 0) throw new Error(`Manifest ${type} component(s) missing from AILI_HOME: ${missing.join(", ")}`);
}

async function listAgentNames(ailiHome: string): Promise<string[]> {
  return (await readdir(path.join(ailiHome, "agents"), { withFileTypes: true }))
    .filter((entry) => entry.isFile() && entry.name.endsWith(".md"))
    .map((entry) => path.basename(entry.name, ".md"))
    .sort();
}

async function listCommandNames(ailiHome: string): Promise<string[]> {
  return (await readdir(path.join(ailiHome, "commands"), { withFileTypes: true }))
    .filter((entry) => entry.isFile() && entry.name.endsWith(".md"))
    .map((entry) => path.basename(entry.name, ".md"))
    .sort();
}

async function listSkillNames(ailiHome: string): Promise<string[]> {
  const entries = await readdir(path.join(ailiHome, "skills"), { withFileTypes: true });
  const names: string[] = [];
  for (const entry of entries) {
    if (!entry.isDirectory()) continue;
    try {
      await access(path.join(ailiHome, "skills", entry.name, "SKILL.md"), constants.F_OK);
      names.push(entry.name);
    } catch {
      // Non-skill directories match the Bash installer skip behavior.
    }
  }
  return names.sort();
}

function validatePlugins(manifest: ComponentManifest, plugins: string[]): InstallSummary["plugins"] {
  return plugins.map((name) => {
    const plugin = findPlugin(manifest, name);
    if (!plugin) {
      return { name, status: "unverified", reason: "No manifest entry; not installed." };
    }
    return {
      name,
      status: "unverified",
      reason: plugin.install?.reason ?? "Plugin installation is not automated by this release.",
      source: plugin.source
    };
  });
}
