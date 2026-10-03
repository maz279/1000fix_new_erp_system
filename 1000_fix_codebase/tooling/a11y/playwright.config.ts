// P04-M06-T07/T08 — accessibility + expansion harness (UX-005, UX-007).
//
// Two projects:
//   axe        — @axe-core/playwright scan of every W1 workspace route,
//                WCAG 2.2 AA ruleset (PS-04). Violations fail the build.
//   expansion  — render each route in bn and en; any element whose content
//                overflows its box (scrollWidth > clientWidth without an
//                intentional scroll container) fails (UX-007 expansion).
//
// The target is the local Odoo runtime (compose `web` on 127.0.0.1:8069).
// Without it the suite reports SKIP — honestly — and the static halves
// (tooling/a11y/check-expansion-static.py, FF-25 po completeness) carry the
// workstation. CI stage 12 runs this suite with the stack up.
import { defineConfig } from "@playwright/test";

const BASE_URL = process.env.FIX_A11Y_BASE_URL ?? "http://127.0.0.1:8069";

// W1 workspace routes (P04-M06-T03) — action/menu xml ids as Odoo renders
// them (#action= / #menu_id=). Keep in step with the workspace menus; FF-27
// (check_portal_contract.py) proves the ids exist.
export const W1_ROUTES = [
  { name: "service-intake", path: "/web#action=cd_front_desk.action_fix_token_queue" },
  { name: "service-orders", path: "/web#action=cd_service_order.action_fix_service_order" },
  { name: "party-master", path: "/web#action=cd_party_master.action_fix_parties" },
  { name: "device-registry", path: "/web#action=cd_device_registry.action_fix_device" },
  { name: "catalogue", path: "/web#action=cd_catalogue.action_fix_catalogue" },
  { name: "administration", path: "/web#menu_id=cd_rbac_ext.menu_ws_administration" },
];

export default defineConfig({
  testDir: "./tests",
  timeout: 60_000,
  retries: 0,
  use: { baseURL: BASE_URL },
  projects: [
    { name: "axe", testMatch: /axe\.spec\.ts/ },
    { name: "expansion", testMatch: /expansion\.spec\.ts/ },
  ],
});
