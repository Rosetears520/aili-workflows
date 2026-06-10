#!/usr/bin/env node
import { chmod, stat } from "node:fs/promises";
import path from "node:path";

const cliPath = path.join(process.cwd(), "dist", "cli.js");
const current = await stat(cliPath);
await chmod(cliPath, current.mode | 0o111);
