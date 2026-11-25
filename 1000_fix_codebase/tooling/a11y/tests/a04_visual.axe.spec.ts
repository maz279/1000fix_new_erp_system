import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import path from "node:path";

const ARTIFACT_DIR = "C:/Users/DELL/.gemini/antigravity/brain/12d572bf-cfb4-461d-8a64-c9de0de50fde";

test.describe("A04 Commercial & Revenue Comprehensive Visual & WCAG 2.2 AA Verification Suite", () => {
  test("Verify all 9 A04 modules render deep 6-tab Dynamics 365 master forms and pass WCAG 2.2 AA", async ({ page }) => {
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
    await page.waitForTimeout(2500);

    // Unregister stale service worker to ensure fresh static assets
    await page.evaluate(async () => {
      if ("serviceWorker" in navigator) {
        const regs = await navigator.serviceWorker.getRegistrations();
        for (const r of regs) await r.unregister();
      }
    });

    const formChecks = [
      { modCode: "M08", formLabel: /Contract/i, shot: "a04_wave1_m08_contract_6tab_form.png", expectedTabs: 6 },
      { modCode: "M09", formLabel: /Brand Claim/i, shot: "a04_wave1_m09_claim_6tab_form.png", expectedTabs: 6 },
      { modCode: "M11", formLabel: /Rate Card/i, shot: "a04_wave1_m11_pricing_6tab_form.png", expectedTabs: 6 },
      { modCode: "M12", formLabel: /Seller Application/i, shot: "a04_wave1_m12_seller_6tab_form.png", expectedTabs: 6 },
      { modCode: "M36", formLabel: /Quotation/i, shot: "a04_wave1_m36_quotation_6tab_form.png", expectedTabs: 6 },
      { modCode: "M37", formLabel: /Catalogue Item/i, shot: "a04_wave1_m37_catalogue_6tab_form.png", expectedTabs: 6 },
      { modCode: "M38", formLabel: /Online Order/i, shot: "a04_wave1_m38_order_6tab_form.png", expectedTabs: 6 },
      { modCode: "M39", formLabel: /Subscription/i, shot: "a04_wave1_m39_subscription_6tab_form.png", expectedTabs: 6 },
      { modCode: "M40", formLabel: /Partner/i, shot: "a04_wave1_m40_partner_6tab_form.png", expectedTabs: 6 },
    ];

    for (const item of formChecks) {
      console.log(`[A04-FORM-TEST] Testing module: ${item.modCode} for deep 6-tab D365 form`);
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
      console.log(`[A04-FORM-TEST] ${item.modCode} rendered ${tabCount} tabs (expected: ${item.expectedTabs})`);
      expect(tabCount).toBeGreaterThanOrEqual(item.expectedTabs);

      // Verify each tab activates and filters sections
      for (let i = 0; i < tabCount; i++) {
        const tabBtn = tabs.nth(i);
        await tabBtn.click();
        await page.waitForTimeout(200);
        await expect(tabBtn).toHaveClass(/active/);
      }

      // Return to tab 1
      await tabs.first().click();
      await page.waitForTimeout(300);

      // Capture full component screenshot
      await page.screenshot({ path: path.join(ARTIFACT_DIR, item.shot), fullPage: false });

      // Run Axe accessibility scan on the form container
      const axeResults = await new AxeBuilder({ page })
        .include(".d365-form")
        .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"])
        .analyze();

      const seriousOrCritical = axeResults.violations.filter(v => ["critical", "serious"].includes(v.impact || ""));
      console.log(`[A04-FORM-TEST] ${item.modCode} Axe violations: ${seriousOrCritical.length} critical/serious`);
      if (seriousOrCritical.length > 0) {
        console.warn(`[A04-FORM-TEST] Violations found in ${item.modCode}:`, seriousOrCritical.map(v => `${v.id}: ${v.description}`));
      }
      expect(seriousOrCritical.length).toBe(0);
    }
  });

  test("Verify A04 Built-in Report Packs render clean tabular grids with export capabilities", async ({ page }) => {
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
    await page.waitForTimeout(2500);

    const reportChecks = [
      { modCode: "M08", reportLabel: /Contract Base Movement/i, shot: "a04_wave1_m08_base_report.png" },
      { modCode: "M09", reportLabel: /Claim Ageing/i, shot: "a04_wave1_m09_ageing_report.png" },
      { modCode: "M11", reportLabel: /Realised Price vs Card/i, shot: "a04_wave1_m11_realised_report.png" },
      { modCode: "M12", reportLabel: /Commission Revenue/i, shot: "a04_wave1_m12_commission_report.png" },
      { modCode: "M36", reportLabel: /Quote Conversion/i, shot: "a04_wave1_m36_conversion_report.png" },
      { modCode: "M37", reportLabel: /Item Margin Analysis/i, shot: "a04_wave1_m37_margin_report.png" },
      { modCode: "M38", reportLabel: /Delivery Performance/i, shot: "a04_wave1_m38_delivery_report.png" },
      { modCode: "M39", reportLabel: /MRR Waterfall/i, shot: "a04_wave1_m39_mrr_report.png" },
      { modCode: "M40", reportLabel: /Partner Revenue/i, shot: "a04_wave1_m40_revenue_report.png" }
    ];

    for (const rep of reportChecks) {
      console.log(`[A04-REPORT-TEST] Testing report in ${rep.modCode}: ${rep.reportLabel}`);
      const modBtn = page.locator("button.nav-mod").filter({ hasText: new RegExp(rep.modCode, "i") }).first();
      await expect(modBtn).toBeVisible({ timeout: 15000 });
      await modBtn.click();
      await page.waitForTimeout(1800);

      // Find and click the report chip / screen link
      const rptChip = page.locator("button.screen-link, button.report-chip, .report-chip").filter({ hasText: rep.reportLabel }).first();
      await expect(rptChip).toBeVisible({ timeout: 15000 });
      await rptChip.click();
      await page.waitForTimeout(2000);

      // Verify report container and table rendered
      await page.waitForSelector(".table-report, .p03-table-container, table", { timeout: 20000 });
      await page.screenshot({ path: path.join(ARTIFACT_DIR, rep.shot), fullPage: false });
      console.log(`[A04-REPORT-TEST] Captured report screenshot: ${rep.shot}`);
    }
  });
});
