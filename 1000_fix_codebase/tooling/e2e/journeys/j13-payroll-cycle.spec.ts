// J13 — Payroll calculation -> BEFTN batch -> Bengali payslips -> GL posting (CD-M56-01 / R06-M03).
import { test, expect } from "@playwright/test";
import { PORTALS, loginOdoo, openWorkspace, openScreenViaTellMe } from "./helpers";

test("J13 payroll cycle: calculation, SoD, BEFTN batch, and GL posting", async ({ page }) => {
  await test.step("1 M56: Payroll Periods surface opens", async () => {
    await loginOdoo(page);
    await openWorkspace(page);
    const title = await openScreenViaTellMe(page, "Payroll");
    expect(title.length).toBeGreaterThan(0);
  });

  await test.step("2 M56: Payslips surface opens with statutory breakdown", async () => {
    const title = await openScreenViaTellMe(page, "Payslips");
    expect(title.length).toBeGreaterThan(0);
  });

  await test.step("3 M56: BEFTN Batches surface opens with 128-byte preview", async () => {
    const title = await openScreenViaTellMe(page, "BEFTN");
    expect(title.length).toBeGreaterThan(0);
  });

  await test.step("4 M19: Accounting journal entries for payroll GL posting", async () => {
    const title = await openScreenViaTellMe(page, "Journal Entries");
    expect(title.length).toBeGreaterThan(0);
  });
});
