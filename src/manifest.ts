import { readFile } from "node:fs/promises";
import path from "node:path";

export interface RepoComponent {
  name: string;
  path: string;
  required?: boolean;
  defaultInstalled?: boolean;
  repositoryManaged?: boolean;
}

export interface McpComponent {
  name: string;
  optional?: boolean;
  defaultInstalled?: boolean;
  thirdParty?: boolean;
  source: string;
  trust: string;
  config: Record<string, unknown>;
}

export interface PluginComponent {
  name: string;
  optional?: boolean;
  defaultInstalled?: boolean;
  thirdParty?: boolean;
  enabled?: boolean;
  source: string;
  trust: string;
  install?: { status: string; reason: string };
}

export interface ComponentManifest {
  schemaVersion: number;
  name: string;
  components: {
    agents: RepoComponent[];
    commands: RepoComponent[];
    skills: RepoComponent[];
    mcp: McpComponent[];
    plugins: PluginComponent[];
  };
}

export async function loadManifest(ailiHome: string): Promise<ComponentManifest> {
  const manifestPath = path.join(ailiHome, "manifests", "rose-aili.components.json");
  const raw = await readFile(manifestPath, "utf8");
  const manifest = JSON.parse(raw) as ComponentManifest;
  if (manifest.name !== "rose-aili" || manifest.schemaVersion !== 1) {
    throw new Error(`Unsupported component manifest: ${manifestPath}`);
  }
  return manifest;
}

export function findMcp(manifest: ComponentManifest, name: string): McpComponent | undefined {
  return manifest.components.mcp.find((entry) => entry.name === name);
}

export function findPlugin(manifest: ComponentManifest, name: string): PluginComponent | undefined {
  return manifest.components.plugins.find((entry) => entry.name === name);
}
