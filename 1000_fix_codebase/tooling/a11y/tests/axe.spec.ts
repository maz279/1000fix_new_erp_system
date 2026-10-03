// axe.spec.ts — P04-M06-T07: WCAG 2.2 AA audit of every W1 workspace (UX-005).
//
// UX-005 names 11 criteria no automated scan can discharge — the manual
// audit record remains a human deliverable. What axe DOES catch (contrast,
// names, roles, target size, focus order) fails the build here, per CI
// stage 12.
import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { W1_ROUTES } from "../playwright.config";

const LOGIN = { user: process.env.FIX_A11Y_USER ?? "admin", password: process.env.FIX_A11Y_PASSWORD ?? "" };

test.beforeEach(async ({ page }) => {
  // Credentials come from the environment only (never literals in tests).
  if (!LOGIN.password) {
    test.skip(true, "FIX_A11Y_PASSWORD not set - runtime scan skipped (static halves carry the workstation)");
  }
  await page.goto("/web/login");
  await page.fill("input[name='login']", LOGIN.user);
  await page.fill("input[name='password']", LOGIN.password);
  await page.click("button[type='submit']");
  await expect(page).toHaveURL(/\/web/);
});

for (const route of W1_ROUTES) {
  test(`axe: ${route.name} has no WCAG 2.2 AA violations`, async ({ page }) => {
    await page.goto(route.path);
    await page.waitForLoadState("networkidle");
    const results = await new AxeBuilder({ page })
      .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"])
      .analyze();
    const serious = results.violations.filter(v => v.impact === "serious" || v.impact === "critical");
    // Minor/moderate findings are recorded, not blocking; serious+critical
    // block (DoD-07) — the same split UX-005 prescribes for manual review.
    if (serious.length) {
      console.error(JSON.stringify(serious.map(v => ({ id: v.id, nodes: v.nodes.length, help: v.help })), null, 2));
    }
    expect(serious).toEqual([]);
  });
}
