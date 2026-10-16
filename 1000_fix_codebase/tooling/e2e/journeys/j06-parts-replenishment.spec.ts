// J06 — Parts stockout → replenishment → payment · 7 steps. P05 vendor live.
import { test, expect } from "@playwright/test";
import { PORTALS, loginOdoo, openWorkspace, openScreenViaTellMe } from "./helpers";

test("J06 parts stockout to replenishment payment", async ({ page }) => {
  await test.step("1 M15: on-hand stock surface (alert context)", async () => {
    await loginOdoo(page);
    await openWorkspace(page);
    const title = await openScreenViaTellMe(page, "Stock");
    expect(title.length).toBeGreaterThan(0);
  });

  await test.step("2 M43: demand-planning surface opens", async () => {
    const title = await openScreenViaTellMe(page, "Demand");
    expect(title.length).toBeGreaterThan(0);
  });

  await test.step("3 M16: RFQ/procurement surface opens", async () => {
    const title = await openScreenViaTellMe(page, "Requisition");
    expect(title.length).toBeGreaterThan(0);
  });

  await test.step("4 M42: supplier-gate surface opens", async () => {
    const title = await openScreenViaTellMe(page, "Supplier");
    expect(title.length).toBeGreaterThan(0);
  });

  await test.step("5 P05: vendor portal renders PO + invoice surfaces", async () => {
    await page.goto(`${PORTALS.vendor}/`);
    await expect(page.locator("main")).toBeVisible();
    await page.goto(`${PORTALS.vendor}/invoices`);
    await expect(page.locator("main")).toBeVisible();
  });

  await test.step("6 M41: warehouse receiving surface opens", async () => {
    await loginOdoo(page);
    await openWorkspace(page);
    const title = await openScreenViaTellMe(page, "Warehouse");
    expect(title.length).toBeGreaterThan(0);
  });

  await test.step("7 M16: three-way-match surface opens", async () => {
    const title = await openScreenViaTellMe(page, "Purchase");
    expect(title.length).toBeGreaterThan(0);
  });
});
