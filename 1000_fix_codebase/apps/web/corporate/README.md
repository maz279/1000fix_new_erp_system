# apps/web/corporate — P04 Corporate B2B Portal (R2, PP1 template app)

The first Next.js app of the porting programme and the **template every other
portal copies** (PP3 extracts the reusable component set from it). The home
screen renders *entirely from generated artefacts*: design tokens from
`libs/ts/ui/src/tokens/tokens.generated.ts` (R2 emission) and strings from the
copy registry via `libs/ts/api-client/src/ui-copy.ts`. No literals, no
fixtures (FF-39 enforces).

## Next-16 checklist (PP1-M01-T03 — applies to every app copying this template)

- [x] **Turbopack** is the default for `dev` and `build` — no webpack config.
- [x] **`middleware.ts` is `proxy.ts`** in Next 16 — this app ships neither at
      scaffold; when PP3 needs edge logic, the file is `proxy.ts`.
- [x] **Cache Components** are explicit — nothing caches unless annotated
      `'use cache'`; the scaffold annotates nothing yet.
- [x] **`next lint` was removed in Next 16** — no `lint` script until the PP3
      template extraction lands ESLint config; `next build` type-checks.
- [x] **React 19.3** — `React.ReactNode` types without importing React.
- [x] **Monorepo modules**: `outputFileTracingRoot` (next.config.ts) points at
      the codebase root so Turbopack compiles the in-tree `libs/` — apps import
      them by relative path from `app/` (four levels: `../../../../libs/...`).
- [x] **Payload floor ≥ 3.89** (F4, verified 2026-10-06): Payload is only for
      CMS-true surfaces (customer/marketing) — this app does not use it.

## Commands

```powershell
npm install
npm run dev     # 127.0.0.1:3001 (EP-12 loopback)
npm run build   # Turbopack production build
python ../../..//tooling/scripts/check-bundle-budget.py apps/web/corporate 400
```

## Budget (measured 2026-10-06)

First-load **171 KB gz** (JS+CSS chunks + route HTML) against the 400 KB
contract. The 400 KB figure is the **P01** critical-path budget (roadmap
P02-M07-T07); corporate tracks it as the leading indicator until P01 builds.

## API access

Through `libs/ts/api-client` only (FF-39 fails any raw `fetch` outside it).
Base URL: `FIX_API_BASE` env (loopback default for the compose stack; the
gateway is Kong). The estate endpoints land in PP3 against
`contracts/openapi/w4-portals.json`.
