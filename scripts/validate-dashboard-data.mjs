import { readFile } from "node:fs/promises";
import { resolve } from "node:path";
import { parseDashboardConfig, validateDataset } from "./dashboard-data-lib.mjs";

const configPath = resolve("config/dashboard.sql");
const dataPath = resolve("src/generated/dashboard-data.json");

const components = await parseDashboardConfig(configPath);
const dataset = JSON.parse(await readFile(dataPath, "utf8"));
validateDataset(dataset);

const configuredIds = new Set(components.map(({ id }) => id));
const generatedIds = Object.keys(dataset.components);
for (const id of generatedIds) {
  if (!configuredIds.has(id)) throw new Error(`Generated data contains unconfigured component ${id}.`);
}

console.log(`Dashboard contracts verified: ${generatedIds.length} components`);
