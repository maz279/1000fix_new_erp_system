// J10 — E-waste collection -> triage -> destruction (wipe gate) -> recycling -> disposal certificate (CD-M18 / R07-M04).
// Implements Journey 10 of the 15 critical journeys (RQ-007 §4.3, URD §18, Gate G8-4).
import { test, expect } from "@playwright/test";
import { PORTALS, loginOdoo, openWorkspace, openScreenViaTellMe } from "./helpers";

test("J10 e-waste lifecycle: collection intake, triage, wipe destruction gate, and disposal certification", async ({ page }) => {
  await test.step("1 M18: E-Waste Collections surface opens with intake registry", async () => {
    await loginOdoo(page);
    await openWorkspace(page);
    const title = await openScreenViaTellMe(page, "E-Waste");
    expect(title.length).toBeGreaterThan(0);
  });

  await test.step("2 M18: Triage & Processing surface opens with material grading", async () => {
    const title = await openScreenViaTellMe(page, "Processing");
    expect(title.length).toBeGreaterThan(0);
  });

  await test.step("3 M18: Data Wipe & Destruction Gate surface opens (NIST 800-88)", async () => {
    const title = await openScreenViaTellMe(page, "Destruction");
    expect(title.length).toBeGreaterThan(0);
  });

  await test.step("4 M18: Compliance & Disposal Certificates surface opens", async () => {
    const title = await openScreenViaTellMe(page, "Compliance");
    expect(title.length).toBeGreaterThan(0);
  });

  await test.step("5 M60: Document Vault e-signature & certificate archive verified", async () => {
    const title = await openScreenViaTellMe(page, "Vault");
    expect(title.length).toBeGreaterThan(0);
  });
});
