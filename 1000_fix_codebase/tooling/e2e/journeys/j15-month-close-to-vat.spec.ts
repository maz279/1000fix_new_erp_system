// J15 — Month-end close → Mushak 9.1 VAT filing · 5 steps.
// Milestone R05-M05-T04 / Gate G4-07.
import { test, expect } from "@playwright/test";
import { PORTALS, loginOdoo, openWorkspace, openScreenViaTellMe } from "./helpers";

test("J15 month-end close to Mushak 9.1 VAT return", async ({ page }) => {
  await test.step("1 M19: period-close surface opens", async () => {
    await loginOdoo(page);
    await openWorkspace(page);
    const title = await openScreenViaTellMe(page, "Close");
    expect(title.length).toBeGreaterThan(0);
  });

  await test.step("2 M50: cash & treasury surface opens", async () => {
    const title = await openScreenViaTellMe(page, "Cash");
    expect(title.length).toBeGreaterThan(0);
  });

  await test.step("3 M19: financial statements & ledger surface opens", async () => {
    const title = await openScreenViaTellMe(page, "Ledger");
    expect(title.length).toBeGreaterThan(0);
  });

  await test.step("4 M51: Mushak 9.1 VAT return surface opens", async () => {
    const title = await openScreenViaTellMe(page, "VAT");
    expect(title.length).toBeGreaterThan(0);
  });

  await test.step("5 M51: statutory return filing & submission surface verifies", async () => {
    const title = await openScreenViaTellMe(page, "Return");
    expect(title.toLowerCase()).toContain("return");
  });
});
