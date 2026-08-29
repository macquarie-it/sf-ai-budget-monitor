import { readFile, stat } from "node:fs/promises";
import { resolve } from "node:path";

const target = resolve("streamlit_app/frontend/index.html");
const html = await readFile(target, "utf8");
const info = await stat(target);

if (/<script\b[^>]*\bsrc=/i.test(html) || /<link\b[^>]*rel=["']stylesheet["']/i.test(html)) {
  throw new Error("Streamlit build is not self-contained: external local assets were found.");
}

if (!html.includes("Snowflake AI Credit Control") || info.size < 10_000) {
  throw new Error("Streamlit build looks incomplete.");
}

console.log(`Streamlit bundle verified: ${target} (${Math.round(info.size / 1024)} KB, single HTML file)`);

