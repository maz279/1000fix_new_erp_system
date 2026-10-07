# Next.js portal layer runbook (layer 5)

## The port map (dev machine)

| App | prod | dev |
|---|---|---|
| customer | 3010 | 3020 |
| corporate | 3001 | — |
| analytics | 3012 | — |
| seller | 3013 | — |
| brand | 3014 | — |
| agent-console | 3015 | — |
| partner | 3016 | — |
| vendor | 3017 | 3021 |
| prototype (static, not Next) | 3030 | — |

## Build law (scar #1 — never regress)

- Production: `next build --webpack` (all 8 package.json scripts pinned).
  Turbopack prod builds crash client-side in real browsers
  (`(void 0) is not a function` in chunk registration → Next error page).
- Dev: `next dev --turbopack` is fine (and is the ONLY flavor that renders
  in the ZCode IAB pane).
- `NEXT_PUBLIC_FIX_API_BASE` bakes at BUILD time. Default in each
  `lib/api.ts` is the gateway `http://127.0.0.1:8000`. Changing the base
  = rebuild the app, restart is not enough.

## The verified startup ritual

```bash
cd apps/web/<app>
NEXT_PUBLIC_FIX_API_BASE=http://127.0.0.1:8000 npx next start --port <port> --hostname ::
```
`--hostname ::` = dual-stack (loopback v4+v6). After build crashes or
experiments: `rm -rf .next` BEFORE rebuilding — stale artifacts (ghost
chunks like `2ep3-*.js`) produce phantom 500 error pages in browsers
while curl looks fine.

## Hydration forensics (the 3-question autopsy)

1. Did the document commit? — curl 200 means nothing; headless Edge dump:
   `grep data-theme` (ThemeProvider sets it on mount ⇒ hydration ran).
2. Did scripts load? — `tee_logger.py` (scratch) shows what the SERVER
   actually returned per request; the browser may receive error-HTML for
   chunk requests while curl gets 200s (IAB pane does exactly this).
3. Did scripts run? — inject a first-in-head trap
   (`onerror/unhandledrejection → document.title`) or Edge
   `--enable-logging=stderr` for the console stream.

Always `--user-data-dir=$(fresh temp)` on headless Edge — a reused profile
replays cached error pages forever (9614-byte ghost chased us for an hour).

## Money/i18n/lint tripwires (CI-enforced, FF-39/43/45)

- No client-side arithmetic on money-named fields (`*_bdt, amount, price,
  total, vat, tds…`) — BN-007 strings come from the backend; `bn007()`
  in `libs/ts/ui/src/masks.ts` may FORMAT only.
- No raw `fetch()` outside libs/ts/api-client (P-11); auth.ts is the
  sole exception (Keycloak IdP exchange).
- Hand-hex colors fail CFM-01 (every hex must exist in tokens.generated).
- P01 customer is Bengali-first (`lang="bn"`, bn copy, Bengali font).
- Shared atoms: `libs/ts/ui/src/components.tsx` (Pill/Stat/DataTable),
  masks in `masks.ts`, landing shell in `landing.tsx`; barrels re-export
  via each app's `lib/imports.ts` (react/jsx-runtime path mapping lives in
  each app tsconfig — needed because lib .tsx files sit outside app
  node_modules walk-up).

## Bundle budgets

customer critical path ≈154–177 KB gz (budget 400, 3G gate). Check after
dependency changes: gzip the top chunks in `.next/static/chunks`.
