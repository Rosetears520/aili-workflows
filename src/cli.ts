#!/usr/bin/env node
import os from "node:os";
import path from "node:path";
import readline from "node:readline/promises";
import { readOpenCodeConfig } from "./config.js";
import { runDoctor } from "./doctor.js";
import { defaultAiliHome, InstallOptions, runInstall, validateOpenCodeHome } from "./installer.js";

interface CliOptions extends InstallOptions {
  help?: boolean;
}

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
  if (command === "install" || command === "update" || command === "doctor") {
    validateOpenCodeHome(options.opencodeHome);
  }
  if (command === "install" || command === "update") {
    if (command === "install") {
      await applyInteractivePrompts(options);
    }
    const summary = await runInstall(command, options);
    print(summary, options.json);
    return;
  }
  if (command === "doctor") {
    const summary = await runDoctor({ opencodeHome: options.opencodeHome, ailiHome: options.ailiHome });
    print(summary, options.json);
    if (!summary.ok) process.exitCode = 1;
    return;
  }
  throw new Error(`Unknown command: ${command}`);
}

async function applyInteractivePrompts(options: CliOptions): Promise<void> {
  if (options.json || options.yes || !process.stdin.isTTY || !process.stdout.isTTY) return;
  const config = await readOpenCodeConfig(options.opencodeHome);
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  try {
    if (!options.setDefaultRose) {
      const currentDefault = config.value?.default_agent;
      const prompt = currentDefault && currentDefault !== "rose"
        ? `OpenCode default_agent is ${String(currentDefault)}. Replace it with rose? [y/N] `
        : "Set rose as OpenCode default_agent? [Y/n] ";
      const answer = (await rl.question(prompt)).trim().toLowerCase();
      options.setDefaultRose = currentDefault && currentDefault !== "rose" ? answer === "y" || answer === "yes" : answer !== "n" && answer !== "no";
      options.forceDefaultAgent = Boolean(currentDefault && currentDefault !== "rose" && options.setDefaultRose);
    }
    if (!options.model && !config.value?.agent?.rose?.model) {
      const model = (await rl.question("Model for agent.rose.model (provider/model, blank to skip): ")).trim();
      if (model) options.model = model;
    }
    if (!options.enablePlaywright && !options.skipPlaywright) {
      const answer = (await rl.question("Enable optional Playwright MCP? [y/N] ")).trim().toLowerCase();
      options.enablePlaywright = answer === "y" || answer === "yes";
      options.skipPlaywright = !options.enablePlaywright;
    }
  } finally {
    rl.close();
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
      case "--enable-playwright":
        options.enablePlaywright = true;
        break;
      case "--skip-playwright":
        options.skipPlaywright = true;
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
  --opencode-home <path>
  --aili-home <path>
  --yes
  --set-default-rose
  --model <provider/model>
  --force-default-agent
  --force-model
  --enable-playwright | --skip-playwright
  --plugin <name>
  --json`);
}

main(process.argv.slice(2)).catch((error: unknown) => {
  const message = error instanceof Error ? error.message : String(error);
  console.error(message);
  process.exitCode = 1;
});

export { parseOptions };
