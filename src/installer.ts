import { spawn } from "node:child_process";
import { constants } from "node:fs";
import { access, readdir } from "node:fs/promises";
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
  plugins: string[];
  json?: boolean;
}

export interface InstallSummary {
  command: "install" | "update";
  dryRun: boolean;
  ailiHome: string;
  opencodeHome: string;
  componentInstall: { status: "planned" | "completed"; code: number | null };
  config: Awaited<ReturnType<typeof mergeOpenCodeConfig>>;
  mcp: { playwright: "configured" | "planned" | "skipped" };
  plugins: Array<{ name: string; status: "skipped" | "unverified"; reason: string; source?: string }>;
}

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

  return {
    command,
    dryRun: options.dryRun,
    ailiHome: options.ailiHome,
    opencodeHome: options.opencodeHome,
    componentInstall,
    config,
    mcp: { playwright: shouldConfigurePlaywright ? (options.dryRun ? "planned" : "configured") : "skipped" },
    plugins: pluginStatuses
  };
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
