// expansion.spec.ts — P04-M06-T08 / P04-M08-T09: layout under text expansion.
//
// Bengali typically runs 15-30% longer than English (UX-007). A layout that
// survives the English string and clips the Bengali one ships a broken
// product to the majority locale. Each workspace route renders in BOTH
// locales; any element whose content overflows its box without being an
// intentional scroll container fails.
import { test, expect } from "@playwright/test";
import { W1_ROUTES } from "../playwright.config";

const LOGIN = { user: process.env.FIX_A11Y_USER ?? "admin", password: process.env.FIX_A11Y_PASSWORD ?? "" };

async function setLocale(page: import("@playwright/test").Page, locale: "bn" | "en") {
  // Odoo honours the lang cookie; the seeded bn_BD language must exist.
  await page.context().addCookies([{ name: "frontend_lang", value: locale, url: page.url() }]);
}

test.beforeEach(async ({ page }) => {
  if (!LOGIN.password) {
    test.skip(true, "FIX_A11Y_PASSWORD not set - runtime expansion scan skipped");
  }
  await page.goto("/web/login");
  await page.fill("input[name='login']", LOGIN.user);
  await page.fill("input[name='password']", LOGIN.password);
  await page.click("button[type='submit']");
  await expect(page).toHaveURL(/\/web/);
});

for (const route of W1_ROUTES) {
  for (const locale of ["bn", "en"] as const) {
    test(`expansion: ${route.name} (${locale}) has no clipped labels`, async ({ page }) => {
      await setLocale(page, locale);
      await page.goto(route.path);
      await page.waitForLoadState("networkidle");
      // An element clips its content when it overflows without scrolling
      // being the intent (overflow hidden/auto on the element itself).
      const clipped = await page.evaluate(() => {
        const offenders: string[] = [];
        for (const el of document.querySelectorAll<HTMLElement>("label, th, .o_field_widget, button, .btn, h1, h2, h3")) {
          const style = getComputedStyle(el);
          const intentionalScroll = style.overflowX === "auto" || style.overflowX === "scroll";
          if (!intentionalScroll && el.scrollWidth > el.clientWidth + 1) {
            offenders.push(`${el.tagName.toLowerCase()}.${el.className.split(" ")[0]}: ${el.scrollWidth}>${el.clientWidth}`);
          }
        }
        return offenders;
      });
      expect(clipped, `clipped elements in ${locale}: ${clipped.join("; ")}`).toEqual([]);
    });
  }
}
