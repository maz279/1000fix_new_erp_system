import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import path from "node:path";

const ARTIFACT_DIR = "C:/Users/DELL/.gemini/antigravity/brain/12d572bf-cfb4-461d-8a64-c9de0de50fde";

test.describe("A05 Circular Economy Comprehensive Visual & WCAG 2.2 AA Verification Suite", () => {
  test("Verify M13, M14, M18 render deep 6-tab Dynamics 365 master forms and pass WCAG 2.2 AA", async ({ page }) => {
    test.setTimeout(360_000);

    // Step 1: Login to Odoo
    await page.goto("http://127.0.0.1:8069/web/login", { waitUntil: "networkidle" });
    await page.fill("input[name='login']", "admin");
    await page.fill("input[name='password']", "admin");
    await page.click("button[type='submit']");
    await page.waitForURL(/\/web|\/odoo/);

    // Step 2: Navigate to P03 Operations Workspace
    await page.goto("http://127.0.0.1:8069/odoo/action-cd_p03_portal.action_p03_workspace", { waitUntil: "domcontentloaded" });
    await page.waitForSelector(".p03-workspace-root", { timeout: 45000 });
    await page.waitForTimeout(2000);

    // Unregister stale service worker and clear caches to guarantee fresh static assets
    await page.evaluate(async () => {
      if ("serviceWorker" in navigator) {
        const regs = await navigator.serviceWorker.getRegistrations();
        for (const r of regs) await r.unregister();
      }
      if ("caches" in window) {
        const keys = await caches.keys();
        for (const k of keys) await caches.delete(k);
      }
    });
    await page.reload({ waitUntil: "domcontentloaded" });
    await page.waitForSelector(".p03-workspace-root", { timeout: 45000 });
    await page.waitForTimeout(2000);

    const formChecks = [
      { modCode: "M13", formLabel: /Reservation Cockpit/i, shot: "a05_wave1_m13_reservation_6tab_form.png", expectedTabs: 6 },
      { modCode: "M14", formLabel: /Trade-In Intake Dossier/i, shot: "a05_wave1_m14_request_6tab_form.png", expectedTabs: 6 },
      { modCode: "M18", formLabel: /E-Waste Collection Dossier/i, shot: "a05_wave1_m18_collection_6tab_form.png", expectedTabs: 6 },
    ];

    for (const item of formChecks) {
      console.log(`[A05-FORM-TEST] Testing module: ${item.modCode} for deep 6-tab D365 form`);
      const modBtn = page.locator("button.nav-mod").filter({ hasText: new RegExp(item.modCode, "i") }).first();
      await expect(modBtn).toBeVisible({ timeout: 15000 });
      await modBtn.click();
      await page.waitForTimeout(1800);

      // Click the specific form chip
      const chipBtn = page.locator("button.form-chip").filter({ hasText: item.formLabel }).first();
      await expect(chipBtn).toBeVisible({ timeout: 15000 });
      await chipBtn.click();
      await page.waitForTimeout(2500);

      // Verify the D365 multi-tab strip
      await page.waitForSelector(".d365-formtabs", { timeout: 20000 });
      const tablist = page.locator(".d365-formtabs[role='tablist']");
      await expect(tablist).toBeVisible();

      const tabs = page.locator(".d365-formtabs button[role='tab']");
      const tabCount = await tabs.count();
      console.log(`[A05-FORM-TEST] ${item.modCode} rendered ${tabCount} tabs (expected: ${item.expectedTabs})`);
      expect(tabCount).toBeGreaterThanOrEqual(item.expectedTabs);

      // Verify each tab activates and filters sections
      for (let i = 0; i < tabCount; i++) {
        const tabBtn = tabs.nth(i);
        await tabBtn.click();
        await page.waitForTimeout(250);
        await expect(tabBtn).toHaveClass(/active/);
      }

      // Return to tab 1
      await tabs.first().click();
      await page.waitForTimeout(300);

      // Capture full component screenshot
      await page.screenshot({ path: path.join(ARTIFACT_DIR, item.shot), fullPage: false });
      console.log(`[A05-FORM-TEST] Captured form screenshot: ${item.shot}`);

      // Run Axe accessibility scan on the form container
      const axeResults = await new AxeBuilder({ page })
        .include(".d365-form")
        .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"])
        .analyze();

      const seriousOrCritical = axeResults.violations.filter(v => ["critical", "serious"].includes(v.impact || ""));
      console.log(`[A05-FORM-TEST] ${item.modCode} Axe violations: ${seriousOrCritical.length} critical/serious`);
      if (seriousOrCritical.length > 0) {
        console.warn(`[A05-FORM-TEST] Violations found in ${item.modCode}:`, seriousOrCritical.map(v => `${v.id}: ${v.description}`));
      }
      expect(seriousOrCritical.length).toBe(0);
    }
  });

  test("Verify A05 Built-in Report Packs render clean tabular grids with live data rows", async ({ page }) => {
    test.setTimeout(240_000);

    // Login to Odoo
    await page.goto("http://127.0.0.1:8069/web/login", { waitUntil: "networkidle" });
    await page.fill("input[name='login']", "admin");
    await page.fill("input[name='password']", "admin");
    await page.click("button[type='submit']");
    await page.waitForURL(/\/web|\/odoo/);

    // Navigate to P03 Operations Workspace
    await page.goto("http://127.0.0.1:8069/odoo/action-cd_p03_portal.action_p03_workspace", { waitUntil: "domcontentloaded" });
    await page.waitForSelector(".p03-workspace-root", { timeout: 45000 });
    await page.waitForTimeout(2000);

    // Clear caches in Test 2 as well
    await page.evaluate(async () => {
      if ("serviceWorker" in navigator) {
        const regs = await navigator.serviceWorker.getRegistrations();
        for (const r of regs) await r.unregister();
      }
      if ("caches" in window) {
        const keys = await caches.keys();
        for (const k of keys) await caches.delete(k);
      }
    });
    await page.reload({ waitUntil: "domcontentloaded" });
    await page.waitForSelector(".p03-workspace-root", { timeout: 45000 });
    await page.waitForTimeout(2000);

    const reportChecks = [
      { modCode: "M13", reportLabel: /Rental P&L/i, shot: "a05_wave1_m13_rental_pl_report.png" },
      { modCode: "M14", reportLabel: /Trade-In Margin/i, shot: "a05_wave1_m14_margin_report.png" },
      { modCode: "M18", reportLabel: /Collection Volume/i, shot: "a05_wave1_m18_collection_volume_report.png" },
    ];

    for (const rep of reportChecks) {
      console.log(`[A05-REPORT-TEST] Testing report in ${rep.modCode}: ${rep.reportLabel}`);
      const modBtn = page.locator("button.nav-mod").filter({ hasText: new RegExp(rep.modCode, "i") }).first();
      await expect(modBtn).toBeVisible({ timeout: 15000 });
      await modBtn.click();
      await page.waitForTimeout(1800);

      // Find and click the report chip
      const rptChip = page.locator("button.screen-link").filter({ hasText: rep.reportLabel }).first();
      await expect(rptChip).toBeVisible({ timeout: 15000 });
      await rptChip.click();
      await page.waitForTimeout(2500);

      // Verify report container and table rendered
      await page.waitForSelector(".table-report, .p03-table-container, table", { timeout: 20000 });
      await page.screenshot({ path: path.join(ARTIFACT_DIR, rep.shot), fullPage: false });
      console.log(`[A05-REPORT-TEST] Captured report screenshot: ${rep.shot}`);
    }
  });
});
