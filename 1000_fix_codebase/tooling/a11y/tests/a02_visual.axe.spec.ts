import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import path from "node:path";

const ARTIFACT_DIR = "C:/Users/DELL/.gemini/antigravity/brain/12d572bf-cfb4-461d-8a64-c9de0de50fde";

test.describe("A02 Service Delivery & Execution Complete Visual & WCAG 2.2 AA Suite", () => {
  test("Verify all 7 A02 modules (M01, M02, M03, M04, M05, M06, M31), multi-tab forms, and 0 critical/serious Axe violations", async ({ page }) => {
    test.setTimeout(180_000);

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

    // Unregister any stale service workers
    await page.evaluate(async () => {
      if ("serviceWorker" in navigator) {
        const regs = await navigator.serviceWorker.getRegistrations();
        for (const r of regs) await r.unregister();
      }
    });

    const checks = [
      { modCode: "M01", targetRegex: /Service Order/i, shot: "a02_wave5_m01_service_order_form.png", minTabs: 6 },
      { modCode: "M02", targetRegex: /Field Work Order/i, shot: "a02_wave5_m02_field_work_order_form.png", minTabs: 5 },
      { modCode: "M03", targetRegex: /Consignment/i, shot: "a02_wave5_m03_consignment_form.png", minTabs: 4 },
      { modCode: "M04", targetRegex: /Shift Open\/Close/i, shot: "a02_wave5_m04_cash_shift_form.png", minTabs: 3 },
      { modCode: "M05", targetRegex: /Remote Session/i, shot: "a02_wave5_m05_remote_session_form.png", minTabs: 2 },
      { modCode: "M06", targetRegex: /Recovery Case/i, shot: "a02_wave5_m06_data_case_form.png", minTabs: 4 },
      { modCode: "M31", targetRegex: /Repair Order/i, shot: "a02_wave5_m31_repair_order_form.png", minTabs: 5 },
    ];

    for (const item of checks) {
      const modBtn = page.locator("button.nav-mod").filter({ hasText: new RegExp(item.modCode, "i") }).first();
      await expect(modBtn).toBeVisible({ timeout: 15000 });
      await modBtn.click();
      await page.waitForTimeout(1800);

      const chipBtn = page.locator("button.form-chip, .form-chip").filter({ hasText: item.targetRegex }).first();
      await expect(chipBtn).toBeVisible({ timeout: 15000 });
      await chipBtn.click();
      await page.waitForTimeout(2000);

      await page.waitForSelector(".d365-formtabs", { timeout: 20000 });
      const tabs = page.locator(".d365-formtabs button[role='tab']");
      const tabCount = await tabs.count();
      console.log(`[A02-A11Y] ${item.modCode} (${item.shot}) -> rendered ${tabCount} tabs`);
      expect(tabCount).toBeGreaterThanOrEqual(item.minTabs);

      await page.screenshot({ path: path.join(ARTIFACT_DIR, item.shot), fullPage: false });

      const axeResults = await new AxeBuilder({ page })
        .include(".d365-form")
        .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"])
        .analyze();

      const criticalSerious = axeResults.violations.filter(v => v.impact === "critical" || v.impact === "serious");
      console.log(`[A02-A11Y] ${item.modCode} Axe violations: total=${axeResults.violations.length}, critical/serious=${criticalSerious.length}`);
      expect(criticalSerious.length).toBe(0);
    }
  });
});
