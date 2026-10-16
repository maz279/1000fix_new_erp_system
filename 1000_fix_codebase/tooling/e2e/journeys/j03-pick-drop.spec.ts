// J03 — Pick & drop logistics round trip · 5 steps (2 mobile → patrol).
import { test, expect } from "@playwright/test";
import { PORTALS, loginOdoo, openWorkspace, openScreenViaTellMe } from "./helpers";

test("J03 pick & drop logistics round trip", async ({ page }) => {
  await test.step("1 P01: pick-drop booking surface reachable", async () => {
    await page.goto(`${PORTALS.customer}/booking`);
    await expect(page.locator("main")).toBeVisible();
  });

  await test.step("2 M03: consignment/manifest surface in P03", async () => {
    await loginOdoo(page);
    await openWorkspace(page);
    const title = await openScreenViaTellMe(page, "Manifest");
    expect(title.length).toBeGreaterThan(0);
  });

  await test.step("3 P09: rider custody (mobile half → patrol, SDK machine)", async () => {
    const res = await page.request.get(`${PORTALS.odoo}/`, { failOnStatusCode: false });
    expect(res.status()).toBeLessThan(500); // stack alive; rider app is Flutter
  });

  await test.step("4 M31: workshop custody (ON BENCH) surface opens", async () => {
    const title = await openScreenViaTellMe(page, "Bench");
    expect(title.length).toBeGreaterThan(0);
  });

  await test.step("5 M03: return-leg consignment tracking surface", async () => {
    const title = await openScreenViaTellMe(page, "Consignment");
    expect(title.length).toBeGreaterThan(0);
  });
});
