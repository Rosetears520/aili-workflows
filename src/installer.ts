import { spawn } from "node:child_process";
import { constants, realpathSync, statSync } from "node:fs";
import { access, stat } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { configPathFor, mergeOpenCodeConfig } from "./config.js";
import {
  fingerprintPath,
  GRAPHIFY_CLI_INSTALL_COMMAND,
  GraphifyCliPreflight,
  graphifyGlobalSkillRoots,
  GRAPHIFY_SKILL_INSTALL_COMMAND,
  GRAPHIFY_SKILL_RELATIVE_PATH,
  inspectGraphifyCliPreflight,
  inspectGraphifySkillInventory,
  treeContainsSymlink,
  verifyGraphifyCatalog
} from "./graphify.js";
import { ComponentManifest, findMcp, findPlugin, loadManifest, resolveSkillSelection, validateManifestAllowlist } from "./manifest.js";
import { MemPalaceInstallSummary, MemPalaceMcpPlan, planMemPalaceMcpConfiguration, runMemPalaceInstall } from "./mempalace.js";
import { OfficeCliInstallSummary, runOfficeCliInstall } from "./officecli.js";

export interface InstallOptions {
  dryRun: boolean;
  opencode?: boolean;
  profile?: InstallProfile;
  skills?: string[];
  skillGroups?: string[];
  opencodeHome: string;
  ailiHome: string;
  yes?: boolean;
  setDefaultRose?: boolean;
  model?: string;
  forceDefaultAgent?: boolean;
  forceModel?: boolean;
  skipOpenCodeConfig?: boolean;
  enablePlaywright?: boolean;
  skipPlaywright?: boolean;
  enableCodegraph?: boolean;
  skipCodegraph?: boolean;
  enableGraphify?: boolean;
  skipGraphify?: boolean;
  registerGraphifySkill?: boolean;
  enableOpenspec?: boolean;
  skipOpenspec?: boolean;
  skipOfficecli?: boolean;
  enableOfficecli?: boolean;
  skipMempalace?: boolean;
  enableMempalace?: boolean;
  reconcileRetiredSkills?: boolean;
  projectRoot?: string;
  plugins: string[];
  json?: boolean;
}

export type InstallProfile = "default" | "pi" | "opencode";

type OptionalStatus = "configured" | "planned" | "skipped" | "failed" | "unverified";

interface OptionalSummary {
  status: OptionalStatus;
  command?: string;
  reason?: string;
  recovery?: string;
  nextStep?: string;
}

type GraphifyStageStatus = "installed" | "registered" | "planned" | "skipped" | "pending" | "failed" | "conflict";

interface GraphifyStageSummary {
  status: GraphifyStageStatus;
  command: string;
  exitCode?: number | null;
  reason?: string;
  observedVersion?: string;
  path?: string;
  nextStep?: string;
  route?: { name: string; location: string };
}

interface GraphifyOperationPacket {
  command: string;
  effects: string[];
  refusalResult: string;
  approval: "fresh-exact-separate";
}

interface GraphifySummary {
  ownership: "upstream";
  cli: GraphifyStageSummary;
  globalSkill: GraphifyStageSummary;
  operations: {
    cliInstall: GraphifyOperationPacket;
    globalSkillRegistration: GraphifyOperationPacket;
  };
  inventory: {
    targetPath: string;
    versionStampPath: string;
    referencesPath: string;
    candidateVersionStampPaths: string[];
    existingVersionStampPaths: string[];
    ambiguousPaths: string[];
    currentProjectOpenCodePath: string;
    uvToolDirectory?: string;
    uvBinDirectory?: string;
  };
}

export interface InstallSummary {
  command: "install" | "update";
  dryRun: boolean;
  profile: InstallProfile;
  selectedSkills: string[];
  ailiHome: string;
  opencodeHome: string;
  componentInstall: {
    status: "planned" | "completed";
    scope: "skills" | "pi" | "opencode";
    code: number | null;
    retiredSkillReconciliation: Array<{
      name: string;
      target: string;
      action: "absent" | "planned-unlink" | "unlinked" | "preserved";
      reason: string;
    }>;
  };
  officecli: OfficeCliInstallSummary;
  mempalace: MemPalaceInstallSummary;
  mempalaceMcp: MemPalaceMcpPlan;
  config: Awaited<ReturnType<typeof mergeOpenCodeConfig>>;
  mcp: { playwright: "configured" | "planned" | "skipped" };
  optionalDecisions: Array<{ name: string; status: "configured" | "planned" | "skipped"; nextStep?: string; reason?: string }>;
  codegraph: OptionalSummary;
  graphify: GraphifySummary;
  openspec: OptionalSummary;
  externalToolOperations: Array<{
    name: "OfficeCLI" | "Playwright" | "CodeGraph" | "Graphify" | "OpenSpec" | "MemPalace";
    status: "planned" | "skipped" | "unavailable";
    approval: "fresh-exact-separate";
    command?: string;
    reason: string;
    refusalResult: string;
  }>;
  plugins: Array<{ name: string; status: "skipped" | "unverified"; reason: string; source?: string }>;
}

const CODEGRAPH_INSTALL_COMMAND = ["npm", "install", "-g", "@colbymchenry/codegraph@latest"];
const CODEGRAPH_OPENCODE_COMMAND = ["codegraph", "install", "--target=opencode", "--yes"];
const CODEGRAPH_RESTART_STEP = "Restart OpenCode so it loads the CodeGraph OpenCode integration.";
const GRAPHIFY_REGISTER_STEP = "rose-aili install --opencode --register-graphify-skill";
const OPENSPEC_INSTALL_COMMAND = ["npm", "install", "-g", "@fission-ai/openspec@latest"];
const OPENSPEC_DETECT_COMMAND = ["openspec", "--version"];
const MIN_OPENSPEC_NODE = [20, 19, 0] as const;

export function defaultAiliHome(): string {
  const here = path.dirname(fileURLToPath(import.meta.url));
  return path.resolve(here, "..");
}

export async function runInstall(command: "install" | "update", rawOptions: InstallOptions): Promise<InstallSummary> {
  validateOpenCodeScope(rawOptions);
  const profile = resolveProfile(rawOptions);
  const options = {
    ...rawOptions,
    profile,
    opencode: profile === "opencode",
    opencodeHome: profile === "opencode" ? validateOpenCodeHome(rawOptions.opencodeHome) : rawOptions.opencodeHome
  };
  if (options.skipGraphify && (options.enableGraphify || options.registerGraphifySkill)) {
    throw new Error("--skip-graphify cannot be combined with a Graphify install or registration flag.");
  }
  if (options.skipMempalace && options.enableMempalace) {
    throw new Error("--skip-mempalace cannot be combined with --enable-mempalace.");
  }
  if (options.enableGraphify && options.registerGraphifySkill) {
    throw new Error("Graphify CLI installation and global skill registration require separate invocations and approvals.");
  }
  if (options.projectRoot) options.projectRoot = validateExactProjectRoot(options.projectRoot);
  if (options.enableOpenspec && !options.skipOpenspec && !options.projectRoot) {
    throw new Error("--enable-openspec requires --project-root <path>.");
  }
  const manifest = await loadManifest(options.ailiHome);
  await validateManifestAllowlist(options.ailiHome, manifest);
  const selectedSkills = resolveSkillSelection(manifest, options.skills, options.skillGroups);
  if (options.opencode) await validateInstallerSources(options.ailiHome);
  if (profile === "pi") await validatePiInstallerSources(options.ailiHome);
  const playwright = findMcp(manifest, "playwright");
  const shouldSyncOpenCodeConfig = Boolean(options.opencode && !options.skipOpenCodeConfig);
  const shouldConfigurePlaywright = Boolean(shouldSyncOpenCodeConfig && options.enablePlaywright && !options.skipPlaywright);
  const pluginStatuses = validatePlugins(manifest, options.plugins);
  const unknown = pluginStatuses.find((plugin) => plugin.status === "unverified" && !plugin.source);
  if (unknown) {
    throw new Error(`Unknown plugin is not manifest-defined and will not be installed: ${unknown.name}`);
  }

  const configRequest = {
    opencodeHome: options.opencodeHome,
    dryRun: options.dryRun,
    setDefaultRose: shouldSyncOpenCodeConfig && options.setDefaultRose !== false,
    forceDefaultAgent: options.forceDefaultAgent,
    model: options.model,
    forceModel: options.forceModel,
    playwrightConfig: shouldConfigurePlaywright ? playwright?.config : undefined
  };
  const shouldMergeConfig = shouldSyncOpenCodeConfig && Boolean(configRequest.setDefaultRose || options.model || shouldConfigurePlaywright);
  const preflightConfig = !shouldSyncOpenCodeConfig
    ? await skippedOpenCodeConfig(options)
    : shouldMergeConfig
    ? await mergeOpenCodeConfig({ ...configRequest, dryRun: true })
    : await mergeOpenCodeConfig(configRequest);

  const componentInstall = await runCompatibilityInstaller(
    options,
    selectedSkills.map((skill) => skill.name),
    manifest.retiredSkills?.map((skill) => skill.name) ?? []
  );
  const config = shouldMergeConfig && !options.dryRun ? await mergeOpenCodeConfig(configRequest) : preflightConfig;
  const officecli = await runOfficeCliInstall({
    ailiHome: options.ailiHome,
    opencodeHome: options.opencodeHome,
    dryRun: options.dryRun,
    enabled: options.enableOfficecli,
    skip: options.skipOfficecli
  });
  const mempalace = await runMemPalaceInstall({
    ailiHome: options.ailiHome,
    dryRun: options.dryRun,
    enabled: options.enableMempalace,
    skip: options.skipMempalace
  });
  const mempalaceMcp = await planMemPalaceMcpConfiguration({
    ailiHome: options.ailiHome,
    adapter: profile,
    readiness: mempalace.readiness
  });
  const codegraph = await runCodeGraphInstall(options);
  const graphify = await runGraphifyInstall(options);
  const openspec = await runOpenSpecInstall(options);

  return {
    command,
    dryRun: options.dryRun,
    profile,
    selectedSkills: selectedSkills.map((skill) => skill.name),
    ailiHome: options.ailiHome,
    opencodeHome: options.opencodeHome,
    componentInstall,
    officecli,
    mempalace,
    mempalaceMcp,
    config,
    mcp: { playwright: shouldConfigurePlaywright ? (options.dryRun ? "planned" : "configured") : "skipped" },
    optionalDecisions: buildOptionalDecisions(command, options, shouldConfigurePlaywright, shouldSyncOpenCodeConfig),
    codegraph,
    graphify,
    openspec,
    externalToolOperations: externalToolOperations(profile, options),
    plugins: pluginStatuses
  };
}

function resolveProfile(options: InstallOptions): InstallProfile {
  if (options.profile && !["default", "pi", "opencode"].includes(options.profile)) {
    throw new Error(`Unknown profile: ${options.profile}`);
  }
  if (options.opencode && options.profile && options.profile !== "opencode") {
    throw new Error("--opencode is a legacy alias for --profile opencode and cannot be combined with another profile.");
  }
  return options.profile ?? (options.opencode ? "opencode" : "default");
}

function externalToolOperations(profile: InstallProfile, options: InstallOptions): InstallSummary["externalToolOperations"] {
  const refusal = "The tool remains unavailable or unchanged; Core Skill installation continues.";
  const operations: InstallSummary["externalToolOperations"] = [
    {
      name: "OfficeCLI",
      status: options.skipOfficecli ? "skipped" : "planned",
      approval: "fresh-exact-separate",
      command: "npm install --prefix ~/.agents/tools/officecli --no-save --no-package-lock @officecli/officecli@1.0.143",
      reason: options.skipOfficecli ? "OfficeCLI explicitly skipped." : "Default-selected; requires a separate exact install approval.",
      refusalResult: refusal
    },
    {
      name: "MemPalace",
      status: options.skipMempalace ? "skipped" : "planned",
      approval: "fresh-exact-separate",
      command: "uv tool install mempalace==3.6.0",
      reason: options.skipMempalace ? "MemPalace explicitly skipped." : "Default-selected; exact-version installation and MCP configuration are separate approval-gated operations.",
      refusalResult: "Durable-memory capabilities remain unavailable; Core Skill installation continues."
    }
  ];
  if (profile === "opencode") {
    operations.push(
      {
        name: "Playwright",
        status: options.skipPlaywright ? "skipped" : "planned",
        approval: "fresh-exact-separate",
        command: "npx -y @playwright/mcp@0.0.75 --caps=testing,storage",
        reason: options.skipPlaywright ? "Playwright explicitly skipped." : "Default-selected; MCP configuration requires a separate exact approval.",
        refusalResult: refusal
      },
      {
        name: "CodeGraph",
        status: options.skipCodegraph ? "skipped" : "planned",
        approval: "fresh-exact-separate",
        command: `${CODEGRAPH_INSTALL_COMMAND.join(" ")} && ${CODEGRAPH_OPENCODE_COMMAND.join(" ")}`,
        reason: options.skipCodegraph ? "CodeGraph explicitly skipped." : "Default-selected; installation and OpenCode setup require a separate exact approval.",
        refusalResult: refusal
      },
      {
        name: "Graphify",
        status: options.skipGraphify ? "skipped" : "planned",
        approval: "fresh-exact-separate",
        command: GRAPHIFY_CLI_INSTALL_COMMAND.join(" "),
        reason: options.skipGraphify ? "Graphify explicitly skipped." : "Default-selected; upstream CLI installation and global skill registration are separately approved operations.",
        refusalResult: refusal
      },
      {
        name: "OpenSpec",
        status: options.skipOpenspec ? "skipped" : "planned",
        approval: "fresh-exact-separate",
        command: "npm install -g @fission-ai/openspec@latest && openspec init|update",
        reason: options.skipOpenspec ? "OpenSpec explicitly skipped." : "Default-selected when an exact project root is supplied; installation and project initialization remain separate operations.",
        refusalResult: refusal
      }
    );
  }
  return operations;
}

async function skippedOpenCodeConfig(options: InstallOptions): Promise<InstallSummary["config"]> {
  return {
    configPath: options.opencode ? await configPathFor(options.opencodeHome) : path.join(options.opencodeHome, "opencode.json"),
    changed: false,
    actions: [],
    skipped: [options.opencode ? "OpenCode config sync explicitly skipped" : "OpenCode integration not enabled; installed shared skills only"]
  };
}

function buildOptionalDecisions(command: "install" | "update", options: InstallOptions, shouldConfigurePlaywright: boolean, shouldSyncOpenCodeConfig: boolean): InstallSummary["optionalDecisions"] {
  const decisions: InstallSummary["optionalDecisions"] = [];
  if (!options.opencode) {
    decisions.push({
      name: "OpenCode integration",
      status: "skipped",
      reason: "default installation scope is shared skills only",
      nextStep: `rose-aili ${command} --opencode`
    });
  }
  if (options.opencode && !shouldSyncOpenCodeConfig) {
    decisions.push({
      name: "OpenCode config",
      status: "skipped",
      reason: "explicitly skipped",
      nextStep: `rose-aili ${command} --opencode`
    });
  }
  if (options.opencode && !options.model) {
    decisions.push({
      name: "rose model override",
      status: "skipped",
      reason: "not configured in this install; omit this to use OpenCode's default model behavior",
      nextStep: "rose-aili install --opencode --model <provider/model>"
    });
  }
  if (options.opencode && !shouldConfigurePlaywright) {
    decisions.push({
      name: "Playwright MCP",
      status: "skipped",
      reason: options.skipPlaywright ? "explicitly skipped" : options.skipOpenCodeConfig ? "OpenCode config sync explicitly skipped" : "not configured in this install",
      nextStep: "rose-aili install --opencode --enable-playwright"
    });
  }
  if (options.opencode && !options.enableCodegraph) {
    decisions.push({
      name: "CodeGraph",
      status: "skipped",
      reason: options.skipCodegraph ? "explicitly skipped" : "not configured in this install",
      nextStep: "rose-aili install --opencode --enable-codegraph"
    });
  }
  if (options.opencode && !options.enableGraphify && !options.registerGraphifySkill) {
    decisions.push({
      name: "Graphify",
      status: "skipped",
      reason: options.skipGraphify ? "explicitly skipped" : "not installed or registered in this invocation",
      nextStep: "rose-aili install --opencode --enable-graphify"
    });
  } else if (options.enableGraphify && !options.registerGraphifySkill) {
    decisions.push({
      name: "Graphify global skill",
      status: "skipped",
      reason: "global agents-skill registration requires a different fresh exact approval",
      nextStep: GRAPHIFY_REGISTER_STEP
    });
  }
  if (options.opencode && (!options.enableOpenspec || options.skipOpenspec)) {
    decisions.push({
      name: "OpenSpec",
      status: "skipped",
      reason: options.skipOpenspec ? "explicitly skipped" : "not configured in this install",
      nextStep: "rose-aili install --opencode --enable-openspec --project-root <absolute-canonical-path>"
    });
  }
  return decisions;
}

async function runGraphifyInstall(options: InstallOptions): Promise<GraphifySummary> {
  const home = process.env.HOME || os.homedir();
  const targetPath = path.join(home, GRAPHIFY_SKILL_RELATIVE_PATH);
  const versionStampPath = path.join(targetPath, ".graphify_version");
  const referencesPath = path.join(targetPath, "references");
  const currentProjectOpenCodePath = path.join(process.cwd(), ".opencode");
  const cliCommand = GRAPHIFY_CLI_INSTALL_COMMAND.join(" ");
  const skillCommand = GRAPHIFY_SKILL_INSTALL_COMMAND.join(" ");
  const operations: GraphifySummary["operations"] = {
    cliInstall: {
      command: cliCommand,
      effects: ["network dependency resolution", "uv user-global tool installation", "Graphify CLI executable installation"],
      refusalResult: "Graphify remains absent or unchanged; core AILI installation continues.",
      approval: "fresh-exact-separate"
    },
    globalSkillRegistration: {
      command: skillCommand,
      effects: [`write upstream skill files under ${targetPath}`, "refresh version stamps at other existing upstream Graphify skill destinations"],
      refusalResult: "The Graphify CLI state is preserved and global skill registration remains pending.",
      approval: "fresh-exact-separate"
    }
  };
  const baseInventory: GraphifySummary["inventory"] = {
    targetPath,
    versionStampPath,
    referencesPath,
    candidateVersionStampPaths: graphifyGlobalSkillRoots(home).map((root) => path.join(root, ".graphify_version")),
    existingVersionStampPaths: [],
    ambiguousPaths: [],
    currentProjectOpenCodePath
  };

  if (options.skipGraphify || (!options.enableGraphify && !options.registerGraphifySkill)) {
    return {
      ownership: "upstream",
      cli: { status: "skipped", command: cliCommand, reason: options.skipGraphify ? "Graphify explicitly skipped." : "Graphify requires an explicit enable flag." },
      globalSkill: { status: "skipped", command: skillCommand, path: targetPath, reason: "Graphify global skill registration was not approved." },
      operations,
      inventory: baseInventory
    };
  }

  try {
    const skillInventory = await inspectGraphifySkillInventory(home);
    const inventory: GraphifySummary["inventory"] = {
      ...baseInventory,
      existingVersionStampPaths: skillInventory.existingVersionStampPaths,
      ambiguousPaths: skillInventory.ambiguousPaths
    };
    if (options.dryRun) {
      return {
        ownership: "upstream",
        cli: { status: "planned", command: cliCommand, reason: "Requires its own dependency/network/user-global-write approval." },
        globalSkill: skillInventory.ambiguousPaths.length > 0
          ? { status: "conflict", command: skillCommand, path: targetPath, reason: `Ambiguous existing Graphify skill paths: ${skillInventory.ambiguousPaths.join(", ")}` }
          : { status: "planned", command: skillCommand, path: targetPath, reason: "Requires a different global-skill-write approval after CLI installation." },
        operations,
        inventory
      };
    }

    const run = (command: string, args: string[], cwd?: string) => spawnOptionalCapture(command, args, options, cwd);
    const preflight = await inspectGraphifyCliPreflight(run);
    inventory.uvToolDirectory = preflight.uvToolDirectory;
    inventory.uvBinDirectory = preflight.uvBinDirectory;
    if (options.enableGraphify) return installGraphifyCli(preflight, inventory, operations, run);
    return registerGraphifySkill(preflight, skillInventory, inventory, operations, run);
  } catch (error: unknown) {
    const reason = `Graphify preflight or verification failed without fallback: ${error instanceof Error ? error.message : String(error)}`;
    return {
      ownership: "upstream",
      cli: { status: "conflict", command: cliCommand, reason },
      globalSkill: { status: "conflict", command: skillCommand, path: targetPath, reason },
      operations,
      inventory: baseInventory
    };
  }
}

async function installGraphifyCli(
  preflight: GraphifyCliPreflight,
  inventory: GraphifySummary["inventory"],
  operations: GraphifySummary["operations"],
  run: (command: string, args: string[], cwd?: string) => Promise<{ code: number | null; detail: string; stdout: string }>
): Promise<GraphifySummary> {
  const cliCommand = GRAPHIFY_CLI_INSTALL_COMMAND.join(" ");
  const skillCommand = GRAPHIFY_SKILL_INSTALL_COMMAND.join(" ");
  const pendingSkill: GraphifyStageSummary = {
    status: "pending",
    command: skillCommand,
    path: inventory.targetPath,
    reason: "Global agents-skill registration requires a different fresh exact approval.",
    nextStep: GRAPHIFY_REGISTER_STEP
  };
  if (preflight.status === "prerequisite-missing" || preflight.status === "conflict") {
    return {
      ownership: "upstream",
      cli: { status: preflight.status === "conflict" ? "conflict" : "failed", command: cliCommand, reason: preflight.reason, observedVersion: preflight.observedVersion },
      globalSkill: pendingSkill,
      operations,
      inventory
    };
  }
  if (preflight.status === "installed") {
    return {
      ownership: "upstream",
      cli: { status: "installed", command: cliCommand, reason: "Existing uv-managed graphifyy installation preserved; no reinstall or upgrade ran.", observedVersion: preflight.observedVersion },
      globalSkill: pendingSkill,
      operations,
      inventory
    };
  }

  const installed = await run(GRAPHIFY_CLI_INSTALL_COMMAND[0], [...GRAPHIFY_CLI_INSTALL_COMMAND.slice(1)]);
  if (installed.code !== 0) {
    return {
      ownership: "upstream",
      cli: { status: "failed", command: cliCommand, exitCode: installed.code, reason: installed.detail || `command exited with ${installed.code ?? "unknown status"}` },
      globalSkill: pendingSkill,
      operations,
      inventory
    };
  }
  const verified = await inspectGraphifyCliPreflight(run);
  inventory.uvToolDirectory = verified.uvToolDirectory;
  inventory.uvBinDirectory = verified.uvBinDirectory;
  if (verified.status !== "installed") {
    return {
      ownership: "upstream",
      cli: { status: "failed", command: cliCommand, exitCode: installed.code, reason: verified.reason || "uv install exited successfully but Graphify ownership/version verification failed", observedVersion: verified.observedVersion },
      globalSkill: pendingSkill,
      operations,
      inventory
    };
  }
  return {
    ownership: "upstream",
    cli: { status: "installed", command: cliCommand, exitCode: installed.code, observedVersion: verified.observedVersion },
    globalSkill: pendingSkill,
    operations,
    inventory
  };
}

async function registerGraphifySkill(
  preflight: GraphifyCliPreflight,
  skillInventory: Awaited<ReturnType<typeof inspectGraphifySkillInventory>>,
  inventory: GraphifySummary["inventory"],
  operations: GraphifySummary["operations"],
  run: (command: string, args: string[], cwd?: string) => Promise<{ code: number | null; detail: string; stdout: string }>
): Promise<GraphifySummary> {
  const cliCommand = GRAPHIFY_CLI_INSTALL_COMMAND.join(" ");
  const skillCommand = GRAPHIFY_SKILL_INSTALL_COMMAND.join(" ");
  const cli: GraphifyStageSummary = preflight.status === "installed"
    ? { status: "installed", command: cliCommand, observedVersion: preflight.observedVersion }
    : { status: preflight.status === "conflict" ? "conflict" : "failed", command: cliCommand, reason: preflight.reason, observedVersion: preflight.observedVersion };
  if (preflight.status !== "installed") {
    return {
      ownership: "upstream",
      cli,
      globalSkill: { status: "failed", command: skillCommand, path: inventory.targetPath, reason: "A verified uv-managed Graphify CLI is required before global skill registration." },
      operations,
      inventory
    };
  }
  if (skillInventory.ambiguousPaths.length > 0) {
    return {
      ownership: "upstream",
      cli,
      globalSkill: { status: "conflict", command: skillCommand, path: inventory.targetPath, reason: `Ambiguous existing Graphify skill paths: ${skillInventory.ambiguousPaths.join(", ")}` },
      operations,
      inventory
    };
  }

  if (skillInventory.target.valid) {
    const catalog = await verifyGraphifyCatalog(run, skillInventory.target.skillPath);
    return {
      ownership: "upstream",
      cli,
      globalSkill: catalog.ok
        ? { status: "registered", command: skillCommand, path: inventory.targetPath, reason: "Existing valid upstream global skill preserved; registration command did not run.", route: catalog.route }
        : { status: "failed", command: skillCommand, path: inventory.targetPath, reason: catalog.reason },
      operations,
      inventory
    };
  }

  const beforeOpenCode = await fingerprintPath(inventory.currentProjectOpenCodePath);
  if (await treeContainsSymlink(inventory.currentProjectOpenCodePath)) {
    return {
      ownership: "upstream",
      cli,
      globalSkill: { status: "conflict", command: skillCommand, path: inventory.targetPath, reason: `Cannot prove an unchanged current-project .opencode tree containing symlinks: ${inventory.currentProjectOpenCodePath}` },
      operations,
      inventory
    };
  }
  const installed = await run(GRAPHIFY_SKILL_INSTALL_COMMAND[0], [...GRAPHIFY_SKILL_INSTALL_COMMAND.slice(1)]);
  const afterOpenCode = await fingerprintPath(inventory.currentProjectOpenCodePath);
  if (beforeOpenCode !== afterOpenCode) {
    return {
      ownership: "upstream",
      cli,
      globalSkill: { status: "failed", command: skillCommand, exitCode: installed.code, path: inventory.targetPath, reason: `Unexpected current-project .opencode change detected at ${inventory.currentProjectOpenCodePath}` },
      operations,
      inventory
    };
  }
  if (installed.code !== 0) {
    return {
      ownership: "upstream",
      cli,
      globalSkill: { status: "failed", command: skillCommand, exitCode: installed.code, path: inventory.targetPath, reason: installed.detail || `command exited with ${installed.code ?? "unknown status"}` },
      operations,
      inventory
    };
  }

  const verifiedInventory = await inspectGraphifySkillInventory(process.env.HOME || os.homedir());
  inventory.existingVersionStampPaths = verifiedInventory.existingVersionStampPaths;
  inventory.ambiguousPaths = verifiedInventory.ambiguousPaths;
  const referencesReported = /(?:^|\s)references(?:\s|$)/imu.test(installed.stdout);
  if (!verifiedInventory.target.valid || verifiedInventory.ambiguousPaths.length > 0 || (referencesReported && !verifiedInventory.target.referencesPresent)) {
    const reasons = [
      ...verifiedInventory.target.issues,
      ...verifiedInventory.ambiguousPaths.filter((item) => item !== verifiedInventory.target.root).map((item) => `ambiguous refreshed path: ${item}`),
      ...(referencesReported && !verifiedInventory.target.referencesPresent ? ["installer reported references but no regular references sidecar was found"] : [])
    ];
    return {
      ownership: "upstream",
      cli,
      globalSkill: { status: "failed", command: skillCommand, exitCode: installed.code, path: inventory.targetPath, reason: reasons.join("; ") || "upstream skill files did not validate" },
      operations,
      inventory
    };
  }
  const catalog = await verifyGraphifyCatalog(run, verifiedInventory.target.skillPath);
  return {
    ownership: "upstream",
    cli,
    globalSkill: catalog.ok
      ? { status: "registered", command: skillCommand, exitCode: installed.code, path: inventory.targetPath, route: catalog.route }
      : { status: "failed", command: skillCommand, exitCode: installed.code, path: inventory.targetPath, reason: catalog.reason },
    operations,
    inventory
  };
}

async function runCodeGraphInstall(options: InstallOptions): Promise<OptionalSummary> {
  const installCommand = CODEGRAPH_INSTALL_COMMAND.join(" ");
  const opencodeCommand = CODEGRAPH_OPENCODE_COMMAND.join(" ");
  const command = `${installCommand} && ${opencodeCommand}`;
  if (!options.enableCodegraph || options.skipCodegraph) {
    return { status: "skipped", command, reason: "CodeGraph is explicit opt-in only; run rose-aili install --opencode --enable-codegraph." };
  }
  if (options.dryRun) return { status: "planned", command, nextStep: CODEGRAPH_RESTART_STEP };
  const installResult = await spawnOptional(CODEGRAPH_INSTALL_COMMAND[0], CODEGRAPH_INSTALL_COMMAND.slice(1), options);
  if (installResult.code !== 0) {
    return {
      status: "failed",
      command: installCommand,
      reason: installResult.detail || `command exited with ${installResult.code ?? "unknown status"}`,
      recovery: "Install CodeGraph manually with: npm install -g @colbymchenry/codegraph@latest"
    };
  }
  const opencodeResult = await spawnOptional(CODEGRAPH_OPENCODE_COMMAND[0], CODEGRAPH_OPENCODE_COMMAND.slice(1), options);
  if (opencodeResult.code !== 0) {
    return {
      status: "failed",
      command: opencodeCommand,
      reason: opencodeResult.detail || `command exited with ${opencodeResult.code ?? "unknown status"}`,
      recovery: "Run CodeGraph OpenCode setup manually with: codegraph install --target=opencode --yes, then restart OpenCode."
    };
  }
  return { status: "configured", command, nextStep: CODEGRAPH_RESTART_STEP };
}

async function runOpenSpecInstall(options: InstallOptions): Promise<OptionalSummary> {
  if (!options.enableOpenspec || options.skipOpenspec) {
    return {
      status: "skipped",
      command: "rose-aili install --opencode --enable-openspec --project-root <absolute-canonical-path>",
      reason: options.skipOpenspec ? "OpenSpec explicitly skipped." : "OpenSpec is explicit opt-in only and requires an exact project root."
    };
  }
  if (!supportsOpenSpecNode(process.versions.node)) {
    return {
      status: "failed",
      command: OPENSPEC_INSTALL_COMMAND.join(" "),
      reason: `OpenSpec requires Node.js 20.19.0 or higher; current Node.js is ${process.versions.node}.`,
      recovery: "Upgrade Node.js to 20.19.0+ and rerun: rose-aili install --opencode --enable-openspec"
    };
  }
  if (!options.projectRoot) throw new Error("--enable-openspec requires --project-root <path>.");
  const projectCommand = await hasOpenSpecProject(options.projectRoot) ? "update" : "init";
  const command = `${OPENSPEC_INSTALL_COMMAND.join(" ")} && openspec ${projectCommand}`;
  if (options.dryRun) return { status: "planned", command };
  const installed = await isOpenSpecInstalled(options);
  const installResult = installed ? { code: 0, detail: "" } : await spawnOptional(OPENSPEC_INSTALL_COMMAND[0], OPENSPEC_INSTALL_COMMAND.slice(1), options);
  if (installResult.code !== 0) {
    return {
      status: "failed",
      command: OPENSPEC_INSTALL_COMMAND.join(" "),
      reason: installResult.detail || `command exited with ${installResult.code ?? "unknown status"}`,
      recovery: "Install OpenSpec manually with: npm install -g @fission-ai/openspec@latest"
    };
  }
  const projectResult = await spawnOptional("openspec", [projectCommand], options, options.projectRoot);
  if (projectResult.code !== 0) {
    return {
      status: "failed",
      command: `openspec ${projectCommand}`,
      reason: projectResult.detail || `command exited with ${projectResult.code ?? "unknown status"}`,
      recovery: `Run manually inside the target project: openspec ${projectCommand}`
    };
  }
  return { status: "configured", command: installed ? `openspec ${projectCommand}` : command };
}

async function isOpenSpecInstalled(options: InstallOptions): Promise<boolean> {
  const result = await spawnOptionalCapture(OPENSPEC_DETECT_COMMAND[0], OPENSPEC_DETECT_COMMAND.slice(1), options);
  return result.code === 0;
}

function supportsOpenSpecNode(version: string): boolean {
  const parts = version.split(".").map((part) => Number.parseInt(part, 10));
  return parts[0] > MIN_OPENSPEC_NODE[0]
    || (parts[0] === MIN_OPENSPEC_NODE[0] && parts[1] > MIN_OPENSPEC_NODE[1])
    || (parts[0] === MIN_OPENSPEC_NODE[0] && parts[1] === MIN_OPENSPEC_NODE[1] && parts[2] >= MIN_OPENSPEC_NODE[2]);
}

async function hasOpenSpecProject(cwd: string): Promise<boolean> {
  for (const name of ["openspec", "openspec.json", "openspec.yaml", "openspec.yml"] as const) {
    try {
      const marker = await stat(path.join(cwd, name));
      if (name === "openspec" ? marker.isDirectory() : marker.isFile()) return true;
    } catch {
      // keep checking known OpenSpec markers
    }
  }
  return false;
}

function spawnOptional(command: string, args: string[], options: InstallOptions, cwd?: string): Promise<{ code: number | null; detail: string }> {
  return spawnOptionalCapture(command, args, options, cwd).then(({ code, detail }) => ({ code, detail }));
}

function spawnOptionalCapture(command: string, args: string[], options: InstallOptions, cwd?: string): Promise<{ code: number | null; detail: string; stdout: string }> {
  return new Promise((resolve) => {
    let stdout = "";
    let stderr = "";
    const env = sanitizedOptionalEnv(options);
    if (!env.PATH) {
      resolve({ code: null, detail: `${command} command not found in sanitized PATH`, stdout });
      return;
    }
    const child = spawn(command, args, {
      cwd,
      stdio: ["ignore", "pipe", "pipe"],
      env
    });
    child.stdout?.setEncoding("utf8");
    child.stdout?.on("data", (chunk: string) => {
      stdout += chunk;
    });
    child.stderr?.setEncoding("utf8");
    child.stderr?.on("data", (chunk: string) => {
      stderr += chunk;
    });
    child.on("error", (error: NodeJS.ErrnoException) => {
      resolve({ code: null, detail: error.code === "ENOENT" ? `${command} command not found` : error.message, stdout });
    });
    child.on("close", (code) => {
      resolve({ code, detail: stderr.trim(), stdout: stdout.trim() });
    });
  });
}

function sanitizedOptionalEnv(options: InstallOptions): NodeJS.ProcessEnv {
  return {
    HOME: process.env.HOME || os.homedir(),
    PATH: sanitizedOptionalPath(process.env.PATH ?? "/usr/bin:/bin:/usr/sbin:/sbin"),
    OPENCODE_HOME: options.opencodeHome,
    OPENCODE_ALLOW_CUSTOM_HOME: "yes",
    AILI_ALLOW_PACKAGE_HOME: "yes"
  };
}

function sanitizedOptionalPath(rawPath: string): string {
  const cwd = path.resolve(process.cwd());
  const tempDir = path.resolve(os.tmpdir());
  const entries = rawPath.split(path.delimiter).filter((entry) => {
    if (!entry || !path.isAbsolute(entry)) return false;
    const resolved = path.resolve(entry);
    return !isPathOrDescendant(resolved, cwd) && !isPathOrDescendant(resolved, tempDir);
  });
  return entries.join(path.delimiter);
}

function isPathOrDescendant(candidate: string, parent: string): boolean {
  const relative = path.relative(parent, candidate);
  return relative === "" || (relative !== "" && !relative.startsWith("..") && !path.isAbsolute(relative));
}

async function runCompatibilityInstaller(options: InstallOptions, selectedSkills: string[], retiredSkillNames: string[]): Promise<InstallSummary["componentInstall"]> {
  const script = path.join(options.ailiHome, "scripts", "install_opencode.sh");
  await access(script, constants.F_OK);
  const mode = await isGitRepository(options.ailiHome) ? "selective" : "copy";
  const args = [script, "--mode", mode, "--aili-home", options.ailiHome, "--opencode-home", options.opencodeHome];
  args.push("--profile", options.profile ?? "default");
  for (const skill of selectedSkills) args.push("--skill", skill);
  if (options.reconcileRetiredSkills) args.push("--reconcile-retired-skills");
  args.push("--skip-officecli");
  if (options.dryRun) args.push("--dry-run");
  const result = await spawnInstaller(args, options);
  return {
    status: options.dryRun ? "planned" : "completed",
    scope: options.profile === "opencode" ? "opencode" : options.profile === "pi" ? "pi" : "skills",
    code: result.code,
    retiredSkillReconciliation: parseRetiredSkillReconciliation(result.stdout, retiredSkillNames, options)
  };
}

function spawnInstaller(args: string[], options: InstallOptions): Promise<{ code: number; stdout: string }> {
  return new Promise((resolve, reject) => {
    let stdout = "";
    let stderr = "";
    const child = spawn("/bin/bash", args, {
      stdio: ["ignore", "pipe", "pipe"],
      env: {
        HOME: process.env.HOME || os.homedir(),
        PATH: "/usr/bin:/bin:/usr/sbin:/sbin",
        OPENCODE_HOME: options.opencodeHome,
        OPENCODE_ALLOW_CUSTOM_HOME: "yes",
        AILI_ALLOW_PACKAGE_HOME: "yes",
        AILI_INSTALLER_DRY_RUN: options.dryRun ? "1" : "0"
      }
    });
    if (child.stdout) {
      child.stdout.setEncoding("utf8");
      child.stdout.on("data", (chunk: string) => {
        stdout += chunk;
        if (!options.json) process.stdout.write(chunk);
      });
    }
    if (child.stderr) {
      child.stderr.setEncoding("utf8");
      child.stderr.on("data", (chunk: string) => {
        stderr += chunk;
        if (!options.json) process.stderr.write(chunk);
      });
    }
    child.on("error", reject);
    child.on("close", (code) => {
      if (code === 0) resolve({ code, stdout });
      else {
        const detail = options.json ? stderr.trim() : "";
        reject(new Error(`Compatibility installer failed with exit code ${code ?? "unknown"}${detail ? `: ${detail}` : ""}`));
      }
    });
  });
}

function parseRetiredSkillReconciliation(
  stdout: string,
  retiredSkillNames: string[],
  options: Pick<InstallOptions, "dryRun" | "reconcileRetiredSkills">
): InstallSummary["componentInstall"]["retiredSkillReconciliation"] {
  const summaryLine = stdout.trim().split(/\r?\n/).at(-1);
  if (!summaryLine) throw new Error("Compatibility installer returned no summary.");
  let raw: unknown;
  try {
    raw = JSON.parse(summaryLine);
  } catch {
    throw new Error("Compatibility installer returned an invalid summary.");
  }
  const entries = typeof raw === "object" && raw !== null
    ? (raw as { retired_skill_reconciliation?: unknown }).retired_skill_reconciliation
    : undefined;
  if (!Array.isArray(entries)) throw new Error("Compatibility installer summary omitted retired-skill reconciliation.");
  const actions = new Set(["absent", "planned-unlink", "unlinked", "preserved"] as const);
  const parsed = entries.map((entry) => {
    if (typeof entry !== "object" || entry === null) throw new Error("Compatibility installer returned an invalid retired-skill reconciliation entry.");
    const candidate = entry as Record<string, unknown>;
    if (typeof candidate.name !== "string" || typeof candidate.target !== "string" || typeof candidate.reason !== "string" || typeof candidate.action !== "string" || !actions.has(candidate.action as "absent" | "planned-unlink" | "unlinked" | "preserved")) {
      throw new Error("Compatibility installer returned an invalid retired-skill reconciliation entry.");
    }
    const action = candidate.action as "absent" | "planned-unlink" | "unlinked" | "preserved";
    if (!options.reconcileRetiredSkills && (action === "planned-unlink" || action === "unlinked")) {
      throw new Error("Compatibility installer attempted retired-skill reconciliation without explicit selection.");
    }
    if (options.dryRun && action === "unlinked") {
      throw new Error("Compatibility installer reported a retired-skill unlink during dry-run.");
    }
    return {
      name: candidate.name,
      target: candidate.target,
      action,
      reason: candidate.reason
    };
  });
  const expected = new Set(retiredSkillNames);
  const received = new Set(parsed.map((entry) => entry.name));
  if (expected.size !== retiredSkillNames.length || parsed.length !== expected.size || received.size !== expected.size || [...expected].some((name) => !received.has(name))) {
    throw new Error("Compatibility installer returned an incomplete or unexpected retired-skill reconciliation.");
  }
  return parsed;
}

async function isGitRepository(ailiHome: string): Promise<boolean> {
  try {
    await access(path.join(ailiHome, ".git"), constants.F_OK);
    return true;
  } catch {
    return false;
  }
}

async function validateInstallerSources(ailiHome: string): Promise<void> {
  await Promise.all([
    access(path.join(ailiHome, "generated", "opencode", "AGENTS.md"), constants.F_OK),
    access(path.join(ailiHome, "generated", "opencode", "provenance.json"), constants.F_OK)
  ]);
}

async function validatePiInstallerSources(ailiHome: string): Promise<void> {
  await Promise.all([
    access(path.join(ailiHome, "generated", "pi", "AGENTS.md"), constants.F_OK),
    access(path.join(ailiHome, "generated", "pi", "provenance.json"), constants.F_OK),
    access(path.join(ailiHome, "generated", "pi", "installation-contract.json"), constants.F_OK)
  ]);
}

function validateOpenCodeScope(options: InstallOptions): void {
  if (options.opencode || options.profile === "opencode") return;
  const requested = [
    [options.setDefaultRose, "--set-default-rose"],
    [options.model, "--model"],
    [options.forceDefaultAgent, "--force-default-agent"],
    [options.forceModel, "--force-model"],
    [options.skipOpenCodeConfig, "--skip-opencode-config"],
    [options.enablePlaywright, "--enable-playwright"],
    [options.skipPlaywright, "--skip-playwright"],
    [options.enableCodegraph, "--enable-codegraph"],
    [options.skipCodegraph, "--skip-codegraph"],
    [options.enableGraphify, "--enable-graphify"],
    [options.skipGraphify, "--skip-graphify"],
    [options.registerGraphifySkill, "--register-graphify-skill"],
    [options.enableOpenspec, "--enable-openspec"],
    [options.skipOpenspec, "--skip-openspec"],
    [options.projectRoot, "--project-root"],
    [options.plugins.length > 0, "--plugin"]
  ].find(([enabled]) => Boolean(enabled));
  if (requested) throw new Error(`${requested[1]} requires --opencode because the default installation scope is shared skills only.`);
}

export function validateOpenCodeHome(opencodeHome: string): string {
  if (!opencodeHome) throw new Error("Refusing empty OPENCODE_HOME.");
  if (!path.isAbsolute(opencodeHome)) throw new Error(`Refusing relative OPENCODE_HOME: ${opencodeHome}`);
  const resolved = path.resolve(opencodeHome);
  if (resolved === path.parse(resolved).root) throw new Error(`Refusing unsafe OPENCODE_HOME: ${opencodeHome}`);
  if (resolved === path.resolve(os.homedir())) throw new Error(`Refusing unsafe OPENCODE_HOME: ${opencodeHome}`);
  if (resolved === path.resolve(os.tmpdir())) throw new Error(`Refusing unsafe OPENCODE_HOME: ${opencodeHome}`);
  return resolved;
}

export function validateExactProjectRoot(projectRoot: string): string {
  if (!projectRoot || !path.isAbsolute(projectRoot)) {
    throw new Error(`OpenSpec --project-root requires an absolute canonical directory: ${projectRoot || "<empty>"}`);
  }
  const resolved = path.resolve(projectRoot);
  let canonical: string;
  try {
    canonical = realpathSync(resolved);
  } catch {
    throw new Error(`OpenSpec --project-root requires an existing directory: ${projectRoot}`);
  }
  if (resolved !== canonical || !statSync(canonical).isDirectory()) {
    throw new Error(`Refusing ambiguous or symlinked OpenSpec project root: ${projectRoot}`);
  }
  for (const unsafe of [path.parse(canonical).root, path.resolve(os.homedir()), path.resolve(os.userInfo().homedir), path.resolve(os.tmpdir())]) {
    if (canonical === unsafe) throw new Error(`Refusing unsafe OpenSpec project root: ${projectRoot}`);
  }
  return canonical;
}

function validatePlugins(manifest: ComponentManifest, plugins: string[]): InstallSummary["plugins"] {
  return plugins.map((name) => {
    const plugin = findPlugin(manifest, name);
    if (!plugin) {
      return { name, status: "unverified", reason: "No manifest entry; not installed." };
    }
    return {
      name,
      status: "unverified",
      reason: plugin.install?.reason ?? "Plugin installation is not automated by this release.",
      source: plugin.source
    };
  });
}
