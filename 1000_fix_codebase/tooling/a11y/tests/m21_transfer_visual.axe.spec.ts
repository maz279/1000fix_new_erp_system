import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import fs from "node:fs";
import path from "node:path";

const ARTIFACT_DIR = "C:/Users/DELL/.gemini/antigravity/brain/12d572bf-cfb4-461d-8a64-c9de0de50fde";

test.describe("M21 Transfer & Promotion 8-Tab Dynamics 365 Visual & A11y Suite", () => {
  test("Open M21-form-transfer, inspect 8 tabs, ARIA roles, and WCAG 2.2 AA conformance", async ({ page }) => {
    test.setTimeout(120_000);

    // Step 1: Login to Odoo
    await page.goto("http://127.0.0.1:8069/web/login", { waitUntil: "networkidle" });
    await page.fill("input[name='login']", "admin");
    await page.fill("input[name='password']", "admin");
    await page.click("button[type='submit']");
    await page.waitForURL(/\/web|\/odoo/);

    // Step 2: Navigate to P03 Operations Workspace
    await page.goto("http://127.0.0.1:8069/odoo/action-cd_p03_portal.action_p03_workspace", { waitUntil: "domcontentloaded" });
    await page.waitForSelector(".p03-workspace-root", { timeout: 45000 });
    console.log("[A11Y-TEST] .p03-workspace-root mounted successfully");
    await page.waitForTimeout(3000);

    // Step 3: Click Module M21 in Navigation Sidebar
    const m21Nav = page.locator("button.nav-mod").filter({ hasText: /M21|Core HR/i }).first();
    await expect(m21Nav).toBeVisible({ timeout: 15000 });
    console.log("[A11Y-TEST] Clicking M21 Core HR in sidebar...");
    await m21Nav.click();
    await page.waitForTimeout(3000);

    // Step 4: Click Transfer / Promotion Form Chip in Data-Entry Forms
    const trfChip = page.locator("button.form-chip, .form-chip").filter({ hasText: /Transfer|Promotion/i }).first();
    await expect(trfChip).toBeVisible({ timeout: 15000 });
    console.log("[A11Y-TEST] Clicking Transfer Data-Entry Form Chip...");
    await trfChip.click();
    await page.waitForTimeout(3000);

    // Step 5: Verify .d365-formtabs Container
    await page.waitForSelector(".d365-formtabs", { timeout: 25000 });
    console.log("[A11Y-TEST] .d365-formtabs container rendered successfully!");
    await page.waitForTimeout(2000);

    // Step 6: Verify All 8 Dynamics 365 Tabs Exist
    const tabButtons = page.locator(".d365-formtabs button[role='tab']");
    const count = await tabButtons.count();
    console.log(`[A11Y-TEST] Rendered tab buttons count: ${count}`);
    expect(count).toBe(8);

    const expectedTabLabels = [
      "Movement Scope",
      "Position & Org Realignment",
      "Compensation & Payroll",
      "Technical Tier & OEM Badges",
      "Handover & Custody Clearance",
      "Relocation & Transit Leave",
      "Authorization & Digital Signoff",
      "Document Vault & Physical Scans"
    ];

    for (let i = 0; i < expectedTabLabels.length; i++) {
      const tabText = await tabButtons.nth(i).innerText();
      console.log(`[A11Y-TEST] Tab ${i + 1}: ${tabText.replace(/\n/g, ' ')}`);
      expect(tabText).toContain(expectedTabLabels[i]);
    }

    // Step 7: Capture Visual Screenshots of All Major Tabs
    // Tab 1: Scope
    await tabButtons.nth(0).click();
    await page.waitForTimeout(800);
    await page.screenshot({ path: path.join(ARTIFACT_DIR, "m21_transfer_tab1_scope.png"), fullPage: false });

    // Tab 2: Organization
    await tabButtons.nth(1).click();
    await page.waitForTimeout(800);
    await page.screenshot({ path: path.join(ARTIFACT_DIR, "m21_transfer_tab2_organization.png"), fullPage: false });

    // Tab 3: Compensation
    await tabButtons.nth(2).click();
    await page.waitForTimeout(800);
    await page.screenshot({ path: path.join(ARTIFACT_DIR, "m21_transfer_tab3_compensation.png"), fullPage: false });

    // Tab 4: Technical
    await tabButtons.nth(3).click();
    await page.waitForTimeout(800);
    await page.screenshot({ path: path.join(ARTIFACT_DIR, "m21_transfer_tab4_technical.png"), fullPage: false });

    // Tab 5: Handover
    await tabButtons.nth(4).click();
    await page.waitForTimeout(800);
    await page.screenshot({ path: path.join(ARTIFACT_DIR, "m21_transfer_tab5_handover.png"), fullPage: false });

    // Tab 7: Approval
    await tabButtons.nth(6).click();
    await page.waitForTimeout(800);
    await page.screenshot({ path: path.join(ARTIFACT_DIR, "m21_transfer_tab7_approval.png"), fullPage: false });

    // Tab 8: Document Vault
    await tabButtons.nth(7).click();
    await page.waitForTimeout(800);
    await page.screenshot({ path: path.join(ARTIFACT_DIR, "m21_transfer_tab8_vault.png"), fullPage: false });

    // Step 8: Execute Axe Core Accessibility Audit
    console.log("[A11Y-TEST] Running Axe Core WCAG 2.2 AA accessibility audit on form...");
    const axeResults = await new AxeBuilder({ page })
      .include(".d365-form")
      .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"])
      .analyze();

    const criticalSerious = axeResults.violations.filter(v => v.impact === "critical" || v.impact === "serious");
    console.log(`[A11Y-TEST] Axe violations found: total=${axeResults.violations.length}, critical/serious=${criticalSerious.length}`);

    if (criticalSerious.length > 0) {
      console.error("[A11Y-TEST] Critical/Serious Violations:", JSON.stringify(criticalSerious, null, 2));
    }
    expect(criticalSerious.length).toBe(0);
    console.log("[A11Y-TEST] PASSED: 0 critical/serious WCAG violations on M21 Transfer 8-Tab form!");
  });
});
