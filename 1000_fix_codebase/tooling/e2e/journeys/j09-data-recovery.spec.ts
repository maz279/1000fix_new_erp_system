// J09 — Data recovery case (sealed custody → certificate) · 4 steps.
import { test, expect } from "@playwright/test";
import { loginOdoo, openWorkspace, openScreenViaTellMe } from "./helpers";

test("J09 data recovery case sealed custody", async ({ page }) => {
  await test.step("1 M06: case-intake surface opens", async () => {
    await loginOdoo(page);
    await openWorkspace(page);
    const title = await openScreenViaTellMe(page, "Recovery");
    expect(title.length).toBeGreaterThan(0);
  });

  await test.step("2 M06: custody surface opens", async () => {
    const title = await openScreenViaTellMe(page, "Custody");
    expect(title.length).toBeGreaterThan(0);
  });

  await test.step("3 M06: evaluation/quotation surface opens", async () => {
    const title = await openScreenViaTellMe(page, "Evaluation");
    expect(title.length).toBeGreaterThan(0);
  });

  await test.step("4 M06: secure-handover surface opens", async () => {
    const title = await openScreenViaTellMe(page, "Handover");
    expect(title.length).toBeGreaterThan(0);
  });
});
