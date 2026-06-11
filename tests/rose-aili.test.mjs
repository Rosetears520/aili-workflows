import assert from "node:assert/strict";
import { execFile } from "node:child_process";
import { chmod, cp, lstat, mkdir, mkdtemp, readFile, rm, stat, symlink, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { applyPromptDecisions } from "../dist/cli.js";
import { mergeOpenCodeConfig } from "../dist/config.js";

const repoRoot = process.cwd();
const cliPath = path.join(repoRoot, "dist", "cli.js");
const openSpecNodeSkip = supportsOpenSpecSuccessNode(process.versions.node) ? false : "OpenSpec install success paths require Node.js 20.19.0+";

test("dry-run install reports operations without mutating OpenCode home", async () => {
  const fixture = await fixtureAiliHome();
  const opencodeHome = path.join(fixture.root, "opencode");

  const result = await runCli(["install", "--dry-run", "--aili-home", fixture.ailiHome, "--opencode-home", opencodeHome, "--yes", "--model", "anthropic/claude-sonnet-4-5", "--json"]);
  const summary = JSON.parse(result.stdout);

  assert.equal(summary.dryRun, true);
  assert.equal(summary.componentInstall.status, "planned");
  assert.equal(summary.config.changed, true);
  await assert.rejects(stat(opencodeHome));
  await fixture.cleanup();
});

test("config merge preserves existing default agent, model, unrelated keys, and JSONC comments", async () => {
  const root = await mkdtemp(path.join(os.tmpdir(), "rose-aili-config-"));
  const opencodeHome = path.join(root, "opencode");
  await mkdir(opencodeHome, { recursive: true });
  const configPath = path.join(opencodeHome, "opencode.jsonc");
  await writeFile(configPath, `{
  // keep theme comment
  "theme": "catppuccin",
  "default_agent": "build",
  "agent": {
    "rose": { "model": "existing/model" }
  },
  "mcp": { "other": { "enabled": true } }
}
`, "utf8");

  const result = await mergeOpenCodeConfig({
    opencodeHome,
    dryRun: false,
    setDefaultRose: true,
    model: "new/model",
    playwrightConfig: { type: "local", command: ["npx", "-y", "@playwright/mcp@0.0.75"], enabled: true }
  });
  const text = await readFile(configPath, "utf8");

  assert.equal(result.changed, true);
  assert.ok(result.backupPath);
  assert.match(text, /keep theme comment/);
  assert.match(text, /"theme": "catppuccin"/);
  assert.match(text, /"default_agent": "build"/);
  assert.match(text, /"model": "existing\/model"/);
  assert.match(text, /"other"/);
  assert.match(text, /"playwright"/);
  await rm(root, { recursive: true, force: true });
});

test("force flags overwrite default agent and rose model", async () => {
  const root = await mkdtemp(path.join(os.tmpdir(), "rose-aili-force-"));
  const opencodeHome = path.join(root, "opencode");
  await mkdir(opencodeHome, { recursive: true });
  const configPath = path.join(opencodeHome, "opencode.json");
  await writeFile(configPath, `{"default_agent":"build","agent":{"rose":{"model":"old/model"}},"permission":"ask"}\n`, "utf8");

  await mergeOpenCodeConfig({ opencodeHome, dryRun: false, setDefaultRose: true, forceDefaultAgent: true, model: "new/model", forceModel: true });
  const value = JSON.parse(await readFile(configPath, "utf8"));

  assert.equal(value.default_agent, "rose");
  assert.equal(value.agent.rose.model, "new/model");
  assert.equal(value.permission, "ask");
  await rm(root, { recursive: true, force: true });
});

test("set-default-rose does not create a model override", async () => {
  const fixture = await fixtureAiliHome();
  const opencodeHome = path.join(fixture.root, "opencode");

  await runCli(["install", "--aili-home", fixture.ailiHome, "--opencode-home", opencodeHome, "--set-default-rose", "--json"]);
  const config = JSON.parse(await readFile(path.join(opencodeHome, "opencode.json"), "utf8"));

  assert.equal(config.default_agent, "rose");
  assert.equal(config.agent, undefined);
  await fixture.cleanup();
});

test("invalid JSONC fails closed without overwrite", async () => {
  const root = await mkdtemp(path.join(os.tmpdir(), "rose-aili-invalid-"));
  const opencodeHome = path.join(root, "opencode");
  await mkdir(opencodeHome, { recursive: true });
  const configPath = path.join(opencodeHome, "opencode.jsonc");
  const invalid = `{ "default_agent": `;
  await writeFile(configPath, invalid, "utf8");

  await assert.rejects(mergeOpenCodeConfig({ opencodeHome, dryRun: false, setDefaultRose: true }), /invalid JSONC/);
  assert.equal(await readFile(configPath, "utf8"), invalid);
  await rm(root, { recursive: true, force: true });
});

test("install configures or skips Playwright MCP by explicit flag", async () => {
  const enabledFixture = await fixtureAiliHome();
  const enabledHome = path.join(enabledFixture.root, "opencode-enabled");
  await runCli(["install", "--aili-home", enabledFixture.ailiHome, "--opencode-home", enabledHome, "--yes", "--enable-playwright", "--json"]);
  const enabledConfig = JSON.parse(await readFile(path.join(enabledHome, "opencode.json"), "utf8"));
  assert.deepEqual(enabledConfig.mcp.playwright.command, ["npx", "-y", "@playwright/mcp@0.0.75", "--caps=testing,storage"]);

  const skippedFixture = await fixtureAiliHome();
  const skippedHome = path.join(skippedFixture.root, "opencode-skipped");
  await runCli(["install", "--aili-home", skippedFixture.ailiHome, "--opencode-home", skippedHome, "--yes", "--skip-playwright", "--json"]);
  const skippedConfig = JSON.parse(await readFile(path.join(skippedHome, "opencode.json"), "utf8"));
  assert.equal(skippedConfig.mcp, undefined);
  await enabledFixture.cleanup();
  await skippedFixture.cleanup();
});

test("interactive prompt decisions cover defaults, blank model, DCP, CodeGraph, and OpenSpec", async () => {
  const options = { dryRun: false, opencodeHome: "/tmp/opencode", ailiHome: repoRoot, plugins: [] };
  const answers = ["", "", "y", "y", "y", "n"];
  const prompts = [];

  await applyPromptDecisions(options, {}, async (prompt) => {
    prompts.push(prompt);
    return answers.shift() ?? "";
  });

  assert.deepEqual(prompts, [
    "Set rose as OpenCode default_agent? [Y/n] ",
    "Model for agent.rose.model (provider/model, blank to skip): ",
    "Enable optional Playwright MCP? [y/N] ",
    "Enable DCP plugin globally via `opencode plugin @tarquinen/opencode-dcp@latest --global`? [y/N] ",
    "Install optional CodeGraph for OpenCode via `npm install -g @colbymchenry/codegraph@latest` and `codegraph install --target=opencode --yes`? Requires restarting OpenCode. [y/N] ",
    "Install/configure OpenSpec for spec-driven changes via `npm install -g @fission-ai/openspec@latest` and project `openspec init/update`? Requires Node.js 20.19+. [y/N] "
  ]);
  assert.equal(options.setDefaultRose, true);
  assert.equal(options.model, undefined);
  assert.equal(options.enablePlaywright, true);
  assert.equal(options.skipPlaywright, false);
  assert.equal(options.enableDcp, true);
  assert.equal(options.skipDcp, false);
  assert.equal(options.enableCodegraph, true);
  assert.equal(options.skipCodegraph, false);
  assert.equal(options.enableOpenspec, false);
  assert.equal(options.skipOpenspec, true);
});

test("update prompt decisions ask CodeGraph without core config or OpenSpec prompts", async () => {
  const options = { dryRun: false, opencodeHome: "/tmp/opencode", ailiHome: repoRoot, plugins: [] };
  const answers = ["y"];
  const prompts = [];

  await applyPromptDecisions(options, {}, async (prompt) => {
    prompts.push(prompt);
    return answers.shift() ?? "";
  }, { includeCoreConfig: false, includePlaywright: false, includeDcp: false, includeCodegraph: true, includeOpenspec: false });

  assert.deepEqual(prompts, [
    "Install optional CodeGraph for OpenCode via `npm install -g @colbymchenry/codegraph@latest` and `codegraph install --target=opencode --yes`? Requires restarting OpenCode. [y/N] "
  ]);
  assert.equal(options.setDefaultRose, undefined);
  assert.equal(options.model, undefined);
  assert.equal(options.enablePlaywright, undefined);
  assert.equal(options.skipPlaywright, undefined);
  assert.equal(options.enableDcp, undefined);
  assert.equal(options.skipDcp, undefined);
  assert.equal(options.enableCodegraph, true);
  assert.equal(options.skipCodegraph, false);
  assert.equal(options.enableOpenspec, undefined);
  assert.equal(options.skipOpenspec, undefined);
});

test("non-interactive install reports skipped optional decisions with next steps", async () => {
  const fixture = await fixtureAiliHome();
  const opencodeHome = path.join(fixture.root, "opencode");
  const result = await runCli(["install", "--aili-home", fixture.ailiHome, "--opencode-home", opencodeHome, "--json"]);
  const summary = JSON.parse(result.stdout);

  assert.equal(summary.componentInstall.status, "completed");
  assert.equal(summary.dcp.status, "skipped");
  assert.equal(summary.codegraph.status, "skipped");
  assert.equal(summary.openspec.status, "skipped");
  assertDecision(summary, "default rose", "rose-aili install --set-default-rose");
  assertDecision(summary, "rose model override", "rose-aili install --model <provider/model>");
  assertDecision(summary, "Playwright MCP", "rose-aili install --enable-playwright");
  assertDecision(summary, "DCP plugin", "rose-aili install --enable-dcp");
  assertDecision(summary, "CodeGraph", "rose-aili install --enable-codegraph");
  assertDecision(summary, "OpenSpec", "rose-aili install --enable-openspec");
  await fixture.cleanup();
});

test("install copies global AGENTS rules into OpenCode home", async () => {
  const fixture = await fixtureAiliHome();
  const opencodeHome = path.join(fixture.root, "opencode");

  await runCli(["install", "--aili-home", fixture.ailiHome, "--opencode-home", opencodeHome, "--json"]);
  const target = path.join(opencodeHome, "AGENTS.md");
  const text = await readFile(target, "utf8");

  assert.equal((await lstat(target)).isSymbolicLink(), false);
  assert.match(text, /AILI_GLOBAL_AGENTS_TEMPLATE_SOURCE: templates\/opencode-global-AGENTS\.md/);
  assert.match(text, /Project facts, repository commands, local test locations/);
  assert.match(text, /Do not symlink this global file into project roots/);
  assert.match(text, /codegraph init -i/);
  assert.match(text, /Do not batch-initialize other repositories or run `openspec init`/);
  await fixture.cleanup();
});

test("DCP is not installed without flag and --yes does not silently install it", async () => {
  const fixture = await fixtureAiliHome();
  const binDir = path.join(fixture.root, "bin");
  const logPath = path.join(fixture.root, "commands.log");
  await writeStub(binDir, "opencode", logPath);
  const opencodeHome = path.join(fixture.root, "opencode");

  const result = await runCli(["install", "--aili-home", fixture.ailiHome, "--opencode-home", opencodeHome, "--yes", "--json"], {
    env: { ...process.env, PATH: `${binDir}${path.delimiter}${process.env.PATH}` }
  });
  const summary = JSON.parse(result.stdout);

  assert.equal(summary.dcp.status, "skipped");
  await assert.rejects(readFile(logPath, "utf8"));
  await fixture.cleanup();
});

test("--enable-dcp delegates exact opencode argv", async () => {
  const fixture = await fixtureAiliHome();
  const binDir = path.join(fixture.root, "bin");
  const logPath = path.join(fixture.root, "commands.log");
  await writeStub(binDir, "opencode", logPath);
  const opencodeHome = path.join(fixture.root, "opencode");

  const result = await runCli(["install", "--aili-home", fixture.ailiHome, "--opencode-home", opencodeHome, "--enable-dcp", "--json"], {
    env: { ...process.env, PATH: `${binDir}${path.delimiter}${process.env.PATH}` }
  });
  const summary = JSON.parse(result.stdout);
  const logged = JSON.parse(await readFile(logPath, "utf8"));

  assert.equal(summary.dcp.status, "configured");
  assert.deepEqual(logged, [{ name: "opencode", args: ["plugin", "@tarquinen/opencode-dcp@latest", "--global"] }]);
  await fixture.cleanup();
});

test("DCP failure is reported separately while core install succeeds", async () => {
  const fixture = await fixtureAiliHome();
  const binDir = path.join(fixture.root, "bin");
  const logPath = path.join(fixture.root, "commands.log");
  await writeStub(binDir, "opencode", logPath, { exitCode: 7, stderr: "dcp failed" });
  const opencodeHome = path.join(fixture.root, "opencode");

  const result = await runCli(["install", "--aili-home", fixture.ailiHome, "--opencode-home", opencodeHome, "--enable-dcp", "--json"], {
    env: { ...process.env, PATH: `${binDir}${path.delimiter}${process.env.PATH}` }
  });
  const summary = JSON.parse(result.stdout);

  assert.equal(result.code, 0);
  assert.equal(summary.componentInstall.status, "completed");
  assert.equal(summary.dcp.status, "failed");
  assert.match(summary.dcp.reason, /dcp failed/);
  assert.match(summary.dcp.recovery, /opencode plugin @tarquinen\/opencode-dcp@latest --global/);
  await fixture.cleanup();
});

test("CodeGraph is not installed without flag and --yes does not silently install it", async () => {
  const fixture = await fixtureAiliHome();
  const binDir = path.join(fixture.root, "bin");
  const logPath = path.join(fixture.root, "commands.log");
  await writeStub(binDir, "npm", logPath);
  await writeStub(binDir, "codegraph", logPath);
  const opencodeHome = path.join(fixture.root, "opencode");

  const result = await runCli(["install", "--aili-home", fixture.ailiHome, "--opencode-home", opencodeHome, "--yes", "--json"], {
    env: { ...process.env, PATH: `${binDir}${path.delimiter}${process.env.PATH}` }
  });
  const summary = JSON.parse(result.stdout);

  assert.equal(summary.codegraph.status, "skipped");
  await assert.rejects(readFile(logPath, "utf8"));
  await fixture.cleanup();
});

test("--enable-codegraph delegates exact npm and codegraph argv", async () => {
  const fixture = await fixtureAiliHome();
  const binDir = path.join(fixture.root, "bin");
  const logPath = path.join(fixture.root, "commands.log");
  await writeStub(binDir, "npm", logPath);
  await writeStub(binDir, "codegraph", logPath);
  const opencodeHome = path.join(fixture.root, "opencode");

  const result = await runCli(["install", "--aili-home", fixture.ailiHome, "--opencode-home", opencodeHome, "--enable-codegraph", "--json"], {
    env: { ...process.env, PATH: `${binDir}${path.delimiter}${process.env.PATH}` }
  });
  const summary = JSON.parse(result.stdout);
  const logged = JSON.parse(await readFile(logPath, "utf8"));

  assert.equal(summary.codegraph.status, "configured");
  assert.match(summary.codegraph.nextStep, /Restart OpenCode/);
  assert.deepEqual(logged, [
    { name: "npm", args: ["install", "-g", "@colbymchenry/codegraph@latest"] },
    { name: "codegraph", args: ["install", "--target=opencode", "--yes"] }
  ]);
  await fixture.cleanup();
});

test("--enable-codegraph dry-run reports planned setup without spawning optional commands", async () => {
  const fixture = await fixtureAiliHome();
  const binDir = path.join(fixture.root, "bin");
  const logPath = path.join(fixture.root, "commands.log");
  await writeStub(binDir, "npm", logPath);
  await writeStub(binDir, "codegraph", logPath);
  const opencodeHome = path.join(fixture.root, "opencode");

  const result = await runCli(["install", "--dry-run", "--aili-home", fixture.ailiHome, "--opencode-home", opencodeHome, "--enable-codegraph", "--json"], {
    env: { ...process.env, PATH: `${binDir}${path.delimiter}${process.env.PATH}` }
  });
  const summary = JSON.parse(result.stdout);

  assert.equal(summary.codegraph.status, "planned");
  assert.match(summary.codegraph.command, /npm install -g @colbymchenry\/codegraph@latest/);
  assert.match(summary.codegraph.command, /codegraph install --target=opencode --yes/);
  assert.match(summary.codegraph.nextStep, /Restart OpenCode/);
  await assert.rejects(readFile(logPath, "utf8"));
  await fixture.cleanup();
});

test("CodeGraph npm install failure is reported before OpenCode setup", async () => {
  const fixture = await fixtureAiliHome();
  const binDir = path.join(fixture.root, "bin");
  const logPath = path.join(fixture.root, "commands.log");
  await writeStub(binDir, "npm", logPath, { exitCode: 9, stderr: "npm failed" });
  await writeStub(binDir, "codegraph", logPath);
  const opencodeHome = path.join(fixture.root, "opencode");

  const result = await runCli(["install", "--aili-home", fixture.ailiHome, "--opencode-home", opencodeHome, "--enable-codegraph", "--json"], {
    env: { ...process.env, PATH: `${binDir}${path.delimiter}${process.env.PATH}` }
  });
  const summary = JSON.parse(result.stdout);
  const logged = JSON.parse(await readFile(logPath, "utf8"));

  assert.equal(result.code, 0);
  assert.equal(summary.componentInstall.status, "completed");
  assert.equal(summary.codegraph.status, "failed");
  assert.match(summary.codegraph.reason, /npm failed/);
  assert.match(summary.codegraph.recovery, /npm install -g @colbymchenry\/codegraph@latest/);
  assert.deepEqual(logged, [{ name: "npm", args: ["install", "-g", "@colbymchenry/codegraph@latest"] }]);
  await fixture.cleanup();
});

test("CodeGraph failure is reported separately while core install succeeds", async () => {
  const fixture = await fixtureAiliHome();
  const binDir = path.join(fixture.root, "bin");
  const logPath = path.join(fixture.root, "commands.log");
  await writeStub(binDir, "npm", logPath);
  await writeStub(binDir, "codegraph", logPath, { exitCode: 9, stderr: "codegraph failed" });
  const opencodeHome = path.join(fixture.root, "opencode");

  const result = await runCli(["install", "--aili-home", fixture.ailiHome, "--opencode-home", opencodeHome, "--enable-codegraph", "--json"], {
    env: { ...process.env, PATH: `${binDir}${path.delimiter}${process.env.PATH}` }
  });
  const summary = JSON.parse(result.stdout);

  assert.equal(result.code, 0);
  assert.equal(summary.componentInstall.status, "completed");
  assert.equal(summary.codegraph.status, "failed");
  assert.match(summary.codegraph.reason, /codegraph failed/);
  assert.match(summary.codegraph.recovery, /codegraph install --target=opencode --yes/);
  await fixture.cleanup();
});

test("OpenSpec is not installed without flag and --yes does not silently install it", async () => {
  const fixture = await fixtureAiliHome();
  const binDir = path.join(fixture.root, "bin");
  const logPath = path.join(fixture.root, "commands.log");
  await writeStub(binDir, "npm", logPath);
  await writeStub(binDir, "openspec", logPath);
  const opencodeHome = path.join(fixture.root, "opencode");

  const result = await runCli(["install", "--aili-home", fixture.ailiHome, "--opencode-home", opencodeHome, "--yes", "--json"], {
    env: { ...process.env, PATH: `${binDir}${path.delimiter}${process.env.PATH}` }
  });
  const summary = JSON.parse(result.stdout);

  assert.equal(summary.openspec.status, "skipped");
  await assert.rejects(readFile(logPath, "utf8"));
  await fixture.cleanup();
});

test("--enable-openspec installs package then initializes first-time project", { skip: openSpecNodeSkip }, async () => {
  const fixture = await fixtureAiliHome();
  const binDir = path.join(fixture.root, "bin");
  const logPath = path.join(fixture.root, "commands.log");
  const projectDir = path.join(fixture.root, "target-project");
  await mkdir(projectDir);
  await writeStub(binDir, "npm", logPath);
  await writeStub(binDir, "openspec", logPath);
  const opencodeHome = path.join(fixture.root, "opencode");

  const result = await runCli(["install", "--aili-home", fixture.ailiHome, "--opencode-home", opencodeHome, "--enable-openspec", "--json"], {
    cwd: projectDir,
    env: { ...process.env, PATH: `${binDir}${path.delimiter}${process.env.PATH}` }
  });
  const summary = JSON.parse(result.stdout);
  const logged = JSON.parse(await readFile(logPath, "utf8"));

  assert.equal(summary.openspec.status, "configured");
  assert.deepEqual(logged, [
    { name: "npm", args: ["install", "-g", "@fission-ai/openspec@latest"] },
    { name: "openspec", args: ["init"] }
  ]);
  await fixture.cleanup();
});

test("--enable-openspec updates existing OpenSpec project", { skip: openSpecNodeSkip }, async () => {
  const fixture = await fixtureAiliHome();
  const binDir = path.join(fixture.root, "bin");
  const logPath = path.join(fixture.root, "commands.log");
  const projectDir = path.join(fixture.root, "target-project");
  await mkdir(path.join(projectDir, "openspec"), { recursive: true });
  await writeStub(binDir, "npm", logPath);
  await writeStub(binDir, "openspec", logPath);
  const opencodeHome = path.join(fixture.root, "opencode");

  await runCli(["install", "--aili-home", fixture.ailiHome, "--opencode-home", opencodeHome, "--enable-openspec", "--json"], {
    cwd: projectDir,
    env: { ...process.env, PATH: `${binDir}${path.delimiter}${process.env.PATH}` }
  });
  const logged = JSON.parse(await readFile(logPath, "utf8"));

  assert.deepEqual(logged.at(-1), { name: "openspec", args: ["update"] });
  await fixture.cleanup();
});

test("OpenSpec optional commands ignore unsafe current-directory PATH entries", { skip: openSpecNodeSkip }, async () => {
  const fixture = await fixtureAiliHome();
  const npmBinDir = path.join(fixture.root, "npm-bin");
  const openspecBinDir = path.join(fixture.root, "openspec-bin");
  const safeLogPath = path.join(fixture.root, "commands.log");
  const unsafeLogPath = path.join(fixture.root, "unsafe.log");
  const projectDir = path.join(fixture.root, "target-project");
  await mkdir(projectDir);
  await writeStub(npmBinDir, "npm", safeLogPath);
  await writeStub(openspecBinDir, "openspec", safeLogPath);
  await writeStub(projectDir, "openspec", unsafeLogPath, { exitCode: 99, stderr: "unsafe openspec ran" });
  const opencodeHome = path.join(fixture.root, "opencode");

  const result = await runCli(["install", "--aili-home", fixture.ailiHome, "--opencode-home", opencodeHome, "--enable-openspec", "--json"], {
    cwd: projectDir,
    env: { ...process.env, PATH: [npmBinDir, projectDir, ".", "", openspecBinDir, process.env.PATH].join(path.delimiter) }
  });
  const summary = JSON.parse(result.stdout);
  const logged = JSON.parse(await readFile(safeLogPath, "utf8"));

  assert.equal(summary.openspec.status, "configured");
  assert.deepEqual(logged, [
    { name: "npm", args: ["install", "-g", "@fission-ai/openspec@latest"] },
    { name: "openspec", args: ["init"] }
  ]);
  await assert.rejects(readFile(unsafeLogPath, "utf8"));
  await fixture.cleanup();
});

test("OpenSpec optional commands ignore relative PATH entries", { skip: openSpecNodeSkip }, async () => {
  const fixture = await fixtureAiliHome();
  const npmBinDir = path.join(fixture.root, "npm-bin");
  const openspecBinDir = path.join(fixture.root, "openspec-bin");
  const unsafeBinDir = path.join(fixture.root, "target-project", "bin");
  const safeLogPath = path.join(fixture.root, "commands.log");
  const unsafeLogPath = path.join(fixture.root, "unsafe.log");
  const projectDir = path.join(fixture.root, "target-project");
  await mkdir(projectDir);
  await writeStub(npmBinDir, "npm", safeLogPath);
  await writeStub(openspecBinDir, "openspec", safeLogPath);
  await writeStub(unsafeBinDir, "openspec", unsafeLogPath, { exitCode: 99, stderr: "relative openspec ran" });
  const opencodeHome = path.join(fixture.root, "opencode");

  const result = await runCli(["install", "--aili-home", fixture.ailiHome, "--opencode-home", opencodeHome, "--enable-openspec", "--json"], {
    cwd: projectDir,
    env: { ...process.env, PATH: [npmBinDir, "bin", openspecBinDir, process.env.PATH].join(path.delimiter) }
  });
  const summary = JSON.parse(result.stdout);
  const logged = JSON.parse(await readFile(safeLogPath, "utf8"));

  assert.equal(summary.openspec.status, "configured");
  assert.deepEqual(logged.at(-1), { name: "openspec", args: ["init"] });
  await assert.rejects(readFile(unsafeLogPath, "utf8"));
  await fixture.cleanup();
});

test("optional commands fail closed when sanitized PATH has no safe entries", { skip: openSpecNodeSkip }, async () => {
  const fixture = await fixtureAiliHome();
  const unsafeLogPath = path.join(fixture.root, "unsafe.log");
  const projectDir = path.join(fixture.root, "target-project");
  await mkdir(projectDir);
  await writeStub(projectDir, "npm", unsafeLogPath, { exitCode: 99, stderr: "unsafe npm ran" });
  await writeStub(projectDir, "openspec", unsafeLogPath, { exitCode: 99, stderr: "unsafe openspec ran" });
  const opencodeHome = path.join(fixture.root, "opencode");

  const result = await runCli(["install", "--aili-home", fixture.ailiHome, "--opencode-home", opencodeHome, "--enable-openspec", "--json"], {
    cwd: projectDir,
    env: { ...process.env, PATH: [projectDir, ".", "bin", ""].join(path.delimiter) }
  });
  const summary = JSON.parse(result.stdout);

  assert.equal(result.code, 0);
  assert.equal(summary.componentInstall.status, "completed");
  assert.equal(summary.openspec.status, "failed");
  assert.match(summary.openspec.reason, /npm command not found in sanitized PATH/);
  await assert.rejects(readFile(unsafeLogPath, "utf8"));
  await fixture.cleanup();
});

test("OpenSpec low Node.js gate is reported separately before optional commands", { skip: !openSpecNodeSkip && "current Node.js already satisfies the OpenSpec minimum" }, async () => {
  const fixture = await fixtureAiliHome();
  const binDir = path.join(fixture.root, "bin");
  const logPath = path.join(fixture.root, "commands.log");
  const projectDir = path.join(fixture.root, "target-project");
  await mkdir(projectDir);
  await writeStub(binDir, "npm", logPath);
  await writeStub(binDir, "openspec", logPath);
  const opencodeHome = path.join(fixture.root, "opencode");

  const result = await runCli(["install", "--aili-home", fixture.ailiHome, "--opencode-home", opencodeHome, "--enable-openspec", "--json"], {
    cwd: projectDir,
    env: { ...process.env, PATH: `${binDir}${path.delimiter}${process.env.PATH}` }
  });
  const summary = JSON.parse(result.stdout);

  assert.equal(result.code, 0);
  assert.equal(summary.componentInstall.status, "completed");
  assert.equal(summary.openspec.status, "failed");
  assert.match(summary.openspec.reason, /OpenSpec requires Node\.js 20\.19\.0 or higher/);
  await assert.rejects(readFile(logPath, "utf8"));
  await fixture.cleanup();
});

test("OpenSpec failure is reported separately while core install succeeds", { skip: openSpecNodeSkip }, async () => {
  const fixture = await fixtureAiliHome();
  const binDir = path.join(fixture.root, "bin");
  const logPath = path.join(fixture.root, "commands.log");
  const projectDir = path.join(fixture.root, "target-project");
  await mkdir(projectDir);
  await writeStub(binDir, "npm", logPath, { exitCode: 8, stderr: "npm failed" });
  await writeStub(binDir, "openspec", logPath);
  const opencodeHome = path.join(fixture.root, "opencode");

  const result = await runCli(["install", "--aili-home", fixture.ailiHome, "--opencode-home", opencodeHome, "--enable-openspec", "--json"], {
    cwd: projectDir,
    env: { ...process.env, PATH: `${binDir}${path.delimiter}${process.env.PATH}` }
  });
  const summary = JSON.parse(result.stdout);

  assert.equal(result.code, 0);
  assert.equal(summary.componentInstall.status, "completed");
  assert.equal(summary.openspec.status, "failed");
  assert.match(summary.openspec.reason, /npm failed/);
  assert.match(summary.openspec.recovery, /npm install -g @fission-ai\/openspec@latest/);
  await fixture.cleanup();
});

test("unknown plugins are rejected and not installed", async () => {
  const fixture = await fixtureAiliHome();
  const opencodeHome = path.join(fixture.root, "opencode");
  const result = await runCli(["install", "--dry-run", "--aili-home", fixture.ailiHome, "--opencode-home", opencodeHome, "--plugin", "unknown-plugin", "--json"], { reject: false });

  assert.notEqual(result.code, 0);
  assert.match(result.stderr, /Unknown plugin/);
  await assert.rejects(stat(opencodeHome));
  await fixture.cleanup();
});

test("doctor reports required components and optional Playwright separately", async () => {
  const fixture = await fixtureAiliHome();
  const opencodeHome = path.join(fixture.root, "opencode");
  await runCli(["install", "--aili-home", fixture.ailiHome, "--opencode-home", opencodeHome, "--yes", "--model", "anthropic/claude-sonnet-4-5", "--json"]);

  const result = await runCli(["doctor", "--aili-home", fixture.ailiHome, "--opencode-home", opencodeHome, "--json"]);
  const summary = JSON.parse(result.stdout);

  assert.equal(summary.ok, true);
  assert.equal(summary.defaultAgent, "rose");
  assert.equal(summary.roseModel, "anthropic/claude-sonnet-4-5");
  assert.equal(summary.playwright, "missing-optional");
  assert.equal(summary.codegraph, "missing-optional");
  assert.ok(summary.required.some((entry) => entry.type === "global" && entry.name === "AGENTS.md" && entry.installed));
  assert.ok(summary.required.some((entry) => entry.type === "agent" && entry.name === "rose" && entry.installed));
  await fixture.cleanup();
});

test("doctor reports configured CodeGraph when OpenCode config has CodeGraph MCP", async () => {
  const fixture = await fixtureAiliHome();
  const opencodeHome = path.join(fixture.root, "opencode");
  await runCli(["install", "--aili-home", fixture.ailiHome, "--opencode-home", opencodeHome, "--yes", "--json"]);
  const configPath = path.join(opencodeHome, "opencode.json");
  const config = JSON.parse(await readFile(configPath, "utf8"));
  config.mcp = { ...(config.mcp ?? {}), codegraph: { type: "local", command: ["codegraph", "serve", "--mcp"], enabled: true } };
  await writeFile(configPath, `${JSON.stringify(config, null, 2)}\n`, "utf8");

  const result = await runCli(["doctor", "--aili-home", fixture.ailiHome, "--opencode-home", opencodeHome, "--json"]);
  const summary = JSON.parse(result.stdout);

  assert.equal(summary.codegraph, "configured");
  await fixture.cleanup();
});

test("packaged non-git install copies files instead of symlinking transient source", async () => {
  const fixture = await fixtureAiliHome();
  const opencodeHome = path.join(fixture.root, "opencode");
  await runCli(["install", "--aili-home", fixture.ailiHome, "--opencode-home", opencodeHome, "--yes", "--json"]);

  const roseTarget = path.join(opencodeHome, "agents", "rose.md");
  const skillTarget = path.join(opencodeHome, "skills", "rose-memory", "SKILL.md");
  const globalAgentsTarget = path.join(opencodeHome, "AGENTS.md");
  assert.equal((await lstat(roseTarget)).isSymbolicLink(), false);
  assert.equal((await lstat(path.dirname(skillTarget))).isSymbolicLink(), false);
  assert.equal((await lstat(globalAgentsTarget)).isSymbolicLink(), false);

  await rm(fixture.ailiHome, { recursive: true, force: true });
  assert.match(await readFile(roseTarget, "utf8"), /ROSE Runtime Charter/);
  assert.match(await readFile(skillTarget, "utf8"), /rose-memory/);
  assert.match(await readFile(globalAgentsTarget, "utf8"), /installer-owned-global-file/);
  await fixture.cleanup();
});

test("invalid config aborts install before component mutation", async () => {
  const fixture = await fixtureAiliHome();
  const opencodeHome = path.join(fixture.root, "opencode");
  await mkdir(opencodeHome, { recursive: true });
  await writeFile(path.join(opencodeHome, "opencode.jsonc"), `{ "default_agent": `, "utf8");

  const result = await runCli(["install", "--aili-home", fixture.ailiHome, "--opencode-home", opencodeHome, "--yes", "--json"], { reject: false });

  assert.notEqual(result.code, 0);
  assert.match(result.stderr, /invalid JSONC/);
  await assert.rejects(stat(path.join(opencodeHome, "agents", "rose.md")));
  await fixture.cleanup();
});

test("json mode preserves compatibility installer stderr on failure", async () => {
  const fixture = await fixtureAiliHome();
  const result = await runCli(["install", "--aili-home", fixture.ailiHome, "--opencode-home", "/", "--json"], { reject: false });

  assert.notEqual(result.code, 0);
  assert.equal(result.stdout, "");
  assert.match(result.stderr, /Refusing unsafe OPENCODE_HOME/);
  await fixture.cleanup();
});

test("relative OpenCode home is rejected before component mutation", async () => {
  const fixture = await fixtureAiliHome();
  const result = await runCli(["install", "--aili-home", fixture.ailiHome, "--opencode-home", "relative-opencode", "--yes", "--json"], { reject: false });

  assert.notEqual(result.code, 0);
  assert.match(result.stderr, /Refusing relative OPENCODE_HOME/);
  await assert.rejects(stat(path.join(repoRoot, "relative-opencode")));
  await fixture.cleanup();
});

test("unmanifested repo components abort install before mutation", async () => {
  const fixture = await fixtureAiliHome();
  const opencodeHome = path.join(fixture.root, "opencode");
  await writeFile(path.join(fixture.ailiHome, "agents", "extra-agent.md"), "# extra\n", "utf8");
  await writeFile(path.join(fixture.ailiHome, "commands", "extra-command.md"), "# extra\n", "utf8");
  await mkdir(path.join(fixture.ailiHome, "skills", "extra-skill"), { recursive: true });
  await writeFile(path.join(fixture.ailiHome, "skills", "extra-skill", "SKILL.md"), "---\nname: extra-skill\n---\n", "utf8");

  const result = await runCli(["install", "--aili-home", fixture.ailiHome, "--opencode-home", opencodeHome, "--yes", "--json"], { reject: false });

  assert.notEqual(result.code, 0);
  assert.match(result.stderr, /Unmanifested agents component\(s\): extra-agent/);
  await assert.rejects(stat(opencodeHome));
  await fixture.cleanup();
});

test("environment AILI_HOME is ignored unless passed by flag", async () => {
  const fixture = await fixtureAiliHome();
  const opencodeHome = path.join(fixture.root, "opencode");
  const poisonedAiliHome = path.join(fixture.root, "poisoned-aili-home");
  const result = await runCli(["install", "--dry-run", "--aili-home", fixture.ailiHome, "--opencode-home", opencodeHome, "--yes", "--json"], {
    env: { ...process.env, AILI_HOME: poisonedAiliHome }
  });
  const summary = JSON.parse(result.stdout);

  assert.equal(path.resolve(summary.ailiHome), path.resolve(fixture.ailiHome));
  assert.notEqual(path.resolve(summary.ailiHome), path.resolve(poisonedAiliHome));
  await fixture.cleanup();
});

test("environment OPENCODE_HOME is ignored unless passed by flag", async () => {
  const fixture = await fixtureAiliHome();
  const opencodeHome = path.join(fixture.root, "opencode");
  const result = await runCli(["install", "--dry-run", "--aili-home", fixture.ailiHome, "--opencode-home", opencodeHome, "--yes", "--json"], {
    env: { ...process.env, OPENCODE_HOME: "/" }
  });
  const summary = JSON.parse(result.stdout);

  assert.equal(path.resolve(summary.opencodeHome), path.resolve(opencodeHome));
  assert.notEqual(path.resolve(summary.opencodeHome), path.resolve("/"));
  await fixture.cleanup();
});

test("bash delegation ignores shell startup injection environment", async () => {
  const fixture = await fixtureAiliHome();
  const opencodeHome = path.join(fixture.root, "opencode");
  const marker = path.join(fixture.root, "bash-env-ran");
  const bashEnv = path.join(fixture.root, "malicious-bash-env.sh");
  await writeFile(bashEnv, `touch "${marker}"\n`, "utf8");

  await runCli(["install", "--dry-run", "--aili-home", fixture.ailiHome, "--opencode-home", opencodeHome, "--yes", "--json"], {
    env: { ...process.env, BASH_ENV: bashEnv, ENV: bashEnv, CDPATH: fixture.root }
  });

  await assert.rejects(stat(marker));
  await fixture.cleanup();
});

test("config merge refuses to write symlinked OpenCode config", async () => {
  const root = await mkdtemp(path.join(os.tmpdir(), "rose-aili-symlink-config-"));
  const opencodeHome = path.join(root, "opencode");
  await mkdir(opencodeHome, { recursive: true });
  const realConfig = path.join(root, "real-opencode.jsonc");
  await writeFile(realConfig, `{}\n`, "utf8");
  await symlink(realConfig, path.join(opencodeHome, "opencode.jsonc"));

  await assert.rejects(mergeOpenCodeConfig({ opencodeHome, dryRun: false, setDefaultRose: true }), /not a regular file/);
  assert.equal(await readFile(realConfig, "utf8"), `{}\n`);
  await rm(root, { recursive: true, force: true });
});

test("config merge refuses broken symlink OpenCode config without writing target", async () => {
  const root = await mkdtemp(path.join(os.tmpdir(), "rose-aili-broken-symlink-config-"));
  const opencodeHome = path.join(root, "opencode");
  await mkdir(opencodeHome, { recursive: true });
  const missingTarget = path.join(root, "missing-opencode.jsonc");
  await symlink(missingTarget, path.join(opencodeHome, "opencode.jsonc"));

  await assert.rejects(mergeOpenCodeConfig({ opencodeHome, dryRun: false, setDefaultRose: true }), /not a regular file/);
  await assert.rejects(stat(missingTarget));
  await rm(root, { recursive: true, force: true });
});

test("package exposes executable rose-aili bin at dist/cli.js with shebang", async () => {
  const packageJson = JSON.parse(await readFile(path.join(repoRoot, "package.json"), "utf8"));
  const cliText = await readFile(cliPath, "utf8");
  const cliStat = await stat(cliPath);

  assert.equal(packageJson.name, "rose-aili");
  assert.equal(packageJson.private, undefined);
  assert.deepEqual(packageJson.bin, { "rose-aili": "dist/cli.js" });
  assert.match(cliText, /^#!\/usr\/bin\/env node/);
  assert.ok((cliStat.mode & 0o111) !== 0, `expected ${cliPath} to be executable`);
});

test("root gitignore excludes CodeGraph local index", async () => {
  const gitignore = await readFile(path.join(repoRoot, ".gitignore"), "utf8");

  assert.match(gitignore, /^\.codegraph\/$/m);
});

test("packed package keeps CLI bin executable", async () => {
  const root = await mkdtemp(path.join(os.tmpdir(), "rose-aili-pack-"));
  const packResult = await execFileP("npm", ["pack", "--pack-destination", root], { cwd: repoRoot });
  const tarball = path.join(root, packResult.stdout.trim().split(/\r?\n/).at(-1));
  const extractDir = path.join(root, "extract");
  await mkdir(extractDir);
  await execFileP("tar", ["-xzf", tarball, "-C", extractDir]);
  const packedCli = path.join(extractDir, "package", "dist", "cli.js");
  const packedGlobalAgents = path.join(extractDir, "package", "templates", "opencode-global-AGENTS.md");
  const packedText = await readFile(packedCli, "utf8");
  const packedGlobalAgentsText = await readFile(packedGlobalAgents, "utf8");
  const packedStat = await stat(packedCli);

  assert.match(packedText, /^#!\/usr\/bin\/env node/);
  assert.match(packedGlobalAgentsText, /AILI_GLOBAL_AGENTS_TEMPLATE_SOURCE/);
  assert.ok((packedStat.mode & 0o111) !== 0, `expected ${packedCli} to be executable`);
  await rm(root, { recursive: true, force: true });
});

test("package bin symlink invokes CLI main", async () => {
  const root = await mkdtemp(path.join(os.tmpdir(), "rose-aili-bin-"));
  const binPath = path.join(root, "rose-aili");
  await symlink(cliPath, binPath);

  const result = await execFileP(binPath, ["help"], { cwd: repoRoot });

  assert.match(result.stdout, /rose-aili install\|update\|doctor/);
  await rm(root, { recursive: true, force: true });
});

async function fixtureAiliHome() {
  const root = await mkdtemp(path.join(os.tmpdir(), "rose-aili-fixture-"));
  const ailiHome = path.join(root, "aili-home");
  await mkdir(ailiHome, { recursive: true });
  for (const entry of ["agents", "commands", "skills", "manifests", "scripts", "templates"]) {
    await cp(path.join(repoRoot, entry), path.join(ailiHome, entry), { recursive: true });
  }
  return {
    root,
    ailiHome,
    cleanup: () => rm(root, { recursive: true, force: true })
  };
}

function runCli(args, options = {}) {
  return new Promise((resolve, reject) => {
    execFile(process.execPath, [cliPath, ...args], { cwd: options.cwd ?? repoRoot, env: options.env }, (error, stdout, stderr) => {
      const code = error && typeof error.code === "number" ? error.code : 0;
      const result = { code, stdout, stderr };
      if (error && options.reject !== false) reject(Object.assign(error, result));
      else resolve(result);
    });
  });
}

function execFileP(file, args, options = {}) {
  return new Promise((resolve, reject) => {
    execFile(file, args, options, (error, stdout, stderr) => {
      if (error) reject(Object.assign(error, { stdout, stderr }));
      else resolve({ stdout, stderr });
    });
  });
}

function supportsOpenSpecSuccessNode(version) {
  const [major, minor, patch] = version.split(".").map((part) => Number.parseInt(part, 10));
  return major > 20 || (major === 20 && (minor > 19 || (minor === 19 && patch >= 0)));
}

function assertDecision(summary, name, nextStep) {
  const decision = summary.optionalDecisions.find((entry) => entry.name === name);
  assert.ok(decision, `missing decision ${name}`);
  assert.equal(decision.status, "skipped");
  assert.equal(decision.nextStep, nextStep);
}

async function writeStub(binDir, name, logPath, options = {}) {
  await mkdir(binDir, { recursive: true });
  const exitCode = options.exitCode ?? 0;
  const stderr = JSON.stringify(options.stderr ?? "");
  const scriptPath = path.join(binDir, name);
  await writeFile(scriptPath, `#!/usr/bin/env node
import { readFileSync, writeFileSync } from "node:fs";
const logPath = ${JSON.stringify(logPath)};
let entries = [];
try { entries = JSON.parse(readFileSync(logPath, "utf8")); } catch {}
entries.push({ name: ${JSON.stringify(name)}, args: process.argv.slice(2) });
writeFileSync(logPath, JSON.stringify(entries));
const stderr = ${stderr};
if (stderr) process.stderr.write(stderr);
process.exit(${exitCode});
`, "utf8");
  await chmod(scriptPath, 0o755);
}
