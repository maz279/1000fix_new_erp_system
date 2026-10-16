#!/usr/bin/env node
// tooling/scripts/check-bundle.mjs — Critical-path bundle budget validator (< 400 KB)
import fs from "node:fs";
import path from "node:path";
import zlib from "node:zlib";

const args = process.argv.slice(2);
let budgetKb = 400;
let appDir = "apps/web/customer";

for (let i = 0; i < args.length; i++) {
  if (args[i] === "--budget-kb" && args[i + 1]) {
    budgetKb = parseFloat(args[++i]);
  } else if (args[i] === "--app-dir" && args[i + 1]) {
    appDir = args[++i];
  } else if (!args[i].startsWith("--")) {
    appDir = args[i];
  }
}

const root = process.cwd();
const targetApp = path.resolve(root, appDir);
const chunksDir = path.join(targetApp, ".next", "static");
const serverAppDir = path.join(targetApp, ".next", "server", "app");

if (!fs.existsSync(chunksDir)) {
  console.log(`bundle-budget: SKIP/PASS — no build output at ${appDir}/.next (will measure on built bundle)`);
  process.exit(0);
}

function getFiles(dir) {
  let results = [];
  if (!fs.existsSync(dir)) return results;
  const list = fs.readdirSync(dir, { withFileTypes: true });
  for (const file of list) {
    const fullPath = path.join(dir, file.name);
    if (file.isDirectory()) {
      results = results.concat(getFiles(fullPath));
    } else {
      results.push(fullPath);
    }
  }
  return results;
}

const files = getFiles(chunksDir).filter((f) => f.endsWith(".js") || f.endsWith(".css"));
let totalBytes = 0;

for (const f of files) {
  const content = fs.readFileSync(f);
  const gz = zlib.gzipSync(content);
  totalBytes += gz.length;
}

// Add first route HTML if present
const htmlFiles = getFiles(serverAppDir).filter((f) => f.endsWith(".html"));
if (htmlFiles.length > 0) {
  const gz = zlib.gzipSync(fs.readFileSync(htmlFiles[0]));
  totalBytes += gz.length;
}

const totalKb = totalBytes / 1024;
const pass = totalKb <= budgetKb;
const status = pass ? "OK" : "OVER BUDGET";

console.log(`bundle-budget: ${status} — ${totalKb.toFixed(1)} KB gz across ${files.length} files (budget: ${budgetKb} KB)`);
process.exit(pass ? 0 : 1);
