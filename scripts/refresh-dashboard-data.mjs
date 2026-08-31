import { spawnSync } from "node:child_process";
import { mkdir, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { buildDataset, parseDashboardConfig, rowsFromSnowOutput } from "./dashboard-data-lib.mjs";

const options = parseArguments(process.argv.slice(2));
const configPath = resolve(options.config ?? "config/dashboard.sql");
const outputPath = resolve(options.output ?? "src/generated/dashboard-data.json");
const componentConfigs = await parseDashboardConfig(configPath);

if (options.dryRun) {
  console.log(`SQL config is valid: ${componentConfigs.length} components in ${configPath}`);
  for (const component of componentConfigs) {
    console.log(`- ${component.id} -> ${component.renderer} (${component.cardinality})`);
  }
  process.exit(0);
}

const results = componentConfigs.map((component) => {
  const args = ["sql", "--format", "JSON", "--silent", "--stdin"];
  if (options.connection) args.push("--connection", options.connection);
  for (const variable of options.variables) args.push("--variable", variable);

  console.log(`Querying ${component.id}...`);
  const execution = spawnSync("snow", args, {
    encoding: "utf8",
    input: component.sql,
    maxBuffer: 20 * 1024 * 1024,
  });

  if (execution.error) {
    throw new Error(`Could not run Snowflake CLI for ${component.id}: ${execution.error.message}`);
  }
  if (execution.status !== 0) {
    throw new Error(`${component.id} query failed:\n${execution.stderr || execution.stdout}`);
  }

  return {
    ...component,
    rows: rowsFromSnowOutput(execution.stdout, component.id),
  };
});

const dataset = buildDataset(results);
await mkdir(dirname(outputPath), { recursive: true });
await writeFile(outputPath, `${JSON.stringify(dataset, null, 2)}\n`, "utf8");
console.log(`Dashboard data written to ${outputPath}`);

function parseArguments(args) {
  const parsed = { connection: null, config: null, output: null, dryRun: false, variables: [] };
  for (let index = 0; index < args.length; index += 1) {
    const argument = args[index];
    if (argument === "--dry-run") {
      parsed.dryRun = true;
      continue;
    }
    const valueOptions = new Map([
      ["--connection", "connection"], ["-c", "connection"],
      ["--config", "config"], ["--output", "output"],
    ]);
    if (valueOptions.has(argument)) {
      const value = args[index + 1];
      if (!value || value.startsWith("--")) throw new Error(`${argument} requires a value.`);
      parsed[valueOptions.get(argument)] = value;
      index += 1;
      continue;
    }
    if (argument === "--variable" || argument === "-D") {
      const value = args[index + 1];
      if (!value || !value.includes("=")) throw new Error(`${argument} requires KEY=value.`);
      parsed.variables.push(value);
      index += 1;
      continue;
    }
    throw new Error(`Unknown argument: ${argument}`);
  }
  return parsed;
}
