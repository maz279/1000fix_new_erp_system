# a11y suite — WCAG 2.2 AA audit + Bengali layout-under-expansion (P04-M06-T07/T08)

> UX-005 names 11 criteria no automated scan can discharge — the manual audit
> record stays a human deliverable. What automation can catch (contrast,
> names, roles, target size, focus order, clipped labels) **fails the build**
> here. This is CI stage 12.

## Two halves, honestly split

| Half | What | When |
|---|---|---|
| Static | `check-expansion-static.py` — UI-copy character budgets (VB-002) + no truncation classes on translatable surfaces | Runs on every workstation, no browser |
| Dynamic | Playwright + @axe-core — per-workspace WCAG scan; bn/en overflow comparison | Needs the Odoo runtime (compose stack); runs in CI stage 12 and locally |

## Run

```powershell
# static (always)
py tooling/a11y/check-expansion-static.py

# dynamic (stack up; credentials from the environment only)
cd tooling/a11y
npm ci
npx playwright install chromium
$env:FIX_A11Y_PASSWORD = <from your secret store>   # never a literal
npx playwright test
```

## Configuration

| Env | Purpose | Default |
|---|---|---|
| `FIX_A11Y_BASE_URL` | Odoo web base | `http://127.0.0.1:8069` |
| `FIX_A11Y_USER` / `FIX_A11Y_PASSWORD` | login for the scan | unset ⇒ honest SKIP |

The W1 workspace routes are declared once in `playwright.config.ts`
(`W1_ROUTES`) and consumed by both specs.
