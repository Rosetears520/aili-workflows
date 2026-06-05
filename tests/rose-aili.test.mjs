import assert from "node:assert/strict";
import { execFile } from "node:child_process";
import { cp, lstat, mkdir, mkdtemp, readFile, rm, stat, symlink, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { mergeOpenCodeConfig } from "../dist/config.js";

const repoRoot = process.cwd();
const cliPath = path.join(repoRoot, "dist", "cli.js");

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
  assert.ok(summary.required.some((entry) => entry.type === "agent" && entry.name === "rose" && entry.installed));
  await fixture.cleanup();
});

test("packaged non-git install copies files instead of symlinking transient source", async () => {
  const fixture = await fixtureAiliHome();
  const opencodeHome = path.join(fixture.root, "opencode");
  await runCli(["install", "--aili-home", fixture.ailiHome, "--opencode-home", opencodeHome, "--yes", "--json"]);

  const roseTarget = path.join(opencodeHome, "agents", "rose.md");
  const skillTarget = path.join(opencodeHome, "skills", "rose-memory", "SKILL.md");
  assert.equal((await lstat(roseTarget)).isSymbolicLink(), false);
  assert.equal((await lstat(path.dirname(skillTarget))).isSymbolicLink(), false);

  await rm(fixture.ailiHome, { recursive: true, force: true });
  assert.match(await readFile(roseTarget, "utf8"), /ROSE Runtime Charter/);
  assert.match(await readFile(skillTarget, "utf8"), /rose-memory/);
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

test("package exposes rose-aili bin at dist/cli.js with shebang", async () => {
  const packageJson = JSON.parse(await readFile(path.join(repoRoot, "package.json"), "utf8"));
  const cliText = await readFile(cliPath, "utf8");

  assert.equal(packageJson.name, "rose-aili");
  assert.equal(packageJson.private, undefined);
  assert.deepEqual(packageJson.bin, { "rose-aili": "dist/cli.js" });
  assert.match(cliText, /^#!\/usr\/bin\/env node/);
});

async function fixtureAiliHome() {
  const root = await mkdtemp(path.join(os.tmpdir(), "rose-aili-fixture-"));
  const ailiHome = path.join(root, "aili-home");
  await mkdir(ailiHome, { recursive: true });
  for (const entry of ["agents", "commands", "skills", "manifests", "scripts"]) {
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
    execFile(process.execPath, [cliPath, ...args], { cwd: repoRoot, env: options.env }, (error, stdout, stderr) => {
      const code = error && typeof error.code === "number" ? error.code : 0;
      const result = { code, stdout, stderr };
      if (error && options.reject !== false) reject(Object.assign(error, result));
      else resolve(result);
    });
  });
}
