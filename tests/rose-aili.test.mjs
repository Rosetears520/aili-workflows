import assert from "node:assert/strict";
import { execFile } from "node:child_process";
import { chmod, cp, lstat, mkdir, mkdtemp, readFile, readdir, readlink, rm, stat, symlink, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { applyPromptDecisions } from "../dist/cli.js";
import { mergeOpenCodeConfig } from "../dist/config.js";
import { loadManifest, repoInstallTargets, repoSourcePaths } from "../dist/manifest.js";

const repoRoot = process.cwd();
const cliPath = path.join(repoRoot, "dist", "cli.js");
const SKIP_DEFAULT_ADDONS = ["--skip-openspec"];
const openSpecNodeSkip = supportsOpenSpecSuccessNode(process.versions.node) ? false : "OpenSpec install success paths require Node.js 20.19.0+";
const SPECIALIZED_QA_LANES = [
  { agent: "test-coverage-reviewer", skill: "coverage-review", owner: "subagent:review", nearMiss: "Writing or modifying tests: use `test-engineer`" },
  { agent: "pr-test-analyzer", skill: "pr-test-analysis", owner: "subagent:review", nearMiss: "General code correctness review: `code-reviewer`" },
  { agent: "ai-regression-scout", skill: "ai-regression-scout", owner: "subagent:test", nearMiss: "Product-code behavior regression: use `test-engineer` or `debug-investigator`" },
  { agent: "silent-failure-reviewer", skill: "silent-failure-hunting", owner: "subagent:review", nearMiss: "Coverage adequacy: `coverage-review`" },
  { agent: "browser-qa-runner", skill: "browser-qa", owner: "subagent:test", nearMiss: "Persistent E2E report/trace packaging: `e2e-artifact-handling`" },
  { agent: "e2e-artifact-runner", skill: "e2e-artifact-handling", owner: "subagent:test", nearMiss: "Browser manual QA without durable artifacts: `browser-qa`" }
];

const ECC_SELECTED_AGENTS = [
  { name: "spec-miner", owner: "subagent:research" },
  { name: "agent-evaluator", owner: "subagent:review" },
  { name: "opensource-sanitizer", owner: "subagent:review" }
];

const ECC_SELECTED_SKILLS = [
  "comment-accuracy-review",
  "oss-release-readiness",
  "build-failure-repair",
  "code-review-quality-gates",
  "harness-optimization-audit"
];

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

  await runCli(["install", "--aili-home", fixture.ailiHome, "--opencode-home", opencodeHome, "--set-default-rose", ...SKIP_DEFAULT_ADDONS, "--json"]);
  const config = JSON.parse(await readFile(path.join(opencodeHome, "opencode.json"), "utf8"));

  assert.equal(config.default_agent, "rose");
  assert.equal(config.agent, undefined);
  assert.match(await readFile(path.join(opencodeHome, "commands", "local-review.md"), "utf8"), /# \/local-review/);
  await fixture.cleanup();
});

test("install defaults sync OpenCode config without model override", async () => {
  const fixture = await fixtureAiliHome();
  const opencodeHome = path.join(fixture.root, "opencode");

  await runCli(["install", "--aili-home", fixture.ailiHome, "--opencode-home", opencodeHome, ...SKIP_DEFAULT_ADDONS, "--json"]);
  const config = JSON.parse(await readFile(path.join(opencodeHome, "opencode.json"), "utf8"));

  assert.equal(config.default_agent, "rose");
  assert.equal(config.agent, undefined);
  await fixture.cleanup();
});

test("--skip-opencode-config does not write OpenCode config", async () => {
  const fixture = await fixtureAiliHome();
  const opencodeHome = path.join(fixture.root, "opencode");

  const result = await runCli(["install", "--aili-home", fixture.ailiHome, "--opencode-home", opencodeHome, "--skip-opencode-config", ...SKIP_DEFAULT_ADDONS, "--json"]);
  const summary = JSON.parse(result.stdout);

  assert.equal(summary.config.changed, false);
  assert.deepEqual(summary.config.skipped, ["OpenCode config sync explicitly skipped"]);
  await assert.rejects(readFile(path.join(opencodeHome, "opencode.json"), "utf8"));
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
  await runCli(["install", "--aili-home", enabledFixture.ailiHome, "--opencode-home", enabledHome, "--yes", "--enable-playwright", ...SKIP_DEFAULT_ADDONS, "--json"]);
  const enabledConfig = JSON.parse(await readFile(path.join(enabledHome, "opencode.json"), "utf8"));
  assert.deepEqual(enabledConfig.mcp.playwright.command, ["npx", "-y", "@playwright/mcp@0.0.75", "--caps=testing,storage"]);

  const skippedFixture = await fixtureAiliHome();
  const skippedHome = path.join(skippedFixture.root, "opencode-skipped");
  await runCli(["install", "--aili-home", skippedFixture.ailiHome, "--opencode-home", skippedHome, "--yes", "--skip-playwright", ...SKIP_DEFAULT_ADDONS, "--json"]);
  const skippedConfig = JSON.parse(await readFile(path.join(skippedHome, "opencode.json"), "utf8"));
  assert.equal(skippedConfig.mcp, undefined);
  await enabledFixture.cleanup();
  await skippedFixture.cleanup();
});

test("interactive install prompt decisions name the exact OpenSpec root without removed plugin prompts", async () => {
  const options = { dryRun: false, opencodeHome: "/tmp/opencode", ailiHome: repoRoot, projectRoot: repoRoot, plugins: [] };
  const answers = ["y", "", "y", "n", "y"];
  const prompts = [];

  await applyPromptDecisions(options, {}, async (prompt) => {
    prompts.push(prompt);
    return answers.shift() ?? "";
  }, { includeCoreConfig: true, includeOpenspec: true });

  assert.deepEqual(prompts, [
    "Set rose as OpenCode default_agent? [Y/n] ",
    "Model for agent.rose.model (provider/model, blank to skip): ",
    "Enable optional Playwright MCP? [y/N] ",
    "Install optional CodeGraph for OpenCode via `npm install -g @colbymchenry/codegraph@latest` and `codegraph install --target=opencode --yes`? Requires restarting OpenCode. [y/N] ",
    `Install/configure OpenSpec in exact project root ${repoRoot} via \`npm install -g @fission-ai/openspec@latest\` and \`openspec init/update\`? Requires Node.js 20.19+. [y/N] `
  ]);
  assert.equal(options.setDefaultRose, true);
  assert.equal(options.model, undefined);
  assert.equal(options.enablePlaywright, true);
  assert.equal(options.skipPlaywright, false);
  assert.equal(options.enableCodegraph, false);
  assert.equal(options.skipCodegraph, true);
  assert.equal(options.enableOpenspec, true);
  assert.equal(options.skipOpenspec, false);
});

test("update prompt decisions ask CodeGraph without core config or OpenSpec prompts", async () => {
  const options = { dryRun: false, opencodeHome: "/tmp/opencode", ailiHome: repoRoot, plugins: [] };
  const answers = ["y"];
  const prompts = [];

  await applyPromptDecisions(options, {}, async (prompt) => {
    prompts.push(prompt);
    return answers.shift() ?? "";
  }, { includeCoreConfig: false, includePlaywright: false, includeCodegraph: true, includeOpenspec: false });

  assert.deepEqual(prompts, [
    "Install optional CodeGraph for OpenCode via `npm install -g @colbymchenry/codegraph@latest` and `codegraph install --target=opencode --yes`? Requires restarting OpenCode. [y/N] "
  ]);
  assert.equal(options.setDefaultRose, undefined);
  assert.equal(options.model, undefined);
  assert.equal(options.enablePlaywright, undefined);
  assert.equal(options.skipPlaywright, undefined);
  assert.equal(options.enableCodegraph, true);
  assert.equal(options.skipCodegraph, false);
  assert.equal(options.enableOpenspec, undefined);
  assert.equal(options.skipOpenspec, undefined);
});

test("removed DCP parser compatibility follows current generic option command and help precedence", async () => {
  for (const command of ["install", "update", "doctor"]) {
    for (const flag of ["--enable-dcp", "--skip-dcp"]) {
      const result = await runCli([command, flag], { reject: false });
      assert.equal(result.code, 1, `${command} ${flag}`);
      assert.equal(result.stdout, "");
      assert.equal(result.stderr, `Unknown option: ${flag}\n`);
    }
  }

  for (const flag of ["--enable-dcp", "--skip-dcp"]) {
    const unknownOption = await runCli(["nonexistent", flag], { reject: false });
    assert.equal(unknownOption.code, 1);
    assert.equal(unknownOption.stderr, `Unknown option: ${flag}\n`);

    const bare = await runCli([flag], { reject: false });
    assert.equal(bare.code, 1);
    assert.equal(bare.stderr, `Unknown command: ${flag}\n`);
  }

  for (const argv of [
    ["install", "--help", "--enable-dcp"],
    ["update", "--skip-dcp", "--help"],
    ["doctor", "--help", "--enable-dcp"],
    ["nonexistent", "--enable-dcp", "--help"]
  ]) {
    const result = await runCli(argv, { reject: false });
    assert.equal(result.code, 1, argv.join(" "));
    assert.match(result.stderr, /Unknown option: --(?:enable|skip)-dcp/);
    assert.equal(result.stdout, "");
  }

  for (const argv of [
    ["help", "--enable-dcp"],
    ["--help", "--enable-dcp"],
    ["-h", "--skip-dcp"],
    ["nonexistent", "--help"]
  ]) {
    const result = await runCli(argv, { reject: false });
    assert.equal(result.code, 0, argv.join(" "));
    assert.equal(result.stderr, "");
    assert.match(result.stdout, /rose-aili install\|update\|doctor/);
    assert.doesNotMatch(result.stdout, /--(?:enable|skip)-dcp/);
  }
});

test("DCP zero interaction preserves third-party files metadata symlinks plugins and emits no status", async () => {
  for (const command of ["install", "update", "doctor"]) {
    for (const state of ["malformed-jsonc", "regular-json", "symlink-jsonc", "custom-home-bytes"]) {
      const fixture = await fixtureAiliHome();
      const opencodeHome = path.join(fixture.root, `custom-opencode-${command}-${state}`);
      const binDir = safeBinDir(fixture, `bin-${command}-${state}`);
      const processLog = path.join(fixture.root, `optional-${command}-${state}.log`);
      await mkdir(opencodeHome, { recursive: true });
      await writeStub(binDir, "opencode", processLog, { stdout: "third-party plugin present\n" });
      const pluginEntry = "@tarquinen/opencode-dcp@third-party";
      await writeFile(path.join(opencodeHome, "opencode.json"), `${JSON.stringify({ plugin: [pluginEntry, "unrelated-plugin"] })}\n`, "utf8");

      const dcpPath = path.join(opencodeHome, state === "regular-json" ? "dcp.json" : "dcp.jsonc");
      let symlinkTarget;
      if (state === "symlink-jsonc") {
        symlinkTarget = path.join(fixture.root, "third-party-dcp-target.jsonc");
        await writeFile(symlinkTarget, "{\n  // third-party bytes\n}\n", "utf8");
        await symlink(symlinkTarget, dcpPath);
      } else {
        const bytes = state === "malformed-jsonc" ? "{ malformed third-party bytes\0\n" : `third-party:${state}:\r\n`;
        await writeFile(dcpPath, bytes, "utf8");
        await chmod(dcpPath, 0o640);
      }

      const before = await capturePathState(dcpPath, symlinkTarget);
      const args = [command, "--aili-home", fixture.ailiHome, "--opencode-home", opencodeHome, "--skip-openspec"];
      if (state !== "custom-home-bytes") args.push("--json");
      const result = await runCli(args, {
        cwd: await safeCommandCwd(fixture),
        env: { ...process.env, PATH: `${binDir}${path.delimiter}${process.env.PATH}` },
        reject: false
      });
      assert.equal(result.code, command === "doctor" ? 1 : 0, `${command} ${state}: ${result.stderr}`);
      if (state === "custom-home-bytes") {
        assert.doesNotMatch(result.stdout, /DCP|"dcp"/);
      } else {
        const summary = JSON.parse(result.stdout);
        assert.equal(Object.hasOwn(summary, "dcp"), false);
        assert.equal(result.stdout.includes('"dcp"'), false);
      }
      assert.deepEqual(await capturePathState(dcpPath, symlinkTarget), before);
      await assert.rejects(readFile(processLog, "utf8"));
      const entries = await readFileNames(opencodeHome);
      assert.equal(entries.some((name) => name.startsWith("dcp.json.backup.") || name.startsWith("dcp.jsonc.backup.") || name.includes("dcp.json.tmp") || name.includes("dcp.jsonc.tmp")), false);
      const config = JSON.parse(await readFile(path.join(opencodeHome, "opencode.json"), "utf8"));
      assert.deepEqual(config.plugin, [pluginEntry, "unrelated-plugin"]);
      await fixture.cleanup();
    }
  }
});

test("Playwright MCP pin and unrelated MCP and plugin config are preserved", async () => {
  const fixture = await fixtureAiliHome();
  const opencodeHome = path.join(fixture.root, "opencode");
  await mkdir(opencodeHome, { recursive: true });
  await writeFile(path.join(opencodeHome, "opencode.json"), `${JSON.stringify({
    default_agent: "existing-agent",
    agent: { rose: { model: "existing/model" } },
    plugin: ["third-party-plugin"],
    mcp: { unrelated: { type: "local", command: ["unrelated"], enabled: true } }
  })}\n`, "utf8");

  await runCli(["install", "--aili-home", fixture.ailiHome, "--opencode-home", opencodeHome, "--enable-playwright", "--skip-openspec", "--json"]);
  const config = JSON.parse(await readFile(path.join(opencodeHome, "opencode.json"), "utf8"));
  assert.equal(config.default_agent, "existing-agent");
  assert.equal(config.agent.rose.model, "existing/model");
  assert.deepEqual(config.plugin, ["third-party-plugin"]);
  assert.deepEqual(config.mcp.unrelated, { type: "local", command: ["unrelated"], enabled: true });
  assert.deepEqual(config.mcp.playwright.command, ["npx", "-y", "@playwright/mcp@0.0.75", "--caps=testing,storage"]);
  await fixture.cleanup();
});

test("explicit OpenSpec update uses installed command without npm install", { skip: openSpecNodeSkip }, async () => {
  const fixture = await fixtureAiliHome();
  const binDir = safeBinDir(fixture);
  const logPath = path.join(fixture.root, "commands.log");
  const projectDir = path.join(fixture.root, "target-project");
  await mkdir(projectDir);
  await writeStub(binDir, "npm", logPath);
  await writeStub(binDir, "openspec", logPath);
  const opencodeHome = path.join(fixture.root, "opencode");

  const result = await runCli(["update", "--aili-home", fixture.ailiHome, "--opencode-home", opencodeHome, "--enable-openspec", "--project-root", projectDir, "--json"], {
    cwd: projectDir,
    env: { ...process.env, PATH: `${binDir}${path.delimiter}${process.env.PATH}` }
  });
  const summary = JSON.parse(result.stdout);
  const logged = JSON.parse(await readFile(logPath, "utf8"));

  assert.equal(summary.openspec.status, "configured");
  assert.deepEqual(logged, [
    { name: "openspec", args: ["--version"] },
    { name: "openspec", args: ["init"] }
  ]);
  await fixture.cleanup();
});

test("OpenSpec missing during update installs package then runs project command", { skip: openSpecNodeSkip }, async () => {
  const fixture = await fixtureAiliHome();
  const binDir = safeBinDir(fixture);
  const logPath = path.join(fixture.root, "commands.log");
  const projectDir = path.join(fixture.root, "target-project");
  await mkdir(projectDir);
  await writeStub(binDir, "npm", logPath);
  await writeOpenSpecStub(binDir, logPath, { versionExitCode: 1 });
  const opencodeHome = path.join(fixture.root, "opencode");

  const result = await runCli(["update", "--aili-home", fixture.ailiHome, "--opencode-home", opencodeHome, "--enable-openspec", "--project-root", projectDir, "--json"], {
    cwd: projectDir,
    env: { ...process.env, PATH: `${binDir}${path.delimiter}${process.env.PATH}` }
  });
  const summary = JSON.parse(result.stdout);
  const logged = JSON.parse(await readFile(logPath, "utf8"));

  assert.equal(summary.openspec.status, "configured");
  assert.deepEqual(logged, [
    { name: "openspec", args: ["--version"] },
    { name: "npm", args: ["install", "-g", "@fission-ai/openspec@latest"] },
    { name: "openspec", args: ["init"] }
  ]);
  await fixture.cleanup();
});

test("non-interactive install reports skipped optional decisions with next steps", async () => {
  const fixture = await fixtureAiliHome();
  const opencodeHome = path.join(fixture.root, "opencode");
  const result = await runCli(["install", "--aili-home", fixture.ailiHome, "--opencode-home", opencodeHome, ...SKIP_DEFAULT_ADDONS, "--json"]);
  const summary = JSON.parse(result.stdout);

  assert.equal(summary.componentInstall.status, "completed");
  assert.equal(summary.codegraph.status, "skipped");
  assert.equal(summary.openspec.status, "skipped");
  assertDecision(summary, "rose model override", "rose-aili install --model <provider/model>");
  assertDecision(summary, "Playwright MCP", "rose-aili install --enable-playwright");
  assertDecision(summary, "CodeGraph", "rose-aili install --enable-codegraph");
  assertDecision(summary, "OpenSpec", "rose-aili install --enable-openspec --project-root <absolute-canonical-path>");
  await fixture.cleanup();
});

test("non-interactive install skips OpenSpec without explicit enable and reports exact next step", async () => {
  const fixture = await fixtureAiliHome();
  const opencodeHome = path.join(fixture.root, "opencode");
  const result = await runCli(["install", "--dry-run", "--aili-home", fixture.ailiHome, "--opencode-home", opencodeHome, "--json"]);
  const summary = JSON.parse(result.stdout);

  assert.equal(summary.openspec.status, "skipped");
  assert.equal(Object.hasOwn(summary, "dcp"), false);
  assertDecision(summary, "OpenSpec", "rose-aili install --enable-openspec --project-root <absolute-canonical-path>");
  await fixture.cleanup();
});

test("install copies global AGENTS rules into OpenCode home", async () => {
  const fixture = await fixtureAiliHome();
  const opencodeHome = path.join(fixture.root, "opencode");

  await runCli(["install", "--aili-home", fixture.ailiHome, "--opencode-home", opencodeHome, ...SKIP_DEFAULT_ADDONS, "--json"]);
  const target = path.join(opencodeHome, "AGENTS.md");
  const text = await readFile(target, "utf8");

  assert.equal((await lstat(target)).isSymbolicLink(), false);
  assert.match(text, /AILI_GLOBAL_AGENTS_TEMPLATE_SOURCE: templates\/opencode-global-AGENTS\.md/);
  assert.match(text, /Project facts, repository commands, local test locations/);
  assert.match(text, /Do not symlink this global file into project roots/);
  assert.match(text, /codegraph init -i/);
  assert.match(text, /refuse batch or multi-repository initialization even under broad approval, and do not run `openspec init`/);
  await fixture.cleanup();
});

test("CodeGraph is not installed without flag and --yes does not silently install it", async () => {
  const fixture = await fixtureAiliHome();
  const binDir = path.join(fixture.root, "bin");
  const logPath = path.join(fixture.root, "commands.log");
  await writeStub(binDir, "npm", logPath);
  await writeStub(binDir, "codegraph", logPath);
  const opencodeHome = path.join(fixture.root, "opencode");

  const result = await runCli(["install", "--aili-home", fixture.ailiHome, "--opencode-home", opencodeHome, "--yes", ...SKIP_DEFAULT_ADDONS, "--json"], {
    env: { ...process.env, PATH: `${binDir}${path.delimiter}${process.env.PATH}` }
  });
  const summary = JSON.parse(result.stdout);

  assert.equal(summary.codegraph.status, "skipped");
  await assert.rejects(readFile(logPath, "utf8"));
  await fixture.cleanup();
});

test("--enable-codegraph delegates exact npm and codegraph argv", async () => {
  const fixture = await fixtureAiliHome();
  const binDir = safeBinDir(fixture);
  const logPath = path.join(fixture.root, "commands.log");
  await writeStub(binDir, "npm", logPath);
  await writeStub(binDir, "codegraph", logPath);
  const opencodeHome = path.join(fixture.root, "opencode");
  const commandCwd = await safeCommandCwd(fixture);

  const result = await runCli(["install", "--aili-home", fixture.ailiHome, "--opencode-home", opencodeHome, "--enable-codegraph", ...SKIP_DEFAULT_ADDONS, "--json"], {
    cwd: commandCwd,
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

  const result = await runCli(["install", "--dry-run", "--aili-home", fixture.ailiHome, "--opencode-home", opencodeHome, "--enable-codegraph", ...SKIP_DEFAULT_ADDONS, "--json"], {
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
  const binDir = safeBinDir(fixture);
  const logPath = path.join(fixture.root, "commands.log");
  await writeStub(binDir, "npm", logPath, { exitCode: 9, stderr: "npm failed" });
  await writeStub(binDir, "codegraph", logPath);
  const opencodeHome = path.join(fixture.root, "opencode");
  const commandCwd = await safeCommandCwd(fixture);

  const result = await runCli(["install", "--aili-home", fixture.ailiHome, "--opencode-home", opencodeHome, "--enable-codegraph", ...SKIP_DEFAULT_ADDONS, "--json"], {
    cwd: commandCwd,
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
  const binDir = safeBinDir(fixture);
  const logPath = path.join(fixture.root, "commands.log");
  await writeStub(binDir, "npm", logPath);
  await writeStub(binDir, "codegraph", logPath, { exitCode: 9, stderr: "codegraph failed" });
  const opencodeHome = path.join(fixture.root, "opencode");
  const commandCwd = await safeCommandCwd(fixture);

  const result = await runCli(["install", "--aili-home", fixture.ailiHome, "--opencode-home", opencodeHome, "--enable-codegraph", ...SKIP_DEFAULT_ADDONS, "--json"], {
    cwd: commandCwd,
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

test("default non-interactive install does not inspect or initialize ambient OpenSpec", async () => {
  const fixture = await fixtureAiliHome();
  const binDir = safeBinDir(fixture);
  const logPath = path.join(fixture.root, "commands.log");
  const projectDir = path.join(fixture.root, "target-project");
  await mkdir(projectDir);
  await writeStub(binDir, "npm", logPath);
  await writeStub(binDir, "openspec", logPath);
  const opencodeHome = path.join(fixture.root, "opencode");

  const result = await runCli(["install", "--aili-home", fixture.ailiHome, "--opencode-home", opencodeHome, "--yes", "--json"], {
    cwd: projectDir,
    env: { ...process.env, PATH: `${binDir}${path.delimiter}${process.env.PATH}` }
  });
  const summary = JSON.parse(result.stdout);
  assert.equal(summary.openspec.status, "skipped");
  assertDecision(summary, "OpenSpec", "rose-aili install --enable-openspec --project-root <absolute-canonical-path>");
  await assert.rejects(readFile(logPath, "utf8"));
  await fixture.cleanup();
});

test("--skip-openspec skips OpenSpec install", async () => {
  const fixture = await fixtureAiliHome();
  const binDir = path.join(fixture.root, "bin");
  const logPath = path.join(fixture.root, "commands.log");
  await writeStub(binDir, "npm", logPath);
  await writeStub(binDir, "openspec", logPath);
  const opencodeHome = path.join(fixture.root, "opencode");

  const result = await runCli(["install", "--aili-home", fixture.ailiHome, "--opencode-home", opencodeHome, "--yes", "--skip-openspec", "--json"], {
    env: { ...process.env, PATH: `${binDir}${path.delimiter}${process.env.PATH}` }
  });
  const summary = JSON.parse(result.stdout);

  assert.equal(summary.openspec.status, "skipped");
  await assert.rejects(readFile(logPath, "utf8"));
  await fixture.cleanup();
});

test("--enable-openspec requires an explicit exact project root", async () => {
  const fixture = await fixtureAiliHome();
  const opencodeHome = path.join(fixture.root, "opencode");
  const result = await runCli(["install", "--aili-home", fixture.ailiHome, "--opencode-home", opencodeHome, "--enable-openspec", "--json"], { reject: false });

  assert.equal(result.code, 1);
  assert.match(result.stderr, /--enable-openspec requires --project-root <path>/);
  await assert.rejects(readFile(path.join(opencodeHome, "opencode.json"), "utf8"));
  await fixture.cleanup();
});

test("OpenSpec exact project root rejects root, home, temp, relative, and symlink aliases before install", async () => {
  const fixture = await fixtureAiliHome();
  const target = path.join(fixture.root, "target-project");
  const alias = path.join(fixture.root, "target-alias");
  await mkdir(target);
  await symlink(target, alias, "dir");
  const opencodeHome = path.join(fixture.root, "opencode");
  for (const unsafeRoot of [path.parse(repoRoot).root, os.homedir(), os.tmpdir(), "relative-project", alias]) {
    const result = await runCli(["install", "--aili-home", fixture.ailiHome, "--opencode-home", opencodeHome, "--enable-openspec", "--project-root", unsafeRoot, "--json"], { reject: false });
    assert.equal(result.code, 1, unsafeRoot);
    assert.match(result.stderr, /Refusing|requires an absolute canonical directory/);
  }
  await assert.rejects(readFile(path.join(opencodeHome, "opencode.json"), "utf8"));
  await fixture.cleanup();
});

test("--enable-openspec installs package then initializes first-time exact project", { skip: openSpecNodeSkip }, async () => {
  const fixture = await fixtureAiliHome();
  const binDir = safeBinDir(fixture);
  const logPath = path.join(fixture.root, "commands.log");
  const projectDir = path.join(fixture.root, "target-project");
  await mkdir(projectDir);
  await writeStub(binDir, "npm", logPath);
  await writeOpenSpecStub(binDir, logPath, { versionExitCode: 1 });
  const opencodeHome = path.join(fixture.root, "opencode");

  const result = await runCli(["install", "--aili-home", fixture.ailiHome, "--opencode-home", opencodeHome, "--enable-openspec", "--project-root", projectDir, "--json"], {
    cwd: fixture.root,
    env: { ...process.env, PATH: `${binDir}${path.delimiter}${process.env.PATH}` }
  });
  const summary = JSON.parse(result.stdout);
  const logged = JSON.parse(await readFile(logPath, "utf8"));

  assert.equal(summary.openspec.status, "configured");
  assert.deepEqual(logged, [
    { name: "openspec", args: ["--version"] },
    { name: "npm", args: ["install", "-g", "@fission-ai/openspec@latest"] },
    { name: "openspec", args: ["init"] }
  ]);
  await fixture.cleanup();
});

test("--enable-openspec updates existing OpenSpec project", { skip: openSpecNodeSkip }, async () => {
  const fixture = await fixtureAiliHome();
  const binDir = safeBinDir(fixture);
  const logPath = path.join(fixture.root, "commands.log");
  const projectDir = path.join(fixture.root, "target-project");
  await mkdir(path.join(projectDir, "openspec"), { recursive: true });
  await writeStub(binDir, "npm", logPath);
  await writeStub(binDir, "openspec", logPath);
  const opencodeHome = path.join(fixture.root, "opencode");

  await runCli(["install", "--aili-home", fixture.ailiHome, "--opencode-home", opencodeHome, "--enable-openspec", "--project-root", projectDir, "--json"], {
    cwd: fixture.root,
    env: { ...process.env, PATH: `${binDir}${path.delimiter}${process.env.PATH}` }
  });
  const logged = JSON.parse(await readFile(logPath, "utf8"));

  assert.deepEqual(logged.at(-1), { name: "openspec", args: ["update"] });
  await fixture.cleanup();
});

test("OpenSpec optional commands ignore unsafe current-directory PATH entries", { skip: openSpecNodeSkip }, async () => {
  const fixture = await fixtureAiliHome();
  const npmBinDir = safeBinDir(fixture, "npm-bin");
  const openspecBinDir = safeBinDir(fixture, "openspec-bin");
  const safeLogPath = path.join(fixture.root, "commands.log");
  const unsafeLogPath = path.join(fixture.root, "unsafe.log");
  const projectDir = path.join(fixture.root, "target-project");
  await mkdir(projectDir);
  await writeStub(npmBinDir, "npm", safeLogPath);
  await writeOpenSpecStub(openspecBinDir, safeLogPath, { versionExitCode: 1 });
  await writeStub(projectDir, "openspec", unsafeLogPath, { exitCode: 99, stderr: "unsafe openspec ran" });
  const opencodeHome = path.join(fixture.root, "opencode");

  const result = await runCli(["install", "--aili-home", fixture.ailiHome, "--opencode-home", opencodeHome, "--enable-openspec", "--project-root", projectDir, "--json"], {
    cwd: projectDir,
    env: { ...process.env, PATH: [npmBinDir, projectDir, ".", "", openspecBinDir, process.env.PATH].join(path.delimiter) }
  });
  const summary = JSON.parse(result.stdout);
  const logged = JSON.parse(await readFile(safeLogPath, "utf8"));

  assert.equal(summary.openspec.status, "configured");
  assert.deepEqual(logged, [
    { name: "openspec", args: ["--version"] },
    { name: "npm", args: ["install", "-g", "@fission-ai/openspec@latest"] },
    { name: "openspec", args: ["init"] }
  ]);
  await assert.rejects(readFile(unsafeLogPath, "utf8"));
  await fixture.cleanup();
});

test("OpenSpec optional commands ignore unsafe absolute project subdirectory PATH entries", { skip: openSpecNodeSkip }, async () => {
  const fixture = await fixtureAiliHome();
  const npmBinDir = safeBinDir(fixture, "npm-bin");
  const openspecBinDir = safeBinDir(fixture, "openspec-bin");
  const safeLogPath = path.join(fixture.root, "commands.log");
  const unsafeLogPath = path.join(fixture.root, "unsafe.log");
  const projectDir = path.join(fixture.root, "target-project");
  const unsafeBinDir = path.join(projectDir, "node_modules", ".bin");
  await mkdir(projectDir, { recursive: true });
  await writeStub(npmBinDir, "npm", safeLogPath);
  await writeStub(openspecBinDir, "openspec", safeLogPath);
  await writeStub(unsafeBinDir, "openspec", unsafeLogPath, { exitCode: 99, stderr: "unsafe project openspec ran" });
  const opencodeHome = path.join(fixture.root, "opencode");

  const result = await runCli(["install", "--aili-home", fixture.ailiHome, "--opencode-home", opencodeHome, "--enable-openspec", "--project-root", projectDir, "--json"], {
    cwd: projectDir,
    env: { ...process.env, PATH: [npmBinDir, unsafeBinDir, openspecBinDir, process.env.PATH].join(path.delimiter) }
  });
  const summary = JSON.parse(result.stdout);
  const logged = JSON.parse(await readFile(safeLogPath, "utf8"));

  assert.equal(summary.openspec.status, "configured");
  assert.deepEqual(logged.at(-1), { name: "openspec", args: ["init"] });
  await assert.rejects(readFile(unsafeLogPath, "utf8"));
  await fixture.cleanup();
});

test("OpenSpec optional commands ignore relative PATH entries", { skip: openSpecNodeSkip }, async () => {
  const fixture = await fixtureAiliHome();
  const npmBinDir = safeBinDir(fixture, "npm-bin");
  const openspecBinDir = safeBinDir(fixture, "openspec-bin");
  const unsafeBinDir = path.join(fixture.root, "target-project", "bin");
  const safeLogPath = path.join(fixture.root, "commands.log");
  const unsafeLogPath = path.join(fixture.root, "unsafe.log");
  const projectDir = path.join(fixture.root, "target-project");
  await mkdir(projectDir);
  await writeStub(npmBinDir, "npm", safeLogPath);
  await writeStub(openspecBinDir, "openspec", safeLogPath);
  await writeStub(unsafeBinDir, "openspec", unsafeLogPath, { exitCode: 99, stderr: "relative openspec ran" });
  const opencodeHome = path.join(fixture.root, "opencode");

  const result = await runCli(["install", "--aili-home", fixture.ailiHome, "--opencode-home", opencodeHome, "--enable-openspec", "--project-root", projectDir, "--json"], {
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

  const result = await runCli(["install", "--aili-home", fixture.ailiHome, "--opencode-home", opencodeHome, "--enable-openspec", "--project-root", projectDir, "--json"], {
    cwd: projectDir,
    env: { ...process.env, PATH: [projectDir, ".", "bin", ""].join(path.delimiter) },
    reject: false
  });
  const summary = JSON.parse(result.stdout);

  assert.equal(result.code, 1);
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

  const result = await runCli(["install", "--aili-home", fixture.ailiHome, "--opencode-home", opencodeHome, "--enable-openspec", "--project-root", projectDir, "--json"], {
    cwd: projectDir,
    env: { ...process.env, PATH: `${binDir}${path.delimiter}${process.env.PATH}` },
    reject: false
  });
  const summary = JSON.parse(result.stdout);

  assert.equal(result.code, 1);
  assert.equal(summary.componentInstall.status, "completed");
  assert.equal(summary.openspec.status, "failed");
  assert.match(summary.openspec.reason, /OpenSpec requires Node\.js 20\.19\.0 or higher/);
  await assert.rejects(readFile(logPath, "utf8"));
  await fixture.cleanup();
});

test("explicit OpenSpec failure returns exit code 1 with the successful core install summary", { skip: openSpecNodeSkip }, async () => {
  for (const command of ["install", "update"]) {
    const fixture = await fixtureAiliHome();
    const binDir = safeBinDir(fixture);
    const logPath = path.join(fixture.root, "commands.log");
    const projectDir = path.join(fixture.root, "target-project");
    await mkdir(projectDir);
    await writeStub(binDir, "npm", logPath, { exitCode: 8, stderr: "npm failed" });
    await writeOpenSpecStub(binDir, logPath, { versionExitCode: 1 });
    const opencodeHome = path.join(fixture.root, "opencode");

    const result = await runCli([command, "--aili-home", fixture.ailiHome, "--opencode-home", opencodeHome, "--enable-openspec", "--project-root", projectDir, "--json"], {
      cwd: projectDir,
      env: { ...process.env, PATH: `${binDir}${path.delimiter}${process.env.PATH}` },
      reject: false
    });
    const summary = JSON.parse(result.stdout);

    assert.equal(result.code, 1, command);
    assert.equal(summary.componentInstall.status, "completed");
    assert.equal(summary.openspec.status, "failed");
    assert.match(summary.openspec.reason, /npm failed/);
    assert.match(summary.openspec.recovery, /npm install -g @fission-ai\/openspec@latest/);
    await fixture.cleanup();
  }
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

test("doctor reports required components and optional project CodeGraph separately", async () => {
  const fixture = await fixtureAiliHome();
  const binDir = path.join(fixture.root, "bin");
  const logPath = path.join(fixture.root, "commands.log");
  const projectDir = path.join(fixture.root, "target-project");
  await mkdir(projectDir);
  await writeStub(binDir, "codegraph", logPath);
  const opencodeHome = path.join(fixture.root, "opencode");
  await runCli(["install", "--aili-home", fixture.ailiHome, "--opencode-home", opencodeHome, "--yes", "--model", "anthropic/claude-sonnet-4-5", ...SKIP_DEFAULT_ADDONS, "--json"]);

  const result = await runCli(["doctor", "--aili-home", fixture.ailiHome, "--opencode-home", opencodeHome, "--json"], {
    cwd: projectDir,
    env: { ...process.env, PATH: `${binDir}${path.delimiter}${process.env.PATH}` }
  });
  const summary = JSON.parse(result.stdout);

  assert.equal(summary.ok, true);
  assert.equal(summary.defaultAgent, "rose");
  assert.equal(summary.roseModel, "anthropic/claude-sonnet-4-5");
  assert.equal(summary.playwright, "missing-optional");
  assert.equal(summary.codegraph.opencodeMcp, "missing-optional");
  assert.equal(summary.codegraph.projectIndex.status, "not-initialized-optional");
  assert.equal(summary.codegraph.projectIndex.root, projectDir);
  assert.equal(summary.codegraph.projectIndex.marker, path.join(projectDir, ".codegraph"));
  assert.match(summary.codegraph.projectIndex.nextStep, /codegraph init -i/);
  assert.match(summary.codegraph.projectIndex.nextStep, /codegraph status/);
  assert.equal(summary.install.ok, true);
  assert.equal(summary.source.sharedSkills.status, "ready");
  assert.equal(summary.source.manifestDrift.ok, true);
  assert.equal(summary.source.agentsMd.status, "missing");
  assert.ok(summary.required.some((entry) => entry.type === "global" && entry.name === "AGENTS.md" && entry.installed));
  assert.ok(summary.required.some((entry) => entry.type === "agent" && entry.name === "rose" && entry.installed));
  assert.ok(summary.required.some((entry) => entry.type === "skill" && entry.name === "rose-memory" && entry.installed));
  await stat(path.join(sharedSkillsHome(fixture), "rose-memory", "SKILL.md"));
  await assert.rejects(stat(path.join(opencodeHome, "skills", "rose-memory", "SKILL.md")));
  await assert.rejects(readFile(logPath, "utf8"));
  await fixture.cleanup();
});

test("doctor reports repo source drift without failing core OpenCode install", async () => {
  const fixture = await fixtureAiliHome();
  const opencodeHome = path.join(fixture.root, "opencode");
  await runCli(["install", "--aili-home", fixture.ailiHome, "--opencode-home", opencodeHome, "--yes", ...SKIP_DEFAULT_ADDONS, "--json"]);
  await writeFile(path.join(fixture.ailiHome, "agents", "unmanifested-agent.md"), "# extra\n", "utf8");
  await rm(path.join(fixture.ailiHome, ".agents", "skills", "rose-memory", "SKILL.md"));
  const templateAgents = await readFile(path.join(fixture.ailiHome, "templates", "AGENTS.md"), "utf8");
  await writeFile(path.join(fixture.ailiHome, "AGENTS.md"), templateAgents.replace(/AILI_AGENTS_TEMPLATE_VERSION:\s*\d+/, "AILI_AGENTS_TEMPLATE_VERSION: 0"), "utf8");

  const result = await runCli(["doctor", "--aili-home", fixture.ailiHome, "--opencode-home", opencodeHome, "--json"]);
  const summary = JSON.parse(result.stdout);

  assert.equal(result.code, 0);
  assert.equal(summary.ok, true);
  assert.equal(summary.install.ok, true);
  assert.equal(summary.source.ok, false);
  assert.deepEqual(summary.source.manifestDrift.agents.unmanifested, ["unmanifested-agent"]);
  assert.ok(summary.source.manifestDrift.skills.missing.includes("rose-memory"));
  assert.equal(summary.source.agentsMd.status, "stale");
  assert.match(summary.source.agentsMd.issues.join("\n"), /template version mismatch/);
  await fixture.cleanup();
});

test("doctor reports missing shared skill source separately from installed OpenCode targets", async () => {
  const fixture = await fixtureAiliHome();
  const opencodeHome = path.join(fixture.root, "opencode");
  await runCli(["install", "--aili-home", fixture.ailiHome, "--opencode-home", opencodeHome, "--yes", ...SKIP_DEFAULT_ADDONS, "--json"]);
  await rm(path.join(fixture.ailiHome, ".agents", "skills"), { recursive: true, force: true });

  const result = await runCli(["doctor", "--aili-home", fixture.ailiHome, "--opencode-home", opencodeHome, "--json"]);
  const summary = JSON.parse(result.stdout);

  assert.equal(result.code, 0);
  assert.equal(summary.ok, true);
  assert.equal(summary.source.sharedSkills.status, "missing");
  assert.ok(summary.source.manifestDrift.skills.missing.includes("rose-memory"));
  await fixture.cleanup();
});

test("doctor reports configured CodeGraph when OpenCode config has CodeGraph MCP", async () => {
  const fixture = await fixtureAiliHome();
  const projectDir = path.join(fixture.root, "target-project");
  await mkdir(projectDir);
  const opencodeHome = path.join(fixture.root, "opencode");
  await runCli(["install", "--aili-home", fixture.ailiHome, "--opencode-home", opencodeHome, "--yes", ...SKIP_DEFAULT_ADDONS, "--json"]);
  const configPath = path.join(opencodeHome, "opencode.json");
  const config = JSON.parse(await readFile(configPath, "utf8"));
  config.mcp = { ...(config.mcp ?? {}), codegraph: { type: "local", command: ["codegraph", "serve", "--mcp"], enabled: true } };
  await writeFile(configPath, `${JSON.stringify(config, null, 2)}\n`, "utf8");

  const result = await runCli(["doctor", "--aili-home", fixture.ailiHome, "--opencode-home", opencodeHome, "--json"], { cwd: projectDir });
  const summary = JSON.parse(result.stdout);

  assert.equal(summary.codegraph.opencodeMcp, "configured");
  assert.equal(summary.codegraph.projectIndex.status, "not-initialized-optional");
  await fixture.cleanup();
});

test("doctor reports initialized project CodeGraph index when .codegraph exists", async () => {
  const fixture = await fixtureAiliHome();
  const projectDir = path.join(fixture.root, "target-project");
  await mkdir(path.join(projectDir, ".codegraph"), { recursive: true });
  const opencodeHome = path.join(fixture.root, "opencode");
  await runCli(["install", "--aili-home", fixture.ailiHome, "--opencode-home", opencodeHome, "--yes", ...SKIP_DEFAULT_ADDONS, "--json"]);

  const result = await runCli(["doctor", "--aili-home", fixture.ailiHome, "--opencode-home", opencodeHome, "--json"], { cwd: projectDir });
  const summary = JSON.parse(result.stdout);

  assert.equal(summary.codegraph.projectIndex.status, "initialized");
  assert.equal(summary.codegraph.projectIndex.root, projectDir);
  assert.equal(summary.codegraph.projectIndex.marker, path.join(projectDir, ".codegraph"));
  assert.equal(summary.codegraph.projectIndex.nextStep, undefined);
  await fixture.cleanup();
});

test("packaged non-git install copies files instead of symlinking transient source", async () => {
  const fixture = await fixtureAiliHome();
  const opencodeHome = path.join(fixture.root, "opencode");
  await runCli(["install", "--aili-home", fixture.ailiHome, "--opencode-home", opencodeHome, "--yes", ...SKIP_DEFAULT_ADDONS, "--json"]);

  const roseTarget = path.join(opencodeHome, "agents", "rose.md");
  const skillTarget = path.join(sharedSkillsHome(fixture), "rose-memory", "SKILL.md");
  const globalAgentsTarget = path.join(opencodeHome, "AGENTS.md");
  assert.equal((await lstat(roseTarget)).isSymbolicLink(), false);
  assert.equal((await lstat(path.dirname(skillTarget))).isSymbolicLink(), false);
  assert.equal((await lstat(globalAgentsTarget)).isSymbolicLink(), false);
  await assert.rejects(stat(path.join(opencodeHome, "skills", "rose-memory")));

  await rm(fixture.ailiHome, { recursive: true, force: true });
  assert.match(await readFile(roseTarget, "utf8"), /ROSE Runtime Charter/);
  assert.match(await readFile(skillTarget, "utf8"), /rose-memory/);
  assert.match(await readFile(globalAgentsTarget, "utf8"), /installer-owned-global-file/);
  await fixture.cleanup();
});

test("selective Bash install links shared skills from .agents/skills and preserves OpenCode skills directory", async () => {
  const fixture = await fixtureAiliHome();
  const opencodeHome = path.join(fixture.root, "opencode");
  const skillsParent = path.join(opencodeHome, "skills");
  const preserved = path.join(skillsParent, "local-note.txt");
  await mkdir(skillsParent, { recursive: true });
  await writeFile(preserved, "keep\n", "utf8");

  await execFileP("bash", [
    path.join(fixture.ailiHome, "scripts", "install_opencode.sh"),
    "--mode", "selective",
    "--aili-home", fixture.ailiHome,
    "--opencode-home", opencodeHome,
    "--no-update"
  ], { env: installerEnv(fixture.root) });

  const skillTarget = path.join(sharedSkillsHome(fixture), "rose-memory");
  assert.equal((await lstat(skillsParent)).isDirectory(), true);
  assert.equal(await readFile(preserved, "utf8"), "keep\n");
  assert.equal((await lstat(skillTarget)).isSymbolicLink(), true);
  assert.equal(await readlink(skillTarget), path.join(fixture.ailiHome, ".agents", "skills", "rose-memory"));
  await assert.rejects(stat(path.join(opencodeHome, "skills", "rose-memory")));
  await fixture.cleanup();
});

test("selective Bash dry-run reports .agents skill source without mutating OpenCode home", async () => {
  const fixture = await fixtureAiliHome();
  const opencodeHome = path.join(fixture.root, "dry-run-opencode");

  const result = await execFileP("bash", [
    path.join(fixture.ailiHome, "scripts", "install_opencode.sh"),
    "--mode", "selective",
    "--aili-home", fixture.ailiHome,
    "--opencode-home", opencodeHome,
    "--dry-run"
  ], { env: installerEnv(fixture.root) });

  assert.match(result.stderr, new RegExp(`DRY RUN: would link entry: ${escapeRegExp(path.join(sharedSkillsHome(fixture), "rose-memory"))} -> .*\/\.agents\/skills\/rose-memory`));
  await assert.rejects(stat(opencodeHome));
  await assert.rejects(stat(sharedSkillsHome(fixture)));
  await fixture.cleanup();
});

test("direct Bash install rejects unmanifested manifest drift before mutation", async () => {
  const fixture = await fixtureAiliHome();
  const opencodeHome = path.join(fixture.root, "opencode");
  await writeFile(path.join(fixture.ailiHome, "agents", "extra-agent.md"), "# extra\n", "utf8");
  await writeFile(path.join(fixture.ailiHome, "commands", "extra-command.md"), "# extra\n", "utf8");
  await mkdir(path.join(fixture.ailiHome, ".agents", "skills", "extra-skill"), { recursive: true });
  await writeFile(path.join(fixture.ailiHome, ".agents", "skills", "extra-skill", "SKILL.md"), "---\nname: extra-skill\n---\n", "utf8");

  try {
    await execFileP("bash", [
      path.join(fixture.ailiHome, "scripts", "install_opencode.sh"),
      "--mode", "selective",
      "--aili-home", fixture.ailiHome,
      "--opencode-home", opencodeHome,
      "--dry-run"
    ], { env: installerEnv(fixture.root) });
    assert.fail("expected unmanifested direct Bash components to be rejected");
  } catch (error) {
    assert.match(error.stderr, /Unmanifested agents component\(s\): extra-agent/);
    assert.match(error.stderr, /Unmanifested commands component\(s\): extra-command/);
    assert.match(error.stderr, /Unmanifested skills component\(s\): extra-skill/);
  }
  await assert.rejects(stat(opencodeHome));
  await fixture.cleanup();
});

test("direct Bash install rejects missing manifest components before mutation", async () => {
  const fixture = await fixtureAiliHome();
  const opencodeHome = path.join(fixture.root, "opencode");
  await rm(path.join(fixture.ailiHome, "agents", "rose.md"));
  await rm(path.join(fixture.ailiHome, "commands", "build.md"));
  await rm(path.join(fixture.ailiHome, ".agents", "skills", "rose-memory", "SKILL.md"));

  try {
    await execFileP("bash", [
      path.join(fixture.ailiHome, "scripts", "install_opencode.sh"),
      "--mode", "copy",
      "--aili-home", fixture.ailiHome,
      "--opencode-home", opencodeHome,
      "--dry-run"
    ], { env: installerEnv(fixture.root) });
    assert.fail("expected missing direct Bash components to be rejected");
  } catch (error) {
    assert.match(error.stderr, /Manifest agents component\(s\) missing from AILI_HOME: rose/);
    assert.match(error.stderr, /Manifest commands component\(s\) missing from AILI_HOME: build/);
    assert.match(error.stderr, /Manifest skills component\(s\) missing from AILI_HOME: rose-memory/);
  }
  await assert.rejects(stat(opencodeHome));
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

test("OpenCode home traversal resolving to tmp root is rejected before mutation", async () => {
  const fixture = await fixtureAiliHome();
  const result = await runCli(["install", "--dry-run", "--aili-home", fixture.ailiHome, "--opencode-home", path.join(os.tmpdir(), "subdir", ".."), "--yes", "--json"], { reject: false });

  assert.notEqual(result.code, 0);
  assert.match(result.stderr, /Refusing unsafe OPENCODE_HOME/);
  assert.equal(result.stdout, "");
  await fixture.cleanup();
});

test("install summary uses canonical OpenCode home path", async () => {
  const fixture = await fixtureAiliHome();
  const rawOpenCodeHome = path.join(fixture.root, "parent", "child", "..", "opencode");
  const result = await runCli(["install", "--dry-run", "--aili-home", fixture.ailiHome, "--opencode-home", rawOpenCodeHome, "--yes", ...SKIP_DEFAULT_ADDONS, "--json"]);
  const summary = JSON.parse(result.stdout);

  assert.equal(summary.opencodeHome, path.resolve(rawOpenCodeHome));
  await assert.rejects(stat(path.resolve(rawOpenCodeHome)));
  await fixture.cleanup();
});

test("Bash installer canonicalizes OpenCode home before unsafe path validation", async () => {
  const fixture = await fixtureAiliHome();
  try {
    await execFileP("bash", [
      path.join(fixture.ailiHome, "scripts", "install_opencode.sh"),
      "--mode", "selective",
      "--aili-home", fixture.ailiHome,
      "--opencode-home", path.join(os.tmpdir(), "subdir", ".."),
      "--dry-run"
    ], { env: installerEnv(fixture.root) });
    assert.fail("expected unsafe OpenCode home to be rejected");
  } catch (error) {
    assert.match(error.stderr, /Refusing unsafe OPENCODE_HOME: \/tmp/);
  }
  await fixture.cleanup();
});

test("Bash installer rejects root HOME before shared skill mutation", async () => {
  const fixture = await fixtureAiliHome();
  const opencodeHome = path.join(fixture.root, "opencode");
  try {
    await execFileP("bash", [
      path.join(fixture.ailiHome, "scripts", "install_opencode.sh"),
      "--mode", "selective",
      "--aili-home", fixture.ailiHome,
      "--opencode-home", opencodeHome,
      "--dry-run"
    ], { env: installerEnv("/") });
    assert.fail("expected unsafe root HOME to be rejected");
  } catch (error) {
    assert.match(error.stderr, /Refusing unsafe HOME for shared skill install root: \//);
  }
  await assert.rejects(stat(opencodeHome));
  await fixture.cleanup();
});

test("Bash installer rejects tmp HOME before shared skill mutation", async () => {
  const fixture = await fixtureAiliHome();
  const opencodeHome = path.join(fixture.root, "opencode");
  try {
    await execFileP("bash", [
      path.join(fixture.ailiHome, "scripts", "install_opencode.sh"),
      "--mode", "selective",
      "--aili-home", fixture.ailiHome,
      "--opencode-home", opencodeHome,
      "--dry-run"
    ], { env: installerEnv(os.tmpdir()) });
    assert.fail("expected unsafe tmp HOME to be rejected");
  } catch (error) {
    assert.match(error.stderr, new RegExp(`Refusing unsafe HOME for shared skill install root: ${escapeRegExp(os.tmpdir())}`));
  }
  await assert.rejects(stat(opencodeHome));
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
  await mkdir(path.join(fixture.ailiHome, ".agents", "skills", "extra-skill"), { recursive: true });
  await writeFile(path.join(fixture.ailiHome, ".agents", "skills", "extra-skill", "SKILL.md"), "---\nname: extra-skill\n---\n", "utf8");

  const result = await runCli(["install", "--aili-home", fixture.ailiHome, "--opencode-home", opencodeHome, "--yes", "--json"], { reject: false });

  assert.notEqual(result.code, 0);
  assert.match(result.stderr, /Unmanifested agents component\(s\): extra-agent/);
  await assert.rejects(stat(opencodeHome));
  await fixture.cleanup();
});

test("manifest skills declare canonical shared source and shared install target", async () => {
  const manifest = await loadManifest(repoRoot);
  const skill = manifest.components.skills.find((entry) => entry.name === "rose-memory");
  assert.ok(skill, "expected rose-memory skill manifest entry");

  assert.equal(skill.path, ".agents/skills/rose-memory");
  assert.deepEqual(repoSourcePaths(skill), [".agents/skills/rose-memory"]);
  assert.deepEqual(repoInstallTargets(skill), [
    { kind: "shared", path: ".agents/skills/rose-memory" }
  ]);
  await stat(path.join(repoRoot, ".agents", "skills", "rose-memory", "SKILL.md"));
});

test("manifest registers local-review command", async () => {
  const manifest = await loadManifest(repoRoot);
  const commandNames = new Set(manifest.components.commands.map((entry) => entry.name));
  const command = manifest.components.commands.find((entry) => entry.name === "local-review");

  assert.ok(commandNames.has("local-review"), "expected manifest command local-review");
  assert.equal(command.path, "commands/local-review.md");
  assert.equal(command.defaultInstalled, true);
  assert.deepEqual(repoSourcePaths(command), ["commands/local-review.md"]);
  assert.deepEqual(repoInstallTargets(command), [{ kind: "opencode", path: "commands/local-review.md" }]);
  assert.match(await readFile(path.join(repoRoot, "commands", "local-review.md"), "utf8"), /OpenCode's built-in `\/review`/);
});

test("manifest registers specialized QA agents and skills", async () => {
  const manifest = await loadManifest(repoRoot);
  const agentNames = new Set(manifest.components.agents.map((entry) => entry.name));
  const skillNames = new Set(manifest.components.skills.map((entry) => entry.name));
  const roseText = await readFile(path.join(repoRoot, "agents", "rose.md"), "utf8");
  const reviewPipelineText = await readFile(path.join(repoRoot, ".agents", "skills", "review-pipeline", "SKILL.md"), "utf8");

  for (const { agent: name, owner } of SPECIALIZED_QA_LANES) {
    assert.ok(agentNames.has(name), `expected manifest agent ${name}`);
    await stat(path.join(repoRoot, "agents", `${name}.md`));
    assert.ok(roseText.includes(`"${name}": allow`));
    assert.ok(roseText.includes(`- \`${name}\` (\`${owner}\`):`));
    assert.ok(reviewPipelineText.includes(`- \`${name}\`:`));
  }

  for (const { agent, skill: name, nearMiss } of SPECIALIZED_QA_LANES) {
    assert.ok(skillNames.has(name), `expected manifest skill ${name}`);
    const skill = manifest.components.skills.find((entry) => entry.name === name);
    assert.equal(skill.path, `.agents/skills/${name}`);
    assert.deepEqual(repoInstallTargets(skill), [
      { kind: "shared", path: `.agents/skills/${name}` }
    ]);
    const skillText = await readFile(path.join(repoRoot, ".agents", "skills", name, "SKILL.md"), "utf8");
    assert.match(skillText, new RegExp(`---\\nname: ${name}\\n`));
    assert.ok(skillText.includes(`Agent: \`${agent}\``));
    assert.match(skillText, new RegExp(escapeRegExp(nearMiss)));
  }
});

test("manifest registers ECC-derived selected agents and skills", async () => {
  const manifest = await loadManifest(repoRoot);
  const agentNames = new Set(manifest.components.agents.map((entry) => entry.name));
  const skillNames = new Set(manifest.components.skills.map((entry) => entry.name));
  const roseText = await readFile(path.join(repoRoot, "agents", "rose.md"), "utf8");
  const reviewPipelineText = await readFile(path.join(repoRoot, ".agents", "skills", "review-pipeline", "SKILL.md"), "utf8");

  for (const { name, owner } of ECC_SELECTED_AGENTS) {
    const agent = manifest.components.agents.find((entry) => entry.name === name);
    assert.ok(agentNames.has(name), `expected manifest agent ${name}`);
    assert.equal(agent.path, `agents/${name}.md`);
    assert.equal(agent.defaultInstalled, true);
    await stat(path.join(repoRoot, "agents", `${name}.md`));
    assert.ok(roseText.includes(`"${name}": allow`));
    assert.ok(roseText.includes(`- \`${name}\` (\`${owner}\`):`));
  }

  assert.ok(reviewPipelineText.includes("- `agent-evaluator`:"));
  assert.ok(reviewPipelineText.includes("- `opensource-sanitizer`:"));
  assert.ok(reviewPipelineText.includes("- `code-review-quality-gates`:"));

  for (const name of ECC_SELECTED_SKILLS) {
    assert.ok(skillNames.has(name), `expected manifest skill ${name}`);
    const skill = manifest.components.skills.find((entry) => entry.name === name);
    assert.equal(skill.path, `.agents/skills/${name}`);
    assert.equal(skill.defaultInstalled, true);
    assert.deepEqual(repoInstallTargets(skill), [
      { kind: "shared", path: `.agents/skills/${name}` }
    ]);
    const skillText = await readFile(path.join(repoRoot, ".agents", "skills", name, "SKILL.md"), "utf8");
    assert.match(skillText, new RegExp(`---\\nname: ${name}\\n`));
  }
});

test("ECC-derived components preserve safety boundaries and exclusions", async () => {
  const manifest = await loadManifest(repoRoot);
  const componentNames = new Set([
    ...manifest.components.agents.map((entry) => entry.name),
    ...manifest.components.skills.map((entry) => entry.name)
  ]);
  const roseText = await readFile(path.join(repoRoot, "agents", "rose.md"), "utf8");
  const reviewPipelineText = await readFile(path.join(repoRoot, ".agents", "skills", "review-pipeline", "SKILL.md"), "utf8");

  for (const forbidden of ["type-design-analyzer", "typescript-reviewer", "python-reviewer", "general-reviewer"]) {
    assert.equal(componentNames.has(forbidden), false, `unexpected forbidden component ${forbidden}`);
    assert.doesNotMatch(roseText, new RegExp(`"${escapeRegExp(forbidden)}":\\s*allow`));
  }

  for (const { name } of ECC_SELECTED_AGENTS) {
    const agentText = await readFile(path.join(repoRoot, "agents", `${name}.md`), "utf8");
    assert.ok(agentText.includes("edit: deny"));
    assert.ok(agentText.includes("task: deny"));
    assert.ok(agentText.includes("external_directory: ask"));
    assert.ok(agentText.includes("bash: deny"));
    assert.doesNotMatch(agentText, /"git diff[^"]*": allow/);
    assert.doesNotMatch(agentText, /"git show[^"]*": allow/);
    assert.doesNotMatch(agentText, /"git log[^"]*": allow/);
    assert.doesNotMatch(agentText, /"git ls-files[^"]*": allow/);
  }

  const sanitizerText = await readFile(path.join(repoRoot, "agents", "opensource-sanitizer.md"), "utf8");
  assert.ok(sanitizerText.includes("Do not edit, delete, move, rename, publish, unpublish"));
  assert.ok(sanitizerText.includes("report only `path:line`, type, and `<redacted>`"));

  const expectedSkillBoundaries = new Map([
    ["comment-accuracy-review", "General correctness, architecture, performance, or security review"],
    ["oss-release-readiness", "Actual publishing, tagging, release creation, deletion, history rewrite"],
    ["build-failure-repair", "Dependency upgrades, lockfile regeneration, toolchain migration, or CI redesign"],
    ["code-review-quality-gates", "do not invent a new code-review agent"],
    ["harness-optimization-audit", "Do not edit core harness controls from this skill"]
  ]);

  for (const [name, marker] of expectedSkillBoundaries) {
    const skillText = await readFile(path.join(repoRoot, ".agents", "skills", name, "SKILL.md"), "utf8");
    assert.ok(skillText.includes(marker), `expected ${name} to include boundary marker`);
  }

  assert.ok(reviewPipelineText.includes("only for disputed, critical, acceptance-blocking, or user-requested agent/subagent outputs"));
  assert.ok(reviewPipelineText.includes("- `oss-release-readiness`:"));
});

test("manifest registers DeerFlow clean-room pattern skills", async () => {
  const manifest = await loadManifest(repoRoot);
  const skillNames = new Set(manifest.components.skills.map((entry) => entry.name));

  for (const name of [
    "academic-paper-review",
    "systematic-literature-review",
    "newsletter-generation",
    "consulting-analysis",
    "data-analysis",
    "chart-visualization"
  ]) {
    assert.ok(skillNames.has(name), `expected manifest skill ${name}`);
    const skill = manifest.components.skills.find((entry) => entry.name === name);
    assert.equal(skill.path, `.agents/skills/${name}`);
    assert.deepEqual(repoInstallTargets(skill), [
      { kind: "shared", path: `.agents/skills/${name}` }
    ]);
    await stat(path.join(repoRoot, ".agents", "skills", name, "SKILL.md"));
  }
});

test("manifest rejects unsafe source and install target paths before mutation", async () => {
  const sourceFixture = await fixtureAiliHome();
  const sourceOpenCodeHome = path.join(sourceFixture.root, "opencode");
  const sourceManifestPath = path.join(sourceFixture.ailiHome, "manifests", "rose-aili.components.json");
  const sourceManifest = JSON.parse(await readFile(sourceManifestPath, "utf8"));
  sourceManifest.components.skills[0].sourcePath = "../unsafe-source";
  await writeFile(sourceManifestPath, `${JSON.stringify(sourceManifest, null, 2)}\n`, "utf8");

  const sourceResult = await runCli(["install", "--dry-run", "--aili-home", sourceFixture.ailiHome, "--opencode-home", sourceOpenCodeHome, "--yes", "--json"], { reject: false });
  assert.notEqual(sourceResult.code, 0);
  assert.match(sourceResult.stderr, /Invalid manifest source path/);
  await assert.rejects(stat(sourceOpenCodeHome));
  await sourceFixture.cleanup();

  const targetFixture = await fixtureAiliHome();
  const targetOpenCodeHome = path.join(targetFixture.root, "opencode");
  const targetManifestPath = path.join(targetFixture.ailiHome, "manifests", "rose-aili.components.json");
  const targetManifest = JSON.parse(await readFile(targetManifestPath, "utf8"));
  targetManifest.components.skills[0].installTargets[0].path = "../unsafe-target";
  await writeFile(targetManifestPath, `${JSON.stringify(targetManifest, null, 2)}\n`, "utf8");

  const targetResult = await runCli(["install", "--dry-run", "--aili-home", targetFixture.ailiHome, "--opencode-home", targetOpenCodeHome, "--yes", "--json"], { reject: false });
  assert.notEqual(targetResult.code, 0);
  assert.match(targetResult.stderr, /Invalid manifest install target/);
  await assert.rejects(stat(targetOpenCodeHome));
  await targetFixture.cleanup();
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
  assert.ok(packageJson.files.includes(".agents/"));
  assert.equal(packageJson.files.includes("skills/"), false);
  assert.match(cliText, /^#!\/usr\/bin\/env node/);
  assert.ok((cliStat.mode & 0o111) !== 0, `expected ${cliPath} to be executable`);
});

test("root gitignore excludes local generated browser and index residue", async () => {
  const gitignore = await readFile(path.join(repoRoot, ".gitignore"), "utf8");

  assert.match(gitignore, /^\.codegraph\/$/m);
  assert.match(gitignore, /^\.playwright-mcp\/$/m);
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
  const packedEntries = (await execFileP("tar", ["-tzf", tarball])).stdout.split(/\r?\n/).filter(Boolean);

  assert.match(packedText, /^#!\/usr\/bin\/env node/);
  assert.match(packedGlobalAgentsText, /AILI_GLOBAL_AGENTS_TEMPLATE_SOURCE/);
  assert.ok((packedStat.mode & 0o111) !== 0, `expected ${packedCli} to be executable`);
  assert.ok(packedEntries.includes("package/manifests/rose-aili.components.json"));
  assert.ok(packedEntries.includes("package/agents/rose.md"));
  assert.ok(packedEntries.includes("package/commands/build.md"));
  assert.ok(packedEntries.includes("package/commands/local-review.md"));
  assert.ok(packedEntries.includes("package/.agents/skills/rose-memory/SKILL.md"));
  const manifest = await loadManifest(repoRoot);
  for (const agent of manifest.components.agents) {
    assert.ok(packedEntries.includes(`package/${agent.path}`), `expected packed agent ${agent.path}`);
  }
  for (const command of manifest.components.commands) {
    assert.ok(packedEntries.includes(`package/${command.path}`), `expected packed command ${command.path}`);
  }
  for (const skill of manifest.components.skills) {
    assert.ok(packedEntries.includes(`package/${skill.path}/SKILL.md`), `expected packed skill ${skill.path}`);
  }
  assert.equal(packedEntries.some((entry) => entry.startsWith("package/skills/")), false);
  assert.equal(packedEntries.some((entry) => entry.startsWith("package/.codegraph/")), false);
  assert.equal(packedEntries.some((entry) => entry.startsWith("package/.playwright-mcp/")), false);
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

test("help documents supported options and omits removed plugin flags", async () => {
  for (const argv of [["help"], ["--help"], ["install", "--help"], ["update", "--help"], ["doctor", "--help"]]) {
    const result = await runCli(argv);
    assert.match(result.stdout, /--skip-opencode-config/);
    assert.match(result.stdout, /--enable-openspec \| --skip-openspec/);
    assert.match(result.stdout, /--project-root <absolute-canonical-path>/);
    assert.doesNotMatch(result.stdout, /--(?:enable|skip)-dcp/);
  }
});

async function fixtureAiliHome() {
  const root = await mkdtemp(path.join(os.tmpdir(), "rose-aili-fixture-"));
  const safeRoot = path.join(repoRoot, ".opencode", "test-fixtures", path.basename(root));
  const ailiHome = path.join(root, "aili-home");
  await mkdir(ailiHome, { recursive: true });
  for (const entry of ["agents", ".agents", "commands", "manifests", "scripts", "templates"]) {
    await cp(path.join(repoRoot, entry), path.join(ailiHome, entry), { recursive: true });
  }
  return {
    root,
    safeRoot,
    ailiHome,
    cleanup: async () => {
      await rm(root, { recursive: true, force: true });
      await rm(safeRoot, { recursive: true, force: true });
    }
  };
}

function safeBinDir(fixture, name = "bin") {
  return path.join(fixture.safeRoot, name);
}

async function safeCommandCwd(fixture) {
  const cwd = path.join(fixture.safeRoot, "cwd");
  await mkdir(cwd, { recursive: true });
  return cwd;
}

function runCli(args, options = {}) {
  return new Promise((resolve, reject) => {
    execFile(process.execPath, [cliPath, ...args], { cwd: options.cwd ?? repoRoot, env: testCliEnv(args, options.env) }, (error, stdout, stderr) => {
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

function testCliEnv(args, baseEnv = process.env) {
  return installerEnv(cliHomeFromArgs(args) ?? baseEnv.HOME, baseEnv);
}

function cliHomeFromArgs(args) {
  const index = args.indexOf("--opencode-home");
  const opencodeHome = index >= 0 ? args[index + 1] : undefined;
  return opencodeHome && path.isAbsolute(opencodeHome) ? path.dirname(opencodeHome) : undefined;
}

function sharedSkillsHome(fixture) {
  return path.join(fixture.root, ".agents", "skills");
}

function installerEnv(home, baseEnv = process.env) {
  return {
    ...baseEnv,
    HOME: home ?? baseEnv.HOME,
    OPENCODE_ALLOW_CUSTOM_HOME: "yes",
    AILI_ALLOW_PACKAGE_HOME: "yes"
  };
}

function escapeRegExp(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
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

async function capturePathState(filePath, symlinkTarget) {
  const bytes = (await readFile(filePath)).toString("base64");
  const targetStats = symlinkTarget ? await stat(symlinkTarget, { bigint: true }) : undefined;
  const pathStats = await lstat(filePath, { bigint: true });
  return {
    bytes,
    link: pathStats.isSymbolicLink() ? await readlink(filePath) : null,
    path: capturedMetadata(pathStats),
    target: targetStats ? capturedMetadata(targetStats) : null
  };
}

function capturedMetadata(stats) {
  return {
    mode: stats.mode.toString(),
    size: stats.size.toString(),
    mtimeNs: stats.mtimeNs.toString(),
    ctimeNs: stats.ctimeNs.toString(),
    ino: stats.ino.toString()
  };
}

async function readFileNames(directory) {
  return readdir(directory);
}

async function writeStub(binDir, name, logPath, options = {}) {
  await mkdir(binDir, { recursive: true });
  const exitCode = options.exitCode ?? 0;
  const stdout = JSON.stringify(options.stdout ?? "");
  const stderr = JSON.stringify(options.stderr ?? "");
  const scriptPath = path.join(binDir, name);
  await writeFile(scriptPath, `#!/usr/bin/env node
import { readFileSync, writeFileSync } from "node:fs";
const logPath = ${JSON.stringify(logPath)};
let entries = [];
try { entries = JSON.parse(readFileSync(logPath, "utf8")); } catch {}
entries.push({ name: ${JSON.stringify(name)}, args: process.argv.slice(2) });
writeFileSync(logPath, JSON.stringify(entries));
const stdout = ${stdout};
if (stdout) process.stdout.write(stdout);
const stderr = ${stderr};
if (stderr) process.stderr.write(stderr);
process.exit(${exitCode});
`, "utf8");
  await chmod(scriptPath, 0o755);
}

async function writeOpenSpecStub(binDir, logPath, options = {}) {
  await mkdir(binDir, { recursive: true });
  const versionExitCode = options.versionExitCode ?? 0;
  const scriptPath = path.join(binDir, "openspec");
  await writeFile(scriptPath, `#!/usr/bin/env node
import { readFileSync, writeFileSync } from "node:fs";
const logPath = ${JSON.stringify(logPath)};
let entries = [];
try { entries = JSON.parse(readFileSync(logPath, "utf8")); } catch {}
const args = process.argv.slice(2);
entries.push({ name: "openspec", args });
writeFileSync(logPath, JSON.stringify(entries));
if (args.length === 1 && args[0] === "--version") {
  process.exit(${versionExitCode});
}
process.exit(0);
`, "utf8");
  await chmod(scriptPath, 0o755);
}
