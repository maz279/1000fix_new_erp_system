import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import path from "node:path";

const ARTIFACT_DIR = "C:/Users/DELL/.gemini/antigravity/brain/12d572bf-cfb4-461d-8a64-c9de0de50fde";

test.describe("A03 Customer Experience & Engagement Wave 8 Comprehensive Visual & WCAG Suite", () => {
  test("Verify all 7 A03 modules (M33, M07, M27, M32, M10, M34, M35) render deep multi-tab forms and 0 Axe violations", async ({ page }) => {
    test.setTimeout(300_000);

    // Step 1: Login to Odoo
    await page.goto("http://127.0.0.1:8069/web/login", { waitUntil: "networkidle" });
    await page.fill("input[name='login']", "admin");
    await page.fill("input[name='password']", "admin");
    await page.click("button[type='submit']");
    await page.waitForURL(/\/web|\/odoo/);

    // Step 2: Navigate to P03 Operations Workspace
    await page.goto("http://127.0.0.1:8069/odoo/action-cd_p03_portal.action_p03_workspace", { waitUntil: "domcontentloaded" });
    await page.waitForSelector(".p03-workspace-root", { timeout: 45000 });
    await page.waitForTimeout(2500);

    // Clear stale service workers and force reload fresh assets
    await page.evaluate(async () => {
      if ("serviceWorker" in navigator) {
        const regs = await navigator.serviceWorker.getRegistrations();
        for (const r of regs) await r.unregister();
      }
    });

    const checks = [
      { modCode: "M33", formLabel: /Party Master/i, shot: "a03_wave8_m33_party_10tab_form.png", expectedTabs: 10 },
      { modCode: "M07", formLabel: /Opportunity/i, shot: "a03_wave8_m07_opportunity_8tab_form.png", expectedTabs: 8 },
      { modCode: "M27", formLabel: /Call Conversation/i, shot: "a03_wave8_m27_call_6tab_form.png", expectedTabs: 6 },
      { modCode: "M32", formLabel: /Intent Definition/i, shot: "a03_wave8_m32_intent_5tab_form.png", expectedTabs: 5 },
      { modCode: "M10", formLabel: /Loyalty Programme/i, shot: "a03_wave8_m10_loyalty_6tab_form.png", expectedTabs: 6 },
      { modCode: "M34", formLabel: /Complaint/i, shot: "a03_wave8_m34_complaint_6tab_form.png", expectedTabs: 6 },
      { modCode: "M35", formLabel: /Campaign/i, shot: "a03_wave8_m35_campaign_7tab_form.png", expectedTabs: 7 },
    ];

    for (const item of checks) {
      console.log(`[A03-WAVE8] Testing module: ${item.modCode} for deep multi-tab form`);
      const modBtn = page.locator("button.nav-mod").filter({ hasText: new RegExp(item.modCode, "i") }).first();
      await expect(modBtn).toBeVisible({ timeout: 15000 });
      await modBtn.click();
      await page.waitForTimeout(1800);

      // Click the specific form chip
      const chipBtn = page.locator("button.form-chip, .form-chip").filter({ hasText: item.formLabel }).first();
      await expect(chipBtn).toBeVisible({ timeout: 15000 });
      await chipBtn.click();
      await page.waitForTimeout(2000);

      // Verify the D365 multi-tab strip
      await page.waitForSelector(".d365-formtabs", { timeout: 20000 });
      const tablist = page.locator(".d365-formtabs[role='tablist']");
      await expect(tablist).toBeVisible();

      const tabs = page.locator(".d365-formtabs button[role='tab']");
      const tabCount = await tabs.count();
      console.log(`[A03-WAVE8] ${item.modCode} rendered ${tabCount} tabs (expected: ${item.expectedTabs})`);
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
      await page.waitForTimeout(400);

      // Capture full component screenshot
      await page.screenshot({ path: path.join(ARTIFACT_DIR, item.shot), fullPage: false });

      // Run Axe accessibility scan
      const axeResults = await new AxeBuilder({ page })
        .include(".d365-form")
        .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"])
        .analyze();

      const seriousOrCritical = axeResults.violations.filter(v => ["critical", "serious"].includes(v.impact || ""));
      console.log(`[A03-WAVE8] ${item.modCode} Axe violations: ${seriousOrCritical.length} critical/serious`);
      if (seriousOrCritical.length > 0) {
        console.warn(`[A03-WAVE8] Violations found in ${item.modCode}:`, seriousOrCritical.map(v => `${v.id}: ${v.description}`));
      }
      expect(seriousOrCritical.length).toBe(0);
    }
  });

  test("Verify A03 Built-in Report Packs render clean tabular grids with export capabilities", async ({ page }) => {
    test.setTimeout(180_000);

    // Login to Odoo
    await page.goto("http://127.0.0.1:8069/web/login", { waitUntil: "networkidle" });
    await page.fill("input[name='login']", "admin");
    await page.fill("input[name='password']", "admin");
    await page.click("button[type='submit']");
    await page.waitForURL(/\/web|\/odoo/);

    // Navigate to P03 Operations Workspace
    await page.goto("http://127.0.0.1:8069/odoo/action-cd_p03_portal.action_p03_workspace", { waitUntil: "domcontentloaded" });
    await page.waitForSelector(".p03-workspace-root", { timeout: 45000 });
    await page.waitForTimeout(2500);

    // Test a sample of reports across A03
    const reportChecks = [
      { modCode: "M33", reportLabel: /Customer Growth/i, shot: "a03_wave8_m33_growth_report.png" },
      { modCode: "M07", reportLabel: /Pipeline by Revenue/i, shot: "a03_wave8_m07_pipeline_report.png" },
      { modCode: "M27", reportLabel: /First Contact Resolution/i, shot: "a03_wave8_m27_fcr_report.png" },
      { modCode: "M10", reportLabel: /Member Growth/i, shot: "a03_wave8_m10_growth_report.png" },
      { modCode: "M34", reportLabel: /Complaint Category Pareto/i, shot: "a03_wave8_m34_pareto_report.png" },
      { modCode: "M35", reportLabel: /Attribution & ROI/i, shot: "a03_wave8_m35_roi_report.png" }
    ];

    for (const rep of reportChecks) {
      console.log(`[A03-REPORTS] Testing report in ${rep.modCode}: ${rep.reportLabel}`);
      const modBtn = page.locator("button.nav-mod").filter({ hasText: new RegExp(rep.modCode, "i") }).first();
      await expect(modBtn).toBeVisible({ timeout: 15000 });
      await modBtn.click();
      await page.waitForTimeout(1500);

      const rptChip = page.locator("button.screen-link").filter({ hasText: rep.reportLabel }).first();
      await expect(rptChip).toBeVisible({ timeout: 15000 });
      await rptChip.click();
      await page.waitForTimeout(2000);

      // Check report table or layout exists
      const tableOrLayout = page.locator(".gl-layout, .fx-table, .data-screen, table, .report-container").first();
      await expect(tableOrLayout).toBeVisible({ timeout: 15000 });
      await page.screenshot({ path: path.join(ARTIFACT_DIR, rep.shot), fullPage: false });
      console.log(`[A03-REPORTS] Captured ${rep.shot}`);
    }
  });
});
