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
  groups?: SkillGroup[];
  repositoryManaged?: boolean;
}

export type SkillGroup = "research" | "specialized-dev";

export interface RetiredSkill {
  name: string;
  path: string;
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
  retiredSkills?: RetiredSkill[];
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

export function resolveSkillSelection(manifest: ComponentManifest, skillNames: string[] = [], groupNames: string[] = []): RepoComponent[] {
  validateManifestComponentDefinitions(manifest);
  const skills = manifest.components.skills;
  const byName = new Map(skills.map((skill) => [skill.name, skill]));
  const groups = new Set<SkillGroup>(["research", "specialized-dev"]);
  const selected = new Set(skills.filter((skill) => skill.defaultInstalled).map((skill) => skill.name));

  for (const name of skillNames) {
    if (!byName.has(name)) throw new Error(`Unknown skill: ${name}`);
    selected.add(name);
  }
  for (const group of groupNames) {
    if (!groups.has(group as SkillGroup)) throw new Error(`Unknown skill group: ${group}`);
    for (const skill of skills) {
      if (skill.groups?.includes(group as SkillGroup)) selected.add(skill.name);
    }
  }
  return skills.filter((skill) => selected.has(skill.name));
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
  const drift = await repoManifestDrift(ailiHome, expected, manifest.retiredSkills?.map((entry) => entry.name) ?? []);
  for (const type of ["agents", "commands", "skills"] as const) {
    const entry = drift[type];
    if (entry.unmanifested.length > 0) throw new Error(`Unmanifested ${type} component(s): ${entry.unmanifested.join(", ")}`);
    if (entry.missing.length > 0) throw new Error(`Manifest ${type} component(s) missing from AILI_HOME: ${entry.missing.join(", ")}`);
  }
}

export async function checkRepoManifestDrift(ailiHome: string, manifest: ComponentManifest): Promise<RepoManifestDrift> {
  const expected = validateManifestComponentDefinitions(manifest);
  return repoManifestDrift(ailiHome, expected, manifest.retiredSkills?.map((entry) => entry.name) ?? []);
}

function validateManifestComponentDefinitions(manifest: ComponentManifest): Record<RepoManifestKind, string[]> {
  validateSkillTiers(manifest);
  validateCommandCatalog(manifest);
  return {
    agents: manifest.components.agents.map((entry) => validateRepoEntry("agents", entry, `agents/${entry.name}.md`)),
    commands: manifest.components.commands.map((entry) => validateRepoEntry("commands", entry, `commands/${entry.name}.md`)),
    skills: manifest.components.skills.map(validateSkillEntry)
  };
}

function validateCommandCatalog(manifest: ComponentManifest): void {
  const expected = [
    "ideate",
    "define",
    "build",
    "ship",
    "local-review",
    "handoff",
    "agents-md",
    "harness-audit",
    "retro",
    "security-review"
  ].sort();
  const actual = manifest.components.commands.map((command) => command.name).sort();
  if (actual.join("\u0000") !== expected.join("\u0000")) {
    throw new Error(`Command inventory must be exactly: ${expected.join(", ")}`);
  }
}

function validateSkillTiers(manifest: ComponentManifest): void {
  const skills = manifest.components.skills;
  const optional = [
    "academic-paper-review",
    "systematic-literature-review",
    "newsletter-generation",
    "consulting-analysis",
    "android-native-dev",
    "ios-application-dev",
    "flutter-dev",
    "react-native-dev",
    "shader-dev"
  ];
  const groups: Record<SkillGroup, string[]> = {
    research: optional.slice(0, 4),
    "specialized-dev": optional.slice(4)
  };
  const retired = [
    "local-review-gate",
    "session-handoff",
    "agents-md-initialization",
    "harness-optimization-audit",
    "evidence-scoped-retrospective",
    "rose-memory"
  ];
  if (skills.length !== 58) throw new Error(`Expected exactly 58 retained Skills, found ${skills.length}.`);
  if (skills.filter((skill) => skill.defaultInstalled).length !== 49) throw new Error("Expected exactly 49 default-installed Core Skills.");
  const optionalNames = skills.filter((skill) => !skill.defaultInstalled).map((skill) => skill.name).sort();
  if (optionalNames.join("\u0000") !== optional.slice().sort().join("\u0000")) {
    throw new Error(`Optional Skill inventory must be exactly: ${optional.join(", ")}`);
  }
  for (const [group, expected] of Object.entries(groups) as Array<[SkillGroup, string[]]>) {
    const actual = skills.filter((skill) => skill.groups?.includes(group)).map((skill) => skill.name).sort();
    if (actual.join("\u0000") !== expected.slice().sort().join("\u0000")) {
      throw new Error(`Skill group ${group} must be exactly: ${expected.join(", ")}`);
    }
  }
  for (const skill of skills) {
    if (skill.groups?.some((group) => group !== "research" && group !== "specialized-dev")) {
      throw new Error(`Unknown Skill group for ${skill.name}.`);
    }
  }
  const retiredEntries = manifest.retiredSkills ?? [];
  if (retiredEntries.map((entry) => entry.name).sort().join("\u0000") !== retired.slice().sort().join("\u0000")) {
    throw new Error(`Deferred retired Skill inventory must be exactly: ${retired.join(", ")}`);
  }
  for (const entry of retiredEntries) {
    if (entry.path !== `.agents/skills/${entry.name}`) throw new Error(`Invalid retired Skill path for ${entry.name}: ${entry.path}`);
    validateRelativeComponentPath(`retired Skill for ${entry.name}`, entry.path);
  }
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

async function repoManifestDrift(ailiHome: string, expected: Record<RepoManifestKind, string[]>, retiredSkills: string[]): Promise<RepoManifestDrift> {
  return {
    agents: completeAllowlist(expected.agents, await listAgentNames(ailiHome)),
    commands: completeAllowlist(expected.commands, await listCommandNames(ailiHome)),
    skills: completeAllowlist(expected.skills, await listSkillNames(ailiHome, expected.skills, retiredSkills))
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

async function listSkillNames(ailiHome: string, manifestNames: string[], retiredSkillNames: string[]): Promise<string[]> {
  const shared = await listSkillNamesAt(path.join(ailiHome, ".agents", "skills"));
  const opencode = await listSkillNamesAt(path.join(ailiHome, ".opencode", "skills"));
  const expected = new Set(manifestNames);
  const retired = new Set(retiredSkillNames);
  const names = [...shared.filter((name) => !retired.has(name)), ...opencode.filter((name) => expected.has(name))];
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
