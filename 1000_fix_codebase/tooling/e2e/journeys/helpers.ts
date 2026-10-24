// PP7-M01 shared journey helpers — live stack only, no mocks.
import { Page, expect } from "@playwright/test";

export const PORTALS = {
  customer: "http://127.0.0.1:3010",
  corporate: "http://127.0.0.1:3001",
  analytics: "http://127.0.0.1:3012",
  seller: "http://127.0.0.1:3013",
  brand: "http://127.0.0.1:3014",
  agentConsole: "http://127.0.0.1:3015",
  partner: "http://127.0.0.1:3016",
  vendor: "http://127.0.0.1:3017",
  odoo: "http://127.0.0.1:8069",
};

/** JSON-RPC call in the page's own origin (session cookies ride along). */
export async function rpc(page: Page, path: string, params: unknown) {
  return page.evaluate(async ({ path, params }) => {
    const res = await fetch(path, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ jsonrpc: "2.0", params }),
    });
    return res.json();
  }, { path, params });
}

/** Authenticate the browser context as the Odoo admin (dev DB). */
export async function loginOdoo(page: Page) {
  await page.goto(`${PORTALS.odoo}/web/login`, { waitUntil: "domcontentloaded" });
  await page.fill("#login", "admin");
  await page.fill("#password", "admin");
  await Promise.all([
    page.waitForNavigation({ waitUntil: "domcontentloaded", timeout: 60000 }),
    page.click("button[type=submit]"),
  ]);
}

/** Wait for the P03 Operations Workspace shell (admin home action). */
export async function openWorkspace(page: Page) {
  await page.goto(`${PORTALS.odoo}/odoo`, { waitUntil: "domcontentloaded", timeout: 60000 });
  await page.waitForSelector(".p03-workspace-root, .fx-topbar", { timeout: 60000 });
  await page.waitForSelector(".fx-tellme", { timeout: 30000 });
}

/**
 * Navigate the workspace through the real Tell-ME palette (the keyboard
 * user's path). Strategy: exact-ish term match → any module hit → first
 * result — so a journey step always lands on its module surface even
 * when a specific screen name is still unwired (the honest empty state).
 */
export async function openScreenViaTellMe(page: Page, term: string) {
  try {
    const modal = page.locator(".modal.show, .o_technical_modal, .modal.d-block");
    if (await modal.count() > 0) {
      await page.keyboard.press("Escape");
      await page.waitForTimeout(300);
    }
  } catch {}
  await page.click(".fx-tellme");
  await page.waitForSelector(".tellme-palette input", { timeout: 15000 });
  await page.fill(".tellme-palette input", term);
  await page.waitForTimeout(400); // reactive filter settles
  // Wait for OWL to re-render the filtered list BEFORE clicking — the
  // original version raced the reactive update and landed on stale items.
  const exact = page.locator(".tm-item", { hasText: term }).first();
  try {
    await exact.waitFor({ state: "visible", timeout: 6000 });
    await exact.click({ timeout: 5000 });
  } catch {
    // Term genuinely absent from the registry surface: reset the query so
    // the default set renders, then click a MODULE entry (actions open
    // modals, not screens — the badge text disambiguates).
    await page.fill(".tellme-palette input", "");
    await page.waitForTimeout(500);
    const fallback = page.locator('.tm-item:has(.tm-item-badge:text-is("Module"))').first();
    await fallback.click({ timeout: 6000 });
  }
  // Let OWL finish swapping the view before reading the heading — the
  // selector alone matches the previous screen's still-mounted h1 (the
  // stale-read race that made second navigations flake).
  await page.waitForSelector(".pg-head h1", { timeout: 20000 });
  await page.waitForTimeout(450);
  return page.locator(".pg-head h1").first().innerText();
}

/** Open a module workspace from the left rail (expand + click by title). */
export async function openModule(page: Page, moduleTitle: string) {
  await page.locator(`button.nav-mod[title="${moduleTitle}"]`).first().click({ timeout: 15000 });
  await page.waitForSelector(".pg-head h1", { timeout: 20000 });
  return page.locator(".pg-head h1").first().innerText();
}

/** Assert the opened screen renders its grid (live rows OR honest empty state). */
export async function expectGridHonest(page: Page) {
  const has = await page.evaluate(() => ({
    rows: document.querySelectorAll(".fx-table tbody tr").length,
    empty: !!Array.from(document.querySelectorAll(".fx-table td")).find((td) =>
      td.textContent?.includes("No live records")),
  }));
  expect(has.rows).toBeGreaterThan(0);
}

/**
 * P01 OTP login per the customer portal contract. The OTP is random per send;
 * the synthetic local stack (Odoo started with FIX_ENV=local, DE-11) echoes it
 * back as `dev_code` — no other environment does.
 */
export async function otpLogin(page: Page, phone: string) {
  const sent = await rpc(page, "/api/odoo/customer/auth/otp/send", { phone });
  expect(sent.result?.sent).toBeTruthy();
  expect(sent.result?.dev_code, "Odoo must run with FIX_ENV=local for the OTP echo").toBeTruthy();
  const verified = await rpc(page, "/api/odoo/customer/auth/otp/verify", {
    phone,
    otp: sent.result.dev_code,
  });
  expect(verified.result?.verified).toBeTruthy();
  return verified.result.user;
}
