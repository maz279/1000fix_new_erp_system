// J08 — Marketplace seller: onboarding → job → payout · 5 steps. P07 live.
import { test, expect } from "@playwright/test";
import { PORTALS, loginOdoo, openWorkspace, openScreenViaTellMe } from "./helpers";

test("J08 marketplace seller onboarding to payout", async ({ page }) => {
  await test.step("1 M12: seller KYC surface (P07 shell renders)", async () => {
    await page.goto(`${PORTALS.seller}/`);
    await expect(page.locator("main")).toBeVisible();
  });

  await test.step("2 M12: seller agreement/quote surfaces render", async () => {
    await page.goto(`${PORTALS.seller}/jobs`);
    await expect(page.locator("main")).toBeVisible();
  });

  await test.step("3 P07: seller dashboard + settlements render", async () => {
    await page.goto(`${PORTALS.seller}/scorecard`);
    await expect(page.locator("main")).toBeVisible();
    await page.goto(`${PORTALS.seller}/settlements`);
    await expect(page.locator("main")).toBeVisible();
  });

  await test.step("4 M12: marketplace broadcast surface in P03", async () => {
    await loginOdoo(page);
    await openWorkspace(page);
    const title = await openScreenViaTellMe(page, "Marketplace");
    expect(title.length).toBeGreaterThan(0);
  });

  await test.step("5 M53: payout/settlement surface opens", async () => {
    const title = await openScreenViaTellMe(page, "Settlement");
    expect(title.length).toBeGreaterThan(0);
  });
});
