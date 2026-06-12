import { lstat, mkdir, readFile, rename, unlink, writeFile } from "node:fs/promises";
import path from "node:path";
import { applyEdits, modify, parse, ParseError, printParseErrorCode } from "jsonc-parser";

export interface ConfigOptions {
  opencodeHome: string;
  dryRun: boolean;
  setDefaultRose?: boolean;
  forceDefaultAgent?: boolean;
  model?: string;
  forceModel?: boolean;
  playwrightConfig?: Record<string, unknown>;
}

export interface ConfigResult {
  configPath: string;
  changed: boolean;
  backupPath?: string;
  actions: string[];
  skipped: string[];
}

export interface DcpConfigOptions {
  opencodeHome: string;
  dryRun: boolean;
}

export async function configPathFor(opencodeHome: string): Promise<string> {
  const jsonc = path.join(opencodeHome, "opencode.jsonc");
  const json = path.join(opencodeHome, "opencode.json");
  if (await pathExists(jsonc)) return jsonc;
  if (await pathExists(json)) return json;
  return json;
}

export async function dcpConfigPathFor(opencodeHome: string): Promise<string> {
  const jsonc = path.join(opencodeHome, "dcp.jsonc");
  const json = path.join(opencodeHome, "dcp.json");
  if (await pathExists(jsonc)) return jsonc;
  if (await pathExists(json)) return json;
  return jsonc;
}

export function parseConfigText(text: string, label = "OpenCode config"): unknown {
  const errors: ParseError[] = [];
  const value = parse(text, errors, { allowTrailingComma: true, disallowComments: false });
  if (errors.length > 0) {
    const error = errors[0];
    throw new Error(`${label} is invalid JSONC at offset ${error.offset}: ${printParseErrorCode(error.error)}`);
  }
  return value ?? {};
}

export async function readOpenCodeConfig(opencodeHome: string): Promise<{ configPath: string; text: string; value: any; exists: boolean }> {
  const configPath = await configPathFor(opencodeHome);
  const existsOnDisk = await pathExists(configPath);
  const text = existsOnDisk ? await readFile(configPath, "utf8") : "{}\n";
  const value = parseConfigText(text, configPath);
  return { configPath, text, value, exists: existsOnDisk };
}

export async function mergeOpenCodeConfig(options: ConfigOptions): Promise<ConfigResult> {
  if (requestsConfigWrite(options)) {
    await assertWritableConfigTarget(await configPathFor(options.opencodeHome));
  }
  const current = await readOpenCodeConfig(options.opencodeHome);
  let text = current.text;
  const actions: string[] = [];
  const skipped: string[] = [];
  const formattingOptions = { insertSpaces: true, tabSize: 2, eol: "\n" };

  if (options.setDefaultRose) {
    const existingDefault = current.value?.default_agent;
    if (existingDefault === undefined || existingDefault === "rose" || options.forceDefaultAgent) {
      text = applyEdits(text, modify(text, ["default_agent"], "rose", { formattingOptions }));
      actions.push(existingDefault === undefined ? "set default_agent to rose" : "kept default_agent as rose");
    } else {
      skipped.push(`preserved existing default_agent ${String(existingDefault)}`);
    }
  }

  if (options.model) {
    const existingModel = current.value?.agent?.rose?.model;
    if (existingModel === undefined || options.forceModel) {
      text = applyEdits(text, modify(text, ["agent", "rose", "model"], options.model, { formattingOptions }));
      actions.push(existingModel === undefined ? "set agent.rose.model" : "overwrote agent.rose.model");
    } else {
      skipped.push("preserved existing agent.rose.model");
    }
  }

  if (options.playwrightConfig) {
    text = applyEdits(text, modify(text, ["mcp", "playwright"], options.playwrightConfig, { formattingOptions }));
    actions.push("set mcp.playwright");
  }

  const changed = text !== current.text;
  if (changed) {
    await assertWritableConfigTarget(current.configPath);
  }
  if (!changed || options.dryRun) {
    return { configPath: current.configPath, changed, actions, skipped };
  }

  await mkdir(path.dirname(current.configPath), { recursive: true });
  let backupPath: string | undefined;
  if (current.exists) {
    backupPath = `${current.configPath}.backup.${timestamp()}`;
    await writeFile(backupPath, current.text, { encoding: "utf8", flag: "wx" });
  }
  await atomicWriteFile(current.configPath, text);
  return { configPath: current.configPath, changed, backupPath, actions, skipped };
}

export async function mergeDcpConfig(options: DcpConfigOptions): Promise<ConfigResult> {
  const configPath = await dcpConfigPathFor(options.opencodeHome);
  await assertWritableConfigTarget(configPath);
  const existsOnDisk = await pathExists(configPath);
  const currentText = existsOnDisk ? await readFile(configPath, "utf8") : "{}\n";
  parseConfigText(currentText, configPath);

  let text = currentText;
  const formattingOptions = { insertSpaces: true, tabSize: 2, eol: "\n" };
  const entries: Array<{ path: Array<string>; value: string | number | boolean }> = [
    { path: ["enabled"], value: true },
    { path: ["pruneNotification"], value: "minimal" },
    { path: ["pruneNotificationType"], value: "toast" },
    { path: ["turnProtection", "enabled"], value: true },
    { path: ["turnProtection", "turns"], value: 4 },
    { path: ["compress", "mode"], value: "range" },
    { path: ["compress", "permission"], value: "allow" },
    { path: ["compress", "showCompression"], value: false },
    { path: ["compress", "minContextLimit"], value: "65%" },
    { path: ["compress", "maxContextLimit"], value: "85%" },
    { path: ["compress", "summaryBuffer"], value: false },
    { path: ["compress", "nudgeFrequency"], value: 4 },
    { path: ["compress", "iterationNudgeThreshold"], value: 12 },
    { path: ["compress", "nudgeForce"], value: "soft" },
    { path: ["compress", "protectTags"], value: true },
    { path: ["compress", "protectUserMessages"], value: false },
    { path: ["strategies", "deduplication", "enabled"], value: true },
    { path: ["strategies", "purgeErrors", "enabled"], value: true },
    { path: ["strategies", "purgeErrors", "turns"], value: 6 }
  ];

  for (const entry of entries) {
    text = applyEdits(text, modify(text, entry.path, entry.value, { formattingOptions }));
  }

  const changed = text !== currentText;
  const actions = changed ? ["wrote recommended DCP config"] : ["kept recommended DCP config"];
  const skipped: string[] = [];
  if (!changed || options.dryRun) {
    return { configPath, changed, actions, skipped };
  }

  await mkdir(path.dirname(configPath), { recursive: true });
  let backupPath: string | undefined;
  if (existsOnDisk) {
    backupPath = `${configPath}.backup.${timestamp()}`;
    await writeFile(backupPath, currentText, { encoding: "utf8", flag: "wx" });
  }
  await atomicWriteFile(configPath, text);
  return { configPath, changed, backupPath, actions, skipped };
}

function requestsConfigWrite(options: ConfigOptions): boolean {
  return Boolean(options.setDefaultRose || options.model || options.playwrightConfig);
}

async function assertWritableConfigTarget(configPath: string): Promise<void> {
  let stats;
  try {
    stats = await lstat(configPath);
  } catch (error: any) {
    if (error?.code === "ENOENT") return;
    throw error;
  }
  if (stats.isSymbolicLink() || !stats.isFile()) {
    throw new Error(`Refusing to write OpenCode config because it is not a regular file: ${configPath}`);
  }
}

async function atomicWriteFile(filePath: string, text: string): Promise<void> {
  const tempPath = path.join(path.dirname(filePath), `.${path.basename(filePath)}.tmp.${process.pid}.${Date.now()}`);
  try {
    await writeFile(tempPath, text, { encoding: "utf8", flag: "wx" });
    await rename(tempPath, filePath);
  } catch (error) {
    await unlink(tempPath).catch(() => undefined);
    throw error;
  }
}

async function pathExists(filePath: string): Promise<boolean> {
  try {
    await lstat(filePath);
    return true;
  } catch (error: any) {
    if (error?.code === "ENOENT") return false;
    throw error;
  }
}

function timestamp(): string {
  const now = new Date();
  const pad = (value: number, width = 2) => String(value).padStart(width, "0");
  return `${now.getFullYear()}${pad(now.getMonth() + 1)}${pad(now.getDate())}${pad(now.getHours())}${pad(now.getMinutes())}${pad(now.getSeconds())}${pad(now.getMilliseconds(), 3)}.${process.pid}`;
}
