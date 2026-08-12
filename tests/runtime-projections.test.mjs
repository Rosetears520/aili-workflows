import assert from "node:assert/strict";
import { mkdtemp, cp, mkdir, readFile, readdir, rm, unlink, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import test from "node:test";
import { fileURLToPath } from "node:url";

const repositoryRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const generator = path.join(repositoryRoot, "scripts", "generate-runtime-projections.mjs");
const heroScopeLimits = `=== SCOPE LIMITS (these bound what you PROPOSE, never what you look for) ===
Report anything that is actually wrong here — including a rare-looking case, if
this project actually produces it. Then keep the fix in scope:
1. This is not a security paper. Verification is welcome; over-defense is not.
   Unless this project states otherwise, assume a cooperating operator on their
   own machine; if it has a real adversary, it will say so and that scope wins.
2. Do not add hashes, checksums or fingerprints unless the hash replaces a
   materially more expensive operation AND its result changes what happens next.
3. No defensive scaffolding: no feature flags, migration frameworks, compat
   layers or wrappers for cases that do not occur here.
4. No corner-case obsession: exotic encodings, symlink races, RTL text and
   millisecond races are out of scope unless the case is reachable through this
   project's supported use — its documented inputs, its published interface, its
   real data. Reachable is enough; you do not need a reproduction. Constructible
   in principle is not enough.
5. Where judgement is needed, judge. Do not replace it with a scoring table, a
   checklist, or a re-verification loop over something already settled.
Shapes already seen, for calibration. Examples, not a checklist — a real finding
is not dismissed by resembling one:
  H  hashing every row of two spreadsheets to answer what comparing cells answers
  H  writing checksum files that nothing ever reads
  E  hardening the accounts of an app that has no users and no deployment
  R  auditing your own patch all night while the feature stays unwritten
  R  a reviewer that returns a failing verdict on everything
  O  guards whose justification is the previous guard, not the requirement
Before running any check, answer: what specific failure would this detect, and
what would I do differently if it occurred? No answer means do not run it.
Say plainly when something is correct. Do not manufacture findings.`;

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
  const piInstallationContract = JSON.parse(await readFile(path.join(workspace, "generated/pi/installation-contract.json"), "utf8"));
  assert.deepEqual(piInstallationContract.installation.globalContext, {
    source: "generated/pi/AGENTS.md",
    destination: "~/.pi/agent/AGENTS.md"
  });
  assert.equal(piInstallationContract.installation.discovery, "non-recursive");
  assert.match(piInstallationContract.contract, /global context.*non-recursive Pi prompts/);
  assert.equal(await hasNestedPrompt(workspace), false);

  for (const relativePath of ["generated/opencode/AGENTS.md", "templates/opencode-global-AGENTS.md", "generated/pi/AGENTS.md"]) {
    const output = await readFile(path.join(workspace, relativePath), "utf8");
    assert.equal(output.split(heroScopeLimits).length - 1, 1, `${relativePath} must contain the exact HERO block once`);
  }
  const piGlobal = await readFile(path.join(workspace, "generated/pi/AGENTS.md"), "utf8");
  assert.match(piGlobal, /AILI_PI_GLOBAL_CONTEXT: ~\/\.pi\/agent\/AGENTS\.md/);
  assert.doesNotMatch(piGlobal, /AILI Pi System Projection|Canonical roles|AgentSession/);
  const piProvenance = JSON.parse(await readFile(path.join(workspace, "generated/pi/provenance.json"), "utf8"));
  assert.ok(piProvenance.outputs.some((output) => output.path === "generated/pi/AGENTS.md"));
  assert.ok(piProvenance.canonicalInputs.includes("core/governance/hero-scope-limits.md"));
  for (const relativePath of [
    "generated/opencode/agents/implementer.md",
    "generated/opencode/commands/build.md",
    "generated/pi/system.md",
    "generated/pi/prompts/build.md"
  ]) {
    assert.doesNotMatch(await readFile(path.join(workspace, relativePath), "utf8"), /SCOPE LIMITS|hero-scope-limits/);
  }

  assert.equal(runGenerator(workspace).status, 0);
  assert.deepEqual(await snapshot(workspace, ["generated", "agents", "commands", "templates/opencode-global-AGENTS.md"]), firstSnapshot);

  const piAdapterPath = path.join(workspace, "adapters/pi/adapter.json");
  const validPiAdapter = await readFile(piAdapterPath, "utf8");
  const invalidPiAdapter = JSON.parse(validPiAdapter);
  invalidPiAdapter.installation.globalContext.destination = "~/.pi/agent/not-AGENTS.md";
  await writeFile(piAdapterPath, `${JSON.stringify(invalidPiAdapter, null, 2)}\n`, "utf8");
  assert.match(runGenerator(workspace, "--check").stderr, /official AGENTS\.md path/);
  await writeFile(piAdapterPath, validPiAdapter, "utf8");
  assert.equal(runGenerator(workspace, "--check").status, 0);

  const compatibilityBuild = path.join(workspace, "commands/build.md");
  await writeFile(compatibilityBuild, "tampered projection\n", "utf8");
  assert.match(runGenerator(workspace, "--check").stderr, /stale: commands\/build\.md/);
  assert.equal(runGenerator(workspace).status, 0);
  assert.doesNotMatch(await readFile(compatibilityBuild, "utf8"), /tampered projection/);

  await unlink(path.join(workspace, "commands/ideate.md"));
  assert.match(runGenerator(workspace, "--check").stderr, /missing: commands\/ideate\.md/);
  assert.equal(runGenerator(workspace).status, 0);

  await unlink(path.join(workspace, "generated/pi/AGENTS.md"));
  assert.match(runGenerator(workspace, "--check").stderr, /missing: generated\/pi\/AGENTS\.md/);
  assert.equal(runGenerator(workspace).status, 0);

  await writeFile(path.join(workspace, "generated/pi/AGENTS.md"), "tampered projection\n", "utf8");
  assert.match(runGenerator(workspace, "--check").stderr, /stale: generated\/pi\/AGENTS\.md/);
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
