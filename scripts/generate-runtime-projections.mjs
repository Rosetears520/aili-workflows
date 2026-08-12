#!/usr/bin/env node
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { mkdir, readdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import process from "node:process";

const GENERATOR_ID = "aili-runtime-projections/v1";
const root = parseRoot(process.argv.slice(2));
const checkOnly = process.argv.includes("--check");

try {
  const expected = await buildExpected(root);
  const drift = await findDrift(root, expected);
  if (checkOnly) {
    if (drift.length > 0) throw new Error(formatDrift(drift));
    console.log("Generated runtime projections are current.");
  } else {
    const extra = drift.filter((entry) => entry.kind === "unexpected-generated" || entry.kind === "unexpected-compatibility");
    if (extra.length > 0) throw new Error(formatDrift(extra));
    await writeOutputs(root, expected.generated);
    await writeOutputs(root, expected.compatibility);
    console.log(`Generated ${expected.generated.size} runtime assets and ${expected.compatibility.size} compatibility projections.`);
  }
} catch (error) {
  console.error(error instanceof Error ? error.message : String(error));
  process.exitCode = 1;
}

function parseRoot(argv) {
  let value = process.cwd();
  for (let index = 0; index < argv.length; index += 1) {
    const argument = argv[index];
    if (argument === "--check") continue;
    if (argument === "--root") {
      const candidate = argv[++index];
      if (!candidate) throw new Error("--root requires a path.");
      value = candidate;
      continue;
    }
    throw new Error(`Unknown generator option: ${argument}`);
  }
  return path.resolve(value);
}

async function buildExpected(projectRoot) {
  const projection = await readJson(projectRoot, "manifests/runtime-projections.json");
  if (projection.schemaVersion !== 1 || projection.generator?.id !== GENERATOR_ID) {
    throw new Error("Unsupported runtime projection manifest.");
  }
  const governanceInputs = ["core/governance/decision-core.md", "core/governance/operating-discipline.md"];
  const globalGovernanceInputs = ["core/governance/hero-scope-limits.md"];
  const [rolesDocument, openCodeAdapter, piAdapter, governanceParts, globalGovernanceParts] = await Promise.all([
    readJson(projectRoot, "core/roles/roles.json"),
    readJson(projectRoot, "adapters/opencode/adapter.json"),
    readJson(projectRoot, "adapters/pi/adapter.json"),
    Promise.all(governanceInputs.map((relativePath) => readText(projectRoot, relativePath))),
    Promise.all(globalGovernanceInputs.map((relativePath) => readText(projectRoot, relativePath)))
  ]);
  const governance = governanceParts.join("\n\n");
  const globalGovernanceContent = globalGovernanceParts.join("\n\n");
  validateProjectionInputs(projection, rolesDocument, openCodeAdapter, piAdapter, projectRoot);

  const commands = new Map();
  for (const name of projection.commands) commands.set(name, await readText(projectRoot, `core/commands/${name}.md`));
  const protocols = new Map();
  for (const name of projection.protocols) protocols.set(name, await readJson(projectRoot, `core/protocols/${name}`));

  const commonInputs = [
    "manifests/runtime-projections.json",
    ...governanceInputs,
    "core/roles/roles.json",
    "adapters/opencode/adapter.json",
    "adapters/pi/adapter.json"
  ];
  const generated = new Map();
  const compatibility = new Map();
  const opencodeOutputRecords = [];
  const piOutputRecords = [];

  for (const name of projection.commands) {
    const commandInputs = [...commonInputs, `core/commands/${name}.md`];
    const openCode = renderOpenCodeCommand(name, commands.get(name), openCodeAdapter, commandInputs, projectRoot);
    const pi = renderPiPrompt(name, commands.get(name), piAdapter, commandInputs, projectRoot);
    addOutput(generated, `generated/opencode/commands/${name}.md`, openCode, commandInputs, opencodeOutputRecords, projectRoot);
    addOutput(compatibility, `commands/${name}.md`, openCode, commandInputs, opencodeOutputRecords, projectRoot);
    addOutput(generated, `generated/pi/prompts/${name}.md`, pi, commandInputs, piOutputRecords, projectRoot);
  }

  for (const role of rolesDocument.roles) {
    const roleInputs = [...commonInputs];
    const openCode = renderOpenCodeAgent(role, rolesDocument.sharedWorkerBoundary, openCodeAdapter, roleInputs, projectRoot);
    addOutput(generated, `generated/opencode/agents/${role.id}.md`, openCode, roleInputs, opencodeOutputRecords, projectRoot);
    addOutput(compatibility, `agents/${role.id}.md`, openCode, roleInputs, opencodeOutputRecords, projectRoot);
  }

  const globalGovernance = `${governance.trimEnd()}\n\n${globalGovernanceContent.trimEnd()}`;
  const openCodeGlobalInputs = ["manifests/runtime-projections.json", ...governanceInputs, ...globalGovernanceInputs, "adapters/opencode/adapter.json"];
  const globalProjection = renderOpenCodeGlobal(globalGovernance, openCodeAdapter, openCodeGlobalInputs, projectRoot);
  addOutput(generated, "generated/opencode/AGENTS.md", globalProjection, openCodeGlobalInputs, opencodeOutputRecords, projectRoot);
  addOutput(compatibility, openCodeAdapter.globalProjection.compatibilityPath, globalProjection, openCodeGlobalInputs, opencodeOutputRecords, projectRoot);

  const piGlobalInputs = ["manifests/runtime-projections.json", ...governanceInputs, ...globalGovernanceInputs, "adapters/pi/adapter.json"];
  addOutput(generated, "generated/pi/AGENTS.md", renderPiGlobal(globalGovernance, piGlobalInputs, projectRoot), piGlobalInputs, piOutputRecords, projectRoot);

  const piSystemInputs = ["manifests/runtime-projections.json", ...governanceInputs, "core/roles/roles.json", "adapters/pi/adapter.json"];
  addOutput(generated, "generated/pi/system.md", renderPiSystem(governance, rolesDocument.roles, piSystemInputs, projectRoot), piSystemInputs, piOutputRecords, projectRoot);
  addOutput(generated, "generated/pi/role-metadata.json", renderJson({
    schemaVersion: 1,
    protocol: "aili-pi-role-metadata/v1",
    roles: rolesDocument.roles.map(({ id, title, mode, description, goal, output }) => ({ id, title, mode, description, goal, output })),
    authorityBoundary: "Adapter metadata may narrow loadability but cannot grant Worker decision, integration, verification-selection, or final-verdict authority."
  }, piSystemInputs, projectRoot), piSystemInputs, piOutputRecords, projectRoot);
  addOutput(generated, "generated/pi/selection-map.json", renderJson({
    schemaVersion: 1,
    protocol: "aili-agent-selection/v1",
    roles: rolesDocument.roles.map(({ id, mode }) => ({ id, mode })),
    decisionOwner: "ROSE",
    persistentContinuation: "Only unchanged same-package work may continue; runtime IDs are private mappings and not completion evidence."
  }, piSystemInputs, projectRoot), piSystemInputs, piOutputRecords, projectRoot);

  const installationInputs = ["manifests/runtime-projections.json", "adapters/pi/adapter.json"];
  addOutput(generated, "generated/pi/installation-contract.json", renderJson({
    schemaVersion: 1,
    adapter: "pi",
    installation: piAdapter.installation,
    contract: "generated/pi/AGENTS.md is installed as Pi global context and generated/pi/prompts/*.md as non-recursive Pi prompts. All runtime/session metadata is package-only."
  }, installationInputs, projectRoot), installationInputs, piOutputRecords, projectRoot);

  for (const [name, schema] of protocols) {
    const protocolInputs = ["manifests/runtime-projections.json", `core/protocols/${name}`, "adapters/pi/adapter.json"];
    addOutput(generated, `generated/pi/protocols/${name}`, renderProtocolProjection(schema, protocolInputs, projectRoot), protocolInputs, piOutputRecords, projectRoot);
  }

  const allInputs = [
    ...await listFiles(projectRoot, "core"),
    ...await listFiles(projectRoot, "adapters"),
    "manifests/runtime-projections.json"
  ].sort();
  generated.set("generated/opencode/provenance.json", renderProvenance("opencode", opencodeOutputRecords, allInputs, projectRoot));
  generated.set("generated/pi/provenance.json", renderProvenance("pi", piOutputRecords, allInputs, projectRoot));
  return { generated, compatibility };
}

function validateProjectionInputs(projection, rolesDocument, openCodeAdapter, piAdapter, projectRoot) {
  const expectedCommands = ["ideate", "define", "build", "ship", "local-review", "handoff", "agents-md", "harness-audit", "retro", "security-review"];
  assertExactList("command projection inventory", projection.commands, expectedCommands);
  assertExactList("agent projection inventory", projection.agents, rolesDocument.roles.map((role) => role.id).sort());
  assertExactList("canonical role registry", rolesDocument.roles.map((role) => role.id).sort(), projection.agents);
  assertExactList("protocol projection inventory", projection.protocols, ["package-envelope.schema.json", "aili-agent-selection.v1.schema.json", "aili-task-board.v1.schema.json"]);
  assertExactList("OpenCode adapter authority boundary", openCodeAdapter.authorityBoundary?.mayNotRedefine, ["role authority", "package identity", "evidence semantics", "approval gates", "lifecycle gates", "ROSE decision ownership", "final verdict ownership"]);
  assertExactList("Pi adapter authority boundary", piAdapter.authorityBoundary?.mayNotRedefine, ["role authority", "package identity", "evidence semantics", "approval gates", "lifecycle gates", "ROSE decision ownership", "final verdict ownership"]);
  if (piAdapter.installation?.globalContext?.source !== "generated/pi/AGENTS.md" || piAdapter.installation?.globalContext?.destination !== "~/.pi/agent/AGENTS.md") {
    throw new Error("Pi adapter installation contract must map the generated global context to Pi's official AGENTS.md path.");
  }
  if (piAdapter.installation?.allowedSourceGlob !== "generated/pi/prompts/*.md" || piAdapter.installation?.destinationGlob !== "~/.pi/agent/prompts/*.md" || piAdapter.installation?.discovery !== "non-recursive") {
    throw new Error("Pi adapter installation contract must permit non-recursive generated prompt files.");
  }
  const requiredPiPackageOnly = ["generated/pi/system.md", "generated/pi/role-metadata.json", "generated/pi/selection-map.json", "generated/pi/installation-contract.json", "generated/pi/protocols/*.json"];
  if (!Array.isArray(piAdapter.installation?.packageOnly) || requiredPiPackageOnly.some((path) => !piAdapter.installation.packageOnly.includes(path))) {
    throw new Error("Pi adapter installation contract must keep runtime metadata package-only.");
  }
  if (!Array.isArray(openCodeAdapter.globalProjection?.preamble) || openCodeAdapter.globalProjection.preamble.length < 3 || openCodeAdapter.globalProjection.compatibilityPath !== "templates/opencode-global-AGENTS.md") {
    throw new Error("OpenCode adapter must declare the generated global compatibility projection.");
  }
  if (!Array.isArray(rolesDocument.sharedWorkerBoundary) || rolesDocument.sharedWorkerBoundary.length === 0) {
    throw new Error("Canonical roles must declare the shared Worker boundary.");
  }
  for (const role of rolesDocument.roles) {
    if (!Array.isArray(role.successCriteria) || !Array.isArray(role.constraints) || typeof role.stop !== "string") {
      throw new Error(`Canonical role is missing detailed guidance: ${role.id}`);
    }
  }
  for (const name of projection.commands) ensureFile(projectRoot, `core/commands/${name}.md`);
  for (const profileName of Object.values(openCodeAdapter.roles ?? {})) {
    if (!openCodeAdapter.roleProfiles?.[profileName]) throw new Error(`OpenCode role profile is missing: ${profileName}`);
  }
}

function renderOpenCodeCommand(name, body, adapter, inputs, projectRoot) {
  const description = `AILI ${name} command generated from the backend-neutral canonical body.`;
  return `---\ndescription: ${yamlScalar(description)}\nagent: ${adapter.command.agent}\nsubtask: ${adapter.command.subtask}\n---\n\n${provenanceComment(inputs, projectRoot)}\n\n${body.trimEnd()}\n`;
}

function renderPiPrompt(name, body, adapter, inputs, projectRoot) {
  const description = `${adapter.prompt.descriptionPrefix} /${name}`;
  return `---\ndescription: ${yamlScalar(description)}\nargument-hint: ${yamlScalar(adapter.prompt.argumentHint)}\n---\n\n${provenanceComment(inputs, projectRoot)}\n\n${body.trimEnd()}\n`;
}

function renderOpenCodeAgent(role, sharedWorkerBoundary, adapter, inputs, projectRoot) {
  const profileName = adapter.roles[role.id];
  const profile = adapter.roleProfiles[profileName];
  if (!profile) throw new Error(`No OpenCode profile for canonical role: ${role.id}`);
  const frontmatter = { description: role.description, ...profile, ...(adapter.frontmatterOverrides?.[role.id] ?? {}) };
  const sharedBoundary = role.mode === "decision-core" ? [] : sharedWorkerBoundary;
  return `---\n${yamlObject(frontmatter)}---\n\n${provenanceComment(inputs, projectRoot)}\n\n# ${role.title}\n\n## Role\n\n${role.description}\n\n## Goal\n\n${role.goal}\n\n## Success criteria\n\n${markdownList(role.successCriteria)}\n\n## Constraints\n\n${markdownList([...(role.constraints ?? []), ...sharedBoundary])}\n\n## Tools\n\nUse only the capabilities exposed by the active runtime and only when needed for the assigned result. A task packet may narrow but never broaden them.\n\n## Output\n\n${role.output}\n\n## Stop\n\n${role.stop}\n`;
}

function renderOpenCodeGlobal(governance, adapter, inputs, projectRoot) {
  return `${adapter.globalProjection.preamble.join("\n")}\n${provenanceComment(inputs, projectRoot)}\n\n${governance.trimEnd()}\n`;
}

function renderPiGlobal(governance, inputs, projectRoot) {
  return `<!-- AILI_PI_GLOBAL_CONTEXT: ~/.pi/agent/AGENTS.md -->\n${provenanceComment(inputs, projectRoot)}\n\n${governance.trimEnd()}\n`;
}

function renderPiSystem(governance, roles, inputs, projectRoot) {
  const roleList = roles.map((role) => `- \`${role.id}\` — ${role.description}`).join("\n");
  return `${provenanceComment(inputs, projectRoot)}\n\n# AILI Pi System Projection\n\nThis package artifact is for the separately owned Pi runtime. It does not install or run Pi sessions, scheduler, daemon, park/revive, or retry behavior.\n\n${governance.trimEnd()}\n\n## Canonical roles\n\n${roleList}\n`;
}

function renderProtocolProjection(schema, inputs, projectRoot) {
  return renderJson({
    ...schema,
    "$comment": `Generated by ${GENERATOR_ID}; canonical inputs: ${inputs.slice().sort().join(", ")}; input_sha256: ${inputHash(inputs, projectRoot)}`
  }, inputs, projectRoot, false);
}

function renderJson(value, inputs, projectRoot, includeProvenance = true) {
  const result = includeProvenance
    ? {
        ...value,
        generated: {
          generator: GENERATOR_ID,
          canonicalInputs: inputs.slice().sort(),
          inputSha256: inputHash(inputs, projectRoot)
        }
      }
    : value;
  return `${JSON.stringify(result, null, 2)}\n`;
}

function renderProvenance(adapter, records, inputs, projectRoot) {
  return `${JSON.stringify({
    schemaVersion: 1,
    generator: GENERATOR_ID,
    adapter,
    canonicalInputs: inputs.slice().sort(),
    inputSha256: inputHash(inputs, projectRoot),
    outputs: records.sort((left, right) => left.path.localeCompare(right.path))
  }, null, 2)}\n`;
}

function addOutput(target, relativePath, content, inputs, records, projectRoot) {
  target.set(relativePath, content);
  records.push({
    path: relativePath,
    canonicalInputs: inputs.slice().sort(),
    inputSha256: inputHash(inputs, projectRoot),
    outputSha256: sha256(content)
  });
}

function provenanceComment(inputs, projectRoot) {
  return `<!-- GENERATED: ${GENERATOR_ID}; canonical_inputs: ${inputs.slice().sort().join(", ")}; input_sha256: ${inputHash(inputs, projectRoot)}; do not edit directly -->`;
}

function yamlObject(value, indent = "") {
  return Object.entries(value).map(([key, entry]) => {
    const renderedKey = yamlKey(key);
    if (entry && typeof entry === "object" && !Array.isArray(entry)) return `${indent}${renderedKey}:\n${yamlObject(entry, `${indent}  `)}`;
    return `${indent}${renderedKey}: ${yamlScalar(entry)}`;
  }).join("\n") + "\n";
}

function yamlKey(value) {
  return /^[A-Za-z_][A-Za-z0-9_-]*$/u.test(value) ? value : JSON.stringify(value);
}

function yamlScalar(value) {
  if (typeof value === "boolean" || typeof value === "number") return String(value);
  const text = String(value);
  return /^[A-Za-z][A-Za-z0-9_-]*$/u.test(text) ? text : JSON.stringify(text);
}

function markdownList(items) {
  return items.map((item) => `- ${item}`).join("\n");
}

async function findDrift(projectRoot, expected) {
  const result = [];
  for (const [relativePath, content] of [...expected.generated, ...expected.compatibility]) {
    try {
      const actual = await readFile(path.join(projectRoot, relativePath), "utf8");
      if (actual !== content) result.push({ kind: "stale", path: relativePath });
    } catch (error) {
      if (error?.code === "ENOENT") result.push({ kind: "missing", path: relativePath });
      else throw error;
    }
  }
  for (const relativePath of await listFiles(projectRoot, "generated")) {
    if (!expected.generated.has(relativePath)) result.push({ kind: "unexpected-generated", path: relativePath });
  }
  for (const compatibilityRoot of ["agents", "commands"]) {
    for (const relativePath of await listFiles(projectRoot, compatibilityRoot)) {
      if (!expected.compatibility.has(relativePath)) result.push({ kind: "unexpected-compatibility", path: relativePath });
    }
  }
  return result.sort((left, right) => `${left.kind}:${left.path}`.localeCompare(`${right.kind}:${right.path}`));
}

async function writeOutputs(projectRoot, outputs) {
  for (const [relativePath, content] of outputs) {
    const destination = path.join(projectRoot, relativePath);
    await mkdir(path.dirname(destination), { recursive: true });
    await writeFile(destination, content, "utf8");
  }
}

async function listFiles(projectRoot, relativeRoot) {
  const absoluteRoot = path.join(projectRoot, relativeRoot);
  let entries;
  try {
    entries = await readdir(absoluteRoot, { withFileTypes: true });
  } catch (error) {
    if (error?.code === "ENOENT") return [];
    throw error;
  }
  const files = [];
  for (const entry of entries.sort((left, right) => left.name.localeCompare(right.name))) {
    const child = path.posix.join(relativeRoot, entry.name);
    if (entry.isDirectory()) files.push(...await listFiles(projectRoot, child));
    else if (entry.isFile()) files.push(child);
  }
  return files;
}

async function readJson(projectRoot, relativePath) {
  return JSON.parse(await readText(projectRoot, relativePath));
}

async function readText(projectRoot, relativePath) {
  return readFile(path.join(projectRoot, relativePath), "utf8");
}

function ensureFile(projectRoot, relativePath) {
  if (!relativePath || path.isAbsolute(relativePath) || relativePath.split(/[\\/]/u).includes("..")) {
    throw new Error(`Unsafe canonical projection path: ${relativePath}`);
  }
}

function inputHash(inputs, projectRoot) {
  const source = inputs.slice().sort().map((relativePath) => {
    const absolute = path.join(projectRoot, relativePath);
    return `${relativePath}\u0000${createHash("sha256").update(readFileSync(absolute)).digest("hex")}`;
  }).join("\n");
  return sha256(source);
}

function sha256(value) {
  return createHash("sha256").update(value).digest("hex");
}

function assertExactList(label, actual, expected) {
  if (!Array.isArray(actual)) throw new Error(`${label} must be an array.`);
  if (actual.length !== expected.length || actual.some((value, index) => value !== expected[index])) {
    throw new Error(`${label} must be exactly: ${expected.join(", ")}`);
  }
}

function formatDrift(drift) {
  return `Generated runtime projection drift:\n${drift.map((entry) => `- ${entry.kind}: ${entry.path}`).join("\n")}`;
}
