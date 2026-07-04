import { constants } from "node:fs";
import { access, readFile, stat } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { readOpenCodeConfig } from "./config.js";
import { RepoComponent, checkRepoManifestDrift, loadManifest, repoInstallTargets } from "./manifest.js";

export interface DoctorOptions {
  opencodeHome: string;
  ailiHome: string;
}

export interface DoctorSummary {
  ok: boolean;
  install: {
    ok: boolean;
    required: Array<{ type: string; name: string; installed: boolean }>;
  };
  required: Array<{ type: string; name: string; installed: boolean }>;
  source: {
    ok: boolean;
    sharedSkills: { status: "ready" | "missing"; path: string };
    manifestDrift: {
      ok: boolean;
      agents: { missing: string[]; unmanifested: string[] };
      commands: { missing: string[]; unmanifested: string[] };
      skills: { missing: string[]; unmanifested: string[] };
      issues: string[];
    };
    agentsMd: { status: "fresh" | "stale" | "missing"; path: string; templatePath: string; issues: string[] };
  };
  defaultAgent: string | null;
  roseModel: string | null;
  playwright: "configured" | "missing-optional";
  codegraph: {
    opencodeMcp: "configured" | "missing-optional";
    projectIndex: {
      status: "initialized" | "not-initialized-optional";
      root: string;
      marker: string;
      nextStep?: string;
    };
  };
  plugins: Array<{ name: string; status: "missing-optional" | "unverified" }>;
}

export async function runDoctor(options: DoctorOptions): Promise<DoctorSummary> {
  const manifest = await loadManifest(options.ailiHome);
  const installRoots = { opencode: options.opencodeHome, shared: sharedInstallHome() };
  const required = [
    { type: "global", name: "AGENTS.md", installed: await exists(path.join(options.opencodeHome, "AGENTS.md")) },
    ...(await Promise.all(manifest.components.agents.filter((entry) => entry.required).map((entry) => requiredInstallTarget(installRoots, "agent", entry, `agents/${entry.name}.md`)))),
    ...(await Promise.all(manifest.components.commands.filter((entry) => entry.required).map((entry) => requiredInstallTarget(installRoots, "command", entry, `commands/${entry.name}.md`)))),
    ...(await Promise.all(manifest.components.skills.filter((entry) => entry.required).map((entry) => requiredInstallTarget(installRoots, "skill", entry, `.agents/skills/${entry.name}`, "SKILL.md"))))
  ];
  const config = await readOpenCodeConfig(options.opencodeHome);
  const defaultAgent = typeof config.value?.default_agent === "string" ? config.value.default_agent : null;
  const roseModel = typeof config.value?.agent?.rose?.model === "string" ? config.value.agent.rose.model : null;
  const playwright = config.value?.mcp?.playwright ? "configured" : "missing-optional";
  const codegraph = await codegraphStatus(config.value?.mcp?.codegraph);
  const installOk = required.every((entry) => entry.installed);
  const source = await sourceReadiness(options.ailiHome, manifest);
  return {
    ok: installOk,
    install: { ok: installOk, required },
    required,
    source,
    defaultAgent,
    roseModel,
    playwright,
    codegraph,
    plugins: manifest.components.plugins.map((entry) => ({ name: entry.name, status: "missing-optional" }))
  };
}

async function sourceReadiness(ailiHome: string, manifest: Awaited<ReturnType<typeof loadManifest>>): Promise<DoctorSummary["source"]> {
  const sharedSkillsPath = path.join(ailiHome, ".agents", "skills");
  const sharedSkills = { status: (await isDirectory(sharedSkillsPath)) ? "ready" as const : "missing" as const, path: sharedSkillsPath };
  const manifestDrift = await manifestDriftStatus(ailiHome, manifest);
  const agentsMd = await agentsMdFreshness(ailiHome);
  return {
    ok: sharedSkills.status === "ready" && manifestDrift.ok && agentsMd.status === "fresh",
    sharedSkills,
    manifestDrift,
    agentsMd
  };
}

async function manifestDriftStatus(ailiHome: string, manifest: Awaited<ReturnType<typeof loadManifest>>): Promise<DoctorSummary["source"]["manifestDrift"]> {
  try {
    const drift = await checkRepoManifestDrift(ailiHome, manifest);
    const ok = (["agents", "commands", "skills"] as const).every((type) => drift[type].missing.length === 0 && drift[type].unmanifested.length === 0);
    return { ok, ...drift, issues: [] };
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : String(error);
    return {
      ok: false,
      agents: { missing: [], unmanifested: [] },
      commands: { missing: [], unmanifested: [] },
      skills: { missing: [], unmanifested: [] },
      issues: [message]
    };
  }
}

async function agentsMdFreshness(ailiHome: string): Promise<DoctorSummary["source"]["agentsMd"]> {
  const agentsPath = path.join(ailiHome, "AGENTS.md");
  const templatePath = path.join(ailiHome, "templates", "AGENTS.md");
  const issues: string[] = [];
  let text: string;
  let template: string;
  try {
    text = await readFile(agentsPath, "utf8");
  } catch {
    return { status: "missing", path: agentsPath, templatePath, issues: [`AGENTS.md does not exist: ${agentsPath}`] };
  }
  try {
    template = await readFile(templatePath, "utf8");
  } catch {
    return { status: "stale", path: agentsPath, templatePath, issues: [`AGENTS.md template does not exist: ${templatePath}`] };
  }

  const currentVersion = templateVersion(text);
  const expectedVersion = templateVersion(template);
  if (!currentVersion) issues.push("missing AILI_AGENTS_TEMPLATE_VERSION marker");
  else if (!expectedVersion) issues.push("template missing AILI_AGENTS_TEMPLATE_VERSION marker");
  else if (currentVersion !== expectedVersion) issues.push(`template version mismatch: AGENTS.md has ${currentVersion}, template has ${expectedVersion}`);
  if (!text.includes("<!-- AILI_AGENTS_TEMPLATE_SOURCE: templates/AGENTS.md -->")) issues.push("missing AILI_AGENTS_TEMPLATE_SOURCE marker");
  if (!text.includes("<!-- AILI_AGENTS_TEMPLATE_MODE: generated-project-local-file -->")) issues.push("missing AILI_AGENTS_TEMPLATE_MODE marker");

  const targetBlocks = managedBlocks(text);
  const templateBlocks = managedBlocks(template);
  for (const [name, block] of templateBlocks) {
    if (!targetBlocks.has(name)) issues.push(`missing managed block: ${name}`);
    else if (targetBlocks.get(name) !== block) issues.push(`managed block differs from template: ${name}`);
  }
  for (const name of [...targetBlocks.keys()].filter((name) => !templateBlocks.has(name)).sort()) {
    issues.push(`stale managed block not present in template: ${name}`);
  }

  return { status: issues.length > 0 ? "stale" : "fresh", path: agentsPath, templatePath, issues };
}

function templateVersion(text: string): string | null {
  return /<!--\s*AILI_AGENTS_TEMPLATE_VERSION:\s*(\d+)\s*-->/.exec(text)?.[1] ?? null;
}

function managedBlocks(text: string): Map<string, string> {
  const blocks = new Map<string, string>();
  const re = /<!-- AILI_MANAGED_BLOCK_BEGIN: (?<name>[a-z0-9-]+) -->[\s\S]*?<!-- AILI_MANAGED_BLOCK_END: \k<name> -->/g;
  for (const match of text.matchAll(re)) {
    const name = match.groups?.name;
    if (name) blocks.set(name, match[0]);
  }
  return blocks;
}

async function codegraphStatus(configuredMcp: unknown): Promise<DoctorSummary["codegraph"]> {
  const root = process.cwd();
  const marker = path.join(root, ".codegraph");
  const initialized = await isDirectory(marker);
  return {
    opencodeMcp: configuredMcp ? "configured" : "missing-optional",
    projectIndex: initialized
      ? { status: "initialized", root, marker }
      : {
          status: "not-initialized-optional",
          root,
          marker,
          nextStep: "From this project root, run: codegraph init -i && codegraph status"
        }
  };
}

function sharedInstallHome(): string {
  return process.env.HOME || os.homedir();
}

async function requiredInstallTarget(installRoots: { opencode: string; shared: string }, type: string, entry: RepoComponent, defaultTargetPath: string, requiredFile?: string): Promise<{ type: string; name: string; installed: boolean }> {
  const targets = repoInstallTargets(entry, defaultTargetPath);
  const checks = targets.map((target) => path.join(installRoots[target.kind], target.path, requiredFile ?? ""));
  const installed = checks.length > 0 && (await Promise.all(checks.map((targetPath) => exists(targetPath)))).every(Boolean);
  return { type, name: entry.name, installed };
}

async function exists(filePath: string): Promise<boolean> {
  try {
    await access(filePath, constants.F_OK);
    return true;
  } catch {
    return false;
  }
}

async function isDirectory(filePath: string): Promise<boolean> {
  try {
    const target = await stat(filePath);
    return target.isDirectory();
  } catch {
    return false;
  }
}
