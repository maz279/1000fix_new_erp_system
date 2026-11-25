# E2E journeys

Two generations of journeys live here:

- **`j16-portal-surfaces.spec.ts` — current (2026-11-24).** Gate-2 smoke
  gate for the rebuilt portals: every portal serves its public landing and
  login, and every protected surface redirects to `/login?next=...`.
  Ports are the live local stack: 3000 customer, 3001 corporate,
  3002 analytics, 3003 seller, 3004 brand, 3005 agent console,
  3006 partner, 3007 vendor, 8090 Odoo (fix_dev).

- **`j01` — re-authored (2026-11-25), GREEN on the UAT stack.** The customer
  booking end-to-end journey (OTP → booking form → catalogue → device →
  booking write → P03 dispatch/QC workspace → technician API → estimates).
  The rebuild moved the auth boundary: sign-in comes FIRST (every record
  surface is gated), and the pages render into the shell `body`, not a
  `<main>` element. Run it with `E2E_UAT=1` (the dev Odoo currently lacks
  `FIX_ENV=local`, so the OTP echo only works on the UAT stack).

- **`j02`–`j15` — still pre-rebuild.** Same fixes apply (auth-first ordering,
  `body` locators, `E2E_UAT=1`); they are NOT yet green and must not be
  reported as sign-off evidence until re-authored and verified.

Run the current smoke gate with:

```bash
cd tooling/e2e
npx playwright test journeys/j16-portal-surfaces.spec.ts        # developer stack
E2E_UAT=1 npx playwright test journeys/j16-portal-surfaces.spec.ts   # UAT stack (3400-3407)
```

`E2E_UAT=1` points the same contract at the single-host synthetic UAT stack
(`infra/compose/docker-compose.uat.full.yml`, Odoo 8073). Both modes passed
8/8 on 2026-11-24.
