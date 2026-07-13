import { spawn } from "node:child_process";
import { constants, realpathSync, statSync } from "node:fs";
import { access, stat } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { configPathFor, mergeOpenCodeConfig } from "./config.js";
import { ComponentManifest, findMcp, findPlugin, loadManifest, validateManifestAllowlist } from "./manifest.js";

export interface InstallOptions {
  dryRun: boolean;
  opencodeHome: string;
  ailiHome: string;
  yes?: boolean;
  setDefaultRose?: boolean;
  model?: string;
  forceDefaultAgent?: boolean;
  forceModel?: boolean;
  skipOpenCodeConfig?: boolean;
  enablePlaywright?: boolean;
  skipPlaywright?: boolean;
  enableCodegraph?: boolean;
  skipCodegraph?: boolean;
  enableOpenspec?: boolean;
  skipOpenspec?: boolean;
  projectRoot?: string;
  plugins: string[];
  json?: boolean;
}

type OptionalStatus = "configured" | "planned" | "skipped" | "failed" | "unverified";

interface OptionalSummary {
  status: OptionalStatus;
  command?: string;
  reason?: string;
  recovery?: string;
  nextStep?: string;
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
  codegraph: OptionalSummary;
  openspec: OptionalSummary;
  plugins: Array<{ name: string; status: "skipped" | "unverified"; reason: string; source?: string }>;
}

const CODEGRAPH_INSTALL_COMMAND = ["npm", "install", "-g", "@colbymchenry/codegraph@latest"];
const CODEGRAPH_OPENCODE_COMMAND = ["codegraph", "install", "--target=opencode", "--yes"];
const CODEGRAPH_RESTART_STEP = "Restart OpenCode so it loads the CodeGraph OpenCode integration.";
const OPENSPEC_INSTALL_COMMAND = ["npm", "install", "-g", "@fission-ai/openspec@latest"];
const OPENSPEC_DETECT_COMMAND = ["openspec", "--version"];
const MIN_OPENSPEC_NODE = [20, 19, 0] as const;

export function defaultAiliHome(): string {
  const here = path.dirname(fileURLToPath(import.meta.url));
  return path.resolve(here, "..");
}

export async function runInstall(command: "install" | "update", rawOptions: InstallOptions): Promise<InstallSummary> {
  const options = { ...rawOptions, opencodeHome: validateOpenCodeHome(rawOptions.opencodeHome) };
  if (options.projectRoot) options.projectRoot = validateExactProjectRoot(options.projectRoot);
  if (options.enableOpenspec && !options.skipOpenspec && !options.projectRoot) {
    throw new Error("--enable-openspec requires --project-root <path>.");
  }
  const manifest = await loadManifest(options.ailiHome);
  await validateManifestAllowlist(options.ailiHome, manifest);
  await validateInstallerSources(options.ailiHome);
  const playwright = findMcp(manifest, "playwright");
  const shouldSyncOpenCodeConfig = !options.skipOpenCodeConfig;
  const shouldConfigurePlaywright = Boolean(shouldSyncOpenCodeConfig && options.enablePlaywright && !options.skipPlaywright);
  const pluginStatuses = validatePlugins(manifest, options.plugins);
  const unknown = pluginStatuses.find((plugin) => plugin.status === "unverified" && !plugin.source);
  if (unknown) {
    throw new Error(`Unknown plugin is not manifest-defined and will not be installed: ${unknown.name}`);
  }

  const configRequest = {
    opencodeHome: options.opencodeHome,
    dryRun: options.dryRun,
    setDefaultRose: shouldSyncOpenCodeConfig && options.setDefaultRose !== false,
    forceDefaultAgent: options.forceDefaultAgent,
    model: options.model,
    forceModel: options.forceModel,
    playwrightConfig: shouldConfigurePlaywright ? playwright?.config : undefined
  };
  const shouldMergeConfig = shouldSyncOpenCodeConfig && Boolean(configRequest.setDefaultRose || options.model || shouldConfigurePlaywright);
  const preflightConfig = options.skipOpenCodeConfig
    ? await skippedOpenCodeConfig(options)
    : shouldMergeConfig
    ? await mergeOpenCodeConfig({ ...configRequest, dryRun: true })
    : await mergeOpenCodeConfig(configRequest);

  const componentInstall = await runCompatibilityInstaller(options);
  const config = shouldMergeConfig && !options.dryRun ? await mergeOpenCodeConfig(configRequest) : preflightConfig;
  const codegraph = await runCodeGraphInstall(options);
  const openspec = await runOpenSpecInstall(options);

  return {
    command,
    dryRun: options.dryRun,
    ailiHome: options.ailiHome,
    opencodeHome: options.opencodeHome,
    componentInstall,
    config,
    mcp: { playwright: shouldConfigurePlaywright ? (options.dryRun ? "planned" : "configured") : "skipped" },
    optionalDecisions: buildOptionalDecisions(command, options, shouldConfigurePlaywright, shouldSyncOpenCodeConfig),
    codegraph,
    openspec,
    plugins: pluginStatuses
  };
}

async function skippedOpenCodeConfig(options: InstallOptions): Promise<InstallSummary["config"]> {
  return {
    configPath: await configPathFor(options.opencodeHome),
    changed: false,
    actions: [],
    skipped: ["OpenCode config sync explicitly skipped"]
  };
}

function buildOptionalDecisions(command: "install" | "update", options: InstallOptions, shouldConfigurePlaywright: boolean, shouldSyncOpenCodeConfig: boolean): InstallSummary["optionalDecisions"] {
  const decisions: InstallSummary["optionalDecisions"] = [];
  if (!shouldSyncOpenCodeConfig) {
    decisions.push({
      name: "OpenCode config",
      status: "skipped",
      reason: "explicitly skipped",
      nextStep: `rose-aili ${command}`
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
      reason: options.skipPlaywright ? "explicitly skipped" : options.skipOpenCodeConfig ? "OpenCode config sync explicitly skipped" : "not configured in this install",
      nextStep: "rose-aili install --enable-playwright"
    });
  }
  if (!options.enableCodegraph) {
    decisions.push({
      name: "CodeGraph",
      status: "skipped",
      reason: options.skipCodegraph ? "explicitly skipped" : "not configured in this install",
      nextStep: "rose-aili install --enable-codegraph"
    });
  }
  if (!options.enableOpenspec || options.skipOpenspec) {
    decisions.push({
      name: "OpenSpec",
      status: "skipped",
      reason: options.skipOpenspec ? "explicitly skipped" : "not configured in this install",
      nextStep: "rose-aili install --enable-openspec --project-root <absolute-canonical-path>"
    });
  }
  return decisions;
}

async function runCodeGraphInstall(options: InstallOptions): Promise<OptionalSummary> {
  const installCommand = CODEGRAPH_INSTALL_COMMAND.join(" ");
  const opencodeCommand = CODEGRAPH_OPENCODE_COMMAND.join(" ");
  const command = `${installCommand} && ${opencodeCommand}`;
  if (!options.enableCodegraph || options.skipCodegraph) {
    return { status: "skipped", command, reason: "CodeGraph is explicit opt-in only; run rose-aili install --enable-codegraph." };
  }
  if (options.dryRun) return { status: "planned", command, nextStep: CODEGRAPH_RESTART_STEP };
  const installResult = await spawnOptional(CODEGRAPH_INSTALL_COMMAND[0], CODEGRAPH_INSTALL_COMMAND.slice(1), options);
  if (installResult.code !== 0) {
    return {
      status: "failed",
      command: installCommand,
      reason: installResult.detail || `command exited with ${installResult.code ?? "unknown status"}`,
      recovery: "Install CodeGraph manually with: npm install -g @colbymchenry/codegraph@latest"
    };
  }
  const opencodeResult = await spawnOptional(CODEGRAPH_OPENCODE_COMMAND[0], CODEGRAPH_OPENCODE_COMMAND.slice(1), options);
  if (opencodeResult.code !== 0) {
    return {
      status: "failed",
      command: opencodeCommand,
      reason: opencodeResult.detail || `command exited with ${opencodeResult.code ?? "unknown status"}`,
      recovery: "Run CodeGraph OpenCode setup manually with: codegraph install --target=opencode --yes, then restart OpenCode."
    };
  }
  return { status: "configured", command, nextStep: CODEGRAPH_RESTART_STEP };
}

async function runOpenSpecInstall(options: InstallOptions): Promise<OptionalSummary> {
  if (!options.enableOpenspec || options.skipOpenspec) {
    return {
      status: "skipped",
      command: "rose-aili install --enable-openspec --project-root <absolute-canonical-path>",
      reason: options.skipOpenspec ? "OpenSpec explicitly skipped." : "OpenSpec is explicit opt-in only and requires an exact project root."
    };
  }
  if (!supportsOpenSpecNode(process.versions.node)) {
    return {
      status: "failed",
      command: OPENSPEC_INSTALL_COMMAND.join(" "),
      reason: `OpenSpec requires Node.js 20.19.0 or higher; current Node.js is ${process.versions.node}.`,
      recovery: "Upgrade Node.js to 20.19.0+ and rerun: rose-aili install --enable-openspec"
    };
  }
  if (!options.projectRoot) throw new Error("--enable-openspec requires --project-root <path>.");
  const projectCommand = await hasOpenSpecProject(options.projectRoot) ? "update" : "init";
  const command = `${OPENSPEC_INSTALL_COMMAND.join(" ")} && openspec ${projectCommand}`;
  if (options.dryRun) return { status: "planned", command };
  const installed = await isOpenSpecInstalled(options);
  const installResult = installed ? { code: 0, detail: "" } : await spawnOptional(OPENSPEC_INSTALL_COMMAND[0], OPENSPEC_INSTALL_COMMAND.slice(1), options);
  if (installResult.code !== 0) {
    return {
      status: "failed",
      command: OPENSPEC_INSTALL_COMMAND.join(" "),
      reason: installResult.detail || `command exited with ${installResult.code ?? "unknown status"}`,
      recovery: "Install OpenSpec manually with: npm install -g @fission-ai/openspec@latest"
    };
  }
  const projectResult = await spawnOptional("openspec", [projectCommand], options, options.projectRoot);
  if (projectResult.code !== 0) {
    return {
      status: "failed",
      command: `openspec ${projectCommand}`,
      reason: projectResult.detail || `command exited with ${projectResult.code ?? "unknown status"}`,
      recovery: `Run manually inside the target project: openspec ${projectCommand}`
    };
  }
  return { status: "configured", command: installed ? `openspec ${projectCommand}` : command };
}

async function isOpenSpecInstalled(options: InstallOptions): Promise<boolean> {
  const result = await spawnOptionalCapture(OPENSPEC_DETECT_COMMAND[0], OPENSPEC_DETECT_COMMAND.slice(1), options);
  return result.code === 0;
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
  return spawnOptionalCapture(command, args, options, cwd).then(({ code, detail }) => ({ code, detail }));
}

function spawnOptionalCapture(command: string, args: string[], options: InstallOptions, cwd?: string): Promise<{ code: number | null; detail: string; stdout: string }> {
  return new Promise((resolve) => {
    let stdout = "";
    let stderr = "";
    const env = sanitizedOptionalEnv(options);
    if (!env.PATH) {
      resolve({ code: null, detail: `${command} command not found in sanitized PATH`, stdout });
      return;
    }
    const child = spawn(command, args, {
      cwd,
      stdio: ["ignore", "pipe", "pipe"],
      env
    });
    child.stdout?.setEncoding("utf8");
    child.stdout?.on("data", (chunk: string) => {
      stdout += chunk;
    });
    child.stderr?.setEncoding("utf8");
    child.stderr?.on("data", (chunk: string) => {
      stderr += chunk;
    });
    child.on("error", (error: NodeJS.ErrnoException) => {
      resolve({ code: null, detail: error.code === "ENOENT" ? `${command} command not found` : error.message, stdout });
    });
    child.on("close", (code) => {
      resolve({ code, detail: stderr.trim(), stdout: stdout.trim() });
    });
  });
}

function sanitizedOptionalEnv(options: InstallOptions): NodeJS.ProcessEnv {
  return {
    HOME: process.env.HOME || os.homedir(),
    PATH: sanitizedOptionalPath(process.env.PATH ?? "/usr/bin:/bin:/usr/sbin:/sbin"),
    OPENCODE_HOME: options.opencodeHome,
    OPENCODE_ALLOW_CUSTOM_HOME: "yes",
    AILI_ALLOW_PACKAGE_HOME: "yes"
  };
}

function sanitizedOptionalPath(rawPath: string): string {
  const cwd = path.resolve(process.cwd());
  const tempDir = path.resolve(os.tmpdir());
  const entries = rawPath.split(path.delimiter).filter((entry) => {
    if (!entry || !path.isAbsolute(entry)) return false;
    const resolved = path.resolve(entry);
    return !isPathOrDescendant(resolved, cwd) && !isPathOrDescendant(resolved, tempDir);
  });
  return entries.join(path.delimiter);
}

function isPathOrDescendant(candidate: string, parent: string): boolean {
  const relative = path.relative(parent, candidate);
  return relative === "" || (relative !== "" && !relative.startsWith("..") && !path.isAbsolute(relative));
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
        HOME: process.env.HOME || os.homedir(),
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

async function validateInstallerSources(ailiHome: string): Promise<void> {
  await access(path.join(ailiHome, "templates", "opencode-global-AGENTS.md"), constants.F_OK);
}

export function validateOpenCodeHome(opencodeHome: string): string {
  if (!opencodeHome) throw new Error("Refusing empty OPENCODE_HOME.");
  if (!path.isAbsolute(opencodeHome)) throw new Error(`Refusing relative OPENCODE_HOME: ${opencodeHome}`);
  const resolved = path.resolve(opencodeHome);
  if (resolved === path.parse(resolved).root) throw new Error(`Refusing unsafe OPENCODE_HOME: ${opencodeHome}`);
  if (resolved === path.resolve(os.homedir())) throw new Error(`Refusing unsafe OPENCODE_HOME: ${opencodeHome}`);
  if (resolved === path.resolve(os.tmpdir())) throw new Error(`Refusing unsafe OPENCODE_HOME: ${opencodeHome}`);
  return resolved;
}

export function validateExactProjectRoot(projectRoot: string): string {
  if (!projectRoot || !path.isAbsolute(projectRoot)) {
    throw new Error(`OpenSpec --project-root requires an absolute canonical directory: ${projectRoot || "<empty>"}`);
  }
  const resolved = path.resolve(projectRoot);
  let canonical: string;
  try {
    canonical = realpathSync(resolved);
  } catch {
    throw new Error(`OpenSpec --project-root requires an existing directory: ${projectRoot}`);
  }
  if (resolved !== canonical || !statSync(canonical).isDirectory()) {
    throw new Error(`Refusing ambiguous or symlinked OpenSpec project root: ${projectRoot}`);
  }
  for (const unsafe of [path.parse(canonical).root, path.resolve(os.homedir()), path.resolve(os.userInfo().homedir), path.resolve(os.tmpdir())]) {
    if (canonical === unsafe) throw new Error(`Refusing unsafe OpenSpec project root: ${projectRoot}`);
  }
  return canonical;
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
