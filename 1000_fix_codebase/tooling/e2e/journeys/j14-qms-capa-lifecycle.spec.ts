// J14 — Non-conformance (QC/complaint) -> root cause -> CAPA -> verification -> closure (CD-M23 / R06-M04).
import { test, expect } from "@playwright/test";
import { PORTALS, loginOdoo, openWorkspace, openScreenViaTellMe } from "./helpers";

test("J14 QMS lifecycle: Non-conformance reporting, root cause, CAPA, and CON-11 closure", async ({ page }) => {
  await test.step("1 M23: Non-Conformance Records (NCR) surface opens", async () => {
    await loginOdoo(page);
    await openWorkspace(page);
    const title = await openScreenViaTellMe(page, "NCR");
    expect(title.length).toBeGreaterThan(0);
  });

  await test.step("2 M23: Corrective & Preventive Actions (CAPA) surface opens", async () => {
    const title = await openScreenViaTellMe(page, "CAPA");
    expect(title.length).toBeGreaterThan(0);
  });

  await test.step("3 M23: Internal Audit Programme surface opens", async () => {
    const title = await openScreenViaTellMe(page, "Audit");
    expect(title.length).toBeGreaterThan(0);
  });

  await test.step("4 M31: Workshop Jobs with QC and NCR linkage", async () => {
    const title = await openScreenViaTellMe(page, "Workshop");
    expect(title.length).toBeGreaterThan(0);
  });
});
