import { createHash } from "node:crypto";
import { lstat, readFile, readdir, readlink } from "node:fs/promises";
import os from "node:os";
import path from "node:path";

export const GRAPHIFY_CLI_INSTALL_COMMAND = ["uv", "tool", "install", "graphifyy"] as const;
export const GRAPHIFY_SKILL_INSTALL_COMMAND = ["graphify", "install", "--platform", "agents"] as const;
export const GRAPHIFY_SKILL_RELATIVE_PATH = path.join(".agents", "skills", "graphify");

export interface CapturedCommand {
  code: number | null;
  detail: string;
  stdout: string;
}

export type GraphifyCommandRunner = (command: string, args: string[], cwd?: string) => Promise<CapturedCommand>;

export interface GraphifyVersionStatus {
  status: "installed" | "missing";
  observedVersion?: string;
  output?: string;
  reason?: string;
  ownership: "upstream";
}

export interface GraphifyCliPreflight {
  status: "installed" | "absent" | "prerequisite-missing" | "conflict";
  observedVersion?: string;
  uvVersion?: string;
  uvToolDirectory?: string;
  uvBinDirectory?: string;
  reason?: string;
}

export interface GraphifySkillPathState {
  root: string;
  skillPath: string;
  versionStampPath: string;
  referencesPath: string;
  present: boolean;
  skillPresent: boolean;
  versionStampPresent: boolean;
  valid: boolean;
  version?: string;
  referencesPresent: boolean;
  issues: string[];
}

export interface GraphifySkillInventory {
  target: GraphifySkillPathState;
  candidates: GraphifySkillPathState[];
  existingVersionStampPaths: string[];
  ambiguousPaths: string[];
}

export async function inspectGraphifyVersion(run: GraphifyCommandRunner): Promise<GraphifyVersionStatus> {
  const result = await run("graphify", ["--version"]);
  const output = result.stdout.trim();
  if (result.code !== 0 || !output) {
    return {
      status: "missing",
      reason: result.detail || (result.code === 0 ? "graphify --version returned no output" : "graphify command is unavailable"),
      ownership: "upstream"
    };
  }
  return {
    status: "installed",
    observedVersion: extractVersion(output),
    output,
    ownership: "upstream"
  };
}

export async function inspectGraphifyCliPreflight(run: GraphifyCommandRunner): Promise<GraphifyCliPreflight> {
  const uvVersionResult = await run("uv", ["--version"]);
  const graphify = await inspectGraphifyVersion(run);
  if (uvVersionResult.code !== 0 || !uvVersionResult.stdout.trim()) {
    return {
      status: graphify.status === "installed" ? "conflict" : "prerequisite-missing",
      observedVersion: graphify.observedVersion,
      reason: graphify.status === "installed"
        ? "graphify is available but existing uv ownership cannot be verified because uv is unavailable"
        : "uv is required; install uv separately before enabling Graphify"
    };
  }

  const toolDirectoryResult = await run("uv", ["tool", "dir"]);
  const binDirectoryResult = await run("uv", ["tool", "dir", "--bin"]);
  const listResult = await run("uv", ["tool", "list"]);
  const failed = [toolDirectoryResult, binDirectoryResult].find((result) => result.code !== 0 || !result.stdout.trim())
    ?? (listResult.code !== 0 ? listResult : undefined);
  if (failed) {
    return {
      status: "conflict",
      observedVersion: graphify.observedVersion,
      uvVersion: uvVersionResult.stdout.trim(),
      reason: failed.detail || "uv tool ownership or target paths could not be inventoried"
    };
  }

  const uvOwnsGraphify = /^graphifyy(?:\s+.*)?$/mu.test(listResult.stdout);
  const graphifyExists = graphify.status === "installed";
  if (uvOwnsGraphify !== graphifyExists) {
    return {
      status: "conflict",
      observedVersion: graphify.observedVersion,
      uvVersion: uvVersionResult.stdout.trim(),
      uvToolDirectory: toolDirectoryResult.stdout.trim(),
      uvBinDirectory: binDirectoryResult.stdout.trim(),
      reason: uvOwnsGraphify
        ? "uv records graphifyy but graphify --version is unavailable"
        : "graphify is available but uv tool list does not record graphifyy"
    };
  }

  return {
    status: graphifyExists ? "installed" : "absent",
    observedVersion: graphify.observedVersion,
    uvVersion: uvVersionResult.stdout.trim(),
    uvToolDirectory: toolDirectoryResult.stdout.trim(),
    uvBinDirectory: binDirectoryResult.stdout.trim()
  };
}

export function graphifyGlobalSkillRoots(home = os.homedir()): string[] {
  const relativeRoots = [
    [".claude", "skills", "graphify"],
    [".codex", "skills", "graphify"],
    [".config", "opencode", "skills", "graphify"],
    [".config", "kilo", "skills", "graphify"],
    [".aider", "graphify"],
    [".copilot", "skills", "graphify"],
    [".openclaw", "skills", "graphify"],
    [".factory", "skills", "graphify"],
    [".trae", "skills", "graphify"],
    [".trae-cn", "skills", "graphify"],
    [".hermes", "skills", "graphify"],
    [".kiro", "skills", "graphify"],
    [".pi", "agent", "skills", "graphify"],
    [".codebuddy", "skills", "graphify"],
    [".agents", "skills", "graphify"],
    [".kimi", "skills", "graphify"],
    [".config", "agents", "skills", "graphify"],
    [".config", "devin", "skills", "graphify"]
  ];
  return [...new Set(relativeRoots.map((parts) => path.join(home, ...parts)))];
}

export async function inspectGraphifySkillInventory(home = os.homedir()): Promise<GraphifySkillInventory> {
  const roots = graphifyGlobalSkillRoots(home);
  const candidates = await Promise.all(roots.map((root) => inspectGraphifySkillPath(root, home)));
  const targetRoot = path.join(home, GRAPHIFY_SKILL_RELATIVE_PATH);
  const target = candidates.find((candidate) => candidate.root === targetRoot);
  if (!target) throw new Error(`Graphify agents target is missing from the inventory: ${targetRoot}`);
  return {
    target,
    candidates,
    existingVersionStampPaths: candidates.filter((candidate) => candidate.versionStampPresent).map((candidate) => candidate.versionStampPath),
    ambiguousPaths: candidates.filter((candidate) => candidate.present && !candidate.valid).map((candidate) => candidate.root)
  };
}

export async function verifyGraphifyCatalog(run: GraphifyCommandRunner, targetSkillPath: string): Promise<{ ok: boolean; reason?: string; route?: { name: string; location: string } }> {
  const result = await run("opencode", ["--pure", "debug", "skill"], os.tmpdir());
  if (result.code !== 0) return { ok: false, reason: result.detail || "OpenCode skill catalog command failed" };
  let value: unknown;
  try {
    value = JSON.parse(result.stdout);
  } catch {
    return { ok: false, reason: "OpenCode skill catalog did not return one JSON document" };
  }
  if (!Array.isArray(value)) return { ok: false, reason: "OpenCode skill catalog is not an array" };
  const routes = value.filter((entry): entry is { name: string; location: string } => (
    typeof entry === "object" && entry !== null
    && (entry as Record<string, unknown>).name === "graphify"
    && typeof (entry as Record<string, unknown>).location === "string"
  ));
  if (routes.length !== 1) return { ok: false, reason: `OpenCode catalog resolved ${routes.length} graphify routes instead of exactly one` };
  if (path.resolve(routes[0].location) !== path.resolve(targetSkillPath)) {
    return { ok: false, reason: `OpenCode graphify route points to ${routes[0].location} instead of ${targetSkillPath}` };
  }
  return { ok: true, route: routes[0] };
}

export async function fingerprintPath(targetPath: string): Promise<string | null> {
  try {
    const hash = createHash("sha256");
    await appendFingerprint(hash, targetPath, ".");
    return hash.digest("hex");
  } catch (error: unknown) {
    if ((error as NodeJS.ErrnoException).code === "ENOENT") return null;
    throw error;
  }
}

export async function treeContainsSymlink(targetPath: string): Promise<boolean> {
  try {
    const value = await lstat(targetPath);
    if (value.isSymbolicLink()) return true;
    if (!value.isDirectory()) return false;
    for (const entry of await readdir(targetPath)) {
      if (await treeContainsSymlink(path.join(targetPath, entry))) return true;
    }
    return false;
  } catch (error: unknown) {
    if ((error as NodeJS.ErrnoException).code === "ENOENT") return false;
    throw error;
  }
}

async function inspectGraphifySkillPath(root: string, home: string): Promise<GraphifySkillPathState> {
  const skillPath = path.join(root, "SKILL.md");
  const versionStampPath = path.join(root, ".graphify_version");
  const referencesPath = path.join(root, "references");
  const rootState = await pathKind(root);
  if (rootState === "missing") {
    return { root, skillPath, versionStampPath, referencesPath, present: false, skillPresent: false, versionStampPresent: false, valid: false, referencesPresent: false, issues: [] };
  }

  const issues: string[] = [];
  if (rootState !== "directory" || await hasSymlinkBelow(home, root)) {
    issues.push(rootState !== "directory" ? "skill root is not a regular directory" : "skill root has a symlinked ancestor below HOME");
    return { root, skillPath, versionStampPath, referencesPath, present: true, skillPresent: false, versionStampPresent: false, valid: false, referencesPresent: false, issues };
  }
  const skillState = await pathKind(skillPath);
  const stampState = await pathKind(versionStampPath);
  const referencesState = await pathKind(referencesPath);
  if (skillState !== "file") issues.push("SKILL.md is missing or not a regular file");
  if (stampState !== "file") issues.push(".graphify_version is missing or not a regular file");
  if (referencesState !== "missing" && referencesState !== "directory") issues.push("references is not a regular directory");
  if (referencesState === "directory" && !(await directoryContainsOnlyRegularEntries(referencesPath))) {
    issues.push("references contains a symlink or special entry");
  }
  let version: string | undefined;
  if (stampState === "file") {
    version = (await readFile(versionStampPath, "utf8")).trim();
    if (!version) issues.push(".graphify_version is empty");
  }
  return {
    root,
    skillPath,
    versionStampPath,
    referencesPath,
    present: true,
    skillPresent: skillState === "file",
    versionStampPresent: stampState === "file",
    valid: issues.length === 0,
    version,
    referencesPresent: referencesState === "directory",
    issues
  };
}

async function pathKind(targetPath: string): Promise<"missing" | "file" | "directory" | "other"> {
  try {
    const value = await lstat(targetPath);
    if (value.isFile()) return "file";
    if (value.isDirectory()) return "directory";
    return "other";
  } catch (error: unknown) {
    if ((error as NodeJS.ErrnoException).code === "ENOENT") return "missing";
    throw error;
  }
}

async function directoryContainsOnlyRegularEntries(directory: string): Promise<boolean> {
  const entries = await readdir(directory, { withFileTypes: true });
  if (entries.length === 0) return false;
  for (const entry of entries) {
    const entryPath = path.join(directory, entry.name);
    if (entry.isFile()) continue;
    if (entry.isDirectory() && await directoryContainsOnlyRegularEntries(entryPath)) continue;
    return false;
  }
  return true;
}

async function hasSymlinkBelow(parent: string, target: string): Promise<boolean> {
  const relative = path.relative(parent, target);
  if (!relative || relative.startsWith("..") || path.isAbsolute(relative)) return true;
  let current = parent;
  for (const part of relative.split(path.sep)) {
    current = path.join(current, part);
    try {
      if ((await lstat(current)).isSymbolicLink()) return true;
    } catch (error: unknown) {
      if ((error as NodeJS.ErrnoException).code === "ENOENT") return false;
      throw error;
    }
  }
  return false;
}

async function appendFingerprint(hash: ReturnType<typeof createHash>, targetPath: string, relative: string): Promise<void> {
  const value = await lstat(targetPath);
  const metadata = `${value.mode}\0${value.size}\0${value.mtimeMs}\0${value.ctimeMs}\0`;
  if (value.isSymbolicLink()) {
    hash.update(`link\0${relative}\0${metadata}${await readlink(targetPath)}\0`);
    return;
  }
  if (value.isFile()) {
    hash.update(`file\0${relative}\0${metadata}`);
    hash.update(await readFile(targetPath));
    hash.update("\0");
    return;
  }
  if (value.isDirectory()) {
    hash.update(`dir\0${relative}\0${metadata}`);
    const entries = (await readdir(targetPath)).sort();
    for (const entry of entries) await appendFingerprint(hash, path.join(targetPath, entry), path.join(relative, entry));
    return;
  }
  hash.update(`other\0${relative}\0${metadata}`);
}

function extractVersion(output: string): string {
  return /\b\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?\b/u.exec(output)?.[0] ?? output;
}
