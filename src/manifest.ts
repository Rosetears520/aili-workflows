import { constants, type Dirent } from "node:fs";
import { access, readdir, readFile } from "node:fs/promises";
import path from "node:path";

export interface RepoComponent {
  name: string;
  path: string;
  sourcePath?: string;
  sourceFallbackPaths?: string[];
  installTargets?: RepoInstallTarget[];
  required?: boolean;
  defaultInstalled?: boolean;
  repositoryManaged?: boolean;
}

export type RepoInstallTargetKind = "shared" | "opencode";

export interface RepoInstallTarget {
  kind: RepoInstallTargetKind;
  path: string;
}

export interface McpComponent {
  name: string;
  optional?: boolean;
  defaultInstalled?: boolean;
  thirdParty?: boolean;
  source: string;
  trust: string;
  config: Record<string, unknown>;
}

export interface PluginComponent {
  name: string;
  optional?: boolean;
  defaultInstalled?: boolean;
  thirdParty?: boolean;
  enabled?: boolean;
  source: string;
  trust: string;
  install?: { status: string; reason: string };
}

export interface ComponentManifest {
  schemaVersion: number;
  name: string;
  components: {
    agents: RepoComponent[];
    commands: RepoComponent[];
    skills: RepoComponent[];
    mcp: McpComponent[];
    plugins: PluginComponent[];
  };
}

export type RepoManifestKind = "agents" | "commands" | "skills";

export interface RepoManifestDriftEntry {
  missing: string[];
  unmanifested: string[];
}

export type RepoManifestDrift = Record<RepoManifestKind, RepoManifestDriftEntry>;

export async function loadManifest(ailiHome: string): Promise<ComponentManifest> {
  const manifestPath = path.join(ailiHome, "manifests", "rose-aili.components.json");
  const raw = await readFile(manifestPath, "utf8");
  const manifest = JSON.parse(raw) as ComponentManifest;
  if (manifest.name !== "rose-aili" || manifest.schemaVersion !== 1) {
    throw new Error(`Unsupported component manifest: ${manifestPath}`);
  }
  return manifest;
}

export function findMcp(manifest: ComponentManifest, name: string): McpComponent | undefined {
  return manifest.components.mcp.find((entry) => entry.name === name);
}

export function findPlugin(manifest: ComponentManifest, name: string): PluginComponent | undefined {
  return manifest.components.plugins.find((entry) => entry.name === name);
}

export function repoSourcePaths(component: RepoComponent): string[] {
  return uniquePaths([
    component.sourcePath,
    ...(component.sourceFallbackPaths ?? []),
    component.path
  ]);
}

export function repoInstallTargets(component: RepoComponent, defaultTargetPath = component.path): RepoInstallTarget[] {
  const targets = component.installTargets?.length
    ? component.installTargets
    : [{ kind: "opencode", path: defaultTargetPath } satisfies RepoInstallTarget];
  for (const target of targets) {
    validateRelativeComponentPath(`install target for ${component.name}`, target.path);
    if (target.kind !== "shared" && target.kind !== "opencode") {
      throw new Error(`Invalid install target kind for ${component.name}: ${target.kind}`);
    }
  }
  return targets;
}

export function opencodeInstallTargets(component: RepoComponent, defaultTargetPath = component.path): RepoInstallTarget[] {
  return repoInstallTargets(component, defaultTargetPath).filter((target) => target.kind === "opencode");
}

export function validateRelativeComponentPath(label: string, entryPath: string): void {
  if (!entryPath || path.isAbsolute(entryPath) || entryPath.split(/[\\/]/).includes("..")) {
    throw new Error(`Invalid manifest ${label} path: ${entryPath}`);
  }
}

export async function validateManifestAllowlist(ailiHome: string, manifest: ComponentManifest): Promise<void> {
  const expected = validateManifestComponentDefinitions(manifest);
  const drift = await repoManifestDrift(ailiHome, expected);
  for (const type of ["agents", "commands", "skills"] as const) {
    const entry = drift[type];
    if (entry.unmanifested.length > 0) throw new Error(`Unmanifested ${type} component(s): ${entry.unmanifested.join(", ")}`);
    if (entry.missing.length > 0) throw new Error(`Manifest ${type} component(s) missing from AILI_HOME: ${entry.missing.join(", ")}`);
  }
}

export async function checkRepoManifestDrift(ailiHome: string, manifest: ComponentManifest): Promise<RepoManifestDrift> {
  const expected = validateManifestComponentDefinitions(manifest);
  return repoManifestDrift(ailiHome, expected);
}

function validateManifestComponentDefinitions(manifest: ComponentManifest): Record<RepoManifestKind, string[]> {
  return {
    agents: manifest.components.agents.map((entry) => validateRepoEntry("agents", entry, `agents/${entry.name}.md`)),
    commands: manifest.components.commands.map((entry) => validateRepoEntry("commands", entry, `commands/${entry.name}.md`)),
    skills: manifest.components.skills.map(validateSkillEntry)
  };
}

function validateSkillEntry(entry: RepoComponent): string {
  const targets = repoInstallTargets(entry, entry.path);
  if (targets.length !== 1) throw new Error(`Invalid manifest skills installTargets for ${entry.name}: expected exactly one platform owner.`);
  const target = targets[0];
  const expectedPath = target.kind === "shared" ? `.agents/skills/${entry.name}` : `.opencode/skills/${entry.name}`;
  const expectedTargetPath = target.kind === "shared" ? expectedPath : `skills/${entry.name}`;
  return validateRepoEntry("skills", entry, expectedPath, {
    sourcePath: expectedPath,
    installTargets: [{ kind: target.kind, path: expectedTargetPath }]
  });
}

function validateRepoEntry(type: string, entry: RepoComponent, expectedPath: string, expected?: { sourcePath: string; installTargets: Array<{ kind: "shared" | "opencode"; path: string }> }): string {
  if (!entry.name) throw new Error(`Invalid manifest ${type} entry without name.`);
  validateRelativeComponentPath(`${type} for ${entry.name}`, entry.path);
  for (const sourcePath of repoSourcePaths(entry)) {
    validateRelativeComponentPath(`${type} source for ${entry.name}`, sourcePath);
  }
  if (entry.path !== expectedPath) {
    throw new Error(`Invalid manifest ${type} path for ${entry.name}: expected ${expectedPath}, got ${entry.path}`);
  }
  if (expected && entry.sourcePath && entry.sourcePath !== expected.sourcePath) {
    throw new Error(`Invalid manifest ${type} sourcePath for ${entry.name}: expected ${expected.sourcePath}, got ${entry.sourcePath}`);
  }
  const targets = repoInstallTargets(entry, expectedPath);
  if (expected) {
    assertExpectedInstallTargets(type, entry.name, targets, expected.installTargets);
  }
  return entry.name;
}

function assertExpectedInstallTargets(type: string, name: string, actual: Array<{ kind: "shared" | "opencode"; path: string }>, expected: Array<{ kind: "shared" | "opencode"; path: string }>): void {
  if (actual.length !== expected.length) {
    throw new Error(`Invalid manifest ${type} installTargets for ${name}: expected ${expected.length}, got ${actual.length}`);
  }
  for (const expectedTarget of expected) {
    if (!actual.some((target) => target.kind === expectedTarget.kind && target.path === expectedTarget.path)) {
      throw new Error(`Invalid manifest ${type} installTargets for ${name}: missing ${expectedTarget.kind}:${expectedTarget.path}`);
    }
  }
}

async function repoManifestDrift(ailiHome: string, expected: Record<RepoManifestKind, string[]>): Promise<RepoManifestDrift> {
  return {
    agents: completeAllowlist(expected.agents, await listAgentNames(ailiHome)),
    commands: completeAllowlist(expected.commands, await listCommandNames(ailiHome)),
    skills: completeAllowlist(expected.skills, await listSkillNames(ailiHome, expected.skills))
  };
}

function completeAllowlist(manifestNames: string[], diskNames: string[]): RepoManifestDriftEntry {
  const manifestSet = new Set(manifestNames);
  if (manifestSet.size !== manifestNames.length) throw new Error("Duplicate manifest component entry.");
  const diskSet = new Set(diskNames);
  if (diskSet.size !== diskNames.length) throw new Error("Duplicate repository component entry.");
  return {
    unmanifested: diskNames.filter((name) => !manifestSet.has(name)),
    missing: manifestNames.filter((name) => !diskNames.includes(name))
  };
}

async function listAgentNames(ailiHome: string): Promise<string[]> {
  return listMarkdownComponentNames(path.join(ailiHome, "agents"));
}

async function listCommandNames(ailiHome: string): Promise<string[]> {
  return listMarkdownComponentNames(path.join(ailiHome, "commands"));
}

async function listMarkdownComponentNames(root: string): Promise<string[]> {
  let entries: Dirent[];
  try {
    entries = await readdir(root, { withFileTypes: true });
  } catch {
    return [];
  }
  return entries
    .filter((entry) => entry.isFile() && entry.name.endsWith(".md"))
    .map((entry) => path.basename(entry.name, ".md"))
    .sort();
}

async function listSkillNames(ailiHome: string, manifestNames: string[]): Promise<string[]> {
  const shared = await listSkillNamesAt(path.join(ailiHome, ".agents", "skills"));
  const opencode = await listSkillNamesAt(path.join(ailiHome, ".opencode", "skills"));
  const expected = new Set(manifestNames);
  const names = [...shared, ...opencode.filter((name) => expected.has(name))];
  return names.sort();
}

async function listSkillNamesAt(root: string): Promise<string[]> {
  let entries: Dirent[];
  try {
    entries = await readdir(root, { withFileTypes: true });
  } catch {
    return [];
  }
  const names: string[] = [];
  for (const entry of entries) {
    if (!entry.isDirectory()) continue;
    try {
      await access(path.join(root, entry.name, "SKILL.md"), constants.F_OK);
      names.push(entry.name);
    } catch {
      // Non-skill directories match installer behavior.
    }
  }
  return names;
}

function uniquePaths(paths: Array<string | undefined>): string[] {
  const result: string[] = [];
  for (const entryPath of paths) {
    if (!entryPath || result.includes(entryPath)) continue;
    validateRelativeComponentPath("source", entryPath);
    result.push(entryPath);
  }
  return result;
}
