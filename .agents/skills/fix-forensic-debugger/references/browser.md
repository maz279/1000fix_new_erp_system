# Browser-layer runbook (layer 6: desktop, headless-Edge instrument, IAB pane)

## Surfaces ranked by trust

1. **Desktop Chrome/Edge** — ground truth for user-visible behavior.
2. **Headless Edge (instrument)** — scriptable, reproducible; use fresh
   `--user-data-dir` per run or you'll chase cached error-page ghosts.
3. **ZCode IAB pane** — most constrained; know its measured limits below
   before blaming app code.

## The headless-Edge harness (memorize)

```bash
MSEDGE="/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
[ -f "$MSEDGE" ] || MSEDGE="/c/Program Files/Microsoft/Edge/Application/msedge.exe"
rm -rf /tmp/ep   # FRESH profile every run — non-negotiable
"$MSEDGE" --headless=new --disable-gpu --user-data-dir="$(cygpath -w /tmp/ep)" \
  --virtual-time-budget=12000 --dump-dom "URL" > dom.html 2> console.log
grep -o 'data-theme="[a-z]*"' dom.html          # hydration proof
grep -oE 'Failed to load[^<]{0,140}' dom.html   # data-call outcome
grep CONSOLE console.log | grep -viE "GPU|dbus|extension"
```
- `--virtual-time-budget` fast-forwards timers; ≥12s lets data calls settle.
- `--dump-dom` serializes script bodies too — "leaked source text" in the
  dump inside `<script>` is NORMAL, not a bug.
- 500/error pages: if curl gets 200 but Edge gets the Next error doc,
  the crash is CLIENT-SIDE (hydration) — read console.log, then suspect
  the build flavor (Turbopack → rebuild --webpack).

## In-page error trap (when you can't get a console)

Inject FIRST in `<head>` (works through proxies/panes):
```html
<script>window.onerror=function(m,s,l,c,e){document.title=
 'ERR|'+String(m).slice(0,80)+'|'+((e&&e.stack)||'').slice(0,220)};
window.addEventListener('unhandledrejection',function(e){
 document.title='REJ|'+String(e.reason).slice(0,250)})</script>
```
Then dump-dom and read `<title>`. This technique cracked both the
`new URL(...)` asset-prefix crash and the ChunkLoadError mystery.

## ZCode IAB pane — measured limits (this machine, Chromium 146/Electron 41)

| Capability | Result |
|---|---|
| Static HTML | ✅ |
| Prototype :3030 | ✅ |
| Odoo :8069 pages | ✅ |
| **Next dev servers (3020/3021)** | ✅ (dev chunking stays under limits) |
| Next PROD builds (8-9 script tags) | ❌ "page couldn't load" |
| Script subresource fetches | ❌ >6 per page; substitutes HTML error bodies |
| Very large inline scripts (~>600KB) | ❌ truncated silently |
| Cross-origin fetch (to Kong :8000) | ❌ "Failed to fetch" (clean, no crash) |
| Loopback addressing | `localhost` only (not `127.0.0.1`); 127.0.0.1 = "couldn't load" |

Rules of engagement:
- Pane failing on prod portals is NOT a code bug. Prove in Edge first,
  state the pane limitation, move on.
- To show something in the pane: prototype, dev servers, Odoo, static.
- Never "fix" the app by degrading prod bundles for the pane.

## Request-forensics proxies (scratch arsenal, tooling/scripts/scratch/)

- `bisect_proxy.py` (3019→upstream): mutates responses one variable per
  run — BODYMODE strip-all-headers / noscript / extscript / inlscript /
  nonomodule / noasync / keep:N / stub / inlineall / inlinekeepR /
  mergeleaves. THE chunk-bisect instrument (found the 6-script ceiling).
- `tee_logger.py` (3022→upstream): logs status+bytes per request — shows
  what the browser REALLY received vs what curl sees.
- `pane_front.py`: all-inline experiment front (research only).
- Kill scratch servers when done (they poison the next port sweep).

## Session/cookie flow for data-in-browser

Portals call Kong :8000 with `credentials:"include"`. Browser needs an
Odoo session cookie first: log in at http://127.0.0.1:8069/web/login
(admin/admin) — cookies are host-scoped (127.0.0.1), shared across ports.
No login ⇒ every grid correctly shows "Odoo Session Expired". Log in,
refresh, data flows.
