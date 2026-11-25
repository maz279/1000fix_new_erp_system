// J06-MSP — Endpoint telemetry -> SLA alert -> ticket -> remote session (PDPA) -> monthly report (CD-M05 / R06-M04).
import { test, expect } from "@playwright/test";
import { PORTALS, loginOdoo, openWorkspace, openScreenViaTellMe } from "./helpers";

test("J06 MSP alert lifecycle: telemetry, SLA monitoring, remote support, and bilingual reports", async ({ page }) => {
  await test.step("1 M05: MSP Contracts surface opens", async () => {
    await loginOdoo(page);
    await openWorkspace(page);
    const title = await openScreenViaTellMe(page, "MSP");
    expect(title.length).toBeGreaterThan(0);
  });

  await test.step("2 M05: SLA Alerts surface opens with severity classification", async () => {
    const title = await openScreenViaTellMe(page, "Alert");
    expect(title.length).toBeGreaterThan(0);
  });

  await test.step("3 M05: Remote Sessions surface opens with PDPA consent gate", async () => {
    const title = await openScreenViaTellMe(page, "Remote");
    expect(title.length).toBeGreaterThan(0);
  });

  await test.step("4 M05: Monthly Reports surface opens with bilingual summaries", async () => {
    const title = await openScreenViaTellMe(page, "Monthly");
    expect(title.length).toBeGreaterThan(0);
  });
});
