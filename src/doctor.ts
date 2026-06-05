import { constants } from "node:fs";
import { access } from "node:fs/promises";
import path from "node:path";
import { readOpenCodeConfig } from "./config.js";
import { loadManifest } from "./manifest.js";

export interface DoctorOptions {
  opencodeHome: string;
  ailiHome: string;
}

export interface DoctorSummary {
  ok: boolean;
  required: Array<{ type: string; name: string; installed: boolean }>;
  defaultAgent: string | null;
  roseModel: string | null;
  playwright: "configured" | "missing-optional";
  plugins: Array<{ name: string; status: "missing-optional" | "unverified" }>;
}

export async function runDoctor(options: DoctorOptions): Promise<DoctorSummary> {
  const manifest = await loadManifest(options.ailiHome);
  const required = [
    ...(await Promise.all(manifest.components.agents.filter((entry) => entry.required).map(async (entry) => ({ type: "agent", name: entry.name, installed: await exists(path.join(options.opencodeHome, "agents", `${entry.name}.md`)) })))),
    ...(await Promise.all(manifest.components.commands.filter((entry) => entry.required).map(async (entry) => ({ type: "command", name: entry.name, installed: await exists(path.join(options.opencodeHome, "commands", `${entry.name}.md`)) })))),
    ...(await Promise.all(manifest.components.skills.filter((entry) => entry.required).map(async (entry) => ({ type: "skill", name: entry.name, installed: await exists(path.join(options.opencodeHome, "skills", entry.name, "SKILL.md")) }))))
  ];
  const config = await readOpenCodeConfig(options.opencodeHome);
  const defaultAgent = typeof config.value?.default_agent === "string" ? config.value.default_agent : null;
  const roseModel = typeof config.value?.agent?.rose?.model === "string" ? config.value.agent.rose.model : null;
  const playwright = config.value?.mcp?.playwright ? "configured" : "missing-optional";
  return {
    ok: required.every((entry) => entry.installed),
    required,
    defaultAgent,
    roseModel,
    playwright,
    plugins: manifest.components.plugins.map((entry) => ({ name: entry.name, status: "missing-optional" }))
  };
}

async function exists(filePath: string): Promise<boolean> {
  try {
    await access(filePath, constants.F_OK);
    return true;
  } catch {
    return false;
  }
}
