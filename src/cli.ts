#!/usr/bin/env node
import os from "node:os";
import { realpathSync } from "node:fs";
import path from "node:path";
import readline from "node:readline/promises";
import { fileURLToPath } from "node:url";
import { readOpenCodeConfig } from "./config.js";
import { runDoctor } from "./doctor.js";
import { defaultAiliHome, InstallOptions, runInstall, validateExactProjectRoot, validateOpenCodeHome } from "./installer.js";

interface CliOptions extends InstallOptions {
  help?: boolean;
}

type PromptAsk = (prompt: string) => Promise<string>;

async function main(argv: string[]): Promise<void> {
  const command = argv[0] ?? "help";
  if (command === "help" || command === "--help" || command === "-h") {
    printHelp();
    return;
  }
  const options = parseOptions(argv.slice(1));
  if (options.help) {
    printHelp();
    return;
  }
  if (((command === "install" || command === "update" || command === "doctor") && selectedProfile(options) === "opencode")) {
    validateOpenCodeHome(options.opencodeHome);
  }
  if (command === "install" || command === "update") {
    if (selectedProfile(options) === "opencode" && options.projectRoot) options.projectRoot = validateExactProjectRoot(options.projectRoot);
    const includeOpenCode = selectedProfile(options) === "opencode";
    await applyInteractivePrompts(options, command === "install"
      ? { includeCoreConfig: includeOpenCode, includePlaywright: includeOpenCode, includeCodegraph: includeOpenCode, includeGraphify: includeOpenCode, includeOpenspec: includeOpenCode }
      : { includeCoreConfig: false, includePlaywright: false, includeCodegraph: includeOpenCode, includeGraphify: includeOpenCode, includeOpenspec: false });
    if (options.enableOpenspec && !options.skipOpenspec && !options.projectRoot) {
      throw new Error("--enable-openspec requires --project-root <path>.");
    }
    const summary = await runInstall(command, options);
    print(summary, options.json);
    if (summary.officecli.status === "failed" || summary.mempalace.status === "failed" || (options.enableOpenspec && !options.skipOpenspec && summary.openspec.status === "failed")) {
      process.exitCode = 1;
    }
    return;
  }
  if (command === "doctor") {
    const summary = await runDoctor({
      opencodeHome: options.opencodeHome,
      ailiHome: options.ailiHome,
      profile: selectedProfile(options),
      skills: options.skills,
      skillGroups: options.skillGroups
    });
    print(summary, options.json);
    if (!summary.ok) process.exitCode = 1;
    return;
  }
  throw new Error(`Unknown command: ${command}`);
}

interface PromptDecisionOptions {
  includeCoreConfig?: boolean;
  includePlaywright?: boolean;
  includeCodegraph?: boolean;
  includeGraphify?: boolean;
  includeOpenspec?: boolean;
}

async function applyInteractivePrompts(options: CliOptions, promptOptions: PromptDecisionOptions = {}): Promise<void> {
  if (options.json || options.yes || !process.stdin.isTTY || !process.stdout.isTTY) return;
  if (!Object.values(promptOptions).some(Boolean)) return;
  const config = promptOptions.includeCoreConfig ? await readOpenCodeConfig(options.opencodeHome) : { value: undefined };
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  try {
    await applyPromptDecisions(options, config.value, (prompt) => rl.question(prompt), promptOptions);
  } finally {
    rl.close();
  }
}

async function applyPromptDecisions(options: CliOptions, config: Record<string, any> | undefined, ask: PromptAsk, promptOptions: PromptDecisionOptions = {}): Promise<void> {
  const includeCoreConfig = promptOptions.includeCoreConfig ?? false;
  const includePlaywright = promptOptions.includePlaywright ?? true;
  const includeCodegraph = promptOptions.includeCodegraph ?? true;
  const includeGraphify = promptOptions.includeGraphify ?? true;
  const includeOpenspec = promptOptions.includeOpenspec ?? false;
  if (includeCoreConfig && !options.setDefaultRose) {
    const currentDefault = config?.default_agent;
    const prompt = currentDefault && currentDefault !== "rose"
      ? `OpenCode default_agent is ${String(currentDefault)}. Replace it with rose? [y/N] `
      : "Set rose as OpenCode default_agent? [Y/n] ";
    const answer = (await ask(prompt)).trim().toLowerCase();
    options.setDefaultRose = currentDefault && currentDefault !== "rose" ? answer === "y" || answer === "yes" : answer !== "n" && answer !== "no";
    options.forceDefaultAgent = Boolean(currentDefault && currentDefault !== "rose" && options.setDefaultRose);
  }
  if (includeCoreConfig && !options.model && !config?.agent?.rose?.model) {
    const model = (await ask("Model for agent.rose.model (provider/model, blank to skip): ")).trim();
    if (model) options.model = model;
  }
  if (includePlaywright && !options.enablePlaywright && !options.skipPlaywright) {
    const answer = (await ask("Enable optional Playwright MCP? [y/N] ")).trim().toLowerCase();
    options.enablePlaywright = answer === "y" || answer === "yes";
    options.skipPlaywright = !options.enablePlaywright;
  }
  if (includeCodegraph && !options.enableCodegraph && !options.skipCodegraph) {
    const answer = (await ask("Install optional CodeGraph for OpenCode via `npm install -g @colbymchenry/codegraph@latest` and `codegraph install --target=opencode --yes`? Requires restarting OpenCode. [y/N] ")).trim().toLowerCase();
    options.enableCodegraph = answer === "y" || answer === "yes";
    options.skipCodegraph = !options.enableCodegraph;
  }
  if (includeGraphify && !options.enableGraphify && !options.skipGraphify && !options.registerGraphifySkill) {
    const answer = (await ask("Install optional Graphify CLI via `uv tool install graphifyy`? This downloads dependencies and writes uv user-global tool paths; global skill registration remains a separate later approval. [y/N] ")).trim().toLowerCase();
    options.enableGraphify = answer === "y" || answer === "yes";
    options.skipGraphify = !options.enableGraphify;
  }
  if (includeOpenspec && !options.enableOpenspec && !options.skipOpenspec && options.projectRoot) {
    const answer = (await ask(`Install/configure OpenSpec in exact project root ${options.projectRoot} via \`npm install -g @fission-ai/openspec@latest\` and \`openspec init/update\`? Requires Node.js 20.19+. [y/N] `)).trim().toLowerCase();
    options.enableOpenspec = answer === "y" || answer === "yes";
    options.skipOpenspec = !options.enableOpenspec;
  }
}

function parseOptions(argv: string[]): CliOptions {
  const options: CliOptions = {
    dryRun: false,
    opencodeHome: path.join(os.homedir(), ".config", "opencode"),
    ailiHome: defaultAiliHome(),
    plugins: []
  };
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    switch (arg) {
      case "--dry-run":
        options.dryRun = true;
        break;
      case "--opencode-home":
        options.opencodeHome = requireValue(argv, ++index, arg);
        break;
      case "--opencode":
        options.opencode = true;
        break;
      case "--profile":
        options.profile = requireValue(argv, ++index, arg) as InstallOptions["profile"];
        break;
      case "--skill":
        (options.skills ??= []).push(requireValue(argv, ++index, arg));
        break;
      case "--skill-group":
        (options.skillGroups ??= []).push(requireValue(argv, ++index, arg));
        break;
      case "--aili-home":
        options.ailiHome = requireValue(argv, ++index, arg);
        break;
      case "--yes":
        options.yes = true;
        break;
      case "--set-default-rose":
        options.setDefaultRose = true;
        break;
      case "--model":
        options.model = requireValue(argv, ++index, arg);
        break;
      case "--force-default-agent":
        options.forceDefaultAgent = true;
        break;
      case "--force-model":
        options.forceModel = true;
        break;
      case "--skip-opencode-config":
        options.skipOpenCodeConfig = true;
        break;
      case "--enable-playwright":
        options.enablePlaywright = true;
        break;
      case "--skip-playwright":
        options.skipPlaywright = true;
        break;
      case "--enable-codegraph":
        options.enableCodegraph = true;
        break;
      case "--skip-codegraph":
        options.skipCodegraph = true;
        break;
      case "--enable-graphify":
        options.enableGraphify = true;
        break;
      case "--skip-graphify":
        options.skipGraphify = true;
        break;
      case "--register-graphify-skill":
        options.registerGraphifySkill = true;
        break;
      case "--enable-openspec":
        options.enableOpenspec = true;
        break;
      case "--skip-openspec":
        options.skipOpenspec = true;
        break;
      case "--skip-officecli":
        options.skipOfficecli = true;
        break;
      case "--enable-officecli":
        options.enableOfficecli = true;
        break;
      case "--skip-mempalace":
        options.skipMempalace = true;
        break;
      case "--enable-mempalace":
        options.enableMempalace = true;
        break;
      case "--reconcile-retired-skills":
        options.reconcileRetiredSkills = true;
        break;
      case "--project-root":
        options.projectRoot = requireValue(argv, ++index, arg);
        break;
      case "--plugin":
        options.plugins.push(requireValue(argv, ++index, arg));
        break;
      case "--json":
        options.json = true;
        break;
      case "--help":
      case "-h":
        options.help = true;
        break;
      default:
        throw new Error(`Unknown option: ${arg}`);
    }
  }
  return options;
}

function selectedProfile(options: CliOptions): "default" | "pi" | "opencode" {
  if (options.profile && !["default", "pi", "opencode"].includes(options.profile)) return options.profile as never;
  if (options.opencode && options.profile && options.profile !== "opencode") return options.profile as never;
  return options.profile ?? (options.opencode ? "opencode" : "default");
}

function requireValue(argv: string[], index: number, flag: string): string {
  const value = argv[index];
  if (!value || value.startsWith("--")) throw new Error(`Missing value for ${flag}`);
  return value;
}

function print(value: unknown, json?: boolean): void {
  if (json) {
    console.log(JSON.stringify(value, null, 2));
  } else {
    console.log(JSON.stringify(value, null, 2));
  }
}

function printHelp(): void {
  console.log(`rose-aili install|update|doctor [options]

Options:
  --dry-run
  --profile <default|pi|opencode>
  --opencode (legacy alias for --profile opencode)
  --skill <skill-name> (repeatable)
  --skill-group <research|specialized-dev> (repeatable)
  --opencode-home <path>
  --aili-home <path>
  --yes
  --set-default-rose
  --model <provider/model>
  --force-default-agent
  --force-model
  --skip-opencode-config
  --enable-playwright | --skip-playwright
  --enable-codegraph | --skip-codegraph
  --enable-graphify | --skip-graphify (CLI install only; existing uv required)
  --register-graphify-skill (separate global ~/.agents/skills/graphify registration)
  --enable-openspec | --skip-openspec (OpenSpec installs only when explicitly enabled)
  --enable-officecli | --skip-officecli (OfficeCLI is default-selected but separately approval-gated)
  --enable-mempalace | --skip-mempalace (MemPalace is default-selected; installation and MCP configuration stay separate)
  --reconcile-retired-skills (explicitly reconcile proven installer-owned retired entries)
  --project-root <absolute-canonical-path> (required with --enable-openspec)
  --plugin <name>
  --json`);
}

if (process.argv[1] && isMainModule(process.argv[1], fileURLToPath(import.meta.url))) {
  main(process.argv.slice(2)).catch((error: unknown) => {
    const message = error instanceof Error ? error.message : String(error);
    console.error(message);
    process.exitCode = 1;
  });
}

function isMainModule(argvPath: string, modulePath: string): boolean {
  try {
    return realpathSync(argvPath) === realpathSync(modulePath);
  } catch {
    return path.resolve(argvPath) === path.resolve(modulePath);
  }
}

export { applyPromptDecisions, parseOptions };
