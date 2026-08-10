import { spawn } from "node:child_process";
import { constants } from "node:fs";
import { createHash } from "node:crypto";
import { access, readFile, readdir, stat } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { readOpenCodeConfig } from "./config.js";
import { inspectGraphifySkillInventory, inspectGraphifyVersion } from "./graphify.js";
import type { InstallProfile } from "./installer.js";
import { RepoComponent, checkRepoManifestDrift, loadManifest, repoInstallTargets, resolveSkillSelection } from "./manifest.js";
import { MemPalaceCommandRunner, MemPalaceMcpPlan, MemPalaceReadiness, inspectMemPalace, planMemPalaceMcpConfiguration } from "./mempalace.js";
import { inspectOfficeCli, OfficeCliReadiness } from "./officecli.js";

export interface DoctorOptions {
  opencodeHome: string;
  ailiHome: string;
  profile?: InstallProfile;
  skills?: string[];
  skillGroups?: string[];
  mempalaceRunner?: MemPalaceCommandRunner;
}

export interface DoctorSummary {
  ok: boolean;
  profile: InstallProfile;
  selectedSkills: string[];
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
    generated: { status: "ready" | "missing" | "drift"; paths: string[]; issues: string[] };
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
  graphifyCli: {
    status: "installed" | "missing";
    observedVersion?: string;
    reason?: string;
    ownership: "upstream";
  };
  graphifyGlobalSkill: {
    status: "registered" | "missing" | "invalid";
    path: string;
    versionStampPath: string;
    referencesPath: string;
    version?: string;
    referencesPresent: boolean;
    issues: string[];
    ownership: "upstream";
  };
  officecli: OfficeCliReadiness;
  mempalace: MemPalaceReadiness;
  mempalaceMcp: MemPalaceMcpPlan;
  plugins: Array<{ name: string; status: "missing-optional" | "unverified" }>;
  unavailableCapabilities: Array<{ name: string; reason: string }>;
}

export async function runDoctor(options: DoctorOptions): Promise<DoctorSummary> {
  const manifest = await loadManifest(options.ailiHome);
  const profile = options.profile ?? "default";
  if (!["default", "pi", "opencode"].includes(profile)) throw new Error(`Unknown profile: ${profile}`);
  const selectedSkills = resolveSkillSelection(manifest, options.skills, options.skillGroups);
  const installRoots = { opencode: options.opencodeHome, shared: sharedInstallHome() };
  const officecli = await inspectOfficeCli(options.ailiHome);
  const mempalace = await inspectMemPalace(options.ailiHome, options.mempalaceRunner);
  const required = [
    ...(await Promise.all(selectedSkills.map((entry) => requiredInstallTarget(installRoots, "skill", entry, `.agents/skills/${entry.name}`, "SKILL.md")))),
    ...(profile === "opencode" ? [
      { type: "global", name: "AGENTS.md", installed: await exists(path.join(options.opencodeHome, "AGENTS.md")) },
      ...(await Promise.all(manifest.components.agents.filter((entry) => entry.required).map((entry) => requiredInstallTarget(installRoots, "agent", entry, `agents/${entry.name}.md`)))),
      ...(await Promise.all(manifest.components.commands.filter((entry) => entry.required).map((entry) => requiredInstallTarget(installRoots, "command", entry, `commands/${entry.name}.md`))))
    ] : []),
    ...(profile === "pi" ? await piPromptRequirements(options.ailiHome) : [])
  ];
  const config = profile === "opencode" ? await readOpenCodeConfig(options.opencodeHome) : { value: undefined };
  const defaultAgent = typeof config.value?.default_agent === "string" ? config.value.default_agent : null;
  const roseModel = typeof config.value?.agent?.rose?.model === "string" ? config.value.agent.rose.model : null;
  const playwright = config.value?.mcp?.playwright ? "configured" : "missing-optional";
  const codegraph = await codegraphStatus(config.value?.mcp?.codegraph);
  const mempalaceMcp = await planMemPalaceMcpConfiguration({
    ailiHome: options.ailiHome,
    adapter: profile,
    readiness: mempalace,
    configured: Boolean(config.value?.mcp?.mempalace)
  });
  const graphifyCli = await inspectGraphifyVersion(runReadOnlyCommand);
  const graphifyHome = process.env.HOME || os.homedir();
  const graphifyPath = path.join(graphifyHome, ".agents", "skills", "graphify");
  let graphifyGlobalSkill: DoctorSummary["graphifyGlobalSkill"];
  try {
    const graphifySkillInventory = await inspectGraphifySkillInventory(graphifyHome);
    graphifyGlobalSkill = {
      status: !graphifySkillInventory.target.present ? "missing" : graphifySkillInventory.target.valid ? "registered" : "invalid",
      path: graphifySkillInventory.target.root,
      versionStampPath: graphifySkillInventory.target.versionStampPath,
      referencesPath: graphifySkillInventory.target.referencesPath,
      version: graphifySkillInventory.target.version,
      referencesPresent: graphifySkillInventory.target.referencesPresent,
      issues: graphifySkillInventory.target.issues,
      ownership: "upstream"
    };
  } catch (error: unknown) {
    graphifyGlobalSkill = {
      status: "invalid",
      path: graphifyPath,
      versionStampPath: path.join(graphifyPath, ".graphify_version"),
      referencesPath: path.join(graphifyPath, "references"),
      referencesPresent: false,
      issues: [error instanceof Error ? error.message : String(error)],
      ownership: "upstream"
    };
  }
  const installOk = required.every((entry) => entry.installed);
  const source = await sourceReadiness(options.ailiHome, manifest);
  return {
    ok: installOk,
    profile,
    selectedSkills: selectedSkills.map((skill) => skill.name),
    install: { ok: installOk, required },
    required,
    source,
    defaultAgent,
    roseModel,
    playwright,
    codegraph,
    graphifyCli,
    graphifyGlobalSkill,
    officecli,
    mempalace,
    mempalaceMcp,
    plugins: manifest.components.plugins.map((entry) => ({ name: entry.name, status: "missing-optional" })),
    unavailableCapabilities: [
      ...(officecli.status === "ready" ? [] : [{ name: "officecli", reason: officecli.reason ?? "Managed OfficeCLI is unavailable." }]),
      ...(mempalace.status === "compatible" && mempalaceMcp.status === "already-configured"
        ? []
        : [{ name: "mempalace", reason: mempalaceMcp.reason || mempalace.reason || "MemPalace is unavailable or unconfigured; memory-dependent operations fail closed." }])
    ]
  };
}

function runReadOnlyCommand(command: string, args: string[], cwd?: string): Promise<{ code: number | null; detail: string; stdout: string }> {
  return new Promise((resolve) => {
    let stdout = "";
    let stderr = "";
    const child = spawn(command, args, {
      cwd,
      stdio: ["ignore", "pipe", "pipe"],
      env: {
        HOME: process.env.HOME || os.homedir(),
        PATH: sanitizedReadOnlyPath(process.env.PATH ?? "/usr/bin:/bin:/usr/sbin:/sbin")
      }
    });
    child.stdout?.setEncoding("utf8");
    child.stdout?.on("data", (chunk: string) => { stdout += chunk; });
    child.stderr?.setEncoding("utf8");
    child.stderr?.on("data", (chunk: string) => { stderr += chunk; });
    child.on("error", (error: NodeJS.ErrnoException) => {
      resolve({ code: null, detail: error.code === "ENOENT" ? `${command} command not found` : error.message, stdout: stdout.trim() });
    });
    child.on("close", (code) => resolve({ code, detail: stderr.trim(), stdout: stdout.trim() }));
  });
}

function sanitizedReadOnlyPath(rawPath: string): string {
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

async function sourceReadiness(ailiHome: string, manifest: Awaited<ReturnType<typeof loadManifest>>): Promise<DoctorSummary["source"]> {
  const sharedSkillsPath = path.join(ailiHome, ".agents", "skills");
  const sharedSkills = { status: (await isDirectory(sharedSkillsPath)) ? "ready" as const : "missing" as const, path: sharedSkillsPath };
  const manifestDrift = await manifestDriftStatus(ailiHome, manifest);
  const agentsMd = await agentsMdFreshness(ailiHome);
  const generated = await generatedReadiness(ailiHome, manifest);
  return {
    ok: sharedSkills.status === "ready" && manifestDrift.ok && agentsMd.status === "fresh" && generated.status === "ready",
    sharedSkills,
    manifestDrift,
    agentsMd,
    generated
  };
}

async function generatedReadiness(ailiHome: string, manifest: Awaited<ReturnType<typeof loadManifest>>): Promise<DoctorSummary["source"]["generated"]> {
  const inventory = await runtimeProjectionInventory(ailiHome, manifest);
  if (inventory.issues.length > 0) return { status: "drift", paths: [], issues: inventory.issues };
  const issues: string[] = [];
  const paths: string[] = [];
  const expectedGenerated = new Set<string>();
  for (const [adapter, expectedOutputs] of Object.entries(inventory.outputs)) {
    const provenancePath = `generated/${adapter}/provenance.json`;
    paths.push(provenancePath, ...expectedOutputs);
    expectedGenerated.add(provenancePath);
    for (const output of expectedOutputs) {
      if (output.startsWith("generated/")) expectedGenerated.add(output);
    }
    let provenance: { canonicalInputs?: unknown; inputSha256?: unknown; outputs?: unknown };
    try {
      provenance = JSON.parse(await readFile(path.join(ailiHome, provenancePath), "utf8"));
    } catch {
      issues.push(`Missing or unreadable generated provenance: ${provenancePath}`);
      continue;
    }
    const outputs = Array.isArray(provenance.outputs) ? provenance.outputs as Array<{ path?: unknown; outputSha256?: unknown }> : [];
    const outputPaths = outputs.map((output) => output.path).filter((entry): entry is string => typeof entry === "string");
    if (outputs.length !== expectedOutputs.length || new Set(outputPaths).size !== outputPaths.length || outputPaths.length !== expectedOutputs.length || expectedOutputs.some((expected) => !outputPaths.includes(expected))) {
      issues.push(`Generated ${adapter} provenance does not declare exactly the expected runtime projections.`);
    }
    for (const output of outputs) {
      if (typeof output.path !== "string" || typeof output.outputSha256 !== "string") {
        issues.push(`Generated ${adapter} provenance contains an invalid output record.`);
        continue;
      }
      try {
        const actual = createHash("sha256").update(await readFile(path.join(ailiHome, output.path))).digest("hex");
        if (actual !== output.outputSha256) issues.push(`Generated output drift: ${output.path}`);
      } catch {
        issues.push(`Missing generated output: ${output.path}`);
      }
    }
    const inputs = Array.isArray(provenance.canonicalInputs) && provenance.canonicalInputs.every((entry) => typeof entry === "string")
      ? provenance.canonicalInputs as string[]
      : [];
    if (inputs.length === 0 || typeof provenance.inputSha256 !== "string") {
      issues.push(`Generated ${adapter} provenance is missing canonical input hashes.`);
    } else {
      try {
        const source = (await Promise.all(inputs.slice().sort().map(async (relativePath) => `${relativePath}\u0000${createHash("sha256").update(await readFile(path.join(ailiHome, relativePath))).digest("hex")}`))).join("\n");
        if (createHash("sha256").update(source).digest("hex") !== provenance.inputSha256) issues.push(`Canonical input drift from ${adapter} generated provenance.`);
      } catch {
        issues.push(`A ${adapter} generated provenance canonical input is missing or unreadable.`);
      }
    }
  }
  for (const actual of await listRelativeFiles(ailiHome, "generated")) {
    if (!expectedGenerated.has(actual)) issues.push(`Unexpected generated output: ${actual}`);
  }
  return { status: issues.length > 0 ? "drift" : "ready", paths: [...new Set(paths)].sort(), issues };
}

async function runtimeProjectionInventory(ailiHome: string, manifest: Awaited<ReturnType<typeof loadManifest>>): Promise<{
  outputs: Record<"opencode" | "pi", string[]>;
  issues: string[];
}> {
  const issues: string[] = [];
  let projection: { schemaVersion?: unknown; generator?: { id?: unknown }; commands?: unknown; agents?: unknown; protocols?: unknown };
  try {
    projection = JSON.parse(await readFile(path.join(ailiHome, "manifests", "runtime-projections.json"), "utf8"));
  } catch {
    return { outputs: { opencode: [], pi: [] }, issues: ["Missing or unreadable runtime projection manifest."] };
  }
  const commands = stringList(projection.commands, "runtime projection command inventory", issues);
  const agents = stringList(projection.agents, "runtime projection agent inventory", issues);
  const protocols = stringList(projection.protocols, "runtime projection protocol inventory", issues);
  if (projection.schemaVersion !== 1 || projection.generator?.id !== "aili-runtime-projections/v1") {
    issues.push("Unsupported runtime projection manifest.");
  }
  const manifestCommands = manifest.components.commands.map((entry) => entry.name).sort();
  const manifestAgents = manifest.components.agents.map((entry) => entry.name).sort();
  if (!sameStringSet(commands, manifestCommands)) issues.push("Runtime projection commands differ from the retained command catalog.");
  if (!sameStringSet(agents, manifestAgents)) issues.push("Runtime projection agents differ from the retained agent catalog.");
  const opencode = [
    "generated/opencode/AGENTS.md",
    ...commands.map((name) => `generated/opencode/commands/${name}.md`),
    ...agents.map((name) => `generated/opencode/agents/${name}.md`),
    "templates/opencode-global-AGENTS.md",
    ...commands.map((name) => `commands/${name}.md`),
    ...agents.map((name) => `agents/${name}.md`)
  ].sort();
  const pi = [
    "generated/pi/system.md",
    "generated/pi/role-metadata.json",
    "generated/pi/selection-map.json",
    "generated/pi/installation-contract.json",
    ...commands.map((name) => `generated/pi/prompts/${name}.md`),
    ...protocols.map((name) => `generated/pi/protocols/${name}`)
  ].sort();
  return { outputs: { opencode, pi }, issues };
}

function stringList(value: unknown, label: string, issues: string[]): string[] {
  if (!Array.isArray(value) || value.some((entry) => typeof entry !== "string") || new Set(value).size !== value.length) {
    issues.push(`Invalid ${label}.`);
    return [];
  }
  return value.slice().sort() as string[];
}

function sameStringSet(left: string[], right: string[]): boolean {
  return left.length === right.length && left.every((entry, index) => entry === right[index]);
}

async function listRelativeFiles(ailiHome: string, relativeRoot: string): Promise<string[]> {
  const root = path.join(ailiHome, relativeRoot);
  let entries;
  try {
    entries = await readdir(root, { withFileTypes: true });
  } catch {
    return [];
  }
  const files: string[] = [];
  for (const entry of entries) {
    const relativePath = path.posix.join(relativeRoot, entry.name);
    if (entry.isDirectory()) files.push(...await listRelativeFiles(ailiHome, relativePath));
    else if (entry.isFile()) files.push(relativePath);
  }
  return files.sort();
}

async function piPromptRequirements(ailiHome: string): Promise<Array<{ type: string; name: string; installed: boolean }>> {
  const promptRoot = path.join(sharedInstallHome(), ".pi", "agent", "prompts");
  let entries: string[];
  try {
    entries = (await readdir(path.join(ailiHome, "generated", "pi", "prompts"))).filter((entry) => entry.endsWith(".md"));
  } catch {
    entries = [];
  }
  return Promise.all(entries.sort().map(async (name) => ({ type: "pi-prompt", name, installed: await exists(path.join(promptRoot, name)) })));
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
