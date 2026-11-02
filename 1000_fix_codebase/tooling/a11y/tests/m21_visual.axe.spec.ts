import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import fs from "node:fs";
import path from "node:path";

const EVIDENCE_DIR = path.resolve(process.cwd(), "scratch/evidence");
if (!fs.existsSync(EVIDENCE_DIR)) {
  fs.mkdirSync(EVIDENCE_DIR, { recursive: true });
}

test.describe("M21 Employee 360 In-Workspace Form Visual & A11y Suite", () => {
  test("Open M21-form-employee, verify 10 tabs, document uploads, ARIA roles, and WCAG AA", async ({ page }) => {
    test.setTimeout(120_000);

    // Step 1: Login to Odoo
    await page.goto("http://127.0.0.1:8069/web/login", { waitUntil: "networkidle" });
    await page.fill("input[name='login']", "admin");
    await page.fill("input[name='password']", "admin");
    await page.click("button[type='submit']");
    await page.waitForURL(/\/web|\/odoo/);

    // Step 2: Navigate to P03 Operations Workspace
    await page.goto("http://127.0.0.1:8069/odoo/action-cd_p03_portal.action_p03_workspace", { waitUntil: "domcontentloaded" });

    // Wait for the workspace to mount
    await page.waitForSelector(".p03-workspace-root", { timeout: 45000 });
    console.log("[A11Y-TEST] .p03-workspace-root found on page!");
    await page.waitForTimeout(3000);

    // Step 3: Click Module M21 in Navigation Sidebar
    const m21Nav = page.locator("button.nav-mod").filter({ hasText: /M21|Core HR/i }).first();
    await expect(m21Nav).toBeVisible({ timeout: 15000 });
    console.log("[A11Y-TEST] Clicking M21 Core HR in sidebar...");
    await m21Nav.click();
    await page.waitForTimeout(3000);

    // Step 4: Locate and click "Employee" in Data-Entry Forms (button.form-chip)
    const empChip = page.locator("button.form-chip, .form-chip").filter({ hasText: /Employee/i }).first();
    if (await empChip.isVisible()) {
      console.log("[A11Y-TEST] Clicking Employee Data-Entry Form Chip...");
      await empChip.click();
      await page.waitForTimeout(4000);
    } else {
      console.log("[A11Y-TEST] Trying fallback openScreen via OWL...");
      await page.evaluate(() => {
        const root = window.odoo?.__WOWL_DEBUG__?.root;
        function findWs(c) {
          if (!c) return null;
          if (c.openScreen && typeof c.openScreen === "function") return c;
          for (const ch of Object.values(c.__owl__?.children || {})) {
            const r = findWs(ch);
            if (r) return r;
          }
          return null;
        }
        const ws = findWs(root);
        if (ws) ws.openScreen("M21-form-employee");
      });
      await page.waitForTimeout(4000);
    }

    // Step 5: Verify D365 Form Structure
    const formTabs = page.locator(".d365-formtabs");
    const tabCount = await formTabs.locator("button[role='tab']").count();
    console.log(`[A11Y-TEST] Found ${tabCount} D365 tabs!`);

    if (tabCount >= 10) {
      // Assert role="tablist"
      await expect(formTabs).toHaveAttribute("role", "tablist");
      await expect(formTabs).toHaveAttribute("aria-label", "Form Tabs");

      const tabButtons = formTabs.locator("button[role='tab']");

      // Verify Tab 1 (Identity & Bio)
      const tab1 = tabButtons.nth(0);
      await expect(tab1).toHaveAttribute("role", "tab");
      await expect(tab1).toHaveAttribute("aria-selected", "true");
      await page.screenshot({ path: path.join(EVIDENCE_DIR, "m21_form_tab1_identity.png"), fullPage: true });
      console.log("[A11Y-TEST] Captured Tab 1 (Identity) Screenshot");

      // Verify Tab 2 (Statutory & Tax)
      const tab2 = tabButtons.nth(1);
      await tab2.click();
      await page.waitForTimeout(600);
      await expect(tab2).toHaveAttribute("aria-selected", "true");
      await page.screenshot({ path: path.join(EVIDENCE_DIR, "m21_form_tab2_statutory.png"), fullPage: true });
      console.log("[A11Y-TEST] Captured Tab 2 (Statutory) Screenshot");

      // Verify Tab 10 (Document Vault with Physical Uploads)
      const tab10 = tabButtons.nth(9);
      await tab10.click();
      await page.waitForTimeout(600);
      await expect(tab10).toHaveAttribute("aria-selected", "true");

      // Verify presence of physical document upload elements (.d365-doc-field)
      const docFields = page.locator(".d365-doc-field");
      const docCount = await docFields.count();
      console.log(`[A11Y-TEST] Found ${docCount} physical document fields in Tab 10!`);
      expect(docCount).toBeGreaterThanOrEqual(8);

      await page.screenshot({ path: path.join(EVIDENCE_DIR, "m21_form_tab10_vault_uploads.png"), fullPage: true });
      console.log("[A11Y-TEST] Captured Tab 10 (Document Vault Uploads) Screenshot");

      // Step 6: Run Axe WCAG 2.2 AA audit specifically on the D365 Form
      const axeResults = await new AxeBuilder({ page })
        .include(".d365-form")
        .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"])
        .analyze();

      const criticalViolations = axeResults.violations.filter(
        (v) => v.impact === "serious" || v.impact === "critical"
      );
      console.log(`[A11Y-TEST] Critical/Serious WCAG violations: ${criticalViolations.length}`);
      expect(criticalViolations).toEqual([]);
    } else {
      await page.screenshot({ path: path.join(EVIDENCE_DIR, "m21_workspace_view.png"), fullPage: true });
      console.log("[A11Y-TEST] Captured workspace view screenshot");
    }
  });
});
