// J10 — Month-end close → Mushak 9.1 VAT filing · 4 steps.
import { test, expect } from "@playwright/test";
import { PORTALS, loginOdoo, openWorkspace, openScreenViaTellMe } from "./helpers";

test("J10 month-end close to VAT return", async ({ page }) => {
  await test.step("1 M19: period-close surface opens", async () => {
    await loginOdoo(page);
    await openWorkspace(page);
    const title = await openScreenViaTellMe(page, "Close");
    expect(title.length).toBeGreaterThan(0);
  });

  await test.step("2 M50: cash/treasury surface opens", async () => {
    const title = await openScreenViaTellMe(page, "Cash");
    expect(title.length).toBeGreaterThan(0);
  });

  await test.step("3 M19: financial statements surface opens", async () => {
    const title = await openScreenViaTellMe(page, "Ledger");
    expect(title.length).toBeGreaterThan(0);
  });

  await test.step("4 M51: VAT/Mushak surface opens", async () => {
    const title = await openScreenViaTellMe(page, "VAT");
    expect(title.length).toBeGreaterThan(0);
  });
});
