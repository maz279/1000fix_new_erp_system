// PP7-M03 verification sweep — every portal route must: serve the nonce
// CSP + HSTS headers, stamp the nonce on its scripts, hydrate without a
// single console error or page error. Run: node sweep.mjs (from the a11y
// harness's playwright install).
import { chromium } from "@playwright/test";
import path from "node:path";
import fs from "node:fs";

const exe =
  process.env.CHROMIUM_EXECUTABLE_PATH ||
  path.join(process.env.USERPROFILE || process.env.HOME || ".",
    "AppData/Local/ms-playwright/chromium_headless_shell-1200/chrome-headless-shell-win64/chrome-headless-shell.exe");

const ROUTES = [
  ["corporate", 3001, ["/", "/estate", "/invoices", "/service-requests"]],
  ["customer", 3010, ["/", "/welcome", "/booking", "/tracking", "/devices", "/consent"]],
  ["analytics", 3012, ["/"]],
  ["seller", 3013, ["/", "/jobs", "/scorecard", "/settlements"]],
  ["brand", 3014, ["/", "/reconciliation"]],
  ["agent-console", 3015, ["/", "/conversation"]],
  ["partner", 3016, ["/", "/referrals", "/commissions"]],
  ["vendor", 3017, ["/", "/invoices"]],
];

const browser = await chromium.launch({ headless: true, ...(fs.existsSync(exe) ? { executablePath: exe } : {}) });
let pass = 0, fail = 0;
for (const [name, port, routes] of ROUTES) {
  for (const route of routes) {
    const page = await browser.newPage();
    const errs = [];
    page.on("console", (m) => { if (m.type() === "error") errs.push(m.text().slice(0, 120)); });
    page.on("pageerror", (e) => errs.push("PAGEERROR " + String(e).slice(0, 120)));
    try {
      const resp = await page.goto(`http://127.0.0.1:${port}${route}`, { waitUntil: "networkidle", timeout: 30000 });
      const h = resp.headers();
      const html = await page.content();
      const hydrated = await page.evaluate(() => !!document.documentElement.getAttribute("data-theme"));
      const checks = {
        csp: /nonce-/.test(h["content-security-policy"] || ""),
        hsts: /max-age=63072000/.test(h["strict-transport-security"] || ""),
        scriptNonce: /<script[^>]*nonce=/.test(html),
        noErrors: errs.length === 0,
        rendered: html.length > 400,
      };
      const ok = Object.values(checks).every(Boolean);
      ok ? pass++ : fail++;
      console.log(`${ok ? "PASS" : "FAIL"} ${name}${route} :: ` +
        Object.entries(checks).filter(([, v]) => !v).map(([k]) => k).join(",") || "-");
      if (!ok && errs.length) errs.slice(0, 2).forEach((e) => console.log("   ", e));
      if (!ok && !errs.length) console.log("    headers:", JSON.stringify({ csp: (h["content-security-policy"] || "").slice(0, 40), hsts: h["strict-transport-security"] }));
    } catch (e) {
      fail++;
      console.log(`FAIL ${name}${route} NAV ${String(e).split("\n")[0].slice(0, 100)}`);
    }
    await page.close();
  }
}
await browser.close();
console.log(`\nSWEEP: ${pass} pass / ${fail} fail`);
process.exit(fail ? 1 : 0);
