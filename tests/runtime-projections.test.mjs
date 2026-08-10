import assert from "node:assert/strict";
import { mkdtemp, cp, mkdir, readFile, readdir, rm, unlink, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import test from "node:test";
import { fileURLToPath } from "node:url";

const repositoryRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const generator = path.join(repositoryRoot, "scripts", "generate-runtime-projections.mjs");

test("runtime projections are provenanced, byte-stable, and reject generated or compatibility drift", async (t) => {
  const workspace = await mkdtemp(path.join(os.tmpdir(), "aili-runtime-projections-"));
  t.after(() => rm(workspace, { recursive: true, force: true }));
  await Promise.all([
    cp(path.join(repositoryRoot, "core"), path.join(workspace, "core"), { recursive: true }),
    cp(path.join(repositoryRoot, "adapters"), path.join(workspace, "adapters"), { recursive: true }),
    cp(path.join(repositoryRoot, "manifests"), path.join(workspace, "manifests"), { recursive: true })
  ]);

  assert.equal(runGenerator(workspace).status, 0);
  const firstSnapshot = await snapshot(workspace, ["generated", "agents", "commands", "templates/opencode-global-AGENTS.md"]);
  const check = runGenerator(workspace, "--check");
  assert.equal(check.status, 0, check.stderr);
  assert.match(await readFile(path.join(workspace, "generated/opencode/provenance.json"), "utf8"), /core\/commands\/build\.md/);
  assert.match(await readFile(path.join(workspace, "generated/pi/system.md"), "utf8"), /does not install or run Pi sessions/);
  assert.match(await readFile(path.join(workspace, "generated/pi/installation-contract.json"), "utf8"), /generated\/pi\/prompts\/\*\.md/);
  assert.equal(await hasNestedPrompt(workspace), false);

  assert.equal(runGenerator(workspace).status, 0);
  assert.deepEqual(await snapshot(workspace, ["generated", "agents", "commands", "templates/opencode-global-AGENTS.md"]), firstSnapshot);

  const compatibilityBuild = path.join(workspace, "commands/build.md");
  await writeFile(compatibilityBuild, "tampered projection\n", "utf8");
  assert.match(runGenerator(workspace, "--check").stderr, /stale: commands\/build\.md/);
  assert.equal(runGenerator(workspace).status, 0);
  assert.doesNotMatch(await readFile(compatibilityBuild, "utf8"), /tampered projection/);

  await unlink(path.join(workspace, "commands/ideate.md"));
  assert.match(runGenerator(workspace, "--check").stderr, /missing: commands\/ideate\.md/);
  assert.equal(runGenerator(workspace).status, 0);

  await unlink(path.join(workspace, "generated/pi/prompts/build.md"));
  assert.match(runGenerator(workspace, "--check").stderr, /missing: generated\/pi\/prompts\/build\.md/);
  assert.equal(runGenerator(workspace).status, 0);

  await writeFile(path.join(workspace, "generated/pi/prompts/build.md"), "tampered projection\n", "utf8");
  assert.match(runGenerator(workspace, "--check").stderr, /stale: generated\/pi\/prompts\/build\.md/);
  assert.equal(runGenerator(workspace).status, 0);

  await writeFile(path.join(workspace, "generated/pi/prompts/extra.md"), "extra\n", "utf8");
  assert.match(runGenerator(workspace, "--check").stderr, /unexpected-generated: generated\/pi\/prompts\/extra\.md/);
  await unlink(path.join(workspace, "generated/pi/prompts/extra.md"));

  const nestedPromptDirectory = path.join(workspace, "generated/pi/prompts/nested");
  await mkdir(nestedPromptDirectory);
  await writeFile(path.join(nestedPromptDirectory, "extra.md"), "extra\n", "utf8");
  assert.match(runGenerator(workspace, "--check").stderr, /unexpected-generated: generated\/pi\/prompts\/nested\/extra\.md/);
  await rm(nestedPromptDirectory, { recursive: true, force: true });

  await writeFile(path.join(workspace, "agents/extra.md"), "extra\n", "utf8");
  assert.match(runGenerator(workspace, "--check").stderr, /unexpected-compatibility: agents\/extra\.md/);
});

function runGenerator(root, ...args) {
  return spawnSync(process.execPath, [generator, "--root", root, ...args], { encoding: "utf8" });
}

async function hasNestedPrompt(root) {
  const entries = await readdir(path.join(root, "generated/pi/prompts"), { withFileTypes: true });
  return entries.some((entry) => entry.isDirectory());
}

async function snapshot(root, paths) {
  const entries = [];
  for (const relative of paths) {
    const absolute = path.join(root, relative);
    const children = await collect(absolute, relative);
    entries.push(...children);
  }
  return Object.fromEntries(entries.sort(([left], [right]) => left.localeCompare(right)));
}

async function collect(absolute, relative) {
  const entries = await readdir(absolute, { withFileTypes: true }).catch((error) => error.code === "ENOTDIR" ? null : Promise.reject(error));
  if (entries === null) return [[relative, await readFile(absolute, "utf8")]];
  const result = [];
  for (const entry of entries.sort((left, right) => left.name.localeCompare(right.name))) {
    result.push(...await collect(path.join(absolute, entry.name), path.posix.join(relative, entry.name)));
  }
  return result;
}
