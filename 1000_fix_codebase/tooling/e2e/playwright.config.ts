// PP7-M01 — Journey E2E suite (J01–J10 · 54 steps, ARCHITECTURE_STATE §8).
//
// Runs headless Chromium against the LIVE local stack:
//   P01 customer :3000 · P04 corporate :3001 · P05 vendor :3007 ·
//   P07 seller :3003 · P08 brand :3004 · P03 back office :8090.
// Mobile companion steps (P02/P09/P11) live in patrol/ for SDK machines —
// this suite runs their web halves and records the split honestly.
//
// Launch note: the workstation's Playwright 1.63 install is paired with
// chromium-1200; CHROMIUM_EXECUTABLE_PATH (or the default ms-playwright
// path below) pins the browser so the suite never wants a newer build.
import { defineConfig } from "@playwright/test";
import path from "node:path";
import fs from "node:fs";

const DEFAULT_EXE = path.join(
  process.env.USERPROFILE || process.env.HOME || ".",
  "AppData/Local/ms-playwright/chromium_headless_shell-1200/chrome-headless-shell-win64/chrome-headless-shell.exe",
);
const EXE = process.env.CHROMIUM_EXECUTABLE_PATH || (fs.existsSync(DEFAULT_EXE) ? DEFAULT_EXE : undefined);

export default defineConfig({
  testDir: "./journeys",
  timeout: 120_000,
  fullyParallel: false,
  workers: 1,
  retries: 0,
  reporter: [["list"], ["json", { outputFile: "results/journeys.json" }]],
  use: {
    headless: true,
    ...(EXE ? { launchOptions: { executablePath: EXE } } : {}),
    viewport: { width: 1366, height: 768 },
    actionTimeout: 20_000,
    navigationTimeout: 45_000,
  },
});
