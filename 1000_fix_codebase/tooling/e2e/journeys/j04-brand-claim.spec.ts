// J04 — Brand warranty claim → reimbursement · 5 steps. P08 portal is live.
import { test, expect } from "@playwright/test";
import { PORTALS, loginOdoo, openWorkspace, openScreenViaTellMe } from "./helpers";

test("J04 brand warranty claim to reimbursement", async ({ page }) => {
  await test.step("1 M01: entitlement evaluation surface opens", async () => {
    await loginOdoo(page);
    await openWorkspace(page);
    const title = await openScreenViaTellMe(page, "Entitlement");
    expect(title.length).toBeGreaterThan(0);
  });

  await test.step("2 M09: claim surface in the workspace", async () => {
    const title = await openScreenViaTellMe(page, "Claim");
    expect(title.toLowerCase()).toContain("claim");
  });

  await test.step("3 M24: evidence/document surface opens", async () => {
    const title = await openScreenViaTellMe(page, "Document");
    expect(title.length).toBeGreaterThan(0);
  });

  await test.step("4 P08: brand portal renders its claim surfaces", async () => {
    await page.goto(`${PORTALS.brand}/`);
    await expect(page.locator("main")).toBeVisible();
    await page.goto(`${PORTALS.brand}/reconciliation`);
    await expect(page.locator("main")).toBeVisible();
  });

  await test.step("5 M20: brand-receivable surface opens", async () => {
    await loginOdoo(page);
    await openWorkspace(page);
    const title = await openScreenViaTellMe(page, "Invoice");
    expect(title.length).toBeGreaterThan(0);
  });
});
