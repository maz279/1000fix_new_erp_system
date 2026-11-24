// J16 — rebuilt portal surfaces (2026-11-24).
//
// The J01–J15 journeys were written against the pre-rebuild portals (routes
// such as /booking and /estimates that no longer exist). This spec is the
// Gate-2 smoke gate for the current build: every portal serves its public
// landing and login, and every protected surface redirects to /login.
import { test, expect } from "@playwright/test";
import { PORTALS } from "./helpers";

const SURFACES = [
  { name: "customer", landing: /Customer Portal|কাস্টমার/i, protected: "/dashboard" },
  { name: "corporate", landing: /Corporate|কর্পোরেট/i, protected: "/dashboard" },
  { name: "analytics", landing: /Analytics|Executive|বিশ্লেষণ/i, protected: "/dashboards" },
  { name: "seller", landing: /Seller|বিক্রেতা/i, protected: "/dashboard" },
  { name: "brand", landing: /Brand Partner|ব্র্যান্ড/i, protected: "/dashboard" },
  { name: "agentConsole", landing: /Contact Centre|কন্টাক্ট সেন্টার/i, protected: "/queue" },
  { name: "partner", landing: /Partner|পার্টনার/i, protected: "/dashboard" },
  { name: "vendor", landing: /Vendor|Supplier|সরবরাহকারী/i, protected: "/dashboard" },
] as const;

for (const surface of SURFACES) {
  test(`${surface.name}: landing, login and the protected boundary`, async ({ page }) => {
    const base = PORTALS[surface.name];

    await page.goto(`${base}/`, { waitUntil: "domcontentloaded" });
    await expect(page.locator("body")).toContainText(surface.landing);

    await page.goto(`${base}/login`, { waitUntil: "domcontentloaded" });
    await expect(page.locator("body")).toContainText(/sign in|সাইন ইন/i);

    await page.goto(`${base}${surface.protected}`, { waitUntil: "domcontentloaded" });
    await page.waitForURL(/\/login\?next=/, { timeout: 15_000 });
  });
}
