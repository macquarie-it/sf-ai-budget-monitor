import { readFile } from "node:fs/promises";

const text = { type: "string", required: true };
const number = { type: "number", required: true };

export const contracts = {
  dashboard_shell: {
    renderer: "shell", cardinality: "one",
    fields: {
      brandTitle: text, brandSubtitle: text, environmentLabel: text, accountName: text,
      pageOverline: text, titleLine1: text, titleEmphasis: text, lede: text,
    },
  },
  monitoring_status: { renderer: "status", cardinality: "one", fields: { message: text } },
  credits_consumed: metricContract(),
  projected_month: metricContract(),
  active_identities: metricContract(),
  chart_menu: {
    renderer: "radio_group", cardinality: "many",
    fields: { chartId: text, label: text, description: text, displayOrder: number },
  },
  credit_burn: {
    renderer: "line_chart", cardinality: "many",
    fields: {
      rangeLabel: text, position: number, value: number, kicker: text, title: text, description: text,
    },
  },
  agent_bar_chart: {
    renderer: "bar_chart", cardinality: "many",
    fields: {
      label: text, sublabel: text, value: number, changePercent: number,
      kicker: text, title: text, description: text,
    },
  },
  usage_scatter: {
    renderer: "scatter_plot", cardinality: "many",
    fields: {
      label: text, xValue: number, yValue: number, size: number, color: text,
      kicker: text, title: text, description: text,
    },
  },
  service_pie_chart: {
    renderer: "pie_chart", cardinality: "many",
    fields: {
      label: text, value: number, credits: number, color: text,
      kicker: text, title: text, description: text,
    },
  },
  activity_heatmap: {
    renderer: "heatmap", cardinality: "many",
    fields: { rowLabel: text, columnLabel: text, value: number, kicker: text, title: text, description: text },
  },
  dashboard_footer: {
    renderer: "footer", cardinality: "one", fields: { leftText: text, rightText: text },
  },
};

function metricContract() {
  return {
    renderer: "metric", cardinality: "one",
    fields: { eyebrow: text, value: text, suffix: text, trend: text, note: text, tone: text },
  };
}

export async function parseDashboardConfig(configPath) {
  const source = await readFile(configPath, "utf8");
  const lines = source.split(/\r?\n/);
  const components = [];
  let current = null;

  for (const [index, line] of lines.entries()) {
    const componentMatch = line.match(/^\s*--\s*@component\s+([a-z][a-z0-9_]*)\s*$/i);
    if (componentMatch) {
      if (current) throw new Error(`Nested @component at line ${index + 1}.`);
      current = { id: componentMatch[1].toLowerCase(), renderer: null, cardinality: null, sql: [] };
      continue;
    }

    if (!current) continue;

    if (/^\s*--\s*@end-component\s*$/i.test(line)) {
      current.sql = current.sql.join("\n").trim();
      if (!current.sql) throw new Error(`Component ${current.id} has no SQL.`);
      components.push(current);
      current = null;
      continue;
    }

    const rendererMatch = line.match(/^\s*--\s*@renderer\s+([a-z][a-z0-9_]*)\s*$/i);
    const cardinalityMatch = line.match(/^\s*--\s*@cardinality\s+(one|many)\s*$/i);
    if (rendererMatch) current.renderer = rendererMatch[1].toLowerCase();
    if (cardinalityMatch) current.cardinality = cardinalityMatch[1].toLowerCase();
    current.sql.push(line);
  }

  if (current) throw new Error(`Component ${current.id} is missing @end-component.`);

  const duplicate = components.find((item, index) => components.findIndex(({ id }) => id === item.id) !== index);
  if (duplicate) throw new Error(`Duplicate component id: ${duplicate.id}.`);

  const expectedIds = Object.keys(contracts);
  const actualIds = components.map(({ id }) => id);
  for (const id of expectedIds) {
    if (!actualIds.includes(id)) throw new Error(`Required component ${id} is missing from the SQL config.`);
  }
  for (const component of components) {
    const contract = contracts[component.id];
    if (!contract) throw new Error(`Unknown component ${component.id}; add an application contract before using it.`);
    if (component.renderer !== contract.renderer) {
      throw new Error(`${component.id} must use renderer ${contract.renderer}, received ${component.renderer ?? "none"}.`);
    }
    if (component.cardinality && component.cardinality !== contract.cardinality) {
      throw new Error(`${component.id} has an outdated result-shape marker. Remove the @cardinality line; the app now handles that rule for the DBA.`);
    }
    component.cardinality = contract.cardinality;
  }

  return components;
}

export function rowsFromSnowOutput(output, componentId) {
  const trimmed = output.trim();
  let parsed;
  try {
    parsed = JSON.parse(trimmed);
  } catch {
    const start = trimmed.indexOf("[");
    const end = trimmed.lastIndexOf("]");
    if (start < 0 || end <= start) {
      throw new Error(`${componentId}: Snowflake CLI did not return JSON rows. Output: ${trimmed.slice(0, 300)}`);
    }
    parsed = JSON.parse(trimmed.slice(start, end + 1));
  }

  if (!Array.isArray(parsed)) {
    parsed = parsed.data ?? parsed.rows ?? parsed.rowset;
  }
  if (!Array.isArray(parsed)) throw new Error(`${componentId}: unsupported Snowflake JSON response shape.`);
  return parsed.map(normalizeRow);
}

export function buildDataset(componentResults, generatedAt = new Date().toISOString()) {
  const components = {};
  for (const { id, renderer, cardinality, rows } of componentResults) {
    const coercedRows = validateAndCoerceRows(id, rows);
    components[id] = {
      renderer,
      data: cardinality === "one" ? coercedRows[0] : coercedRows,
    };
  }

  const dataset = { version: 1, generatedAt, components };
  validateDataset(dataset);
  return dataset;
}

export function validateDataset(dataset) {
  if (!dataset || dataset.version !== 1 || !dataset.components) {
    throw new Error("Dashboard data must contain version 1 and a components object.");
  }
  if (Number.isNaN(Date.parse(dataset.generatedAt))) throw new Error("Dashboard data has an invalid generatedAt timestamp.");

  for (const [id, contract] of Object.entries(contracts)) {
    const component = dataset.components[id];
    if (!component) throw new Error(`Dashboard data is missing ${id}.`);
    if (component.renderer !== contract.renderer) throw new Error(`${id}: renderer must be ${contract.renderer}.`);
    const rows = contract.cardinality === "one" ? [component.data] : component.data;
    validateAndCoerceRows(id, rows, false);
  }
  return dataset;
}

function validateAndCoerceRows(id, rows, coerce = true) {
  const contract = contracts[id];
  if (!Array.isArray(rows)) throw new Error(`${id}: expected an array of result rows.`);
  if (contract.cardinality === "one" && rows.length !== 1) {
    throw new Error(`${id} is a summary component. Its SQL should return one summary result, but it returned ${rows.length}. Try SUM(), COUNT(), MAX(), or another summary calculation.`);
  }
  if (contract.cardinality === "many" && rows.length < 1) {
    throw new Error(`${id} has nothing to display because its SQL returned no data.`);
  }

  return rows.map((originalRow, index) => {
    if (!originalRow || typeof originalRow !== "object" || Array.isArray(originalRow)) {
      throw new Error(`${id} row ${index + 1}: expected an object.`);
    }
    const row = { ...originalRow };
    for (const [field, rule] of Object.entries(contract.fields)) {
      let value = row[field];
      if (value === null || value === undefined) throw new Error(`${id} row ${index + 1}: missing ${field}.`);
      if (rule.type === "number" && typeof value !== "number") {
        const converted = Number(value);
        if (coerce && Number.isFinite(converted)) value = converted;
      }
      if (typeof value !== rule.type || (rule.type === "number" && !Number.isFinite(value))) {
        throw new Error(`${id} row ${index + 1}: ${field} must be a ${rule.type}.`);
      }
      row[field] = value;
    }
    return row;
  });
}

function normalizeRow(row) {
  if (!row || typeof row !== "object" || Array.isArray(row)) return row;
  return Object.fromEntries(Object.entries(row).map(([key, value]) => [toCamelCase(key), value]));
}

function toCamelCase(value) {
  return value.toLowerCase().replace(/_([a-z0-9])/g, (_, character) => character.toUpperCase());
}
