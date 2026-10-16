// J07 — Trade-in → refurbish → graded resale · 5 steps.
import { test, expect } from "@playwright/test";
import { PORTALS, loginOdoo, openWorkspace, openScreenViaTellMe } from "./helpers";

test("J07 trade-in to graded resale", async ({ page }) => {
  await test.step("1 M14: trade-in valuation surface opens", async () => {
    await loginOdoo(page);
    await openWorkspace(page);
    const title = await openScreenViaTellMe(page, "Trade");
    expect(title.length).toBeGreaterThan(0);
  });

  await test.step("2 M14: provenance/IMEI screening surface opens", async () => {
    const title = await openScreenViaTellMe(page, "Screening");
    expect(title.length).toBeGreaterThan(0);
  });

  await test.step("3 M06: data-destruction surface opens", async () => {
    const title = await openScreenViaTellMe(page, "Destruction");
    expect(title.length).toBeGreaterThan(0);
  });

  await test.step("4 M31: refurb/QA surface opens", async () => {
    const title = await openScreenViaTellMe(page, "Refurb");
    expect(title.length).toBeGreaterThan(0);
  });

  await test.step("5 M14: grading surface opens", async () => {
    const title = await openScreenViaTellMe(page, "Grading");
    expect(title.length).toBeGreaterThan(0);
  });
});
