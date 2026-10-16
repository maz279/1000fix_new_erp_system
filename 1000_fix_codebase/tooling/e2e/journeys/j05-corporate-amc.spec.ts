// J05 — Corporate AMC: contract → PM → billing · 5 steps. P04 is live.
import { test, expect } from "@playwright/test";
import { PORTALS, loginOdoo, openWorkspace, openScreenViaTellMe } from "./helpers";

test("J05 corporate AMC contract to consolidated billing", async ({ page }) => {
  await test.step("1 M07: CRM opportunity surface opens", async () => {
    await loginOdoo(page);
    await openWorkspace(page);
    const title = await openScreenViaTellMe(page, "Lead");
    expect(title.length).toBeGreaterThan(0);
  });

  await test.step("2 M08: contract/AMC surface opens", async () => {
    const title = await openScreenViaTellMe(page, "Contract");
    expect(title.toLowerCase()).toContain("contract");
  });

  await test.step("3 M17/P04: corporate estate registry renders", async () => {
    await page.goto(`${PORTALS.corporate}/estate`);
    await expect(page.locator("main")).toBeVisible();
  });

  await test.step("4 M08: preventive-maintenance surface opens", async () => {
    await loginOdoo(page);
    await openWorkspace(page);
    const title = await openScreenViaTellMe(page, "Maintenance");
    expect(title.length).toBeGreaterThan(0);
  });

  await test.step("5 M20/P04: consolidated B2B invoice surface renders", async () => {
    await page.goto(`${PORTALS.corporate}/invoices`);
    await expect(page.locator("main")).toBeVisible();
  });
});
