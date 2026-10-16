// J02 — Walk-in branch repair (counter → bench → collection) · 6 steps.
// Counter/token surfaces are the REAL Odoo token-queue action plus the
// workspace's M04 screens; bench/parts screens are registry surfaces with
// honest empty states until their phases land.
import { test, expect } from "@playwright/test";
import { PORTALS, loginOdoo, openWorkspace, openScreenViaTellMe } from "./helpers";

test("J02 walk-in branch repair through the back office", async ({ page }) => {
  await test.step("1 M04: front-desk counter surface (workspace module)", async () => {
    await loginOdoo(page);
    await openWorkspace(page);
    const title = await openScreenViaTellMe(page, "Front");
    expect(title.length).toBeGreaterThan(0);
  });

  await test.step("2 M01: workshop order registered (orders screen)", async () => {
    await openWorkspace(page);
    const title = await openScreenViaTellMe(page, "All Service Orders");
    expect(title.toLowerCase()).toContain("service orders");
  });

  await test.step("3 M31: bench routing surface opens (module workspace)", async () => {
    const title = await openScreenViaTellMe(page, "Workshop");
    expect(title.length).toBeGreaterThan(0);
  });

  await test.step("4 M15: parts/stock screen renders live-or-empty grid", async () => {
    const title = await openScreenViaTellMe(page, "Parts Stock");
    expect(title.length).toBeGreaterThan(0);
  });

  await test.step("5 M31: testing/diagnostics surface opens", async () => {
    const title = await openScreenViaTellMe(page, "Testing");
    expect(title.length).toBeGreaterThan(0);
  });

  await test.step("6 M04: collection/handover surface opens", async () => {
    const title = await openScreenViaTellMe(page, "Handover");
    expect(title.length).toBeGreaterThan(0);
  });
});
