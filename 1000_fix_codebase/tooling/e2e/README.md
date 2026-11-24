# E2E journeys

Two generations of journeys live here:

- **`j16-portal-surfaces.spec.ts` — current (2026-11-24).** Gate-2 smoke
  gate for the rebuilt portals: every portal serves its public landing and
  login, and every protected surface redirects to `/login?next=...`.
  Ports are the live local stack: 3000 customer, 3001 corporate,
  3002 analytics, 3003 seller, 3004 brand, 3005 agent console,
  3006 partner, 3007 vendor, 8090 Odoo (fix_dev).

- **`j01`–`j15` — pre-rebuild.** They were authored against the previous
  portal routes (`/booking`, `/estimates`, old port migration numbers
  3010–3017) and Odoo 8069. The 2026-11-24 rebuild replaced those routes
  with landing/login/dashboard surfaces, so these journeys fail at their
  first step and must be re-authored against the current UI before they
  can be used as UAT sign-off evidence. Do not report them as green.

Run the current smoke gate with:

```bash
cd tooling/e2e
npx playwright test journeys/j16-portal-surfaces.spec.ts        # developer stack
E2E_UAT=1 npx playwright test journeys/j16-portal-surfaces.spec.ts   # UAT stack (3400-3407)
```

`E2E_UAT=1` points the same contract at the single-host synthetic UAT stack
(`infra/compose/docker-compose.uat.full.yml`, Odoo 8073). Both modes passed
8/8 on 2026-11-24.
