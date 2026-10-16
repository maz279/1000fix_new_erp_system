// PP7-M02 — WCAG 2.2 AA gatekeeper (axe-core) across the full surface:
// every portal route + the Odoo P03 workspace. Zero critical/serious
// violations is the gate (DoD D9); moderate violations are inventoried
// to results/a11y-gatekeeper.json for the burn-down.
import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { writeFileSync, mkdirSync } from "node:fs";

const PORTAL_ROUTES: Array<[string, string]> = [
  ["corporate", "http://127.0.0.1:3001/"],
  ["corporate-estate", "http://127.0.0.1:3001/estate"],
  ["corporate-invoices", "http://127.0.0.1:3001/invoices"],
  ["corporate-service-requests", "http://127.0.0.1:3001/service-requests"],
  ["customer", "http://127.0.0.1:3010/"],
  ["customer-welcome", "http://127.0.0.1:3010/welcome"],
  ["customer-booking", "http://127.0.0.1:3010/booking"],
  ["customer-tracking", "http://127.0.0.1:3010/tracking"],
  ["customer-devices", "http://127.0.0.1:3010/devices"],
  ["customer-consent", "http://127.0.0.1:3010/consent"],
  ["analytics", "http://127.0.0.1:3012/"],
  ["seller", "http://127.0.0.1:3013/"],
  ["seller-jobs", "http://127.0.0.1:3013/jobs"],
  ["seller-scorecard", "http://127.0.0.1:3013/scorecard"],
  ["seller-settlements", "http://127.0.0.1:3013/settlements"],
  ["brand", "http://127.0.0.1:3014/"],
  ["brand-reconciliation", "http://127.0.0.1:3014/reconciliation"],
  ["agent-console", "http://127.0.0.1:3015/"],
  ["agent-console-conversation", "http://127.0.0.1:3015/conversation"],
  ["partner", "http://127.0.0.1:3016/"],
  ["partner-referrals", "http://127.0.0.1:3016/referrals"],
  ["partner-commissions", "http://127.0.0.1:3016/commissions"],
  ["vendor", "http://127.0.0.1:3017/"],
  ["vendor-invoices", "http://127.0.0.1:3017/invoices"],
];

const report: Record<string, unknown> = { generated: new Date().toISOString(), routes: {} };
const inventory: Array<{ route: string; id: string; impact: string; nodes: number; help: string }> = [];

test.describe("PP7-M02 WCAG 2.2 AA gatekeeper", () => {
  for (const [name, url] of PORTAL_ROUTES) {
    test(`axe: ${name}`, async ({ page }) => {
      await page.goto(url, { waitUntil: "networkidle" });
      const results = await new AxeBuilder({ page })
        .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"])
        .analyze();
      const serious = results.violations.filter((v) =>
        ["serious", "critical"].includes(v.impact ?? ""));
      (report.routes as Record<string, unknown>)[name] = {
        url,
        critical: serious.length,
        total: results.violations.length,
        violations: results.violations.map((v) => ({
          id: v.id, impact: v.impact, nodes: v.nodes.length, help: v.help,
        })),
      };
      results.violations.forEach((v) =>
        inventory.push({ route: name, id: v.id, impact: v.impact ?? "?", nodes: v.nodes.length, help: v.help }));
      expect(serious, `${name}: ${serious.map((v) => v.id).join(", ")}`).toHaveLength(0);
    });
  }

  // The back-office surface: axe scoped to the P03 workspace we own.
  // Odoo 19's own client chrome (list views: ~1,700 vendor hits —
  // aria-allowed-attr &c.) is vendor code, recorded as an upstream
  // finding, never patched in vendor/ (FF-03 territory).
  test("axe: p03-workspace (scoped, back office)", async ({ page }) => {
    await page.goto("http://127.0.0.1:8069/web/login");
    const password = process.env.FIX_A11Y_PASSWORD;
    test.skip(!password, "FIX_A11Y_PASSWORD not set");
    await page.fill("input[name=login]", "admin");
    await page.fill("input[name=password]", password!);
    await Promise.all([
      page.waitForNavigation({ waitUntil: "domcontentloaded", timeout: 60000 }),
      page.click("button[type=submit]"),
    ]);
    await page.goto("http://127.0.0.1:8069/odoo", { waitUntil: "domcontentloaded" });
    await page.waitForSelector(".p03-workspace-root", { timeout: 60000 });
    await page.waitForTimeout(1200);
    const results = await new AxeBuilder({ page })
      .include(".p03-workspace-root")
      .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"])
      .analyze();
    const serious = results.violations.filter((v) =>
      ["serious", "critical"].includes(v.impact ?? ""));
    (report.routes as Record<string, unknown>)["p03-workspace"] = {
      url: "http://127.0.0.1:8069/odoo (scoped)",
      critical: serious.length,
      total: results.violations.length,
      violations: results.violations.map((v) => ({
        id: v.id, impact: v.impact, nodes: v.nodes.length, help: v.help,
      })),
    };
    results.violations.forEach((v) =>
      inventory.push({ route: "p03-workspace", id: v.id, impact: v.impact ?? "?", nodes: v.nodes.length, help: v.help }));
    expect(serious, serious.map((v) => v.id).join(", ")).toHaveLength(0);
  });

  test.afterAll(async () => {
    mkdirSync("results", { recursive: true });
    writeFileSync("results/a11y-gatekeeper.json", JSON.stringify(report, null, 2));
    writeFileSync("results/a11y-inventory.json", JSON.stringify(inventory, null, 2));
  });
});
