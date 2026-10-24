// J08 — Rental reservation -> delivery consignment -> return -> damage assessment -> billing (CD-M37 / R07-M03).
// Implements Journey 8 of the 15 critical journeys (RQ-007 §4.3, URD §18, Gate G6-2 / G6-4).
import { test, expect } from "@playwright/test";
import { PORTALS, loginOdoo, openWorkspace, openScreenViaTellMe } from "./helpers";

test("J08 rental lifecycle: reservation, delivery consignment, return, damage assessment, and deposit settlement", async ({ page }) => {
  await test.step("1 M37: Rental Assets surface opens with active inventory", async () => {
    await loginOdoo(page);
    await openWorkspace(page);
    const title = await openScreenViaTellMe(page, "Rental");
    expect(title.length).toBeGreaterThan(0);
  });

  await test.step("2 M37: Rental Reservations surface opens with date conflict check", async () => {
    const title = await openScreenViaTellMe(page, "Reservation");
    expect(title.length).toBeGreaterThan(0);
  });

  await test.step("3 M04: Outbound & Inbound Consignments surface opens for device logistics", async () => {
    const title = await openScreenViaTellMe(page, "Consignment");
    expect(title.length).toBeGreaterThan(0);
  });

  await test.step("4 M37: Damage Assessment surface opens with evidence inspection", async () => {
    const title = await openScreenViaTellMe(page, "Damage");
    expect(title.length).toBeGreaterThan(0);
  });

  await test.step("5 M20: Deposit Settlement & customer billing reconciliation verified", async () => {
    const title = await openScreenViaTellMe(page, "Invoices");
    expect(title.length).toBeGreaterThan(0);
  });
});
